"""
Question Sets SQLAlchemy model.
Links assessments to questions.
"""

from typing import Any, Dict
from sqlalchemy import Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class QuestionSet(Base):
    """Question set model linking configurations to questions."""

    __tablename__ = "question_sets"

    set_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    config_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("assessment_configurations.config_id", ondelete="CASCADE"),
        nullable=False
    )
    
    question_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("questions.question_id"),
        nullable=False
    )
    
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    required: Mapped[bool] = mapped_column(Boolean, default=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "set_id": self.set_id,
            "config_id": self.config_id,
            "question_id": self.question_id,
            "sequence_order": self.sequence_order,
            "weight": self.weight,
            "required": self.required
        }

    def __repr__(self) -> str:
        return f"<QuestionSet(set_id={self.set_id}, config_id={self.config_id}, question_id={self.question_id})>"