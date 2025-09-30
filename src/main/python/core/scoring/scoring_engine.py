#!/usr/bin/env python3
"""
Scoring Engine - Gallup Strengths Assessment

Implements the main scoring engine for Mini-IPIP personality assessments.
Follows Test-Driven Development (TDD) principles and Design by Contract (DbC).
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from models.schemas import QuestionResponse


@dataclass
class DimensionScores:
    """Scores for all Big Five personality dimensions."""
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary format."""
        return {
            "openness": self.openness,
            "conscientiousness": self.conscientiousness,
            "extraversion": self.extraversion,
            "agreeableness": self.agreeableness,
            "neuroticism": self.neuroticism
        }


class ScoringEngine:
    """
    Main scoring engine for Mini-IPIP Big Five personality assessment.

    Implements standard scoring procedures for the 20-item Mini-IPIP questionnaire.
    """

    def __init__(self):
        """Initialize scoring engine with Mini-IPIP question mapping."""
        # Mini-IPIP question to dimension mapping
        self.dimension_mapping = {
            "openness": [1, 2, 3, 4],
            "conscientiousness": [5, 6, 7, 8],
            "extraversion": [9, 10, 11, 12],
            "agreeableness": [13, 14, 15, 16],
            "neuroticism": [17, 18, 19, 20]
        }

        # Valid dimension names
        self.valid_dimensions = set(self.dimension_mapping.keys())

    def calculate_dimension_score(
        self,
        dimension: str,
        responses: List[QuestionResponse]
    ) -> float:
        """
        Calculate score for a specific Big Five dimension.

        Args:
            dimension: Dimension name (openness, conscientiousness, etc.)
            responses: List of question responses

        Returns:
            Dimension score (sum of 4 question scores)

        Raises:
            ValueError: If dimension invalid, wrong number of responses,
                       or invalid score values

        Preconditions:
            - dimension must be valid Big Five dimension
            - responses must contain exactly 4 responses for the dimension
            - each response score must be 1-5

        Postconditions:
            - returned score is sum of 4 question scores
            - score is in range [4, 20]
        """
        # Validate dimension name
        if dimension not in self.valid_dimensions:
            raise ValueError(f"Invalid dimension: {dimension}")

        # Validate responses not empty
        if not responses:
            raise ValueError("Responses cannot be empty")

        # Validate correct number of responses
        if len(responses) != 4:
            raise ValueError(f"Expected 4 responses for {dimension}, got {len(responses)}")

        # Get expected question IDs for this dimension
        expected_questions = set(self.dimension_mapping[dimension])

        # Validate question IDs and collect scores
        question_ids = []
        scores = []

        for response in responses:
            # Validate score range (defense in depth)
            if not 1 <= response.score <= 5:
                raise ValueError(f"Score must be between 1 and 5, got {response.score}")

            question_ids.append(response.question_id)
            scores.append(response.score)

        # Check for duplicates
        if len(set(question_ids)) != len(question_ids):
            raise ValueError("Duplicate question IDs detected")

        # Validate question IDs match dimension
        actual_questions = set(question_ids)
        if actual_questions != expected_questions:
            raise ValueError(
                f"Question IDs {actual_questions} don't match expected {expected_questions} for {dimension}"
            )

        # Calculate and return score
        total_score = sum(scores)

        # Postcondition check
        assert 4 <= total_score <= 20, f"Score {total_score} out of valid range [4, 20]"

        return float(total_score)

    def calculate_all_dimensions(
        self,
        responses: List[QuestionResponse]
    ) -> Dict[str, float]:
        """
        Calculate scores for all Big Five dimensions.

        Args:
            responses: Complete list of 20 question responses

        Returns:
            Dictionary with scores for all 5 dimensions

        Raises:
            ValueError: If wrong number of responses or invalid data

        Preconditions:
            - responses must contain exactly 20 responses
            - question IDs must be 1-20 with no duplicates
            - all scores must be 1-5

        Postconditions:
            - returned dict has all 5 dimension keys
            - all scores are in range [4, 20]
        """
        # Validate minimum response count (traditional questions are required)
        traditional_responses = [r for r in responses if 1 <= r.question_id <= 20]
        if len(traditional_responses) != 20:
            raise ValueError(f"Expected 20 traditional responses (questions 1-20), got {len(traditional_responses)}")

        # Log info about situational questions
        situational_responses = [r for r in responses if 21 <= r.question_id <= 23]
        if situational_responses:
            print(f"Found {len(situational_responses)} situational responses, will be used for enhanced analysis")

        # Group responses by dimension
        dimension_responses = {dim: [] for dim in self.valid_dimensions}

        # Only process traditional responses for Big Five scoring
        for response in traditional_responses:
            # Find which dimension this question belongs to
            for dim, question_ids in self.dimension_mapping.items():
                if response.question_id in question_ids:
                    dimension_responses[dim].append(response)
                    break
            else:
                raise ValueError(f"Question ID {response.question_id} not found in any dimension")

        # Calculate score for each dimension
        scores = {}
        for dimension in self.valid_dimensions:
            dim_responses = dimension_responses[dimension]
            scores[dimension] = self.calculate_dimension_score(dimension, dim_responses)

        # Postcondition check
        assert len(scores) == 5, "Must have scores for all 5 dimensions"
        for dim, score in scores.items():
            assert 4 <= score <= 20, f"{dim} score {score} out of range"

        return scores

    def get_dimension_questions(self) -> Dict[str, List[int]]:
        """
        Get the mapping of dimensions to question IDs.

        Returns:
            Dictionary mapping dimension names to question ID lists
        """
        return self.dimension_mapping.copy()

    def create_dimension_scores(
        self,
        responses: List[QuestionResponse]
    ) -> DimensionScores:
        """
        Create DimensionScores object from responses.

        Args:
            responses: Complete list of 20 question responses

        Returns:
            DimensionScores object with all dimension scores
        """
        scores = self.calculate_all_dimensions(responses)

        return DimensionScores(
            openness=scores["openness"],
            conscientiousness=scores["conscientiousness"],
            extraversion=scores["extraversion"],
            agreeableness=scores["agreeableness"],
            neuroticism=scores["neuroticism"]
        )