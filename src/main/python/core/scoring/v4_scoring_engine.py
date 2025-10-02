"""
V4 Scoring Engine - Simplified version for file storage
"""

from typing import List, Dict, Any
import random
import time


class V4ScoringEngine:
    """Simplified scoring engine for rapid development"""

    def __init__(self):
        self.dimensions = [
            "structured_execution",
            "quality_perfectionism",
            "exploration_innovation",
            "analytical_insight",
            "influence_advocacy",
            "collaboration_harmony",
            "customer_orientation",
            "learning_growth",
            "discipline_trust",
            "pressure_regulation",
            "conflict_integration",
            "responsibility_accountability"
        ]

    def score_assessment(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Score assessment responses - simplified version
        """
        start_time = time.time()

        if not responses:
            raise ValueError("No responses to score")

        # Simplified scoring: count preferences per dimension
        dimension_counts = {dim: 0 for dim in self.dimensions}

        # Mock scoring based on response patterns
        for response in responses:
            most_like = response.get("most_like", "")
            least_like = response.get("least_like", "")

            # Extract dimension from statement ID (e.g., T1001 -> T1)
            if most_like:
                dim_id = most_like[:2]  # T1, T2, etc.
                if dim_id in ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10", "T11", "T12"]:
                    dim_index = int(dim_id[1:]) - 1
                    if 0 <= dim_index < len(self.dimensions):
                        dimension_counts[self.dimensions[dim_index]] += 2

            if least_like:
                dim_id = least_like[:2]
                if dim_id in ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10", "T11", "T12"]:
                    dim_index = int(dim_id[1:]) - 1
                    if 0 <= dim_index < len(self.dimensions):
                        dimension_counts[self.dimensions[dim_index]] -= 1

        # Convert to percentiles (simplified)
        max_count = max(dimension_counts.values()) if dimension_counts.values() else 1
        min_count = min(dimension_counts.values()) if dimension_counts.values() else 0
        range_count = max_count - min_count if max_count > min_count else 1

        dimension_scores = {}
        theta_estimates = {}
        for i, (dim, count) in enumerate(dimension_counts.items()):
            # Normalize to 0-100 scale
            percentile = ((count - min_count) / range_count) * 60 + 20  # 20-80 range
            dimension_scores[dim] = round(percentile, 1)

            # Mock theta estimates
            theta_estimates[f"T{i+1}"] = round((percentile - 50) / 20, 1)  # -1.5 to 1.5 range

        # Categorize talents
        sorted_dims = sorted(dimension_scores.items(), key=lambda x: x[1], reverse=True)
        dominant_talents = [dim for dim, score in sorted_dims[:4]]
        supporting_talents = [dim for dim, score in sorted_dims[4:8]]
        lesser_talents = [dim for dim, score in sorted_dims[8:]]

        computation_time = (time.time() - start_time) * 1000

        return {
            "dimension_scores": dimension_scores,
            "theta_estimates": theta_estimates,
            "standard_errors": {f"t{i+1}": round(0.3 + random.random() * 0.2, 4) for i in range(12)},
            "overall_confidence": 0.85 + random.random() * 0.1,
            "dimension_reliability": {f"t{i+1}": 0.87 for i in range(12)},
            "dominant_talents": dominant_talents,
            "supporting_talents": supporting_talents,
            "lesser_talents": lesser_talents,
            "computation_time_ms": round(computation_time, 1)
        }