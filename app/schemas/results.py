"""
Results-related Pydantic schemas for API validation.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class StrengthResult(BaseModel):
    """Schema for individual strength result."""
    strength_name: str
    theme: str
    score: float
    percentile: Optional[float] = None
    rank_position: Optional[int] = None
    is_top_strength: bool
    strength_category: str
    
    class Config:
        from_attributes = True


class AssessmentResults(BaseModel):
    """Schema for complete assessment results."""
    session_id: str
    participant_type: str
    completion_date: datetime
    top_strengths: List[StrengthResult]
    all_strengths: List[StrengthResult]
    themes_summary: Dict[str, Any]
    assessment_metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ResultsExport(BaseModel):
    """Schema for results export request."""
    export_format: str = Field("json", description="Export format (json, csv, pdf)")
    include_details: bool = Field(True, description="Include detailed breakdown")
    include_development_suggestions: bool = Field(True, description="Include development suggestions")