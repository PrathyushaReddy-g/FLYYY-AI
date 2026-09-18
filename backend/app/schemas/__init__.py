from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# Authentication Schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str


# Discovery Schemas
class DiscoveryField(BaseModel):
    field_name: str
    data_type: str
    classification: str
    confidence: float
    recommended_protection: str
    sample_masked: Optional[str] = None

class DiscoveryResponse(BaseModel):
    fields: List[DiscoveryField]
    total_fields: int
    discovered_at: str


# Policy Schemas
class PolicyItem(BaseModel):
    field_name: str
    classification: str
    protection_method: str  # KEEP, TOKENIZE, FPE, ENCRYPT, MASK
    enabled: bool = True
    deterministic: bool = True
    version: int = 1

class PolicyUpdateRequest(BaseModel):
    policies: List[PolicyItem]

class PolicyResponse(BaseModel):
    policies: List[PolicyItem]
    active_version: int


# Batch Schemas
class BatchRunRequest(BaseModel):
    source: str = "DATABASE"  # DATABASE or CSV
    batch_size: int = Field(default=1000, ge=1, le=100000)

class BatchRunResponse(BaseModel):
    batch_id: str
    source: str
    start_time: str
    end_time: Optional[str] = None
    status: str
    batch_size: int
    processed_rows: int
    success_count: int
    error_count: int
    error_summary: Optional[str] = None


# Customer Schemas
class ProtectedCustomerResponse(BaseModel):
    customer_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    city: Optional[str] = None
    segment: Optional[str] = None
    protection_version: int = 1
    created_at: Optional[str] = None

class CustomerListResponse(BaseModel):
    items: List[ProtectedCustomerResponse]
    total: int
    page: int
    page_size: int


# Email & Marketing Schemas
class SendEmailRequest(BaseModel):
    recipient: str  # Protected EMAIL_xxxxx token
    campaign_id: str
    template_id: str

class SendEmailResponse(BaseModel):
    recipient: str
    status: str  # SENT
    message: str


# Bounce Webhook Schemas
class BounceWebhookRequest(BaseModel):
    email: str  # Raw provider plaintext
    event: str = "BOUNCE"
    reason: Optional[str] = "MAILBOX_NOT_FOUND"

class BounceWebhookResponse(BaseModel):
    recipient: str  # Protected token
    event: str
    reason: Optional[str] = None
    status: str


# Controlled Reveal Schemas
class RevealRequest(BaseModel):
    subject_id: str
    field: str
    purpose: str
    reference: str

class RevealResponse(BaseModel):
    subject_id: str
    field: str
    plaintext_value: str
    warning: str = "This operation has been audited."


# Audit Schemas
class AuditEventItem(BaseModel):
    id: str
    actor: str
    protected_subject: str
    action: str
    field: Optional[str] = None
    purpose: Optional[str] = None
    reference: Optional[str] = None
    result: str
    timestamp: str
    error_code: Optional[str] = None

class AuditListResponse(BaseModel):
    items: List[AuditEventItem]
    total: int
    page: int
    page_size: int


# Dashboard Stats
class DashboardStatsResponse(BaseModel):
    total_source_records: int
    protected_records: int
    latest_batch: Optional[BatchRunResponse] = None
    processed_rows: int
    successful_rows: int
    failed_rows: int
    discovered_pii_fields: int
    audit_events: int
    email_operations: int
    bounce_events: int
    denied_reveals: int
    allowed_reveals: int


# Health Check
class HealthResponse(BaseModel):
    status: str
    dependencies: Dict[str, Any]
