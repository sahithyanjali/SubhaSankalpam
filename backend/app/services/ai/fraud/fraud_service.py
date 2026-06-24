import json
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_score import AIScore, AIScoreType
from app.models.fraud import FraudAlert, FraudType, RiskLevel
from app.models.photo import Photo
from app.models.user import User
from app.schemas.ai import FakeProfileResult


class FraudDetectionService:
    """AI-powered fraud and fake profile detection."""

    @staticmethod
    async def analyze_profile(db: AsyncSession, user_id: UUID) -> FakeProfileResult:
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")

        # Run all detection checks
        duplicate_photos = await FraudDetectionService._check_duplicate_photos(db, user_id)
        duplicate_phone = await FraudDetectionService._check_duplicate_phone(db, user.phone)
        suspicious_activity = await FraudDetectionService._check_suspicious_activity(db, user_id)
        bot_behavior = await FraudDetectionService._check_bot_behavior(db, user_id)

        # Calculate fraud score
        fraud_score = 0.0
        if duplicate_photos:
            fraud_score += 30
        if duplicate_phone:
            fraud_score += 25
        if suspicious_activity:
            fraud_score += 25
        if bot_behavior:
            fraud_score += 20

        # Determine risk level
        if fraud_score >= 70:
            risk_level = RiskLevel.CRITICAL
        elif fraud_score >= 50:
            risk_level = RiskLevel.HIGH
        elif fraud_score >= 30:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        # Create fraud alert if score is concerning
        if fraud_score >= 30:
            fraud_alert = FraudAlert(
                user_id=user_id,
                fraud_type=FraudType.FAKE_PROFILE,
                risk_level=risk_level,
                fraud_score=fraud_score,
                description=f"Automated fraud analysis detected risk score: {fraud_score}",
                evidence=json.dumps(
                    {
                        "duplicate_photos": duplicate_photos,
                        "duplicate_phone": duplicate_phone,
                        "suspicious_activity": suspicious_activity,
                        "bot_behavior": bot_behavior,
                    }
                ),
            )
            db.add(fraud_alert)

        # Store AI score
        ai_score = AIScore(
            user_id=user_id,
            score_type=AIScoreType.FRAUD,
            score=fraud_score,
            details=json.dumps(
                {
                    "duplicate_photos": duplicate_photos,
                    "duplicate_phone": duplicate_phone,
                    "suspicious_activity": suspicious_activity,
                    "bot_behavior": bot_behavior,
                    "risk_level": risk_level.value,
                }
            ),
            model_version="v1.0",
        )
        db.add(ai_score)
        await db.commit()

        return FakeProfileResult(
            user_id=user_id,
            fraud_score=fraud_score,
            risk_level=risk_level.value,
            duplicate_photos=duplicate_photos,
            duplicate_phone=duplicate_phone,
            suspicious_activity=suspicious_activity,
            bot_behavior=bot_behavior,
        )

    @staticmethod
    async def _check_duplicate_photos(db: AsyncSession, user_id: UUID) -> bool:
        """Check if user's photos appear on other profiles."""
        # In production, use image hashing (pHash) or AI embeddings
        # For now, check file URL duplication
        user_photos = await db.execute(select(Photo.file_url).where(Photo.user_id == user_id))
        urls = [r[0] for r in user_photos.all()]

        if not urls:
            return False

        for url in urls:
            dup_result = await db.execute(
                select(func.count(Photo.id)).where(
                    and_(Photo.file_url == url, Photo.user_id != user_id)
                )
            )
            if dup_result.scalar() > 0:
                return True

        return False

    @staticmethod
    async def _check_duplicate_phone(db: AsyncSession, phone: str) -> bool:
        """Check if phone number is associated with multiple accounts."""
        result = await db.execute(select(func.count(User.id)).where(User.phone == phone))
        count = result.scalar()
        return count > 1

    @staticmethod
    async def _check_suspicious_activity(db: AsyncSession, user_id: UUID) -> bool:
        """Check for suspicious activity patterns."""
        from app.models.match import Match

        # Check for mass interest sending (>50 in 24 hours)
        day_ago = datetime.now(timezone.utc) - timedelta(days=1)
        result = await db.execute(
            select(func.count(Match.id)).where(
                and_(Match.sender_id == user_id, Match.sent_at >= day_ago)
            )
        )
        interests_sent = result.scalar()
        return interests_sent > 50

    @staticmethod
    async def _check_bot_behavior(db: AsyncSession, user_id: UUID) -> bool:
        """Check for bot-like behavior patterns."""
        from app.models.chat import ChatMessage

        # Check for repetitive messages
        hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        result = await db.execute(
            select(ChatMessage.content, func.count(ChatMessage.id))
            .where(and_(ChatMessage.sender_id == user_id, ChatMessage.created_at >= hour_ago))
            .group_by(ChatMessage.content)
            .having(func.count(ChatMessage.id) > 10)
        )
        repetitive = result.all()
        return len(repetitive) > 0


fraud_service = FraudDetectionService()
