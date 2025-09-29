"""
Scoring Engine for Mini-IPIP Big Five Personality Assessment

This module implements the scoring logic for the Mini-IPIP (International
Personality Item Pool) 20-item questionnaire, which measures the Big Five
personality dimensions:
- Openness to Experience
- Conscientiousness
- Extraversion
- Agreeableness
- Neuroticism

Design by Contract (DbC):
- Preconditions: Validated input responses (1-5 scale, correct count)
- Postconditions: Dimension scores in range [4, 20]
- Invariants: Each dimension has exactly 4 questions

Author: General Purpose Agent (TaskMaster Hub)
Date: 2025-09-30
Version: 1.0
"""

from typing import List, Dict
from dataclasses import dataclass

from models.schemas import QuestionResponse


@dataclass
class DimensionScores:
    """
    Container for Big Five dimension scores.

    Attributes:
        openness: Openness to Experience (4-20)
        conscientiousness: Conscientiousness (4-20)
        extraversion: Extraversion (4-20)
        agreeableness: Agreeableness (4-20)
        neuroticism: Neuroticism (4-20)
    """
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float

    def to_dict(self) -> Dict[str, float]:
        """Convert scores to dictionary format."""
        return {
            "openness": self.openness,
            "conscientiousness": self.conscientiousness,
            "extraversion": self.extraversion,
            "agreeableness": self.agreeableness,
            "neuroticism": self.neuroticism,
        }


class ScoringEngine:
    """
    Scoring engine for Mini-IPIP Big Five personality assessment.

    This class implements the scoring logic for the 20-item Mini-IPIP
    questionnaire. Each of the Big Five dimensions is measured by 4 questions,
    with scores summed to produce dimension scores ranging from 4 to 20.

    Mini-IPIP Question to Dimension Mapping:
        - Openness: Questions 1-4
        - Conscientiousness: Questions 5-8
        - Extraversion: Questions 9-12
        - Agreeableness: Questions 13-16
        - Neuroticism: Questions 17-20

    Note: Reverse scoring is NOT handled in this class.
          It will be implemented in task 3.2.3.
    """

    # Dimension to question ID mapping
    DIMENSION_QUESTIONS: Dict[str, List[int]] = {
        "openness": [1, 2, 3, 4],
        "conscientiousness": [5, 6, 7, 8],
        "extraversion": [9, 10, 11, 12],
        "agreeableness": [13, 14, 15, 16],
        "neuroticism": [17, 18, 19, 20],
    }

    # Valid dimension names
    VALID_DIMENSIONS = set(DIMENSION_QUESTIONS.keys())

    # Score constraints
    MIN_SCORE_PER_QUESTION = 1
    MAX_SCORE_PER_QUESTION = 5
    QUESTIONS_PER_DIMENSION = 4
    MIN_DIMENSION_SCORE = QUESTIONS_PER_DIMENSION * MIN_SCORE_PER_QUESTION  # 4
    MAX_DIMENSION_SCORE = QUESTIONS_PER_DIMENSION * MAX_SCORE_PER_QUESTION  # 20

    def __init__(self):
        """Initialize the ScoringEngine."""
        pass

    def get_dimension_questions(self) -> Dict[str, List[int]]:
        """
        Get the mapping of dimensions to question IDs.

        Returns:
            Dictionary mapping dimension names to list of question IDs.

        Example:
            >>> engine = ScoringEngine()
            >>> mapping = engine.get_dimension_questions()
            >>> mapping["openness"]
            [1, 2, 3, 4]
        """
        return self.DIMENSION_QUESTIONS.copy()

    def calculate_dimension_score(
        self,
        dimension: str,
        responses: List[QuestionResponse]
    ) -> float:
        """
        Calculate the score for a single Big Five dimension.

        This method sums the scores for the 4 questions that measure
        the specified dimension.

        Preconditions:
            - dimension must be a valid dimension name
            - responses must contain exactly 4 responses
            - Each response score must be in range [1, 5]
            - No duplicate question IDs

        Postconditions:
            - Returns a score in range [4, 20]

        Args:
            dimension: Name of the dimension to calculate
                      (openness, conscientiousness, extraversion,
                       agreeableness, neuroticism)
            responses: List of QuestionResponse objects for this dimension

        Returns:
            Dimension score (sum of 4 question scores)

        Raises:
            ValueError: If preconditions are violated

        Example:
            >>> engine = ScoringEngine()
            >>> responses = [
            ...     QuestionResponse(question_id=1, score=5),
            ...     QuestionResponse(question_id=2, score=4),
            ...     QuestionResponse(question_id=3, score=3),
            ...     QuestionResponse(question_id=4, score=5),
            ... ]
            >>> score = engine.calculate_dimension_score("openness", responses)
            >>> score
            17.0
        """
        # Precondition: Validate dimension name
        if dimension not in self.VALID_DIMENSIONS:
            raise ValueError(
                f"Invalid dimension '{dimension}'. "
                f"Must be one of: {', '.join(sorted(self.VALID_DIMENSIONS))}"
            )

        # Precondition: Check responses not empty
        if not responses:
            raise ValueError("Responses cannot be empty")

        # Precondition: Check correct number of responses
        if len(responses) != self.QUESTIONS_PER_DIMENSION:
            raise ValueError(
                f"Expected {self.QUESTIONS_PER_DIMENSION} responses "
                f"for dimension '{dimension}', got {len(responses)}"
            )

        # Get expected question IDs for this dimension
        expected_question_ids = set(self.DIMENSION_QUESTIONS[dimension])
        actual_question_ids = [r.question_id for r in responses]

        # Precondition: Check for duplicate question IDs
        if len(actual_question_ids) != len(set(actual_question_ids)):
            raise ValueError(
                f"Duplicate question IDs found in responses: {actual_question_ids}"
            )

        # Calculate score
        total_score = 0.0
        for response in responses:
            # Precondition: Validate score range
            if not (self.MIN_SCORE_PER_QUESTION <= response.score <= self.MAX_SCORE_PER_QUESTION):
                raise ValueError(
                    f"Score must be between {self.MIN_SCORE_PER_QUESTION} "
                    f"and {self.MAX_SCORE_PER_QUESTION}, "
                    f"got {response.score} for question {response.question_id}"
                )

            total_score += response.score

        # Postcondition: Verify score in valid range
        assert self.MIN_DIMENSION_SCORE <= total_score <= self.MAX_DIMENSION_SCORE, \
            f"Dimension score {total_score} out of valid range [{self.MIN_DIMENSION_SCORE}, {self.MAX_DIMENSION_SCORE}]"

        return total_score

    def calculate_all_dimensions(
        self,
        responses: List[QuestionResponse]
    ) -> Dict[str, float]:
        """
        Calculate scores for all Big Five dimensions.

        This method processes all 20 responses and calculates scores
        for each of the five personality dimensions.

        Preconditions:
            - responses must contain exactly 20 responses
            - Question IDs must be 1-20 (no gaps, no duplicates)
            - Each response score must be in range [1, 5]

        Postconditions:
            - Returns dictionary with all 5 dimension scores
            - Each score is in range [4, 20]

        Args:
            responses: List of 20 QuestionResponse objects

        Returns:
            Dictionary mapping dimension names to scores

        Raises:
            ValueError: If preconditions are violated

        Example:
            >>> engine = ScoringEngine()
            >>> responses = [
            ...     QuestionResponse(question_id=i, score=3)
            ...     for i in range(1, 21)
            ... ]
            >>> scores = engine.calculate_all_dimensions(responses)
            >>> len(scores)
            5
            >>> all(score == 12.0 for score in scores.values())
            True
        """
        # Precondition: Check total response count
        expected_total = len(self.DIMENSION_QUESTIONS) * self.QUESTIONS_PER_DIMENSION
        if len(responses) != expected_total:
            raise ValueError(
                f"Expected {expected_total} total responses, got {len(responses)}"
            )

        # Precondition: Validate question IDs
        question_ids = [r.question_id for r in responses]
        expected_ids = set(range(1, expected_total + 1))
        actual_ids = set(question_ids)

        if actual_ids != expected_ids:
            missing = expected_ids - actual_ids
            extra = actual_ids - expected_ids
            error_msg = "Invalid question IDs. "
            if missing:
                error_msg += f"Missing: {sorted(missing)}. "
            if extra:
                error_msg += f"Unexpected: {sorted(extra)}."
            raise ValueError(error_msg)

        # Check for duplicates
        if len(question_ids) != len(actual_ids):
            raise ValueError(f"Duplicate question IDs found: {question_ids}")

        # Create a lookup dictionary for faster access
        response_dict = {r.question_id: r for r in responses}

        # Calculate score for each dimension
        dimension_scores = {}
        for dimension, question_ids in self.DIMENSION_QUESTIONS.items():
            # Get responses for this dimension
            dimension_responses = [
                response_dict[qid] for qid in question_ids
            ]

            # Calculate dimension score
            score = self.calculate_dimension_score(dimension, dimension_responses)
            dimension_scores[dimension] = score

        # Postcondition: Verify all dimensions calculated
        assert len(dimension_scores) == len(self.DIMENSION_QUESTIONS), \
            "Not all dimensions were calculated"

        return dimension_scores

    def create_dimension_scores_object(
        self,
        scores_dict: Dict[str, float]
    ) -> DimensionScores:
        """
        Create a DimensionScores dataclass from a scores dictionary.

        Args:
            scores_dict: Dictionary with dimension scores

        Returns:
            DimensionScores object

        Raises:
            KeyError: If any dimension is missing from the dictionary
        """
        return DimensionScores(
            openness=scores_dict["openness"],
            conscientiousness=scores_dict["conscientiousness"],
            extraversion=scores_dict["extraversion"],
            agreeableness=scores_dict["agreeableness"],
            neuroticism=scores_dict["neuroticism"],
        )

    def validate_responses(self, responses: List[QuestionResponse]) -> bool:
        """
        Validate a list of responses before scoring.

        This is a convenience method that can be called before
        calculate_all_dimensions to check if responses are valid.

        Args:
            responses: List of QuestionResponse objects to validate

        Returns:
            True if all validations pass

        Raises:
            ValueError: If any validation fails
        """
        try:
            # This will raise ValueError if any validation fails
            _ = self.calculate_all_dimensions(responses)
            return True
        except ValueError:
            raise