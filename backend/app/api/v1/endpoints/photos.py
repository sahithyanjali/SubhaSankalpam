import os
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.middleware.auth import get_current_active_user
from app.models.photo import Photo, PhotoType
from app.models.user import User
from app.models.verification import Verification

router = APIRouter(prefix="/photos", tags=["Photos"])


@router.post("/upload")
async def upload_photo(
    photo_type: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Upload profile, gallery, family, or selfie photo."""
    if file.content_type not in settings.ALLOWED_PHOTO_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type. Use JPEG, PNG, or WebP")

    content = await file.read()
    if len(content) > settings.MAX_PHOTO_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max {settings.MAX_PHOTO_SIZE_MB}MB",
        )

    # Save file
    upload_dir = os.path.join(settings.UPLOAD_DIR, "photos", str(current_user.id))
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{photo_type}_{file.filename}")

    with open(file_path, "wb") as f:
        f.write(content)

    # Determine if primary
    existing = await db.execute(
        select(Photo).where(Photo.user_id == current_user.id, Photo.photo_type == PhotoType.PROFILE)
    )
    is_primary = photo_type == "profile" and existing.scalar_one_or_none() is None

    photo = Photo(
        user_id=current_user.id,
        photo_type=PhotoType(photo_type),
        file_url=file_path,
        is_primary=is_primary,
    )
    db.add(photo)
    await db.commit()
    await db.refresh(photo)

    return {
        "id": str(photo.id),
        "file_url": photo.file_url,
        "photo_type": photo.photo_type.value,
    }


@router.get("/my-photos")
async def get_my_photos(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all photos for current user."""
    result = await db.execute(
        select(Photo).where(Photo.user_id == current_user.id).order_by(Photo.display_order)
    )
    photos = result.scalars().all()
    return {
        "photos": [
            {
                "id": str(p.id),
                "photo_type": p.photo_type.value,
                "file_url": p.file_url,
                "is_primary": p.is_primary,
                "moderation_status": p.moderation_status.value,
            }
            for p in photos
        ]
    }


@router.delete("/{photo_id}")
async def delete_photo(
    photo_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a photo."""
    result = await db.execute(
        select(Photo).where(Photo.id == photo_id, Photo.user_id == current_user.id)
    )
    photo = result.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    await db.delete(photo)
    await db.commit()
    return {"message": "Photo deleted"}


@router.post("/selfie-verify")
async def selfie_verification(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Upload selfie for verification. Compares with profile photo for verified badge."""
    if file.content_type not in settings.ALLOWED_PHOTO_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type")

    content = await file.read()

    # Save selfie
    upload_dir = os.path.join(settings.UPLOAD_DIR, "selfies", str(current_user.id))
    os.makedirs(upload_dir, exist_ok=True)
    selfie_path = os.path.join(upload_dir, file.filename)

    with open(selfie_path, "wb") as f:
        f.write(content)

    # Get profile photo
    profile_photo_result = await db.execute(
        select(Photo).where(
            Photo.user_id == current_user.id,
            Photo.photo_type == PhotoType.PROFILE,
            Photo.is_primary.is_(True),
        )
    )
    profile_photo = profile_photo_result.scalar_one_or_none()

    # Create/update verification record
    ver_result = await db.execute(
        select(Verification).where(Verification.user_id == current_user.id)
    )
    verification = ver_result.scalar_one_or_none()

    if not verification:
        verification = Verification(
            user_id=current_user.id,
            selfie_url=selfie_path,
            profile_photo_url=profile_photo.file_url if profile_photo else None,
        )
        db.add(verification)
    else:
        verification.selfie_url = selfie_path
        if profile_photo:
            verification.profile_photo_url = profile_photo.file_url

    await db.commit()
    await db.refresh(verification)

    # Trigger AI verification
    from app.services.ai.verification.verification_service import verification_service

    result = await verification_service.verify_profile(db, current_user.id)

    return {
        "verification_score": result.verification_score,
        "trust_score": result.trust_score,
        "is_verified": result.is_verified,
        "message": "Verified! Badge granted."
        if result.is_verified
        else "Verification pending manual review.",
    }
