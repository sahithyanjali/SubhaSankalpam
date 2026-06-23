import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class PhotoType(str, enum.Enum):
    PROFILE = "profile"
    GALLERY = "gallery"
    FAMILY = "family"
    SELFIE = "selfie"


class PhotoModerationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Photo(Base):
    __tablename__ = "photos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    photo_type = Column(Enum(PhotoType), nullable=False)
    file_url = Column(Text, nullable=False)
    thumbnail_url = Column(Text, nullable=True)
    is_primary = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    moderation_status = Column(
        Enum(PhotoModerationStatus), default=PhotoModerationStatus.PENDING
    )
    moderation_notes = Column(Text, nullable=True)
    ai_quality_score = Column(Integer, nullable=True)

    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="photos")
