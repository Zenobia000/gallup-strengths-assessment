"""
Recommendation Engine - Core Orchestration for Gallup Strengths Assessment

This module provides the main recommendation engine that orchestrates all
recommendation components to transform personality assessments into actionable
career and development insights.

Design Philosophy:
Following Linus Torvalds' principles of "good taste" - simple coordination
without complex inheritance hierarchies, clear interfaces, and doing one
thing well: orchestrating recommendations.

Key Components Orchestrated:
- StrengthMapper: Big Five → Gallup Strengths mapping
- RuleEngine: Configurable recommendation logic
- CareerMatcher: Job role matching
- DevelopmentPlanner: Personal development suggestions
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import uuid

from .strength_mapper import StrengthMapper, StrengthProfile, StrengthDomain
from .rule_engine import RuleEngine, RecommendationRule
from .career_matcher import CareerMatcher, CareerMatch
from .development_planner import DevelopmentPlanner, DevelopmentPlan


@dataclass
class JobRecommendation:
    """A job role recommendation with matching details."""
    title: str
    chinese_title: str
    match_score: float
    primary_strengths_used: List[str]
    industry_sector: str
    description: str
    required_skills: List[str]
    development_suggestions: List[str]
    confidence_level: str

    def __str__(self) -> str:
        return f"{self.chinese_title} ({self.title}) - 匹配度: {self.match_score:.1f}%"


@dataclass
class RecommendationResult:
    """Complete recommendation result with all insights."""
    session_id: str
    timestamp: datetime
    strength_profile: StrengthProfile
    job_recommendations: List[JobRecommendation]
    development_plan: DevelopmentPlan
    career_matches: List[CareerMatch]
    applied_rules: List[RecommendationRule]
    confidence_score: float
    summary_insights: List[str]
    next_steps: List[str]


class RecommendationEngine:
    """
    Core orchestration engine for generating comprehensive recommendations.

    This class coordinates all recommendation components to provide
    unified, actionable insights based on personality assessment results.
    Following the "single responsibility principle" - it orchestrates,
    not implements the individual recommendation logic.
    """

    def __init__(self):
        """Initialize the recommendation engine with all required components."""
        self.strength_mapper = StrengthMapper()
        self.rule_engine = RuleEngine()
        self.career_matcher = CareerMatcher()
        self.development_planner = DevelopmentPlanner()

    def generate_recommendations(
        self,
        big_five_scores: Dict[str, float],
        user_context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> RecommendationResult:
        """
        Generate comprehensive recommendations based on Big Five scores.

        Args:
            big_five_scores: Dictionary with Big Five dimensions (0-100 scale)
            user_context: Optional context (age, experience, preferences, etc.)
            session_id: Optional session identifier for tracking

        Returns:
            Complete RecommendationResult with all insights
        """
        if session_id is None:
            session_id = str(uuid.uuid4())

        timestamp = datetime.utcnow()

        # Step 1: Generate strength profile using StrengthMapper
        strength_profile = self.strength_mapper.generate_strength_profile(big_five_scores)

        # Step 2: Apply recommendation rules based on strength profile
        applied_rules = self.rule_engine.evaluate_strength_profile(
            strength_profile, user_context or {}
        )

        # Step 3: Generate career matches
        career_matches = self.career_matcher.find_career_matches(
            strength_profile, user_context or {}
        )

        # Step 4: Create job recommendations from career matches
        job_recommendations = self._create_job_recommendations(
            career_matches, strength_profile
        )

        # Step 5: Generate development plan
        development_plan = self.development_planner.create_development_plan(
            strength_profile, career_matches, user_context or {}
        )

        # Step 6: Calculate overall confidence score
        confidence_score = self._calculate_overall_confidence(
            strength_profile, career_matches, applied_rules
        )

        # Step 7: Generate summary insights
        summary_insights = self._generate_summary_insights(
            strength_profile, job_recommendations, applied_rules
        )

        # Step 8: Generate next steps
        next_steps = self._generate_next_steps(
            strength_profile, development_plan, job_recommendations
        )

        return RecommendationResult(
            session_id=session_id,
            timestamp=timestamp,
            strength_profile=strength_profile,
            job_recommendations=job_recommendations,
            development_plan=development_plan,
            career_matches=career_matches,
            applied_rules=applied_rules,
            confidence_score=confidence_score,
            summary_insights=summary_insights,
            next_steps=next_steps
        )

    def _create_job_recommendations(
        self,
        career_matches: List[CareerMatch],
        strength_profile: StrengthProfile
    ) -> List[JobRecommendation]:
        """Convert career matches into detailed job recommendations."""
        job_recommendations = []

        for match in career_matches[:5]:  # Top 5 matches
            # Determine which strengths are most relevant
            primary_strengths = [
                s.theme.chinese_name for s in strength_profile.top_5_strengths[:3]
            ]

            # Generate development suggestions specific to this role
            dev_suggestions = self._generate_role_specific_suggestions(
                match, strength_profile
            )

            # Determine confidence level
            if match.match_score > 80 and match.confidence > 0.8:
                confidence = "high"
            elif match.match_score > 60 and match.confidence > 0.6:
                confidence = "medium"
            else:
                confidence = "low"

            job_rec = JobRecommendation(
                title=match.role_name,
                chinese_title=match.chinese_name,
                match_score=match.match_score,
                primary_strengths_used=primary_strengths,
                industry_sector=match.industry_sector,
                description=match.description,
                required_skills=match.required_strengths,
                development_suggestions=dev_suggestions,
                confidence_level=confidence
            )

            job_recommendations.append(job_rec)

        return job_recommendations

    def _generate_role_specific_suggestions(
        self,
        career_match: CareerMatch,
        strength_profile: StrengthProfile
    ) -> List[str]:
        """Generate development suggestions specific to a career match."""
        suggestions = []

        # Based on role requirements vs current strengths
        top_strength_names = [s.theme.name.lower() for s in strength_profile.top_5_strengths]

        # Role-specific suggestions based on common patterns
        role_suggestions = {
            "manager": [
                "發展團隊建設和員工激勵技能",
                "加強專案管理和資源分配能力",
                "提升決策制定和問題解決技能"
            ],
            "analyst": [
                "深化數據分析和統計學知識",
                "學習商業智能工具和技術",
                "發展批判思考和邏輯推理能力"
            ],
            "consultant": [
                "提升客戶關係管理技能",
                "發展簡報和溝通表達能力",
                "加強行業知識和專業深度"
            ],
            "developer": [
                "持續學習新技術和程式語言",
                "發展系統思維和架構設計能力",
                "提升問題分析和除錯技能"
            ]
        }

        # Find relevant suggestions based on role name
        role_lower = career_match.role_name.lower()
        for key, suggestions_list in role_suggestions.items():
            if key in role_lower:
                suggestions.extend(suggestions_list[:2])
                break

        # Add generic suggestion if no specific ones found
        if not suggestions:
            suggestions.append("運用您的優勢特質在這個角色中創造價值")

        return suggestions[:3]  # Limit to 3 suggestions

    def _calculate_overall_confidence(
        self,
        strength_profile: StrengthProfile,
        career_matches: List[CareerMatch],
        applied_rules: List[RecommendationRule]
    ) -> float:
        """Calculate overall confidence score for the recommendations."""
        # Base confidence from strength profile
        strength_confidence = strength_profile.profile_confidence

        # Career match confidence
        if career_matches:
            avg_career_confidence = sum(match.confidence for match in career_matches[:3]) / min(3, len(career_matches))
        else:
            avg_career_confidence = 0.5

        # Rule application confidence
        if applied_rules:
            avg_rule_confidence = sum(rule.confidence_score for rule in applied_rules) / len(applied_rules)
        else:
            avg_rule_confidence = 0.7  # Default if no specific rules

        # Weighted average
        overall_confidence = (
            strength_confidence * 0.4 +
            avg_career_confidence * 0.4 +
            avg_rule_confidence * 0.2
        )

        return min(1.0, max(0.0, overall_confidence))

    def _generate_summary_insights(
        self,
        strength_profile: StrengthProfile,
        job_recommendations: List[JobRecommendation],
        applied_rules: List[RecommendationRule]
    ) -> List[str]:
        """Generate high-level summary insights."""
        insights = []

        # Top strength insight
        if strength_profile.top_5_strengths:
            top_strength = strength_profile.top_5_strengths[0]
            insights.append(
                f"您的核心優勢「{top_strength.theme.chinese_name}」是您最大的競爭優勢，"
                f"建議在職業發展中重點運用此特質。"
            )

        # Domain distribution insight
        dominant_domains = sorted(
            strength_profile.domain_distribution.items(),
            key=lambda x: x[1],
            reverse=True
        )[:2]

        if len(dominant_domains) >= 2:
            domain_names = {
                StrengthDomain.EXECUTING: "執行力",
                StrengthDomain.INFLUENCING: "影響力",
                StrengthDomain.RELATIONSHIP_BUILDING: "關係建立",
                StrengthDomain.STRATEGIC_THINKING: "戰略思維"
            }

            primary_domain = domain_names.get(dominant_domains[0][0], "未知")
            secondary_domain = domain_names.get(dominant_domains[1][0], "未知")

            insights.append(
                f"您的優勢主要集中在{primary_domain}和{secondary_domain}領域，"
                f"適合需要這些能力的職業發展方向。"
            )

        # Job match insight
        if job_recommendations:
            top_job = job_recommendations[0]
            if top_job.match_score > 80:
                insights.append(
                    f"「{top_job.chinese_title}」與您的優勢特質高度匹配（{top_job.match_score:.1f}%），"
                    f"是值得深入探索的職業方向。"
                )

        return insights[:3]  # Return top 3 insights

    def _generate_next_steps(
        self,
        strength_profile: StrengthProfile,
        development_plan: DevelopmentPlan,
        job_recommendations: List[JobRecommendation]
    ) -> List[str]:
        """Generate actionable next steps."""
        next_steps = []

        # Immediate action based on top strength
        if strength_profile.top_5_strengths:
            next_steps.append(
                f"立即行動：尋找能發揮您「{strength_profile.top_5_strengths[0].theme.chinese_name}」"
                f"優勢的專案或任務機會。"
            )

        # Development priority
        if development_plan and development_plan.priority_areas:
            priority = development_plan.priority_areas[0]
            next_steps.append(
                f"技能發展：優先提升「{priority}」相關技能，"
                f"這將顯著增強您的競爭力。"
            )

        # Career exploration
        if job_recommendations:
            top_job = job_recommendations[0]
            next_steps.append(
                f"職涯探索：深入了解「{top_job.chinese_title}」的職業要求，"
                f"並評估轉職或發展的可能性。"
            )

        # Networking suggestion
        next_steps.append(
            "關係建立：與您目標職業領域的專業人士建立聯繫，"
            "獲得實際工作經驗和見解。"
        )

        return next_steps[:4]  # Return top 4 next steps


def get_recommendation_engine() -> RecommendationEngine:
    """Get a configured RecommendationEngine instance."""
    return RecommendationEngine()