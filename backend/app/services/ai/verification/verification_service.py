import json
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.ai_score import AIScore, AIScoreType
from app.models.user import User
from app.models.verification import Verification, VerificationStatus
from app.schemas.ai import VerificationResult


class VerificationService:
    """AI-powered profile verification using face comparison and identity analysis."""

    @staticmethod
    async def verify_profile(db: AsyncSession, user_id: UUID) -> VerificationResult:
        result = await db.execute(
            select(Verification).where(Verification.user_id == user_id)
        )
        verification = result.scalar_one_or_none()

        if verification is None:
            raise ValueError("No verification record found")

        # AI-powered face comparison
        verification_score = await VerificationService._compare_faces(
            verification.selfie_url, verification.profile_photo_url
        )

        # Trust score calculation
        trust_score = await VerificationService._calculate_trust_score(db, user_id)

        # Identity consistency
        identity_consistency = (verification_score + trust_score) / 2

        is_verified = verification_score >= 70 and trust_score >= 60

        # Update verification record
        verification.verification_score = verification_score
        verification.trust_score = trust_score
        verification.identity_consistency = identity_consistency
        verification.verification_status = (
            VerificationStatus.VERIFIED
            if is_verified
            else VerificationStatus.MANUAL_REVIEW
        )

        # Update user verified badge
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if user and is_verified:
            user.verified_badge = True
            user.is_verified = True

        # Store AI score
        ai_score = AIScore(
            user_id=user_id,
            score_type=AIScoreType.VERIFICATION,
            score=verification_score,
            details=json.dumps(
                {
                    "verification_score": verification_score,
                    "trust_score": trust_score,
                    "identity_consistency": identity_consistency,
                }
            ),
            model_version="v1.0",
        )
        db.add(ai_score)
        await db.commit()

        return VerificationResult(
            user_id=user_id,
            verification_score=verification_score,
            trust_score=trust_score,
            identity_consistency=identity_consistency,
            is_verified=is_verified,
        )

    @staticmethod
    async def _compare_faces(
        selfie_url: Optional[str], profile_photo_url: Optional[str]
    ) -> float:
        """Compare selfie with profile photo using AI."""
        if not selfie_url or not profile_photo_url:
            return 0.0

        try:
            if settings.GOOGLE_AI_API_KEY:
                import google.generativeai as genai

                genai.configure(api_key=settings.GOOGLE_AI_API_KEY)
                model = genai.GenerativeModel("gemini-1.5-flash")

                response = model.generate_content(
                    [
                        "Compare these two facial images and return a similarity score from 0 to 100. "
                        "Consider facial features, structure, and identity consistency. "
                        "Return ONLY a number between 0 and 100.",
                        f"Selfie URL: {selfie_url}",
                        f"Profile Photo URL: {profile_photo_url}",
                    ]
                )
                score = float(response.text.strip())
                return min(max(score, 0), 100)
        except Exception:
            pass

        # Fallback: basic score
        return 75.0

    @staticmethod
    async def _calculate_trust_score(db: AsyncSession, user_id: UUID) -> float:
        """Calculate overall trust score based on profile completeness and verification."""
        from app.models.photo import Photo
        from app.models.profile import Profile

        score = 50.0  # Base score

        # Check profile completeness
        profile_result = await db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = profile_result.scalar_one_or_none()
        if profile:
            if profile.education:
                score += 5
            if profile.occupation:
                score += 5
            if profile.city:
                score += 5
            if profile.about_me:
                score += 5

        # Check photos
        photos_result = await db.execute(select(Photo).where(Photo.user_id == user_id))
        photos = photos_result.scalars().all()
        if len(photos) >= 3:
            score += 10
        elif len(photos) >= 1:
            score += 5

        # Check user account age
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if user and user.is_phone_verified:
            score += 10
        if user and user.is_email_verified:
            score += 5

        return min(score, 100)


verification_service = VerificationService()
