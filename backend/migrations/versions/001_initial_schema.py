"""Initial schema - all 13 models

Revision ID: 001_initial
Revises:
Create Date: 2024-06-23

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users table
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, index=True, nullable=True),
        sa.Column("phone", sa.String(15), unique=True, index=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column(
            "role",
            sa.Enum("user", "admin", "moderator", "support", name="userrole"),
            nullable=False,
            server_default="user",
        ),
        sa.Column(
            "status",
            sa.Enum("active", "inactive", "suspended", "pending", "deleted", name="userstatus"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "profile_for",
            sa.Enum(
                "myself",
                "son",
                "daughter",
                "brother",
                "sister",
                "relative",
                "friend",
                name="profilefor",
            ),
            nullable=False,
            server_default="myself",
        ),
        sa.Column("is_verified", sa.Boolean, server_default="false"),
        sa.Column("is_email_verified", sa.Boolean, server_default="false"),
        sa.Column("is_phone_verified", sa.Boolean, server_default="false"),
        sa.Column("verified_badge", sa.Boolean, server_default="false"),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_active", sa.DateTime(timezone=True), nullable=True),
        sa.Column("device_token", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Profiles table
    op.create_table(
        "profiles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            unique=True,
            nullable=False,
        ),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("display_name", sa.String(200), nullable=True),
        sa.Column(
            "gender",
            sa.Enum("male", "female", name="gender"),
            nullable=False,
        ),
        sa.Column("date_of_birth", sa.Date, nullable=False),
        sa.Column("age", sa.Integer, nullable=True),
        sa.Column("height_cm", sa.Float, nullable=True),
        sa.Column("weight_kg", sa.Float, nullable=True),
        sa.Column(
            "physical_status",
            sa.Enum("normal", "physically_challenged", name="physicalstatus"),
            server_default="normal",
        ),
        sa.Column(
            "marital_status",
            sa.Enum(
                "never_married",
                "divorced",
                "widowed",
                "awaiting_divorce",
                "annulled",
                name="maritalstatus",
            ),
            server_default="never_married",
        ),
        sa.Column("mother_tongue", sa.String(50), server_default="Telugu"),
        sa.Column("about_me", sa.Text, nullable=True),
        sa.Column("religion", sa.String(50), server_default="Hindu"),
        sa.Column("caste", sa.String(100), nullable=True),
        sa.Column("sub_caste", sa.String(100), nullable=True),
        sa.Column("gothram", sa.String(100), nullable=True),
        sa.Column("dosham", sa.String(50), nullable=True),
        sa.Column("willing_intercaste", sa.Boolean, server_default="false"),
        sa.Column("country", sa.String(100), server_default="India"),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("district", sa.String(100), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("education", sa.String(200), nullable=True),
        sa.Column("institution", sa.String(200), nullable=True),
        sa.Column("occupation", sa.String(200), nullable=True),
        sa.Column("organization", sa.String(200), nullable=True),
        sa.Column("annual_income", sa.String(100), nullable=True),
        sa.Column("father_occupation", sa.String(200), nullable=True),
        sa.Column("mother_occupation", sa.String(200), nullable=True),
        sa.Column("siblings", sa.Integer, nullable=True),
        sa.Column("family_values", sa.String(100), nullable=True),
        sa.Column("family_type", sa.String(50), nullable=True),
        sa.Column(
            "eating_habit",
            sa.Enum("vegetarian", "non_vegetarian", "eggetarian", "vegan", name="eatinghabit"),
            nullable=True,
        ),
        sa.Column(
            "smoking_habit",
            sa.Enum("no", "yes", "occasionally", name="smokinghabit"),
            nullable=True,
        ),
        sa.Column(
            "drinking_habit",
            sa.Enum("no", "yes", "occasionally", name="drinkinghabit"),
            nullable=True,
        ),
        sa.Column("languages", sa.Text, nullable=True),
        sa.Column(
            "approval_status",
            sa.Enum("pending", "approved", "rejected", "suspended", name="profileapprovalstatus"),
            server_default="pending",
        ),
        sa.Column("admin_notes", sa.Text, nullable=True),
        sa.Column("profile_completeness", sa.Integer, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Horoscopes table
    op.create_table(
        "horoscopes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            unique=True,
            nullable=False,
        ),
        sa.Column("nakshatra", sa.String(100), nullable=True),
        sa.Column("rasi", sa.String(100), nullable=True),
        sa.Column("gothram", sa.String(100), nullable=True),
        sa.Column("dosham", sa.String(100), nullable=True),
        sa.Column("birth_time", sa.Time, nullable=True),
        sa.Column("birth_place", sa.String(200), nullable=True),
        sa.Column("horoscope_pdf_url", sa.Text, nullable=True),
        sa.Column("star", sa.String(100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Photos table
    op.create_table(
        "photos",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "photo_type",
            sa.Enum("profile", "gallery", "family", "selfie", name="phototype"),
            nullable=False,
        ),
        sa.Column("file_url", sa.Text, nullable=False),
        sa.Column("thumbnail_url", sa.Text, nullable=True),
        sa.Column("is_primary", sa.Boolean, server_default="false"),
        sa.Column("display_order", sa.Integer, server_default="0"),
        sa.Column(
            "moderation_status",
            sa.Enum("pending", "approved", "rejected", name="photomoderationstatus"),
            server_default="pending",
        ),
        sa.Column("moderation_notes", sa.Text, nullable=True),
        sa.Column("ai_quality_score", sa.Integer, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Verifications table
    op.create_table(
        "verifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            unique=True,
            nullable=False,
        ),
        sa.Column("selfie_url", sa.Text, nullable=True),
        sa.Column("profile_photo_url", sa.Text, nullable=True),
        sa.Column(
            "verification_status",
            sa.Enum("pending", "verified", "failed", "manual_review", name="verificationstatus"),
            server_default="pending",
        ),
        sa.Column("verification_score", sa.Float, nullable=True),
        sa.Column("trust_score", sa.Float, nullable=True),
        sa.Column("identity_consistency", sa.Float, nullable=True),
        sa.Column("ai_notes", sa.Text, nullable=True),
        sa.Column("admin_notes", sa.Text, nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Interests table
    op.create_table(
        "interests",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
        sa.Column(
            "category",
            sa.Enum(
                "reading",
                "movies",
                "tv_shows",
                "sports",
                "travel",
                "fitness",
                "music",
                "cooking",
                "photography",
                "gaming",
                "other",
                name="interestcategory",
            ),
            nullable=False,
        ),
        sa.Column("icon", sa.String(50), nullable=True),
    )

    # User Interests table
    op.create_table(
        "user_interests",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "interest_id",
            UUID(as_uuid=True),
            sa.ForeignKey("interests.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("details", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Matches table
    op.create_table(
        "matches",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "sender_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "receiver_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("pending", "accepted", "rejected", "expired", name="matchstatus"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "source",
            sa.Enum("user_search", "ai_daily", "ai_weekly", "ai_similar", name="matchsource"),
            nullable=False,
            server_default="user_search",
        ),
        sa.Column("compatibility_score", sa.Float, nullable=True),
        sa.Column("horoscope_match_score", sa.Float, nullable=True),
        sa.Column("message", sa.Text, nullable=True),
        sa.Column("rejection_reason", sa.Text, nullable=True),
        sa.Column(
            "sent_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Subscription Plans table
    op.create_table(
        "subscription_plans",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column(
            "tier",
            sa.Enum("free", "silver", "gold", "platinum", name="plantier"),
            unique=True,
            nullable=False,
        ),
        sa.Column("price", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("duration_days", sa.Integer, nullable=False, server_default="30"),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("max_interests_per_day", sa.Integer, server_default="5"),
        sa.Column("max_messages_per_day", sa.Integer, server_default="10"),
        sa.Column("can_see_contact", sa.Boolean, server_default="false"),
        sa.Column("can_see_horoscope", sa.Boolean, server_default="false"),
        sa.Column("can_chat", sa.Boolean, server_default="false"),
        sa.Column("priority_support", sa.Boolean, server_default="false"),
        sa.Column("ai_match_recommendations", sa.Boolean, server_default="false"),
        sa.Column("profile_boost", sa.Boolean, server_default="false"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # User Subscriptions table
    op.create_table(
        "user_subscriptions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            unique=True,
            nullable=False,
        ),
        sa.Column(
            "plan_id",
            UUID(as_uuid=True),
            sa.ForeignKey("subscription_plans.id"),
            nullable=False,
        ),
        sa.Column(
            "starts_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("auto_renew", sa.Boolean, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Payments table
    op.create_table(
        "payments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "subscription_id",
            UUID(as_uuid=True),
            sa.ForeignKey("user_subscriptions.id"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("currency", sa.String(10), server_default="INR"),
        sa.Column("payment_gateway", sa.String(50), server_default="razorpay"),
        sa.Column("gateway_order_id", sa.String(255), nullable=True),
        sa.Column("gateway_payment_id", sa.String(255), nullable=True),
        sa.Column(
            "status",
            sa.Enum("pending", "completed", "failed", "refunded", name="paymentstatus"),
            server_default="pending",
        ),
        sa.Column("refund_reason", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Chat Rooms table
    op.create_table(
        "chat_rooms",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user1_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user2_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("active", "blocked", "closed", name="chatroomstatus"),
            server_default="active",
        ),
        sa.Column("match_id", UUID(as_uuid=True), sa.ForeignKey("matches.id"), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Chat Messages table
    op.create_table(
        "chat_messages",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "room_id",
            UUID(as_uuid=True),
            sa.ForeignKey("chat_rooms.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "sender_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column(
            "message_type",
            sa.Enum("text", "image", "system", name="messagetype"),
            server_default="text",
        ),
        sa.Column("is_read", sa.Boolean, server_default="false"),
        sa.Column("is_moderated", sa.Boolean, server_default="false"),
        sa.Column("moderation_flag", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Notifications table
    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "notification_type",
            sa.Enum(
                "interest_received",
                "interest_accepted",
                "interest_rejected",
                "new_message",
                "profile_viewed",
                "profile_approved",
                "profile_rejected",
                "match_suggestion",
                "subscription_expiry",
                "system",
                "reengagement",
                name="notificationtype",
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("data", sa.Text, nullable=True),
        sa.Column("is_read", sa.Boolean, server_default="false"),
        sa.Column("is_pushed", sa.Boolean, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Fraud Alerts table
    op.create_table(
        "fraud_alerts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "fraud_type",
            sa.Enum(
                "duplicate_photo",
                "duplicate_phone",
                "suspicious_activity",
                "bot_behavior",
                "fake_profile",
                "identity_mismatch",
                "reported_by_user",
                name="fraudtype",
            ),
            nullable=False,
        ),
        sa.Column(
            "risk_level",
            sa.Enum("low", "medium", "high", "critical", name="risklevel"),
            nullable=False,
        ),
        sa.Column("fraud_score", sa.Float, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("evidence", sa.Text, nullable=True),
        sa.Column(
            "status",
            sa.Enum("open", "investigating", "resolved", "dismissed", name="fraudalertstatus"),
            server_default="open",
        ),
        sa.Column("resolution_notes", sa.Text, nullable=True),
        sa.Column("resolved_by", UUID(as_uuid=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # AI Scores table
    op.create_table(
        "ai_scores",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "score_type",
            sa.Enum(
                "verification",
                "trust",
                "compatibility",
                "fraud",
                "photo_quality",
                "profile_completeness",
                "engagement",
                name="aiscoretype",
            ),
            nullable=False,
        ),
        sa.Column("score", sa.Float, nullable=False),
        sa.Column("details", sa.Text, nullable=True),
        sa.Column("model_version", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Audit Logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("action", sa.String(255), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=True),
        sa.Column("resource_id", sa.String(255), nullable=True),
        sa.Column("details", sa.Text, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Indexes for performance
    op.create_index("ix_profiles_gender", "profiles", ["gender"])
    op.create_index("ix_profiles_caste", "profiles", ["caste"])
    op.create_index("ix_profiles_religion", "profiles", ["religion"])
    op.create_index("ix_profiles_city", "profiles", ["city"])
    op.create_index("ix_profiles_state", "profiles", ["state"])
    op.create_index("ix_profiles_approval_status", "profiles", ["approval_status"])
    op.create_index("ix_matches_sender_id", "matches", ["sender_id"])
    op.create_index("ix_matches_receiver_id", "matches", ["receiver_id"])
    op.create_index("ix_matches_status", "matches", ["status"])
    op.create_index("ix_chat_messages_room_id", "chat_messages", ["room_id"])
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_is_read", "notifications", ["is_read"])
    op.create_index("ix_fraud_alerts_user_id", "fraud_alerts", ["user_id"])
    op.create_index("ix_fraud_alerts_status", "fraud_alerts", ["status"])
    op.create_index("ix_ai_scores_user_id", "ai_scores", ["user_id"])
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("ai_scores")
    op.drop_table("fraud_alerts")
    op.drop_table("notifications")
    op.drop_table("chat_messages")
    op.drop_table("chat_rooms")
    op.drop_table("payments")
    op.drop_table("user_subscriptions")
    op.drop_table("subscription_plans")
    op.drop_table("matches")
    op.drop_table("user_interests")
    op.drop_table("interests")
    op.drop_table("verifications")
    op.drop_table("photos")
    op.drop_table("horoscopes")
    op.drop_table("profiles")
    op.drop_table("users")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS userstatus")
    op.execute("DROP TYPE IF EXISTS profilefor")
    op.execute("DROP TYPE IF EXISTS gender")
    op.execute("DROP TYPE IF EXISTS physicalstatus")
    op.execute("DROP TYPE IF EXISTS maritalstatus")
    op.execute("DROP TYPE IF EXISTS eatinghabit")
    op.execute("DROP TYPE IF EXISTS smokinghabit")
    op.execute("DROP TYPE IF EXISTS drinkinghabit")
    op.execute("DROP TYPE IF EXISTS profileapprovalstatus")
    op.execute("DROP TYPE IF EXISTS phototype")
    op.execute("DROP TYPE IF EXISTS photomoderationstatus")
    op.execute("DROP TYPE IF EXISTS verificationstatus")
    op.execute("DROP TYPE IF EXISTS interestcategory")
    op.execute("DROP TYPE IF EXISTS matchstatus")
    op.execute("DROP TYPE IF EXISTS matchsource")
    op.execute("DROP TYPE IF EXISTS plantier")
    op.execute("DROP TYPE IF EXISTS paymentstatus")
    op.execute("DROP TYPE IF EXISTS chatroomstatus")
    op.execute("DROP TYPE IF EXISTS messagetype")
    op.execute("DROP TYPE IF EXISTS notificationtype")
    op.execute("DROP TYPE IF EXISTS fraudtype")
    op.execute("DROP TYPE IF EXISTS risklevel")
    op.execute("DROP TYPE IF EXISTS fraudalertstatus")
    op.execute("DROP TYPE IF EXISTS aiscoretype")
