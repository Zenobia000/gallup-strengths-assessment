"""
Assessment Sessions SQLAlchemy model.
Core session management with TTL and compliance features.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AssessmentSession(Base):
    """
    Assessment session model with comprehensive tracking and TTL support.

    Handles session lifecycle, participant information, and compliance
    requirements for psychological assessments.
    """

    __tablename__ = "assessment_sessions"

    # Primary identification
    session_id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Session status and type
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="created"
    )  # created, active, completed, expired, abandoned

    participant_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="individual"
    )  # individual, team_member, leader, student

    # Language and localization
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")

    # Timestamps and TTL
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=func.now()
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.utcnow() + timedelta(hours=24)
    )

    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=func.now()
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Flexible metadata storage
    session_metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Privacy-compliant client information (hashed)
    ip_address_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    user_agent_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Timezone for proper time handling
    timezone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    consent_records: Mapped[List["ConsentRecord"]] = relationship(
        "ConsentRecord",
        back_populates="session",
        cascade="all, delete-orphan"
    )

    assessment_responses: Mapped[List["AssessmentResponse"]] = relationship(
        "AssessmentResponse",
        back_populates="session",
        cascade="all, delete-orphan"
    )

    strength_scores: Mapped[List["StrengthScore"]] = relationship(
        "StrengthScore",
        back_populates="session",
        cascade="all, delete-orphan"
    )

    audit_trails: Mapped[List["AuditTrail"]] = relationship(
        "AuditTrail",
        back_populates="session",
        cascade="all, delete-orphan"
    )

    privacy_requests: Mapped[List["PrivacyRequest"]] = relationship(
        "PrivacyRequest",
        back_populates="session",
        cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        """Initialize session with default values."""
        super().__init__(**kwargs)
        if not self.session_id:
            from app.core.security import generate_session_id
            self.session_id = generate_session_id()

    @property
    def metadata_dict(self) -> Dict[str, Any]:
        """Parse metadata JSON string into dictionary."""
        if not self.session_metadata:
            return {}
        try:
            return json.loads(self.session_metadata)
        except (json.JSONDecodeError, TypeError):
            return {}

    @metadata_dict.setter
    def metadata_dict(self, value: Dict[str, Any]) -> None:
        """Set metadata from dictionary."""
        self.session_metadata = json.dumps(value) if value else None

    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.utcnow() > self.expires_at

    @property
    def is_active(self) -> bool:
        """Check if session is currently active."""
        return (
            self.status == "active" and
            not self.is_expired
        )

    @property
    def time_remaining_minutes(self) -> int:
        """Get remaining time in minutes before expiration."""
        if self.is_expired:
            return 0

        remaining = self.expires_at - datetime.utcnow()
        return max(0, int(remaining.total_seconds() / 60))

    @property
    def duration_minutes(self) -> Optional[int]:
        """Get session duration in minutes if completed."""
        if not self.completed_at:
            return None

        duration = self.completed_at - self.created_at
        return int(duration.total_seconds() / 60)

    @property
    def response_count(self) -> int:
        """Get number of responses in this session."""
        return len(self.assessment_responses) if self.assessment_responses else 0

    @property
    def completion_percentage(self) -> float:
        """Get assessment completion percentage (assuming 50 total questions)."""
        total_questions = 50  # This could be configurable
        current_responses = self.response_count
        return min(100.0, (current_responses / total_questions) * 100)

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity_at = datetime.utcnow()

    def mark_completed(self) -> None:
        """Mark session as completed."""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
        self.update_activity()

    def mark_abandoned(self) -> None:
        """Mark session as abandoned."""
        self.status = "abandoned"
        self.update_activity()

    def extend_expiration(self, hours: int = 24) -> None:
        """Extend session expiration time."""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)
        self.update_activity()

    def can_continue_assessment(self) -> bool:
        """Check if assessment can be continued."""
        return (
            self.status in ["created", "active"] and
            not self.is_expired
        )

    def has_valid_consent(self) -> bool:
        """Check if session has valid, non-withdrawn consent."""
        if not self.consent_records:
            return False

        # Check for any valid consent record
        for consent in self.consent_records:
            if consent.consent_given and consent.withdrawal_timestamp is None:
                return True

        return False

    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert session to dictionary representation."""
        data = {
            "session_id": self.session_id,
            "status": self.status,
            "participant_type": self.participant_type,
            "language": self.language,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "last_activity_at": self.last_activity_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "timezone": self.timezone,
            "is_expired": self.is_expired,
            "is_active": self.is_active,
            "time_remaining_minutes": self.time_remaining_minutes,
            "response_count": self.response_count,
            "completion_percentage": self.completion_percentage,
            "has_valid_consent": self.has_valid_consent(),
            "metadata": self.metadata_dict
        }

        if include_sensitive:
            data.update({
                "ip_address_hash": self.ip_address_hash,
                "user_agent_hash": self.user_agent_hash,
            })

        return data

    def __repr__(self) -> str:
        return (
            f"<AssessmentSession("
            f"session_id='{self.session_id}', "
            f"status='{self.status}', "
            f"participant_type='{self.participant_type}', "
            f"created_at='{self.created_at}'"
            f")>"
        )