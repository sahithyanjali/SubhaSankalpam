from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.match import Match
from app.models.profile import Gender, Profile
from app.models.user import User, UserStatus
from app.schemas.ai import InactiveProfileAlert, MatchRecommendation, MatchRecommendationList
from app.services.ai.compatibility.compatibility_service import compatibility_service


class RecommendationService:
    """AI Match Recommendation Engine."""

    @staticmethod
    async def get_daily_matches(
        db: AsyncSession, user_id: UUID, limit: int = 5
    ) -> MatchRecommendationList:
        return await RecommendationService._get_recommendations(
            db, user_id, limit, "daily"
        )

    @staticmethod
    async def get_weekly_matches(
        db: AsyncSession, user_id: UUID, limit: int = 20
    ) -> MatchRecommendationList:
        return await RecommendationService._get_recommendations(
            db, user_id, limit, "weekly"
        )

    @staticmethod
    async def get_similar_profiles(
        db: AsyncSession, user_id: UUID, limit: int = 10
    ) -> MatchRecommendationList:
        return await RecommendationService._get_recommendations(
            db, user_id, limit, "similar"
        )

    @staticmethod
    async def _get_recommendations(
        db: AsyncSession, user_id: UUID, limit: int, rec_type: str
    ) -> MatchRecommendationList:
        # Get current user's profile
        profile_result = await db.execute(select(Profile).where(Profile.user_id == user_id))
        user_profile = profile_result.scalar_one_or_none()

        if not user_profile:
            return MatchRecommendationList(recommendations=[], recommendation_type=rec_type)

        # Determine target gender
        target_gender = Gender.FEMALE if user_profile.gender == Gender.MALE else Gender.MALE

        # Get existing match IDs to exclude
        sent_result = await db.execute(select(Match.receiver_id).where(Match.sender_id == user_id))
        received_result = await db.execute(select(Match.sender_id).where(Match.receiver_id == user_id))
        excluded_ids = {r[0] for r in sent_result.all()} | {r[0] for r in received_result.all()}
        excluded_ids.add(user_id)

        # Find candidate profiles
        query = (
            select(Profile)
            .join(User, User.id == Profile.user_id)
            .where(
                and_(
                    Profile.gender == target_gender,
                    User.status == UserStatus.ACTIVE,
                    Profile.user_id.notin_(excluded_ids),
                    Profile.approval_status == "approved",
                )
            )
        )

        # Apply basic filters based on recommendation type
        if rec_type == "similar":
            if user_profile.religion:
                query = query.where(Profile.religion == user_profile.religion)
            if user_profile.state:
                query = query.where(Profile.state == user_profile.state)

        query = query.limit(limit * 3)  # Fetch more for scoring
        result = await db.execute(query)
        candidates = result.scalars().all()

        # Score each candidate
        scored_candidates = []
        for candidate in candidates:
            try:
                compat = await compatibility_service.calculate_compatibility(
                    db, user_id, candidate.user_id
                )
                reason = RecommendationService._generate_match_reason(user_profile, candidate, compat.overall_score)
                scored_candidates.append(
                    MatchRecommendation(
                        user_id=candidate.user_id,
                        compatibility_score=compat.overall_score,
                        match_reason=reason,
                        profile_summary=f"{candidate.first_name}, {candidate.age}y, {candidate.education or 'N/A'}, {candidate.city or 'N/A'}",
                    )
                )
            except Exception:
                continue

        # Sort by score and limit
        scored_candidates.sort(key=lambda x: x.compatibility_score, reverse=True)

        return MatchRecommendationList(
            recommendations=scored_candidates[:limit],
            recommendation_type=rec_type,
        )

    @staticmethod
    def _generate_match_reason(user_profile: Profile, candidate: Profile, score: float) -> str:
        reasons = []
        if user_profile.religion and candidate.religion and user_profile.religion == candidate.religion:
            reasons.append("Same religion")
        if user_profile.caste and candidate.caste and user_profile.caste == candidate.caste:
            reasons.append("Same caste")
        if user_profile.state and candidate.state and user_profile.state == candidate.state:
            reasons.append("Same state")
        if user_profile.city and candidate.city and user_profile.city == candidate.city:
            reasons.append("Same city")
        if user_profile.education and candidate.education:
            reasons.append("Similar education")

        if not reasons:
            reasons.append(f"Good compatibility ({score:.0f}%)")

        return ", ".join(reasons)

    @staticmethod
    async def detect_inactive_profiles(
        db: AsyncSession, days_threshold: int = 30
    ) -> list[InactiveProfileAlert]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_threshold)

        result = await db.execute(
            select(User).where(
                and_(
                    User.status == UserStatus.ACTIVE,
                    or_(
                        User.last_active < cutoff,
                        User.last_active.is_(None),
                    ),
                )
            )
        )
        inactive_users = result.scalars().all()

        alerts = []
        for user in inactive_users:
            last_active = user.last_active or user.created_at
            inactive_days = (datetime.now(timezone.utc) - last_active).days

            if inactive_days >= 90:
                category = "90_days"
            elif inactive_days >= 60:
                category = "60_days"
            else:
                category = "30_days"

            alerts.append(
                InactiveProfileAlert(
                    user_id=user.id,
                    last_active=str(last_active),
                    inactive_days=inactive_days,
                    category=category,
                )
            )

        return alerts


recommendation_service = RecommendationService()
