"""
職業原型映射系統
基於凱爾西氣質理論，將12個才幹維度映射到四大職業原型
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json

# 12個核心才幹維度定義（符合系統設計文檔）
TALENT_DIMENSIONS = {
    'T1': '結構化執行',
    'T2': '品質與完備',
    'T3': '探索與創新',
    'T4': '分析與洞察',
    'T5': '影響與倡議',
    'T6': '協作與共好',
    'T7': '客戶導向',
    'T8': '學習與成長',
    'T9': '紀律與信任',
    'T10': '壓力調節',
    'T11': '衝突整合',
    'T12': '責任與當責'
}

@dataclass
class CareerArchetype:
    """職業原型資料結構"""
    archetype_id: str
    archetype_name: str
    keirsey_temperament: str
    mbti_correlates: List[str]
    description: str
    primary_talents: List[str]  # 核心才幹
    secondary_talents: List[str]  # 輔助才幹
    career_suggestions: List[str]

@dataclass
class TalentProfile:
    """天賦檔案結構"""
    dominant_talents: List[Tuple[str, float]]  # 主導才幹 (PR > 75)
    supporting_talents: List[Tuple[str, float]]  # 輔助才幹 (PR 25-75)
    lesser_talents: List[Tuple[str, float]]  # 較弱才幹 (PR < 25)

class ArchetypeMapper:
    """職業原型映射器"""

    def __init__(self):
        self.archetypes = self._load_archetypes()

    def _load_archetypes(self) -> List[CareerArchetype]:
        """載入職業原型資料庫"""
        archetype_data = [
            {
                "archetype_id": "ARCHITECT",
                "archetype_name": "系統建構者",
                "keirsey_temperament": "理性者 (Rational)",
                "mbti_correlates": ["INTJ", "INTP", "ENTJ"],
                "description": "天生的系統思考者與建構者，擅長將複雜的資訊轉化為清晰的藍圖與高效的流程。注重邏輯、效率與長期規劃。",
                "primary_talents": ["T4", "T1"],  # 分析與洞察、結構化執行
                "secondary_talents": ["T3", "T8", "T12"],  # 探索與創新、學習與成長、責任與當責
                "career_suggestions": [
                    "軟體架構師", "策略顧問", "數據科學家",
                    "研發工程師", "經濟學家", "大學教授", "發明家"
                ]
            },
            {
                "archetype_id": "GUARDIAN",
                "archetype_name": "組織守護者",
                "keirsey_temperament": "守護者 (Guardian)",
                "mbti_correlates": ["ISTJ", "ISFJ", "ESTJ", "ESFJ"],
                "description": "可靠的執行者與維護者，擅長建立和維護穩定的系統，並確保任務按時、按質完成。注重責任、紀律與品質。",
                "primary_talents": ["T12", "T9"],  # 責任與當責、紀律與信任
                "secondary_talents": ["T2", "T1", "T6"],  # 品質與完備、結構化執行、協作與共好
                "career_suggestions": [
                    "專案經理", "會計師/審計師", "供應鏈經理",
                    "法務人員", "公共行政人員", "品質保證(QA)工程師", "數據庫管理員"
                ]
            },
            {
                "archetype_id": "IDEALIST",
                "archetype_name": "人文關懷家",
                "keirsey_temperament": "理想主義者 (Idealist)",
                "mbti_correlates": ["INFJ", "INFP", "ENFJ", "ENFP"],
                "description": "以人為本的溝通者與賦能者，擅長理解他人、建立關係並激勵團隊。注重和諧、成長與共同價值。",
                "primary_talents": ["T6", "T8"],  # 協作與共好、學習與成長
                "secondary_talents": ["T5", "T11", "T7"],  # 影響與倡議、衝突整合、客戶導向
                "career_suggestions": [
                    "人力資源經理", "企業教練/導師", "教師/教育顧問",
                    "諮商心理師/社工", "非營利組織負責人", "公共關係專家", "作家/藝術家"
                ]
            },
            {
                "archetype_id": "ARTISAN",
                "archetype_name": "推廣實踐家",
                "keirsey_temperament": "工匠 (Artisan)",
                "mbti_correlates": ["ESTP", "ESFP", "ISTP", "ISFP"],
                "description": "充滿活力的行動派與連結者，擅長將想法付諸實踐，並在與人互動中獲得能量。注重結果、效率與人際關係。",
                "primary_talents": ["T5", "T10"],  # 影響與倡議、壓力調節
                "secondary_talents": ["T3", "T7", "T11"],  # 探索與創新、客戶導向、衝突整合
                "career_suggestions": [
                    "市場行銷專家", "銷售總監", "創業者/企業家",
                    "危機管理專家", "活動策劃人", "運動員/表演者", "急診科醫生"
                ]
            }
        ]

        return [CareerArchetype(**data) for data in archetype_data]

    def classify_talents(self, talent_scores: Dict[str, float]) -> TalentProfile:
        """
        根據百分等級分數將才幹分類為三個階層

        Args:
            talent_scores: 12個才幹維度的百分等級分數 (0-100)

        Returns:
            TalentProfile: 分類後的天賦檔案
        """
        sorted_talents = sorted(talent_scores.items(), key=lambda x: x[1], reverse=True)

        dominant = []
        supporting = []
        lesser = []

        for talent_id, score in sorted_talents:
            if score > 75:  # PR > 75: 主導才幹
                dominant.append((talent_id, score))
            elif score >= 25:  # PR 25-75: 輔助才幹
                supporting.append((talent_id, score))
            else:  # PR < 25: 較弱才幹
                lesser.append((talent_id, score))

        return TalentProfile(
            dominant_talents=dominant,
            supporting_talents=supporting,
            lesser_talents=lesser
        )

    def map_to_archetype(self, talent_profile: TalentProfile) -> CareerArchetype:
        """
        將天賦檔案映射到最匹配的職業原型

        Args:
            talent_profile: 分類後的天賦檔案

        Returns:
            CareerArchetype: 最匹配的職業原型
        """
        # 獲取主導才幹的ID列表（取前4個）
        top_talents = [t[0] for t in talent_profile.dominant_talents[:4]]

        # 計算每個原型的匹配度
        best_match = None
        best_score = 0

        for archetype in self.archetypes:
            score = 0

            # 核心才幹匹配（權重更高）
            for talent in archetype.primary_talents:
                if talent in top_talents:
                    score += 3

            # 輔助才幹匹配
            for talent in archetype.secondary_talents:
                if talent in top_talents:
                    score += 1

            # 更新最佳匹配
            if score > best_score:
                best_score = score
                best_match = archetype

        # 如果沒有明顯匹配，返回預設原型（系統建構者）
        if best_match is None:
            best_match = self.archetypes[0]

        return best_match

    def get_synergy_analysis(self, dominant_talents: List[str]) -> Dict:
        """
        分析主導才幹的協同效應

        Args:
            dominant_talents: 主導才幹ID列表

        Returns:
            協同效應分析結果
        """
        synergies = []

        # 預定義的協同效應模式
        synergy_patterns = {
            ('T4', 'T1'): {
                'name': '戰略執行者',
                'description': '你不僅能深入分析問題，還能制定結構化的執行計劃',
                'bonus_careers': ['產品經理', '創業家', '事業部總經理']
            },
            ('T3', 'T4'): {
                'name': '創新分析師',
                'description': '你能用數據驗證創新想法，做出理性創新',
                'bonus_careers': ['產品經理', '數據產品經理', 'AI工程師']
            },
            ('T5', 'T6'): {
                'name': '人心領袖',
                'description': '你能深刻理解他人並有效影響，是天生的領導者',
                'bonus_careers': ['CEO', '政治家', '非營利組織領導']
            },
            ('T8', 'T10'): {
                'name': '快速成長者',
                'description': '你能在壓力中快速學習成長，適合動態環境',
                'bonus_careers': ['顧問', '創業家', '轉型專家']
            },
            ('T4', 'T12'): {
                'name': '深度研究者',
                'description': '你能深入分析複雜問題，並負責任地產出高質量成果',
                'bonus_careers': ['研究科學家', '投資分析師', '精算師']
            },
            ('T6', 'T11'): {
                'name': '和諧締造者',
                'description': '你能在衝突中建立共識，創造團隊和諧',
                'bonus_careers': ['人力資源總監', '調解員', '外交官']
            }
        }

        # 檢查才幹組合
        for i, talent1 in enumerate(dominant_talents[:3]):
            for talent2 in dominant_talents[i+1:4]:
                key = tuple(sorted([talent1, talent2]))
                if key in synergy_patterns:
                    synergies.append(synergy_patterns[key])

        return {
            'synergies': synergies,
            'summary': f'你的主導才幹組合創造了{len(synergies)}個協同效應'
        }

    def get_development_suggestions(self, talent_profile: TalentProfile) -> Dict:
        """
        基於天賦檔案提供發展建議

        Args:
            talent_profile: 天賦檔案

        Returns:
            發展建議
        """
        suggestions = {
            'maximize_dominant': [],
            'leverage_supporting': [],
            'manage_lesser': []
        }

        # 主導才幹發展建議
        for talent_id, score in talent_profile.dominant_talents[:3]:
            talent_name = TALENT_DIMENSIONS.get(talent_id, talent_id)
            suggestions['maximize_dominant'].append({
                'talent': talent_name,
                'action': f'主動尋找能發揮{talent_name}的任務與角色',
                'tip': '這是你的超能力，應該成為你的職業標誌'
            })

        # 輔助才幹運用建議
        for talent_id, score in talent_profile.supporting_talents[:2]:
            talent_name = TALENT_DIMENSIONS.get(talent_id, talent_id)
            suggestions['leverage_supporting'].append({
                'talent': talent_name,
                'action': f'在需要時有意識地調用{talent_name}',
                'tip': '這是你的工具箱，善用它來支持主導才幹'
            })

        # 較弱才幹管理建議
        for talent_id, score in talent_profile.lesser_talents[:2]:
            talent_name = TALENT_DIMENSIONS.get(talent_id, talent_id)
            suggestions['manage_lesser'].append({
                'talent': talent_name,
                'action': f'透過團隊合作或工具來彌補{talent_name}',
                'tip': '不要試圖修補，而是聰明地管理其影響'
            })

        return suggestions