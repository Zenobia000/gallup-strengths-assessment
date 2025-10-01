"""
才幹分類標準化模組
基於心理測量學原理的科學分類系統
使用 Stanine 和 T-score 標準而非任意百分位數
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
from enum import Enum
import numpy as np

class TalentTier(Enum):
    """才幹層級"""
    DOMINANT = "dominant"      # 主導才幹
    SUPPORTING = "supporting"  # 支援才幹
    DEVELOPING = "developing"  # 發展才幹

@dataclass
class TalentClassification:
    """才幹分類結果"""
    dimension: str
    percentile: float
    t_score: float
    stanine: int
    sten: int
    tier: TalentTier
    interpretation: str
    confidence: str

class ScientificTalentClassifier:
    """
    科學才幹分類器

    基於心理測量學標準的分類系統：
    1. 使用 Stanine (九分制) 作為主要分類標準
    2. 結合 T-score 進行驗證
    3. 考慮測量誤差和信賴區間
    4. 提供可解釋的分類依據
    """

    def __init__(self):
        self.classification_rules = self._setup_classification_rules()

    def _setup_classification_rules(self) -> Dict:
        """
        建立科學分類規則

        基於標準九分制 (Stanine) 分佈：
        - Stanine 1-2 (底部11%): 發展才幹 (Developing)
        - Stanine 3-4 (23-40%): 發展才幹 (Developing)
        - Stanine 5 (40-60%): 支援才幹 (Supporting)
        - Stanine 6-7 (60-89%): 支援才幹 (Supporting)
        - Stanine 8-9 (頂部11%): 主導才幹 (Dominant)

        更精確的分類使用 T-score 輔助驗證
        """
        return {
            "dominant": {
                "stanine_range": (8, 9),
                "percentile_min": 89.0,
                "t_score_min": 63.0,
                "description": "明顯優勢，表現突出",
                "interpretation": "此才幹是您的核心優勢，在相關情境中表現優異"
            },
            "supporting": {
                "stanine_range": (5, 7),
                "percentile_min": 40.0,
                "percentile_max": 89.0,
                "t_score_min": 40.0,
                "t_score_max": 63.0,
                "description": "穩定表現，可依賴運用",
                "interpretation": "此才幹為您的支援優勢，在適當情境下能有效發揮"
            },
            "developing": {
                "stanine_range": (1, 4),
                "percentile_max": 40.0,
                "t_score_max": 40.0,
                "description": "成長空間，值得培養",
                "interpretation": "此才幹有發展潛力，透過練習與學習可以提升"
            }
        }

    def classify_talents(self, norm_scores: Dict) -> Dict[str, List[TalentClassification]]:
        """
        對所有才幹進行科學分類

        Args:
            norm_scores: 從 NormativeScorer 獲得的常模分數

        Returns:
            分類後的才幹字典，按層級組織
        """
        classified_talents = {
            "dominant": [],
            "supporting": [],
            "developing": []
        }

        for dimension, norm_score in norm_scores.items():
            classification = self._classify_single_talent(norm_score)
            classified_talents[classification.tier.value].append(classification)

        # 按分數排序各組內的才幹
        for tier in classified_talents:
            classified_talents[tier].sort(
                key=lambda x: x.percentile,
                reverse=True
            )

        return classified_talents

    def _classify_single_talent(self, norm_score) -> TalentClassification:
        """
        對單一才幹進行科學分類

        使用多重判斷標準：
        1. 主要標準：Stanine 分數
        2. 驗證標準：T-score 和百分位數
        3. 邊界情況：使用信賴區間考量
        """
        percentile = norm_score.percentile
        t_score = norm_score.t_score
        stanine = norm_score.stanine

        # 主要分類邏輯：基於 Stanine
        if stanine >= 8:
            tier = TalentTier.DOMINANT
            confidence = "高" if stanine == 9 else "中高"
        elif stanine >= 5:
            tier = TalentTier.SUPPORTING
            confidence = "高" if stanine in [6, 7] else "中"
        else:
            tier = TalentTier.DEVELOPING
            confidence = "高" if stanine <= 2 else "中"

        # 邊界情況調整：考慮測量誤差
        tier, confidence = self._handle_boundary_cases(
            tier, percentile, t_score, stanine, confidence
        )

        # 獲取分類說明
        rule = self.classification_rules[tier.value]
        interpretation = rule["interpretation"]

        return TalentClassification(
            dimension=norm_score.dimension,
            percentile=percentile,
            t_score=t_score,
            stanine=stanine,
            sten=norm_score.sten,
            tier=tier,
            interpretation=interpretation,
            confidence=confidence
        )

    def _handle_boundary_cases(self,
                             initial_tier: TalentTier,
                             percentile: float,
                             t_score: float,
                             stanine: int,
                             confidence: str) -> Tuple[TalentTier, str]:
        """
        處理邊界情況，考慮測量誤差

        在分類邊界附近 (±2 percentile) 的分數需要更謹慎處理
        """

        # Stanine 7 邊界檢查 (Supporting vs Dominant)
        if stanine == 7:
            if percentile >= 87:  # 接近 Dominant 閾值
                if t_score >= 61:
                    return TalentTier.DOMINANT, "中"
            confidence = "中高"

        # Stanine 5 邊界檢查 (Developing vs Supporting)
        elif stanine == 5:
            if percentile <= 42:  # 接近 Developing 範圍
                if t_score <= 42:
                    return TalentTier.DEVELOPING, "中"
            confidence = "中"

        # Stanine 4 邊界檢查
        elif stanine == 4:
            if percentile >= 38:  # 接近 Supporting 範圍
                if t_score >= 38:
                    return TalentTier.SUPPORTING, "中低"
            confidence = "中高"

        return initial_tier, confidence

    def get_classification_summary(self,
                                 classified_talents: Dict[str, List]) -> Dict:
        """
        生成分類摘要報告

        包含：
        - 各層級數量統計
        - 分類分佈評估
        - 整體概況類型
        - 建議與解釋
        """
        total_talents = sum(len(talents) for talents in classified_talents.values())

        summary = {
            "total_talents": total_talents,
            "distribution": {
                "dominant": {
                    "count": len(classified_talents["dominant"]),
                    "percentage": len(classified_talents["dominant"]) / total_talents * 100,
                    "expected_range": "8-15%"
                },
                "supporting": {
                    "count": len(classified_talents["supporting"]),
                    "percentage": len(classified_talents["supporting"]) / total_talents * 100,
                    "expected_range": "60-75%"
                },
                "developing": {
                    "count": len(classified_talents["developing"]),
                    "percentage": len(classified_talents["developing"]) / total_talents * 100,
                    "expected_range": "15-25%"
                }
            },
            "profile_type": self._determine_profile_type(classified_talents),
            "recommendations": self._generate_recommendations(classified_talents)
        }

        return summary

    def _determine_profile_type(self, classified_talents: Dict) -> str:
        """
        根據分類分佈判斷概況類型
        """
        dominant_count = len(classified_talents["dominant"])
        developing_count = len(classified_talents["developing"])
        total = sum(len(talents) for talents in classified_talents.values())

        dominant_pct = dominant_count / total * 100
        developing_pct = developing_count / total * 100

        if dominant_pct >= 25:
            return "多元優勢型"
        elif dominant_pct >= 15:
            if developing_pct <= 15:
                return "均衡發展型"
            else:
                return "標準分化型"
        elif dominant_count >= 2:
            return "專業聚焦型"
        elif dominant_count == 1:
            return "單一優勢型"
        else:
            return "潛力發展型"

    def _generate_recommendations(self, classified_talents: Dict) -> List[str]:
        """
        基於分類結果生成個人化建議
        """
        recommendations = []

        dominant_count = len(classified_talents["dominant"])
        supporting_count = len(classified_talents["supporting"])
        developing_count = len(classified_talents["developing"])

        # 主導才幹建議
        if dominant_count == 0:
            recommendations.append("建議透過實務練習培養核心優勢才幹")
        elif dominant_count >= 4:
            recommendations.append("善用多元優勢，但要注意聚焦重點發展領域")
        else:
            recommendations.append("持續強化主導才幹，建立個人品牌優勢")

        # 支援才幹建議
        if supporting_count >= 8:
            recommendations.append("支援才幹豐富，可作為團隊協作的重要資產")
        elif supporting_count <= 3:
            recommendations.append("考慮發展更多支援技能以增加適應性")

        # 發展才幹建議
        if developing_count >= 6:
            recommendations.append("優先選擇2-3個發展才幹進行重點提升")
        elif developing_count <= 2:
            recommendations.append("才幹分佈均衡，可考慮挑戰更高難度的發展目標")

        return recommendations

def get_tier_display_config() -> Dict:
    """
    獲取前端顯示配置

    提供統一的分層顯示標準
    """
    return {
        "dominant": {
            "title": "主導才幹",
            "subtitle": "您的核心優勢",
            "color": "#2E8B57",  # 深綠色
            "icon": "⭐",
            "description": "這些是您最突出的才幹，在相關情境中能展現卓越表現"
        },
        "supporting": {
            "title": "支援才幹",
            "subtitle": "穩定可靠的能力",
            "color": "#4682B4",  # 鋼藍色
            "icon": "🔧",
            "description": "這些才幹為您提供穩定支援，在適當情境下能有效發揮"
        },
        "developing": {
            "title": "發展才幹",
            "subtitle": "未來成長空間",
            "color": "#DAA520",  # 金色
            "icon": "🌱",
            "description": "這些才幹具有發展潜力，透過練習與學習可以提升"
        }
    }