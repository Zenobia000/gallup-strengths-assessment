"""
Test Suite for Scoring Engine
Tests the Mini-IPIP Big Five personality dimension scoring logic.

Following TDD principles and Design by Contract (DbC).
"""

import pytest
from typing import List, Dict

# Import the module we'll create
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "main" / "python"))

from core.scoring import ScoringEngine, DimensionScores
from models.schemas import QuestionResponse


class TestScoringEngine:
    """Test suite for ScoringEngine class."""

    @pytest.fixture
    def scoring_engine(self):
        """Fixture to provide a ScoringEngine instance."""
        return ScoringEngine()

    @pytest.fixture
    def sample_responses_openness(self) -> List[QuestionResponse]:
        """
        Sample responses for Openness dimension (questions 1-4).
        Expected score: (5 + 4 + 3 + 5) = 17
        """
        return [
            QuestionResponse(question_id=1, score=5),   # Openness Q1
            QuestionResponse(question_id=2, score=4),   # Openness Q2
            QuestionResponse(question_id=3, score=3),   # Openness Q3
            QuestionResponse(question_id=4, score=5),   # Openness Q4
        ]

    @pytest.fixture
    def sample_responses_conscientiousness(self) -> List[QuestionResponse]:
        """
        Sample responses for Conscientiousness dimension (questions 5-8).
        Expected score: (4 + 4 + 4 + 4) = 16
        """
        return [
            QuestionResponse(question_id=5, score=4),   # Conscientiousness Q1
            QuestionResponse(question_id=6, score=4),   # Conscientiousness Q2
            QuestionResponse(question_id=7, score=4),   # Conscientiousness Q3
            QuestionResponse(question_id=8, score=4),   # Conscientiousness Q4
        ]

    @pytest.fixture
    def complete_responses(self) -> List[QuestionResponse]:
        """
        Complete 20-question responses covering all 5 dimensions.
        """
        return [
            # Openness (1-4): scores = 5, 4, 3, 5 → sum = 17
            QuestionResponse(question_id=1, score=5),
            QuestionResponse(question_id=2, score=4),
            QuestionResponse(question_id=3, score=3),
            QuestionResponse(question_id=4, score=5),
            # Conscientiousness (5-8): scores = 4, 4, 4, 4 → sum = 16
            QuestionResponse(question_id=5, score=4),
            QuestionResponse(question_id=6, score=4),
            QuestionResponse(question_id=7, score=4),
            QuestionResponse(question_id=8, score=4),
            # Extraversion (9-12): scores = 5, 5, 2, 3 → sum = 15
            QuestionResponse(question_id=9, score=5),
            QuestionResponse(question_id=10, score=5),
            QuestionResponse(question_id=11, score=2),
            QuestionResponse(question_id=12, score=3),
            # Agreeableness (13-16): scores = 4, 5, 4, 3 → sum = 16
            QuestionResponse(question_id=13, score=4),
            QuestionResponse(question_id=14, score=5),
            QuestionResponse(question_id=15, score=4),
            QuestionResponse(question_id=16, score=3),
            # Neuroticism (17-20): scores = 2, 2, 3, 2 → sum = 9
            QuestionResponse(question_id=17, score=2),
            QuestionResponse(question_id=18, score=2),
            QuestionResponse(question_id=19, score=3),
            QuestionResponse(question_id=20, score=2),
        ]

    # Test 1: Calculate Openness Score
    def test_calculate_openness_score(
        self,
        scoring_engine: ScoringEngine,
        sample_responses_openness: List[QuestionResponse]
    ):
        """
        Test calculating Openness dimension score.

        Preconditions:
            - Responses for questions 1-4 exist
            - Scores are in range 1-5

        Postconditions:
            - Openness score is sum of 4 questions
            - Score is in range 4-20
        """
        score = scoring_engine.calculate_dimension_score(
            dimension="openness",
            responses=sample_responses_openness
        )

        assert score == 17.0
        assert 4 <= score <= 20, "Openness score must be in range [4, 20]"

    # Test 2: Calculate Conscientiousness Score
    def test_calculate_conscientiousness_score(
        self,
        scoring_engine: ScoringEngine,
        sample_responses_conscientiousness: List[QuestionResponse]
    ):
        """
        Test calculating Conscientiousness dimension score.
        """
        score = scoring_engine.calculate_dimension_score(
            dimension="conscientiousness",
            responses=sample_responses_conscientiousness
        )

        assert score == 16.0
        assert 4 <= score <= 20

    # Test 3: Calculate All Dimensions
    def test_calculate_all_dimensions(
        self,
        scoring_engine: ScoringEngine,
        complete_responses: List[QuestionResponse]
    ):
        """
        Test calculating all 5 Big Five dimensions at once.

        Preconditions:
            - 20 complete responses provided
            - Each dimension has exactly 4 questions

        Postconditions:
            - All 5 dimensions have scores
            - Each score is in range [4, 20]
        """
        scores = scoring_engine.calculate_all_dimensions(complete_responses)

        # Check all dimensions are present
        assert len(scores) == 5
        assert "openness" in scores
        assert "conscientiousness" in scores
        assert "extraversion" in scores
        assert "agreeableness" in scores
        assert "neuroticism" in scores

        # Check expected scores
        assert scores["openness"] == 17.0
        assert scores["conscientiousness"] == 16.0
        assert scores["extraversion"] == 15.0
        assert scores["agreeableness"] == 16.0
        assert scores["neuroticism"] == 9.0

        # Check all scores in valid range
        for dimension, score in scores.items():
            assert 4 <= score <= 20, f"{dimension} score out of range: {score}"

    # Test 4: Minimum Score Boundary (all 1s)
    def test_minimum_score_boundary(self, scoring_engine: ScoringEngine):
        """
        Test boundary condition: all minimum scores (1).

        Expected: dimension score = 4 (1+1+1+1)
        """
        min_responses = [
            QuestionResponse(question_id=i, score=1)
            for i in range(1, 5)
        ]

        score = scoring_engine.calculate_dimension_score(
            dimension="openness",
            responses=min_responses
        )

        assert score == 4.0, "Minimum score should be 4"

    # Test 5: Maximum Score Boundary (all 5s)
    def test_maximum_score_boundary(self, scoring_engine: ScoringEngine):
        """
        Test boundary condition: all maximum scores (5).

        Expected: dimension score = 20 (5+5+5+5)
        """
        max_responses = [
            QuestionResponse(question_id=i, score=5)
            for i in range(1, 5)
        ]

        score = scoring_engine.calculate_dimension_score(
            dimension="openness",
            responses=max_responses
        )

        assert score == 20.0, "Maximum score should be 20"

    # Test 6: Invalid Response Count
    def test_invalid_response_count(self, scoring_engine: ScoringEngine):
        """
        Test error handling: incorrect number of responses.

        Precondition violation: must have exactly 4 responses per dimension.
        """
        invalid_responses = [
            QuestionResponse(question_id=1, score=5),
            QuestionResponse(question_id=2, score=4),
            # Missing 2 responses
        ]

        with pytest.raises(ValueError, match="Expected 4 responses"):
            scoring_engine.calculate_dimension_score(
                dimension="openness",
                responses=invalid_responses
            )

    # Test 7: Invalid Score Range
    def test_invalid_score_range(self, scoring_engine: ScoringEngine):
        """
        Test error handling: score outside valid range [1, 5].

        Precondition violation: scores must be 1-5.
        Note: Pydantic validation catches this at model instantiation.
        """
        from pydantic import ValidationError

        # Test Pydantic validation catches invalid score at instantiation
        with pytest.raises(ValidationError):
            QuestionResponse(question_id=1, score=6)  # Invalid: > 5

        with pytest.raises(ValidationError):
            QuestionResponse(question_id=1, score=0)  # Invalid: < 1

        # Also test that ScoringEngine catches it if somehow bypassed
        # (for defense in depth)
        class MockResponse:
            def __init__(self, question_id, score):
                self.question_id = question_id
                self.score = score

        invalid_responses = [
            MockResponse(1, 6),  # Bypass Pydantic validation
            MockResponse(2, 4),
            MockResponse(3, 3),
            MockResponse(4, 5),
        ]

        with pytest.raises(ValueError, match="Score must be between 1 and 5"):
            scoring_engine.calculate_dimension_score(
                dimension="openness",
                responses=invalid_responses
            )

    # Test 8: Invalid Dimension Name
    def test_invalid_dimension_name(self, scoring_engine: ScoringEngine):
        """
        Test error handling: invalid dimension name.
        """
        responses = [
            QuestionResponse(question_id=i, score=3)
            for i in range(1, 5)
        ]

        with pytest.raises(ValueError, match="Invalid dimension"):
            scoring_engine.calculate_dimension_score(
                dimension="invalid_dimension",
                responses=responses
            )

    # Test 9: Empty Responses
    def test_empty_responses(self, scoring_engine: ScoringEngine):
        """
        Test error handling: empty response list.
        """
        with pytest.raises(ValueError, match="Responses cannot be empty"):
            scoring_engine.calculate_dimension_score(
                dimension="openness",
                responses=[]
            )

    # Test 10: Duplicate Question IDs
    def test_duplicate_question_ids(self, scoring_engine: ScoringEngine):
        """
        Test error handling: duplicate question IDs in responses.
        """
        duplicate_responses = [
            QuestionResponse(question_id=1, score=5),
            QuestionResponse(question_id=1, score=4),  # Duplicate ID
            QuestionResponse(question_id=3, score=3),
            QuestionResponse(question_id=4, score=5),
        ]

        with pytest.raises(ValueError, match="Duplicate question"):
            scoring_engine.calculate_dimension_score(
                dimension="openness",
                responses=duplicate_responses
            )

    # Test 11: Question ID Mapping
    def test_question_id_to_dimension_mapping(self, scoring_engine: ScoringEngine):
        """
        Test that question IDs correctly map to dimensions.

        Mini-IPIP mapping:
        - Openness: Q1-4
        - Conscientiousness: Q5-8
        - Extraversion: Q9-12
        - Agreeableness: Q13-16
        - Neuroticism: Q17-20
        """
        mapping = scoring_engine.get_dimension_questions()

        assert mapping["openness"] == [1, 2, 3, 4]
        assert mapping["conscientiousness"] == [5, 6, 7, 8]
        assert mapping["extraversion"] == [9, 10, 11, 12]
        assert mapping["agreeableness"] == [13, 14, 15, 16]
        assert mapping["neuroticism"] == [17, 18, 19, 20]

    # Test 12: Immutability of Responses
    def test_responses_not_modified(
        self,
        scoring_engine: ScoringEngine,
        complete_responses: List[QuestionResponse]
    ):
        """
        Test that calculating scores does not modify input responses.

        Invariant: Input data should remain unchanged.
        """
        original_responses = [
            QuestionResponse(question_id=r.question_id, score=r.score)
            for r in complete_responses
        ]

        _ = scoring_engine.calculate_all_dimensions(complete_responses)

        # Verify responses unchanged
        assert len(complete_responses) == len(original_responses)
        for original, current in zip(original_responses, complete_responses):
            assert original.question_id == current.question_id
            assert original.score == current.score