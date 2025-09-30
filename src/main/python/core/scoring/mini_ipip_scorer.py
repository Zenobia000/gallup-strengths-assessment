#!/usr/bin/env python3
"""
Mini-IPIP Scorer - Gallup Strengths Assessment

Implements scoring logic for the Mini-IPIP 20-item personality questionnaire.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import statistics


class InvalidResponseError(Exception):
    """Raised when response data is invalid"""
    pass


class ScoreConfidence(Enum):
    """Confidence levels for scoring results"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class BigFiveScores:
    """Big Five personality scores"""
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float
    honesty_humility: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return {
            "openness": self.openness,
            "conscientiousness": self.conscientiousness,
            "extraversion": self.extraversion,
            "agreeableness": self.agreeableness,
            "neuroticism": self.neuroticism,
            "honesty_humility": self.honesty_humility
        }


@dataclass
class ScoringResult:
    """Result of Mini-IPIP scoring"""
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float
    honesty_humility: float = 0.0  # Not measured in Mini-IPIP
    raw_scores: Dict[str, float] = None
    percentiles: Dict[str, float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "openness": self.openness,
            "conscientiousness": self.conscientiousness,
            "extraversion": self.extraversion,
            "agreeableness": self.agreeableness,
            "neuroticism": self.neuroticism,
            "honesty_humility": self.honesty_humility,
            "raw_scores": self.raw_scores or {},
            "percentiles": self.percentiles or {}
        }


class MiniIPIPScorer:
    """
    Scorer for Mini-IPIP 20-item personality questionnaire.

    Implements standard scoring procedures for the Big Five personality factors.
    """

    def __init__(self):
        # Mini-IPIP item mapping to dimensions and reverse coding
        self.item_mapping = {
            1: {"dimension": "openness", "reverse": False},
            2: {"dimension": "openness", "reverse": True},
            3: {"dimension": "openness", "reverse": True},
            4: {"dimension": "openness", "reverse": True},
            5: {"dimension": "conscientiousness", "reverse": False},
            6: {"dimension": "conscientiousness", "reverse": True},
            7: {"dimension": "conscientiousness", "reverse": False},
            8: {"dimension": "conscientiousness", "reverse": True},
            9: {"dimension": "extraversion", "reverse": False},
            10: {"dimension": "extraversion", "reverse": True},
            11: {"dimension": "extraversion", "reverse": True},
            12: {"dimension": "extraversion", "reverse": True},
            13: {"dimension": "agreeableness", "reverse": False},
            14: {"dimension": "agreeableness", "reverse": True},
            15: {"dimension": "agreeableness", "reverse": False},
            16: {"dimension": "agreeableness", "reverse": True},
            17: {"dimension": "neuroticism", "reverse": False},
            18: {"dimension": "neuroticism", "reverse": True},
            19: {"dimension": "neuroticism", "reverse": False},
            20: {"dimension": "neuroticism", "reverse": True}
        }

        # Population norms for percentile calculation (approximate)
        self.norms = {
            "openness": {"mean": 3.5, "std": 0.7},
            "conscientiousness": {"mean": 3.7, "std": 0.6},
            "extraversion": {"mean": 3.2, "std": 0.8},
            "agreeableness": {"mean": 3.8, "std": 0.6},
            "neuroticism": {"mean": 2.8, "std": 0.8}
        }

    def score_responses(self, responses: List[Dict[str, Any]]) -> ScoringResult:
        """
        Score Mini-IPIP responses and calculate Big Five scores.

        Args:
            responses: List of response dicts with 'question_id' and 'score'

        Returns:
            ScoringResult with Big Five scores

        Raises:
            InvalidResponseError: If responses are invalid
        """
        self._validate_responses(responses)

        # Convert to indexed format
        indexed_responses = {}
        for response in responses:
            question_id = response.get('question_id')
            score = response.get('score')
            indexed_responses[question_id] = score

        # Calculate dimension scores
        dimension_scores = self._calculate_dimension_scores(indexed_responses)

        # Calculate raw scores (means)
        raw_scores = {}
        for dimension, scores in dimension_scores.items():
            raw_scores[dimension] = statistics.mean(scores) if scores else 0.0

        # Calculate percentiles
        percentiles = self._calculate_percentiles(raw_scores)

        return ScoringResult(
            openness=raw_scores.get("openness", 0.0),
            conscientiousness=raw_scores.get("conscientiousness", 0.0),
            extraversion=raw_scores.get("extraversion", 0.0),
            agreeableness=raw_scores.get("agreeableness", 0.0),
            neuroticism=raw_scores.get("neuroticism", 0.0),
            honesty_humility=0.0,  # Not measured in Mini-IPIP
            raw_scores=raw_scores,
            percentiles=percentiles
        )

    def _validate_responses(self, responses: List[Dict[str, Any]]) -> None:
        """Validate response data"""
        if not responses:
            raise InvalidResponseError("No responses provided")

        if len(responses) != 20:
            raise InvalidResponseError(f"Expected 20 responses, got {len(responses)}")

        for i, response in enumerate(responses):
            if not isinstance(response, dict):
                raise InvalidResponseError(f"Response {i} is not a dictionary")

            if 'question_id' not in response:
                raise InvalidResponseError(f"Response {i} missing 'question_id'")

            if 'score' not in response:
                raise InvalidResponseError(f"Response {i} missing 'score'")

            question_id = response['question_id']
            score = response['score']

            if not isinstance(question_id, int) or question_id < 1 or question_id > 20:
                raise InvalidResponseError(f"Invalid question_id: {question_id}")

            if not isinstance(score, (int, float)) or score < 1 or score > 5:
                raise InvalidResponseError(f"Invalid score for question {question_id}: {score}")

    def _calculate_dimension_scores(self, indexed_responses: Dict[int, int]) -> Dict[str, List[float]]:
        """Calculate scores for each Big Five dimension"""
        dimension_scores = {
            "openness": [],
            "conscientiousness": [],
            "extraversion": [],
            "agreeableness": [],
            "neuroticism": []
        }

        for question_id, score in indexed_responses.items():
            if question_id not in self.item_mapping:
                continue

            item_info = self.item_mapping[question_id]
            dimension = item_info["dimension"]
            reverse = item_info["reverse"]

            # Apply reverse coding if needed
            if reverse:
                adjusted_score = 6 - score  # Reverse 1-5 scale
            else:
                adjusted_score = score

            dimension_scores[dimension].append(adjusted_score)

        return dimension_scores

    def _calculate_percentiles(self, raw_scores: Dict[str, float]) -> Dict[str, float]:
        """Calculate percentile scores based on population norms"""
        percentiles = {}

        for dimension, score in raw_scores.items():
            if dimension in self.norms:
                norm = self.norms[dimension]
                # Simple z-score to percentile conversion (approximate)
                z_score = (score - norm["mean"]) / norm["std"]
                # Convert z-score to percentile (simplified)
                percentile = max(1, min(99, 50 + (z_score * 15)))
                percentiles[dimension] = round(percentile, 1)
            else:
                percentiles[dimension] = 50.0  # Default to 50th percentile

        return percentiles

    def get_item_mapping(self) -> Dict[int, Dict[str, Any]]:
        """Get the item to dimension mapping"""
        return self.item_mapping.copy()

    def get_dimension_descriptions(self) -> Dict[str, str]:
        """Get descriptions for each personality dimension"""
        return {
            "openness": "創新思考與藝術欣賞能力",
            "conscientiousness": "組織能力與責任感",
            "extraversion": "社交性與活力",
            "agreeableness": "合作性與信任度",
            "neuroticism": "情緒穩定性與壓力反應"
        }