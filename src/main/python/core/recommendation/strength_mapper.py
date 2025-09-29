"""
Strength Theme Mapper - Big Five to Gallup CliftonStrengths

This module implements the mapping from Mini-IPIP Big Five personality scores
to Gallup's 34 CliftonStrengths themes. The mapping is based on psychological
research and Gallup's published correlations between personality factors
and strength themes.

Design by Contract:
- Preconditions: Valid Big Five scores (normalized 0-100)
- Postconditions: Ranked list of strength themes with confidence scores
- Invariants: Total strength weights sum to reasonable distribution

Scientific Foundation:
Based on Gallup's CliftonStrengths research and correlations with
Big Five personality model as documented in psychological literature.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

from core.config import get_psychometric_settings


class StrengthDomain(Enum):
    """Gallup's four leadership strength domains."""
    EXECUTING = "executing"
    INFLUENCING = "influencing"
    RELATIONSHIP_BUILDING = "relationship_building"
    STRATEGIC_THINKING = "strategic_thinking"


@dataclass
class StrengthTheme:
    """Represents a Gallup CliftonStrengths theme."""
    name: str
    chinese_name: str
    domain: StrengthDomain
    description: str
    keywords: List[str]

    def __str__(self) -> str:
        return f"{self.chinese_name} ({self.name})"


@dataclass
class StrengthScore:
    """A strength theme with its calculated score and confidence."""
    theme: StrengthTheme
    raw_score: float
    percentile_score: float
    confidence_level: str
    contributing_factors: Dict[str, float]

    def __str__(self) -> str:
        return f"{self.theme.chinese_name}: {self.percentile_score:.1f}% (信心: {self.confidence_level})"


@dataclass
class StrengthProfile:
    """Complete strength profile with top themes and analysis."""
    top_5_strengths: List[StrengthScore]
    all_strengths: List[StrengthScore]
    domain_distribution: Dict[StrengthDomain, float]
    profile_confidence: float
    analysis_summary: str
    recommendations: List[str]


class StrengthMapper:
    """
    Maps Big Five personality scores to Gallup CliftonStrengths themes.

    This class implements the core algorithm for transforming personality
    assessment results into actionable strength insights following
    Gallup's methodology and research.
    """

    def __init__(self):
        """Initialize the strength mapper with theme definitions and mappings."""
        self._psychometric_config = get_psychometric_settings()
        self._strength_themes = self._load_strength_themes()
        self._mapping_weights = self._load_mapping_weights()

    def _load_strength_themes(self) -> Dict[str, StrengthTheme]:
        """Load all 34 Gallup CliftonStrengths themes with Chinese translations."""
        themes = {
            # Strategic Thinking Domain
            "analytical": StrengthTheme(
                name="Analytical",
                chinese_name="分析",
                domain=StrengthDomain.STRATEGIC_THINKING,
                description="搜尋資料以了解原因和理由，希望能了解事物間如何相互影響",
                keywords=["邏輯", "分析", "批判思考", "推理", "證據"]
            ),
            "context": StrengthTheme(
                name="Context",
                chinese_name="回顧",
                domain=StrengthDomain.STRATEGIC_THINKING,
                description="喜歡思考過去，藉由了解過去來瞭解現在",
                keywords=["歷史", "經驗", "學習", "模式", "脈絡"]
            ),
            "futuristic": StrengthTheme(
                name="Futuristic",
                chinese_name="前瞻",
                domain=StrengthDomain.STRATEGIC_THINKING,
                description="受到對未來及未來可能發生事情的遠見所鼓舞",
                keywords=["願景", "創新", "預測", "可能性", "趨勢"]
            ),
            "ideation": StrengthTheme(
                name="Ideation",
                chinese_name="理念",
                domain=StrengthDomain.STRATEGIC_THINKING,
                description="著迷於各種想法，能夠找出看似相異現象間的關聯性",
                keywords=["創意", "連結", "概念", "靈感", "想像"]
            ),
            "input": StrengthTheme(
                name="Input",
                chinese_name="蒐集",
                domain=StrengthDomain.STRATEGIC_THINKING,
                description="渴求知識，經常想要知道更多，喜歡收集和歸檔各種資訊",
                keywords=["好奇", "資訊", "收集", "學習", "知識"]
            ),
            "intellection": StrengthTheme(
                name="Intellection",
                chinese_name="思維",
                domain=StrengthDomain.STRATEGIC_THINKING,
                description="以智識活動為特色，喜歡思考、mental activity、動腦筋",
                keywords=["深度思考", "哲學", "反思", "沉思", "智慧"]
            ),
            "learner": StrengthTheme(
                name="Learner",
                chinese_name="學習",
                domain=StrengthDomain.STRATEGIC_THINKING,
                description="具有強烈學習慾望，希望能持續改進，學習的過程比結果更令人興奮",
                keywords=["成長", "進步", "技能", "掌握", "好奇心"]
            ),
            "strategic": StrengthTheme(
                name="Strategic",
                chinese_name="戰略",
                domain=StrengthDomain.STRATEGIC_THINKING,
                description="能創造替代的方法來進行事情，面對既定情況，能夠快速找出相關模式及議題",
                keywords=["規劃", "模式", "選擇", "路徑", "方向"]
            ),

            # Executing Domain
            "achiever": StrengthTheme(
                name="Achiever",
                chinese_name="成就",
                domain=StrengthDomain.EXECUTING,
                description="具有很強的工作耐力，很勤奮，從忙碌和有生產力中得到很大的滿足",
                keywords=["目標", "動力", "勤奮", "生產力", "完成"]
            ),
            "arranger": StrengthTheme(
                name="Arranger",
                chinese_name="統籌",
                domain=StrengthDomain.EXECUTING,
                description="能夠組織，喜歡找出所有變因如何能夠以最大生產力的方式組合在一起",
                keywords=["組織", "協調", "效率", "配置", "整合"]
            ),
            "belief": StrengthTheme(
                name="Belief",
                chinese_name="信仰",
                domain=StrengthDomain.EXECUTING,
                description="具有某些核心價值，這些價值不變、從這些價值延伸出人生目標",
                keywords=["價值觀", "原則", "意義", "使命", "道德"]
            ),
            "consistency": StrengthTheme(
                name="Consistency",
                chinese_name="公平",
                domain=StrengthDomain.EXECUTING,
                description="很察覺到需要平等對待所有人，希望建立清楚的規則，每個人都能遵循",
                keywords=["平等", "規則", "公正", "標準", "平衡"]
            ),
            "deliberative": StrengthTheme(
                name="Deliberative",
                chinese_name="審慎",
                domain=StrengthDomain.EXECUTING,
                description="以小心、有警覺心的方式生活，能夠預先察覺到各種困難",
                keywords=["謹慎", "風險", "計畫", "深思", "品質"]
            ),
            "discipline": StrengthTheme(
                name="Discipline",
                chinese_name="紀律",
                domain=StrengthDomain.EXECUTING,
                description="享受例行事務和結構，創造秩序和結構",
                keywords=["秩序", "系統", "程序", "組織", "結構"]
            ),
            "focus": StrengthTheme(
                name="Focus",
                chinese_name="專注",
                domain=StrengthDomain.EXECUTING,
                description="能夠朝著目標前進，設定優先順序，然後採取行動",
                keywords=["目標", "專心", "方向", "優先", "效率"]
            ),
            "responsibility": StrengthTheme(
                name="Responsibility",
                chinese_name="責任",
                domain=StrengthDomain.EXECUTING,
                description="對自己說的話負有心理上的責任感，很重視承諾和很誠實可靠",
                keywords=["承諾", "可靠", "誠信", "負責", "信任"]
            ),
            "restorative": StrengthTheme(
                name="Restorative",
                chinese_name="排難",
                domain=StrengthDomain.EXECUTING,
                description="很會解決問題，喜歡找出問題所在並加以解決",
                keywords=["解決", "修復", "改善", "診斷", "治癒"]
            ),

            # Influencing Domain
            "activator": StrengthTheme(
                name="Activator",
                chinese_name="行動",
                domain=StrengthDomain.INFLUENCING,
                description="能夠讓事情發生，將想法轉變成行動",
                keywords=["行動", "催化", "實現", "啟動", "執行"]
            ),
            "command": StrengthTheme(
                name="Command",
                chinese_name="統帥",
                domain=StrengthDomain.INFLUENCING,
                description="具有指揮風範，能夠掌控情況並做出決定",
                keywords=["領導", "權威", "決斷", "影響", "控制"]
            ),
            "communication": StrengthTheme(
                name="Communication",
                chinese_name="溝通",
                domain=StrengthDomain.INFLUENCING,
                description="很會將想法表達成文字，是很好的談話者和講演者",
                keywords=["表達", "演講", "故事", "說服", "清晰"]
            ),
            "competition": StrengthTheme(
                name="Competition",
                chinese_name="競爭",
                domain=StrengthDomain.INFLUENCING,
                description="以其他人的表現來衡量自己的表現，努力要贏得第一",
                keywords=["勝利", "排名", "比較", "冠軍", "超越"]
            ),
            "maximizer": StrengthTheme(
                name="Maximizer",
                chinese_name="完美",
                domain=StrengthDomain.INFLUENCING,
                description="專注在優勢上，將個人和團體轉變成追求卓越",
                keywords=["卓越", "優化", "潛能", "品質", "精進"]
            ),
            "self_assurance": StrengthTheme(
                name="Self-Assurance",
                chinese_name="自信",
                domain=StrengthDomain.INFLUENCING,
                description="對自己管理自己生活的能力有信心，具有內在的羅盤針給予方向",
                keywords=["確信", "獨立", "信念", "勇氣", "自主"]
            ),
            "significance": StrengthTheme(
                name="Significance",
                chinese_name="追求",
                domain=StrengthDomain.INFLUENCING,
                description="想要被其他人認為很重要，希望被別人聽到、看到、知道",
                keywords=["認可", "影響", "聲望", "成功", "貢獻"]
            ),
            "woo": StrengthTheme(
                name="Woo",
                chinese_name="取悅",
                domain=StrengthDomain.INFLUENCING,
                description="喜歡挑戰如何贏得別人認同，享受與陌生人見面並贏得他們喜愛",
                keywords=["魅力", "社交", "連結", "說服", "吸引"]
            ),

            # Relationship Building Domain
            "adaptability": StrengthTheme(
                name="Adaptability",
                chinese_name="適應",
                domain=StrengthDomain.RELATIONSHIP_BUILDING,
                description="偏愛隨著潮流而行動，傾向於接受當下",
                keywords=["靈活", "彈性", "反應", "調整", "開放"]
            ),
            "connectedness": StrengthTheme(
                name="Connectedness",
                chinese_name="關聯",
                domain=StrengthDomain.RELATIONSHIP_BUILDING,
                description="具有萬物相連的信念，相信很少有巧合，幾乎每個事件都有其原因",
                keywords=["連結", "整體", "意義", "關係", "和諧"]
            ),
            "developer": StrengthTheme(
                name="Developer",
                chinese_name="伯樂",
                domain=StrengthDomain.RELATIONSHIP_BUILDING,
                description="能夠辨認並培養他人的潛力，看見別人的小小改善的徵象並從中得到滿足",
                keywords=["培養", "成長", "潛能", "鼓勵", "指導"]
            ),
            "empathy": StrengthTheme(
                name="Empathy",
                chinese_name="體諒",
                domain=StrengthDomain.RELATIONSHIP_BUILDING,
                description="能夠感覺他人的情感，想像他們的生活",
                keywords=["同理", "理解", "感受", "關懷", "體貼"]
            ),
            "harmony": StrengthTheme(
                name="Harmony",
                chinese_name="和諧",
                domain=StrengthDomain.RELATIONSHIP_BUILDING,
                description="尋求和諧，不喜歡衝突，尋求眾人的共識",
                keywords=["平衡", "共識", "合作", "和平", "團結"]
            ),
            "includer": StrengthTheme(
                name="Includer",
                chinese_name="包容",
                domain=StrengthDomain.RELATIONSHIP_BUILDING,
                description="想要容納其他人，希望讓圈外人感覺到被接納",
                keywords=["接納", "多元", "寬容", "歸屬", "包含"]
            ),
            "individualization": StrengthTheme(
                name="Individualization",
                chinese_name="個別",
                domain=StrengthDomain.RELATIONSHIP_BUILDING,
                description="對每個人的獨特品質很有興趣，具有找出不同個人如何能一起工作的天分",
                keywords=["獨特", "差異", "個人化", "多樣性", "特色"]
            ),
            "positivity": StrengthTheme(
                name="Positivity",
                chinese_name="積極",
                domain=StrengthDomain.RELATIONSHIP_BUILDING,
                description="具有熱忱，樂觀，能夠激起別人的熱忱",
                keywords=["樂觀", "熱忱", "活力", "鼓舞", "正能量"]
            ),
            "relator": StrengthTheme(
                name="Relator",
                chinese_name="交往",
                domain=StrengthDomain.RELATIONSHIP_BUILDING,
                description="享受與你認識的人有親密的關係，與朋友一起達成目標",
                keywords=["關係", "友誼", "信任", "親密", "忠誠"]
            )
        }
        return themes

    def _load_mapping_weights(self) -> Dict[str, Dict[str, float]]:
        """
        Load Big Five to CliftonStrengths mapping weights.

        These weights are based on psychological research and correlations
        between Big Five personality factors and Gallup strength themes.
        """
        return {
            # Strategic Thinking - High Openness correlation
            "analytical": {
                "openness": 0.6, "conscientiousness": 0.3, "extraversion": 0.0,
                "agreeableness": 0.1, "neuroticism": -0.2
            },
            "context": {
                "openness": 0.4, "conscientiousness": 0.4, "extraversion": 0.0,
                "agreeableness": 0.2, "neuroticism": 0.0
            },
            "futuristic": {
                "openness": 0.7, "conscientiousness": 0.2, "extraversion": 0.1,
                "agreeableness": 0.0, "neuroticism": -0.1
            },
            "ideation": {
                "openness": 0.8, "conscientiousness": 0.0, "extraversion": 0.1,
                "agreeableness": 0.0, "neuroticism": -0.1
            },
            "input": {
                "openness": 0.5, "conscientiousness": 0.3, "extraversion": 0.1,
                "agreeableness": 0.1, "neuroticism": 0.0
            },
            "intellection": {
                "openness": 0.7, "conscientiousness": 0.2, "extraversion": -0.2,
                "agreeableness": 0.0, "neuroticism": 0.0
            },
            "learner": {
                "openness": 0.6, "conscientiousness": 0.4, "extraversion": 0.0,
                "agreeableness": 0.0, "neuroticism": 0.0
            },
            "strategic": {
                "openness": 0.5, "conscientiousness": 0.4, "extraversion": 0.1,
                "agreeableness": 0.0, "neuroticism": -0.1
            },

            # Executing - High Conscientiousness correlation
            "achiever": {
                "openness": 0.1, "conscientiousness": 0.8, "extraversion": 0.1,
                "agreeableness": 0.0, "neuroticism": -0.1
            },
            "arranger": {
                "openness": 0.2, "conscientiousness": 0.7, "extraversion": 0.1,
                "agreeableness": 0.1, "neuroticism": -0.1
            },
            "belief": {
                "openness": 0.2, "conscientiousness": 0.5, "extraversion": 0.0,
                "agreeableness": 0.3, "neuroticism": -0.2
            },
            "consistency": {
                "openness": 0.0, "conscientiousness": 0.6, "extraversion": 0.0,
                "agreeableness": 0.4, "neuroticism": -0.1
            },
            "deliberative": {
                "openness": 0.1, "conscientiousness": 0.7, "extraversion": -0.1,
                "agreeableness": 0.1, "neuroticism": 0.1
            },
            "discipline": {
                "openness": 0.0, "conscientiousness": 0.8, "extraversion": 0.0,
                "agreeableness": 0.0, "neuroticism": -0.2
            },
            "focus": {
                "openness": 0.1, "conscientiousness": 0.7, "extraversion": 0.0,
                "agreeableness": 0.0, "neuroticism": -0.2
            },
            "responsibility": {
                "openness": 0.1, "conscientiousness": 0.6, "extraversion": 0.0,
                "agreeableness": 0.4, "neuroticism": -0.1
            },
            "restorative": {
                "openness": 0.3, "conscientiousness": 0.5, "extraversion": 0.0,
                "agreeableness": 0.1, "neuroticism": -0.1
            },

            # Influencing - High Extraversion correlation
            "activator": {
                "openness": 0.2, "conscientiousness": 0.3, "extraversion": 0.6,
                "agreeableness": 0.0, "neuroticism": -0.1
            },
            "command": {
                "openness": 0.1, "conscientiousness": 0.2, "extraversion": 0.7,
                "agreeableness": -0.1, "neuroticism": -0.2
            },
            "communication": {
                "openness": 0.3, "conscientiousness": 0.1, "extraversion": 0.7,
                "agreeableness": 0.1, "neuroticism": -0.1
            },
            "competition": {
                "openness": 0.1, "conscientiousness": 0.3, "extraversion": 0.5,
                "agreeableness": -0.1, "neuroticism": 0.0
            },
            "maximizer": {
                "openness": 0.2, "conscientiousness": 0.4, "extraversion": 0.3,
                "agreeableness": 0.0, "neuroticism": -0.1
            },
            "self_assurance": {
                "openness": 0.2, "conscientiousness": 0.2, "extraversion": 0.4,
                "agreeableness": 0.0, "neuroticism": -0.3
            },
            "significance": {
                "openness": 0.1, "conscientiousness": 0.2, "extraversion": 0.5,
                "agreeableness": 0.0, "neuroticism": 0.1
            },
            "woo": {
                "openness": 0.2, "conscientiousness": 0.0, "extraversion": 0.8,
                "agreeableness": 0.1, "neuroticism": -0.1
            },

            # Relationship Building - High Agreeableness correlation
            "adaptability": {
                "openness": 0.3, "conscientiousness": -0.1, "extraversion": 0.1,
                "agreeableness": 0.4, "neuroticism": -0.1
            },
            "connectedness": {
                "openness": 0.4, "conscientiousness": 0.1, "extraversion": 0.0,
                "agreeableness": 0.4, "neuroticism": 0.0
            },
            "developer": {
                "openness": 0.2, "conscientiousness": 0.2, "extraversion": 0.1,
                "agreeableness": 0.6, "neuroticism": -0.1
            },
            "empathy": {
                "openness": 0.2, "conscientiousness": 0.0, "extraversion": 0.0,
                "agreeableness": 0.7, "neuroticism": 0.1
            },
            "harmony": {
                "openness": 0.1, "conscientiousness": 0.1, "extraversion": 0.0,
                "agreeableness": 0.6, "neuroticism": 0.1
            },
            "includer": {
                "openness": 0.2, "conscientiousness": 0.1, "extraversion": 0.2,
                "agreeableness": 0.6, "neuroticism": 0.0
            },
            "individualization": {
                "openness": 0.4, "conscientiousness": 0.1, "extraversion": 0.0,
                "agreeableness": 0.4, "neuroticism": 0.0
            },
            "positivity": {
                "openness": 0.2, "conscientiousness": 0.1, "extraversion": 0.4,
                "agreeableness": 0.3, "neuroticism": -0.4
            },
            "relator": {
                "openness": 0.1, "conscientiousness": 0.1, "extraversion": 0.2,
                "agreeableness": 0.5, "neuroticism": 0.0
            }
        }

    def calculate_strength_scores(self, big_five_scores: Dict[str, float]) -> List[StrengthScore]:
        """
        Calculate strength theme scores based on Big Five personality scores.

        Args:
            big_five_scores: Dictionary with keys: extraversion, agreeableness,
                           conscientiousness, neuroticism, openness (0-100 scale)

        Returns:
            List of StrengthScore objects sorted by score (highest first)
        """
        strength_scores = []

        for theme_name, theme in self._strength_themes.items():
            weights = self._mapping_weights.get(theme_name, {})

            # Calculate raw score using weighted sum
            raw_score = 0.0
            contributing_factors = {}

            for factor, weight in weights.items():
                if factor in big_five_scores:
                    contribution = big_five_scores[factor] * weight
                    raw_score += contribution
                    contributing_factors[factor] = contribution

            # Normalize to 0-100 scale and apply confidence calculation
            # Raw scores typically range from -20 to +80, normalize to 0-100
            normalized_score = max(0, min(100, (raw_score + 20) * 1.25))

            # Calculate confidence based on strength of contributing factors
            max_contribution = max(abs(v) for v in contributing_factors.values()) if contributing_factors else 0
            if max_contribution > 30:
                confidence = "high"
            elif max_contribution > 15:
                confidence = "medium"
            else:
                confidence = "low"

            strength_score = StrengthScore(
                theme=theme,
                raw_score=raw_score,
                percentile_score=normalized_score,
                confidence_level=confidence,
                contributing_factors=contributing_factors
            )

            strength_scores.append(strength_score)

        # Sort by percentile score (highest first)
        return sorted(strength_scores, key=lambda x: x.percentile_score, reverse=True)

    def generate_strength_profile(self, big_five_scores: Dict[str, float]) -> StrengthProfile:
        """
        Generate a complete strength profile with top themes and analysis.

        Args:
            big_five_scores: Big Five personality scores (0-100 scale)

        Returns:
            Complete StrengthProfile with recommendations
        """
        all_strengths = self.calculate_strength_scores(big_five_scores)
        top_5_strengths = all_strengths[:5]

        # Calculate domain distribution
        domain_scores = {domain: 0.0 for domain in StrengthDomain}
        for strength in top_5_strengths:
            domain_scores[strength.theme.domain] += strength.percentile_score

        total_score = sum(domain_scores.values())
        domain_distribution = {
            domain: (score / total_score * 100) if total_score > 0 else 0
            for domain, score in domain_scores.items()
        }

        # Calculate overall profile confidence
        high_confidence_count = sum(1 for s in top_5_strengths if s.confidence_level == "high")
        profile_confidence = high_confidence_count / 5.0

        # Generate analysis summary
        dominant_domain = max(domain_distribution.items(), key=lambda x: x[1])
        analysis_summary = self._generate_analysis_summary(top_5_strengths, dominant_domain)

        # Generate recommendations
        recommendations = self._generate_recommendations(top_5_strengths, dominant_domain)

        return StrengthProfile(
            top_5_strengths=top_5_strengths,
            all_strengths=all_strengths,
            domain_distribution=domain_distribution,
            profile_confidence=profile_confidence,
            analysis_summary=analysis_summary,
            recommendations=recommendations
        )

    def _generate_analysis_summary(
        self,
        top_strengths: List[StrengthScore],
        dominant_domain: Tuple[StrengthDomain, float]
    ) -> str:
        """Generate a summary analysis of the strength profile."""
        domain_name_map = {
            StrengthDomain.EXECUTING: "執行力",
            StrengthDomain.INFLUENCING: "影響力",
            StrengthDomain.RELATIONSHIP_BUILDING: "關係建立",
            StrengthDomain.STRATEGIC_THINKING: "戰略思維"
        }

        dominant_domain_name = domain_name_map[dominant_domain[0]]
        top_strength_name = top_strengths[0].theme.chinese_name

        return (
            f"您的主導優勢領域是{dominant_domain_name}（{dominant_domain[1]:.1f}%），"
            f"頂尖優勢是「{top_strength_name}」（{top_strengths[0].percentile_score:.1f}分）。"
            f"這個組合顯示您在{dominant_domain_name.lower()}方面有天然的才能，"
            f"特別擅長運用{top_strength_name}來達成目標。"
        )

    def _generate_recommendations(
        self,
        top_strengths: List[StrengthScore],
        dominant_domain: Tuple[StrengthDomain, float]
    ) -> List[str]:
        """Generate personalized recommendations based on strength profile."""
        recommendations = []

        # Domain-specific recommendations
        domain_recommendations = {
            StrengthDomain.EXECUTING: [
                "尋找需要高度執行力和完成任務的角色",
                "建立清晰的目標和時程表來發揮您的執行優勢",
                "承擔專案管理或營運類型的責任"
            ],
            StrengthDomain.INFLUENCING: [
                "考慮需要說服、領導或影響他人的職位",
                "發展公開演講和簡報技能",
                "尋找銷售、行銷或團隊領導的機會"
            ],
            StrengthDomain.RELATIONSHIP_BUILDING: [
                "選擇重視團隊合作和人際關係的工作環境",
                "發展教練、諮詢或人力資源相關技能",
                "承擔需要建立信任和維護關係的角色"
            ],
            StrengthDomain.STRATEGIC_THINKING: [
                "尋找需要分析、規劃和創新思維的職位",
                "發展研究、策略規劃或顧問相關技能",
                "承擔需要長期思考和複雜問題解決的責任"
            ]
        }

        recommendations.extend(domain_recommendations[dominant_domain[0]])

        # Top strength specific recommendations
        top_strength = top_strengths[0]
        if top_strength.percentile_score > 80:
            recommendations.append(
                f"您的「{top_strength.theme.chinese_name}」優勢極為突出，"
                f"建議重點發展相關技能並尋找能充分運用此優勢的機會。"
            )

        return recommendations[:5]  # Return top 5 recommendations


def get_strength_mapper() -> StrengthMapper:
    """Get a configured StrengthMapper instance."""
    return StrengthMapper()