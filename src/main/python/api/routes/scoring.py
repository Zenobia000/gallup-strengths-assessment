"""
計分 API 端點
提供 Mini-IPIP 計分與優勢映射服務

端點包含:
- POST /api/scoring/calculate - 計算 Big Five 分數
- POST /api/scoring/strengths - 計算優勢檔案
- GET /api/scoring/results/{session_id} - 取得計分結果
- POST /api/scoring/quality-check - 品質檢查
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from utils.sqlalchemy_db import get_db
from models.database import AssessmentSession, AssessmentResponse, Score
from models.schemas import (
    ScoringRequest, ScoringResponse, StrengthsRequest, StrengthsResponse,
    QualityCheckRequest, QualityCheckResponse, ScoreResultResponse
)
from core.scoring import MiniIPIPScorer, ResponseQualityChecker, StrengthMapper

router = APIRouter(prefix="/api/scoring", tags=["scoring"])

# 依賴注入
def get_scorer():
    """取得計分器實例"""
    return MiniIPIPScorer(version="1.0")

def get_quality_checker():
    """取得品質檢查器實例"""
    return ResponseQualityChecker()

def get_strength_mapper():
    """取得優勢映射器實例"""
    return StrengthMapper()


@router.post("/calculate", response_model=ScoringResponse)
async def calculate_big_five_scores(
    request: ScoringRequest,
    db: Session = Depends(get_db),
    scorer: MiniIPIPScorer = Depends(get_scorer)
):
    """
    計算 Big Five 人格分數

    Args:
        request: 包含 session_id 和 responses 的請求
        db: 資料庫會話
        scorer: Mini-IPIP 計分器

    Returns:
        ScoringResponse: Big Five 分數結果
    """
    try:
        # 驗證會話存在
        session = db.query(AssessmentSession).filter(
            AssessmentSession.session_id == request.session_id
        ).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment session not found"
            )

        # 驗證回答完整性
        if len(request.responses) != 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Expected 20 responses, got {len(request.responses)}"
            )

        # 提取回答值
        response_values = [r.response_value for r in request.responses]

        # 計算 Big Five 分數
        big_five_scores = scorer.calculate_scores(response_values)

        # 儲存分數到資料庫
        score_record = Score(
            session_id=request.session_id,
            raw_scores=json.dumps({
                "extraversion": big_five_scores.raw_extraversion,
                "agreeableness": big_five_scores.raw_agreeableness,
                "conscientiousness": big_five_scores.raw_conscientiousness,
                "neuroticism": big_five_scores.raw_neuroticism,
                "openness": big_five_scores.raw_openness
            }),
            standardized_scores=json.dumps({
                "extraversion": big_five_scores.standardized_extraversion,
                "agreeableness": big_five_scores.standardized_agreeableness,
                "conscientiousness": big_five_scores.standardized_conscientiousness,
                "neuroticism": big_five_scores.standardized_neuroticism,
                "openness": big_five_scores.standardized_openness
            }),
            percentiles=json.dumps({
                "extraversion": big_five_scores.percentile_extraversion,
                "agreeableness": big_five_scores.percentile_agreeableness,
                "conscientiousness": big_five_scores.percentile_conscientiousness,
                "neuroticism": big_five_scores.percentile_neuroticism,
                "openness": big_five_scores.percentile_openness
            }),
            confidence_level=big_five_scores.confidence_level.value,
            quality_flags=json.dumps(big_five_scores.quality_flags),
            scoring_version=big_five_scores.scoring_version,
            computation_time_ms=big_five_scores.computation_time_ms,
            created_at=datetime.utcnow()
        )

        db.add(score_record)
        db.commit()
        db.refresh(score_record)

        return ScoringResponse(
            session_id=request.session_id,
            big_five_scores=big_five_scores.to_dict(),
            score_id=score_record.id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scoring calculation failed: {str(e)}"
        )


@router.post("/strengths", response_model=StrengthsResponse)
async def calculate_strengths_profile(
    request: StrengthsRequest,
    db: Session = Depends(get_db),
    scorer: MiniIPIPScorer = Depends(get_scorer),
    mapper: StrengthMapper = Depends(get_strength_mapper)
):
    """
    計算優勢檔案

    Args:
        request: 包含 session_id 的請求 (或直接提供 Big Five 分數)
        db: 資料庫會話
        scorer: Mini-IPIP 計分器
        mapper: 優勢映射器

    Returns:
        StrengthsResponse: 完整優勢檔案
    """
    try:
        big_five_scores = None

        if request.session_id:
            # 從資料庫取得現有分數
            score_record = db.query(Score).filter(
                Score.session_id == request.session_id
            ).first()

            if not score_record:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No scores found for this session. Calculate Big Five scores first."
                )

            # 重建 BigFiveScores 物件
            raw_scores = json.loads(score_record.raw_scores)
            standardized_scores = json.loads(score_record.standardized_scores)
            percentiles = json.loads(score_record.percentiles)

            from core.scoring.mini_ipip_scorer import BigFiveScores, ScoreConfidence
            big_five_scores = BigFiveScores(
                raw_extraversion=raw_scores["extraversion"],
                raw_agreeableness=raw_scores["agreeableness"],
                raw_conscientiousness=raw_scores["conscientiousness"],
                raw_neuroticism=raw_scores["neuroticism"],
                raw_openness=raw_scores["openness"],
                standardized_extraversion=standardized_scores["extraversion"],
                standardized_agreeableness=standardized_scores["agreeableness"],
                standardized_conscientiousness=standardized_scores["conscientiousness"],
                standardized_neuroticism=standardized_scores["neuroticism"],
                standardized_openness=standardized_scores["openness"],
                percentile_extraversion=percentiles["extraversion"],
                percentile_agreeableness=percentiles["agreeableness"],
                percentile_conscientiousness=percentiles["conscientiousness"],
                percentile_neuroticism=percentiles["neuroticism"],
                percentile_openness=percentiles["openness"],
                confidence_level=ScoreConfidence(score_record.confidence_level),
                quality_flags=json.loads(score_record.quality_flags),
                scoring_version=score_record.scoring_version,
                computation_time_ms=score_record.computation_time_ms,
                timestamp=score_record.created_at.strftime("%Y-%m-%d %H:%M:%S")
            )

        elif request.big_five_scores:
            # 使用提供的 Big Five 分數
            responses = [r.response_value for r in request.responses]
            big_five_scores = scorer.calculate_scores(responses)

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either session_id or big_five_scores with responses must be provided"
            )

        # 計算優勢檔案
        strengths_profile = mapper.map_strengths(big_five_scores)

        # 儲存優勢結果 (擴展 Score 表或建立新表)
        if request.session_id:
            score_record = db.query(Score).filter(
                Score.session_id == request.session_id
            ).first()
            if score_record:
                score_record.strengths_profile = json.dumps(strengths_profile.to_dict())
                score_record.updated_at = datetime.utcnow()
                db.commit()

        return StrengthsResponse(
            session_id=request.session_id,
            strengths_profile=strengths_profile.to_dict()
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Strengths calculation failed: {str(e)}"
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


@router.post("/quality-check", response_model=QualityCheckResponse)
async def check_response_quality(
    request: QualityCheckRequest,
    checker: ResponseQualityChecker = Depends(get_quality_checker)
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
    scorer: MiniIPIPScorer = Depends(get_scorer)
):
    """
    取得計分引擎元資料

    Returns:
        Dict: 計分引擎配置與元資料
    """
    return {
        "scorer_metadata": scorer.get_scoring_metadata(),
        "api_version": "1.0",
        "supported_endpoints": [
            "/api/scoring/calculate",
            "/api/scoring/strengths",
            "/api/scoring/results/{session_id}",
            "/api/scoring/quality-check",
            "/api/scoring/metadata"
        ]
    }