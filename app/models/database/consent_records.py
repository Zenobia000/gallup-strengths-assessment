"""
Consent Records SQLAlchemy model.
GDPR compliance and consent tracking for psychological assessments.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy import Boolean, DateTime, String, Text, func, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ConsentRecord(Base):
    """
    Consent record model for GDPR compliance and consent management.

    Tracks consent given, legal basis, and withdrawal capabilities
    for psychological assessment participation.
    """

    __tablename__ = "consent_records"

    # Primary key
    consent_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to session
    session_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("assessment_sessions.session_id", ondelete="CASCADE"),
        nullable=False
    )

    # Consent details
    consent_types: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array
    consent_given: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Timestamps
    consent_timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=func.now()
    )

    withdrawal_timestamp: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )

    # Privacy-compliant client information (hashed)
    ip_address_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    user_agent_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # TTL for data retention
    ttl_expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.utcnow() + timedelta(hours=24)
    )

    # GDPR compliance fields
    legal_basis: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    consent_version: Mapped[str] = mapped_column(String(20), nullable=False, default="1.0")

    # Relationship
    session: Mapped["AssessmentSession"] = relationship(
        "AssessmentSession",
        back_populates="consent_records"
    )

    @property
    def consent_types_list(self) -> List[str]:
        """Parse consent types JSON string into list."""
        if not self.consent_types:
            return []
        try:
            return json.loads(self.consent_types)
        except (json.JSONDecodeError, TypeError):
            return []

    @consent_types_list.setter
    def consent_types_list(self, value: List[str]) -> None:
        """Set consent types from list."""
        self.consent_types = json.dumps(value) if value else "[]"

    @property
    def is_valid(self) -> bool:
        """Check if consent is currently valid."""
        return (
            self.consent_given and
            self.withdrawal_timestamp is None and
            not self.is_expired
        )

    @property
    def is_expired(self) -> bool:
        """Check if consent has expired based on TTL."""
        return datetime.utcnow() > self.ttl_expires_at

    @property
    def is_withdrawn(self) -> bool:
        """Check if consent has been withdrawn."""
        return self.withdrawal_timestamp is not None

    @property
    def time_remaining_hours(self) -> int:
        """Get remaining time in hours before TTL expiration."""
        if self.is_expired:
            return 0

        remaining = self.ttl_expires_at - datetime.utcnow()
        return max(0, int(remaining.total_seconds() / 3600))

    def withdraw_consent(self) -> None:
        """Withdraw consent by setting withdrawal timestamp."""
        self.withdrawal_timestamp = datetime.utcnow()
        self.consent_given = False

    def has_consent_type(self, consent_type: str) -> bool:
        """Check if specific consent type is included."""
        return consent_type in self.consent_types_list

    def add_consent_type(self, consent_type: str) -> None:
        """Add a new consent type to the record."""
        current_types = self.consent_types_list
        if consent_type not in current_types:
            current_types.append(consent_type)
            self.consent_types_list = current_types

    def remove_consent_type(self, consent_type: str) -> None:
        """Remove a consent type from the record."""
        current_types = self.consent_types_list
        if consent_type in current_types:
            current_types.remove(consent_type)
            self.consent_types_list = current_types

    def extend_ttl(self, hours: int = 24) -> None:
        """Extend TTL expiration time."""
        self.ttl_expires_at = datetime.utcnow() + timedelta(hours=hours)

    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert consent record to dictionary representation."""
        data = {
            "consent_id": self.consent_id,
            "session_id": self.session_id,
            "consent_types": self.consent_types_list,
            "consent_given": self.consent_given,
            "consent_timestamp": self.consent_timestamp.isoformat(),
            "withdrawal_timestamp": (
                self.withdrawal_timestamp.isoformat()
                if self.withdrawal_timestamp else None
            ),
            "ttl_expires_at": self.ttl_expires_at.isoformat(),
            "legal_basis": self.legal_basis,
            "consent_version": self.consent_version,
            "is_valid": self.is_valid,
            "is_expired": self.is_expired,
            "is_withdrawn": self.is_withdrawn,
            "time_remaining_hours": self.time_remaining_hours
        }

        if include_sensitive:
            data.update({
                "ip_address_hash": self.ip_address_hash,
                "user_agent_hash": self.user_agent_hash,
            })

        return data

    @classmethod
    def create_with_standard_consents(
        cls,
        session_id: str,
        ip_address_hash: Optional[str] = None,
        user_agent_hash: Optional[str] = None,
        legal_basis: str = "consent"
    ) -> "ConsentRecord":
        """Create consent record with standard consent types."""
        from app.core.config import PSYCHOLOGICAL_ASSESSMENT_CONFIG

        standard_consent_types = PSYCHOLOGICAL_ASSESSMENT_CONFIG["required_consent_types"]

        return cls(
            session_id=session_id,
            consent_types=json.dumps(standard_consent_types),
            consent_given=True,
            ip_address_hash=ip_address_hash,
            user_agent_hash=user_agent_hash,
            legal_basis=legal_basis
        )

    def __repr__(self) -> str:
        return (
            f"<ConsentRecord("
            f"consent_id={self.consent_id}, "
            f"session_id='{self.session_id}', "
            f"consent_given={self.consent_given}, "
            f"is_valid={self.is_valid}"
            f")>"
        )