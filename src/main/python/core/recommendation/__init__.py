"""
Recommendation System - Gallup Strengths Assessment

This module provides comprehensive recommendation services that transform
Big Five personality assessments into actionable career and development insights
following Gallup's 34 CliftonStrengths themes.

Key Components:
- Strength Theme Mapping: Big Five → Gallup 34 Strengths
- Career Recommendation Engine: Role-based matching
- Development Suggestion Generator: Personalized growth plans
- Rule-based Configuration: Flexible, maintainable recommendation logic

Design Philosophy:
Following Linus Torvalds' principles of "good taste" and simplicity
while providing scientifically-backed, actionable recommendations.
"""

from .strength_mapper import StrengthMapper, StrengthProfile
from .recommendation_engine import RecommendationEngine, JobRecommendation
from .rule_engine import RuleEngine, RecommendationRule
from .career_matcher import CareerMatcher, CareerMatch
from .development_planner import DevelopmentPlanner, DevelopmentPlan

__all__ = [
    'StrengthMapper',
    'StrengthProfile',
    'RecommendationEngine',
    'JobRecommendation',
    'RuleEngine',
    'RecommendationRule',
    'CareerMatcher',
    'CareerMatch',
    'DevelopmentPlanner',
    'DevelopmentPlan'
]

__version__ = '1.0.0'