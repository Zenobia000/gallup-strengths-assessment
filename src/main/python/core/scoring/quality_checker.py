"""
Response Quality Checker - Simplified version for file storage
"""

from typing import List, Dict, Any


class ResponseQualityChecker:
    """Simplified quality checker for rapid development"""

    def check_response_quality(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check response quality - simplified version
        """
        if not responses:
            return {
                "overall_quality": "poor",
                "overall_quality_score": 0.0,
                "issues": ["No responses provided"]
            }

        issues = []

        # Basic checks
        total_responses = len(responses)
        valid_responses = 0

        for response in responses:
            if response.get("most_like") and response.get("least_like"):
                valid_responses += 1
            else:
                issues.append("Incomplete response found")

        completion_rate = valid_responses / total_responses if total_responses > 0 else 0

        # Determine quality
        if completion_rate >= 0.9:
            quality = "excellent"
            score = 0.9 + (completion_rate - 0.9)
        elif completion_rate >= 0.7:
            quality = "good"
            score = 0.7 + (completion_rate - 0.7) * 2
        elif completion_rate >= 0.5:
            quality = "acceptable"
            score = 0.5 + (completion_rate - 0.5) * 4
        else:
            quality = "poor"
            score = completion_rate

        return {
            "overall_quality": quality,
            "overall_quality_score": score,
            "completion_rate": completion_rate,
            "total_responses": total_responses,
            "valid_responses": valid_responses,
            "issues": issues
        }