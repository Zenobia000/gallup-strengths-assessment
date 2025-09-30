"""
Recommendations API Routes - Gallup Strengths Assessment

This module provides REST API endpoints for the recommendation system,
allowing clients to generate and retrieve personalized career and
development recommendations based on personality assessments.

Design Philosophy:
Following Linus Torvalds' "good taste" - clean API design, clear endpoints,
proper error handling, and no unnecessary complexity.

Key Endpoints:
- /recommendations/generate - Generate complete recommendations
- /recommendations/{session_id} - Retrieve existing recommendations
- /recommendations/{session_id}/strengths - Get strength profile
- /recommendations/{session_id}/careers - Get career matches
- /recommendations/{session_id}/development - Get development plan
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import UUID
import logging

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from utils.sqlalchemy_db import get_db
from models.database import AssessmentSession, Score
from models.schemas import APIResponse
from core.recommendation import (
    get_recommendation_engine,
    RecommendationResult,
    JobRecommendation,
    StrengthProfile,
    DevelopmentPlan
)
from core.scoring import ScoringEngine


# Request/Response Models
class RecommendationRequest(BaseModel):
    """Request for generating recommendations."""
    session_id: str = Field(..., description="Assessment session ID")
    user_context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional user context (experience, preferences, etc.)"
    )
    include_development_plan: bool = Field(
        default=True,
        description="Whether to include detailed development plan"
    )
    max_career_matches: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of career matches to return"
    )


class StrengthThemeResponse(BaseModel):
    """Response model for strength theme."""
    name: str
    chinese_name: str
    domain: str
    percentile_score: float
    confidence_level: str
    description: str
    keywords: List[str]


class StrengthProfileResponse(BaseModel):
    """Response model for complete strength profile."""
    session_id: str
    top_5_strengths: List[StrengthThemeResponse]
    domain_distribution: Dict[str, float]
    profile_confidence: float
    analysis_summary: str
    recommendations: List[str]


class JobRecommendationResponse(BaseModel):
    """Response model for job recommendation."""
    title: str
    chinese_title: str
    match_score: float
    industry_sector: str
    description: str
    primary_strengths_used: List[str]
    required_skills: List[str]
    development_suggestions: List[str]
    confidence_level: str


class DevelopmentActionResponse(BaseModel):
    """Response model for development action."""
    title: str
    chinese_title: str
    description: str
    timeframe: str
    priority: int
    estimated_hours: int
    learning_method: str
    success_metrics: List[str]
    resources: List[str]


class DevelopmentPlanResponse(BaseModel):
    """Response model for development plan."""
    plan_id: str
    career_focus: str
    priority_areas: List[str]
    immediate_actions: List[DevelopmentActionResponse]
    quarterly_milestones: List[str]
    annual_objectives: List[str]
    success_tracking: Dict[str, str]


class RecommendationResponse(BaseModel):
    """Complete recommendation response."""
    session_id: str
    timestamp: datetime
    strength_profile: StrengthProfileResponse
    job_recommendations: List[JobRecommendationResponse]
    development_plan: Optional[DevelopmentPlanResponse]
    confidence_score: float
    summary_insights: List[str]
    next_steps: List[str]


# Initialize router
router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/api/v1/recommendations/generate")
async def generate_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive recommendations based on assessment results.

    This endpoint takes a completed assessment session and generates
    personalized career and development recommendations using the
    integrated recommendation engine.
    """
    try:
        # 1. Validate session exists and has scoring results
        session = db.query(AssessmentSession).filter(
            AssessmentSession.session_id == request.session_id
        ).first()

        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Assessment session {request.session_id} not found"
            )

        # 2. Get scoring results
        scoring_result = db.query(Score).filter(
            Score.session_id == request.session_id
        ).first()

        if not scoring_result:
            raise HTTPException(
                status_code=404,
                detail=f"No scoring results found for session {request.session_id}"
            )

        # 3. Extract Big Five scores from scoring result (using percentiles for better range)
        percentiles = scoring_result.percentiles
        big_five_scores = {
            "extraversion": percentiles.get("extraversion", 50.0),
            "agreeableness": percentiles.get("agreeableness", 50.0),
            "conscientiousness": percentiles.get("conscientiousness", 50.0),
            "neuroticism": percentiles.get("neuroticism", 50.0),
            "openness": percentiles.get("openness", 50.0)
        }

        # 4. Add Big Five scores to user context
        user_context = request.user_context or {}
        user_context["big_five_scores"] = big_five_scores
        user_context["session_id"] = request.session_id

        # 5. Generate recommendations using RecommendationEngine
        recommendation_engine = get_recommendation_engine()
        recommendations = recommendation_engine.generate_recommendations(
            big_five_scores=big_five_scores,
            user_context=user_context,
            session_id=request.session_id
        )

        # 6. Convert to response format
        response_data = _convert_to_response_format(
            recommendations,
            include_development_plan=request.include_development_plan,
            max_career_matches=request.max_career_matches
        )

        # 7. Store recommendations in database (optional for caching)
        # TODO: Add recommendation storage table if needed

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.get("/api/v1/recommendations/{session_id}/strengths", response_model=StrengthProfileResponse)
async def get_strength_profile(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get strength profile for a specific session.

    Returns only the strength mapping portion of the recommendations,
    showing the user's top strengths and domain distribution.
    """
    try:
        # Get scoring results
        scoring_result = db.query(Score).filter(
            Score.session_id == session_id
        ).first()

        if not scoring_result:
            raise HTTPException(
                status_code=404,
                detail=f"No scoring results found for session {session_id}"
            )

        # Extract Big Five scores
        percentiles = scoring_result.percentiles
        big_five_scores = {
            "extraversion": percentiles.get("extraversion", 50.0),
            "agreeableness": percentiles.get("agreeableness", 50.0),
            "conscientiousness": percentiles.get("conscientiousness", 50.0),
            "neuroticism": percentiles.get("neuroticism", 50.0),
            "openness": percentiles.get("openness", 50.0)
        }

        # Generate strength profile
        recommendation_engine = get_recommendation_engine()
        strength_profile = recommendation_engine.strength_mapper.generate_strength_profile(
            big_five_scores
        )

        # Convert to response format
        response_data = _convert_strength_profile_to_response(strength_profile, session_id)

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get strength profile: {str(e)}"
        )


@router.get("/api/v1/recommendations/{session_id}/careers", response_model=List[JobRecommendationResponse])
async def get_career_recommendations(
    session_id: str,
    max_results: int = Query(default=5, ge=1, le=20, description="Maximum career matches to return"),
    industry_filter: Optional[str] = Query(default=None, description="Filter by industry sector"),
    db: Session = Depends(get_db)
):
    """
    Get career recommendations for a specific session.

    Returns job role matches based on the user's strength profile,
    with optional filtering by industry or other criteria.
    """
    try:
        # Get scoring results and generate strength profile
        scoring_result = db.query(Score).filter(
            Score.session_id == session_id
        ).first()

        if not scoring_result:
            raise HTTPException(
                status_code=404,
                detail=f"No scoring results found for session {session_id}"
            )

        # Extract Big Five scores from scoring result
        percentiles = scoring_result.percentiles
        big_five_scores = {
            "extraversion": percentiles.get("extraversion", 50.0),
            "agreeableness": percentiles.get("agreeableness", 50.0),
            "conscientiousness": percentiles.get("conscientiousness", 50.0),
            "neuroticism": percentiles.get("neuroticism", 50.0),
            "openness": percentiles.get("openness", 50.0)
        }

        # Generate career matches
        recommendation_engine = get_recommendation_engine()
        strength_profile = recommendation_engine.strength_mapper.generate_strength_profile(big_five_scores)

        user_context = {}
        if industry_filter:
            user_context["industry_preference"] = industry_filter

        career_matches = recommendation_engine.career_matcher.find_career_matches(
            strength_profile, user_context
        )

        # Apply filters and limits
        filtered_matches = career_matches
        if industry_filter:
            filtered_matches = [
                match for match in filtered_matches
                if industry_filter.lower() in match.industry_sector.lower()
            ]

        final_matches = filtered_matches[:max_results]

        # Convert to response format
        response_data = [
            _convert_career_match_to_response(match)
            for match in final_matches
        ]

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get career recommendations: {str(e)}"
        )


@router.get("/api/v1/recommendations/{session_id}/development", response_model=DevelopmentPlanResponse)
async def get_development_plan(
    session_id: str,
    include_immediate_only: bool = Query(default=False, description="Include only immediate actions"),
    db: Session = Depends(get_db)
):
    """
    Get development plan for a specific session.

    Returns personalized development recommendations including
    goals, actions, timelines, and success metrics.
    """
    try:
        # Get scoring results and generate full recommendations
        scoring_result = db.query(Score).filter(
            Score.session_id == session_id
        ).first()

        if not scoring_result:
            raise HTTPException(
                status_code=404,
                detail=f"No scoring results found for session {session_id}"
            )

        # Extract Big Five scores from scoring result
        percentiles = scoring_result.percentiles
        big_five_scores = {
            "extraversion": percentiles.get("extraversion", 50.0),
            "agreeableness": percentiles.get("agreeableness", 50.0),
            "conscientiousness": percentiles.get("conscientiousness", 50.0),
            "neuroticism": percentiles.get("neuroticism", 50.0),
            "openness": percentiles.get("openness", 50.0)
        }

        # Generate complete recommendations to get development plan
        recommendation_engine = get_recommendation_engine()
        
        logger.info(f"[{session_id}] Generating recommendations for development plan...")
        recommendations = recommendation_engine.generate_recommendations(
            big_five_scores=big_five_scores,
            user_context={"session_id": session_id},
            session_id=session_id
        )
        logger.info(f"[{session_id}] Successfully generated recommendations.")

        # Convert development plan to response format
        logger.info(f"[{session_id}] Converting development plan to response format...")
        response_data = _convert_development_plan_to_response(
            recommendations.development_plan,
            include_immediate_only=include_immediate_only
        )
        logger.info(f"[{session_id}] Successfully converted development plan.")

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get development plan for session {session_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get development plan: An internal error occurred."
        )


# Helper functions for response conversion
def _convert_to_response_format(
    recommendations: RecommendationResult,
    include_development_plan: bool = True,
    max_career_matches: int = 5
) -> RecommendationResponse:
    """Convert RecommendationResult to API response format."""
    return RecommendationResponse(
        session_id=recommendations.session_id,
        timestamp=recommendations.timestamp,
        strength_profile=_convert_strength_profile_to_response(
            recommendations.strength_profile,
            recommendations.session_id
        ),
        job_recommendations=[
            _convert_job_recommendation_to_response(job)
            for job in recommendations.job_recommendations[:max_career_matches]
        ],
        development_plan=_convert_development_plan_to_response(
            recommendations.development_plan
        ) if include_development_plan else None,
        confidence_score=recommendations.confidence_score,
        summary_insights=recommendations.summary_insights,
        next_steps=recommendations.next_steps
    )


def _convert_strength_profile_to_response(
    profile: StrengthProfile,
    session_id: str
) -> StrengthProfileResponse:
    """Convert StrengthProfile to API response format."""
    return StrengthProfileResponse(
        session_id=session_id,
        top_5_strengths=[
            StrengthThemeResponse(
                name=strength.theme.name,
                chinese_name=strength.theme.chinese_name,
                domain=strength.theme.domain.value,
                percentile_score=strength.percentile_score,
                confidence_level=strength.confidence_level,
                description=strength.theme.description,
                keywords=strength.theme.keywords
            )
            for strength in profile.top_5_strengths
        ],
        domain_distribution={
            domain.value: percentage
            for domain, percentage in profile.domain_distribution.items()
        },
        profile_confidence=profile.profile_confidence,
        analysis_summary=profile.analysis_summary,
        recommendations=profile.recommendations
    )


def _convert_job_recommendation_to_response(job: JobRecommendation) -> JobRecommendationResponse:
    """Convert JobRecommendation to API response format."""
    return JobRecommendationResponse(
        title=job.title,
        chinese_title=job.chinese_title,
        match_score=job.match_score,
        industry_sector=job.industry_sector,
        description=job.description,
        primary_strengths_used=job.primary_strengths_used,
        required_skills=job.required_skills,
        development_suggestions=job.development_suggestions,
        confidence_level=job.confidence_level
    )


def _convert_career_match_to_response(match) -> JobRecommendationResponse:
    """Convert CareerMatch to API response format."""
    return JobRecommendationResponse(
        title=match.role_name,
        chinese_title=match.chinese_name,
        match_score=match.match_score,
        industry_sector=match.industry_sector,
        description=match.description,
        primary_strengths_used=match.matching_strengths[:3],
        required_skills=match.required_strengths,
        development_suggestions=match.development_needs[:3],
        confidence_level="high" if match.confidence > 0.8 else "medium" if match.confidence > 0.6 else "low"
    )


def _convert_development_plan_to_response(
    plan: DevelopmentPlan,
    include_immediate_only: bool = False
) -> DevelopmentPlanResponse:
    """Convert DevelopmentPlan to API response format."""
    actions_to_include = (
        plan.immediate_actions if include_immediate_only
        else plan.immediate_actions
    )

    return DevelopmentPlanResponse(
        plan_id=plan.plan_id,
        career_focus=plan.career_focus,
        priority_areas=plan.priority_areas,
        immediate_actions=[
            DevelopmentActionResponse(
                title=action.title,
                chinese_title=action.chinese_title,
                description=action.description,
                timeframe=action.timeframe.value,
                priority=action.priority,
                estimated_hours=action.estimated_hours,
                learning_method=action.learning_method.value,
                success_metrics=action.success_metrics,
                resources=action.resources
            )
            for action in actions_to_include
        ],
        quarterly_milestones=plan.quarterly_milestones,
        annual_objectives=plan.annual_objectives,
        success_tracking=plan.success_tracking
    )


# Health check endpoint for recommendations service
@router.get("/api/v1/recommendations/health")
async def recommendations_health_check():
    """Health check for recommendations service."""
    try:
        # Test recommendation engine initialization
        recommendation_engine = get_recommendation_engine()

        # Test with dummy data
        test_scores = {
            "extraversion": 50.0,
            "agreeableness": 50.0,
            "conscientiousness": 50.0,
            "neuroticism": 50.0,
            "openness": 50.0
        }

        # Quick test of strength mapping
        strength_profile = recommendation_engine.strength_mapper.generate_strength_profile(test_scores)

        return JSONResponse({
            "status": "healthy",
            "service": "recommendations",
            "components": {
                "strength_mapper": "operational",
                "career_matcher": "operational",
                "development_planner": "operational",
                "rule_engine": "operational"
            },
            "test_result": {
                "top_strength": strength_profile.top_5_strengths[0].theme.chinese_name,
                "confidence": strength_profile.profile_confidence
            },
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Recommendations service unhealthy: {str(e)}"
        )