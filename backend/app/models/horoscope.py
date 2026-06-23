import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Horoscope(Base):
    __tablename__ = "horoscopes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    nakshatra = Column(String(100), nullable=True)
    rasi = Column(String(100), nullable=True)
    gothram = Column(String(100), nullable=True)
    dosham = Column(String(100), nullable=True)
    birth_time = Column(Time, nullable=True)
    birth_place = Column(String(200), nullable=True)
    horoscope_pdf_url = Column(Text, nullable=True)
    star = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="horoscope")
