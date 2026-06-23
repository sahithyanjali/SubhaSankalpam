from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_admin_user
from app.models.audit import AuditLog
from app.models.fraud import FraudAlert, FraudAlertStatus
from app.models.notification import Notification, NotificationType
from app.models.photo import Photo, PhotoModerationStatus
from app.models.profile import Profile, ProfileApprovalStatus
from app.models.subscription import Payment, PaymentStatus
from app.models.user import User, UserStatus
from app.schemas.admin import (
    AdminDashboard,
    AuditLogListResponse,
    FraudAlertResponse,
    FraudAlertUpdate,
    ProfileReviewAction,
    ReportRequest,
    ReportResponse,
)

router = APIRouter(prefix="/admin", tags=["Admin Operations"])


@router.get("/dashboard", response_model=AdminDashboard)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Admin dashboard: total users, verified, pending, active, revenue, fraud alerts."""
    total = (await db.execute(select(func.count(User.id)))).scalar()
    verified = (await db.execute(
        select(func.count(User.id)).where(User.verified_badge.is_(True))
    )).scalar()
    pending = (await db.execute(
        select(func.count(Profile.id)).where(Profile.approval_status == ProfileApprovalStatus.PENDING)
    )).scalar()
    active = (await db.execute(
        select(func.count(User.id)).where(User.status == UserStatus.ACTIVE)
    )).scalar()
    revenue = (await db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.status == PaymentStatus.COMPLETED)
    )).scalar()
    fraud_count = (await db.execute(
        select(func.count(FraudAlert.id)).where(FraudAlert.status == FraudAlertStatus.OPEN)
    )).scalar()

    return AdminDashboard(
        total_users=total,
        verified_users=verified,
        pending_verification=pending,
        active_users=active,
        subscription_revenue=float(revenue),
        fraud_alerts=fraud_count,
        profiles_pending_review=pending,
    )


@router.get("/profiles/pending")
async def get_pending_profiles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Get profiles pending admin review."""
    result = await db.execute(
        select(Profile)
        .where(Profile.approval_status == ProfileApprovalStatus.PENDING)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    profiles = result.scalars().all()
    total = (await db.execute(
        select(func.count(Profile.id)).where(Profile.approval_status == ProfileApprovalStatus.PENDING)
    )).scalar()

    return {"profiles": profiles, "total": total}


@router.put("/profiles/{user_id}/review")
async def review_profile(
    user_id: UUID,
    action: ProfileReviewAction,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Approve, reject, or suspend a profile."""
    result = await db.execute(select(Profile).where(Profile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile.approval_status = action.status
    profile.admin_notes = action.notes

    # Notify user
    status_text = action.status.value
    notification = Notification(
        user_id=user_id,
        notification_type=NotificationType.PROFILE_APPROVED if action.status == ProfileApprovalStatus.APPROVED else NotificationType.PROFILE_REJECTED,
        title=f"Profile {status_text.title()}",
        body=f"Your profile has been {status_text}.",
    )
    db.add(notification)

    # Audit log
    log = AuditLog(
        user_id=admin.id,
        action=f"profile_{status_text}",
        resource_type="profile",
        resource_id=str(user_id),
        details=action.notes,
    )
    db.add(log)

    await db.commit()
    return {"message": f"Profile {status_text}", "user_id": str(user_id)}


@router.get("/fraud-alerts", response_model=list[FraudAlertResponse])
async def get_fraud_alerts(
    status_filter: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Get fraud alerts for investigation."""
    query = select(FraudAlert).order_by(FraudAlert.created_at.desc())
    if status_filter:
        query = query.where(FraudAlert.status == FraudAlertStatus(status_filter))

    result = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    return result.scalars().all()


@router.put("/fraud-alerts/{alert_id}")
async def update_fraud_alert(
    alert_id: UUID,
    data: FraudAlertUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Update fraud alert status (investigating, resolved, dismissed)."""
    result = await db.execute(select(FraudAlert).where(FraudAlert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = data.status
    alert.resolution_notes = data.resolution_notes
    if data.status in (FraudAlertStatus.RESOLVED, FraudAlertStatus.DISMISSED):
        alert.resolved_by = admin.id
        alert.resolved_at = datetime.now(timezone.utc)

    log = AuditLog(
        user_id=admin.id,
        action=f"fraud_alert_{data.status.value}",
        resource_type="fraud_alert",
        resource_id=str(alert_id),
    )
    db.add(log)

    await db.commit()
    return {"message": f"Alert updated to {data.status.value}"}


@router.put("/users/{user_id}/suspend")
async def suspend_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Suspend a user account."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.status = UserStatus.SUSPENDED

    log = AuditLog(
        user_id=admin.id,
        action="user_suspended",
        resource_type="user",
        resource_id=str(user_id),
    )
    db.add(log)

    await db.commit()
    return {"message": "User suspended"}


@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: str = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """List all users with filtering."""
    query = select(User)
    if status_filter:
        query = query.where(User.status == UserStatus(status_filter))

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()

    result = await db.execute(
        query.order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    users = result.scalars().all()

    return {
        "users": [
            {
                "id": str(u.id),
                "email": u.email,
                "phone": u.phone,
                "role": u.role.value,
                "status": u.status.value,
                "verified_badge": u.verified_badge,
                "created_at": u.created_at.isoformat(),
            }
            for u in users
        ],
        "total": total,
    }


@router.post("/reports", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Generate user, revenue, or fraud reports."""
    if request.report_type == "user":
        total = (await db.execute(select(func.count(User.id)))).scalar()
        active = (await db.execute(
            select(func.count(User.id)).where(User.status == UserStatus.ACTIVE)
        )).scalar()
        verified = (await db.execute(
            select(func.count(User.id)).where(User.verified_badge.is_(True))
        )).scalar()
        data = {"total_users": total, "active_users": active, "verified_users": verified}

    elif request.report_type == "revenue":
        total_rev = (await db.execute(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                Payment.status == PaymentStatus.COMPLETED
            )
        )).scalar()
        count = (await db.execute(
            select(func.count(Payment.id)).where(Payment.status == PaymentStatus.COMPLETED)
        )).scalar()
        data = {"total_revenue": float(total_rev), "total_transactions": count}

    elif request.report_type == "fraud":
        total_alerts = (await db.execute(select(func.count(FraudAlert.id)))).scalar()
        open_alerts = (await db.execute(
            select(func.count(FraudAlert.id)).where(FraudAlert.status == FraudAlertStatus.OPEN)
        )).scalar()
        data = {"total_alerts": total_alerts, "open_alerts": open_alerts}
    else:
        raise HTTPException(status_code=400, detail="Invalid report type")

    return ReportResponse(
        report_type=request.report_type,
        data=data,
        generated_at=datetime.now(timezone.utc),
    )


@router.get("/audit-logs", response_model=AuditLogListResponse)
async def get_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Get audit logs for compliance."""
    total = (await db.execute(select(func.count(AuditLog.id)))).scalar()
    result = await db.execute(
        select(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    logs = result.scalars().all()
    return AuditLogListResponse(logs=logs, total=total, page=page, page_size=page_size)


@router.put("/photos/{photo_id}/moderate")
async def moderate_photo(
    photo_id: UUID,
    action: str = Query(..., description="approved or rejected"),
    notes: str = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Moderate a photo (approve/reject)."""
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    photo.moderation_status = PhotoModerationStatus(action)
    photo.moderation_notes = notes

    await db.commit()
    return {"message": f"Photo {action}"}
