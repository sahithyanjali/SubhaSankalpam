from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_active_user
from app.models.profile import Profile, ProfileApprovalStatus
from app.models.user import User, UserStatus
from app.schemas.profile import (
    ProfileCreate,
    ProfileListResponse,
    ProfileResponse,
    ProfileSearchFilters,
    ProfileUpdate,
)

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create user profile with personal, professional, and lifestyle details."""
    existing = await db.execute(select(Profile).where(Profile.user_id == current_user.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Profile already exists")

    # Calculate age
    today = date.today()
    dob = profile_data.date_of_birth
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    profile = Profile(
        user_id=current_user.id,
        age=age,
        **profile_data.model_dump(),
    )

    # Calculate completeness
    profile.profile_completeness = _calculate_completeness(profile)

    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get current user's profile."""
    result = await db.execute(select(Profile).where(Profile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/me", response_model=ProfileResponse)
async def update_my_profile(
    profile_data: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update current user's profile."""
    result = await db.execute(select(Profile).where(Profile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    profile.profile_completeness = _calculate_completeness(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


@router.get("/{user_id}", response_model=ProfileResponse)
async def get_profile(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific user's profile."""
    result = await db.execute(
        select(Profile).where(
            and_(
                Profile.user_id == user_id,
                Profile.approval_status == ProfileApprovalStatus.APPROVED,
            )
        )
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("/search", response_model=ProfileListResponse)
async def search_profiles(
    filters: ProfileSearchFilters,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Search profiles with filters: age, caste, religion, height, education, income, location, etc."""
    query = (
        select(Profile)
        .join(User, User.id == Profile.user_id)
        .where(
            and_(
                Profile.user_id != current_user.id,
                Profile.approval_status == ProfileApprovalStatus.APPROVED,
                User.status == UserStatus.ACTIVE,
            )
        )
    )

    # Apply filters
    if filters.gender:
        query = query.where(Profile.gender == filters.gender)
    if filters.min_age:
        query = query.where(Profile.age >= filters.min_age)
    if filters.max_age:
        query = query.where(Profile.age <= filters.max_age)
    if filters.caste:
        query = query.where(Profile.caste.ilike(f"%{filters.caste}%"))
    if filters.religion:
        query = query.where(Profile.religion.ilike(f"%{filters.religion}%"))
    if filters.min_height:
        query = query.where(Profile.height_cm >= filters.min_height)
    if filters.max_height:
        query = query.where(Profile.height_cm <= filters.max_height)
    if filters.education:
        query = query.where(Profile.education.ilike(f"%{filters.education}%"))
    if filters.location:
        query = query.where(
            or_(
                Profile.city.ilike(f"%{filters.location}%"),
                Profile.state.ilike(f"%{filters.location}%"),
                Profile.district.ilike(f"%{filters.location}%"),
            )
        )
    if filters.marital_status:
        query = query.where(Profile.marital_status == filters.marital_status)
    if filters.mother_tongue:
        query = query.where(Profile.mother_tongue.ilike(f"%{filters.mother_tongue}%"))
    if filters.willing_intercaste is not None:
        query = query.where(Profile.willing_intercaste == filters.willing_intercaste)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    offset = (filters.page - 1) * filters.page_size
    query = query.offset(offset).limit(filters.page_size)

    result = await db.execute(query)
    profiles = result.scalars().all()

    return ProfileListResponse(
        profiles=profiles,
        total=total,
        page=filters.page,
        page_size=filters.page_size,
    )


def _calculate_completeness(profile: Profile) -> int:
    total = 20
    filled = 0
    fields = [
        profile.first_name,
        profile.last_name,
        profile.gender,
        profile.date_of_birth,
        profile.height_cm,
        profile.marital_status,
        profile.religion,
        profile.caste,
        profile.education,
        profile.occupation,
        profile.annual_income,
        profile.city,
        profile.state,
        profile.about_me,
        profile.eating_habit,
        profile.father_occupation,
        profile.languages,
        profile.gothram,
        profile.weight_kg,
        profile.institution,
    ]
    filled = sum(1 for f in fields if f)
    return min(int((filled / total) * 100), 100)
