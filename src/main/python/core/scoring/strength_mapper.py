"""
優勢映射引擎
將 Big Five 人格分數映射到 12 個 Gallup 風格的優勢面向

基於統一職涯知識庫的映射方法，確保與職涯推薦系統的數據一致性
支援可解釋性追蹤與信心評估
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import math
from .mini_ipip_scorer import BigFiveScores, ScoreConfidence
from ..knowledge.career_knowledge_base import get_career_knowledge_base, StrengthCategory


# 使用統一知識庫中的 StrengthCategory，移除重複定義


@dataclass
class StrengthResult:
    """單一優勢結果"""
    name: str
    display_name: str
    score: float                 # 0-100 分數
    percentile: float           # 百分位數
    confidence: ScoreConfidence
    category: StrengthCategory

    # 計算溯源
    primary_factor: str
    primary_contribution: float
    secondary_factors: Dict[str, float]
    weight_formula: str

    # 描述與建議（從統一知識庫獲取）
    description: str
    job_matches: List[str] = field(default_factory=list)  # 從知識庫動態生成
    development_suggestions: List[str] = field(default_factory=list)  # 從知識庫動態生成

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "score": round(self.score, 2),
            "percentile": round(self.percentile, 2),
            "confidence": self.confidence.value,
            "category": self.category.value,
            "provenance": {
                "primary_factor": self.primary_factor,
                "primary_contribution": round(self.primary_contribution, 2),
                "secondary_factors": {
                    k: round(v, 2) for k, v in self.secondary_factors.items()
                },
                "weight_formula": self.weight_formula
            },
            "description": self.description,
            "job_matches": self.job_matches,
            "development_suggestions": self.development_suggestions
        }


@dataclass
class StrengthsProfile:
    """完整優勢檔案"""
    top_strengths: List[StrengthResult]        # 前5名優勢
    all_strengths: List[StrengthResult]        # 全部12個優勢
    dominant_category: StrengthCategory         # 主導類別

    # 統計摘要
    mean_score: float
    score_range: float
    confidence_distribution: Dict[str, int]

    # 職涯建議
    recommended_roles: List[str]
    development_priorities: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "top_strengths": [s.to_dict() for s in self.top_strengths],
            "all_strengths": [s.to_dict() for s in self.all_strengths],
            "dominant_category": self.dominant_category.value,
            "statistics": {
                "mean_score": round(self.mean_score, 2),
                "score_range": round(self.score_range, 2),
                "confidence_distribution": self.confidence_distribution
            },
            "recommendations": {
                "roles": self.recommended_roles,
                "development_priorities": self.development_priorities
            }
        }


class StrengthMapper:
    """優勢映射引擎 - 使用統一職涯知識庫"""

    def __init__(self):
        """初始化優勢映射引擎"""
        self.knowledge_base = get_career_knowledge_base()

    # 保留原有映射配置作為備用（已廢棄，改用統一知識庫）
    DEPRECATED_STRENGTH_MAPPINGS = {
        "structured_execution": {
            "display_name": "結構化執行",
            "category": StrengthCategory.EXECUTION,
            "primary_factor": "conscientiousness",
            "weight_formula": "0.8 * C + 0.2 * (100 - N)",
            "description": "擅長建立系統、流程，確保工作有條不紊地完成",
            "job_matches": ["專案經理", "營運經理", "系統分析師", "品質管理師"],
            "development_suggestions": [
                "學習先進的專案管理方法論",
                "培養跨部門協調能力",
                "提升數據分析與決策技能"
            ]
        },

        "quality_perfectionism": {
            "display_name": "品質與完備",
            "category": StrengthCategory.EXECUTION,
            "primary_factor": "conscientiousness",
            "weight_formula": "0.7 * C + 0.3 * O",
            "description": "對品質有高標準，追求工作的完整性與精確性",
            "job_matches": ["品質保證工程師", "審計師", "研發工程師", "醫療專業人員"],
            "development_suggestions": [
                "學習平衡完美主義與效率",
                "發展領導他人追求卓越的能力",
                "培養創新思維以提升品質標準"
            ]
        },

        "exploration_innovation": {
            "display_name": "探索與創新",
            "category": StrengthCategory.THINKING,
            "primary_factor": "openness",
            "weight_formula": "0.8 * O + 0.2 * E",
            "description": "具有強烈的好奇心，善於探索新想法和創新解決方案",
            "job_matches": ["產品經理", "創意總監", "研究員", "新創企業家"],
            "development_suggestions": [
                "參與跨領域學習與合作",
                "建立創新想法的實作能力",
                "學習將創意轉化為商業價值"
            ]
        },

        "analytical_insight": {
            "display_name": "分析與洞察",
            "category": StrengthCategory.THINKING,
            "primary_factor": "openness",
            "weight_formula": "0.6 * O + 0.4 * C",
            "description": "能深入分析複雜問題，從資料中發現重要洞察",
            "job_matches": ["數據分析師", "策略顧問", "市場研究員", "學術研究者"],
            "development_suggestions": [
                "加強數據科學與統計技能",
                "學習商業分析與決策支援",
                "培養將洞察轉化為行動的能力"
            ]
        },

        "influence_advocacy": {
            "display_name": "影響與倡議",
            "category": StrengthCategory.INFLUENCING,
            "primary_factor": "extraversion",
            "weight_formula": "0.7 * E + 0.3 * C",
            "description": "能有效影響他人，推動重要倡議並獲得支持",
            "job_matches": ["業務經理", "公關經理", "政治工作者", "社會運動者"],
            "development_suggestions": [
                "提升演講與簡報技巧",
                "學習談判與說服技術",
                "培養社群經營與網絡建立能力"
            ]
        },

        "collaboration_harmony": {
            "display_name": "協作與共好",
            "category": StrengthCategory.RELATIONSHIP,
            "primary_factor": "agreeableness",
            "weight_formula": "0.7 * A + 0.3 * E",
            "description": "擅長團隊合作，促進和諧關係並達成共同目標",
            "job_matches": ["人力資源專員", "團隊領導者", "客戶服務經理", "非營利組織工作者"],
            "development_suggestions": [
                "學習衝突管理與調解技巧",
                "提升團隊建設與激勵能力",
                "培養跨文化溝通技能"
            ]
        },

        "customer_orientation": {
            "display_name": "客戶導向",
            "category": StrengthCategory.RELATIONSHIP,
            "primary_factor": "agreeableness",
            "weight_formula": "0.6 * A + 0.4 * E",
            "description": "以客戶需求為中心，建立長期信任關係",
            "job_matches": ["客戶成功經理", "銷售代表", "服務設計師", "客戶體驗專員"],
            "development_suggestions": [
                "深入了解客戶行為與需求分析",
                "學習客戶關係管理系統",
                "培養服務設計思維"
            ]
        },

        "learning_growth": {
            "display_name": "學習與成長",
            "category": StrengthCategory.THINKING,
            "primary_factor": "openness",
            "weight_formula": "0.7 * O + 0.3 * C",
            "description": "持續學習新知識，追求個人與專業成長",
            "job_matches": ["培訓師", "教育工作者", "組織發展專員", "職涯顧問"],
            "development_suggestions": [
                "建立個人知識管理系統",
                "發展教學與指導他人的能力",
                "學習成人學習理論與方法"
            ]
        },

        "discipline_trust": {
            "display_name": "紀律與信任",
            "category": StrengthCategory.EXECUTION,
            "primary_factor": "conscientiousness",
            "weight_formula": "0.8 * C + 0.2 * A",
            "description": "具有強烈的自律精神，值得他人信任與依賴",
            "job_matches": ["財務經理", "合規專員", "專案執行經理", "營運主管"],
            "development_suggestions": [
                "發展領導他人建立紀律的能力",
                "學習風險管理與合規知識",
                "培養組織文化建設技能"
            ]
        },

        "stress_regulation": {
            "display_name": "壓力調節",
            "category": StrengthCategory.EXECUTION,
            "primary_factor": "neuroticism_reversed",
            "weight_formula": "0.8 * (100 - N) + 0.2 * C",
            "description": "在高壓環境中保持冷靜，有效調節壓力",
            "job_matches": ["急診醫護人員", "危機處理專員", "高階主管", "軍警消防人員"],
            "development_suggestions": [
                "學習壓力管理與情緒調節技巧",
                "培養危機處理與決策能力",
                "發展指導他人抗壓的技能"
            ]
        },

        "conflict_integration": {
            "display_name": "衝突整合",
            "category": StrengthCategory.RELATIONSHIP,
            "primary_factor": "agreeableness",
            "weight_formula": "0.6 * A + 0.4 * (100 - N)",
            "description": "善於處理衝突，將不同觀點整合為共識",
            "job_matches": ["調解員", "談判專家", "組織發展顧問", "外交人員"],
            "development_suggestions": [
                "學習調解與仲裁技術",
                "培養多元觀點整合能力",
                "發展跨文化溝通與理解技能"
            ]
        },

        "responsibility_accountability": {
            "display_name": "責任與當責",
            "category": StrengthCategory.EXECUTION,
            "primary_factor": "conscientiousness",
            "weight_formula": "0.7 * C + 0.3 * A",
            "description": "承擔責任，對結果負責，值得信賴",
            "job_matches": ["部門主管", "專案負責人", "財務主管", "法務專員"],
            "development_suggestions": [
                "提升當責文化的建立能力",
                "學習授權與監督技巧",
                "發展成果導向的管理思維"
            ]
        }
    }

    # 移除舊的 __init__ 方法，已在上方重新定義

    def map_strengths(self, big_five_scores: BigFiveScores) -> StrengthsProfile:
        """
        將 Big Five 分數映射為優勢檔案

        Args:
            big_five_scores: Big Five 分數結果

        Returns:
            StrengthsProfile: 完整優勢檔案
        """
        # 提取標準化分數
        scores = {
            "E": big_five_scores.standardized_extraversion,
            "A": big_five_scores.standardized_agreeableness,
            "C": big_five_scores.standardized_conscientiousness,
            "N": big_five_scores.standardized_neuroticism,
            "O": big_five_scores.standardized_openness
        }

        # 計算每個優勢的分數 - 使用統一知識庫
        all_strengths = []
        strength_themes = self.knowledge_base.get_all_strength_themes()

        for strength_id, strength_theme in strength_themes.items():
            strength_result = self._calculate_strength_score_from_knowledge_base(
                strength_id, strength_theme, scores, big_five_scores.confidence_level
            )
            all_strengths.append(strength_result)

        # 排序並選出前5名
        all_strengths.sort(key=lambda x: x.score, reverse=True)
        top_strengths = all_strengths[:5]

        # 分析主導類別
        dominant_category = self._identify_dominant_category(top_strengths)

        # 計算統計摘要
        mean_score = sum(s.score for s in all_strengths) / len(all_strengths)
        score_range = max(s.score for s in all_strengths) - min(s.score for s in all_strengths)

        confidence_distribution = {}
        for conf in ScoreConfidence:
            confidence_distribution[conf.value] = sum(
                1 for s in all_strengths if s.confidence == conf
            )

        # 生成職涯建議 - 使用統一知識庫
        recommended_roles = self._generate_role_recommendations_from_knowledge_base(top_strengths)
        development_priorities = self._generate_development_priorities_from_knowledge_base(all_strengths)

        return StrengthsProfile(
            top_strengths=top_strengths,
            all_strengths=all_strengths,
            dominant_category=dominant_category,
            mean_score=mean_score,
            score_range=score_range,
            confidence_distribution=confidence_distribution,
            recommended_roles=recommended_roles,
            development_priorities=development_priorities
        )

    def _calculate_strength_score_from_knowledge_base(self, strength_id: str, strength_theme,
                                                     big_five_scores: Dict[str, float],
                                                     overall_confidence: ScoreConfidence) -> StrengthResult:
        """計算單一優勢分數 - 基於統一知識庫"""
        # 解析權重公式
        formula = strength_theme.weight_formula

        # 替換變數
        E, A, C, N, O = (big_five_scores[k] for k in ["E", "A", "C", "N", "O"])

        # 安全地計算分數
        try:
            # 使用 eval 計算公式 (在受控環境下安全)
            score = eval(formula, {"__builtins__": {}}, {
                "E": E, "A": A, "C": C, "N": N, "O": O
            })
        except:
            # 萬一公式有問題，使用主要因子分數
            primary_factor_key = strength_theme.primary_factor.upper()
            if primary_factor_key == "NEUROTICISM_REVERSED":
                score = 100 - N
            else:
                score = big_five_scores.get(primary_factor_key[0], 50)

        # 確保分數在 0-100 範圍內
        score = max(0, min(100, score))

        # 計算百分位數 (簡化版)
        percentile = self._calculate_percentile(score)

        # 分解貢獻度
        primary_factor = strength_theme.primary_factor
        primary_contribution, secondary_factors = self._decompose_contributions(
            formula, big_five_scores, score
        )

        # 評估信心等級
        confidence = self._assess_strength_confidence(
            score, primary_contribution, overall_confidence
        )

        # 從知識庫獲取職涯匹配和發展建議
        career_roles = self.knowledge_base.get_roles_for_strength(strength_id)
        job_matches = [role.chinese_name for role in career_roles[:4]]  # 取前4個

        development_suggestions = []
        for suggestion in strength_theme.development_suggestions[:3]:  # 取前3個
            development_suggestions.append(suggestion.title)

        return StrengthResult(
            name=strength_id,
            display_name=strength_theme.chinese_name,
            score=score,
            percentile=percentile,
            confidence=confidence,
            category=strength_theme.category,
            primary_factor=primary_factor,
            primary_contribution=primary_contribution,
            secondary_factors=secondary_factors,
            weight_formula=formula,
            description=strength_theme.description,
            job_matches=job_matches,
            development_suggestions=development_suggestions
        )

    def _calculate_percentile(self, score: float) -> float:
        """簡化的百分位數計算"""
        # 假設分數大致呈常態分佈，以50為中心
        if score <= 50:
            return max(1, score * 0.98)  # 0-50 映射到 1-49
        else:
            return min(99, 50 + (score - 50) * 0.98)  # 50-100 映射到 50-99

    def _decompose_contributions(self, formula: str, big_five_scores: Dict[str, float],
                                total_score: float) -> Tuple[float, Dict[str, float]]:
        """分解各因子的貢獻度"""
        E, A, C, N, O = (big_five_scores[k] for k in ["E", "A", "C", "N", "O"])

        # 簡化的貢獻度計算
        contributions = {}
        primary_contribution = 0

        # 分析公式中的係數
        if "0.8 * C" in formula:
            primary_contribution = 0.8 * C
            contributions["conscientiousness"] = 0.8 * C
        elif "0.7 * E" in formula:
            primary_contribution = 0.7 * E
            contributions["extraversion"] = 0.7 * E
        elif "0.8 * O" in formula:
            primary_contribution = 0.8 * O
            contributions["openness"] = 0.8 * O
        elif "0.7 * A" in formula:
            primary_contribution = 0.7 * A
            contributions["agreeableness"] = 0.7 * A
        elif "0.8 * (100 - N)" in formula:
            primary_contribution = 0.8 * (100 - N)
            contributions["emotional_stability"] = 0.8 * (100 - N)

        # 移除主要貢獻，剩下的作為次要貢獻
        secondary_total = total_score - primary_contribution
        secondary_factors = {k: v for k, v in contributions.items()
                           if v != primary_contribution}

        return primary_contribution, secondary_factors

    def _assess_strength_confidence(self, score: float, primary_contribution: float,
                                  overall_confidence: ScoreConfidence) -> ScoreConfidence:
        """評估單一優勢的信心等級"""
        # 基於分數的極端程度和整體信心等級
        if overall_confidence == ScoreConfidence.LOW:
            return ScoreConfidence.LOW

        if score > 75 or score < 25:  # 極端分數
            return ScoreConfidence.HIGH
        elif score > 65 or score < 35:  # 中等程度
            return ScoreConfidence.MEDIUM
        else:
            return ScoreConfidence.MEDIUM

    def _identify_dominant_category(self, top_strengths: List[StrengthResult]) -> StrengthCategory:
        """識別主導優勢類別"""
        category_counts = {}
        for strength in top_strengths:
            category = strength.category
            category_counts[category] = category_counts.get(category, 0) + 1

        return max(category_counts.keys(), key=lambda x: category_counts[x])

    def _generate_role_recommendations_from_knowledge_base(self, top_strengths: List[StrengthResult]) -> List[str]:
        """從統一知識庫生成職涯角色建議"""
        # 收集前5大優勢的優勢ID
        strength_ids = [s.name for s in top_strengths]

        # 使用知識庫的匹配演算法
        career_matches = self.knowledge_base.find_career_matches_by_strengths(strength_ids, top_n=8)

        # 返回角色名稱
        return [role.chinese_name for role, score in career_matches]

    def _generate_role_recommendations(self, top_strengths: List[StrengthResult]) -> List[str]:
        """生成職涯角色建議 - 舊版方法，保留作為備用"""
        role_frequency = {}

        for strength in top_strengths:
            for role in strength.job_matches:
                role_frequency[role] = role_frequency.get(role, 0) + 1

        # 選出出現最頻繁的職涯角色
        sorted_roles = sorted(role_frequency.items(), key=lambda x: x[1], reverse=True)
        return [role for role, _ in sorted_roles[:8]]  # 取前8個推薦角色

    def _generate_development_priorities_from_knowledge_base(self, all_strengths: List[StrengthResult]) -> List[str]:
        """從統一知識庫生成發展優先順序"""
        # 基於低分優勢生成發展建議
        weak_strengths = [s for s in all_strengths if s.score < 40]
        weak_strengths.sort(key=lambda x: x.score)  # 從最低分開始

        development_priorities = []

        # 從知識庫獲取發展建議
        for strength in weak_strengths[:3]:  # 取最需要發展的3個
            strength_theme = self.knowledge_base.get_strength_theme(strength.name)
            if strength_theme:
                for suggestion in strength_theme.development_suggestions[:2]:
                    development_priorities.append(suggestion.title)

        return development_priorities[:6]  # 最多6個發展建議

    def _generate_development_priorities(self, all_strengths: List[StrengthResult]) -> List[str]:
        """生成發展優先順序 - 舊版方法，保留作為備用"""
        # 基於低分優勢生成發展建議
        weak_strengths = [s for s in all_strengths if s.score < 40]
        weak_strengths.sort(key=lambda x: x.score)  # 從最低分開始

        development_priorities = []
        for strength in weak_strengths[:3]:  # 取最需要發展的3個
            development_priorities.extend(strength.development_suggestions[:2])

        return development_priorities[:6]  # 最多6個發展建議

    def get_strength_details(self, strength_name: str) -> Optional[Dict[str, Any]]:
        """取得特定優勢的詳細資訊 - 從統一知識庫獲取"""
        strength_theme = self.knowledge_base.get_strength_theme(strength_name)
        if strength_theme:
            return {
                "display_name": strength_theme.chinese_name,
                "category": strength_theme.category.value,
                "primary_factor": strength_theme.primary_factor,
                "weight_formula": strength_theme.weight_formula,
                "description": strength_theme.description,
                "behavioral_indicators": strength_theme.behavioral_indicators,
                "work_style_preferences": strength_theme.work_style_preferences
            }
        return None

    def customize_strength_mapping(self, strength_name: str,
                                 custom_config: Dict[str, Any]) -> None:
        """自訂優勢映射配置 - 已廢棄，請直接修改統一知識庫"""
        # 這個方法已不再使用，因為配置統一在知識庫中管理
        print(f"Warning: customize_strength_mapping is deprecated. Please modify the unified knowledge base directly.")

# Alias for backward compatibility with tests
StrengthMappingResult = StrengthsProfile
