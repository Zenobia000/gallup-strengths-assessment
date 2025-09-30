"""
PDF Report Generator - Complete PDF Generation System

This module provides the complete PDF generation system that orchestrates
all report components to produce professional, personalized assessment reports.

Key Components:
- PDFReportGenerator: Main PDF generation orchestrator
- ReportBuilder: Coordinates content generation and PDF assembly
- OutputManager: Handles file output and sharing

Design Philosophy:
Following Clean Architecture with clear separation of concerns.
Each component has a single responsibility and provides testable interfaces.

Integration Points:
- ContentGenerator: Business logic and content creation
- ReportTemplate: PDF styling and layout
- ChartRenderer: Data visualization components
- ShareLinkManager: Report sharing and access control

Author: TaskMaster Agent (3.4.3)
Date: 2025-09-30
Version: 1.0
"""

import os
import io
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import uuid
import tempfile

from reportlab.platypus import SimpleDocTemplate, PageBreak
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

from core.scoring import DimensionScores
from models.schemas import QuestionResponse
from .content_generator import ContentGenerator, ReportContent, ContentType
from .report_template import ReportTemplate, ReportConfig
from .chart_renderer import ChartRenderer
from .share_link import ShareLinkManager


@dataclass
class PDFGenerationOptions:
    """Options for PDF generation."""
    include_charts: bool = True
    include_watermark: bool = False
    watermark_text: str = "機密"
    include_page_numbers: bool = True
    output_format: str = "pdf"  # Future: support for HTML, etc.
    quality: str = "high"  # "draft", "standard", "high"

    def __post_init__(self):
        """Validate options after initialization."""
        valid_formats = ["pdf"]
        if self.output_format not in valid_formats:
            raise ValueError(f"Unsupported output format: {self.output_format}")

        valid_qualities = ["draft", "standard", "high"]
        if self.quality not in valid_qualities:
            raise ValueError(f"Invalid quality setting: {self.quality}")


@dataclass
class GenerationResult:
    """Result of PDF generation process."""
    success: bool
    file_path: Optional[str]
    file_size_bytes: Optional[int]
    generation_time_seconds: float
    report_id: str
    error_message: Optional[str] = None
    warnings: List[str] = None

    def __post_init__(self):
        """Initialize warnings if not provided."""
        if self.warnings is None:
            self.warnings = []


class ReportBuilder:
    """
    Coordinates content generation and PDF assembly.

    This class bridges the content generation logic with the PDF creation
    process, ensuring proper integration of all components.
    """

    def __init__(self, config: Optional[ReportConfig] = None):
        """Initialize builder with configuration."""
        self.config = config or ReportConfig()
        self.content_generator = ContentGenerator(self.config)
        self.template = ReportTemplate(self.config)
        self.chart_renderer = ChartRenderer()

    def build_pdf_elements(
        self,
        report_content: ReportContent,
        options: PDFGenerationOptions
    ) -> List[Any]:
        """
        Build complete list of PDF elements from report content.

        Args:
            report_content: Generated report content
            options: PDF generation options

        Returns:
            List of ReportLab flowable elements
        """
        elements = []

        for section in report_content.sections:
            # Add section elements
            elements.extend(section.content_elements)

            # Add charts if requested and section supports them
            if options.include_charts:
                chart_elements = self._generate_section_charts(
                    section, report_content.metadata
                )
                elements.extend(chart_elements)

            # Add page break after major sections (except last)
            if section != report_content.sections[-1]:
                if section.section_type in [
                    ContentType.COVER_PAGE,
                    ContentType.EXECUTIVE_SUMMARY,
                    ContentType.STRENGTH_ANALYSIS,
                    ContentType.CAREER_RECOMMENDATIONS
                ]:
                    elements.append(PageBreak())

        return elements

    def _generate_section_charts(
        self,
        section: Any,
        report_metadata: Dict[str, Any]
    ) -> List[Any]:
        """Generate charts for specific sections."""
        chart_elements = []

        # Generate charts based on section type
        if section.section_type == ContentType.STRENGTH_ANALYSIS:
            chart_elements.extend(
                self._create_strength_charts(report_metadata)
            )
        elif section.section_type == ContentType.PERSONALITY_PROFILE:
            chart_elements.extend(
                self._create_personality_charts(report_metadata)
            )

        return chart_elements

    def _create_strength_charts(self, metadata: Dict[str, Any]) -> List[Any]:
        """Create strength-related charts."""
        charts = []

        if "recommendation_result" in metadata:
            recommendation_result = metadata["recommendation_result"]
            strength_profile = recommendation_result.strength_profile

            # Top 5 strengths radar chart
            if hasattr(strength_profile, 'top_5_strengths') and strength_profile.top_5_strengths:
                chart_data = {
                    s.theme.chinese_name: s.score
                    for s in strength_profile.top_5_strengths
                }
                radar_chart = self.chart_renderer.create_radar_chart(
                    chart_data,
                    title="前五項核心優勢",
                    width=120*mm,
                    height=100*mm
                )
                charts.append(radar_chart)

            # Domain distribution pie chart
            if hasattr(strength_profile, 'domain_distribution'):
                domain_names = {
                    "executing": "執行力",
                    "influencing": "影響力",
                    "relationship_building": "關係建立",
                    "strategic_thinking": "戰略思維"
                }

                pie_data = []
                for domain, value in strength_profile.domain_distribution.items():
                    domain_name = domain_names.get(domain.value, domain.value)
                    pie_data.append((domain_name, value))

                pie_chart = self.chart_renderer.create_pie_chart(
                    pie_data,
                    title="優勢領域分布",
                    width=100*mm,
                    height=80*mm
                )
                charts.append(pie_chart)

        return charts

    def _create_personality_charts(self, metadata: Dict[str, Any]) -> List[Any]:
        """Create personality-related charts."""
        charts = []

        if "big_five_scores" in metadata:
            big_five_scores = metadata["big_five_scores"]

            # Big Five bar chart
            dimension_names = {
                "openness": "開放性",
                "conscientiousness": "嚴謹性",
                "extraversion": "外向性",
                "agreeableness": "親和性",
                "neuroticism": "情緒穩定性"
            }

            chart_data = []
            for dimension, score in big_five_scores.items():
                name = dimension_names.get(dimension, dimension)
                chart_data.append((name, score))

            bar_chart = self.chart_renderer.create_bar_chart(
                chart_data,
                title="Big Five 人格特質分數",
                width=140*mm,
                height=80*mm,
                x_axis_label="人格維度",
                y_axis_label="分數"
            )
            charts.append(bar_chart)

        return charts


class OutputManager:
    """
    Handles file output and sharing functionality.

    This class manages the final output of generated PDFs, including
    file storage, temporary file handling, and sharing link generation.
    """

    def __init__(self, share_manager: Optional[ShareLinkManager] = None):
        """Initialize output manager."""
        self.share_manager = share_manager or ShareLinkManager()

    def save_pdf_to_file(
        self,
        pdf_buffer: io.BytesIO,
        filename: Optional[str] = None,
        output_dir: Optional[str] = None
    ) -> Tuple[str, int]:
        """
        Save PDF buffer to file.

        Args:
            pdf_buffer: PDF content buffer
            filename: Optional filename (auto-generated if None)
            output_dir: Output directory (temp dir if None)

        Returns:
            Tuple of (file_path, file_size_bytes)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"strength_report_{timestamp}.pdf"

        if output_dir is None:
            output_dir = tempfile.gettempdir()

        output_path = os.path.join(output_dir, filename)

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Write PDF buffer to file
        pdf_buffer.seek(0)
        with open(output_path, 'wb') as f:
            content = pdf_buffer.read()
            f.write(content)
            file_size = len(content)

        return output_path, file_size

    def create_shareable_link(
        self,
        file_path: str,
        user_name: str,
        expiry_hours: int = 72
    ) -> str:
        """
        Create shareable link for PDF report.

        Args:
            file_path: Path to PDF file
            user_name: Name of report recipient
            expiry_hours: Link expiry time in hours

        Returns:
            Shareable link URL
        """
        # Read file for sharing
        with open(file_path, 'rb') as f:
            file_content = f.read()

        # Generate share link
        share_result = self.share_manager.create_share_link(
            file_content=file_content,
            file_name=os.path.basename(file_path),
            recipient_name=user_name,
            expiry_hours=expiry_hours
        )

        return share_result.share_url

    def cleanup_temporary_files(self, file_paths: List[str]) -> None:
        """
        Clean up temporary files.

        Args:
            file_paths: List of file paths to delete
        """
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                # Log warning but don't fail
                print(f"Warning: Could not delete temporary file {file_path}: {e}")


class PDFReportGenerator:
    """
    Main PDF report generator orchestrating all components.

    This is the primary interface for generating complete PDF reports
    from assessment results. It coordinates content generation, PDF creation,
    and output management.
    """

    def __init__(
        self,
        config: Optional[ReportConfig] = None,
        share_manager: Optional[ShareLinkManager] = None
    ):
        """
        Initialize PDF report generator.

        Args:
            config: Report configuration
            share_manager: Share link manager for report sharing
        """
        self.config = config or ReportConfig()
        self.report_builder = ReportBuilder(self.config)
        self.output_manager = OutputManager(share_manager)

    def generate_report_from_responses(
        self,
        responses: List[QuestionResponse],
        user_name: str,
        assessment_date: Optional[datetime] = None,
        user_context: Optional[Dict[str, Any]] = None,
        options: Optional[PDFGenerationOptions] = None
    ) -> GenerationResult:
        """
        Generate complete PDF report from assessment responses.

        Args:
            responses: List of question responses
            user_name: Name of the user
            assessment_date: Date of assessment
            user_context: Additional user context
            options: PDF generation options

        Returns:
            GenerationResult with file path and metadata
        """
        start_time = datetime.now()
        options = options or PDFGenerationOptions()

        try:
            # Convert responses to Big Five scores
            from core.scoring import ScoringEngine
            scoring_engine = ScoringEngine()

            # Convert QuestionResponse to API format
            response_values = [0] * 20  # Initialize with zeros
            for response in responses:
                response_values[response.question_id - 1] = response.score

            # Calculate scores
            scores_dict = scoring_engine.calculate_scores_from_api(
                response_values, scale_type="5-point"
            )

            # Create DimensionScores object
            dimension_scores = scoring_engine.create_dimension_scores_object(scores_dict)

            return self.generate_report_from_scores(
                dimension_scores,
                user_name,
                assessment_date,
                user_context,
                options
            )

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            return GenerationResult(
                success=False,
                file_path=None,
                file_size_bytes=None,
                generation_time_seconds=duration,
                report_id=str(uuid.uuid4()),
                error_message=f"Failed to generate report from responses: {str(e)}"
            )

    def generate_report_from_scores(
        self,
        big_five_scores: DimensionScores,
        user_name: str,
        assessment_date: Optional[datetime] = None,
        user_context: Optional[Dict[str, Any]] = None,
        options: Optional[PDFGenerationOptions] = None
    ) -> GenerationResult:
        """
        Generate complete PDF report from Big Five scores.

        Args:
            big_five_scores: Big Five personality dimension scores
            user_name: Name of the user
            assessment_date: Date of assessment
            user_context: Additional user context
            options: PDF generation options

        Returns:
            GenerationResult with file path and metadata
        """
        start_time = datetime.now()
        options = options or PDFGenerationOptions()
        warnings = []

        try:
            # Generate report content
            report_content = self.report_builder.content_generator.generate_complete_report_content(
                big_five_scores,
                user_name,
                assessment_date,
                user_context
            )

            # Create PDF document
            pdf_buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=self.config.page_size,
                leftMargin=self.config.margin_left,
                rightMargin=self.config.margin_right,
                topMargin=self.config.margin_top,
                bottomMargin=self.config.margin_bottom
            )

            # Build PDF elements
            story = self.report_builder.build_pdf_elements(report_content, options)

            # Build PDF with custom page template
            if options.include_page_numbers or options.include_watermark:
                doc.build(story, onFirstPage=self._create_page_template(options),
                         onLaterPages=self._create_page_template(options))
            else:
                doc.build(story)

            # Save to file
            file_path, file_size = self.output_manager.save_pdf_to_file(pdf_buffer)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            return GenerationResult(
                success=True,
                file_path=file_path,
                file_size_bytes=file_size,
                generation_time_seconds=duration,
                report_id=report_content.report_id,
                warnings=warnings
            )

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            return GenerationResult(
                success=False,
                file_path=None,
                file_size_bytes=None,
                generation_time_seconds=duration,
                report_id=str(uuid.uuid4()),
                error_message=f"Failed to generate PDF report: {str(e)}"
            )

    def generate_and_share_report(
        self,
        big_five_scores: DimensionScores,
        user_name: str,
        assessment_date: Optional[datetime] = None,
        user_context: Optional[Dict[str, Any]] = None,
        options: Optional[PDFGenerationOptions] = None,
        expiry_hours: int = 72
    ) -> Tuple[GenerationResult, Optional[str]]:
        """
        Generate PDF report and create shareable link.

        Args:
            big_five_scores: Big Five personality dimension scores
            user_name: Name of the user
            assessment_date: Date of assessment
            user_context: Additional user context
            options: PDF generation options
            expiry_hours: Share link expiry time

        Returns:
            Tuple of (GenerationResult, share_url)
        """
        # Generate report
        result = self.generate_report_from_scores(
            big_five_scores,
            user_name,
            assessment_date,
            user_context,
            options
        )

        share_url = None
        if result.success and result.file_path:
            try:
                share_url = self.output_manager.create_shareable_link(
                    result.file_path,
                    user_name,
                    expiry_hours
                )
            except Exception as e:
                result.warnings.append(f"Failed to create share link: {str(e)}")

        return result, share_url

    def _create_page_template(self, options: PDFGenerationOptions):
        """Create page template function for headers/footers."""
        def page_template(canvas_obj, doc):
            # Add page numbers
            if options.include_page_numbers:
                self.report_builder.template.add_page_number(canvas_obj, doc)

            # Add watermark
            if options.include_watermark:
                self.report_builder.template.add_watermark(
                    canvas_obj, doc, options.watermark_text
                )

        return page_template

    def get_generation_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the generation process.

        Returns:
            Dictionary with generation statistics
        """
        return {
            "version": "1.0",
            "components": {
                "content_generator": "ContentGenerator v1.0",
                "report_template": "ReportTemplate v1.0",
                "chart_renderer": "ChartRenderer v1.0",
                "share_manager": "ShareLinkManager v1.0"
            },
            "supported_formats": ["pdf"],
            "supported_qualities": ["draft", "standard", "high"],
            "default_config": {
                "page_size": "A4",
                "margins": f"{self.config.margin_left}mm",
                "font_family": self.config.font_family
            }
        }

    def cleanup_temp_files(self, generation_result: GenerationResult) -> None:
        """
        Clean up temporary files created during generation.

        Args:
            generation_result: Result from PDF generation
        """
        if generation_result.file_path:
            self.output_manager.cleanup_temporary_files([generation_result.file_path])


def create_pdf_generator(
    config: Optional[ReportConfig] = None,
    share_manager: Optional[ShareLinkManager] = None
) -> PDFReportGenerator:
    """
    Factory function to create a configured PDF generator.

    Args:
        config: Optional report configuration
        share_manager: Optional share link manager

    Returns:
        Configured PDFReportGenerator instance
    """
    return PDFReportGenerator(config, share_manager)


# Convenience function for quick report generation
def generate_quick_report(
    responses: List[QuestionResponse],
    user_name: str,
    output_path: Optional[str] = None
) -> str:
    """
    Quick report generation function for simple use cases.

    Args:
        responses: List of question responses
        user_name: Name of the user
        output_path: Optional output file path

    Returns:
        Path to generated PDF file

    Raises:
        Exception: If report generation fails
    """
    generator = create_pdf_generator()
    result = generator.generate_report_from_responses(responses, user_name)

    if not result.success:
        raise Exception(f"Report generation failed: {result.error_message}")

    if output_path and result.file_path:
        # Move file to desired location
        import shutil
        shutil.move(result.file_path, output_path)
        return output_path

    return result.file_path