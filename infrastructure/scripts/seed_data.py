"""Seed initial data for SubhaSankalpam."""
import asyncio
import uuid

from sqlalchemy import select

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.interest import Interest, InterestCategory
from app.models.subscription import PlanTier, SubscriptionPlan


async def seed_subscription_plans():
    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(SubscriptionPlan))
        if existing.scalars().first():
            print("Plans already seeded.")
            return

        plans = [
            SubscriptionPlan(
                name="Free",
                tier=PlanTier.FREE,
                price=0,
                duration_days=365,
                description="Basic free plan with limited features",
                max_interests_per_day=3,
                max_messages_per_day=5,
                can_see_contact=False,
                can_see_horoscope=False,
                can_chat=False,
                priority_support=False,
                ai_match_recommendations=False,
                profile_boost=False,
            ),
            SubscriptionPlan(
                name="Silver",
                tier=PlanTier.SILVER,
                price=999,
                duration_days=30,
                description="Silver plan with enhanced features",
                max_interests_per_day=10,
                max_messages_per_day=20,
                can_see_contact=True,
                can_see_horoscope=False,
                can_chat=True,
                priority_support=False,
                ai_match_recommendations=False,
                profile_boost=False,
            ),
            SubscriptionPlan(
                name="Gold",
                tier=PlanTier.GOLD,
                price=2499,
                duration_days=90,
                description="Gold plan with premium features",
                max_interests_per_day=25,
                max_messages_per_day=50,
                can_see_contact=True,
                can_see_horoscope=True,
                can_chat=True,
                priority_support=True,
                ai_match_recommendations=True,
                profile_boost=False,
            ),
            SubscriptionPlan(
                name="Platinum",
                tier=PlanTier.PLATINUM,
                price=4999,
                duration_days=180,
                description="Platinum plan with all features unlocked",
                max_interests_per_day=999,
                max_messages_per_day=999,
                can_see_contact=True,
                can_see_horoscope=True,
                can_chat=True,
                priority_support=True,
                ai_match_recommendations=True,
                profile_boost=True,
            ),
        ]
        for plan in plans:
            db.add(plan)
        await db.commit()
        print("Subscription plans seeded.")


async def seed_interests():
    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(Interest))
        if existing.scalars().first():
            print("Interests already seeded.")
            return

        interests = [
            ("Reading", InterestCategory.READING, "book"),
            ("Movies", InterestCategory.MOVIES, "movie"),
            ("TV Shows", InterestCategory.TV_SHOWS, "tv"),
            ("Cricket", InterestCategory.SPORTS, "sports_cricket"),
            ("Football", InterestCategory.SPORTS, "sports_soccer"),
            ("Badminton", InterestCategory.SPORTS, "sports_tennis"),
            ("Travel", InterestCategory.TRAVEL, "flight"),
            ("Fitness", InterestCategory.FITNESS, "fitness_center"),
            ("Music", InterestCategory.MUSIC, "music_note"),
            ("Cooking", InterestCategory.COOKING, "restaurant"),
            ("Photography", InterestCategory.PHOTOGRAPHY, "camera"),
            ("Gaming", InterestCategory.GAMING, "sports_esports"),
            ("Yoga", InterestCategory.FITNESS, "self_improvement"),
            ("Dancing", InterestCategory.MUSIC, "music_note"),
            ("Painting", InterestCategory.OTHER, "palette"),
        ]

        for name, category, icon in interests:
            db.add(Interest(name=name, category=category, icon=icon))

        await db.commit()
        print("Interests seeded.")


async def main():
    await seed_subscription_plans()
    await seed_interests()


if __name__ == "__main__":
    asyncio.run(main())
