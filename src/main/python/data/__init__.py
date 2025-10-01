"""
Data module for the Strength Assessment System

This module contains data definitions and configurations.
"""

from .v4_statements import STATEMENT_POOL, DIMENSION_MAPPING, get_all_statements

__all__ = [
    'STATEMENT_POOL',
    'DIMENSION_MAPPING',
    'get_all_statements'
]