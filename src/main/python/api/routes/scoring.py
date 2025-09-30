"""
計分 API 端點
提供 Mini-IPIP 計分與優勢映射服務

端點包含:
- POST /api/scoring/calculate - 計算 Big Five 分數
- POST /api/scoring/strengths - 計算優勢檔案
- GET /api/scoring/results/{session_id} - 取得計分結果
- POST /api/scoring/quality-check - 品質檢查
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
import logging
import json

from utils.sqlalchemy_db import get_db
from models.database import Score
from models.schemas import (
    ScoringRequest, 
    ScoringResponse, 
    APIResponse, 
    ScoreResultResponse, 
    QuestionResponse,
    QualityCheckRequest,
    QualityCheckResponse
)
from core.scoring import ScoringEngine, DimensionScores

router = APIRouter()
logger = logging.getLogger(__name__)


def get_scorer():
    """Dependency injector for ScoringEngine."""
    return ScoringEngine()


@router.post("/api/v1/scoring/calculate", response_model=APIResponse)
async def calculate_big_five_scores(
    request: ScoringRequest,
    db: Session = Depends(get_db),
    scorer: ScoringEngine = Depends(get_scorer)
):
    """
    Calculate and save comprehensive psychometric scores.
    """
    logger.info(f"Received scoring request for session_id: {request.session_id}")
    try:
        # 1. Convert request for ScoringEngine
        question_responses = [
            QuestionResponse(question_id=r.question_id, score=r.response_value)
            for r in request.responses
        ]

        # 2. Calculate scores using ScoringEngine
        logger.info("Calculating dimension scores...")
        dimension_scores = scorer.create_dimension_scores(question_responses)
        logger.info(f"Successfully calculated dimension scores: {dimension_scores}")

        # 3. Create or update Score record in database
        logger.info("Saving scores to the database...")
        score_record = db.query(Score).filter_by(session_id=request.session_id).first()
        if not score_record:
            score_record = Score(session_id=request.session_id)
        
        # NOTE: This is a temporary adaptation. The Score model expects more detailed
        # scores (raw, percentiles, etc.) which the basic ScoringEngine does not
        # currently provide. We are populating it with the available data.
        scores_dict = dimension_scores.to_dict()
        score_record.raw_scores = scores_dict
        score_record.standardized_scores = scores_dict # Placeholder
        score_record.percentiles = scores_dict # Placeholder
        score_record.confidence_level = "medium" # Placeholder
        score_record.quality_flags = [] # Placeholder
        score_record.scoring_confidence = 0.85 # Placeholder
        score_record.scoring_version = "1.0.0-basic"
        score_record.computation_time_ms = 50.0 # Placeholder
        score_record.norms_version = "dev-norms-v1" # Placeholder
        
        db.add(score_record)
        db.commit()
        db.refresh(score_record)
        logger.info(f"Successfully saved scores for session_id: {request.session_id}")

        # 4. Prepare and return response
        response_data = ScoringResponse(
            session_id=request.session_id,
            big_five_scores=scores_dict,
            score_id=score_record.id
        )

        return APIResponse(
            success=True,
            data=response_data.dict()
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to calculate scores for session {request.session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate scores: {str(e)}"
        )


@router.get("/results/{session_id}", response_model=ScoreResultResponse)
async def get_scoring_results(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    取得完整計分結果

    Args:
        session_id: 會話 ID
        db: 資料庫會話

    Returns:
        ScoreResultResponse: 完整計分結果
    """
    try:
        # 查詢分數記錄
        score_record = db.query(Score).filter(
            Score.session_id == session_id
        ).first()

        if not score_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No scoring results found for this session"
            )

        # 準備回應資料
        response_data = {
            "session_id": session_id,
            "big_five_scores": {
                "raw_scores": json.loads(score_record.raw_scores),
                "standardized_scores": json.loads(score_record.standardized_scores),
                "percentiles": json.loads(score_record.percentiles)
            },
            "metadata": {
                "confidence_level": score_record.confidence_level,
                "quality_flags": json.loads(score_record.quality_flags),
                "scoring_version": score_record.scoring_version,
                "computation_time_ms": score_record.computation_time_ms,
                "created_at": score_record.created_at.isoformat(),
                "updated_at": score_record.updated_at.isoformat() if score_record.updated_at else None
            }
        }

        # 如果有優勢檔案，也包含進來
        if hasattr(score_record, 'strengths_profile') and score_record.strengths_profile:
            response_data["strengths_profile"] = json.loads(score_record.strengths_profile)

        return ScoreResultResponse(**response_data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve results: {str(e)}"
        )


# TODO: Re-implement quality checking after core functionality is stable
# @router.post("/quality-check", response_model=QualityCheckResponse)
async def check_response_quality_DISABLED(
    request: QualityCheckRequest
):
    """
    檢查回答品質

    Args:
        request: 包含回答和完成時間的請求
        checker: 品質檢查器

    Returns:
        QualityCheckResponse: 品質檢查結果
    """
    try:
        response_values = [r.response_value for r in request.responses]

        # 執行品質檢查
        quality_report = checker.generate_quality_report(
            response_values,
            request.completion_time_seconds
        )

        return QualityCheckResponse(
            session_id=request.session_id,
            quality_report=quality_report
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quality check failed: {str(e)}"
        )


@router.get("/metadata")
async def get_scoring_metadata(
    scorer: ScoringEngine = Depends(get_scorer)
):
    """
    取得計分引擎元資料

    Returns:
        Dict: 計分引擎配置與元資料
    """
    return {
        "scorer_metadata": {
            "engine": "ScoringEngine",
            "version": "1.0.0-basic",
            "dimensions": list(scorer.DIMENSION_QUESTIONS.keys()),
            "questions_per_dimension": scorer.QUESTIONS_PER_DIMENSION,
            "score_range": [scorer.MIN_DIMENSION_SCORE, scorer.MAX_DIMENSION_SCORE],
            "scale_support": ["7-point (with conversion)", "5-point (native)"]
        },
        "api_version": "1.0",
        "supported_endpoints": [
            "/api/scoring/calculate",
            "/api/scoring/results/{session_id}",
            "/api/scoring/metadata"
        ],
        "disabled_endpoints": [
            "/api/scoring/strengths (TODO)",
            "/api/scoring/quality-check (TODO)"
        ]
    }