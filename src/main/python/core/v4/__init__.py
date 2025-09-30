"""
Thurstonian IRT Model Implementation (v4.0 Prototype)

This module implements the forced-choice assessment system using
Thurstonian Item Response Theory to overcome ipsative data limitations.
"""

from .irt_scorer import ThurstonianIRTScorer, ThetaEstimate, NormativeScores
from .block_designer import QuartetBlockDesigner, BlockDesignCriteria

__version__ = '4.0-prototype'

__all__ = [
    'ThurstonianIRTScorer',
    'ThetaEstimate',
    'NormativeScores',
    'QuartetBlockDesigner',
    'BlockDesignCriteria'
]