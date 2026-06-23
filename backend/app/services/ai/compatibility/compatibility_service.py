import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.ai_score import AIScore, AIScoreType
from app.models.horoscope import Horoscope
from app.models.interest import UserInterest
from app.models.profile import Profile
from app.schemas.ai import CompatibilityResult


class CompatibilityService:
    """AI-powered compatibility engine for matchmaking."""

    # Horoscope compatibility matrix (Rasi-based)
    RASI_COMPATIBILITY = {
        ("Mesha", "Simha"): 90,
        ("Mesha", "Dhanu"): 85,
        ("Vrishabha", "Kanya"): 90,
        ("Vrishabha", "Makara"): 85,
        ("Mithuna", "Tula"): 90,
        ("Mithuna", "Kumbha"): 85,
        ("Karkataka", "Vrischika"): 90,
        ("Karkataka", "Meena"): 85,
        ("Simha", "Mesha"): 90,
        ("Simha", "Dhanu"): 85,
        ("Kanya", "Vrishabha"): 90,
        ("Kanya", "Makara"): 85,
        ("Tula", "Mithuna"): 90,
        ("Tula", "Kumbha"): 85,
        ("Vrischika", "Karkataka"): 90,
        ("Vrischika", "Meena"): 85,
        ("Dhanu", "Mesha"): 85,
        ("Dhanu", "Simha"): 90,
        ("Makara", "Vrishabha"): 85,
        ("Makara", "Kanya"): 90,
        ("Kumbha", "Mithuna"): 85,
        ("Kumbha", "Tula"): 90,
        ("Meena", "Karkataka"): 85,
        ("Meena", "Vrischika"): 90,
    }

    @staticmethod
    async def calculate_compatibility(
        db: AsyncSession, user1_id: UUID, user2_id: UUID
    ) -> CompatibilityResult:
        # Fetch profiles
        p1_result = await db.execute(select(Profile).where(Profile.user_id == user1_id))
        p2_result = await db.execute(select(Profile).where(Profile.user_id == user2_id))
        profile1 = p1_result.scalar_one_or_none()
        profile2 = p2_result.scalar_one_or_none()

        if not profile1 or not profile2:
            raise ValueError("Both users must have profiles")

        # Calculate individual scores
        age_score = CompatibilityService._age_compatibility(profile1, profile2)
        education_score = CompatibilityService._education_compatibility(profile1, profile2)
        location_score = CompatibilityService._location_compatibility(profile1, profile2)
        religion_score = CompatibilityService._religion_compatibility(profile1, profile2)
        caste_score = CompatibilityService._caste_compatibility(profile1, profile2)
        lifestyle_score = CompatibilityService._lifestyle_compatibility(profile1, profile2)
        interests_score = await CompatibilityService._interests_compatibility(db, user1_id, user2_id)
        horoscope_score = await CompatibilityService._horoscope_compatibility(db, user1_id, user2_id)

        # Weighted overall score
        weights = {
            "age": 0.10,
            "education": 0.10,
            "location": 0.10,
            "religion": 0.15,
            "caste": 0.15,
            "lifestyle": 0.10,
            "interests": 0.10,
            "horoscope": 0.20,
        }

        overall_score = (
            age_score * weights["age"]
            + education_score * weights["education"]
            + location_score * weights["location"]
            + religion_score * weights["religion"]
            + caste_score * weights["caste"]
            + lifestyle_score * weights["lifestyle"]
            + interests_score * weights["interests"]
            + horoscope_score * weights["horoscope"]
        )

        # Optionally enhance with Gemini AI
        if settings.GOOGLE_AI_API_KEY:
            ai_adjustment = await CompatibilityService._ai_enhance_score(profile1, profile2, overall_score)
            overall_score = (overall_score * 0.7) + (ai_adjustment * 0.3)

        overall_score = round(min(max(overall_score, 0), 100), 1)

        # Store AI score
        ai_score = AIScore(
            user_id=user1_id,
            score_type=AIScoreType.COMPATIBILITY,
            score=overall_score,
            details=json.dumps({
                "target_user_id": str(user2_id),
                "age": age_score,
                "education": education_score,
                "location": location_score,
                "religion": religion_score,
                "caste": caste_score,
                "lifestyle": lifestyle_score,
                "interests": interests_score,
                "horoscope": horoscope_score,
            }),
            model_version="v1.0",
        )
        db.add(ai_score)
        await db.commit()

        return CompatibilityResult(
            user1_id=user1_id,
            user2_id=user2_id,
            overall_score=overall_score,
            age_score=round(age_score, 1),
            education_score=round(education_score, 1),
            location_score=round(location_score, 1),
            religion_score=round(religion_score, 1),
            caste_score=round(caste_score, 1),
            lifestyle_score=round(lifestyle_score, 1),
            interests_score=round(interests_score, 1),
            horoscope_score=round(horoscope_score, 1),
        )

    @staticmethod
    def _age_compatibility(p1: Profile, p2: Profile) -> float:
        if not p1.age or not p2.age:
            return 50.0
        diff = abs(p1.age - p2.age)
        if diff <= 3:
            return 95.0
        elif diff <= 5:
            return 80.0
        elif diff <= 8:
            return 60.0
        elif diff <= 12:
            return 40.0
        return 20.0

    @staticmethod
    def _education_compatibility(p1: Profile, p2: Profile) -> float:
        if not p1.education or not p2.education:
            return 50.0

        edu_levels = {
            "phd": 6, "doctorate": 6,
            "masters": 5, "mtech": 5, "mba": 5, "ms": 5,
            "bachelors": 4, "btech": 4, "be": 4, "bsc": 4, "bcom": 4, "ba": 4,
            "diploma": 3,
            "intermediate": 2, "12th": 2,
            "ssc": 1, "10th": 1,
        }

        level1 = 3  # default
        level2 = 3
        for key, val in edu_levels.items():
            if key in p1.education.lower():
                level1 = val
                break
        for key, val in edu_levels.items():
            if key in p2.education.lower():
                level2 = val
                break

        diff = abs(level1 - level2)
        if diff == 0:
            return 95.0
        elif diff == 1:
            return 80.0
        elif diff == 2:
            return 60.0
        return 40.0

    @staticmethod
    def _location_compatibility(p1: Profile, p2: Profile) -> float:
        score = 30.0
        if p1.country and p2.country and p1.country == p2.country:
            score += 20.0
        if p1.state and p2.state and p1.state == p2.state:
            score += 20.0
        if p1.district and p2.district and p1.district == p2.district:
            score += 15.0
        if p1.city and p2.city and p1.city == p2.city:
            score += 15.0
        return min(score, 100.0)

    @staticmethod
    def _religion_compatibility(p1: Profile, p2: Profile) -> float:
        if not p1.religion or not p2.religion:
            return 50.0
        if p1.religion.lower() == p2.religion.lower():
            return 100.0
        if p1.willing_intercaste and p2.willing_intercaste:
            return 60.0
        return 20.0

    @staticmethod
    def _caste_compatibility(p1: Profile, p2: Profile) -> float:
        if not p1.caste or not p2.caste:
            return 50.0
        if p1.caste.lower() == p2.caste.lower():
            score = 90.0
            if p1.sub_caste and p2.sub_caste and p1.sub_caste.lower() == p2.sub_caste.lower():
                score = 100.0
            return score
        if p1.willing_intercaste or p2.willing_intercaste:
            return 50.0
        return 20.0

    @staticmethod
    def _lifestyle_compatibility(p1: Profile, p2: Profile) -> float:
        score = 50.0
        matches = 0
        total = 0

        if p1.eating_habit and p2.eating_habit:
            total += 1
            if p1.eating_habit == p2.eating_habit:
                matches += 1

        if p1.smoking_habit and p2.smoking_habit:
            total += 1
            if p1.smoking_habit == p2.smoking_habit:
                matches += 1

        if p1.drinking_habit and p2.drinking_habit:
            total += 1
            if p1.drinking_habit == p2.drinking_habit:
                matches += 1

        if total > 0:
            score = (matches / total) * 100

        return score

    @staticmethod
    async def _interests_compatibility(db: AsyncSession, user1_id: UUID, user2_id: UUID) -> float:
        r1 = await db.execute(select(UserInterest).where(UserInterest.user_id == user1_id))
        r2 = await db.execute(select(UserInterest).where(UserInterest.user_id == user2_id))
        interests1 = {ui.interest_id for ui in r1.scalars().all()}
        interests2 = {ui.interest_id for ui in r2.scalars().all()}

        if not interests1 or not interests2:
            return 50.0

        common = interests1 & interests2
        total = interests1 | interests2

        if not total:
            return 50.0

        return (len(common) / len(total)) * 100

    @staticmethod
    async def _horoscope_compatibility(db: AsyncSession, user1_id: UUID, user2_id: UUID) -> float:
        h1_result = await db.execute(select(Horoscope).where(Horoscope.user_id == user1_id))
        h2_result = await db.execute(select(Horoscope).where(Horoscope.user_id == user2_id))
        h1 = h1_result.scalar_one_or_none()
        h2 = h2_result.scalar_one_or_none()

        if not h1 or not h2:
            return 50.0

        score = 50.0

        # Rasi compatibility
        if h1.rasi and h2.rasi:
            rasi_score = CompatibilityService.RASI_COMPATIBILITY.get(
                (h1.rasi, h2.rasi), 50
            )
            score = rasi_score

        # Dosham compatibility
        if h1.dosham and h2.dosham:
            if h1.dosham.lower() == "yes" and h2.dosham.lower() == "yes":
                score = min(score + 10, 100)
            elif h1.dosham.lower() != h2.dosham.lower():
                score = max(score - 15, 0)

        # Gothram check (should NOT match for marriage)
        if h1.gothram and h2.gothram and h1.gothram.lower() == h2.gothram.lower():
            score = max(score - 30, 0)

        return score

    @staticmethod
    async def _ai_enhance_score(p1: Profile, p2: Profile, base_score: float) -> float:
        """Use Gemini AI for nuanced compatibility analysis."""
        try:
            import google.generativeai as genai

            genai.configure(api_key=settings.GOOGLE_AI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")

            prompt = f"""Analyze the compatibility between two matrimony profiles and return a score from 0-100.
            
Profile 1: {p1.gender.value}, Age: {p1.age}, Education: {p1.education}, 
Occupation: {p1.occupation}, City: {p1.city}, Religion: {p1.religion}, Caste: {p1.caste}

Profile 2: {p2.gender.value}, Age: {p2.age}, Education: {p2.education},
Occupation: {p2.occupation}, City: {p2.city}, Religion: {p2.religion}, Caste: {p2.caste}

Base compatibility score: {base_score}

Return ONLY a number between 0 and 100."""

            response = model.generate_content(prompt)
            return float(response.text.strip())
        except Exception:
            return base_score


compatibility_service = CompatibilityService()
