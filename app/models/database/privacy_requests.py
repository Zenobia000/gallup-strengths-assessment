"""
Privacy Requests SQLAlchemy model.
GDPR subject access requests.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, String, Text, Integer, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PrivacyRequest(Base):
    """Privacy request model for GDPR compliance."""

    __tablename__ = "privacy_requests"

    request_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    session_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        ForeignKey("assessment_sessions.session_id"),
        nullable=True
    )
    
    request_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    request_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    processed_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    requester_verification: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    processing_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationship
    session: Mapped[Optional["AssessmentSession"]] = relationship(
        "AssessmentSession",
        back_populates="privacy_requests"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "session_id": self.session_id,
            "request_type": self.request_type,
            "status": self.status,
            "request_timestamp": self.request_timestamp.isoformat(),
            "processed_timestamp": (
                self.processed_timestamp.isoformat() 
                if self.processed_timestamp else None
            ),
        }

    def __repr__(self) -> str:
        return f"<PrivacyRequest(request_id={self.request_id}, request_type='{self.request_type}')>"