from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.fraud import FraudAlertStatus, FraudType, RiskLevel
from app.models.profile import ProfileApprovalStatus


class AdminDashboard(BaseModel):
    total_users: int
    verified_users: int
    pending_verification: int
    active_users: int
    subscription_revenue: float
    fraud_alerts: int
    profiles_pending_review: int


class ProfileReviewAction(BaseModel):
    status: ProfileApprovalStatus
    notes: Optional[str] = None


class FraudAlertResponse(BaseModel):
    id: UUID
    user_id: UUID
    fraud_type: FraudType
    risk_level: RiskLevel
    fraud_score: Optional[float] = None
    description: Optional[str] = None
    status: FraudAlertStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class FraudAlertUpdate(BaseModel):
    status: FraudAlertStatus
    resolution_notes: Optional[str] = None


class SupportTicketCreate(BaseModel):
    subject: str
    description: str
    priority: str = "medium"


class SupportTicketResponse(BaseModel):
    id: UUID
    user_id: UUID
    subject: str
    description: str
    priority: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ReportRequest(BaseModel):
    report_type: str  # user, revenue, fraud
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ReportResponse(BaseModel):
    report_type: str
    data: dict
    generated_at: datetime


class AuditLogResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    logs: list[AuditLogResponse]
    total: int
    page: int
    page_size: int
