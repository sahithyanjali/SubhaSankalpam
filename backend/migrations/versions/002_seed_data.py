"""Seed subscription plans and interests

Revision ID: 002_seed_data
Revises: 001_initial
Create Date: 2024-06-23

"""

import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = "002_seed_data"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Seed Subscription Plans
    plans_table = sa.table(
        "subscription_plans",
        sa.column("id", UUID(as_uuid=True)),
        sa.column("name", sa.String),
        sa.column("tier", sa.String),
        sa.column("price", sa.Float),
        sa.column("duration_days", sa.Integer),
        sa.column("description", sa.Text),
        sa.column("max_interests_per_day", sa.Integer),
        sa.column("max_messages_per_day", sa.Integer),
        sa.column("can_see_contact", sa.Boolean),
        sa.column("can_see_horoscope", sa.Boolean),
        sa.column("can_chat", sa.Boolean),
        sa.column("priority_support", sa.Boolean),
        sa.column("ai_match_recommendations", sa.Boolean),
        sa.column("profile_boost", sa.Boolean),
        sa.column("is_active", sa.Boolean),
    )

    op.bulk_insert(
        plans_table,
        [
            {
                "id": str(uuid.uuid4()),
                "name": "Free Plan",
                "tier": "free",
                "price": 0.0,
                "duration_days": 365,
                "description": "Basic access to browse and send limited interests",
                "max_interests_per_day": 3,
                "max_messages_per_day": 5,
                "can_see_contact": False,
                "can_see_horoscope": False,
                "can_chat": False,
                "priority_support": False,
                "ai_match_recommendations": False,
                "profile_boost": False,
                "is_active": True,
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Silver Plan",
                "tier": "silver",
                "price": 999.0,
                "duration_days": 90,
                "description": "Enhanced matching with chat access and horoscope viewing",
                "max_interests_per_day": 10,
                "max_messages_per_day": 30,
                "can_see_contact": False,
                "can_see_horoscope": True,
                "can_chat": True,
                "priority_support": False,
                "ai_match_recommendations": False,
                "profile_boost": False,
                "is_active": True,
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Gold Plan",
                "tier": "gold",
                "price": 2499.0,
                "duration_days": 180,
                "description": "Premium features with contact visibility and AI recommendations",
                "max_interests_per_day": 25,
                "max_messages_per_day": 100,
                "can_see_contact": True,
                "can_see_horoscope": True,
                "can_chat": True,
                "priority_support": True,
                "ai_match_recommendations": True,
                "profile_boost": False,
                "is_active": True,
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Platinum Plan",
                "tier": "platinum",
                "price": 4999.0,
                "duration_days": 365,
                "description": "All-inclusive with profile boost, AI assistant, and priority support",
                "max_interests_per_day": 50,
                "max_messages_per_day": 500,
                "can_see_contact": True,
                "can_see_horoscope": True,
                "can_chat": True,
                "priority_support": True,
                "ai_match_recommendations": True,
                "profile_boost": True,
                "is_active": True,
            },
        ],
    )

    # Seed Interests
    interests_table = sa.table(
        "interests",
        sa.column("id", UUID(as_uuid=True)),
        sa.column("name", sa.String),
        sa.column("category", sa.String),
        sa.column("icon", sa.String),
    )

    interests_data = [
        ("Fiction Reading", "reading", "book"),
        ("Non-Fiction Reading", "reading", "library_books"),
        ("Poetry", "reading", "auto_stories"),
        ("Bollywood Movies", "movies", "movie"),
        ("Tollywood Movies", "movies", "theaters"),
        ("Hollywood Movies", "movies", "local_movies"),
        ("Anime", "movies", "animation"),
        ("Drama Series", "tv_shows", "tv"),
        ("Comedy Shows", "tv_shows", "sentiment_very_satisfied"),
        ("Cricket", "sports", "sports_cricket"),
        ("Badminton", "sports", "sports_tennis"),
        ("Football", "sports", "sports_soccer"),
        ("Yoga", "fitness", "self_improvement"),
        ("Gym Workouts", "fitness", "fitness_center"),
        ("Running", "fitness", "directions_run"),
        ("Swimming", "fitness", "pool"),
        ("Domestic Travel", "travel", "flight_takeoff"),
        ("International Travel", "travel", "public"),
        ("Trekking", "travel", "terrain"),
        ("Classical Music", "music", "music_note"),
        ("Playback Songs", "music", "queue_music"),
        ("Western Music", "music", "headphones"),
        ("Cooking", "cooking", "restaurant"),
        ("Baking", "cooking", "cake"),
        ("Photography", "photography", "camera_alt"),
        ("Videography", "photography", "videocam"),
        ("Mobile Gaming", "gaming", "phone_android"),
        ("PC Gaming", "gaming", "computer"),
        ("Temple Visits", "other", "temple_hindu"),
        ("Volunteering", "other", "volunteer_activism"),
    ]

    op.bulk_insert(
        interests_table,
        [
            {"id": str(uuid.uuid4()), "name": name, "category": cat, "icon": icon}
            for name, cat, icon in interests_data
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM interests")
    op.execute("DELETE FROM subscription_plans")
