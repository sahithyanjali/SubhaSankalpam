from datetime import datetime, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class HoroscopeCreate(BaseModel):
    nakshatra: Optional[str] = None
    rasi: Optional[str] = None
    gothram: Optional[str] = None
    dosham: Optional[str] = None
    birth_time: Optional[time] = None
    birth_place: Optional[str] = None
    star: Optional[str] = None


class HoroscopeUpdate(HoroscopeCreate):
    pass


class HoroscopeResponse(BaseModel):
    id: UUID
    user_id: UUID
    nakshatra: Optional[str] = None
    rasi: Optional[str] = None
    gothram: Optional[str] = None
    dosham: Optional[str] = None
    birth_time: Optional[time] = None
    birth_place: Optional[str] = None
    star: Optional[str] = None
    horoscope_pdf_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
