import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"


class MaritalStatus(str, enum.Enum):
    NEVER_MARRIED = "never_married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"
    AWAITING_DIVORCE = "awaiting_divorce"
    ANNULLED = "annulled"


class PhysicalStatus(str, enum.Enum):
    NORMAL = "normal"
    PHYSICALLY_CHALLENGED = "physically_challenged"


class EatingHabit(str, enum.Enum):
    VEGETARIAN = "vegetarian"
    NON_VEGETARIAN = "non_vegetarian"
    EGGETARIAN = "eggetarian"
    VEGAN = "vegan"


class SmokingHabit(str, enum.Enum):
    NO = "no"
    YES = "yes"
    OCCASIONALLY = "occasionally"


class DrinkingHabit(str, enum.Enum):
    NO = "no"
    YES = "yes"
    OCCASIONALLY = "occasionally"


class ProfileApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    display_name = Column(String(200), nullable=True)
    gender = Column(Enum(Gender), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    age = Column(Integer, nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    physical_status = Column(Enum(PhysicalStatus), default=PhysicalStatus.NORMAL)
    marital_status = Column(Enum(MaritalStatus), default=MaritalStatus.NEVER_MARRIED)
    mother_tongue = Column(String(50), default="Telugu")
    about_me = Column(Text, nullable=True)

    # Religion & Caste
    religion = Column(String(50), default="Hindu")
    caste = Column(String(100), nullable=True)
    sub_caste = Column(String(100), nullable=True)
    gothram = Column(String(100), nullable=True)
    dosham = Column(String(50), nullable=True)
    willing_intercaste = Column(Boolean, default=False)

    # Location
    country = Column(String(100), default="India")
    state = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)

    # Professional
    education = Column(String(200), nullable=True)
    institution = Column(String(200), nullable=True)
    occupation = Column(String(200), nullable=True)
    organization = Column(String(200), nullable=True)
    annual_income = Column(String(100), nullable=True)

    # Family
    father_occupation = Column(String(200), nullable=True)
    mother_occupation = Column(String(200), nullable=True)
    siblings = Column(Integer, nullable=True)
    family_values = Column(String(100), nullable=True)
    family_type = Column(String(50), nullable=True)

    # Lifestyle
    eating_habit = Column(Enum(EatingHabit), nullable=True)
    smoking_habit = Column(Enum(SmokingHabit), nullable=True)
    drinking_habit = Column(Enum(DrinkingHabit), nullable=True)

    # Languages
    languages = Column(Text, nullable=True)  # JSON array stored as text

    # Admin
    approval_status = Column(Enum(ProfileApprovalStatus), default=ProfileApprovalStatus.PENDING)
    admin_notes = Column(Text, nullable=True)
    profile_completeness = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = relationship("User", back_populates="profile")
