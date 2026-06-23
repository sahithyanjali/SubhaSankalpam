from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class VerificationResult(BaseModel):
    user_id: UUID
    verification_score: float
    trust_score: float
    identity_consistency: float
    is_verified: bool
    notes: Optional[str] = None


class FakeProfileResult(BaseModel):
    user_id: UUID
    fraud_score: float
    risk_level: str
    duplicate_photos: bool
    duplicate_phone: bool
    suspicious_activity: bool
    bot_behavior: bool
    details: Optional[str] = None


class CompatibilityResult(BaseModel):
    user1_id: UUID
    user2_id: UUID
    overall_score: float
    age_score: float
    education_score: float
    location_score: float
    religion_score: float
    caste_score: float
    lifestyle_score: float
    interests_score: float
    horoscope_score: float
    breakdown: Optional[dict] = None


class MatchRecommendation(BaseModel):
    user_id: UUID
    compatibility_score: float
    match_reason: str
    profile_summary: Optional[str] = None


class MatchRecommendationList(BaseModel):
    recommendations: list[MatchRecommendation]
    recommendation_type: str  # daily, weekly, similar


class InactiveProfileAlert(BaseModel):
    user_id: UUID
    last_active: str
    inactive_days: int
    category: str  # 30_days, 60_days, 90_days


class ChatAssistantRequest(BaseModel):
    query: str
    context: Optional[str] = None


class ChatAssistantResponse(BaseModel):
    response: str
    suggestions: list[str] = []


class ProfileImprovementSuggestion(BaseModel):
    user_id: UUID
    suggestions: list[str]
    completeness_score: int
    areas_to_improve: list[str]
