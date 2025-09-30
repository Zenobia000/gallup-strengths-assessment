"""
Gallup Strengths SQLAlchemy model.
34 strength themes with detailed metadata.
"""

import json
from datetime import datetime
from typing import Any, Dict, List
from sqlalchemy import DateTime, String, Text, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class GallupStrength(Base):
    """
    Gallup strength reference model with comprehensive metadata.
    """

    __tablename__ = "gallup_strengths"

    strength_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    strength_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    theme: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # JSON fields for complex data
    key_characteristics: Mapped[str] = mapped_column(Text, nullable=True)  # JSON array
    development_suggestions: Mapped[str] = mapped_column(Text, nullable=True)  # JSON array
    related_strengths: Mapped[str] = mapped_column(Text, nullable=True)  # JSON array
    complementary_strengths: Mapped[str] = mapped_column(Text, nullable=True)  # JSON array
    potential_blind_spots: Mapped[str] = mapped_column(Text, nullable=True)  # JSON array
    
    leadership_application: Mapped[str] = mapped_column(Text, nullable=True)
    team_contribution: Mapped[str] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())

    # Relationships
    scores: Mapped[List["StrengthScore"]] = relationship(
        "StrengthScore",
        back_populates="strength"
    )

    def _parse_json_field(self, field_value: str) -> List[str]:
        """Parse JSON string field into list."""
        if not field_value:
            return []
        try:
            return json.loads(field_value)
        except (json.JSONDecodeError, TypeError):
            return []

    @property
    def key_characteristics_list(self) -> List[str]:
        return self._parse_json_field(self.key_characteristics)

    @property
    def development_suggestions_list(self) -> List[str]:
        return self._parse_json_field(self.development_suggestions)

    def to_dict(self) -> Dict[str, Any]:
        """Convert strength to dictionary representation."""
        return {
            "strength_id": self.strength_id,
            "strength_name": self.strength_name,
            "theme": self.theme,
            "description": self.description,
            "key_characteristics": self.key_characteristics_list,
            "development_suggestions": self.development_suggestions_list,
            "leadership_application": self.leadership_application,
            "team_contribution": self.team_contribution
        }

    def __repr__(self) -> str:
        return f"<GallupStrength(strength_name='{self.strength_name}', theme='{self.theme}')>"