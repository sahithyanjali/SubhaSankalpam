import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class FraudType(str, enum.Enum):
    DUPLICATE_PHOTO = "duplicate_photo"
    DUPLICATE_PHONE = "duplicate_phone"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    BOT_BEHAVIOR = "bot_behavior"
    FAKE_PROFILE = "fake_profile"
    IDENTITY_MISMATCH = "identity_mismatch"
    REPORTED_BY_USER = "reported_by_user"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FraudAlertStatus(str, enum.Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class FraudAlert(Base):
    __tablename__ = "fraud_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    fraud_type = Column(Enum(FraudType), nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False)
    fraud_score = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    evidence = Column(Text, nullable=True)  # JSON
    status = Column(Enum(FraudAlertStatus), default=FraudAlertStatus.OPEN)
    resolution_notes = Column(Text, nullable=True)
    resolved_by = Column(UUID(as_uuid=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="fraud_alerts")
