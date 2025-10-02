"""
Rule Engine - Configurable Recommendation Logic

This module provides a flexible rule-based system for generating recommendations
based on strength profiles and user context. The rules are designed to be
easily configurable and maintainable, following best practices for business logic.

Design Philosophy:
Following Linus Torvalds' principle of "good taste" - simple rule evaluation
without complex inheritance, clear conditions, and predictable outcomes.

Key Features:
- Configurable rule definitions
- Context-aware rule evaluation
- Confidence scoring for rule matches
- Rule chaining and composition
- Audit trail for rule application
"""

from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

from .strength_mapper import StrengthProfile, StrengthScore, StrengthDomain


class RuleType(Enum):
    """Types of recommendation rules."""
    STRENGTH_BASED = "strength_based"
    DOMAIN_BASED = "domain_based"
    CONTEXT_BASED = "context_based"
    COMBINATION = "combination"


class RuleAction(Enum):
    """Actions that rules can recommend."""
    RECOMMEND_CAREER = "recommend_career"
    SUGGEST_DEVELOPMENT = "suggest_development"
    HIGHLIGHT_STRENGTH = "highlight_strength"
    WARN_MISMATCH = "warn_mismatch"
    PROVIDE_INSIGHT = "provide_insight"


@dataclass
class RuleCondition:
    """A condition that must be met for a rule to apply."""
    field_path: str  # e.g., "top_5_strengths.0.theme.name"
    operator: str    # "equals", "greater_than", "contains", "in_list"
    value: Any       # Expected value
    weight: float = 1.0  # Importance weight for this condition


@dataclass
class RecommendationRule:
    """A configurable recommendation rule."""
    rule_id: str
    name: str
    description: str
    rule_type: RuleType
    conditions: List[RuleCondition]
    actions: List[RuleAction]
    priority: int
    confidence_score: float
    output_template: str
    context_requirements: List[str]
    enabled: bool = True

    def __str__(self) -> str:
        return f"Rule[{self.rule_id}]: {self.name} (Priority: {self.priority})"


@dataclass
class RuleEvaluationResult:
    """Result of evaluating a rule against a profile."""
    rule: RecommendationRule
    matched: bool
    match_score: float
    matched_conditions: List[RuleCondition]
    output_message: str
    confidence: float


class RuleEngine:
    """
    Flexible rule engine for generating context-aware recommendations.

    This engine evaluates configurable rules against strength profiles
    and user context to generate personalized insights and suggestions.
    """

    def __init__(self):
        """Initialize the rule engine with default rules."""
        self.rules = self._load_default_rules()
        self._operators = self._setup_operators()

    def _setup_operators(self) -> Dict[str, Callable]:
        """Setup comparison operators for rule conditions."""
        return {
            "equals": lambda a, b: a == b,
            "not_equals": lambda a, b: a != b,
            "greater_than": lambda a, b: float(a) > float(b),
            "less_than": lambda a, b: float(a) < float(b),
            "greater_equal": lambda a, b: float(a) >= float(b),
            "less_equal": lambda a, b: float(a) <= float(b),
            "contains": lambda a, b: str(b).lower() in str(a).lower(),
            "in_list": lambda a, b: a in b,
            "not_in_list": lambda a, b: a not in b,
            "starts_with": lambda a, b: str(a).lower().startswith(str(b).lower()),
            "ends_with": lambda a, b: str(a).lower().endswith(str(b).lower())
        }

    def _load_default_rules(self) -> List[RecommendationRule]:
        """Load default recommendation rules."""
        rules = []

        # Rule 1: High Achiever + High Conscientiousness
        rules.append(RecommendationRule(
            rule_id="R001_high_achiever",
            name="高成就導向者",
            description="識別具有強烈成就動機的個人",
            rule_type=RuleType.STRENGTH_BASED,
            conditions=[
                RuleCondition("top_5_strengths.0.theme.name", "equals", "achiever", 0.8),
                RuleCondition("top_5_strengths.0.percentile_score", "greater_than", 75, 0.6)
            ],
            actions=[RuleAction.RECOMMEND_CAREER, RuleAction.PROVIDE_INSIGHT],
            priority=9,
            confidence_score=0.85,
            output_template="您具備強烈的成就動機，適合目標導向、結果為重的工作環境。建議考慮專案管理、銷售或創業相關角色。",
            context_requirements=[]
        ))

        # Rule 2: Strategic Thinking Dominant
        rules.append(RecommendationRule(
            rule_id="R002_strategic_dominant",
            name="戰略思維主導",
            description="識別戰略思維為主要優勢領域的個人",
            rule_type=RuleType.DOMAIN_BASED,
            conditions=[
                RuleCondition("domain_distribution.strategic_thinking", "greater_than", 40, 1.0)
            ],
            actions=[RuleAction.RECOMMEND_CAREER, RuleAction.SUGGEST_DEVELOPMENT],
            priority=8,
            confidence_score=0.8,
            output_template="您的戰略思維能力突出，適合需要長期規劃、分析和創新的角色，如策略顧問、研究員或產品經理。",
            context_requirements=[]
        ))

        # Rule 3: High Relationship Building + Service Context
        rules.append(RecommendationRule(
            rule_id="R003_relationship_service",
            name="關係建立 + 服務導向",
            description="關係建立能力強且有服務業背景",
            rule_type=RuleType.COMBINATION,
            conditions=[
                RuleCondition("domain_distribution.relationship_building", "greater_than", 30, 0.7),
                RuleCondition("user_context.industry_preference", "contains", "service", 0.5)
            ],
            actions=[RuleAction.RECOMMEND_CAREER, RuleAction.HIGHLIGHT_STRENGTH],
            priority=7,
            confidence_score=0.75,
            output_template="您的關係建立能力結合服務導向，非常適合客戶關係管理、人力資源或諮詢服務等職業。",
            context_requirements=["industry_preference"]
        ))

        # Rule 4: Balanced Profile Warning
        rules.append(RecommendationRule(
            rule_id="R004_balanced_profile",
            name="均衡型優勢分布",
            description="所有優勢領域相對均衡，無明顯主導",
            rule_type=RuleType.DOMAIN_BASED,
            conditions=[
                RuleCondition("domain_max_percentage", "less_than", 35, 1.0)
            ],
            actions=[RuleAction.PROVIDE_INSIGHT, RuleAction.SUGGEST_DEVELOPMENT],
            priority=6,
            confidence_score=0.7,
            output_template="您的優勢分布相對均衡，這是很好的適應性優勢。建議根據興趣和機會來專精特定領域。",
            context_requirements=[]
        ))

        # Rule 5: High Neuroticism + Support Need
        rules.append(RecommendationRule(
            rule_id="R005_high_stress_sensitivity",
            name="壓力敏感型",
            description="情緒穩定性較低，需要支持性環境",
            rule_type=RuleType.CONTEXT_BASED,
            conditions=[
                RuleCondition("user_context.big_five_scores.neuroticism", "greater_than", 70, 0.8)
            ],
            actions=[RuleAction.SUGGEST_DEVELOPMENT, RuleAction.WARN_MISMATCH],
            priority=8,
            confidence_score=0.8,
            output_template="建議選擇支持性強、壓力相對較小的工作環境，並發展壓力管理和情緒調節技能。",
            context_requirements=["big_five_scores"]
        ))

        # Rule 6: Communication + Influencing Synergy
        rules.append(RecommendationRule(
            rule_id="R006_communication_influence",
            name="溝通影響力組合",
            description="溝通能力與影響力的協同效應",
            rule_type=RuleType.STRENGTH_BASED,
            conditions=[
                RuleCondition("strength_contains", "contains", "communication", 0.6),
                RuleCondition("domain_distribution.influencing", "greater_than", 25, 0.7)
            ],
            actions=[RuleAction.RECOMMEND_CAREER, RuleAction.HIGHLIGHT_STRENGTH],
            priority=8,
            confidence_score=0.82,
            output_template="您的溝通能力與影響力相得益彰，非常適合領導、培訓、行銷或公共關係等需要說服和影響他人的角色。",
            context_requirements=[]
        ))

        # Rule 7: Learning + Development Orientation
        rules.append(RecommendationRule(
            rule_id="R007_continuous_learner",
            name="持續學習者",
            description="具備強烈學習動機的個人",
            rule_type=RuleType.STRENGTH_BASED,
            conditions=[
                RuleCondition("strength_contains", "contains", "learner", 0.8),
                RuleCondition("top_5_strengths.learner.percentile_score", "greater_than", 70, 0.6)
            ],
            actions=[RuleAction.SUGGEST_DEVELOPMENT, RuleAction.PROVIDE_INSIGHT],
            priority=7,
            confidence_score=0.78,
            output_template="您具備持續學習的動機，建議選擇技術更新快速、需要不斷學習新知的行業和角色。",
            context_requirements=[]
        ))

        return rules

    def evaluate_strength_profile(
        self,
        strength_profile: StrengthProfile,
        user_context: Dict[str, Any]
    ) -> List[RecommendationRule]:
        """
        Evaluate all rules against a strength profile and return matching rules.

        Args:
            strength_profile: Complete strength profile from StrengthMapper
            user_context: Additional user context (age, experience, preferences)

        Returns:
            List of matching RecommendationRule objects sorted by priority
        """
        matching_rules = []
        evaluation_context = self._prepare_evaluation_context(strength_profile, user_context)

        for rule in self.rules:
            if not rule.enabled:
                continue

            # Check if required context is available
            if not self._has_required_context(rule, user_context):
                continue

            # Evaluate rule conditions
            result = self._evaluate_rule(rule, evaluation_context)
            if result.matched:
                matching_rules.append(rule)

        # Sort by priority (higher priority first)
        return sorted(matching_rules, key=lambda r: r.priority, reverse=True)

    def _prepare_evaluation_context(
        self,
        strength_profile: StrengthProfile,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare combined context for rule evaluation."""
        context = {
            "top_5_strengths": strength_profile.top_5_strengths,
            "all_strengths": strength_profile.all_strengths,
            "domain_distribution": {
                domain.value: percentage
                for domain, percentage in strength_profile.domain_distribution.items()
            },
            "profile_confidence": strength_profile.profile_confidence,
            "analysis_summary": strength_profile.analysis_summary,
            "user_context": user_context
        }

        # Add computed fields for easier rule writing
        context["domain_max_percentage"] = max(
            strength_profile.domain_distribution.values()
        ) if strength_profile.domain_distribution else 0

        # Create strength name lookup for "contains" operations
        strength_names = [s.theme.name.lower() for s in strength_profile.all_strengths]
        context["strength_contains"] = " ".join(strength_names)

        # Add individual strength scores for direct access
        for strength in strength_profile.top_5_strengths[:5]:
            context[f"top_5_strengths.{strength.theme.name.lower()}"] = strength

        return context

    def _has_required_context(self, rule: RecommendationRule, user_context: Dict[str, Any]) -> bool:
        """Check if all required context fields are available."""
        for requirement in rule.context_requirements:
            if not self._get_nested_value(user_context, requirement):
                return False
        return True

    def _evaluate_rule(
        self,
        rule: RecommendationRule,
        context: Dict[str, Any]
    ) -> RuleEvaluationResult:
        """Evaluate a single rule against the context."""
        matched_conditions = []
        total_weight = 0
        matched_weight = 0

        for condition in rule.conditions:
            total_weight += condition.weight

            if self._evaluate_condition(condition, context):
                matched_conditions.append(condition)
                matched_weight += condition.weight

        # Calculate match score based on weighted conditions
        match_score = matched_weight / total_weight if total_weight > 0 else 0
        matched = match_score >= 0.6  # Require at least 60% condition match

        # Generate output message if matched
        output_message = rule.output_template if matched else ""

        # Calculate final confidence
        confidence = rule.confidence_score * match_score if matched else 0

        return RuleEvaluationResult(
            rule=rule,
            matched=matched,
            match_score=match_score,
            matched_conditions=matched_conditions,
            output_message=output_message,
            confidence=confidence
        )

    def _evaluate_condition(self, condition: RuleCondition, context: Dict[str, Any]) -> bool:
        """Evaluate a single condition against the context."""
        try:
            # Get value from context using field path
            actual_value = self._get_nested_value(context, condition.field_path)

            if actual_value is None:
                return False

            # Get operator function
            operator_func = self._operators.get(condition.operator)
            if not operator_func:
                return False

            # Evaluate condition
            return operator_func(actual_value, condition.value)

        except Exception:
            # If evaluation fails, condition is false
            return False

    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get nested value from dictionary using dot notation."""
        try:
            keys = field_path.split('.')
            value = data

            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key)
                elif isinstance(value, list) and key.isdigit():
                    idx = int(key)
                    value = value[idx] if 0 <= idx < len(value) else None
                elif hasattr(value, key):
                    value = getattr(value, key)
                else:
                    return None

            return value
        except (KeyError, IndexError, AttributeError, TypeError):
            return None

    def add_rule(self, rule: RecommendationRule):
        """Add a new rule to the engine."""
        # Check for duplicate rule_id
        if any(r.rule_id == rule.rule_id for r in self.rules):
            raise ValueError(f"Rule with ID {rule.rule_id} already exists")

        self.rules.append(rule)

    def remove_rule(self, rule_id: str):
        """Remove a rule from the engine."""
        self.rules = [r for r in self.rules if r.rule_id != rule_id]

    def enable_rule(self, rule_id: str):
        """Enable a rule by ID."""
        for rule in self.rules:
            if rule.rule_id == rule_id:
                rule.enabled = True
                break

    def disable_rule(self, rule_id: str):
        """Disable a rule by ID."""
        for rule in self.rules:
            if rule.rule_id == rule_id:
                rule.enabled = False
                break

    def get_rule_summary(self) -> Dict[str, Any]:
        """Get summary of all rules in the engine."""
        return {
            "total_rules": len(self.rules),
            "enabled_rules": len([r for r in self.rules if r.enabled]),
            "rules_by_type": {
                rule_type.value: len([r for r in self.rules if r.rule_type == rule_type])
                for rule_type in RuleType
            },
            "rules_by_priority": {
                priority: len([r for r in self.rules if r.priority == priority])
                for priority in sorted(set(r.priority for r in self.rules), reverse=True)
            }
        }


def get_rule_engine() -> RuleEngine:
    """Get a configured RuleEngine instance."""
    return RuleEngine()