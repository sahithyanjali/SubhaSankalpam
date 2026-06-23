from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.match import MatchSource, MatchStatus


class SendInterest(BaseModel):
    receiver_id: UUID
    message: Optional[str] = None


class RespondInterest(BaseModel):
    status: MatchStatus
    rejection_reason: Optional[str] = None


class MatchResponse(BaseModel):
    id: UUID
    sender_id: UUID
    receiver_id: UUID
    status: MatchStatus
    source: MatchSource
    compatibility_score: Optional[float] = None
    horoscope_match_score: Optional[float] = None
    message: Optional[str] = None
    sent_at: datetime
    responded_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class MatchListResponse(BaseModel):
    matches: list[MatchResponse]
    total: int
    page: int
    page_size: int
