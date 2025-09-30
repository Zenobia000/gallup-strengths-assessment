"""
Report Generation System - Gallup Strengths Assessment

This module provides comprehensive PDF report generation services that transform
assessment results into professional, actionable reports for users and coaches.

Key Components:
- ReportGenerator: Main PDF generation orchestration
- ReportTemplate: Professional report layout and styling
- ChartRenderer: Data visualization for strengths and scores
- ShareLinkManager: One-time secure share link generation

Design Philosophy:
Following Linus Torvalds' principles - simple, fast, and reliable.
<1 second PDF generation, professional output, no unnecessary complexity.
"""

from .report_generator import ReportGenerator, get_report_generator
from .report_template import ReportTemplate, ReportSection
from .chart_renderer import ChartRenderer, ChartType
from .share_link import ShareLinkManager, ShareLink

__all__ = [
    'ReportGenerator',
    'get_report_generator',
    'ReportTemplate',
    'ReportSection',
    'ChartRenderer',
    'ChartType',
    'ShareLinkManager',
    'ShareLink'
]

__version__ = '1.0.0'