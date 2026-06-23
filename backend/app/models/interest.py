import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class InterestCategory(str, enum.Enum):
    READING = "reading"
    MOVIES = "movies"
    TV_SHOWS = "tv_shows"
    SPORTS = "sports"
    TRAVEL = "travel"
    FITNESS = "fitness"
    MUSIC = "music"
    COOKING = "cooking"
    PHOTOGRAPHY = "photography"
    GAMING = "gaming"
    OTHER = "other"


class Interest(Base):
    __tablename__ = "interests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(Enum(InterestCategory), nullable=False)
    icon = Column(String(50), nullable=True)

    user_interests = relationship("UserInterest", back_populates="interest")


class UserInterest(Base):
    __tablename__ = "user_interests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    interest_id = Column(UUID(as_uuid=True), ForeignKey("interests.id", ondelete="CASCADE"), nullable=False)
    details = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="user_interests")
    interest = relationship("Interest", back_populates="user_interests")
