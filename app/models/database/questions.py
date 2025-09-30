"""
Questions SQLAlchemy model.
Mini-IPIP and assessment question bank.
"""

from datetime import datetime
from typing import Any, Dict, List
from sqlalchemy import DateTime, String, Text, Integer, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Question(Base):
    """Assessment question model with scoring and metadata."""

    __tablename__ = "questions"

    question_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(50), nullable=False)
    theme_mapping: Mapped[str] = mapped_column(Text, nullable=True)  # JSON
    scoring_key: Mapped[str] = mapped_column(Text, nullable=False)  # JSON
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    difficulty_level: Mapped[int] = mapped_column(Integer, nullable=True)
    estimated_time_seconds: Mapped[int] = mapped_column(Integer, default=30)
    question_category: Mapped[str] = mapped_column(String(100), nullable=True)
    reverse_scored: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())

    # Relationships
    responses: Mapped[List["AssessmentResponse"]] = relationship(
        "AssessmentResponse",
        back_populates="question"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_id": self.question_id,
            "question_text": self.question_text,
            "question_type": self.question_type,
            "difficulty_level": self.difficulty_level,
            "estimated_time_seconds": self.estimated_time_seconds,
            "reverse_scored": self.reverse_scored,
            "active": self.active
        }

    def __repr__(self) -> str:
        return f"<Question(question_id={self.question_id}, active={self.active})>"