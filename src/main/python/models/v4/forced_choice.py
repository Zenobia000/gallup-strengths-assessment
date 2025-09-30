"""
Forced-choice data structures for Thurstonian IRT model
Version: 4.0 Prototype
Date: 2025-09-30
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from enum import Enum


class ResponseType(Enum):
    """Response type for forced-choice items"""
    MOST_LIKE = "most_like"
    LEAST_LIKE = "least_like"


@dataclass
class Statement:
    """Individual statement in a forced-choice block"""
    statement_id: str
    text: str
    dimension: str  # One of 12 strength dimensions
    factor_loading: float  # Item factor loading (λ)
    social_desirability: float  # Social desirability rating

    def __hash__(self):
        return hash(self.statement_id)


@dataclass
class QuartetBlock:
    """Four-statement forced-choice block"""
    block_id: int
    statements: List[Statement]
    dimensions: List[str]  # List of dimensions covered

    def __post_init__(self):
        if len(self.statements) != 4:
            raise ValueError(f"Quartet block must have exactly 4 statements, got {len(self.statements)}")
        self.dimensions = [stmt.dimension for stmt in self.statements]

    def get_statement_by_index(self, index: int) -> Statement:
        """Get statement by position index (0-3)"""
        if 0 <= index < 4:
            return self.statements[index]
        raise IndexError(f"Statement index must be 0-3, got {index}")


@dataclass
class ForcedChoiceResponse:
    """Single response to a forced-choice block"""
    block_id: int
    most_like_index: int  # Index of "most like me" statement (0-3)
    least_like_index: int  # Index of "least like me" statement (0-3)
    response_time_ms: Optional[int] = None

    def __post_init__(self):
        if self.most_like_index == self.least_like_index:
            raise ValueError("Most and least like indices cannot be the same")
        if not (0 <= self.most_like_index < 4):
            raise ValueError(f"Most like index must be 0-3, got {self.most_like_index}")
        if not (0 <= self.least_like_index < 4):
            raise ValueError(f"Least like index must be 0-3, got {self.least_like_index}")


@dataclass
class ForcedChoiceBlockResponse:
    """Complete response data for a forced-choice assessment"""
    session_id: str
    participant_id: str
    responses: List[ForcedChoiceResponse]
    blocks: List[QuartetBlock]
    start_time: datetime
    end_time: Optional[datetime] = None
    total_response_time_ms: Optional[int] = None

    def get_response_for_block(self, block_id: int) -> Optional[ForcedChoiceResponse]:
        """Get response for a specific block"""
        for response in self.responses:
            if response.block_id == block_id:
                return response
        return None

    def get_selected_statements(self, block_id: int) -> Optional[Tuple[Statement, Statement]]:
        """Get the selected most/least like statements for a block"""
        response = self.get_response_for_block(block_id)
        if not response:
            return None

        block = next((b for b in self.blocks if b.block_id == block_id), None)
        if not block:
            return None

        most_like = block.statements[response.most_like_index]
        least_like = block.statements[response.least_like_index]
        return (most_like, least_like)

    def to_irt_format(self) -> List[Dict]:
        """Convert responses to format expected by IRT scorer"""
        irt_data = []
        for response in self.responses:
            irt_data.append({
                'block_id': response.block_id,
                'most_like': response.most_like_index,
                'least_like': response.least_like_index,
                'response_time': response.response_time_ms
            })
        return irt_data

    @property
    def completion_rate(self) -> float:
        """Calculate assessment completion rate"""
        if not self.blocks:
            return 0.0
        return len(self.responses) / len(self.blocks)

    @property
    def dimension_coverage(self) -> Dict[str, int]:
        """Count how many times each dimension appears in responses"""
        coverage = {}
        for response in self.responses:
            block = next((b for b in self.blocks if b.block_id == response.block_id), None)
            if block:
                for dim in block.dimensions:
                    coverage[dim] = coverage.get(dim, 0) + 1
        return coverage


@dataclass
class IRTParameters:
    """Pre-calibrated IRT parameters for the assessment"""
    item_parameters: Dict[str, Dict]  # Statement ID -> parameters
    block_parameters: Dict[int, Dict]  # Block ID -> parameters
    dimension_thresholds: Dict[str, float]  # Dimension -> threshold
    normative_data: Dict[str, Dict]  # Normative statistics
    calibration_sample_size: int
    calibration_date: datetime
    model_version: str = "4.0-prototype"