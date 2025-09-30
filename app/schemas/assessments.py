"""
Assessment-related Pydantic schemas for API validation.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class AssessmentStart(BaseModel):
    """Schema for starting an assessment."""
    assessment_type: str = Field("full_assessment", description="Type of assessment")
    randomize_questions: bool = True


class ResponseSubmit(BaseModel):
    """Schema for submitting a question response."""
    question_id: int
    selected_value: int = Field(..., ge=1, le=7, description="Response value (1-7 scale)")
    response_time_ms: Optional[int] = Field(None, ge=0, description="Response time in milliseconds")
    confidence_level: Optional[int] = Field(None, ge=1, le=5, description="Confidence level (1-5)")


class QuestionResponse(BaseModel):
    """Schema for question with response options."""
    question_id: int
    question_text: str
    question_type: str
    estimated_time_seconds: int
    sequence_number: Optional[int] = None
    
    class Config:
        from_attributes = True


class AssessmentProgress(BaseModel):
    """Schema for assessment progress tracking."""
    session_id: str
    total_questions: int
    completed_questions: int
    completion_percentage: float
    current_question_number: Optional[int] = None
    time_remaining_minutes: int


class AssessmentResponse(BaseModel):
    """Schema for assessment operation responses."""
    session_id: str
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None