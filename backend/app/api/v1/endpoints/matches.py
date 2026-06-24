from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_active_user
from app.models.match import Match, MatchStatus
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.schemas.match import (
    MatchListResponse,
    MatchResponse,
    RespondInterest,
    SendInterest,
)

router = APIRouter(prefix="/matches", tags=["Matches & Interests"])


@router.post("/send-interest", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
async def send_interest(
    data: SendInterest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Send interest to another user."""
    if data.receiver_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send interest to yourself")

    # Check if already sent
    existing = await db.execute(
        select(Match).where(
            and_(
                Match.sender_id == current_user.id,
                Match.receiver_id == data.receiver_id,
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Interest already sent")

    # Calculate compatibility score
    from app.services.ai.compatibility.compatibility_service import (
        compatibility_service,
    )

    try:
        compat = await compatibility_service.calculate_compatibility(
            db, current_user.id, data.receiver_id
        )
        score = compat.overall_score
    except Exception:
        score = None

    match = Match(
        sender_id=current_user.id,
        receiver_id=data.receiver_id,
        message=data.message,
        compatibility_score=score,
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
    )
    db.add(match)

    # Send notification
    notification = Notification(
        user_id=data.receiver_id,
        notification_type=NotificationType.INTEREST_RECEIVED,
        title="New Interest Received!",
        body="Someone has sent you an interest request.",
    )
    db.add(notification)

    await db.commit()
    await db.refresh(match)
    return match


@router.put("/{match_id}/respond", response_model=MatchResponse)
async def respond_to_interest(
    match_id: UUID,
    data: RespondInterest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Accept or reject an interest request."""
    result = await db.execute(
        select(Match).where(and_(Match.id == match_id, Match.receiver_id == current_user.id))
    )
    match = result.scalar_one_or_none()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if match.status != MatchStatus.PENDING:
        raise HTTPException(status_code=400, detail="Already responded")

    if data.status not in (MatchStatus.ACCEPTED, MatchStatus.REJECTED):
        raise HTTPException(status_code=400, detail="Status must be 'accepted' or 'rejected'")

    match.status = data.status
    match.responded_at = datetime.now(timezone.utc)
    if data.rejection_reason:
        match.rejection_reason = data.rejection_reason

    # Notify sender
    notif_type = (
        NotificationType.INTEREST_ACCEPTED
        if data.status == MatchStatus.ACCEPTED
        else NotificationType.INTEREST_REJECTED
    )
    notification = Notification(
        user_id=match.sender_id,
        notification_type=notif_type,
        title="Interest Response",
        body=f"Your interest has been {'accepted' if data.status == MatchStatus.ACCEPTED else 'declined'}.",
    )
    db.add(notification)

    # Create chat room on acceptance
    if data.status == MatchStatus.ACCEPTED:
        from app.models.chat import ChatRoom

        chat_room = ChatRoom(
            user1_id=match.sender_id,
            user2_id=match.receiver_id,
            match_id=match.id,
        )
        db.add(chat_room)

    await db.commit()
    await db.refresh(match)
    return match


@router.get("/sent", response_model=MatchListResponse)
async def get_sent_interests(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all sent interests."""
    count_result = await db.execute(
        select(func.count(Match.id)).where(Match.sender_id == current_user.id)
    )
    total = count_result.scalar()

    result = await db.execute(
        select(Match)
        .where(Match.sender_id == current_user.id)
        .order_by(Match.sent_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    matches = result.scalars().all()

    return MatchListResponse(matches=matches, total=total, page=page, page_size=page_size)


@router.get("/received", response_model=MatchListResponse)
async def get_received_interests(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all received interests."""
    count_result = await db.execute(
        select(func.count(Match.id)).where(Match.receiver_id == current_user.id)
    )
    total = count_result.scalar()

    result = await db.execute(
        select(Match)
        .where(Match.receiver_id == current_user.id)
        .order_by(Match.sent_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    matches = result.scalars().all()

    return MatchListResponse(matches=matches, total=total, page=page, page_size=page_size)
