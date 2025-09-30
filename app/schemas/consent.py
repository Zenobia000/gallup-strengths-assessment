"""
Consent-related Pydantic schemas for API validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


class ConsentType(str, Enum):
    """Standard consent types for psychological assessment."""
    DATA_PROCESSING = "data_processing"
    PSYCHOLOGICAL_ASSESSMENT = "psychological_assessment"
    DATA_RETENTION = "data_retention"
    RESEARCH_PARTICIPATION = "research_participation"
    MARKETING_COMMUNICATION = "marketing_communication"


class LegalBasis(str, Enum):
    """GDPR legal basis options."""
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"


class ConsentCreate(BaseModel):
    """Schema for creating consent record."""
    session_id: str
    consent_types: List[ConsentType]
    consent_given: bool = True
    legal_basis: LegalBasis = LegalBasis.CONSENT
    consent_version: str = "1.0"

    @validator('consent_types')
    def validate_consent_types(cls, v):
        if not v:
            raise ValueError("At least one consent type must be provided")
        return v


class ConsentUpdate(BaseModel):
    """Schema for updating consent record."""
    consent_types: Optional[List[ConsentType]] = None
    consent_given: Optional[bool] = None


class ConsentResponse(BaseModel):
    """Schema for consent response data."""
    consent_id: int
    session_id: str
    consent_types: List[str]
    consent_given: bool
    consent_timestamp: datetime
    withdrawal_timestamp: Optional[datetime] = None
    ttl_expires_at: datetime
    legal_basis: Optional[str]
    consent_version: str
    is_valid: bool
    is_expired: bool
    is_withdrawn: bool
    time_remaining_hours: int

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConsentStatusResponse(BaseModel):
    """Schema for consent status check response."""
    session_id: str
    has_valid_consent: bool
    consent_count: int
    active_consents: List[str]
    withdrawn_consents: List[str]
    expired_consents: List[str]

    class Config:
        from_attributes = True


class PrivacyRequestType(str, Enum):
    """GDPR privacy request types."""
    ACCESS = "access"  # Article 15 - Right of access
    RECTIFICATION = "rectification"  # Article 16 - Right to rectification
    ERASURE = "erasure"  # Article 17 - Right to erasure
    RESTRICT_PROCESSING = "restrict_processing"  # Article 18
    DATA_PORTABILITY = "data_portability"  # Article 20
    OBJECT = "object"  # Article 21 - Right to object


class PrivacyRequestStatus(str, Enum):
    """Privacy request processing status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"


class PrivacyRequestCreate(BaseModel):
    """Schema for creating privacy request."""
    session_id: Optional[str] = None
    request_type: PrivacyRequestType
    requester_verification: Optional[str] = Field(
        None,
        description="Verification data for identity confirmation"
    )
    processing_notes: Optional[str] = Field(
        None,
        description="Additional notes for request processing"
    )


class PrivacyRequestResponse(BaseModel):
    """Schema for privacy request response."""
    request_id: int
    session_id: Optional[str]
    request_type: PrivacyRequestType
    status: PrivacyRequestStatus
    request_timestamp: datetime
    processed_timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DataExportResponse(BaseModel):
    """Schema for data export response (GDPR Article 20)."""
    session_id: str
    export_timestamp: datetime
    data_types: List[str]
    personal_data: Dict[str, Any]
    assessment_data: Optional[Dict[str, Any]] = None
    consent_history: List[Dict[str, Any]]
    privacy_requests: List[Dict[str, Any]]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DataErasureResponse(BaseModel):
    """Schema for data erasure response (GDPR Article 17)."""
    session_id: str
    erasure_timestamp: datetime
    erased_data_types: List[str]
    anonymization_applied: bool
    erasure_verification_id: str

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }