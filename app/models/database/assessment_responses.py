"""
Assessment Responses SQLAlchemy model.
Individual question responses with TTL and validation.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, String, Integer, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AssessmentResponse(Base):
    """
    Assessment response model for storing individual question answers.
    
    Tracks response values, timing, and confidence with TTL compliance.
    """

    __tablename__ = "assessment_responses"

    # Primary key
    response_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    session_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("assessment_sessions.session_id", ondelete="CASCADE"),
        nullable=False
    )

    question_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("questions.question_id"),
        nullable=False
    )

    # Response data
    selected_value: Mapped[int] = mapped_column(Integer, nullable=False)
    response_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    confidence_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5 scale
    sequence_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Timestamps and TTL
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=func.now()
    )

    ttl_expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.utcnow() + timedelta(hours=24)
    )

    # Relationships
    session: Mapped["AssessmentSession"] = relationship(
        "AssessmentSession",
        back_populates="assessment_responses"
    )

    question: Mapped["Question"] = relationship(
        "Question",
        back_populates="responses"
    )

    @property
    def is_expired(self) -> bool:
        """Check if response has expired based on TTL."""
        return datetime.utcnow() > self.ttl_expires_at

    @property
    def is_fast_response(self) -> bool:
        """Check if response was answered suspiciously fast."""
        if not self.response_time_ms:
            return False
        return self.response_time_ms < 500  # Less than 500ms is suspicious

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary representation."""
        return {
            "response_id": self.response_id,
            "session_id": self.session_id,
            "question_id": self.question_id,
            "selected_value": self.selected_value,
            "response_time_ms": self.response_time_ms,
            "confidence_level": self.confidence_level,
            "sequence_number": self.sequence_number,
            "timestamp": self.timestamp.isoformat(),
            "ttl_expires_at": self.ttl_expires_at.isoformat(),
            "is_expired": self.is_expired,
            "is_fast_response": self.is_fast_response
        }

    def __repr__(self) -> str:
        return (
            f"<AssessmentResponse("
            f"response_id={self.response_id}, "
            f"session_id='{self.session_id}', "
            f"question_id={self.question_id}, "
            f"selected_value={self.selected_value}"
            f")>"
        )