from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_admin_user, get_current_active_user
from app.models.user import User
from app.schemas.ai import (
    ChatAssistantRequest,
    ChatAssistantResponse,
    CompatibilityResult,
    FakeProfileResult,
    InactiveProfileAlert,
    MatchRecommendationList,
    ProfileImprovementSuggestion,
    VerificationResult,
)
from app.services.ai.chat_assistant.assistant_service import chat_assistant_service
from app.services.ai.compatibility.compatibility_service import compatibility_service
from app.services.ai.fraud.fraud_service import fraud_service
from app.services.ai.recommendations.recommendation_service import (
    recommendation_service,
)
from app.services.ai.verification.verification_service import verification_service

router = APIRouter(prefix="/ai", tags=["AI Intelligence"])


# --- Profile Verification ---
@router.post("/verify/{user_id}", response_model=VerificationResult)
async def ai_verify_profile(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """AI profile verification: selfie comparison, trust score, identity consistency."""
    result = await verification_service.verify_profile(db, user_id)
    return result


# --- Fake Profile Detection ---
@router.post("/fraud-check/{user_id}", response_model=FakeProfileResult)
async def ai_fraud_check(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """AI fake profile detection: duplicate photos, phones, suspicious activity, bot behavior."""
    result = await fraud_service.analyze_profile(db, user_id)
    return result


# --- Compatibility Engine ---
@router.get("/compatibility/{user1_id}/{user2_id}", response_model=CompatibilityResult)
async def get_compatibility(
    user1_id: UUID,
    user2_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """AI compatibility score (0-100) based on age, education, location, religion, caste, lifestyle, interests, horoscope."""
    result = await compatibility_service.calculate_compatibility(db, user1_id, user2_id)
    return result


# --- Match Recommendations ---
@router.get("/recommendations/daily", response_model=MatchRecommendationList)
async def get_daily_recommendations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """AI-generated daily match recommendations."""
    return await recommendation_service.get_daily_matches(db, current_user.id)


@router.get("/recommendations/weekly", response_model=MatchRecommendationList)
async def get_weekly_recommendations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """AI-generated weekly match recommendations."""
    return await recommendation_service.get_weekly_matches(db, current_user.id)


@router.get("/recommendations/similar", response_model=MatchRecommendationList)
async def get_similar_profiles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """AI-generated similar profile recommendations."""
    return await recommendation_service.get_similar_profiles(db, current_user.id)


# --- Inactive Profile Detection ---
@router.get("/inactive-profiles", response_model=list[InactiveProfileAlert])
async def get_inactive_profiles(
    days: int = Query(30, ge=30, le=90),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Detect inactive profiles (30/60/90 days)."""
    return await recommendation_service.detect_inactive_profiles(db, days)


# --- AI Chat Assistant ---
@router.post("/chat-assistant", response_model=ChatAssistantResponse)
async def chat_with_assistant(
    request: ChatAssistantRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """AI chat assistant: find matches, improve profile, explain compatibility, horoscope insights."""
    return await chat_assistant_service.chat(db, current_user.id, request.query, request.context)


# --- Profile Improvement Suggestions ---
@router.get("/profile-suggestions", response_model=ProfileImprovementSuggestion)
async def get_profile_suggestions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """AI-powered profile improvement suggestions."""
    return await chat_assistant_service.get_profile_suggestions(db, current_user.id)
