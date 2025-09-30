"""
Development Planner - Personalized Growth and Skill Development

This module creates personalized development plans based on strength profiles
and career goals. It provides actionable development suggestions, learning
paths, and growth strategies tailored to individual strengths and aspirations.

Design Philosophy:
Following Linus Torvalds' "good taste" principle - clear development pathways
without overcomplicating, practical suggestions, and measurable growth targets.

Key Features:
- Strength-based development strategies
- Career-aligned skill building
- Prioritized development areas
- Actionable learning recommendations
- Progress tracking frameworks
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json

from .strength_mapper import StrengthProfile, StrengthScore
from .career_matcher import CareerMatch
from ..knowledge.career_knowledge_base import CareerRole, StrengthCategory


class DevelopmentArea(Enum):
    """Categories of development areas."""
    TECHNICAL_SKILLS = "technical_skills"
    LEADERSHIP = "leadership"
    COMMUNICATION = "communication"
    ANALYTICAL_THINKING = "analytical_thinking"
    EMOTIONAL_INTELLIGENCE = "emotional_intelligence"
    STRATEGIC_PLANNING = "strategic_planning"
    PROJECT_MANAGEMENT = "project_management"
    INTERPERSONAL_SKILLS = "interpersonal_skills"
    INNOVATION = "innovation"
    EXECUTION = "execution"


class LearningMethod(Enum):
    """Learning delivery methods."""
    ONLINE_COURSE = "online_course"
    BOOK = "book"
    WORKSHOP = "workshop"
    MENTORING = "mentoring"
    PRACTICAL_PROJECT = "practical_project"
    CERTIFICATION = "certification"
    CONFERENCE = "conference"
    PEER_LEARNING = "peer_learning"


class TimeFrame(Enum):
    """Development timeframes."""
    IMMEDIATE = "immediate"      # 0-3 months
    SHORT_TERM = "short_term"    # 3-12 months
    MEDIUM_TERM = "medium_term"  # 1-2 years
    LONG_TERM = "long_term"      # 2+ years


@dataclass
class DevelopmentAction:
    """A specific development action with details."""
    action_id: str
    title: str
    chinese_title: str
    description: str
    development_area: DevelopmentArea
    learning_method: LearningMethod
    timeframe: TimeFrame
    priority: int  # 1-10, higher is more important
    estimated_hours: int
    prerequisites: List[str]
    success_metrics: List[str]
    resources: List[str]
    cost_estimate: str

    def __str__(self) -> str:
        return f"{self.chinese_title} ({self.timeframe.value}, {self.priority}分優先)"


@dataclass
class DevelopmentGoal:
    """A development goal with associated actions."""
    goal_id: str
    title: str
    chinese_title: str
    description: str
    target_completion: datetime
    actions: List[DevelopmentAction]
    success_criteria: List[str]
    milestones: List[str]
    related_strengths: List[str]

    def __str__(self) -> str:
        return f"{self.chinese_title} (目標: {self.target_completion.strftime('%Y-%m')})"


@dataclass
class DevelopmentPlan:
    """Complete personalized development plan."""
    plan_id: str
    created_date: datetime
    user_profile_summary: str
    career_focus: str
    priority_areas: List[str]
    development_goals: List[DevelopmentGoal]
    immediate_actions: List[DevelopmentAction]
    quarterly_milestones: List[str]
    annual_objectives: List[str]
    resource_requirements: Dict[str, Any]
    success_tracking: Dict[str, str]
    review_schedule: List[datetime]

    def __str__(self) -> str:
        return f"發展計劃 ({len(self.development_goals)}個目標, {len(self.immediate_actions)}個立即行動)"


class DevelopmentPlanner:
    """
    Creates personalized development plans based on strengths and career goals.

    This planner analyzes strength profiles, career matches, and user context
    to generate actionable development strategies with clear priorities and
    timelines.
    """

    def __init__(self):
        """Initialize the development planner with action templates."""
        self.development_templates = self._load_development_templates()

    def create_development_plan(
        self,
        strength_profile: StrengthProfile,
        career_matches: List[CareerMatch],
        user_context: Dict[str, Any]
    ) -> DevelopmentPlan:
        """
        Create a comprehensive development plan.

        Args:
            strength_profile: Complete strength profile from StrengthMapper
            career_matches: Career matches from CareerMatcher
            user_context: User preferences, experience, and goals

        Returns:
            Complete DevelopmentPlan with goals, actions, and timelines
        """
        plan_id = f"DEV_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        created_date = datetime.now()

        # 1. Analyze development priorities
        priority_areas = self._identify_priority_areas(strength_profile, career_matches)

        # 2. Generate development goals
        development_goals = self._generate_development_goals(
            strength_profile, career_matches, priority_areas, user_context
        )

        # 3. Create immediate actions (next 3 months)
        immediate_actions = self._generate_immediate_actions(
            strength_profile, development_goals, user_context
        )

        # 4. Set quarterly milestones
        quarterly_milestones = self._generate_quarterly_milestones(development_goals)

        # 5. Define annual objectives
        annual_objectives = self._generate_annual_objectives(development_goals, career_matches)

        # 6. Calculate resource requirements
        resource_requirements = self._calculate_resource_requirements(development_goals)

        # 7. Setup success tracking
        success_tracking = self._setup_success_tracking(development_goals)

        # 8. Create review schedule
        review_schedule = self._create_review_schedule(created_date)

        # 9. Generate profile summary
        profile_summary = self._generate_profile_summary(strength_profile, career_matches)

        # 10. Determine career focus
        career_focus = career_matches[0].chinese_name if career_matches else "多元職涯發展"

        return DevelopmentPlan(
            plan_id=plan_id,
            created_date=created_date,
            user_profile_summary=profile_summary,
            career_focus=career_focus,
            priority_areas=priority_areas,
            development_goals=development_goals,
            immediate_actions=immediate_actions,
            quarterly_milestones=quarterly_milestones,
            annual_objectives=annual_objectives,
            resource_requirements=resource_requirements,
            success_tracking=success_tracking,
            review_schedule=review_schedule
        )

    def _identify_priority_areas(
        self,
        strength_profile: StrengthProfile,
        career_matches: List[CareerMatch]
    ) -> List[str]:
        """Identify top 3-5 priority development areas."""
        priority_areas = []

        # 1. Areas based on career match development needs
        if career_matches:
            top_career = career_matches[0]
            for need in top_career.development_needs[:3]:
                if need not in priority_areas:
                    priority_areas.append(need)

        # 2. Areas based on strength domain gaps
        domain_priorities = self._analyze_domain_gaps(strength_profile)
        priority_areas.extend(domain_priorities)

        # 3. Areas based on lowest performing strengths in top themes
        for strength in strength_profile.top_5_strengths:
            if strength.confidence_level == "low":
                priority_areas.append(f"強化{strength.theme.chinese_name}優勢")

        return priority_areas[:5]  # Top 5 priorities

    def _analyze_domain_gaps(self, strength_profile: StrengthProfile) -> List[str]:
        """Analyze domain distribution to identify gaps."""
        domain_gaps = []

        domain_names = {
            StrengthCategory.EXECUTING: "執行力",
            StrengthCategory.INFLUENCING: "影響力",
            StrengthCategory.RELATIONSHIP_BUILDING: "關係建立",
            StrengthCategory.STRATEGIC_THINKING: "戰略思維"
        }

        # Find domains with low representation
        for domain, percentage in strength_profile.domain_distribution.items():
            if percentage < 15:  # Less than 15% representation
                domain_name = domain_names.get(domain, domain.value)
                domain_gaps.append(f"發展{domain_name}能力")

        return domain_gaps

    def _generate_development_goals(
        self,
        strength_profile: StrengthProfile,
        career_matches: List[CareerMatch],
        priority_areas: List[str],
        user_context: Dict[str, Any]
    ) -> List[DevelopmentGoal]:
        """Generate development goals based on priorities."""
        goals = []
        goal_counter = 1

        # Goal 1: Strengthen top strengths
        top_strength_goal = self._create_strength_enhancement_goal(
            goal_counter, strength_profile.top_5_strengths[:2]
        )
        goals.append(top_strength_goal)
        goal_counter += 1

        # Goal 2: Career-specific skill development
        if career_matches:
            career_goal = self._create_career_alignment_goal(
                goal_counter, career_matches[0], strength_profile
            )
            goals.append(career_goal)
            goal_counter += 1

        # Goal 3: Address development areas
        if priority_areas:
            development_goal = self._create_skill_development_goal(
                goal_counter, priority_areas[:2]
            )
            goals.append(development_goal)

        return goals

    def _create_strength_enhancement_goal(
        self,
        goal_id: int,
        top_strengths: List[StrengthScore]
    ) -> DevelopmentGoal:
        """Create goal focused on enhancing existing strengths."""
        strength_names = [s.theme.chinese_name for s in top_strengths]
        target_date = datetime.now() + timedelta(days=180)  # Approximately 6 months

        actions = []
        for i, strength in enumerate(top_strengths):
            action = DevelopmentAction(
                action_id=f"SA{goal_id}_{i+1}",
                title=f"Enhance {strength.theme.name} Strength",
                chinese_title=f"強化「{strength.theme.chinese_name}」優勢",
                description=f"深化{strength.theme.chinese_name}相關技能並在實際工作中應用",
                development_area=self._map_strength_to_area(strength.theme.name),
                learning_method=LearningMethod.PRACTICAL_PROJECT,
                timeframe=TimeFrame.SHORT_TERM,
                priority=9 - i,  # First strength gets priority 9, second gets 8
                estimated_hours=40,
                prerequisites=[],
                success_metrics=[f"{strength.theme.chinese_name}應用頻率提升50%"],
                resources=[f"{strength.theme.chinese_name}相關書籍和案例研究"],
                cost_estimate="低成本"
            )
            actions.append(action)

        return DevelopmentGoal(
            goal_id=f"G{goal_id}",
            title="Strengthen Core Talents",
            chinese_title=f"強化核心優勢：{', '.join(strength_names)}",
            description=f"深化您最突出的優勢特質，使其成為競爭優勢",
            target_completion=target_date,
            actions=actions,
            success_criteria=[
                "在工作中有意識地運用核心優勢",
                "獲得主管或同事對優勢表現的正面回饋",
                "找到發揮優勢的新機會或專案"
            ],
            milestones=[
                "完成優勢自我評估",
                "制定優勢應用計劃",
                "實施3個優勢應用專案"
            ],
            related_strengths=strength_names
        )

    def _create_career_alignment_goal(
        self,
        goal_id: int,
        career_match: CareerMatch,
        strength_profile: StrengthProfile
    ) -> DevelopmentGoal:
        """Create goal aligned with target career requirements."""
        target_date = datetime.now() + timedelta(days=365)  # Approximately 12 months

        actions = []
        for i, skill in enumerate(career_match.development_needs[:3]):
            action = DevelopmentAction(
                action_id=f"CA{goal_id}_{i+1}",
                title=f"Develop {skill} for {career_match.role_name}",
                chinese_title=f"發展{skill}技能",
                description=f"針對{career_match.chinese_name}職位需求，建立{skill}相關能力",
                development_area=self._map_skill_to_area(skill),
                learning_method=self._recommend_learning_method(skill),
                timeframe=TimeFrame.MEDIUM_TERM,
                priority=8 - i,
                estimated_hours=60,
                prerequisites=[],
                success_metrics=[f"取得{skill}相關認證或完成專案"],
                resources=[f"{skill}線上課程", "實務專案"],
                cost_estimate="中等成本"
            )
            actions.append(action)

        return DevelopmentGoal(
            goal_id=f"G{goal_id}",
            title=f"Prepare for {career_match.role_name}",
            chinese_title=f"為「{career_match.chinese_name}」做準備",
            description=f"發展{career_match.chinese_name}職位所需的關鍵技能",
            target_completion=target_date,
            actions=actions,
            success_criteria=[
                f"具備{career_match.chinese_name}的核心技能",
                "完成相關專案或取得認證",
                "建立該領域的專業人脈"
            ],
            milestones=[
                "完成技能需求分析",
                "開始第一個學習計劃",
                "完成50%的技能發展目標"
            ],
            related_strengths=career_match.matching_strengths
        )

    def _create_skill_development_goal(
        self,
        goal_id: int,
        priority_areas: List[str]
    ) -> DevelopmentGoal:
        """Create goal for general skill development."""
        target_date = datetime.now() + timedelta(days=270)  # Approximately 9 months

        actions = []
        for i, area in enumerate(priority_areas):
            action = DevelopmentAction(
                action_id=f"SD{goal_id}_{i+1}",
                title=f"Develop {area}",
                chinese_title=f"發展{area}",
                description=f"系統性提升{area}相關能力",
                development_area=DevelopmentArea.TECHNICAL_SKILLS,  # Default
                learning_method=LearningMethod.ONLINE_COURSE,
                timeframe=TimeFrame.MEDIUM_TERM,
                priority=7 - i,
                estimated_hours=30,
                prerequisites=[],
                success_metrics=[f"{area}能力顯著提升"],
                resources=["線上學習平台", "實務練習"],
                cost_estimate="低到中等成本"
            )
            actions.append(action)

        return DevelopmentGoal(
            goal_id=f"G{goal_id}",
            title="Skill Development",
            chinese_title=f"技能發展：{', '.join(priority_areas)}",
            description="補強重要技能領域，提升整體競爭力",
            target_completion=target_date,
            actions=actions,
            success_criteria=[
                "完成所有計劃的學習活動",
                "在實際工作中應用新技能",
                "獲得技能提升的外部確認"
            ],
            milestones=[
                "完成學習計劃制定",
                "完成第一個技能模組",
                "應用新技能於實際專案"
            ],
            related_strengths=[]
        )

    def _generate_immediate_actions(
        self,
        strength_profile: StrengthProfile,
        development_goals: List[DevelopmentGoal],
        user_context: Dict[str, Any]
    ) -> List[DevelopmentAction]:
        """Generate actions that can be started immediately (0-3 months)."""
        immediate_actions = []

        # Extract immediate/short-term actions from goals
        for goal in development_goals:
            for action in goal.actions:
                if action.timeframe in [TimeFrame.IMMEDIATE, TimeFrame.SHORT_TERM]:
                    immediate_actions.append(action)

        # Add some general immediate actions
        immediate_actions.extend([
            DevelopmentAction(
                action_id="IMM_001",
                title="Strength Assessment Review",
                chinese_title="優勢評估回顧",
                description="深入了解您的優勢評估結果，制定應用計劃",
                development_area=DevelopmentArea.EMOTIONAL_INTELLIGENCE,
                learning_method=LearningMethod.BOOK,
                timeframe=TimeFrame.IMMEDIATE,
                priority=10,
                estimated_hours=5,
                prerequisites=[],
                success_metrics=["完成優勢應用計劃"],
                resources=["優勢評估報告", "優勢相關書籍"],
                cost_estimate="免費"
            ),
            DevelopmentAction(
                action_id="IMM_002",
                title="Professional Network Expansion",
                chinese_title="擴展專業人脈",
                description="參加專業活動，建立目標領域的人脈關係",
                development_area=DevelopmentArea.INTERPERSONAL_SKILLS,
                learning_method=LearningMethod.PEER_LEARNING,
                timeframe=TimeFrame.SHORT_TERM,
                priority=8,
                estimated_hours=20,
                prerequisites=[],
                success_metrics=["建立10個新的專業聯繫"],
                resources=["LinkedIn", "專業協會", "產業活動"],
                cost_estimate="低成本"
            )
        ])

        return sorted(immediate_actions, key=lambda x: x.priority, reverse=True)[:5]

    def _generate_quarterly_milestones(self, goals: List[DevelopmentGoal]) -> List[str]:
        """Generate quarterly milestone checkpoints."""
        milestones = []

        # Q1 milestones
        milestones.extend([
            "完成優勢深度分析並制定應用策略",
            "開始第一個學習計劃",
            "建立專業發展追蹤系統"
        ])

        # Q2 milestones
        milestones.extend([
            "完成至少一個重要技能模組",
            "在工作中實際應用新學到的技能",
            "獲得進展的外部確認或回饋"
        ])

        # Q3 milestones
        milestones.extend([
            "完成50%的年度發展目標",
            "建立穩固的專業人脈網絡",
            "完成重要專案或取得認證"
        ])

        # Q4 milestones
        milestones.extend([
            "完成年度發展計劃",
            "評估職涯發展進展",
            "制定下年度發展策略"
        ])

        return milestones

    def _generate_annual_objectives(
        self,
        goals: List[DevelopmentGoal],
        career_matches: List[CareerMatch]
    ) -> List[str]:
        """Generate high-level annual objectives."""
        objectives = []

        # Career progression objective
        if career_matches:
            top_career = career_matches[0]
            objectives.append(
                f"為轉入「{top_career.chinese_name}」職位做好技能和經驗準備"
            )

        # Skill development objectives
        objectives.extend([
            "建立並強化核心優勢，成為該領域的突出人才",
            "建立強大的專業人脈網絡和個人品牌",
            "獲得可衡量的技能提升和職業發展成果"
        ])

        return objectives

    def _calculate_resource_requirements(self, goals: List[DevelopmentGoal]) -> Dict[str, Any]:
        """Calculate required resources for the development plan."""
        total_hours = 0
        cost_breakdown = {"免費": 0, "低成本": 0, "中等成本": 0, "高成本": 0}
        learning_methods = {}

        for goal in goals:
            for action in goal.actions:
                total_hours += action.estimated_hours
                if action.cost_estimate in cost_breakdown:
                    cost_breakdown[action.cost_estimate] += 1

                method = action.learning_method.value
                learning_methods[method] = learning_methods.get(method, 0) + 1

        return {
            "total_time_investment": f"{total_hours}小時 ({total_hours//40}週工作量)",
            "cost_breakdown": cost_breakdown,
            "learning_methods": learning_methods,
            "estimated_budget": "NT$10,000-50,000 (視選擇的學習資源而定)"
        }

    def _setup_success_tracking(self, goals: List[DevelopmentGoal]) -> Dict[str, str]:
        """Setup success tracking metrics and methods."""
        return {
            "progress_measurement": "每月自評 + 季度外部回饋",
            "success_indicators": "技能應用頻率、專案成果、認證取得",
            "review_frequency": "每月檢討進展，每季調整計劃",
            "accountability_system": "尋找mentor或學習夥伴進行定期檢核"
        }

    def _create_review_schedule(self, start_date: datetime) -> List[datetime]:
        """Create regular review schedule."""
        reviews = []
        current_date = start_date

        # Monthly reviews for first year
        for month in range(1, 13):
            review_date = current_date + timedelta(days=30 * month)
            reviews.append(review_date)

        return reviews[:4]  # Return first 4 reviews (quarterly)

    def _generate_profile_summary(
        self,
        strength_profile: StrengthProfile,
        career_matches: List[CareerMatch]
    ) -> str:
        """Generate summary of user profile for the plan."""
        top_strength = strength_profile.top_5_strengths[0].theme.chinese_name
        target_role = career_matches[0].chinese_name if career_matches else "多元發展"

        dominant_domain = max(
            strength_profile.domain_distribution.items(),
            key=lambda x: x[1]
        )[0].value if strength_profile.domain_distribution else "balanced"

        domain_names = {
            "executing": "執行力", "influencing": "影響力",
            "relationship_building": "關係建立", "strategic_thinking": "戰略思維"
        }

        domain_name = domain_names.get(dominant_domain, "均衡")

        return (
            f"您是以「{top_strength}」為核心優勢，{domain_name}導向的專業人才，"
            f"目標發展方向為{target_role}。本計劃將協助您發揮天然優勢，"
            f"補強關鍵技能，實現職涯目標。"
        )

    def _map_strength_to_area(self, strength_name: str) -> DevelopmentArea:
        """Map strength theme to development area."""
        mapping = {
            "analytical": DevelopmentArea.ANALYTICAL_THINKING,
            "strategic": DevelopmentArea.STRATEGIC_PLANNING,
            "communication": DevelopmentArea.COMMUNICATION,
            "command": DevelopmentArea.LEADERSHIP,
            "developer": DevelopmentArea.LEADERSHIP,
            "empathy": DevelopmentArea.EMOTIONAL_INTELLIGENCE,
            "achiever": DevelopmentArea.EXECUTION,
            "activator": DevelopmentArea.EXECUTION,
            "ideation": DevelopmentArea.INNOVATION,
            "futuristic": DevelopmentArea.INNOVATION
        }
        return mapping.get(strength_name.lower(), DevelopmentArea.TECHNICAL_SKILLS)

    def _map_skill_to_area(self, skill: str) -> DevelopmentArea:
        """Map skill name to development area."""
        skill_lower = skill.lower()
        if "management" in skill_lower or "leadership" in skill_lower:
            return DevelopmentArea.LEADERSHIP
        elif "communication" in skill_lower:
            return DevelopmentArea.COMMUNICATION
        elif "analytical" in skill_lower or "analysis" in skill_lower:
            return DevelopmentArea.ANALYTICAL_THINKING
        else:
            return DevelopmentArea.TECHNICAL_SKILLS

    def _recommend_learning_method(self, skill: str) -> LearningMethod:
        """Recommend appropriate learning method for a skill."""
        skill_lower = skill.lower()
        if "management" in skill_lower:
            return LearningMethod.WORKSHOP
        elif "technical" in skill_lower:
            return LearningMethod.ONLINE_COURSE
        elif "communication" in skill_lower:
            return LearningMethod.PRACTICAL_PROJECT
        else:
            return LearningMethod.ONLINE_COURSE

    def _load_development_templates(self) -> Dict[str, Any]:
        """Load development action templates (placeholder for future expansion)."""
        return {
            "strength_enhancement": [],
            "skill_development": [],
            "leadership_development": [],
            "career_transition": []
        }


def get_development_planner() -> DevelopmentPlanner:
    """Get a configured DevelopmentPlanner instance."""
    return DevelopmentPlanner()