import os
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.middleware.auth import get_current_active_user
from app.models.horoscope import Horoscope
from app.models.subscription import SubscriptionPlan, UserSubscription
from app.models.user import User
from app.schemas.horoscope import HoroscopeCreate, HoroscopeResponse, HoroscopeUpdate

router = APIRouter(prefix="/horoscope", tags=["Horoscope"])


@router.post("/", response_model=HoroscopeResponse, status_code=status.HTTP_201_CREATED)
async def create_horoscope(
    data: HoroscopeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create horoscope details: Nakshatra, Rasi, Gothram, Dosham, Birth Time/Place."""
    existing = await db.execute(select(Horoscope).where(Horoscope.user_id == current_user.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Horoscope already exists")

    horoscope = Horoscope(user_id=current_user.id, **data.model_dump(exclude_unset=True))
    db.add(horoscope)
    await db.commit()
    await db.refresh(horoscope)
    return horoscope


@router.get("/me", response_model=HoroscopeResponse)
async def get_my_horoscope(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get current user's horoscope."""
    result = await db.execute(select(Horoscope).where(Horoscope.user_id == current_user.id))
    horoscope = result.scalar_one_or_none()
    if not horoscope:
        raise HTTPException(status_code=404, detail="Horoscope not found")
    return horoscope


@router.put("/me", response_model=HoroscopeResponse)
async def update_horoscope(
    data: HoroscopeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update horoscope details."""
    result = await db.execute(select(Horoscope).where(Horoscope.user_id == current_user.id))
    horoscope = result.scalar_one_or_none()
    if not horoscope:
        raise HTTPException(status_code=404, detail="Horoscope not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(horoscope, field, value)

    await db.commit()
    await db.refresh(horoscope)
    return horoscope


@router.post("/upload-pdf", response_model=HoroscopeResponse)
async def upload_horoscope_pdf(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Upload horoscope PDF document."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Save file
    upload_dir = os.path.join(settings.UPLOAD_DIR, "horoscopes", str(current_user.id))
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Update horoscope record
    result = await db.execute(select(Horoscope).where(Horoscope.user_id == current_user.id))
    horoscope = result.scalar_one_or_none()

    if not horoscope:
        horoscope = Horoscope(user_id=current_user.id, horoscope_pdf_url=file_path)
        db.add(horoscope)
    else:
        horoscope.horoscope_pdf_url = file_path

    await db.commit()
    await db.refresh(horoscope)
    return horoscope


@router.get("/{user_id}", response_model=HoroscopeResponse)
async def get_user_horoscope(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get another user's horoscope (requires subscription with horoscope access)."""
    # Verify subscription allows horoscope viewing
    sub_result = await db.execute(
        select(UserSubscription).where(UserSubscription.user_id == current_user.id)
    )
    subscription = sub_result.scalar_one_or_none()
    if not subscription or not subscription.is_active:
        raise HTTPException(
            status_code=403, detail="Active subscription required to view horoscopes"
        )

    plan_result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.id == subscription.plan_id)
    )
    plan = plan_result.scalar_one_or_none()
    if not plan or not plan.can_see_horoscope:
        raise HTTPException(
            status_code=403,
            detail="Your subscription plan does not include horoscope access",
        )

    result = await db.execute(select(Horoscope).where(Horoscope.user_id == user_id))
    horoscope = result.scalar_one_or_none()
    if not horoscope:
        raise HTTPException(status_code=404, detail="Horoscope not found")
    return horoscope
