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

from .pdf_generator import PDFReportGenerator, create_pdf_generator
from .content_generator import ContentGenerator, PersonalizedContentGenerator, ReportStructureBuilder
from .report_template import ReportTemplate, ReportSection
from .chart_renderer import ChartRenderer, ChartType
from .share_link import ShareLinkManager, ShareLink
from .cache_manager import ReportCacheManager, CacheConfiguration, get_report_cache_manager

__all__ = [
    'PDFReportGenerator',
    'create_pdf_generator',
    'ContentGenerator',
    'PersonalizedContentGenerator',
    'ReportStructureBuilder',
    'ReportTemplate',
    'ReportSection',
    'ChartRenderer',
    'ChartType',
    'ShareLinkManager',
    'ShareLink',
    'ReportCacheManager',
    'CacheConfiguration',
    'get_report_cache_manager'
]

__version__ = '1.0.0'