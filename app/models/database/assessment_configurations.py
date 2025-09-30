"""
Assessment Configurations SQLAlchemy model.
Different assessment types and settings.
"""

from datetime import datetime
from typing import Any, Dict
from sqlalchemy import DateTime, String, Text, Integer, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AssessmentConfiguration(Base):
    """Assessment configuration model for different assessment types."""

    __tablename__ = "assessment_configurations"

    config_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    config_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    assessment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    question_count: Mapped[int] = mapped_column(Integer, nullable=False)
    time_limit_minutes: Mapped[int] = mapped_column(Integer, nullable=True)
    randomize_questions: Mapped[bool] = mapped_column(Boolean, default=True)
    require_all_questions: Mapped[bool] = mapped_column(Boolean, default=True)
    scoring_algorithm: Mapped[str] = mapped_column(Text, nullable=False)  # JSON
    result_categories: Mapped[str] = mapped_column(Text, nullable=True)  # JSON
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "config_id": self.config_id,
            "config_name": self.config_name,
            "assessment_type": self.assessment_type,
            "question_count": self.question_count,
            "time_limit_minutes": self.time_limit_minutes,
            "active": self.active
        }

    def __repr__(self) -> str:
        return f"<AssessmentConfiguration(config_name='{self.config_name}', active={self.active})>"