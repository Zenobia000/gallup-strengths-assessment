#!/usr/bin/env python3
"""
Response Quality Checker - Gallup Strengths Assessment

Validates response quality and detects potential issues with user input.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import statistics


class QualityFlags(Enum):
    """Quality flags for response validation"""
    NONE = "none"
    STRAIGHT_LINE = "straight_line"
    EXTREME_BIAS = "extreme_bias"
    INSUFFICIENT_VARIANCE = "insufficient_variance"
    RAPID_COMPLETION = "rapid_completion"
    INVALID_PATTERN = "invalid_pattern"


@dataclass
class QualityCheckResult:
    """Result of quality check analysis"""
    is_valid: bool
    flags: List[QualityFlags]
    confidence_score: float
    recommendations: List[str]
    details: Dict[str, Any]


class ResponseQualityChecker:
    """
    Validates response quality for assessment submissions.

    Checks for common response patterns that might indicate
    invalid or low-quality responses.
    """

    def __init__(self,
                 min_variance_threshold: float = 0.5,
                 max_straight_line_ratio: float = 0.8,
                 extreme_bias_threshold: float = 0.9):
        self.min_variance_threshold = min_variance_threshold
        self.max_straight_line_ratio = max_straight_line_ratio
        self.extreme_bias_threshold = extreme_bias_threshold

    def check_quality(self, responses: List[int],
                     completion_time_seconds: Optional[int] = None) -> QualityCheckResult:
        """
        Perform comprehensive quality check on responses.

        Args:
            responses: List of response scores (1-5)
            completion_time_seconds: Time taken to complete (optional)

        Returns:
            QualityCheckResult with validation details
        """
        flags = []
        details = {}

        # Check for straight-line responses
        if self._is_straight_line_response(responses):
            flags.append(QualityFlags.STRAIGHT_LINE)

        # Check for extreme bias
        bias_flag = self._check_extreme_bias(responses)
        if bias_flag:
            flags.append(bias_flag)

        # Check response variance
        if self._has_insufficient_variance(responses):
            flags.append(QualityFlags.INSUFFICIENT_VARIANCE)

        # Check completion time if provided
        if completion_time_seconds and self._is_rapid_completion(completion_time_seconds):
            flags.append(QualityFlags.RAPID_COMPLETION)

        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(responses, flags)

        # Generate recommendations
        recommendations = self._generate_recommendations(flags)

        # Compile details
        details = {
            "response_count": len(responses),
            "mean_response": statistics.mean(responses),
            "variance": statistics.variance(responses) if len(responses) > 1 else 0,
            "completion_time": completion_time_seconds,
            "flag_count": len(flags)
        }

        is_valid = len(flags) == 0 or confidence_score > 0.7

        return QualityCheckResult(
            is_valid=is_valid,
            flags=flags,
            confidence_score=confidence_score,
            recommendations=recommendations,
            details=details
        )

    def _is_straight_line_response(self, responses: List[int]) -> bool:
        """Check if responses show straight-line pattern"""
        if len(responses) < 3:
            return False

        unique_responses = len(set(responses))
        straight_line_ratio = 1 - (unique_responses - 1) / (len(responses) - 1)

        return straight_line_ratio > self.max_straight_line_ratio

    def _check_extreme_bias(self, responses: List[int]) -> Optional[QualityFlags]:
        """Check for extreme response bias (all high or all low)"""
        if not responses:
            return None

        high_responses = sum(1 for r in responses if r >= 4)
        low_responses = sum(1 for r in responses if r <= 2)

        total_responses = len(responses)
        high_ratio = high_responses / total_responses
        low_ratio = low_responses / total_responses

        if high_ratio > self.extreme_bias_threshold or low_ratio > self.extreme_bias_threshold:
            return QualityFlags.EXTREME_BIAS

        return None

    def _has_insufficient_variance(self, responses: List[int]) -> bool:
        """Check if responses have insufficient variance"""
        if len(responses) < 2:
            return False

        variance = statistics.variance(responses)
        return variance < self.min_variance_threshold

    def _is_rapid_completion(self, completion_time: int) -> bool:
        """Check if completion time is suspiciously fast"""
        # Assuming minimum reasonable time is 30 seconds for 20 questions
        min_reasonable_time = 30
        return completion_time < min_reasonable_time

    def _calculate_confidence_score(self, responses: List[int], flags: List[QualityFlags]) -> float:
        """Calculate confidence score for response quality"""
        if not responses:
            return 0.0

        base_score = 1.0

        # Deduct for each quality flag
        flag_penalties = {
            QualityFlags.STRAIGHT_LINE: 0.4,
            QualityFlags.EXTREME_BIAS: 0.3,
            QualityFlags.INSUFFICIENT_VARIANCE: 0.2,
            QualityFlags.RAPID_COMPLETION: 0.2,
            QualityFlags.INVALID_PATTERN: 0.5
        }

        for flag in flags:
            penalty = flag_penalties.get(flag, 0.1)
            base_score -= penalty

        return max(0.0, min(1.0, base_score))

    def _generate_recommendations(self, flags: List[QualityFlags]) -> List[str]:
        """Generate recommendations based on quality flags"""
        recommendations = []

        flag_messages = {
            QualityFlags.STRAIGHT_LINE: "Consider retaking the assessment with more varied responses",
            QualityFlags.EXTREME_BIAS: "Try to use the full range of the response scale",
            QualityFlags.INSUFFICIENT_VARIANCE: "Provide more diverse responses across questions",
            QualityFlags.RAPID_COMPLETION: "Take more time to carefully consider each question",
            QualityFlags.INVALID_PATTERN: "Please review your responses and retake if necessary"
        }

        for flag in flags:
            if flag in flag_messages:
                recommendations.append(flag_messages[flag])

        if not recommendations:
            recommendations.append("Response quality appears good")

        return recommendations