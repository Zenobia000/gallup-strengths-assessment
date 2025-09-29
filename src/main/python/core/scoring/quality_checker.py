"""
Response Quality Checker for Psychometric Assessments

Implements comprehensive quality validation following psychometric standards
to detect invalid response patterns and ensure scoring reliability.

Key Quality Checks:
- Completion time validation
- Response pattern analysis
- Straight-line responding detection
- Extreme response bias identification
- Response variance assessment

Author: TaskMaster Week 2 Quality Implementation
Version: 1.0.0
"""

import statistics
from typing import List, Set, Dict
from enum import Enum

from models.schemas import ItemResponse


class QualityFlags(str, Enum):
    """Quality flag enumeration for consistent flagging."""
    COMPLETION_TOO_FAST = "COMPLETION_TOO_FAST"
    COMPLETION_TOO_SLOW = "COMPLETION_TOO_SLOW"
    ALL_SAME_RESPONSE = "ALL_SAME_RESPONSE"
    EXTREME_RESPONSE_BIAS = "EXTREME_RESPONSE_BIAS"
    STRAIGHT_LINE_RESPONDING = "STRAIGHT_LINE_RESPONDING"
    LOW_RESPONSE_VARIANCE = "LOW_RESPONSE_VARIANCE"
    HIGH_ACQUIESCENCE_BIAS = "HIGH_ACQUIESCENCE_BIAS"
    SUSPICIOUS_PATTERN = "SUSPICIOUS_PATTERN"


class ResponseQualityChecker:
    """
    Validates response quality for psychometric standards.

    Implements multiple quality checks to flag potentially invalid responses
    that could compromise scoring reliability and validity.

    Based on established psychometric guidelines and research on
    response quality indicators.
    """

    # Quality thresholds based on research
    MIN_COMPLETION_TIME = 60   # 1 minute minimum
    MAX_COMPLETION_TIME = 1800  # 30 minutes maximum
    MAX_EXTREME_PERCENTAGE = 0.75  # 75% of responses at extremes
    MAX_CONSECUTIVE_SAME = 5  # 5+ consecutive same responses
    MIN_RESPONSE_VARIANCE = 0.5  # Minimum standard deviation
    MAX_ACQUIESCENCE_THRESHOLD = 0.8  # 80% agreement responses

    def __init__(self):
        """Initialize quality checker with default thresholds."""
        pass

    def assess_quality(
        self,
        responses: List[ItemResponse],
        completion_time: int
    ) -> List[str]:
        """
        Comprehensive quality assessment for assessment responses.

        Args:
            responses: List of item responses to assess
            completion_time: Time taken to complete in seconds

        Returns:
            List[str]: Quality flags (empty list indicates good quality)
        """
        flags = []

        # Time-based quality checks
        flags.extend(self._check_completion_time(completion_time))

        # Response pattern quality checks
        response_values = [r.response for r in responses]
        flags.extend(self._check_response_patterns(response_values))

        # Psychometric quality checks
        flags.extend(self._check_psychometric_quality(responses))

        return flags

    def _check_completion_time(self, completion_time: int) -> List[str]:
        """
        Check if completion time is within reasonable bounds.

        Args:
            completion_time: Completion time in seconds

        Returns:
            List of quality flags related to completion time
        """
        flags = []

        if completion_time < self.MIN_COMPLETION_TIME:
            flags.append(QualityFlags.COMPLETION_TOO_FAST.value)

        if completion_time > self.MAX_COMPLETION_TIME:
            flags.append(QualityFlags.COMPLETION_TOO_SLOW.value)

        return flags

    def _check_response_patterns(self, response_values: List[int]) -> List[str]:
        """
        Check for problematic response patterns.

        Args:
            response_values: List of response values (1-7)

        Returns:
            List of quality flags related to response patterns
        """
        flags = []

        # Check for all same responses
        if len(set(response_values)) == 1:
            flags.append(QualityFlags.ALL_SAME_RESPONSE.value)

        # Check for extreme response bias
        extreme_count = response_values.count(1) + response_values.count(7)
        extreme_percentage = extreme_count / len(response_values)
        if extreme_percentage > self.MAX_EXTREME_PERCENTAGE:
            flags.append(QualityFlags.EXTREME_RESPONSE_BIAS.value)

        # Check for straight-line responding
        if self._has_straight_line_pattern(response_values):
            flags.append(QualityFlags.STRAIGHT_LINE_RESPONDING.value)

        # Check response variance
        if len(set(response_values)) > 1:  # Only if not all same
            variance = statistics.stdev(response_values)
            if variance < self.MIN_RESPONSE_VARIANCE:
                flags.append(QualityFlags.LOW_RESPONSE_VARIANCE.value)

        # Check for acquiescence bias (tendency to agree)
        agreement_responses = sum(1 for r in response_values if r >= 5)  # 5, 6, 7
        agreement_rate = agreement_responses / len(response_values)
        if agreement_rate > self.MAX_ACQUIESCENCE_THRESHOLD:
            flags.append(QualityFlags.HIGH_ACQUIESCENCE_BIAS.value)

        return flags

    def _check_psychometric_quality(self, responses: List[ItemResponse]) -> List[str]:
        """
        Check psychometric-specific quality indicators.

        Args:
            responses: Item responses with item IDs

        Returns:
            List of quality flags related to psychometric quality
        """
        flags = []

        # Check for suspicious alternating patterns
        response_values = [r.response for r in responses]
        if self._has_alternating_pattern(response_values):
            flags.append(QualityFlags.SUSPICIOUS_PATTERN.value)

        # Additional psychometric checks can be added here
        # e.g., checking for impossible personality combinations

        return flags

    def _has_straight_line_pattern(self, responses: List[int]) -> bool:
        """
        Check for consecutive identical responses (straight-lining).

        Args:
            responses: List of response values

        Returns:
            bool: True if straight-line pattern detected
        """
        consecutive_count = 1
        max_consecutive = 1

        for i in range(1, len(responses)):
            if responses[i] == responses[i-1]:
                consecutive_count += 1
                max_consecutive = max(max_consecutive, consecutive_count)
            else:
                consecutive_count = 1

        return max_consecutive >= self.MAX_CONSECUTIVE_SAME

    def _has_alternating_pattern(self, responses: List[int]) -> bool:
        """
        Check for suspicious alternating response patterns.

        Args:
            responses: List of response values

        Returns:
            bool: True if alternating pattern detected
        """
        if len(responses) < 6:
            return False

        # Check for simple alternating patterns (e.g., 1,7,1,7,1,7...)
        alternating_pairs = 0
        for i in range(1, len(responses)):
            if abs(responses[i] - responses[i-1]) >= 4:  # Large jumps
                alternating_pairs += 1

        # If more than 50% of transitions are large jumps, flag as suspicious
        alternating_rate = alternating_pairs / (len(responses) - 1)
        return alternating_rate > 0.5

    def calculate_quality_score(self, flags: List[str]) -> float:
        """
        Calculate overall quality score based on flags.

        Args:
            flags: List of quality flags

        Returns:
            float: Quality score between 0.0 (poor) and 1.0 (excellent)
        """
        if not flags:
            return 1.0  # Perfect quality

        # Weight different flags by severity
        flag_weights = {
            QualityFlags.ALL_SAME_RESPONSE.value: 0.8,  # Very severe
            QualityFlags.COMPLETION_TOO_FAST.value: 0.6,  # Severe
            QualityFlags.STRAIGHT_LINE_RESPONDING.value: 0.6,  # Severe
            QualityFlags.EXTREME_RESPONSE_BIAS.value: 0.4,  # Moderate
            QualityFlags.LOW_RESPONSE_VARIANCE.value: 0.3,  # Moderate
            QualityFlags.HIGH_ACQUIESCENCE_BIAS.value: 0.2,  # Mild
            QualityFlags.COMPLETION_TOO_SLOW.value: 0.1,  # Mild
            QualityFlags.SUSPICIOUS_PATTERN.value: 0.3,  # Moderate
        }

        # Calculate weighted penalty
        total_penalty = sum(flag_weights.get(flag, 0.2) for flag in flags)

        # Convert to quality score (1.0 - penalty, minimum 0.0)
        quality_score = max(0.0, 1.0 - total_penalty)

        return round(quality_score, 3)

    def get_quality_interpretation(self, flags: List[str]) -> Dict[str, str]:
        """
        Get human-readable interpretation of quality flags.

        Args:
            flags: List of quality flags

        Returns:
            Dict with interpretation and recommendations
        """
        if not flags:
            return {
                "overall": "Excellent response quality",
                "interpretation": "Responses show good engagement and reliability",
                "recommendation": "Scores can be interpreted with high confidence"
            }

        # Categorize flags by severity
        severe_flags = {
            QualityFlags.ALL_SAME_RESPONSE.value,
            QualityFlags.COMPLETION_TOO_FAST.value,
            QualityFlags.STRAIGHT_LINE_RESPONDING.value
        }

        has_severe = any(flag in severe_flags for flag in flags)

        if has_severe:
            return {
                "overall": "Poor response quality",
                "interpretation": "Responses show signs of non-engagement or invalid responding",
                "recommendation": "Scores should be interpreted with caution or retesting recommended"
            }
        else:
            return {
                "overall": "Acceptable response quality",
                "interpretation": "Some quality concerns but generally reliable responses",
                "recommendation": "Scores can be interpreted with moderate confidence"
            }