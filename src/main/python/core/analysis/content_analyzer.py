"""
深度內容分析與建議生成系統
基於用戶優勢組合提供個性化的職涯建議、學習資源和發展路徑
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from datetime import datetime, timedelta

@dataclass
class StrengthProfile:
    """用戶優勢檔案"""
    top_strengths: List[Tuple[str, float]]
    all_scores: Dict[str, float]
    synergy_patterns: List[Dict]
    development_areas: List[str]

@dataclass
class CareerRecommendation:
    """職涯建議"""
    role: str
    match_score: float
    description: str
    required_skills: List[str]
    growth_path: str
    salary_range: str
    reasons: List[str]

@dataclass
class LearningResource:
    """學習資源"""
    title: str
    type: str  # course, book, article, video
    provider: str
    duration: str
    difficulty: str
    url: str
    relevance_score: float

@dataclass
class DevelopmentMilestone:
    """發展里程碑"""
    timeframe: str  # 30天, 60天, 90天
    goal: str
    actions: List[str]
    success_metrics: List[str]
    resources: List[str]

class ContentAnalyzer:
    """內容分析器"""

    def __init__(self):
        self._init_knowledge_base()

    def _init_knowledge_base(self):
        """初始化知識庫"""
        # 優勢與職業的對應關係
        self.career_mapping = {
            '戰略思維': {
                'roles': [
                    {'role': '產品經理', 'weight': 0.95},
                    {'role': '策略規劃師', 'weight': 0.92},
                    {'role': '管理顧問', 'weight': 0.90},
                    {'role': '創業家', 'weight': 0.88},
                    {'role': '投資分析師', 'weight': 0.85}
                ],
                'skills': ['全局觀', '長遠規劃', '系統思考', '決策能力']
            },
            '創新思維': {
                'roles': [
                    {'role': '創意總監', 'weight': 0.93},
                    {'role': 'UX設計師', 'weight': 0.90},
                    {'role': '研發工程師', 'weight': 0.88},
                    {'role': '新產品開發', 'weight': 0.87},
                    {'role': '創業家', 'weight': 0.85}
                ],
                'skills': ['創造力', '跨界思維', '實驗精神', '原創性']
            },
            '影響力': {
                'roles': [
                    {'role': '銷售總監', 'weight': 0.92},
                    {'role': '公關經理', 'weight': 0.90},
                    {'role': '團隊領導', 'weight': 0.88},
                    {'role': '品牌經理', 'weight': 0.86},
                    {'role': '政治家', 'weight': 0.85}
                ],
                'skills': ['說服力', '魅力', '溝通技巧', '激勵他人']
            },
            '分析力': {
                'roles': [
                    {'role': '數據科學家', 'weight': 0.95},
                    {'role': '財務分析師', 'weight': 0.92},
                    {'role': '研究員', 'weight': 0.90},
                    {'role': '風險管理師', 'weight': 0.88},
                    {'role': '精算師', 'weight': 0.86}
                ],
                'skills': ['邏輯思維', '數據解讀', '批判性思考', '精準度']
            },
            '執行力': {
                'roles': [
                    {'role': '專案經理', 'weight': 0.93},
                    {'role': '運營總監', 'weight': 0.90},
                    {'role': '生產經理', 'weight': 0.88},
                    {'role': '活動策劃', 'weight': 0.85},
                    {'role': '創業家', 'weight': 0.83}
                ],
                'skills': ['目標導向', '時間管理', '細節掌控', '效率']
            },
            '溝通': {
                'roles': [
                    {'role': '培訓講師', 'weight': 0.92},
                    {'role': '客戶成功經理', 'weight': 0.90},
                    {'role': '公關專員', 'weight': 0.88},
                    {'role': '記者編輯', 'weight': 0.86},
                    {'role': '外交官', 'weight': 0.84}
                ],
                'skills': ['表達能力', '傾聽', '同理心', '跨文化溝通']
            },
            '學習力': {
                'roles': [
                    {'role': '研發工程師', 'weight': 0.91},
                    {'role': '顧問', 'weight': 0.89},
                    {'role': '學者教授', 'weight': 0.87},
                    {'role': '技術專家', 'weight': 0.85},
                    {'role': '創新經理', 'weight': 0.83}
                ],
                'skills': ['好奇心', '知識整合', '快速學習', '持續成長']
            },
            '適應力': {
                'roles': [
                    {'role': '變革管理顧問', 'weight': 0.90},
                    {'role': '創業家', 'weight': 0.88},
                    {'role': '國際業務', 'weight': 0.86},
                    {'role': '危機管理師', 'weight': 0.84},
                    {'role': '外派經理', 'weight': 0.82}
                ],
                'skills': ['靈活性', '韌性', '開放心態', '壓力管理']
            },
            '責任感': {
                'roles': [
                    {'role': '合規官', 'weight': 0.92},
                    {'role': '品質經理', 'weight': 0.90},
                    {'role': '審計師', 'weight': 0.88},
                    {'role': '專案經理', 'weight': 0.86},
                    {'role': '醫生', 'weight': 0.84}
                ],
                'skills': ['可靠性', '承諾', '道德感', '細心']
            },
            '積極性': {
                'roles': [
                    {'role': '業務開發', 'weight': 0.91},
                    {'role': '創業家', 'weight': 0.89},
                    {'role': '激勵講師', 'weight': 0.87},
                    {'role': '運動教練', 'weight': 0.85},
                    {'role': '社區組織者', 'weight': 0.83}
                ],
                'skills': ['樂觀', '能量', '主動性', '熱情']
            },
            '同理心': {
                'roles': [
                    {'role': '心理諮詢師', 'weight': 0.93},
                    {'role': '人力資源經理', 'weight': 0.90},
                    {'role': '客服主管', 'weight': 0.88},
                    {'role': '社工', 'weight': 0.86},
                    {'role': '教師', 'weight': 0.84}
                ],
                'skills': ['理解他人', '情商', '關懷', '支持性']
            },
            '專注力': {
                'roles': [
                    {'role': '軟體工程師', 'weight': 0.92},
                    {'role': '研究員', 'weight': 0.90},
                    {'role': '作家', 'weight': 0.88},
                    {'role': '會計師', 'weight': 0.86},
                    {'role': '外科醫生', 'weight': 0.84}
                ],
                'skills': ['深度工作', '持續專注', '抗干擾', '精確性']
            }
        }

        # 優勢協同效應
        self.synergy_patterns = {
            ('戰略思維', '執行力'): {
                'name': '戰略執行者',
                'description': '你不僅能制定優秀策略，還能有效執行',
                'bonus_careers': ['CEO', '創業家', '事業部總經理'],
                'multiplier': 1.3
            },
            ('創新思維', '分析力'): {
                'name': '創新分析師',
                'description': '你能用數據驗證創新想法，做出理性創新',
                'bonus_careers': ['產品經理', '數據產品經理', 'AI工程師'],
                'multiplier': 1.25
            },
            ('影響力', '同理心'): {
                'name': '人心領袖',
                'description': '你能深刻理解他人並有效影響，是天生的領導者',
                'bonus_careers': ['CEO', '政治家', '非營利組織領導'],
                'multiplier': 1.28
            },
            ('學習力', '適應力'): {
                'name': '快速成長者',
                'description': '你能在變化中快速學習成長，適合動態環境',
                'bonus_careers': ['顧問', '創業家', '轉型專家'],
                'multiplier': 1.22
            },
            ('分析力', '專注力'): {
                'name': '深度研究者',
                'description': '你能深入分析複雜問題，產出高質量成果',
                'bonus_careers': ['研究科學家', '投資分析師', '精算師'],
                'multiplier': 1.26
            },
            ('溝通', '戰略思維'): {
                'name': '策略傳播者',
                'description': '你能清晰傳達複雜策略，推動組織變革',
                'bonus_careers': ['管理顧問', '變革領導', '企業傳播總監'],
                'multiplier': 1.24
            }
        }

        # 學習資源庫
        self.learning_resources = {
            '戰略思維': [
                {
                    'title': '好策略壞策略',
                    'type': 'book',
                    'provider': '天下文化',
                    'duration': '2週',
                    'difficulty': '中級',
                    'url': '#',
                    'relevance': 0.95
                },
                {
                    'title': 'Strategic Thinking Course',
                    'type': 'course',
                    'provider': 'Coursera',
                    'duration': '6週',
                    'difficulty': '高級',
                    'url': '#',
                    'relevance': 0.92
                }
            ],
            '創新思維': [
                {
                    'title': 'Design Thinking',
                    'type': 'course',
                    'provider': 'IDEO U',
                    'duration': '4週',
                    'difficulty': '中級',
                    'url': '#',
                    'relevance': 0.94
                },
                {
                    'title': '創新者的解答',
                    'type': 'book',
                    'provider': '天下雜誌',
                    'duration': '1週',
                    'difficulty': '中級',
                    'url': '#',
                    'relevance': 0.90
                }
            ]
        }

    def analyze_profile(self, scores: Dict[str, float]) -> StrengthProfile:
        """分析用戶優勢檔案"""
        # 排序找出前5強優勢
        sorted_strengths = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_strengths = sorted_strengths[:5]

        # 找出協同效應
        synergy_patterns = []
        for i, (strength1, _) in enumerate(top_strengths[:3]):
            for strength2, _ in top_strengths[i+1:4]:
                key = tuple(sorted([strength1, strength2]))
                if key in self.synergy_patterns:
                    pattern = self.synergy_patterns[key].copy()
                    pattern['strengths'] = key
                    synergy_patterns.append(pattern)

        # 找出發展領域（分數較低的）
        development_areas = [s for s, score in sorted_strengths[-3:] if score < 50]

        return StrengthProfile(
            top_strengths=top_strengths,
            all_scores=scores,
            synergy_patterns=synergy_patterns,
            development_areas=development_areas
        )

    def generate_career_recommendations(self,
                                       profile: StrengthProfile,
                                       num_recommendations: int = 5) -> List[CareerRecommendation]:
        """生成職涯建議"""
        career_scores = {}

        # 基於每個優勢計算職業匹配度
        for strength, score in profile.top_strengths[:3]:
            if strength in self.career_mapping:
                for role_info in self.career_mapping[strength]['roles']:
                    role = role_info['role']
                    weight = role_info['weight']

                    if role not in career_scores:
                        career_scores[role] = {
                            'score': 0,
                            'strengths': [],
                            'skills': set()
                        }

                    career_scores[role]['score'] += score * weight / 100
                    career_scores[role]['strengths'].append(strength)
                    career_scores[role]['skills'].update(
                        self.career_mapping[strength]['skills']
                    )

        # 加入協同效應加成
        for pattern in profile.synergy_patterns:
            for career in pattern.get('bonus_careers', []):
                if career in career_scores:
                    career_scores[career]['score'] *= pattern['multiplier']
                else:
                    career_scores[career] = {
                        'score': 0.8 * pattern['multiplier'],
                        'strengths': list(pattern['strengths']),
                        'skills': set()
                    }

        # 排序並生成建議
        sorted_careers = sorted(career_scores.items(),
                              key=lambda x: x[1]['score'],
                              reverse=True)

        recommendations = []
        for career, info in sorted_careers[:num_recommendations]:
            rec = CareerRecommendation(
                role=career,
                match_score=min(info['score'] * 100, 98),
                description=self._get_career_description(career),
                required_skills=list(info['skills'])[:5],
                growth_path=self._get_growth_path(career),
                salary_range=self._get_salary_range(career),
                reasons=[
                    f"你的{strength}優勢非常適合此職位"
                    for strength in info['strengths']
                ]
            )
            recommendations.append(rec)

        return recommendations

    def generate_learning_path(self,
                              profile: StrengthProfile,
                              timeframe: int = 90) -> List[LearningResource]:
        """生成學習路徑"""
        resources = []

        # 為前3個優勢找學習資源
        for strength, _ in profile.top_strengths[:3]:
            if strength in self.learning_resources:
                for resource_data in self.learning_resources[strength]:
                    resource = LearningResource(
                        title=resource_data['title'],
                        type=resource_data['type'],
                        provider=resource_data['provider'],
                        duration=resource_data['duration'],
                        difficulty=resource_data['difficulty'],
                        url=resource_data['url'],
                        relevance_score=resource_data['relevance']
                    )
                    resources.append(resource)

        # 按相關性排序
        resources.sort(key=lambda x: x.relevance_score, reverse=True)

        return resources[:10]

    def generate_action_plan(self,
                           profile: StrengthProfile) -> List[DevelopmentMilestone]:
        """生成行動計劃"""
        milestones = []

        # 30天計劃 - 認識優勢
        milestone_30 = DevelopmentMilestone(
            timeframe='30天',
            goal='深入理解並開始運用你的核心優勢',
            actions=[
                f'每週至少3次刻意運用你的{profile.top_strengths[0][0]}優勢',
                '記錄優勢運用的場景和效果',
                '向同事或朋友收集關於你優勢表現的反饋',
                '閱讀1本關於優勢發展的書籍',
                '加入1個與你優勢相關的社群或論壇'
            ],
            success_metrics=[
                '能清楚說出3個成功運用優勢的案例',
                '收集到至少5份他人反饋',
                '完成優勢日記至少20篇'
            ],
            resources=[
                '《發現我的天才》- Marcus Buckingham',
                'Gallup優勢識別器2.0',
                '優勢教練認證課程'
            ]
        )
        milestones.append(milestone_30)

        # 60天計劃 - 整合發展
        milestone_60 = DevelopmentMilestone(
            timeframe='60天',
            goal='整合優勢組合，提升綜合能力',
            actions=[
                f'結合{profile.top_strengths[0][0]}和{profile.top_strengths[1][0]}解決工作難題',
                '主動承擔能發揮優勢組合的項目',
                '與優勢互補的夥伴建立合作關係',
                '參加2個專業技能提升課程',
                '制定個人品牌定位'
            ],
            success_metrics=[
                '完成至少1個重要項目並獲得認可',
                '建立3個有效的合作關係',
                '專業技能評分提升15%'
            ],
            resources=[
                '相關專業認證課程',
                '行業大會或研討會',
                'LinkedIn學習平台'
            ]
        )
        milestones.append(milestone_60)

        # 90天計劃 - 創造價值
        milestone_90 = DevelopmentMilestone(
            timeframe='90天',
            goal='運用優勢創造顯著價值和影響力',
            actions=[
                '領導或深度參與1個戰略項目',
                '成為團隊中某領域的專家顧問',
                '分享優勢實踐經驗（演講/文章/培訓）',
                '建立個人優勢發展體系',
                '規劃下一階段職涯發展目標'
            ],
            success_metrics=[
                '項目成果超出預期20%以上',
                '獲得上級或客戶的正面評價',
                '影響力擴展到部門或組織層面',
                '明確下階段發展方向和計劃'
            ],
            resources=[
                '高階主管教練',
                '戰略思維工作坊',
                '個人品牌建設指南'
            ]
        )
        milestones.append(milestone_90)

        return milestones

    def _get_career_description(self, career: str) -> str:
        """獲取職業描述"""
        descriptions = {
            '產品經理': '負責產品規劃、設計和推廣，需要結合市場洞察、用戶需求和技術可行性',
            '策略規劃師': '為組織制定長期發展戰略，分析市場趨勢和競爭環境',
            '管理顧問': '為企業提供專業建議，解決複雜商業問題，推動組織變革',
            '創業家': '創建和經營自己的事業，需要願景、執行力和風險承受能力',
            '數據科學家': '運用統計學和機器學習技術，從數據中挖掘洞察和價值',
            'UX設計師': '設計用戶體驗，創造直覺且愉悅的產品互動',
            'CEO': '企業最高決策者，負責制定願景、策略並領導組織實現目標'
        }
        return descriptions.get(career, '專業領域的核心崗位，發揮你的獨特優勢')

    def _get_growth_path(self, career: str) -> str:
        """獲取成長路徑"""
        paths = {
            '產品經理': '產品助理 → 產品經理 → 高級產品經理 → 產品總監 → CPO',
            '策略規劃師': '分析師 → 策略專員 → 策略經理 → 策略總監 → CSO',
            '管理顧問': '分析師 → 顧問 → 高級顧問 → 經理 → 合夥人',
            '創業家': '創始人 → CEO → 連續創業者 → 投資人/導師',
            '數據科學家': '數據分析師 → 數據科學家 → 高級數據科學家 → 首席數據科學家',
            'UX設計師': '初級設計師 → UX設計師 → 高級設計師 → 設計主管 → 設計總監'
        }
        return paths.get(career, '專員 → 經理 → 總監 → 高管')

    def _get_salary_range(self, career: str) -> str:
        """獲取薪資範圍"""
        ranges = {
            '產品經理': '30-100萬/年',
            '策略規劃師': '40-120萬/年',
            '管理顧問': '35-200萬/年',
            '創業家': '變動較大，潛力無限',
            '數據科學家': '40-150萬/年',
            'UX設計師': '25-80萬/年',
            'CEO': '100-1000萬+/年'
        }
        return ranges.get(career, '25-100萬/年')