"""
Pydantic Data Models and Schemas - Gallup Strengths Assessment

Implements data validation following psychometric standards:
- Strong type validation for Likert scale responses
- Comprehensive error handling with specific psychometric error codes
- Provenance tracking for explainability
- Privacy-compliant data models

Follows Linus Torvalds principles of simplicity and clear naming.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from enum import Enum

from pydantic import BaseModel, Field, validator, root_validator, model_validator


# Enums for controlled vocabularies
class SessionStatus(str, Enum):
    """Assessment session status values."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"


class ScaleType(str, Enum):
    """Psychometric scale types."""
    LIKERT_7 = "likert_7"
    LIKERT_5 = "likert_5"


class JobCategory(str, Enum):
    """Job category classifications."""
    PRODUCT_STRATEGY = "product_strategy"
    TECHNICAL_LEADERSHIP = "technical_leadership"
    CREATIVE_INNOVATION = "creative_innovation"
    ANALYTICAL_RESEARCH = "analytical_research"
    SALES_INFLUENCE = "sales_influence"
    TEAM_COLLABORATION = "team_collaboration"


# Base Response Models
class APIResponse(BaseModel):
    """Standard API response wrapper with metadata."""
    success: bool = Field(..., description="Request success status")
    data: Optional[Any] = Field(None, description="Response data payload")
    error: Optional[Dict[str, Any]] = Field(None, description="Error information")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="System health status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="API version")
    database_status: str = Field(..., description="Database connectivity status")
    services: Optional[Dict[str, str]] = Field(None, description="Service status map")
    error: Optional[str] = Field(None, description="Error details if unhealthy")


# Consent Management Models
class ConsentRequest(BaseModel):
    """Privacy consent request model."""
    agreed: bool = Field(..., description="User agreement to privacy terms")
    user_agent: str = Field(..., max_length=500, description="Browser user agent")
    ip_address: Optional[str] = Field(None, description="User IP address")
    consent_version: str = Field(default="v1.0", description="Privacy terms version")

    @validator('agreed')
    def must_agree_to_consent(cls, v):
        """Validate that user has agreed to consent."""
        if not v:
            raise ValueError("Consent must be explicitly agreed to")
        return v


class ConsentResponse(BaseModel):
    """Privacy consent response model."""
    consent_id: str = Field(..., description="Unique consent identifier")
    agreed_at: datetime = Field(..., description="Consent agreement timestamp")
    expires_at: datetime = Field(..., description="Consent expiration timestamp")
    consent_version: str = Field(..., description="Privacy terms version")


# Assessment Session Models
class SessionStartRequest(BaseModel):
    """Assessment session start request."""
    consent_id: str = Field(..., description="Valid consent identifier")
    instrument: str = Field(default="mini_ipip_v1.0", description="Assessment instrument version")

    @validator('instrument')
    def validate_instrument(cls, v):
        """Validate supported assessment instruments."""
        supported = ["mini_ipip_v1.0"]
        if v not in supported:
            raise ValueError(f"Unsupported instrument: {v}. Supported: {supported}")
        return v


class SessionStartResponse(BaseModel):
    """Assessment session start response."""
    session_id: str = Field(..., description="Unique session identifier")
    instrument_version: str = Field(..., description="Assessment instrument version")
    total_items: int = Field(..., description="Total number of assessment items")
    estimated_duration: int = Field(..., description="Estimated completion time in seconds")
    created_at: datetime = Field(..., description="Session creation timestamp")
    expires_at: datetime = Field(..., description="Session expiration timestamp")


# Assessment Item Models
class QuestionType(str, Enum):
    """Question type classifications."""
    TRADITIONAL = "traditional"
    SITUATIONAL = "situational"


class ResponseOption(BaseModel):
    """Response option for situational questions."""
    value: int = Field(..., description="Response value")
    text: str = Field(..., description="Response option text")
    dimensions: Optional[Dict[str, float]] = Field(None, description="Dimension weights for this option")


class AssessmentItem(BaseModel):
    """Individual assessment item model with support for situational questions."""
    item_id: str = Field(..., description="Unique item identifier")
    text: str = Field(..., description="Item text content")
    scale_type: ScaleType = Field(..., description="Response scale type")
    reverse_scored: bool = Field(..., description="Whether item is reverse scored")
    dimension: str = Field(..., description="Personality dimension measured")

    # New fields for situational questions
    question_type: QuestionType = Field(default=QuestionType.TRADITIONAL, description="Type of question")
    scenario_context: Optional[str] = Field(None, description="Scenario context for situational questions")
    response_options: Optional[List[ResponseOption]] = Field(None, description="Custom response options for situational questions")
    dimension_weights: Optional[Dict[str, float]] = Field(None, description="Multi-dimensional weights for scoring")


class ScaleLabels(BaseModel):
    """Scale response labels model."""
    labels: Dict[str, str] = Field(
        default={
            "1": "非常不同意",
            "2": "不同意",
            "3": "稍微不同意",
            "4": "中立",
            "5": "稍微同意",
            "6": "同意",
            "7": "非常同意"
        },
        description="Scale point labels"
    )


class ItemsResponse(BaseModel):
    """Assessment items response model."""
    items: List[AssessmentItem] = Field(..., description="Assessment items")
    instructions: str = Field(..., description="Assessment instructions")
    scale_labels: ScaleLabels = Field(..., description="Response scale labels")
    total_items: int = Field(..., description="Total number of items")


# Response Submission Models
class QuestionResponse(BaseModel):
    """Mini-IPIP question response model for scoring engine."""
    question_id: int = Field(..., ge=1, le=23, description="Question ID (1-23)")
    score: int = Field(..., ge=1, le=5, description="Likert scale score (1-5)")

    @validator('score')
    def validate_score_range(cls, v):
        """Validate score is within Mini-IPIP range."""
        if not 1 <= v <= 5:
            raise ValueError("Score must be between 1 and 5 (inclusive)")
        return v


class ItemResponse(BaseModel):
    """Individual item response model."""
    item_id: str = Field(..., description="Assessment item identifier")
    response: int = Field(..., ge=1, le=7, description="Likert scale response (1-7)")

    @validator('response')
    def validate_likert_range(cls, v):
        """Validate Likert scale response range."""
        if not 1 <= v <= 7:
            raise ValueError("Response must be between 1 and 7 (inclusive)")
        return v


class AssessmentSubmission(BaseModel):
    """Complete assessment submission model."""
    responses: List[ItemResponse] = Field(..., description="Item responses")
    completion_time: int = Field(..., ge=1, description="Completion time in seconds")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    @validator('responses')
    def validate_response_completeness(cls, v):
        """Validate all 20 items are answered."""
        if len(v) != 20:
            raise ValueError("All 20 items must be answered")

        # Check for duplicate item responses
        item_ids = [r.item_id for r in v]
        if len(set(item_ids)) != len(item_ids):
            raise ValueError("Duplicate item responses detected")

        return v

    @validator('completion_time')
    def validate_completion_time(cls, v):
        """Validate reasonable completion time."""
        if v < 60:  # Less than 1 minute
            raise ValueError("Completion time suspiciously fast (< 60 seconds)")
        if v > 1800:  # More than 30 minutes
            raise ValueError("Completion time suspiciously slow (> 30 minutes)")
        return v


# Scoring and Results Models
class BigFiveScores(BaseModel):
    """Big Five personality scores (0-100)."""
    extraversion: int = Field(..., ge=0, le=100)
    agreeableness: int = Field(..., ge=0, le=100)
    conscientiousness: int = Field(..., ge=0, le=100)
    neuroticism: int = Field(..., ge=0, le=100)
    openness: int = Field(..., ge=0, le=100)


class HEXACOScores(BigFiveScores):
    """HEXACO personality scores extending Big Five."""
    honesty_humility: int = Field(..., ge=0, le=100)


class StrengthScores(BaseModel):
    """12-dimension strength scores (0-100)."""
    結構化執行: int = Field(..., ge=0, le=100)
    品質與完備: int = Field(..., ge=0, le=100)
    探索與創新: int = Field(..., ge=0, le=100)
    分析與洞察: int = Field(..., ge=0, le=100)
    影響與倡議: int = Field(..., ge=0, le=100)
    協作與共好: int = Field(..., ge=0, le=100)
    客戶導向: int = Field(..., ge=0, le=100)
    學習與成長: int = Field(..., ge=0, le=100)
    紀律與信任: int = Field(..., ge=0, le=100)
    壓力調節: int = Field(..., ge=0, le=100)
    衝突整合: int = Field(..., ge=0, le=100)
    責任與當責: int = Field(..., ge=0, le=100)


class ProvenanceInfo(BaseModel):
    """Provenance tracking for explainability."""
    algorithm_version: str = Field(..., description="Scoring algorithm version")
    weights_version: str = Field(..., description="Weight matrix version")
    calculated_at: datetime = Field(..., description="Calculation timestamp")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class AssessmentSubmissionResponse(BaseModel):
    """Assessment submission response with basic scores."""
    session_id: str = Field(..., description="Session identifier")
    status: SessionStatus = Field(..., description="Session status")
    submitted_at: datetime = Field(..., description="Submission timestamp")
    basic_scores: HEXACOScores = Field(..., description="Basic personality scores")
    next_step: str = Field(..., description="Next API endpoint to call")


# Results and Analysis Models
class StrengthInsight(BaseModel):
    """Individual strength insight model."""
    name: str = Field(..., description="Strength dimension name")
    score: int = Field(..., ge=0, le=100, description="Strength score")
    description: str = Field(..., description="Strength description")
    development_tips: List[str] = Field(..., description="Development recommendations")


class RiskArea(BaseModel):
    """Risk area identification model."""
    name: str = Field(..., description="Risk area name")
    score: int = Field(..., ge=0, le=100, description="Current score")
    concern: str = Field(..., description="Risk description")
    mitigation: List[str] = Field(..., description="Risk mitigation strategies")


class ResultsResponse(BaseModel):
    """Complete assessment results response."""
    session_id: str = Field(..., description="Session identifier")
    analysis_completed_at: datetime = Field(..., description="Analysis completion time")
    strength_scores: StrengthScores = Field(..., description="12-dimension strength scores")
    top_strengths: List[StrengthInsight] = Field(..., description="Top 3-5 strengths")
    risk_areas: List[RiskArea] = Field(..., description="Areas needing attention")
    provenance: ProvenanceInfo = Field(..., description="Calculation provenance")


# Recommendation Models
class JobRecommendation(BaseModel):
    """Job role recommendation model."""
    role_id: str = Field(..., description="Job role identifier")
    title: str = Field(..., description="Job role title")
    match_score: float = Field(..., ge=0.0, le=1.0, description="Compatibility score")
    reasoning: Dict[str, Any] = Field(..., description="Recommendation reasoning")
    requirements: Dict[str, str] = Field(..., description="Role requirements")


class ImprovementAction(BaseModel):
    """Individual improvement action model."""
    action: str = Field(..., description="Specific action to take")
    timeframe: str = Field(..., description="Expected timeframe")
    expected_impact: str = Field(..., description="Expected impact description")


class ImprovementRecommendation(BaseModel):
    """Area improvement recommendation model."""
    area: str = Field(..., description="Improvement area name")
    current_score: int = Field(..., ge=0, le=100, description="Current score")
    target_score: int = Field(..., ge=0, le=100, description="Target score")
    priority: str = Field(..., description="Priority level")
    actions: List[ImprovementAction] = Field(..., description="Specific actions")


class RecommendationRequest(BaseModel):
    """Recommendation generation request."""
    recommendation_types: List[str] = Field(..., description="Types of recommendations needed")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class RecommendationResponse(BaseModel):
    """Recommendation generation response."""
    job_recommendations: List[JobRecommendation] = Field(..., description="Job recommendations")
    improvement_recommendations: List[ImprovementRecommendation] = Field(..., description="Improvement recommendations")
    generated_at: datetime = Field(..., description="Generation timestamp")
    valid_until: datetime = Field(..., description="Recommendation validity period")


# Error Models
class PsychometricError(BaseModel):
    """Psychometric-specific error model."""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    trace_id: str = Field(..., description="Error trace identifier")


# Database Models (for internal use)
class SessionData(BaseModel):
    """Internal session data model."""
    session_id: str
    consent_id: str
    status: SessionStatus
    instrument_version: str
    created_at: datetime
    expires_at: datetime
    completed_at: Optional[datetime] = None
    raw_responses: Optional[List[int]] = None
    metadata: Optional[Dict[str, Any]] = None


# New Scoring API Models
class ResponseItem(BaseModel):
    """Individual response item for scoring."""
    question_id: int = Field(..., ge=1, le=23, description="Question identifier (1-23)")
    response_value: int = Field(..., ge=1, le=7, description="Likert scale response (1-7)")


class ScoringRequest(BaseModel):
    """Big Five scoring request model with situational support."""
    session_id: str = Field(..., description="Assessment session identifier")
    responses: List[ResponseItem] = Field(..., min_items=20, max_items=23, description="20-23 Mini-IPIP responses (20 traditional + up to 3 situational)")

    @validator('responses')
    def validate_complete_responses(cls, v):
        """Ensure all required questions are answered."""
        question_ids = {r.question_id for r in v}

        # Traditional questions (1-20) are required
        traditional_ids = set(range(1, 21))
        missing_traditional = traditional_ids - question_ids
        if missing_traditional:
            raise ValueError(f"Missing required traditional questions: {missing_traditional}")

        # Situational questions (21-23) are optional
        situational_ids = set(range(21, 24))
        extra_ids = question_ids - traditional_ids - situational_ids
        if extra_ids:
            raise ValueError(f"Invalid question IDs: {extra_ids}")

        return v


class ScoringResponse(BaseModel):
    """Big Five scoring response model."""
    session_id: str = Field(..., description="Assessment session identifier")
    big_five_scores: Dict[str, Any] = Field(..., description="Complete Big Five scores with metadata")
    score_id: int = Field(..., description="Score record identifier")


class StrengthsRequest(BaseModel):
    """Strengths mapping request model."""
    session_id: Optional[str] = Field(None, description="Session ID for existing scores")
    big_five_scores: Optional[Dict[str, float]] = Field(None, description="Direct Big Five scores")
    responses: Optional[List[ResponseItem]] = Field(None, description="Raw responses if no session_id")

    @model_validator(mode='after')
    def validate_request_data(self):
        """Ensure either session_id or scores+responses are provided."""
        if not self.session_id and not (self.big_five_scores and self.responses):
            raise ValueError("Either session_id or big_five_scores with responses must be provided")
        return self


class StrengthsResponse(BaseModel):
    """Strengths mapping response model."""
    session_id: Optional[str] = Field(None, description="Assessment session identifier")
    strengths_profile: Dict[str, Any] = Field(..., description="Complete strengths profile")


class QualityCheckRequest(BaseModel):
    """Response quality check request model."""
    session_id: Optional[str] = Field(None, description="Session identifier")
    responses: List[ResponseItem] = Field(..., min_items=20, max_items=23, description="20-23 Mini-IPIP responses")
    completion_time_seconds: Optional[float] = Field(None, ge=0, description="Assessment completion time in seconds")


class QualityCheckResponse(BaseModel):
    """Response quality check response model."""
    session_id: Optional[str] = Field(None, description="Session identifier")
    quality_report: Dict[str, Any] = Field(..., description="Detailed quality analysis report")


class ScoreResultResponse(BaseModel):
    """Complete scoring results response model."""
    session_id: str = Field(..., description="Assessment session identifier")
    big_five_scores: Dict[str, Any] = Field(..., description="Big Five personality scores")
    strengths_profile: Optional[Dict[str, Any]] = Field(None, description="Strengths profile if available")
    metadata: Dict[str, Any] = Field(..., description="Scoring metadata and timestamps")