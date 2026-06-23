import json
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.profile import Profile
from app.schemas.ai import ChatAssistantResponse, ProfileImprovementSuggestion


class ChatAssistantService:
    """AI Chat Assistant using Gemini/OpenAI + LangChain for user queries."""

    SYSTEM_PROMPT = """You are SubhaSankalpam AI Assistant - a helpful matrimony advisor for Telugu users.
You help users with:
1. Finding compatible matches
2. Improving their profiles
3. Explaining compatibility scores
4. Horoscope insights and compatibility
5. General matrimony advice

Always be respectful, culturally sensitive, and supportive.
Respond in English but understand Telugu cultural contexts.
Keep responses concise and actionable."""

    @staticmethod
    async def chat(
        db: AsyncSession, user_id: UUID, query: str, context: Optional[str] = None
    ) -> ChatAssistantResponse:
        # Get user profile for context
        profile_result = await db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = profile_result.scalar_one_or_none()

        user_context = ""
        if profile:
            user_context = f"""
User Profile: {profile.first_name}, {profile.gender.value}, Age: {profile.age},
Education: {profile.education}, Location: {profile.city}, {profile.state},
Religion: {profile.religion}, Caste: {profile.caste}"""

        # Try Gemini first, then OpenAI
        response_text = await ChatAssistantService._get_ai_response(
            query, user_context, context
        )

        suggestions = ChatAssistantService._generate_suggestions(query)

        return ChatAssistantResponse(
            response=response_text,
            suggestions=suggestions,
        )

    @staticmethod
    async def get_profile_suggestions(
        db: AsyncSession, user_id: UUID
    ) -> ProfileImprovementSuggestion:
        profile_result = await db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = profile_result.scalar_one_or_none()

        suggestions = []
        areas = []
        completeness = 0

        if profile:
            total_fields = 25
            filled = 0

            fields_check = [
                (profile.about_me, "Add a detailed 'About Me' section", "about_me"),
                (profile.education, "Add your education details", "education"),
                (profile.occupation, "Add your occupation", "occupation"),
                (profile.annual_income, "Specify your annual income range", "income"),
                (profile.city, "Add your current city", "location"),
                (profile.height_cm, "Add your height", "physical"),
                (profile.eating_habit, "Specify your eating habits", "lifestyle"),
                (profile.father_occupation, "Add family details", "family"),
                (profile.languages, "Add languages you speak", "languages"),
                (profile.caste, "Specify your caste details", "religion"),
            ]

            for value, suggestion, area in fields_check:
                if value:
                    filled += 1
                else:
                    suggestions.append(suggestion)
                    if area not in areas:
                        areas.append(area)

            # Count other filled fields
            basic_fields = [
                profile.first_name,
                profile.last_name,
                profile.gender,
                profile.date_of_birth,
            ]
            filled += sum(1 for f in basic_fields if f)
            filled += 1  # always have user_id

            completeness = min(int((filled / total_fields) * 100), 100)

            # AI-powered suggestions
            if settings.GOOGLE_AI_API_KEY:
                ai_suggestions = await ChatAssistantService._get_ai_profile_tips(
                    profile
                )
                suggestions.extend(ai_suggestions)
        else:
            suggestions = ["Create your profile to get started"]
            areas = ["profile"]
            completeness = 0

        return ProfileImprovementSuggestion(
            user_id=user_id,
            suggestions=suggestions[:10],
            completeness_score=completeness,
            areas_to_improve=areas,
        )

    @staticmethod
    async def _get_ai_response(
        query: str, user_context: str, extra_context: Optional[str]
    ) -> str:
        full_context = f"{user_context}\n{extra_context or ''}"

        # Try Gemini
        if settings.GOOGLE_AI_API_KEY:
            try:
                import google.generativeai as genai

                genai.configure(api_key=settings.GOOGLE_AI_API_KEY)
                model = genai.GenerativeModel("gemini-1.5-flash")

                prompt = f"""{ChatAssistantService.SYSTEM_PROMPT}

Context: {full_context}

User Query: {query}

Provide a helpful, concise response."""

                response = model.generate_content(prompt)
                return response.text
            except Exception:
                pass

        # Try OpenAI
        if settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI

                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": ChatAssistantService.SYSTEM_PROMPT,
                        },
                        {
                            "role": "user",
                            "content": f"Context: {full_context}\n\nQuery: {query}",
                        },
                    ],
                    max_tokens=500,
                )
                return response.choices[0].message.content
            except Exception:
                pass

        # Fallback responses
        return ChatAssistantService._fallback_response(query)

    @staticmethod
    def _fallback_response(query: str) -> str:
        query_lower = query.lower()
        if "match" in query_lower or "find" in query_lower:
            return (
                "Use our search filters to find compatible matches. "
                "You can filter by age, caste, education, location, and more. "
                "Check your daily AI recommendations for personalized suggestions."
            )
        elif "profile" in query_lower or "improve" in query_lower:
            return (
                "To improve your profile: add a detailed 'About Me', upload multiple photos, "
                "complete all sections including education, occupation, and horoscope details. "
                "A complete profile gets 5x more interest requests."
            )
        elif "compatibility" in query_lower or "score" in query_lower:
            return (
                "Our compatibility score considers: religion, caste, education, location, "
                "lifestyle, interests, age, and horoscope matching. "
                "Scores above 70% indicate strong compatibility."
            )
        elif "horoscope" in query_lower:
            return (
                "Upload your horoscope PDF and fill in Nakshatra, Rasi, and Gothram details. "
                "Our AI matches horoscopes based on traditional Telugu astrological compatibility. "
                "Same Gothram matches are flagged as per tradition."
            )
        return (
            "I'm your SubhaSankalpam AI assistant. I can help you find matches, "
            "improve your profile, explain compatibility, and provide horoscope insights. "
            "What would you like to know?"
        )

    @staticmethod
    def _generate_suggestions(query: str) -> list[str]:
        return [
            "Find me matches",
            "How to improve my profile?",
            "Explain compatibility score",
            "Horoscope matching details",
            "Subscription benefits",
        ]

    @staticmethod
    async def _get_ai_profile_tips(profile: Profile) -> list[str]:
        try:
            import google.generativeai as genai

            genai.configure(api_key=settings.GOOGLE_AI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")

            prompt = f"""Given this matrimony profile, suggest 3 specific improvements:
Name: {profile.first_name}, Education: {profile.education}, 
Occupation: {profile.occupation}, About: {profile.about_me}

Return 3 short, actionable suggestions as a JSON array of strings."""

            response = model.generate_content(prompt)
            return json.loads(response.text)
        except Exception:
            return []


chat_assistant_service = ChatAssistantService()
