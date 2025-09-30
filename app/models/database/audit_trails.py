"""
Audit Trails SQLAlchemy model.
Complete operation tracking for compliance.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, String, Text, Integer, Boolean, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AuditTrail(Base):
    """Audit trail model for compliance and security monitoring."""

    __tablename__ = "audit_trails"

    audit_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    session_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        ForeignKey("assessment_sessions.session_id", ondelete="CASCADE"),
        nullable=True
    )
    
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    old_values: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    new_values: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    ip_address_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    user_agent_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationship
    session: Mapped[Optional["AssessmentSession"]] = relationship(
        "AssessmentSession",
        back_populates="audit_trails"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "audit_id": self.audit_id,
            "session_id": self.session_id,
            "action_type": self.action_type,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "error_message": self.error_message
        }

    def __repr__(self) -> str:
        return f"<AuditTrail(audit_id={self.audit_id}, action_type='{self.action_type}')>"