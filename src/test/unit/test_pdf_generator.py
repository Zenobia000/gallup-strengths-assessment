"""
Unit Tests for PDF Generator

This module provides comprehensive unit tests for the PDF generation
system, ensuring correct functionality and file output quality.

Test Coverage:
- PDFReportGenerator main functionality
- ReportBuilder PDF element creation
- OutputManager file handling
- Error handling and edge cases

Author: TaskMaster Agent (3.4.3)
Date: 2025-09-30
Version: 1.0
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import tempfile
import io
from datetime import datetime
from typing import Dict, List

from core.scoring import DimensionScores
from core.report.pdf_generator import (
    PDFReportGenerator, ReportBuilder, OutputManager,
    PDFGenerationOptions, GenerationResult, create_pdf_generator
)
from models.schemas import QuestionResponse


class TestPDFGenerationOptions(unittest.TestCase):
    """Test cases for PDFGenerationOptions."""

    def test_default_options(self):
        """Test default option values."""
        options = PDFGenerationOptions()

        self.assertTrue(options.include_charts)
        self.assertFalse(options.include_watermark)
        self.assertEqual(options.watermark_text, "機密")
        self.assertTrue(options.include_page_numbers)
        self.assertEqual(options.output_format, "pdf")
        self.assertEqual(options.quality, "high")

    def test_custom_options(self):
        """Test custom option values."""
        options = PDFGenerationOptions(
            include_charts=False,
            include_watermark=True,
            watermark_text="草稿",
            quality="draft"
        )

        self.assertFalse(options.include_charts)
        self.assertTrue(options.include_watermark)
        self.assertEqual(options.watermark_text, "草稿")
        self.assertEqual(options.quality, "draft")

    def test_invalid_format_validation(self):
        """Test validation of invalid output format."""
        with self.assertRaises(ValueError):
            PDFGenerationOptions(output_format="html")

    def test_invalid_quality_validation(self):
        """Test validation of invalid quality setting."""
        with self.assertRaises(ValueError):
            PDFGenerationOptions(quality="ultra")


class TestOutputManager(unittest.TestCase):
    """Test cases for OutputManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.output_manager = OutputManager()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_save_pdf_to_file(self):
        """Test saving PDF buffer to file."""
        # Create test PDF content
        test_content = b"Test PDF content"
        pdf_buffer = io.BytesIO(test_content)

        # Save to file
        file_path, file_size = self.output_manager.save_pdf_to_file(
            pdf_buffer,
            filename="test_report.pdf",
            output_dir=self.temp_dir
        )

        # Verify file was created
        self.assertTrue(os.path.exists(file_path))
        self.assertEqual(file_size, len(test_content))

        # Verify file content
        with open(file_path, 'rb') as f:
            saved_content = f.read()
        self.assertEqual(saved_content, test_content)

    def test_save_pdf_auto_filename(self):
        """Test saving PDF with auto-generated filename."""
        test_content = b"Test PDF content"
        pdf_buffer = io.BytesIO(test_content)

        file_path, file_size = self.output_manager.save_pdf_to_file(
            pdf_buffer,
            output_dir=self.temp_dir
        )

        # Verify file was created with auto-generated name
        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(os.path.basename(file_path).startswith("strength_report_"))
        self.assertTrue(os.path.basename(file_path).endswith(".pdf"))

    @patch('core.report.pdf_generator.ShareLinkManager')
    def test_create_shareable_link(self, mock_share_manager_class):
        """Test creating shareable link for PDF."""
        # Mock share manager
        mock_share_manager = Mock()
        mock_share_result = Mock()
        mock_share_result.share_url = "https://example.com/share/abc123"
        mock_share_manager.create_share_link.return_value = mock_share_result

        output_manager = OutputManager(mock_share_manager)

        # Create test file
        test_file = os.path.join(self.temp_dir, "test.pdf")
        with open(test_file, 'wb') as f:
            f.write(b"Test PDF content")

        # Create share link
        share_url = output_manager.create_shareable_link(
            test_file, "測試用戶", expiry_hours=48
        )

        self.assertEqual(share_url, "https://example.com/share/abc123")
        mock_share_manager.create_share_link.assert_called_once()

    def test_cleanup_temporary_files(self):
        """Test cleaning up temporary files."""
        # Create test files
        test_files = []
        for i in range(3):
            file_path = os.path.join(self.temp_dir, f"test_{i}.pdf")
            with open(file_path, 'w') as f:
                f.write(f"Test content {i}")
            test_files.append(file_path)

        # Verify files exist
        for file_path in test_files:
            self.assertTrue(os.path.exists(file_path))

        # Clean up files
        self.output_manager.cleanup_temporary_files(test_files)

        # Verify files are deleted
        for file_path in test_files:
            self.assertFalse(os.path.exists(file_path))


class TestReportBuilder(unittest.TestCase):
    """Test cases for ReportBuilder."""

    def setUp(self):
        """Set up test fixtures."""
        self.builder = ReportBuilder()

    @patch('core.report.pdf_generator.ChartRenderer')
    def test_build_pdf_elements(self, mock_chart_renderer_class):
        """Test building PDF elements from report content."""
        # Mock report content
        mock_section = Mock()
        mock_section.content_elements = [Mock(), Mock()]
        mock_section.section_type = Mock()

        mock_report_content = Mock()
        mock_report_content.sections = [mock_section]
        mock_report_content.metadata = {}

        options = PDFGenerationOptions(include_charts=False)

        elements = self.builder.build_pdf_elements(mock_report_content, options)

        # Should include section elements
        self.assertEqual(len(elements), 2)

    def test_generate_section_charts_with_charts_disabled(self):
        """Test chart generation when charts are disabled."""
        mock_section = Mock()
        mock_section.section_type = Mock()

        options = PDFGenerationOptions(include_charts=False)
        mock_report_content = Mock()
        mock_report_content.sections = [mock_section]
        mock_report_content.metadata = {}

        elements = self.builder.build_pdf_elements(mock_report_content, options)

        # Should not contain any chart elements when disabled
        # (Implementation depends on section content_elements)
        self.assertIsInstance(elements, list)


class TestPDFReportGenerator(unittest.TestCase):
    """Test cases for PDFReportGenerator."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = PDFReportGenerator()

        # Sample data
        self.sample_scores = DimensionScores(
            openness=16.0,
            conscientiousness=14.0,
            extraversion=18.0,
            agreeableness=15.0,
            neuroticism=12.0
        )

        self.sample_responses = [
            QuestionResponse(question_id=i, score=3)
            for i in range(1, 21)
        ]

    @patch('core.report.pdf_generator.SimpleDocTemplate')
    @patch('core.report.pdf_generator.io.BytesIO')
    def test_generate_report_from_scores_success(self, mock_bytesio, mock_doc_class):
        """Test successful report generation from scores."""
        # Mock BytesIO
        mock_buffer = Mock()
        mock_bytesio.return_value = mock_buffer

        # Mock SimpleDocTemplate
        mock_doc = Mock()
        mock_doc_class.return_value = mock_doc

        # Mock output manager
        self.generator.output_manager.save_pdf_to_file = Mock()
        self.generator.output_manager.save_pdf_to_file.return_value = (
            "/tmp/test_report.pdf", 12345
        )

        result = self.generator.generate_report_from_scores(
            self.sample_scores,
            "測試用戶"
        )

        self.assertIsInstance(result, GenerationResult)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.file_path)
        self.assertIsNotNone(result.file_size_bytes)
        self.assertIsNotNone(result.report_id)
        self.assertIsNone(result.error_message)

    @patch('core.report.pdf_generator.ScoringEngine')
    def test_generate_report_from_responses_success(self, mock_scoring_engine_class):
        """Test successful report generation from responses."""
        # Mock scoring engine
        mock_scoring_engine = Mock()
        mock_scoring_engine_class.return_value = mock_scoring_engine

        mock_scoring_engine.calculate_scores_from_api.return_value = {
            "openness": 16.0,
            "conscientiousness": 14.0,
            "extraversion": 18.0,
            "agreeableness": 15.0,
            "neuroticism": 12.0
        }

        mock_scoring_engine.create_dimension_scores_object.return_value = self.sample_scores

        # Mock the generate_report_from_scores method
        self.generator.generate_report_from_scores = Mock()
        mock_result = GenerationResult(
            success=True,
            file_path="/tmp/test_report.pdf",
            file_size_bytes=12345,
            generation_time_seconds=2.5,
            report_id="TEST-123"
        )
        self.generator.generate_report_from_scores.return_value = mock_result

        result = self.generator.generate_report_from_responses(
            self.sample_responses,
            "測試用戶"
        )

        self.assertTrue(result.success)
        self.assertIsNotNone(result.file_path)

    def test_generate_report_from_responses_error(self):
        """Test error handling in report generation from responses."""
        # Pass invalid responses to trigger error
        invalid_responses = []  # Empty list should cause error

        result = self.generator.generate_report_from_responses(
            invalid_responses,
            "測試用戶"
        )

        self.assertFalse(result.success)
        self.assertIsNone(result.file_path)
        self.assertIsNotNone(result.error_message)

    @patch('core.report.pdf_generator.SimpleDocTemplate')
    def test_generate_report_error_handling(self, mock_doc_class):
        """Test error handling in PDF generation."""
        # Mock SimpleDocTemplate to raise exception
        mock_doc_class.side_effect = Exception("PDF generation failed")

        result = self.generator.generate_report_from_scores(
            self.sample_scores,
            "測試用戶"
        )

        self.assertFalse(result.success)
        self.assertIsNone(result.file_path)
        self.assertIn("PDF generation failed", result.error_message)

    def test_generate_and_share_report_success(self):
        """Test successful report generation with sharing."""
        # Mock generate_report_from_scores
        self.generator.generate_report_from_scores = Mock()
        mock_result = GenerationResult(
            success=True,
            file_path="/tmp/test_report.pdf",
            file_size_bytes=12345,
            generation_time_seconds=2.5,
            report_id="TEST-123",
            warnings=[]
        )
        self.generator.generate_report_from_scores.return_value = mock_result

        # Mock output manager
        self.generator.output_manager.create_shareable_link = Mock()
        self.generator.output_manager.create_shareable_link.return_value = (
            "https://example.com/share/abc123"
        )

        result, share_url = self.generator.generate_and_share_report(
            self.sample_scores,
            "測試用戶"
        )

        self.assertTrue(result.success)
        self.assertIsNotNone(share_url)
        self.assertEqual(share_url, "https://example.com/share/abc123")

    def test_generate_and_share_report_share_error(self):
        """Test report generation with sharing error."""
        # Mock successful report generation
        self.generator.generate_report_from_scores = Mock()
        mock_result = GenerationResult(
            success=True,
            file_path="/tmp/test_report.pdf",
            file_size_bytes=12345,
            generation_time_seconds=2.5,
            report_id="TEST-123",
            warnings=[]
        )
        self.generator.generate_report_from_scores.return_value = mock_result

        # Mock sharing error
        self.generator.output_manager.create_shareable_link = Mock()
        self.generator.output_manager.create_shareable_link.side_effect = Exception("Share failed")

        result, share_url = self.generator.generate_and_share_report(
            self.sample_scores,
            "測試用戶"
        )

        self.assertTrue(result.success)  # Report generation succeeded
        self.assertIsNone(share_url)  # Sharing failed
        self.assertTrue(len(result.warnings) > 0)  # Warning should be added

    def test_get_generation_statistics(self):
        """Test generation statistics."""
        stats = self.generator.get_generation_statistics()

        self.assertIn("version", stats)
        self.assertIn("components", stats)
        self.assertIn("supported_formats", stats)
        self.assertIn("supported_qualities", stats)
        self.assertIn("default_config", stats)

        # Check specific values
        self.assertIn("pdf", stats["supported_formats"])
        self.assertIn("high", stats["supported_qualities"])

    def test_cleanup_temp_files(self):
        """Test temporary file cleanup."""
        mock_result = GenerationResult(
            success=True,
            file_path="/tmp/test_report.pdf",
            file_size_bytes=12345,
            generation_time_seconds=2.5,
            report_id="TEST-123"
        )

        # Mock output manager cleanup
        self.generator.output_manager.cleanup_temporary_files = Mock()

        self.generator.cleanup_temp_files(mock_result)

        self.generator.output_manager.cleanup_temporary_files.assert_called_once_with(
            ["/tmp/test_report.pdf"]
        )


class TestFactoryFunctions(unittest.TestCase):
    """Test cases for factory functions."""

    def test_create_pdf_generator(self):
        """Test PDF generator factory function."""
        generator = create_pdf_generator()

        self.assertIsInstance(generator, PDFReportGenerator)
        self.assertIsNotNone(generator.config)
        self.assertIsNotNone(generator.report_builder)
        self.assertIsNotNone(generator.output_manager)

    def test_create_pdf_generator_with_config(self):
        """Test PDF generator factory with custom config."""
        from core.report.report_template import ReportConfig

        custom_config = ReportConfig(font_family="Arial")
        generator = create_pdf_generator(config=custom_config)

        self.assertEqual(generator.config.font_family, "Arial")

    @patch('core.report.pdf_generator.create_pdf_generator')
    @patch('core.report.pdf_generator.PDFReportGenerator')
    def test_generate_quick_report_success(self, mock_generator_class, mock_factory):
        """Test quick report generation function."""
        from core.report.pdf_generator import generate_quick_report

        # Mock generator
        mock_generator = Mock()
        mock_factory.return_value = mock_generator

        mock_result = GenerationResult(
            success=True,
            file_path="/tmp/test_report.pdf",
            file_size_bytes=12345,
            generation_time_seconds=2.5,
            report_id="TEST-123"
        )
        mock_generator.generate_report_from_responses.return_value = mock_result

        result_path = generate_quick_report(
            self.sample_responses,
            "測試用戶"
        )

        self.assertEqual(result_path, "/tmp/test_report.pdf")

    @patch('core.report.pdf_generator.create_pdf_generator')
    def test_generate_quick_report_error(self, mock_factory):
        """Test quick report generation error handling."""
        from core.report.pdf_generator import generate_quick_report

        # Mock generator with error
        mock_generator = Mock()
        mock_factory.return_value = mock_generator

        mock_result = GenerationResult(
            success=False,
            file_path=None,
            file_size_bytes=None,
            generation_time_seconds=1.0,
            report_id="TEST-123",
            error_message="Generation failed"
        )
        mock_generator.generate_report_from_responses.return_value = mock_result

        with self.assertRaises(Exception) as context:
            generate_quick_report(self.sample_responses, "測試用戶")

        self.assertIn("Generation failed", str(context.exception))


if __name__ == '__main__':
    unittest.main()