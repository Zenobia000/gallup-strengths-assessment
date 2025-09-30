"""
Report Template - Professional PDF Layout System

This module defines the structure and styling for PDF reports, following
professional document design principles while maintaining simplicity.

Design Philosophy:
Clean layout, consistent typography, clear visual hierarchy.
Following the principle of "good taste" - eliminate special cases,
make the common case beautiful and efficient.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, Image, KeepTogether
)
from reportlab.pdfgen import canvas


class ReportSection(Enum):
    """Report section types."""
    COVER = "cover"
    EXECUTIVE_SUMMARY = "executive_summary"
    STRENGTH_PROFILE = "strength_profile"
    DOMAIN_ANALYSIS = "domain_analysis"
    CAREER_RECOMMENDATIONS = "career_recommendations"
    DEVELOPMENT_PLAN = "development_plan"
    METHODOLOGY = "methodology"
    APPENDIX = "appendix"


@dataclass
class ReportConfig:
    """Configuration for report generation."""
    page_size: tuple = A4
    margin_left: float = 25 * mm
    margin_right: float = 25 * mm
    margin_top: float = 25 * mm
    margin_bottom: float = 25 * mm

    # Colors (professional palette)
    primary_color: tuple = (0.2, 0.4, 0.6)  # RGB: Professional blue
    secondary_color: tuple = (0.3, 0.6, 0.8)  # RGB: Light blue
    accent_color: tuple = (0.9, 0.5, 0.2)  # RGB: Warm orange
    success_color: tuple = (0.2, 0.7, 0.4)  # RGB: Green
    warning_color: tuple = (0.9, 0.7, 0.2)  # RGB: Yellow
    text_color: tuple = (0.2, 0.2, 0.2)  # RGB: Dark gray

    # Typography
    font_family: str = "Helvetica"
    title_font_size: int = 24
    heading1_font_size: int = 18
    heading2_font_size: int = 14
    heading3_font_size: int = 12
    body_font_size: int = 10
    caption_font_size: int = 8

    # Layout
    line_spacing: float = 1.2
    paragraph_spacing: float = 12
    section_spacing: float = 24


class ReportTemplate:
    """
    Professional report template with consistent styling.

    This class provides the structure and styling for generating
    professional PDF reports. It follows design best practices
    while maintaining code simplicity.
    """

    def __init__(self, config: Optional[ReportConfig] = None):
        """Initialize report template with configuration."""
        self.config = config or ReportConfig()
        self.styles = self._create_styles()

    def _create_styles(self) -> Dict[str, ParagraphStyle]:
        """
        Create paragraph styles for the report.

        Returns consistent, professional styling throughout the document.
        Following the principle of "do one thing well" - this method
        defines all styles in one place.
        """
        base_styles = getSampleStyleSheet()

        styles = {
            # Title styles
            'ReportTitle': ParagraphStyle(
                'ReportTitle',
                parent=base_styles['Heading1'],
                fontName=f'{self.config.font_family}-Bold',
                fontSize=self.config.title_font_size,
                textColor=colors.Color(*self.config.primary_color),
                alignment=TA_CENTER,
                spaceAfter=self.config.section_spacing,
                leading=self.config.title_font_size * self.config.line_spacing
            ),

            # Heading styles
            'Heading1': ParagraphStyle(
                'Heading1',
                parent=base_styles['Heading1'],
                fontName=f'{self.config.font_family}-Bold',
                fontSize=self.config.heading1_font_size,
                textColor=colors.Color(*self.config.primary_color),
                spaceBefore=self.config.section_spacing,
                spaceAfter=self.config.paragraph_spacing,
                leading=self.config.heading1_font_size * self.config.line_spacing
            ),

            'Heading2': ParagraphStyle(
                'Heading2',
                parent=base_styles['Heading2'],
                fontName=f'{self.config.font_family}-Bold',
                fontSize=self.config.heading2_font_size,
                textColor=colors.Color(*self.config.secondary_color),
                spaceBefore=self.config.paragraph_spacing,
                spaceAfter=self.config.paragraph_spacing * 0.5,
                leading=self.config.heading2_font_size * self.config.line_spacing
            ),

            'Heading3': ParagraphStyle(
                'Heading3',
                parent=base_styles['Heading3'],
                fontName=f'{self.config.font_family}-Bold',
                fontSize=self.config.heading3_font_size,
                textColor=colors.Color(*self.config.text_color),
                spaceBefore=self.config.paragraph_spacing * 0.5,
                spaceAfter=self.config.paragraph_spacing * 0.3,
                leading=self.config.heading3_font_size * self.config.line_spacing
            ),

            # Body text styles
            'Body': ParagraphStyle(
                'Body',
                parent=base_styles['Normal'],
                fontName=self.config.font_family,
                fontSize=self.config.body_font_size,
                textColor=colors.Color(*self.config.text_color),
                alignment=TA_JUSTIFY,
                spaceAfter=self.config.paragraph_spacing * 0.5,
                leading=self.config.body_font_size * self.config.line_spacing
            ),

            'BodyBold': ParagraphStyle(
                'BodyBold',
                parent=base_styles['Normal'],
                fontName=f'{self.config.font_family}-Bold',
                fontSize=self.config.body_font_size,
                textColor=colors.Color(*self.config.text_color),
                alignment=TA_LEFT,
                spaceAfter=self.config.paragraph_spacing * 0.5,
                leading=self.config.body_font_size * self.config.line_spacing
            ),

            # Special styles
            'Caption': ParagraphStyle(
                'Caption',
                parent=base_styles['Normal'],
                fontName=f'{self.config.font_family}-Oblique',
                fontSize=self.config.caption_font_size,
                textColor=colors.gray,
                alignment=TA_CENTER,
                spaceAfter=self.config.paragraph_spacing * 0.3
            ),

            'Bullet': ParagraphStyle(
                'Bullet',
                parent=base_styles['Normal'],
                fontName=self.config.font_family,
                fontSize=self.config.body_font_size,
                textColor=colors.Color(*self.config.text_color),
                leftIndent=20,
                bulletIndent=10,
                spaceAfter=6,
                leading=self.config.body_font_size * self.config.line_spacing
            ),

            'Quote': ParagraphStyle(
                'Quote',
                parent=base_styles['Normal'],
                fontName=f'{self.config.font_family}-Oblique',
                fontSize=self.config.body_font_size,
                textColor=colors.Color(*self.config.secondary_color),
                leftIndent=20,
                rightIndent=20,
                spaceBefore=self.config.paragraph_spacing * 0.5,
                spaceAfter=self.config.paragraph_spacing * 0.5,
                leading=self.config.body_font_size * self.config.line_spacing
            ),

            # Footer style
            'Footer': ParagraphStyle(
                'Footer',
                parent=base_styles['Normal'],
                fontName=self.config.font_family,
                fontSize=self.config.caption_font_size,
                textColor=colors.gray,
                alignment=TA_CENTER
            )
        }

        return styles

    def create_table_style(self, header: bool = True) -> TableStyle:
        """
        Create table style for data presentation.

        Args:
            header: Whether the table has a header row

        Returns:
            TableStyle with professional formatting
        """
        style_commands = [
            # Grid and borders
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('BOX', (0, 0), (-1, -1), 1, colors.Color(*self.config.primary_color)),

            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),

            # Alignment
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]

        if header:
            # Header row styling
            style_commands.extend([
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(*self.config.primary_color)),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), f'{self.config.font_family}-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), self.config.body_font_size),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ])

            # Alternating row colors
            style_commands.extend([
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.95, 0.95)]),
            ])

        return TableStyle(style_commands)

    def create_strength_badge_style(self, strength_level: str) -> Dict[str, Any]:
        """
        Create styling for strength level badges.

        Args:
            strength_level: "high", "medium", or "low"

        Returns:
            Dictionary with color and label styling
        """
        badge_styles = {
            "high": {
                "color": colors.Color(*self.config.success_color),
                "label": "高",
                "bg_color": colors.Color(0.9, 0.98, 0.9)
            },
            "medium": {
                "color": colors.Color(*self.config.accent_color),
                "label": "中",
                "bg_color": colors.Color(0.99, 0.97, 0.9)
            },
            "low": {
                "color": colors.Color(*self.config.warning_color),
                "label": "待發展",
                "bg_color": colors.Color(0.99, 0.95, 0.9)
            }
        }

        return badge_styles.get(strength_level, badge_styles["medium"])

    def add_page_number(self, canvas_obj: canvas.Canvas, doc: SimpleDocTemplate):
        """
        Add page numbers to PDF pages.

        Args:
            canvas_obj: ReportLab canvas object
            doc: SimpleDocTemplate document
        """
        page_num = canvas_obj.getPageNumber()
        text = f"第 {page_num} 頁"

        canvas_obj.saveState()
        canvas_obj.setFont(self.config.font_family, self.config.caption_font_size)
        canvas_obj.setFillColor(colors.gray)
        canvas_obj.drawCentredString(
            doc.pagesize[0] / 2,
            self.config.margin_bottom / 2,
            text
        )
        canvas_obj.restoreState()

    def add_watermark(self, canvas_obj: canvas.Canvas, doc: SimpleDocTemplate, text: str = "機密"):
        """
        Add watermark to PDF pages.

        Args:
            canvas_obj: ReportLab canvas object
            doc: SimpleDocTemplate document
            text: Watermark text
        """
        canvas_obj.saveState()
        canvas_obj.setFont(f'{self.config.font_family}-Bold', 60)
        canvas_obj.setFillColor(colors.Color(0.9, 0.9, 0.9, alpha=0.3))
        canvas_obj.translate(doc.pagesize[0] / 2, doc.pagesize[1] / 2)
        canvas_obj.rotate(45)
        canvas_obj.drawCentredString(0, 0, text)
        canvas_obj.restoreState()

    def get_page_size(self) -> tuple:
        """Get configured page size."""
        return self.config.page_size

    def get_margins(self) -> Dict[str, float]:
        """Get configured margins."""
        return {
            "left": self.config.margin_left,
            "right": self.config.margin_right,
            "top": self.config.margin_top,
            "bottom": self.config.margin_bottom
        }
