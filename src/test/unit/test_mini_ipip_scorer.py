"""
Unit Tests for Mini-IPIP Scorer

Tests the core scoring functionality including:
- Raw score calculation with reverse scoring
- Score standardization and percentile calculation
- Quality assessment and confidence scoring
- Error handling and edge cases

Author: TaskMaster Week 2 Testing Implementation
Version: 1.0.0
"""

import pytest
from datetime import datetime
from models.schemas import ItemResponse, BigFiveScores
from core.scoring.mini_ipip_scorer import MiniIPIPScorer, ScoringResult, InvalidResponseError


class TestMiniIPIPScorer:
    """Test suite for Mini-IPIP scoring functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.scorer = MiniIPIPScorer()

        # Create test responses with known pattern
        self.test_responses = [
            # Extraversion items (high extraversion pattern)
            ItemResponse(item_id="ipip_001", response=7),  # Life of party (positive)
            ItemResponse(item_id="ipip_002", response=1),  # Don't talk much (reverse -> 7)
            ItemResponse(item_id="ipip_003", response=6),  # Comfortable with people (positive)
            ItemResponse(item_id="ipip_004", response=2),  # Keep in background (reverse -> 6)

            # Agreeableness items (medium agreeableness)
            ItemResponse(item_id="ipip_005", response=5),  # Feel others' emotions (positive)
            ItemResponse(item_id="ipip_006", response=3),  # Not interested in others (reverse -> 5)
            ItemResponse(item_id="ipip_007", response=4),  # Feel others' emotions (positive)
            ItemResponse(item_id="ipip_008", response=4),  # Not interested in problems (reverse -> 4)

            # Conscientiousness items (high conscientiousness)
            ItemResponse(item_id="ipip_009", response=7),  # Always prepared (positive)
            ItemResponse(item_id="ipip_010", response=1),  # Leave belongings around (reverse -> 7)
            ItemResponse(item_id="ipip_011", response=6),  # Pay attention to details (positive)
            ItemResponse(item_id="ipip_012", response=2),  # Make a mess (reverse -> 6)

            # Neuroticism items (low neuroticism - stable)
            ItemResponse(item_id="ipip_013", response=2),  # Get stressed easily (positive)
            ItemResponse(item_id="ipip_014", response=6),  # Relaxed most of time (reverse -> 2)
            ItemResponse(item_id="ipip_015", response=3),  # Worry about things (positive)
            ItemResponse(item_id="ipip_016", response=7),  # Seldom feel blue (reverse -> 1)

            # Openness items (medium openness)
            ItemResponse(item_id="ipip_017", response=5),  # Rich vocabulary (positive)
            ItemResponse(item_id="ipip_018", response=3),  # Difficulty with abstract (reverse -> 5)
            ItemResponse(item_id="ipip_019", response=4),  # Excellent ideas (positive)
            ItemResponse(item_id="ipip_020", response=4),  # No good imagination (reverse -> 4)
        ]

    def test_scorer_initialization(self):
        """Test scorer initialization with default norms."""
        scorer = MiniIPIPScorer()
        assert scorer.norms is not None
        assert "extraversion" in scorer.norms
        assert scorer.ALGORITHM_VERSION == "v1.0.0"

    def test_scorer_initialization_with_custom_norms(self):
        """Test scorer initialization with custom normative data."""
        custom_norms = {
            "extraversion": {"mean": 20.0, "std": 5.0},
            "agreeableness": {"mean": 18.0, "std": 4.5}
        }
        scorer = MiniIPIPScorer(custom_norms)
        assert scorer.norms["extraversion"]["mean"] == 20.0
        assert scorer.norms["agreeableness"]["std"] == 4.5

    def test_validate_responses_valid(self):
        """Test response validation with valid responses."""
        # Should not raise any exception
        self.scorer._validate_responses(self.test_responses)

    def test_validate_responses_insufficient_count(self):
        """Test response validation with insufficient response count."""
        incomplete_responses = self.test_responses[:15]  # Only 15 responses

        with pytest.raises(InvalidResponseError) as exc_info:
            self.scorer._validate_responses(incomplete_responses)

        assert "Expected 20 responses" in str(exc_info.value)
        assert exc_info.value.code == "INVALID_RESPONSE_COUNT"

    def test_validate_responses_missing_items(self):
        """Test response validation with missing specific items."""
        # Remove one specific item
        incomplete_responses = [r for r in self.test_responses if r.item_id != "ipip_010"]

        with pytest.raises(InvalidResponseError) as exc_info:
            self.scorer._validate_responses(incomplete_responses)

        assert "Missing responses for items" in str(exc_info.value)

    def test_validate_responses_duplicate_items(self):
        """Test response validation with duplicate items."""
        duplicate_responses = self.test_responses + [
            ItemResponse(item_id="ipip_001", response=4)  # Duplicate
        ]

        with pytest.raises(InvalidResponseError) as exc_info:
            self.scorer._validate_responses(duplicate_responses[:20])  # Keep 20 total

        assert "Duplicate item responses" in str(exc_info.value)

    def test_validate_responses_out_of_range(self):
        """Test response validation with out of range values."""
        invalid_responses = self.test_responses.copy()
        invalid_responses[0] = ItemResponse(item_id="ipip_001", response=8)  # Out of range

        with pytest.raises(InvalidResponseError) as exc_info:
            self.scorer._validate_responses(invalid_responses)

        assert "out of range" in str(exc_info.value)

    def test_calculate_raw_scores(self):
        """Test raw score calculation with reverse scoring."""
        raw_scores = self.scorer._calculate_raw_scores(self.test_responses)

        # Check that we get BigFiveScores object
        assert isinstance(raw_scores, BigFiveScores)

        # Expected raw scores based on test pattern:
        # Extraversion: 7 + (8-1) + 6 + (8-2) = 7 + 7 + 6 + 6 = 26
        assert raw_scores.extraversion == 26

        # Conscientiousness: 7 + (8-1) + 6 + (8-2) = 7 + 7 + 6 + 6 = 26
        assert raw_scores.conscientiousness == 26

        # Agreeableness: 5 + (8-3) + 4 + (8-4) = 5 + 5 + 4 + 4 = 18
        assert raw_scores.agreeableness == 18

        # All scores should be within valid range (4-28 for 7-point scale)
        for score in [raw_scores.extraversion, raw_scores.agreeableness,
                     raw_scores.conscientiousness, raw_scores.neuroticism,
                     raw_scores.openness]:
            assert 4 <= score <= 28

    def test_reverse_scoring_application(self):
        """Test that reverse scoring is applied correctly."""
        # Create responses with extreme values to test reverse scoring
        extreme_responses = []
        for i, item_id in enumerate(self.scorer.ITEM_FACTOR_MAPPING.keys()):
            response_value = 1 if i % 2 == 0 else 7  # Alternate between 1 and 7
            extreme_responses.append(ItemResponse(item_id=item_id, response=response_value))

        raw_scores = self.scorer._calculate_raw_scores(extreme_responses)

        # Verify scores are calculated (specific values depend on the alternating pattern)
        assert isinstance(raw_scores, BigFiveScores)
        assert 4 <= raw_scores.extraversion <= 28

    def test_standardize_scores(self):
        """Test score standardization and percentile calculation."""
        # Use known raw scores
        raw_scores = BigFiveScores(
            extraversion=20,  # Above mean (16.0)
            agreeableness=15,  # Below mean (17.5)
            conscientiousness=18,  # Near mean (18.2)
            neuroticism=12,   # Below mean (15.3)
            openness=16       # Near mean (16.8)
        )

        standardized, percentiles = self.scorer._standardize_scores(raw_scores)

        # Check standardized scores are BigFiveScores
        assert isinstance(standardized, BigFiveScores)

        # Check all scores are in 0-100 range
        for score in [standardized.extraversion, standardized.agreeableness,
                     standardized.conscientiousness, standardized.neuroticism,
                     standardized.openness]:
            assert 0 <= score <= 100

        # Check percentiles are calculated
        assert isinstance(percentiles, dict)
        assert len(percentiles) == 5

        # Check percentile ranges
        for percentile in percentiles.values():
            assert 0.1 <= percentile <= 99.9

    def test_calculate_confidence(self):
        """Test confidence calculation."""
        raw_scores = BigFiveScores(
            extraversion=26, agreeableness=18, conscientiousness=26,
            neuroticism=8, openness=18
        )

        confidence = self.scorer._calculate_confidence(self.test_responses, raw_scores)

        # Confidence should be between 0 and 1
        assert 0.0 <= confidence <= 1.0

        # Should return a float with 3 decimal places
        assert isinstance(confidence, float)

    def test_score_assessment_complete_pipeline(self):
        """Test complete scoring pipeline."""
        completion_time = 300  # 5 minutes

        result = self.scorer.score_assessment(self.test_responses, completion_time)

        # Check result structure
        assert isinstance(result, ScoringResult)
        assert isinstance(result.raw_scores, BigFiveScores)
        assert isinstance(result.standardized_scores, BigFiveScores)
        assert isinstance(result.percentiles, dict)
        assert isinstance(result.quality_flags, list)
        assert isinstance(result.confidence, float)
        assert isinstance(result.processing_time_ms, float)
        assert result.algorithm_version == "v1.0.0"
        assert isinstance(result.calculated_at, datetime)

        # Check performance requirement
        assert result.processing_time_ms < 10  # Less than 10ms

    def test_score_assessment_with_quality_issues(self):
        """Test scoring with responses that have quality issues."""
        # Create responses with quality issues (all same response)
        poor_quality_responses = [
            ItemResponse(item_id=f"ipip_{i:03d}", response=4)
            for i in range(1, 21)
        ]

        completion_time = 30  # Very fast completion

        result = self.scorer.score_assessment(poor_quality_responses, completion_time)

        # Should still produce results but with quality flags
        assert isinstance(result, ScoringResult)
        assert len(result.quality_flags) > 0
        assert "ALL_SAME_RESPONSE" in result.quality_flags
        assert "COMPLETION_TOO_FAST" in result.quality_flags

        # Confidence should be low
        assert result.confidence < 0.5

    def test_response_consistency_assessment(self):
        """Test response consistency calculation."""
        # Create highly consistent responses within factors
        consistent_responses = []
        response_value = 6
        for item_id in self.scorer.ITEM_FACTOR_MAPPING.keys():
            consistent_responses.append(ItemResponse(item_id=item_id, response=response_value))

        consistency_score = self.scorer._assess_response_consistency(consistent_responses)

        # High consistency should result in high score
        assert 0.0 <= consistency_score <= 1.0
        assert consistency_score > 0.8  # Should be high for consistent responses

    def test_score_extremeness_assessment(self):
        """Test score extremeness calculation."""
        # Create extreme scores (far from midpoint)
        extreme_scores = BigFiveScores(
            extraversion=28, agreeableness=4, conscientiousness=26,
            neuroticism=6, openness=24
        )

        extremeness_score = self.scorer._assess_score_extremeness(extreme_scores)

        # Extreme scores should result in high extremeness
        assert 0.0 <= extremeness_score <= 1.0
        assert extremeness_score > 0.7  # Should be high for extreme scores

    def test_response_variance_assessment(self):
        """Test response variance calculation."""
        # Test with good variance
        varied_responses = [
            ItemResponse(item_id=f"ipip_{i:03d}", response=(i % 7) + 1)
            for i in range(1, 21)
        ]

        variance_score = self.scorer._assess_response_variance(varied_responses)
        assert 0.0 <= variance_score <= 1.0

        # Test with no variance (all same)
        same_responses = [
            ItemResponse(item_id=f"ipip_{i:03d}", response=4)
            for i in range(1, 21)
        ]

        no_variance_score = self.scorer._assess_response_variance(same_responses)
        assert no_variance_score == 0.0

    def test_performance_requirement(self):
        """Test that scoring meets performance requirements."""
        import time

        start_time = time.perf_counter()
        result = self.scorer.score_assessment(self.test_responses, 300)
        end_time = time.perf_counter()

        actual_time_ms = (end_time - start_time) * 1000

        # Should meet the 10ms performance target
        assert actual_time_ms < 10
        assert result.processing_time_ms < 10

    def test_algorithm_version_tracking(self):
        """Test that algorithm version is tracked correctly."""
        result = self.scorer.score_assessment(self.test_responses, 300)
        assert result.algorithm_version == "v1.0.0"

    def test_item_factor_mapping_completeness(self):
        """Test that all 20 items are mapped to factors."""
        assert len(self.scorer.ITEM_FACTOR_MAPPING) == 20

        # Check that all expected items are present
        expected_items = [f"ipip_{i:03d}" for i in range(1, 21)]
        actual_items = list(self.scorer.ITEM_FACTOR_MAPPING.keys())

        assert set(expected_items) == set(actual_items)

        # Check that all Big Five factors are represented
        factors = [mapping[0] for mapping in self.scorer.ITEM_FACTOR_MAPPING.values()]
        expected_factors = {"extraversion", "agreeableness", "conscientiousness",
                           "neuroticism", "openness"}
        assert set(factors) == expected_factors

    def test_reverse_scoring_items_identification(self):
        """Test that reverse-scored items are correctly identified."""
        # Check that reverse-scored items match documentation
        expected_reverse_items = {
            "ipip_002", "ipip_004", "ipip_006", "ipip_008", "ipip_010",
            "ipip_012", "ipip_014", "ipip_016", "ipip_018", "ipip_020"
        }

        assert self.scorer.REVERSE_SCORED_ITEMS == expected_reverse_items

        # Check that reverse items match the mapping
        reverse_in_mapping = {
            item_id for item_id, (factor, is_reverse)
            in self.scorer.ITEM_FACTOR_MAPPING.items()
            if is_reverse
        }

        assert reverse_in_mapping == expected_reverse_items