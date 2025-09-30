"""
Session-related Pydantic schemas for API validation.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


class ParticipantType(str, Enum):
    INDIVIDUAL = "individual"
    TEAM_MEMBER = "team_member"
    LEADER = "leader"
    STUDENT = "student"


class SessionStatus(str, Enum):
    CREATED = "created"
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"
    ABANDONED = "abandoned"


class SessionCreate(BaseModel):
    """Schema for creating a new assessment session."""
    participant_type: ParticipantType = ParticipantType.INDIVIDUAL
    language: str = Field("en", pattern=r"^[a-z]{2}$", description="Language code (ISO 639-1)")
    timezone: Optional[str] = Field(None, description="Client timezone")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional session metadata")


class SessionUpdate(BaseModel):
    """Schema for updating an existing session."""
    status: Optional[SessionStatus] = None
    metadata: Optional[Dict[str, Any]] = None


class SessionResponse(BaseModel):
    """Schema for session response data."""
    session_id: str
    status: SessionStatus
    participant_type: ParticipantType
    language: str
    created_at: datetime
    expires_at: datetime
    last_activity_at: datetime
    completed_at: Optional[datetime] = None
    timezone: Optional[str] = None
    is_expired: bool
    is_active: bool
    time_remaining_minutes: int
    response_count: int
    completion_percentage: float
    has_valid_consent: bool
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SessionStatusResponse(BaseModel):
    """Schema for session status check response."""
    session_id: str
    status: SessionStatus
    is_expired: bool
    is_active: bool
    time_remaining_minutes: int
    can_continue_assessment: bool
    has_valid_consent: bool
    completion_percentage: float
    
    class Config:
        from_attributes = True