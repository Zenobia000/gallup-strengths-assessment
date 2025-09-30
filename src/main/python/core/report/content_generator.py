"""
PDF Report Content Generator - Core Content Generation Logic

This module implements the core business logic for generating personalized
PDF report content based on Big Five personality assessment results and
Gallup Strengths recommendations.

Key Components:
- ContentGenerator: Main orchestrator for content generation
- PersonalizedContentGenerator: Individual content module generator
- ReportStructureBuilder: Report structure and page layout definition
- ContentTemplate: Dynamic content template system

Design Philosophy:
Following Clean Architecture principles with clear separation between
business logic and presentation layer. Each module has a single responsibility
and provides testable, maintainable code.

Author: TaskMaster Agent (3.4.3)
Date: 2025-09-30
Version: 1.0
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import uuid

from reportlab.platypus import Paragraph, Spacer, PageBreak, Table, KeepTogether
from reportlab.lib.units import mm

from core.scoring import DimensionScores
from core.recommendation import (
    RecommendationEngine, RecommendationResult,
    StrengthProfile, JobRecommendation, DevelopmentPlan
)
from .report_template import ReportTemplate, ReportConfig, ReportSection


class ContentType(Enum):
    """Types of content that can be generated."""
    COVER_PAGE = "cover_page"
    EXECUTIVE_SUMMARY = "executive_summary"
    STRENGTH_ANALYSIS = "strength_analysis"
    PERSONALITY_PROFILE = "personality_profile"
    CAREER_RECOMMENDATIONS = "career_recommendations"
    DEVELOPMENT_PLAN = "development_plan"
    DETAILED_INSIGHTS = "detailed_insights"
    APPENDIX = "appendix"


@dataclass
class ContentSection:
    """Represents a section of report content."""
    section_type: ContentType
    title: str
    chinese_title: str
    content_elements: List[Any]  # ReportLab flowables
    metadata: Dict[str, Any]

    def __post_init__(self):
        """Validate content section after initialization."""
        if not self.content_elements:
            self.content_elements = []
        if not self.metadata:
            self.metadata = {}


@dataclass
class ReportContent:
    """Complete report content with all sections."""
    report_id: str
    generation_timestamp: datetime
    user_name: str
    assessment_date: datetime
    sections: List[ContentSection]
    metadata: Dict[str, Any]

    def get_section(self, section_type: ContentType) -> Optional[ContentSection]:
        """Get a specific section by type."""
        for section in self.sections:
            if section.section_type == section_type:
                return section
        return None


class PersonalizedContentGenerator:
    """
    Generator for personalized content modules based on assessment results.

    This class handles the creation of individualized content that adapts
    to the user's specific personality profile and strength assessment results.
    """

    def __init__(self, template: ReportTemplate):
        """Initialize with report template for styling."""
        self.template = template

    def generate_personality_description(
        self,
        big_five_scores: DimensionScores,
        strength_profile: StrengthProfile
    ) -> List[str]:
        """
        Generate personalized personality description.

        Args:
            big_five_scores: Big Five dimension scores
            strength_profile: Mapped strength profile

        Returns:
            List of personalized description paragraphs
        """
        descriptions = []

        # Convert scores to percentile descriptions
        score_dict = big_five_scores.to_dict()

        # Primary personality insights
        dominant_traits = self._identify_dominant_traits(score_dict)
        descriptions.append(
            f"您的個性特質顯示出{dominant_traits['primary']}的傾向，"
            f"同時在{dominant_traits['secondary']}方面也表現突出。"
        )

        # Strength-based personality integration
        if strength_profile.top_5_strengths:
            top_strength = strength_profile.top_5_strengths[0]
            descriptions.append(
                f"您的核心優勢「{top_strength.theme.chinese_name}」"
                f"與您的個性特質相互輝映，形成了獨特的個人風格。"
                f"{top_strength.theme.description}"
            )

        # Behavioral patterns
        behavioral_insights = self._generate_behavioral_insights(score_dict)
        descriptions.extend(behavioral_insights)

        return descriptions

    def generate_strength_narrative(
        self,
        strength_profile: StrengthProfile
    ) -> List[str]:
        """
        Generate narrative description of strength profile.

        Args:
            strength_profile: User's strength profile

        Returns:
            List of narrative paragraphs about strengths
        """
        narratives = []

        # Top strengths overview
        if len(strength_profile.top_5_strengths) >= 2:
            top_two = strength_profile.top_5_strengths[:2]
            narratives.append(
                f"您最突出的兩項優勢是「{top_two[0].theme.chinese_name}」"
                f"和「{top_two[1].theme.chinese_name}」。這個組合讓您在"
                f"{self._describe_strength_combination(top_two)}"
            )

        # Domain distribution narrative
        domain_story = self._create_domain_narrative(strength_profile.domain_distribution)
        narratives.append(domain_story)

        # Application suggestions
        application_narrative = self._create_application_narrative(strength_profile)
        narratives.append(application_narrative)

        return narratives

    def generate_career_fit_description(
        self,
        job_recommendations: List[JobRecommendation],
        strength_profile: StrengthProfile
    ) -> List[str]:
        """
        Generate personalized career fit descriptions.

        Args:
            job_recommendations: Recommended job roles
            strength_profile: User's strength profile

        Returns:
            List of career fit description paragraphs
        """
        descriptions = []

        if not job_recommendations:
            descriptions.append("基於您的優勢特質，我們建議您探索多元化的職業發展機會。")
            return descriptions

        # Top recommendation narrative
        top_job = job_recommendations[0]
        descriptions.append(
            f"「{top_job.chinese_title}」是最適合您的職業方向之一"
            f"（匹配度 {top_job.match_score:.1f}%）。"
            f"這個角色能充分發揮您在{', '.join(top_job.primary_strengths_used[:2])}的優勢。"
        )

        # Career pattern analysis
        if len(job_recommendations) >= 3:
            pattern_analysis = self._analyze_career_patterns(job_recommendations)
            descriptions.append(pattern_analysis)

        # Industry fit insights
        industry_insights = self._generate_industry_insights(job_recommendations)
        descriptions.append(industry_insights)

        return descriptions

    def _identify_dominant_traits(self, score_dict: Dict[str, float]) -> Dict[str, str]:
        """Identify dominant personality traits."""
        trait_labels = {
            "openness": ("開放性", "創新思維和學習熱忱"),
            "conscientiousness": ("嚴謹性", "組織能力和責任感"),
            "extraversion": ("外向性", "社交活力和表達能力"),
            "agreeableness": ("親和性", "合作精神和同理心"),
            "neuroticism": ("情緒穩定性", "壓力管理和情緒調節")
        }

        # Sort traits by score
        sorted_traits = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)

        primary_trait = trait_labels[sorted_traits[0][0]][0]
        secondary_trait = trait_labels[sorted_traits[1][0]][0]

        return {
            "primary": primary_trait,
            "secondary": secondary_trait
        }

    def _generate_behavioral_insights(self, score_dict: Dict[str, float]) -> List[str]:
        """Generate behavioral pattern insights."""
        insights = []

        # Work style insights
        if score_dict["conscientiousness"] > 15:
            insights.append(
                "在工作中，您傾向於採用系統化和有序的方法，"
                "重視計劃性和細節的完善。"
            )

        # Social interaction insights
        if score_dict["extraversion"] > 15:
            insights.append(
                "您在團隊環境中表現活躍，擅長與他人建立聯繫，"
                "並能有效地表達想法和觀點。"
            )

        # Innovation insights
        if score_dict["openness"] > 15:
            insights.append(
                "您對新想法和不同觀點持開放態度，"
                "喜歡探索創新的解決方案和學習新技能。"
            )

        return insights[:2]  # Limit to 2 insights

    def _describe_strength_combination(self, top_strengths: List[Any]) -> str:
        """Describe the combination effect of top strengths."""
        combinations = {
            ("achiever", "focus"): "目標達成和專注執行方面特別出色",
            ("strategic", "analytical"): "策略思考和分析決策方面展現卓越能力",
            ("communication", "woo"): "人際溝通和影響他人方面具有天賦",
            ("learner", "input"): "知識獲取和資訊整合方面表現優異"
        }

        # Try to find matching combination pattern
        strength_names = [s.theme.name.lower() for s in top_strengths]
        for combo, description in combinations.items():
            if all(name in strength_names for name in combo):
                return description

        # Default description
        return "多個領域中都能發揮重要作用"

    def _create_domain_narrative(self, domain_distribution: Dict[Any, float]) -> str:
        """Create narrative about domain distribution."""
        domain_names = {
            "executing": "執行力",
            "influencing": "影響力",
            "relationship_building": "關係建立",
            "strategic_thinking": "戰略思維"
        }

        sorted_domains = sorted(
            domain_distribution.items(),
            key=lambda x: x[1],
            reverse=True
        )

        if len(sorted_domains) >= 2:
            primary = domain_names.get(sorted_domains[0][0].value, "未知")
            secondary = domain_names.get(sorted_domains[1][0].value, "未知")

            return (
                f"您的優勢主要集中在{primary}領域，其次是{secondary}領域。"
                f"這樣的組合讓您能在需要{primary}和{secondary}的環境中充分發揮。"
            )

        return "您的優勢呈現均衡分布，適應性較強。"

    def _create_application_narrative(self, strength_profile: StrengthProfile) -> str:
        """Create narrative about how to apply strengths."""
        if not strength_profile.top_5_strengths:
            return "建議您將個人優勢運用在符合興趣的領域中。"

        top_strength = strength_profile.top_5_strengths[0]
        application_tips = {
            "achiever": "設定具挑戰性的目標並持續追求卓越表現",
            "analytical": "參與需要深度分析和邏輯思考的專案",
            "communication": "承擔需要表達和說服他人的角色",
            "strategic": "參與長期規劃和策略制定的工作",
            "learner": "主動探索新知識和技能發展機會"
        }

        tip = application_tips.get(
            top_strength.theme.name.lower(),
            "將您的核心優勢運用在最感興趣的領域"
        )

        return f"建議您{tip}，以充分發揮您的天賦潛能。"

    def _analyze_career_patterns(self, job_recommendations: List[JobRecommendation]) -> str:
        """Analyze patterns in career recommendations."""
        industries = [job.industry_sector for job in job_recommendations[:3]]
        common_skills = []

        # Find common required skills
        all_skills = []
        for job in job_recommendations[:3]:
            all_skills.extend(job.required_skills)

        skill_counts = {}
        for skill in all_skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1

        common_skills = [
            skill for skill, count in skill_counts.items()
            if count >= 2
        ][:3]

        if common_skills:
            return (
                f"推薦的職業角色都強調{', '.join(common_skills[:2])}等核心技能，"
                f"這與您的優勢特質高度一致。"
            )

        return "推薦的職業角色涵蓋多個領域，為您提供豐富的發展選項。"

    def _generate_industry_insights(self, job_recommendations: List[JobRecommendation]) -> str:
        """Generate insights about industry fit."""
        industries = [job.industry_sector for job in job_recommendations[:3]]
        unique_industries = list(set(industries))

        if len(unique_industries) == 1:
            return f"您特別適合在{unique_industries[0]}領域發展，這個行業與您的特質高度匹配。"
        elif len(unique_industries) >= 2:
            return f"您在{unique_industries[0]}和{unique_industries[1]}等領域都有很好的發展潛力。"

        return "您的優勢特質讓您在多個行業領域都能找到合適的發展機會。"


class ReportStructureBuilder:
    """
    Builder for report structure and page layout definition.

    This class defines the overall structure of the PDF report and
    coordinates the generation of different sections.
    """

    def __init__(self, template: ReportTemplate):
        """Initialize with report template."""
        self.template = template

    def build_cover_page(
        self,
        user_name: str,
        assessment_date: datetime,
        report_id: str
    ) -> ContentSection:
        """
        Build cover page section.

        Args:
            user_name: Name of the user
            assessment_date: Date of assessment
            report_id: Unique report identifier

        Returns:
            ContentSection for cover page
        """
        elements = []

        # Report title
        title_text = "個人優勢評估報告<br/>Personal Strengths Assessment Report"
        elements.append(Paragraph(title_text, self.template.styles['ReportTitle']))
        elements.append(Spacer(1, 30*mm))

        # User information
        user_info = f"評估對象：{user_name}"
        elements.append(Paragraph(user_info, self.template.styles['Heading2']))

        date_info = f"評估日期：{assessment_date.strftime('%Y年%m月%d日')}"
        elements.append(Paragraph(date_info, self.template.styles['Body']))

        report_info = f"報告編號：{report_id}"
        elements.append(Paragraph(report_info, self.template.styles['Body']))

        elements.append(Spacer(1, 40*mm))

        # Disclaimer
        disclaimer = """
        本報告基於 Mini-IPIP Big Five 人格測驗結果，結合 Gallup 34 項優勢主題進行分析。
        報告內容僅供參考，不應作為決策的唯一依據。個人發展需要綜合考慮多種因素，
        包括但不限於個人興趣、價值觀、工作經驗和市場環境等。
        """
        elements.append(Paragraph(disclaimer, self.template.styles['Caption']))

        elements.append(PageBreak())

        return ContentSection(
            section_type=ContentType.COVER_PAGE,
            title="Cover Page",
            chinese_title="封面",
            content_elements=elements,
            metadata={
                "user_name": user_name,
                "assessment_date": assessment_date,
                "report_id": report_id
            }
        )

    def build_executive_summary(
        self,
        strength_profile: StrengthProfile,
        job_recommendations: List[JobRecommendation],
        summary_insights: List[str]
    ) -> ContentSection:
        """
        Build executive summary section.

        Args:
            strength_profile: User's strength profile
            job_recommendations: Top job recommendations
            summary_insights: Key insights from analysis

        Returns:
            ContentSection for executive summary
        """
        elements = []

        # Section title
        elements.append(Paragraph("執行摘要", self.template.styles['Heading1']))

        # Key insights
        elements.append(Paragraph("關鍵洞察", self.template.styles['Heading2']))
        for insight in summary_insights[:3]:
            elements.append(Paragraph(f"• {insight}", self.template.styles['Bullet']))

        elements.append(Spacer(1, 10*mm))

        # Top strengths summary
        elements.append(Paragraph("核心優勢", self.template.styles['Heading2']))
        if strength_profile.top_5_strengths:
            strength_summary = "您的前三項核心優勢為："
            top_three = strength_profile.top_5_strengths[:3]
            strength_list = [f"「{s.theme.chinese_name}」" for s in top_three]
            strength_summary += "、".join(strength_list) + "。"
            elements.append(Paragraph(strength_summary, self.template.styles['Body']))

        elements.append(Spacer(1, 10*mm))

        # Career recommendations summary
        elements.append(Paragraph("職業建議", self.template.styles['Heading2']))
        if job_recommendations:
            career_summary = f"最推薦的職業方向是「{job_recommendations[0].chinese_title}」"
            career_summary += f"（匹配度 {job_recommendations[0].match_score:.1f}%）。"
            elements.append(Paragraph(career_summary, self.template.styles['Body']))

        return ContentSection(
            section_type=ContentType.EXECUTIVE_SUMMARY,
            title="Executive Summary",
            chinese_title="執行摘要",
            content_elements=elements,
            metadata={}
        )

    def build_strength_analysis_section(
        self,
        strength_profile: StrengthProfile,
        personalized_content: PersonalizedContentGenerator
    ) -> ContentSection:
        """
        Build detailed strength analysis section.

        Args:
            strength_profile: User's strength profile
            personalized_content: Content generator for personalized text

        Returns:
            ContentSection for strength analysis
        """
        elements = []

        # Section title
        elements.append(Paragraph("優勢分析", self.template.styles['Heading1']))

        # Strength narrative
        strength_narratives = personalized_content.generate_strength_narrative(strength_profile)
        for narrative in strength_narratives:
            elements.append(Paragraph(narrative, self.template.styles['Body']))
            elements.append(Spacer(1, 6))

        elements.append(Spacer(1, 10*mm))

        # Top 5 strengths table
        elements.append(Paragraph("您的前五項優勢", self.template.styles['Heading2']))

        if strength_profile.top_5_strengths:
            table_data = [["排名", "優勢主題", "領域", "分數"]]

            for i, strength in enumerate(strength_profile.top_5_strengths, 1):
                domain_chinese = {
                    "executing": "執行力",
                    "influencing": "影響力",
                    "relationship_building": "關係建立",
                    "strategic_thinking": "戰略思維"
                }.get(strength.theme.domain.value, "未知")

                table_data.append([
                    str(i),
                    strength.theme.chinese_name,
                    domain_chinese,
                    f"{strength.score:.1f}"
                ])

            table = Table(table_data, colWidths=[20*mm, 50*mm, 40*mm, 25*mm])
            table.setStyle(self.template.create_table_style(header=True))
            elements.append(table)

        return ContentSection(
            section_type=ContentType.STRENGTH_ANALYSIS,
            title="Strength Analysis",
            chinese_title="優勢分析",
            content_elements=elements,
            metadata={}
        )

    def build_career_recommendations_section(
        self,
        job_recommendations: List[JobRecommendation],
        personalized_content: PersonalizedContentGenerator,
        strength_profile: StrengthProfile
    ) -> ContentSection:
        """
        Build career recommendations section.

        Args:
            job_recommendations: List of job recommendations
            personalized_content: Content generator for personalized text
            strength_profile: User's strength profile

        Returns:
            ContentSection for career recommendations
        """
        elements = []

        # Section title
        elements.append(Paragraph("職業建議", self.template.styles['Heading1']))

        # Career fit description
        career_descriptions = personalized_content.generate_career_fit_description(
            job_recommendations, strength_profile
        )
        for description in career_descriptions:
            elements.append(Paragraph(description, self.template.styles['Body']))
            elements.append(Spacer(1, 6))

        elements.append(Spacer(1, 10*mm))

        # Job recommendations details
        elements.append(Paragraph("推薦職位詳細分析", self.template.styles['Heading2']))

        for i, job in enumerate(job_recommendations[:3], 1):
            # Job title and match score
            job_title = f"{i}. {job.chinese_title} ({job.title})"
            elements.append(Paragraph(job_title, self.template.styles['Heading3']))

            match_text = f"匹配度：{job.match_score:.1f}% | 信心度：{job.confidence_level}"
            elements.append(Paragraph(match_text, self.template.styles['BodyBold']))

            # Job description
            elements.append(Paragraph(f"職位描述：{job.description}", self.template.styles['Body']))

            # Primary strengths used
            strengths_text = f"運用優勢：{', '.join(job.primary_strengths_used)}"
            elements.append(Paragraph(strengths_text, self.template.styles['Body']))

            # Development suggestions
            if job.development_suggestions:
                elements.append(Paragraph("發展建議：", self.template.styles['BodyBold']))
                for suggestion in job.development_suggestions:
                    elements.append(Paragraph(f"• {suggestion}", self.template.styles['Bullet']))

            elements.append(Spacer(1, 8))

        return ContentSection(
            section_type=ContentType.CAREER_RECOMMENDATIONS,
            title="Career Recommendations",
            chinese_title="職業建議",
            content_elements=elements,
            metadata={}
        )


class ContentGenerator:
    """
    Main orchestrator for PDF report content generation.

    This class coordinates all content generation components to produce
    complete, personalized PDF report content based on assessment results.
    """

    def __init__(self, config: Optional[ReportConfig] = None):
        """Initialize content generator with configuration."""
        self.config = config or ReportConfig()
        self.template = ReportTemplate(self.config)
        self.personalized_generator = PersonalizedContentGenerator(self.template)
        self.structure_builder = ReportStructureBuilder(self.template)
        self.recommendation_engine = RecommendationEngine()

    def generate_complete_report_content(
        self,
        big_five_scores: DimensionScores,
        user_name: str,
        assessment_date: Optional[datetime] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> ReportContent:
        """
        Generate complete report content from assessment results.

        Args:
            big_five_scores: Big Five personality dimension scores
            user_name: Name of the user
            assessment_date: Date of assessment (defaults to now)
            user_context: Additional user context for recommendations

        Returns:
            Complete ReportContent object with all sections
        """
        # Generate unique report ID
        report_id = f"RPT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

        if assessment_date is None:
            assessment_date = datetime.now()

        # Generate recommendations based on Big Five scores
        recommendation_result = self.recommendation_engine.generate_recommendations(
            big_five_scores.to_dict(),
            user_context or {}
        )

        # Build all sections
        sections = []

        # 1. Cover page
        cover_section = self.structure_builder.build_cover_page(
            user_name, assessment_date, report_id
        )
        sections.append(cover_section)

        # 2. Executive summary
        summary_section = self.structure_builder.build_executive_summary(
            recommendation_result.strength_profile,
            recommendation_result.job_recommendations,
            recommendation_result.summary_insights
        )
        sections.append(summary_section)

        # 3. Personality profile
        personality_section = self._build_personality_profile_section(
            big_five_scores, recommendation_result.strength_profile
        )
        sections.append(personality_section)

        # 4. Strength analysis
        strength_section = self.structure_builder.build_strength_analysis_section(
            recommendation_result.strength_profile,
            self.personalized_generator
        )
        sections.append(strength_section)

        # 5. Career recommendations
        career_section = self.structure_builder.build_career_recommendations_section(
            recommendation_result.job_recommendations,
            self.personalized_generator,
            recommendation_result.strength_profile
        )
        sections.append(career_section)

        # 6. Development plan
        development_section = self._build_development_plan_section(
            recommendation_result.development_plan
        )
        sections.append(development_section)

        return ReportContent(
            report_id=report_id,
            generation_timestamp=datetime.now(),
            user_name=user_name,
            assessment_date=assessment_date,
            sections=sections,
            metadata={
                "big_five_scores": big_five_scores.to_dict(),
                "recommendation_result": recommendation_result,
                "confidence_score": recommendation_result.confidence_score
            }
        )

    def _build_personality_profile_section(
        self,
        big_five_scores: DimensionScores,
        strength_profile: StrengthProfile
    ) -> ContentSection:
        """Build personality profile section."""
        elements = []

        # Section title
        elements.append(Paragraph("個性特質分析", self.template.styles['Heading1']))

        # Personality description
        personality_descriptions = self.personalized_generator.generate_personality_description(
            big_five_scores, strength_profile
        )
        for description in personality_descriptions:
            elements.append(Paragraph(description, self.template.styles['Body']))
            elements.append(Spacer(1, 6))

        elements.append(Spacer(1, 10*mm))

        # Big Five scores table
        elements.append(Paragraph("Big Five 人格特質分數", self.template.styles['Heading2']))

        dimension_names = {
            "openness": "開放性 (Openness)",
            "conscientiousness": "嚴謹性 (Conscientiousness)",
            "extraversion": "外向性 (Extraversion)",
            "agreeableness": "親和性 (Agreeableness)",
            "neuroticism": "情緒穩定性 (Emotional Stability)"
        }

        table_data = [["人格維度", "分數", "描述"]]
        score_dict = big_five_scores.to_dict()

        for dimension, score in score_dict.items():
            name = dimension_names.get(dimension, dimension)

            # Convert score to description
            if score >= 16:
                level_desc = "高"
            elif score >= 12:
                level_desc = "中等偏高"
            elif score >= 8:
                level_desc = "中等偏低"
            else:
                level_desc = "低"

            table_data.append([name, f"{score:.1f}", level_desc])

        table = Table(table_data, colWidths=[70*mm, 25*mm, 40*mm])
        table.setStyle(self.template.create_table_style(header=True))
        elements.append(table)

        return ContentSection(
            section_type=ContentType.PERSONALITY_PROFILE,
            title="Personality Profile",
            chinese_title="個性特質分析",
            content_elements=elements,
            metadata={}
        )

    def _build_development_plan_section(
        self,
        development_plan: DevelopmentPlan
    ) -> ContentSection:
        """Build development plan section."""
        elements = []

        # Section title
        elements.append(Paragraph("發展計劃", self.template.styles['Heading1']))

        # Priority areas
        if development_plan and development_plan.priority_areas:
            elements.append(Paragraph("優先發展領域", self.template.styles['Heading2']))
            for area in development_plan.priority_areas[:3]:
                elements.append(Paragraph(f"• {area}", self.template.styles['Bullet']))

        elements.append(Spacer(1, 10*mm))

        # Action items
        if development_plan and development_plan.action_items:
            elements.append(Paragraph("具體行動建議", self.template.styles['Heading2']))
            for action in development_plan.action_items[:5]:
                elements.append(Paragraph(f"• {action}", self.template.styles['Bullet']))

        elements.append(Spacer(1, 10*mm))

        # Resources
        if development_plan and development_plan.recommended_resources:
            elements.append(Paragraph("推薦資源", self.template.styles['Heading2']))
            for resource in development_plan.recommended_resources[:3]:
                elements.append(Paragraph(f"• {resource}", self.template.styles['Bullet']))

        return ContentSection(
            section_type=ContentType.DEVELOPMENT_PLAN,
            title="Development Plan",
            chinese_title="發展計劃",
            content_elements=elements,
            metadata={}
        )

    def get_content_statistics(self, report_content: ReportContent) -> Dict[str, Any]:
        """
        Get statistics about generated report content.

        Args:
            report_content: Generated report content

        Returns:
            Dictionary with content statistics
        """
        stats = {
            "total_sections": len(report_content.sections),
            "total_elements": sum(len(section.content_elements) for section in report_content.sections),
            "sections_by_type": {},
            "generation_time": report_content.generation_timestamp,
            "report_id": report_content.report_id
        }

        for section in report_content.sections:
            section_type = section.section_type.value
            stats["sections_by_type"][section_type] = {
                "title": section.chinese_title,
                "element_count": len(section.content_elements)
            }

        return stats