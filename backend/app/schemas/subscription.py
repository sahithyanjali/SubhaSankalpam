from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.subscription import PaymentStatus, PlanTier


class PlanResponse(BaseModel):
    id: UUID
    name: str
    tier: PlanTier
    price: float
    duration_days: int
    description: Optional[str] = None
    max_interests_per_day: int
    max_messages_per_day: int
    can_see_contact: bool
    can_see_horoscope: bool
    can_chat: bool
    priority_support: bool
    ai_match_recommendations: bool
    profile_boost: bool

    model_config = {"from_attributes": True}


class SubscribeRequest(BaseModel):
    plan_id: UUID


class SubscriptionResponse(BaseModel):
    id: UUID
    user_id: UUID
    plan: PlanResponse
    starts_at: datetime
    expires_at: datetime
    is_active: bool
    auto_renew: bool

    model_config = {"from_attributes": True}


class PaymentCreate(BaseModel):
    gateway_order_id: str
    gateway_payment_id: str
    amount: float


class PaymentResponse(BaseModel):
    id: UUID
    amount: float
    currency: str
    status: PaymentStatus
    gateway_order_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
