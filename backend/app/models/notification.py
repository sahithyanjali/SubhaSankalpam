import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class NotificationType(str, enum.Enum):
    INTEREST_RECEIVED = "interest_received"
    INTEREST_ACCEPTED = "interest_accepted"
    INTEREST_REJECTED = "interest_rejected"
    NEW_MESSAGE = "new_message"
    PROFILE_VIEWED = "profile_viewed"
    PROFILE_APPROVED = "profile_approved"
    PROFILE_REJECTED = "profile_rejected"
    MATCH_SUGGESTION = "match_suggestion"
    SUBSCRIPTION_EXPIRY = "subscription_expiry"
    SYSTEM = "system"
    REENGAGEMENT = "reengagement"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    notification_type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    data = Column(Text, nullable=True)  # JSON payload
    is_read = Column(Boolean, default=False)
    is_pushed = Column(Boolean, default=False)

    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="notifications")
