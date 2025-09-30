"""
Strength Scores SQLAlchemy model.
Calculated assessment results with statistical data.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, String, Integer, Float, Text, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class StrengthScore(Base):
    """
    Strength score model for storing calculated assessment results.
    
    Includes statistical data, rankings, and confidence intervals.
    """

    __tablename__ = "strength_scores"

    # Primary key
    score_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    session_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("assessment_sessions.session_id", ondelete="CASCADE"),
        nullable=False
    )

    strength_name: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("gallup_strengths.strength_name"),
        nullable=False
    )

    # Score data
    theme: Mapped[str] = mapped_column(String(50), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    percentile: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rank_position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-34 ranking

    # Statistical data
    confidence_interval_lower: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence_interval_upper: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Metadata and timestamps
    calculation_timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=func.now()
    )

    calculation_metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON

    ttl_expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.utcnow() + timedelta(hours=24)
    )

    # Relationships
    session: Mapped["AssessmentSession"] = relationship(
        "AssessmentSession",
        back_populates="strength_scores"
    )

    strength: Mapped["GallupStrength"] = relationship(
        "GallupStrength",
        back_populates="scores"
    )

    @property
    def is_expired(self) -> bool:
        """Check if score has expired based on TTL."""
        return datetime.utcnow() > self.ttl_expires_at

    @property
    def is_top_strength(self) -> bool:
        """Check if this is a top 5 strength."""
        return self.rank_position is not None and self.rank_position <= 5

    @property
    def strength_category(self) -> str:
        """Get strength category based on rank."""
        if not self.rank_position:
            return "unranked"
        elif self.rank_position <= 5:
            return "signature"
        elif self.rank_position <= 15:
            return "supporting"
        else:
            return "lesser"

    def to_dict(self) -> Dict[str, Any]:
        """Convert strength score to dictionary representation."""
        return {
            "score_id": self.score_id,
            "session_id": self.session_id,
            "strength_name": self.strength_name,
            "theme": self.theme,
            "score": self.score,
            "percentile": self.percentile,
            "rank_position": self.rank_position,
            "confidence_interval_lower": self.confidence_interval_lower,
            "confidence_interval_upper": self.confidence_interval_upper,
            "calculation_timestamp": self.calculation_timestamp.isoformat(),
            "ttl_expires_at": self.ttl_expires_at.isoformat(),
            "is_expired": self.is_expired,
            "is_top_strength": self.is_top_strength,
            "strength_category": self.strength_category
        }

    def __repr__(self) -> str:
        return (
            f"<StrengthScore("
            f"score_id={self.score_id}, "
            f"strength_name='{self.strength_name}', "
            f"score={self.score}, "
            f"rank_position={self.rank_position}"
            f")>"
        )