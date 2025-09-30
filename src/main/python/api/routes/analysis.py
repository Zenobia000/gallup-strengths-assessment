"""
深度分析 API 路由
提供個性化的職涯建議、學習資源和行動計劃
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
from pydantic import BaseModel
import logging

from core.analysis.content_analyzer import (
    ContentAnalyzer,
    StrengthProfile,
    CareerRecommendation,
    LearningResource,
    DevelopmentMilestone
)
from core.analysis.archetype_mapper import (
    ArchetypeMapper,
    TalentProfile,
    TALENT_DIMENSIONS
)

logger = logging.getLogger(__name__)
router = APIRouter()

# 初始化分析器
analyzer = ContentAnalyzer()
archetype_mapper = ArchetypeMapper()

# 資料模型
class StrengthScores(BaseModel):
    """優勢分數輸入"""
    scores: Dict[str, float]
    session_id: Optional[str] = None

class CareerRecommendationResponse(BaseModel):
    """職涯建議響應"""
    role: str
    match_score: float
    description: str
    required_skills: List[str]
    growth_path: str
    salary_range: str
    reasons: List[str]

class LearningResourceResponse(BaseModel):
    """學習資源響應"""
    title: str
    type: str
    provider: str
    duration: str
    difficulty: str
    url: str
    relevance_score: float

class DevelopmentMilestoneResponse(BaseModel):
    """發展里程碑響應"""
    timeframe: str
    goal: str
    actions: List[str]
    success_metrics: List[str]
    resources: List[str]

class ProfileAnalysisResponse(BaseModel):
    """完整檔案分析響應"""
    top_strengths: List[Dict]
    synergy_patterns: List[Dict]
    development_areas: List[str]
    career_recommendations: List[CareerRecommendationResponse]
    learning_resources: List[LearningResourceResponse]
    action_plan: List[DevelopmentMilestoneResponse]

@router.post("/analyze-profile", response_model=ProfileAnalysisResponse)
async def analyze_profile(strength_scores: StrengthScores):
    """
    分析用戶優勢檔案並提供完整建議
    """
    try:
        # 分析優勢檔案
        profile = analyzer.analyze_profile(strength_scores.scores)

        # 生成職涯建議
        career_recs = analyzer.generate_career_recommendations(profile)

        # 生成學習資源
        learning_resources = analyzer.generate_learning_path(profile)

        # 生成行動計劃
        action_plan = analyzer.generate_action_plan(profile)

        # 組合響應
        response = ProfileAnalysisResponse(
            top_strengths=[
                {'name': name, 'score': score}
                for name, score in profile.top_strengths
            ],
            synergy_patterns=profile.synergy_patterns,
            development_areas=profile.development_areas,
            career_recommendations=[
                CareerRecommendationResponse(
                    role=rec.role,
                    match_score=rec.match_score,
                    description=rec.description,
                    required_skills=rec.required_skills,
                    growth_path=rec.growth_path,
                    salary_range=rec.salary_range,
                    reasons=rec.reasons
                )
                for rec in career_recs
            ],
            learning_resources=[
                LearningResourceResponse(
                    title=res.title,
                    type=res.type,
                    provider=res.provider,
                    duration=res.duration,
                    difficulty=res.difficulty,
                    url=res.url,
                    relevance_score=res.relevance_score
                )
                for res in learning_resources
            ],
            action_plan=[
                DevelopmentMilestoneResponse(
                    timeframe=milestone.timeframe,
                    goal=milestone.goal,
                    actions=milestone.actions,
                    success_metrics=milestone.success_metrics,
                    resources=milestone.resources
                )
                for milestone in action_plan
            ]
        )

        logger.info(f"Profile analysis completed for session: {strength_scores.session_id}")
        return response

    except Exception as e:
        logger.error(f"Error analyzing profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/career-recommendations")
async def get_career_recommendations(
    session_id: str = Query(..., description="Session ID"),
    num_recommendations: int = Query(5, ge=1, le=10)
):
    """
    獲取職涯建議
    """
    try:
        # 這裡應該從資料庫獲取用戶分數
        # 暫時使用示例數據
        sample_scores = {
            '戰略思維': 95,
            '創新思維': 91,
            '影響力': 88,
            '分析力': 85,
            '執行力': 72,
            '溝通': 86,
            '學習力': 78,
            '適應力': 82,
            '責任感': 83,
            '積極性': 79,
            '同理心': 74,
            '專注力': 70
        }

        profile = analyzer.analyze_profile(sample_scores)
        recommendations = analyzer.generate_career_recommendations(
            profile,
            num_recommendations
        )

        return [
            CareerRecommendationResponse(
                role=rec.role,
                match_score=rec.match_score,
                description=rec.description,
                required_skills=rec.required_skills,
                growth_path=rec.growth_path,
                salary_range=rec.salary_range,
                reasons=rec.reasons
            )
            for rec in recommendations
        ]

    except Exception as e:
        logger.error(f"Error getting career recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning-path")
async def get_learning_path(
    session_id: str = Query(..., description="Session ID"),
    timeframe: int = Query(90, ge=30, le=365, description="Timeframe in days")
):
    """
    獲取個性化學習路徑
    """
    try:
        # 暫時使用示例數據
        sample_scores = {
            '戰略思維': 95,
            '創新思維': 91,
            '影響力': 88,
            '分析力': 85,
            '執行力': 72,
            '溝通': 86,
            '學習力': 78,
            '適應力': 82,
            '責任感': 83,
            '積極性': 79,
            '同理心': 74,
            '專注力': 70
        }

        profile = analyzer.analyze_profile(sample_scores)
        resources = analyzer.generate_learning_path(profile, timeframe)

        return [
            LearningResourceResponse(
                title=res.title,
                type=res.type,
                provider=res.provider,
                duration=res.duration,
                difficulty=res.difficulty,
                url=res.url,
                relevance_score=res.relevance_score
            )
            for res in resources
        ]

    except Exception as e:
        logger.error(f"Error getting learning path: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/action-plan")
async def get_action_plan(
    session_id: str = Query(..., description="Session ID")
):
    """
    獲取90天行動計劃
    """
    try:
        # 暫時使用示例數據
        sample_scores = {
            '戰略思維': 95,
            '創新思維': 91,
            '影響力': 88,
            '分析力': 85,
            '執行力': 72,
            '溝通': 86,
            '學習力': 78,
            '適應力': 82,
            '責任感': 83,
            '積極性': 79,
            '同理心': 74,
            '專注力': 70
        }

        profile = analyzer.analyze_profile(sample_scores)
        milestones = analyzer.generate_action_plan(profile)

        return [
            DevelopmentMilestoneResponse(
                timeframe=milestone.timeframe,
                goal=milestone.goal,
                actions=milestone.actions,
                success_metrics=milestone.success_metrics,
                resources=milestone.resources
            )
            for milestone in milestones
        ]

    except Exception as e:
        logger.error(f"Error getting action plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/career-archetype")
async def analyze_career_archetype(strength_scores: StrengthScores):
    """
    分析職業原型（基於凱爾西氣質理論）
    """
    try:
        # 將分數轉換為T1-T12格式
        talent_scores = {}
        for key, value in strength_scores.scores.items():
            # 如果key已經是T1-T12格式，直接使用
            if key.startswith('T'):
                talent_scores[key] = value
            else:
                # 嘗試映射到T1-T12
                # 這裡需要一個映射表，暫時使用簡單的對應
                talent_map = {
                    '戰略思維': 'T4',  # 分析與洞察
                    '創新思維': 'T3',  # 探索與創新
                    '影響力': 'T5',    # 影響與倡議
                    '執行力': 'T1',    # 結構化執行
                    '分析力': 'T4',    # 分析與洞察
                    '溝通': 'T6',      # 協作與共好
                    '學習力': 'T8',    # 學習與成長
                    '適應力': 'T10',   # 壓力調節
                    '責任感': 'T12',   # 責任與當責
                    '積極性': 'T5',    # 影響與倡議
                    '同理心': 'T6',    # 協作與共好
                    '專注力': 'T2'     # 品質與完備
                }
                if key in talent_map:
                    talent_scores[talent_map[key]] = value

        # 分類天賦
        talent_profile = archetype_mapper.classify_talents(talent_scores)

        # 映射到職業原型
        archetype = archetype_mapper.map_to_archetype(talent_profile)

        # 分析協同效應
        dominant_ids = [t[0] for t in talent_profile.dominant_talents]
        synergy_analysis = archetype_mapper.get_synergy_analysis(dominant_ids)

        # 獲取發展建議
        development_suggestions = archetype_mapper.get_development_suggestions(talent_profile)

        return {
            'archetype': {
                'id': archetype.archetype_id,
                'name': archetype.archetype_name,
                'temperament': archetype.keirsey_temperament,
                'mbti_correlates': archetype.mbti_correlates,
                'description': archetype.description,
                'career_suggestions': archetype.career_suggestions
            },
            'talent_hierarchy': {
                'dominant': [
                    {'id': t[0], 'name': TALENT_DIMENSIONS.get(t[0], t[0]), 'score': t[1]}
                    for t in talent_profile.dominant_talents
                ],
                'supporting': [
                    {'id': t[0], 'name': TALENT_DIMENSIONS.get(t[0], t[0]), 'score': t[1]}
                    for t in talent_profile.supporting_talents
                ],
                'lesser': [
                    {'id': t[0], 'name': TALENT_DIMENSIONS.get(t[0], t[0]), 'score': t[1]}
                    for t in talent_profile.lesser_talents
                ]
            },
            'synergy_analysis': synergy_analysis,
            'development_suggestions': development_suggestions
        }

    except Exception as e:
        logger.error(f"Error analyzing career archetype: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strength-synergies")
async def get_strength_synergies(
    strength1: str = Query(..., description="First strength"),
    strength2: str = Query(..., description="Second strength")
):
    """
    獲取優勢協同效應分析
    """
    try:
        key = tuple(sorted([strength1, strength2]))

        if key in analyzer.synergy_patterns:
            synergy = analyzer.synergy_patterns[key]
            return {
                'strengths': key,
                'name': synergy['name'],
                'description': synergy['description'],
                'bonus_careers': synergy.get('bonus_careers', []),
                'multiplier': synergy['multiplier']
            }
        else:
            return {
                'strengths': [strength1, strength2],
                'name': '獨特組合',
                'description': f'{strength1}與{strength2}的結合創造了獨特的優勢組合',
                'bonus_careers': [],
                'multiplier': 1.1
            }

    except Exception as e:
        logger.error(f"Error getting synergies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))