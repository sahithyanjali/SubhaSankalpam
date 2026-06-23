from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.profile import (
    DrinkingHabit,
    EatingHabit,
    Gender,
    MaritalStatus,
    PhysicalStatus,
    ProfileApprovalStatus,
    SmokingHabit,
)


class ProfileCreate(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    display_name: Optional[str] = None
    gender: Gender
    date_of_birth: date
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    physical_status: PhysicalStatus = PhysicalStatus.NORMAL
    marital_status: MaritalStatus = MaritalStatus.NEVER_MARRIED
    mother_tongue: str = "Telugu"
    about_me: Optional[str] = None

    # Religion
    religion: str = "Hindu"
    caste: Optional[str] = None
    sub_caste: Optional[str] = None
    gothram: Optional[str] = None
    dosham: Optional[str] = None
    willing_intercaste: bool = False

    # Location
    country: str = "India"
    state: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None

    # Professional
    education: Optional[str] = None
    institution: Optional[str] = None
    occupation: Optional[str] = None
    organization: Optional[str] = None
    annual_income: Optional[str] = None

    # Family
    father_occupation: Optional[str] = None
    mother_occupation: Optional[str] = None
    siblings: Optional[int] = None
    family_values: Optional[str] = None
    family_type: Optional[str] = None

    # Lifestyle
    eating_habit: Optional[EatingHabit] = None
    smoking_habit: Optional[SmokingHabit] = None
    drinking_habit: Optional[DrinkingHabit] = None

    # Languages
    languages: Optional[str] = None


class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    physical_status: Optional[PhysicalStatus] = None
    marital_status: Optional[MaritalStatus] = None
    mother_tongue: Optional[str] = None
    about_me: Optional[str] = None
    religion: Optional[str] = None
    caste: Optional[str] = None
    sub_caste: Optional[str] = None
    gothram: Optional[str] = None
    dosham: Optional[str] = None
    willing_intercaste: Optional[bool] = None
    country: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    education: Optional[str] = None
    institution: Optional[str] = None
    occupation: Optional[str] = None
    organization: Optional[str] = None
    annual_income: Optional[str] = None
    father_occupation: Optional[str] = None
    mother_occupation: Optional[str] = None
    siblings: Optional[int] = None
    family_values: Optional[str] = None
    family_type: Optional[str] = None
    eating_habit: Optional[EatingHabit] = None
    smoking_habit: Optional[SmokingHabit] = None
    drinking_habit: Optional[DrinkingHabit] = None
    languages: Optional[str] = None


class ProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    first_name: str
    last_name: str
    display_name: Optional[str] = None
    gender: Gender
    date_of_birth: date
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    physical_status: Optional[PhysicalStatus] = None
    marital_status: Optional[MaritalStatus] = None
    mother_tongue: Optional[str] = None
    about_me: Optional[str] = None
    religion: Optional[str] = None
    caste: Optional[str] = None
    sub_caste: Optional[str] = None
    gothram: Optional[str] = None
    dosham: Optional[str] = None
    willing_intercaste: bool = False
    country: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    education: Optional[str] = None
    institution: Optional[str] = None
    occupation: Optional[str] = None
    organization: Optional[str] = None
    annual_income: Optional[str] = None
    father_occupation: Optional[str] = None
    mother_occupation: Optional[str] = None
    siblings: Optional[int] = None
    family_values: Optional[str] = None
    eating_habit: Optional[EatingHabit] = None
    smoking_habit: Optional[SmokingHabit] = None
    drinking_habit: Optional[DrinkingHabit] = None
    languages: Optional[str] = None
    approval_status: ProfileApprovalStatus
    profile_completeness: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ProfileSearchFilters(BaseModel):
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    gender: Optional[Gender] = None
    caste: Optional[str] = None
    religion: Optional[str] = None
    min_height: Optional[float] = None
    max_height: Optional[float] = None
    education: Optional[str] = None
    min_income: Optional[str] = None
    location: Optional[str] = None
    marital_status: Optional[MaritalStatus] = None
    mother_tongue: Optional[str] = None
    willing_intercaste: Optional[bool] = None
    dosham: Optional[str] = None
    page: int = 1
    page_size: int = 20


class ProfileListResponse(BaseModel):
    profiles: list[ProfileResponse]
    total: int
    page: int
    page_size: int
