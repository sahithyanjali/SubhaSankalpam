import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class AIScoreType(str, enum.Enum):
    VERIFICATION = "verification"
    TRUST = "trust"
    COMPATIBILITY = "compatibility"
    FRAUD = "fraud"
    PHOTO_QUALITY = "photo_quality"
    PROFILE_COMPLETENESS = "profile_completeness"
    ENGAGEMENT = "engagement"


class AIScore(Base):
    __tablename__ = "ai_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    score_type = Column(Enum(AIScoreType), nullable=False)
    score = Column(Float, nullable=False)
    details = Column(Text, nullable=True)  # JSON with breakdown
    model_version = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="ai_scores")
