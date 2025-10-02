"""
Assessment Core Module
評測核心模組，基於文件存儲的評測系統

Author: Claude Code AI
Date: 2025-10-02
Version: 1.0
"""

from .file_based_engine import (
    FileBasedAssessmentEngine,
    AssessmentResult,
    TalentScore,
    DomainScore,
    BalanceMetrics,
    ArchetypeClassification
)

__all__ = [
    "FileBasedAssessmentEngine",
    "AssessmentResult",
    "TalentScore",
    "DomainScore",
    "BalanceMetrics",
    "ArchetypeClassification"
]