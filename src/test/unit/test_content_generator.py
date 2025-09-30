"""
Unit Tests for Content Generator

This module provides comprehensive unit tests for the content generation
system, ensuring correct functionality and maintaining code quality.

Test Coverage:
- PersonalizedContentGenerator functionality
- ReportStructureBuilder section generation
- ContentGenerator orchestration
- Edge cases and error handling

Author: TaskMaster Agent (3.4.3)
Date: 2025-09-30
Version: 1.0
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, List

from core.scoring import DimensionScores
from core.report.content_generator import (
    ContentGenerator, PersonalizedContentGenerator, ReportStructureBuilder,
    ContentType, ContentSection, ReportContent
)
from core.report.report_template import ReportTemplate, ReportConfig
from models.schemas import QuestionResponse


class TestPersonalizedContentGenerator(unittest.TestCase):
    """Test cases for PersonalizedContentGenerator."""

    def setUp(self):
        """Set up test fixtures."""
        self.template = ReportTemplate()
        self.generator = PersonalizedContentGenerator(self.template)

        # Mock Big Five scores
        self.sample_scores = DimensionScores(
            openness=16.0,
            conscientiousness=14.0,
            extraversion=18.0,
            agreeableness=15.0,
            neuroticism=12.0
        )

        # Mock strength profile
        self.mock_strength_profile = Mock()
        self.mock_strength_profile.top_5_strengths = [
            Mock(theme=Mock(chinese_name="戰略思維", name="strategic", description="善於制定長期計劃")),
            Mock(theme=Mock(chinese_name="溝通表達", name="communication", description="擅長與他人交流"))
        ]
        self.mock_strength_profile.domain_distribution = {
            Mock(value="strategic_thinking"): 0.4,
            Mock(value="influencing"): 0.3,
            Mock(value="executing"): 0.2,
            Mock(value="relationship_building"): 0.1
        }

    def test_generate_personality_description(self):
        """Test personality description generation."""
        descriptions = self.generator.generate_personality_description(
            self.sample_scores, self.mock_strength_profile
        )

        self.assertIsInstance(descriptions, list)
        self.assertTrue(len(descriptions) > 0)

        # Check that descriptions contain relevant content
        combined_text = " ".join(descriptions)
        self.assertIn("個性特質", combined_text)

    def test_generate_strength_narrative(self):
        """Test strength narrative generation."""
        narratives = self.generator.generate_strength_narrative(
            self.mock_strength_profile
        )

        self.assertIsInstance(narratives, list)
        self.assertTrue(len(narratives) > 0)

        # Check for strength-related content
        combined_text = " ".join(narratives)
        self.assertIn("優勢", combined_text)

    def test_generate_career_fit_description(self):
        """Test career fit description generation."""
        # Mock job recommendations
        mock_jobs = [
            Mock(
                chinese_title="策略分析師",
                match_score=85.5,
                primary_strengths_used=["戰略思維", "分析能力"],
                industry_sector="諮詢業"
            ),
            Mock(
                chinese_title="產品經理",
                match_score=78.2,
                primary_strengths_used=["溝通表達", "執行力"],
                industry_sector="科技業"
            )
        ]

        descriptions = self.generator.generate_career_fit_description(
            mock_jobs, self.mock_strength_profile
        )

        self.assertIsInstance(descriptions, list)
        self.assertTrue(len(descriptions) > 0)

        # Check for career-related content
        combined_text = " ".join(descriptions)
        self.assertIn("職業", combined_text)
        self.assertIn("85.5", combined_text)  # Match score should appear

    def test_identify_dominant_traits(self):
        """Test dominant trait identification."""
        score_dict = self.sample_scores.to_dict()
        traits = self.generator._identify_dominant_traits(score_dict)

        self.assertIn("primary", traits)
        self.assertIn("secondary", traits)
        self.assertIsInstance(traits["primary"], str)
        self.assertIsInstance(traits["secondary"], str)

    def test_empty_job_recommendations(self):
        """Test handling of empty job recommendations."""
        descriptions = self.generator.generate_career_fit_description(
            [], self.mock_strength_profile
        )

        self.assertIsInstance(descriptions, list)
        self.assertEqual(len(descriptions), 1)
        self.assertIn("多元化", descriptions[0])


class TestReportStructureBuilder(unittest.TestCase):
    """Test cases for ReportStructureBuilder."""

    def setUp(self):
        """Set up test fixtures."""
        self.template = ReportTemplate()
        self.builder = ReportStructureBuilder(self.template)

    def test_build_cover_page(self):
        """Test cover page building."""
        user_name = "測試用戶"
        assessment_date = datetime(2025, 9, 30)
        report_id = "RPT-20250930-TEST"

        section = self.builder.build_cover_page(
            user_name, assessment_date, report_id
        )

        self.assertIsInstance(section, ContentSection)
        self.assertEqual(section.section_type, ContentType.COVER_PAGE)
        self.assertTrue(len(section.content_elements) > 0)
        self.assertEqual(section.metadata["user_name"], user_name)
        self.assertEqual(section.metadata["report_id"], report_id)

    def test_build_executive_summary(self):
        """Test executive summary building."""
        # Mock inputs
        mock_strength_profile = Mock()
        mock_strength_profile.top_5_strengths = [
            Mock(theme=Mock(chinese_name="分析思維")),
            Mock(theme=Mock(chinese_name="執行力"))
        ]

        mock_jobs = [
            Mock(chinese_title="數據分析師", match_score=88.5)
        ]

        summary_insights = [
            "您的核心優勢是分析思維",
            "建議發展數據科學技能"
        ]

        section = self.builder.build_executive_summary(
            mock_strength_profile, mock_jobs, summary_insights
        )

        self.assertIsInstance(section, ContentSection)
        self.assertEqual(section.section_type, ContentType.EXECUTIVE_SUMMARY)
        self.assertTrue(len(section.content_elements) > 0)

    def test_build_strength_analysis_section(self):
        """Test strength analysis section building."""
        # Mock strength profile
        mock_strength_profile = Mock()
        mock_strength_profile.top_5_strengths = [
            Mock(
                theme=Mock(
                    chinese_name="戰略思維",
                    domain=Mock(value="strategic_thinking")
                ),
                score=95.5
            ),
            Mock(
                theme=Mock(
                    chinese_name="溝通能力",
                    domain=Mock(value="influencing")
                ),
                score=87.2
            )
        ]

        # Mock personalized content generator
        mock_content_gen = Mock()
        mock_content_gen.generate_strength_narrative.return_value = [
            "您的戰略思維能力出色",
            "建議在規劃工作中發揮優勢"
        ]

        section = self.builder.build_strength_analysis_section(
            mock_strength_profile, mock_content_gen
        )

        self.assertIsInstance(section, ContentSection)
        self.assertEqual(section.section_type, ContentType.STRENGTH_ANALYSIS)
        self.assertTrue(len(section.content_elements) > 0)

    def test_build_career_recommendations_section(self):
        """Test career recommendations section building."""
        # Mock job recommendations
        mock_jobs = [
            Mock(
                chinese_title="策略顧問",
                title="Strategy Consultant",
                match_score=92.3,
                primary_strengths_used=["戰略思維", "分析能力"],
                description="負責企業策略制定和分析",
                confidence_level="high",
                development_suggestions=["提升簡報技能", "加強財務知識"]
            )
        ]

        # Mock strength profile
        mock_strength_profile = Mock()

        # Mock personalized content generator
        mock_content_gen = Mock()
        mock_content_gen.generate_career_fit_description.return_value = [
            "策略顧問是您的理想職業選擇"
        ]

        section = self.builder.build_career_recommendations_section(
            mock_jobs, mock_content_gen, mock_strength_profile
        )

        self.assertIsInstance(section, ContentSection)
        self.assertEqual(section.section_type, ContentType.CAREER_RECOMMENDATIONS)
        self.assertTrue(len(section.content_elements) > 0)


class TestContentGenerator(unittest.TestCase):
    """Test cases for ContentGenerator."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = ContentGenerator()

        # Sample Big Five scores
        self.sample_scores = DimensionScores(
            openness=16.0,
            conscientiousness=14.0,
            extraversion=18.0,
            agreeableness=15.0,
            neuroticism=12.0
        )

    @patch('core.report.content_generator.RecommendationEngine')
    def test_generate_complete_report_content(self, mock_rec_engine_class):
        """Test complete report content generation."""
        # Mock recommendation engine
        mock_rec_engine = Mock()
        mock_rec_engine_class.return_value = mock_rec_engine

        # Mock recommendation result
        mock_result = Mock()
        mock_result.strength_profile = Mock()
        mock_result.strength_profile.top_5_strengths = []
        mock_result.job_recommendations = []
        mock_result.summary_insights = ["測試洞察"]
        mock_result.development_plan = Mock()
        mock_result.development_plan.priority_areas = ["技能發展"]
        mock_result.development_plan.action_items = ["學習新技術"]
        mock_result.development_plan.recommended_resources = ["在線課程"]
        mock_result.confidence_score = 0.85

        mock_rec_engine.generate_recommendations.return_value = mock_result

        # Generate report content
        user_name = "測試用戶"
        assessment_date = datetime(2025, 9, 30)

        report_content = self.generator.generate_complete_report_content(
            self.sample_scores,
            user_name,
            assessment_date
        )

        self.assertIsInstance(report_content, ReportContent)
        self.assertEqual(report_content.user_name, user_name)
        self.assertEqual(report_content.assessment_date, assessment_date)
        self.assertTrue(len(report_content.sections) > 0)
        self.assertIsNotNone(report_content.report_id)

        # Verify all expected sections are present
        section_types = [section.section_type for section in report_content.sections]
        expected_types = [
            ContentType.COVER_PAGE,
            ContentType.EXECUTIVE_SUMMARY,
            ContentType.PERSONALITY_PROFILE,
            ContentType.STRENGTH_ANALYSIS,
            ContentType.CAREER_RECOMMENDATIONS,
            ContentType.DEVELOPMENT_PLAN
        ]

        for expected_type in expected_types:
            self.assertIn(expected_type, section_types)

    def test_get_content_statistics(self):
        """Test content statistics generation."""
        # Create a mock report content
        mock_sections = [
            Mock(
                section_type=ContentType.COVER_PAGE,
                chinese_title="封面",
                content_elements=[Mock(), Mock()]
            ),
            Mock(
                section_type=ContentType.EXECUTIVE_SUMMARY,
                chinese_title="執行摘要",
                content_elements=[Mock(), Mock(), Mock()]
            )
        ]

        mock_report = Mock()
        mock_report.sections = mock_sections
        mock_report.generation_timestamp = datetime.now()
        mock_report.report_id = "TEST-REPORT-123"

        stats = self.generator.get_content_statistics(mock_report)

        self.assertIn("total_sections", stats)
        self.assertIn("total_elements", stats)
        self.assertIn("sections_by_type", stats)
        self.assertEqual(stats["total_sections"], 2)
        self.assertEqual(stats["total_elements"], 5)  # 2 + 3


class TestContentSection(unittest.TestCase):
    """Test cases for ContentSection data class."""

    def test_content_section_creation(self):
        """Test ContentSection creation and validation."""
        section = ContentSection(
            section_type=ContentType.COVER_PAGE,
            title="Cover Page",
            chinese_title="封面",
            content_elements=[],
            metadata={}
        )

        self.assertEqual(section.section_type, ContentType.COVER_PAGE)
        self.assertEqual(section.title, "Cover Page")
        self.assertEqual(section.chinese_title, "封面")
        self.assertIsInstance(section.content_elements, list)
        self.assertIsInstance(section.metadata, dict)

    def test_content_section_post_init(self):
        """Test ContentSection post-initialization behavior."""
        # Test with None values
        section = ContentSection(
            section_type=ContentType.COVER_PAGE,
            title="Test",
            chinese_title="測試",
            content_elements=None,
            metadata=None
        )

        # Post-init should initialize empty containers
        self.assertIsInstance(section.content_elements, list)
        self.assertIsInstance(section.metadata, dict)


class TestReportContent(unittest.TestCase):
    """Test cases for ReportContent data class."""

    def test_get_section(self):
        """Test getting specific sections from report content."""
        sections = [
            ContentSection(
                section_type=ContentType.COVER_PAGE,
                title="Cover",
                chinese_title="封面",
                content_elements=[],
                metadata={}
            ),
            ContentSection(
                section_type=ContentType.EXECUTIVE_SUMMARY,
                title="Summary",
                chinese_title="摘要",
                content_elements=[],
                metadata={}
            )
        ]

        report = ReportContent(
            report_id="TEST-123",
            generation_timestamp=datetime.now(),
            user_name="測試用戶",
            assessment_date=datetime.now(),
            sections=sections,
            metadata={}
        )

        # Test getting existing section
        cover_section = report.get_section(ContentType.COVER_PAGE)
        self.assertIsNotNone(cover_section)
        self.assertEqual(cover_section.section_type, ContentType.COVER_PAGE)

        # Test getting non-existing section
        missing_section = report.get_section(ContentType.DEVELOPMENT_PLAN)
        self.assertIsNone(missing_section)


if __name__ == '__main__':
    unittest.main()