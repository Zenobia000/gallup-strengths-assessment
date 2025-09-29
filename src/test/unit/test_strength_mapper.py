"""
Unit Tests for Strengths Mapper

Tests strength mapping functionality including:
- Big Five to 12 strengths conversion
- Formula validation and calculations
- Top strengths identification
- Development area flagging
- Confidence scoring per strength

Author: TaskMaster Week 2 Testing Implementation
Version: 1.0.0
"""

import pytest
from models.schemas import BigFiveScores, StrengthScores
from core.scoring.strength_mapper import StrengthsMapper, StrengthMappingResult


class TestStrengthsMapper:
    """Test suite for strength mapping functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mapper = StrengthsMapper()

        # Create test Big Five scores
        self.test_big_five = BigFiveScores(
            extraversion=70,        # High
            agreeableness=60,       # Medium-high
            conscientiousness=80,   # High
            neuroticism=30,         # Low (emotionally stable)
            openness=65            # Medium-high
        )

        # Create extreme Big Five scores for testing
        self.extreme_big_five = BigFiveScores(
            extraversion=95,        # Very high
            agreeableness=15,       # Very low
            conscientiousness=90,   # Very high
            neuroticism=10,         # Very low (very stable)
            openness=85            # High
        )

    def test_mapper_initialization(self):
        """Test mapper initialization."""
        mapper = StrengthsMapper()
        assert mapper.MAPPING_VERSION == "v1.0.0"
        assert len(mapper.STRENGTH_FORMULAS) == 12
        assert len(mapper.STRENGTH_DESCRIPTIONS) == 12

    def test_strength_formulas_completeness(self):
        """Test that all strength formulas are defined."""
        expected_strengths = {
            "結構化執行", "品質與完備", "探索與創新", "分析與洞察",
            "影響與倡議", "協作與共好", "客戶導向", "學習與成長",
            "紀律與信任", "壓力調節", "衝突整合", "責任與當責"
        }

        formula_strengths = set(self.mapper.STRENGTH_FORMULAS.keys())
        description_strengths = set(self.mapper.STRENGTH_DESCRIPTIONS.keys())

        assert formula_strengths == expected_strengths
        assert description_strengths == expected_strengths

    def test_map_to_strengths_basic_functionality(self):
        """Test basic strength mapping functionality."""
        result = self.mapper.map_to_strengths(self.test_big_five)

        # Check result structure
        assert isinstance(result, StrengthMappingResult)
        assert isinstance(result.strength_scores, StrengthScores)
        assert isinstance(result.top_strengths, list)
        assert isinstance(result.development_areas, list)
        assert isinstance(result.confidence_scores, dict)
        assert result.mapping_version == "v1.0.0"

    def test_strength_score_calculations(self):
        """Test specific strength score calculations using formulas."""
        result = self.mapper.map_to_strengths(self.test_big_five)
        scores = result.strength_scores

        # Test specific formula calculations
        # 結構化執行 = 0.8 * C + 0.2 * (100 - N) = 0.8 * 80 + 0.2 * 70 = 64 + 14 = 78
        expected_structured_execution = int(0.8 * 80 + 0.2 * (100 - 30))
        assert scores.結構化執行 == expected_structured_execution

        # 探索與創新 = 0.8 * O + 0.2 * E = 0.8 * 65 + 0.2 * 70 = 52 + 14 = 66
        expected_innovation = int(0.8 * 65 + 0.2 * 70)
        assert scores.探索與創新 == expected_innovation

        # 協作與共好 = 0.7 * A + 0.3 * E = 0.7 * 60 + 0.3 * 70 = 42 + 21 = 63
        expected_collaboration = int(0.7 * 60 + 0.3 * 70)
        assert scores.協作與共好 == expected_collaboration

        # All scores should be in 0-100 range
        for strength_score in scores.__dict__.values():
            assert 0 <= strength_score <= 100

    def test_strength_score_clamping(self):
        """Test that strength scores are properly clamped to 0-100 range."""
        # Create Big Five scores that might produce out-of-range results
        extreme_scores = BigFiveScores(
            extraversion=100, agreeableness=100, conscientiousness=100,
            neuroticism=0, openness=100
        )

        result = self.mapper.map_to_strengths(extreme_scores)
        scores = result.strength_scores

        # All scores should be clamped to 0-100
        for strength_score in scores.__dict__.values():
            assert 0 <= strength_score <= 100

    def test_top_strengths_identification(self):
        """Test top strengths identification."""
        result = self.mapper.map_to_strengths(self.test_big_five)

        # Should have 3-5 top strengths
        assert 3 <= len(result.top_strengths) <= 5

        # Top strengths should be sorted by score (descending)
        scores = [s["score"] for s in result.top_strengths]
        assert scores == sorted(scores, reverse=True)

        # Each top strength should have required fields
        for strength in result.top_strengths:
            assert "name" in strength
            assert "score" in strength
            assert "confidence" in strength
            assert "description" in strength
            assert "behaviors" in strength
            assert "development_tips" in strength

            # Score should be reasonable for top strength
            assert strength["score"] >= 40  # Should be above average

    def test_development_areas_identification(self):
        """Test development area identification."""
        result = self.mapper.map_to_strengths(self.extreme_big_five)

        # Check development areas structure
        for area in result.development_areas:
            assert "name" in area
            assert "current_score" in area
            assert "confidence" in area
            assert "description" in area
            assert "development_priority" in area
            assert "development_tips" in area

            # Development areas should have low scores
            assert area["current_score"] < 40

            # Priority should be valid
            assert area["development_priority"] in ["high", "medium"]

    def test_confidence_scoring_per_strength(self):
        """Test confidence scoring for individual strengths."""
        result = self.mapper.map_to_strengths(self.test_big_five)

        # Should have confidence score for each strength
        assert len(result.confidence_scores) == 12

        # All confidence scores should be between 0 and 1
        for confidence in result.confidence_scores.values():
            assert 0.0 <= confidence <= 1.0

        # Confidence should be higher for more extreme scores
        high_scores = [name for name, score in result.strength_scores.__dict__.items()
                      if score > 70]
        if high_scores:
            high_confidences = [result.confidence_scores[name] for name in high_scores]
            avg_high_confidence = sum(high_confidences) / len(high_confidences)
            assert avg_high_confidence > 0.5

    def test_primary_factor_strength_assessment(self):
        """Test primary factor strength assessment."""
        # Test with high conscientiousness (primary factor for several strengths)
        high_c_scores = BigFiveScores(
            extraversion=50, agreeableness=50, conscientiousness=90,
            neuroticism=50, openness=50
        )

        primary_confidence = self.mapper._assess_primary_factor_strength(
            "結構化執行", high_c_scores
        )

        # Should have high confidence for conscientiousness-based strength
        assert primary_confidence > 0.7

    def test_factor_consistency_assessment(self):
        """Test factor consistency assessment."""
        # Test with consistent scores
        consistent_scores = BigFiveScores(
            extraversion=60, agreeableness=65, conscientiousness=62,
            neuroticism=58, openness=63
        )

        consistency = self.mapper._assess_factor_consistency(
            "結構化執行", consistent_scores
        )

        # Should have reasonable consistency
        assert 0.0 <= consistency <= 1.0

    def test_strength_descriptions_completeness(self):
        """Test that strength descriptions are complete."""
        for strength_name, description_data in self.mapper.STRENGTH_DESCRIPTIONS.items():
            assert "description" in description_data
            assert "behaviors" in description_data
            assert "development_tips" in description_data

            # Check that lists are not empty
            assert len(description_data["behaviors"]) > 0
            assert len(description_data["development_tips"]) > 0

            # Check that strings are not empty
            assert len(description_data["description"]) > 0

    def test_get_strength_profile_summary(self):
        """Test strength profile summary generation."""
        mapping_result = self.mapper.map_to_strengths(self.test_big_five)
        summary = self.mapper.get_strength_profile_summary(mapping_result)

        # Check summary structure
        required_fields = [
            "profile_type", "profile_description", "average_score",
            "score_variance", "top_strengths", "development_areas",
            "overall_confidence", "mapping_version"
        ]

        for field in required_fields:
            assert field in summary

        # Check data types and ranges
        assert isinstance(summary["average_score"], float)
        assert 0 <= summary["average_score"] <= 100

        assert isinstance(summary["score_variance"], float)
        assert summary["score_variance"] >= 0

        assert isinstance(summary["overall_confidence"], float)
        assert 0.0 <= summary["overall_confidence"] <= 1.0

        assert summary["profile_type"] in ["平衡型", "多元優勢型", "專精型"]

    def test_profile_type_classification(self):
        """Test profile type classification logic."""
        # Test balanced profile (low variance)
        balanced_scores = BigFiveScores(
            extraversion=52, agreeableness=51, conscientiousness=53,
            neuroticism=49, openness=50
        )

        result = self.mapper.map_to_strengths(balanced_scores)
        summary = self.mapper.get_strength_profile_summary(result)

        # Should be classified as balanced with low variance
        if summary["score_variance"] < 100:
            assert summary["profile_type"] == "平衡型"

    def test_confidence_threshold_filtering(self):
        """Test confidence threshold filtering for top strengths."""
        # Test with high confidence threshold
        result = self.mapper.map_to_strengths(
            self.test_big_five, confidence_threshold=0.9
        )

        # With very high threshold, might have fewer top strengths
        assert len(result.top_strengths) >= 0  # Could be empty with high threshold

        # All included strengths should meet the threshold
        for strength in result.top_strengths:
            assert strength["confidence"] >= 0.9

    def test_formula_mathematical_validity(self):
        """Test that formulas produce mathematically valid results."""
        # Test with boundary values
        min_scores = BigFiveScores(
            extraversion=0, agreeableness=0, conscientiousness=0,
            neuroticism=100, openness=0  # Worst case
        )

        max_scores = BigFiveScores(
            extraversion=100, agreeableness=100, conscientiousness=100,
            neuroticism=0, openness=100  # Best case
        )

        min_result = self.mapper.map_to_strengths(min_scores)
        max_result = self.mapper.map_to_strengths(max_scores)

        # All results should be in valid range
        for score in min_result.strength_scores.__dict__.values():
            assert 0 <= score <= 100

        for score in max_result.strength_scores.__dict__.values():
            assert 0 <= score <= 100

        # Max scores should generally be higher than min scores
        min_avg = sum(min_result.strength_scores.__dict__.values()) / 12
        max_avg = sum(max_result.strength_scores.__dict__.values()) / 12
        assert max_avg > min_avg

    def test_development_priority_assignment(self):
        """Test development priority assignment logic."""
        # Create scores with very low strengths
        low_strength_scores = BigFiveScores(
            extraversion=10, agreeableness=15, conscientiousness=20,
            neuroticism=80, openness=25  # Very low performance
        )

        result = self.mapper.map_to_strengths(low_strength_scores)

        # Should have development areas
        assert len(result.development_areas) > 0

        # Check priority assignment
        for area in result.development_areas:
            if area["current_score"] < 30:
                assert area["development_priority"] == "high"
            else:
                assert area["development_priority"] == "medium"

    def test_mapping_version_consistency(self):
        """Test that mapping version is consistently tracked."""
        result = self.mapper.map_to_strengths(self.test_big_five)
        summary = self.mapper.get_strength_profile_summary(result)

        assert result.mapping_version == self.mapper.MAPPING_VERSION
        assert summary["mapping_version"] == self.mapper.MAPPING_VERSION