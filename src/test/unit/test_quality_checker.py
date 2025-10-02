"""
Unit Tests for Response Quality Checker

Tests quality validation functionality including:
- Pattern detection (straight-line, extreme bias)
- Completion time validation
- Quality flag generation
- Quality score calculation

Author: TaskMaster Week 2 Testing Implementation
Version: 1.0.0
"""

import pytest
import sys
from pathlib import Path

# Add the main Python source directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "main" / "python"))

from models.schemas import ItemResponse
from core.scoring.quality_checker import ResponseQualityChecker, QualityFlags


class TestResponseQualityChecker:
    """Test suite for response quality checking functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.checker = ResponseQualityChecker()

        # Create good quality responses
        self.good_responses = [
            ItemResponse(item_id=f"ipip_{i:03d}", response=(i % 6) + 1)
            for i in range(1, 21)
        ]

    def test_quality_checker_initialization(self):
        """Test quality checker initialization."""
        checker = ResponseQualityChecker()
        assert checker.MIN_COMPLETION_TIME == 60
        assert checker.MAX_COMPLETION_TIME == 1800
        assert checker.MAX_EXTREME_PERCENTAGE == 0.75

    def test_assess_quality_good_responses(self):
        """Test quality assessment with good responses."""
        completion_time = 300  # 5 minutes
        flags = self.checker.assess_quality(self.good_responses, completion_time)

        # Good responses should have no quality flags
        assert isinstance(flags, list)
        assert len(flags) == 0

    def test_completion_time_too_fast(self):
        """Test detection of completion time too fast."""
        completion_time = 30  # 30 seconds - too fast
        flags = self.checker.assess_quality(self.good_responses, completion_time)

        assert QualityFlags.COMPLETION_TOO_FAST.value in flags

    def test_completion_time_too_slow(self):
        """Test detection of completion time too slow."""
        completion_time = 2000  # Over 30 minutes - too slow
        flags = self.checker.assess_quality(self.good_responses, completion_time)

        assert QualityFlags.COMPLETION_TOO_SLOW.value in flags

    def test_all_same_response_detection(self):
        """Test detection of all same responses."""
        same_responses = [
            ItemResponse(item_id=f"ipip_{i:03d}", response=4)
            for i in range(1, 21)
        ]

        flags = self.checker.assess_quality(same_responses, 300)
        assert QualityFlags.ALL_SAME_RESPONSE.value in flags

    def test_extreme_response_bias_detection(self):
        """Test detection of extreme response bias."""
        # Create responses with 80% extremes (1s and 7s)
        extreme_responses = []
        for i in range(1, 21):
            if i <= 16:  # 80% of 20 = 16
                response = 1 if i % 2 == 0 else 7
            else:
                response = 4  # Neutral for remaining
            extreme_responses.append(ItemResponse(item_id=f"ipip_{i:03d}", response=response))

        flags = self.checker.assess_quality(extreme_responses, 300)
        assert QualityFlags.EXTREME_RESPONSE_BIAS.value in flags

    def test_straight_line_responding_detection(self):
        """Test detection of straight-line responding."""
        # Create responses with 6 consecutive same responses
        straight_line_responses = []
        for i in range(1, 21):
            if 1 <= i <= 6:
                response = 5  # 6 consecutive same responses
            else:
                response = (i % 6) + 1  # Varied responses for the rest
            straight_line_responses.append(ItemResponse(item_id=f"ipip_{i:03d}", response=response))

        flags = self.checker.assess_quality(straight_line_responses, 300)
        assert QualityFlags.STRAIGHT_LINE_RESPONDING.value in flags

    def test_low_response_variance_detection(self):
        """Test detection of low response variance."""
        # Create responses with very low variance (mostly 4s with one 5)
        low_variance_responses = []
        for i in range(1, 21):
            response = 5 if i == 1 else 4  # Very low variance
            low_variance_responses.append(ItemResponse(item_id=f"ipip_{i:03d}", response=response))

        flags = self.checker.assess_quality(low_variance_responses, 300)
        assert QualityFlags.LOW_RESPONSE_VARIANCE.value in flags

    def test_high_acquiescence_bias_detection(self):
        """Test detection of high acquiescence bias (agreement tendency)."""
        # Create responses with 85% agreement (5, 6, 7)
        acquiescence_responses = []
        for i in range(1, 21):
            if i <= 17:  # 85% of 20 = 17
                response = 5 + (i % 3)  # 5, 6, or 7
            else:
                response = 2  # Disagreement for remaining
            acquiescence_responses.append(ItemResponse(item_id=f"ipip_{i:03d}", response=response))

        flags = self.checker.assess_quality(acquiescence_responses, 300)
        assert QualityFlags.HIGH_ACQUIESCENCE_BIAS.value in flags

    def test_alternating_pattern_detection(self):
        """Test detection of suspicious alternating patterns."""
        # Create alternating extreme responses (1, 7, 1, 7, ...)
        alternating_responses = []
        for i in range(1, 21):
            response = 1 if i % 2 == 1 else 7
            alternating_responses.append(ItemResponse(item_id=f"ipip_{i:03d}", response=response))

        flags = self.checker.assess_quality(alternating_responses, 300)
        assert QualityFlags.SUSPICIOUS_PATTERN.value in flags

    def test_straight_line_pattern_detection_edge_cases(self):
        """Test edge cases for straight-line pattern detection."""
        # Test with exactly 5 consecutive (should trigger)
        exactly_five_responses = [
            ItemResponse(item_id=f"ipip_{i:03d}", response=3 if 1 <= i <= 5 else (i % 6) + 1)
            for i in range(1, 21)
        ]

        flags = self.checker.assess_quality(exactly_five_responses, 300)
        assert QualityFlags.STRAIGHT_LINE_RESPONDING.value in flags

        # Test with 4 consecutive (should not trigger)
        four_consecutive_responses = [
            ItemResponse(item_id=f"ipip_{i:03d}", response=3 if 1 <= i <= 4 else (i % 6) + 1)
            for i in range(1, 21)
        ]

        flags = self.checker.assess_quality(four_consecutive_responses, 300)
        assert QualityFlags.STRAIGHT_LINE_RESPONDING.value not in flags

    def test_has_straight_line_pattern_method(self):
        """Test the internal straight-line pattern detection method."""
        # Test with straight-line pattern
        straight_line_values = [3, 3, 3, 3, 3, 1, 2, 4, 5, 6] + [2] * 10
        assert self.checker._has_straight_line_pattern(straight_line_values) is True

        # Test without straight-line pattern
        varied_values = list(range(1, 8)) * 3  # Varied pattern
        assert self.checker._has_straight_line_pattern(varied_values[:20]) is False

    def test_has_alternating_pattern_method(self):
        """Test the internal alternating pattern detection method."""
        # Test with strong alternating pattern
        alternating_values = [1, 7] * 10  # Strong alternating
        assert self.checker._has_alternating_pattern(alternating_values) is True

        # Test with normal variance
        normal_values = [3, 4, 5, 4, 3, 5, 4, 3, 4, 5] * 2
        assert self.checker._has_alternating_pattern(normal_values) is False

        # Test with insufficient data
        short_values = [1, 7, 1, 7, 1]
        assert self.checker._has_alternating_pattern(short_values) is False

    def test_calculate_quality_score(self):
        """Test quality score calculation."""
        # Test with no flags (perfect quality)
        no_flags = []
        score = self.checker.calculate_quality_score(no_flags)
        assert score == 1.0

        # Test with mild flags
        mild_flags = [QualityFlags.COMPLETION_TOO_SLOW.value]
        score = self.checker.calculate_quality_score(mild_flags)
        assert 0.8 <= score < 1.0

        # Test with severe flags
        severe_flags = [QualityFlags.ALL_SAME_RESPONSE.value, QualityFlags.COMPLETION_TOO_FAST.value]
        score = self.checker.calculate_quality_score(severe_flags)
        assert score < 0.5

        # Test quality score bounds
        all_flags = list(QualityFlags)
        score = self.checker.calculate_quality_score([f.value for f in all_flags])
        assert 0.0 <= score <= 1.0

    def test_get_quality_interpretation(self):
        """Test quality interpretation generation."""
        # Test excellent quality
        no_flags = []
        interpretation = self.checker.get_quality_interpretation(no_flags)
        assert interpretation["overall"] == "Excellent response quality"
        assert "high confidence" in interpretation["recommendation"]

        # Test poor quality
        severe_flags = [QualityFlags.ALL_SAME_RESPONSE.value]
        interpretation = self.checker.get_quality_interpretation(severe_flags)
        assert interpretation["overall"] == "Poor response quality"
        assert "caution" in interpretation["recommendation"]

        # Test acceptable quality
        moderate_flags = [QualityFlags.HIGH_ACQUIESCENCE_BIAS.value]
        interpretation = self.checker.get_quality_interpretation(moderate_flags)
        assert interpretation["overall"] == "Acceptable response quality"
        assert "moderate confidence" in interpretation["recommendation"]

    def test_quality_thresholds_consistency(self):
        """Test that quality thresholds are consistent and reasonable."""
        # Test completion time thresholds
        assert self.checker.MIN_COMPLETION_TIME < self.checker.MAX_COMPLETION_TIME
        assert self.checker.MIN_COMPLETION_TIME > 0

        # Test percentage thresholds
        assert 0 < self.checker.MAX_EXTREME_PERCENTAGE < 1
        assert 0 < self.checker.MAX_ACQUIESCENCE_THRESHOLD < 1

        # Test consecutive response threshold
        assert self.checker.MAX_CONSECUTIVE_SAME >= 5

        # Test variance threshold
        assert self.checker.MIN_RESPONSE_VARIANCE > 0

    def test_comprehensive_quality_assessment(self):
        """Test comprehensive quality assessment with multiple issues."""
        # Create responses with multiple quality issues
        problematic_responses = [
            ItemResponse(item_id=f"ipip_{i:03d}", response=1)  # All same + extreme bias
            for i in range(1, 21)
        ]

        completion_time = 45  # Too fast

        flags = self.checker.assess_quality(problematic_responses, completion_time)

        # Should detect multiple issues
        expected_flags = [
            QualityFlags.COMPLETION_TOO_FAST.value,
            QualityFlags.ALL_SAME_RESPONSE.value,
            QualityFlags.EXTREME_RESPONSE_BIAS.value,
            QualityFlags.LOW_RESPONSE_VARIANCE.value
        ]

        for flag in expected_flags:
            assert flag in flags

    def test_edge_case_empty_responses(self):
        """Test handling of edge cases."""
        # Test with minimum valid completion time
        flags = self.checker.assess_quality(self.good_responses, 60)
        assert QualityFlags.COMPLETION_TOO_FAST.value not in flags

        # Test with maximum valid completion time
        flags = self.checker.assess_quality(self.good_responses, 1800)
        assert QualityFlags.COMPLETION_TOO_SLOW.value not in flags

    def test_response_variance_calculation_edge_cases(self):
        """Test response variance calculation with edge cases."""
        # Test with perfect variance (all different responses in range)
        perfect_variance_responses = [
            ItemResponse(item_id=f"ipip_{i:03d}", response=min(7, (i % 7) + 1))
            for i in range(1, 21)
        ]

        flags = self.checker.assess_quality(perfect_variance_responses, 300)
        assert QualityFlags.LOW_RESPONSE_VARIANCE.value not in flags

    def test_quality_flags_enum_values(self):
        """Test that quality flags enum has expected values."""
        expected_flags = {
            "COMPLETION_TOO_FAST",
            "COMPLETION_TOO_SLOW",
            "ALL_SAME_RESPONSE",
            "EXTREME_RESPONSE_BIAS",
            "STRAIGHT_LINE_RESPONDING",
            "LOW_RESPONSE_VARIANCE",
            "HIGH_ACQUIESCENCE_BIAS",
            "SUSPICIOUS_PATTERN"
        }

        actual_flags = {flag.name for flag in QualityFlags}
        assert actual_flags == expected_flags