import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class MatchStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class MatchSource(str, enum.Enum):
    USER_SEARCH = "user_search"
    AI_DAILY = "ai_daily"
    AI_WEEKLY = "ai_weekly"
    AI_SIMILAR = "ai_similar"


class Match(Base):
    __tablename__ = "matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    receiver_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    status = Column(Enum(MatchStatus), default=MatchStatus.PENDING, nullable=False)
    source = Column(Enum(MatchSource), default=MatchSource.USER_SEARCH, nullable=False)
    compatibility_score = Column(Float, nullable=True)
    horoscope_match_score = Column(Float, nullable=True)
    message = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    sent_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    responded_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    sender = relationship(
        "User", foreign_keys=[sender_id], back_populates="sent_matches"
    )
    receiver = relationship(
        "User", foreign_keys=[receiver_id], back_populates="received_matches"
    )
