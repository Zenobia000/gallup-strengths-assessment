"""
統一職涯知識庫 - Gallup 優勢測驗

統合管理優勢主題、職位角色、技能發展等職涯相關資料
確保所有模組使用一致的資料來源，消除資料重複和不一致問題

設計原則：
- Single Source of Truth：單一事實來源
- 優勢主題與職位的雙向映射
- 可擴展的技能發展建議
- 支援多語言和本地化
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json


class StrengthCategory(Enum):
    """優勢類別"""
    EXECUTION = "execution"      # 執行力
    INFLUENCING = "influencing"  # 影響力
    RELATIONSHIP = "relationship" # 關係建立
    THINKING = "thinking"        # 策略思維


class IndustrySector(Enum):
    """產業類別"""
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    CONSULTING = "consulting"
    MEDIA = "media"
    GOVERNMENT = "government"
    NON_PROFIT = "non_profit"
    STARTUP = "startup"
    CORPORATE = "corporate"


class ExperienceLevel(Enum):
    """經驗等級"""
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    EXECUTIVE = "executive"


@dataclass
class SkillRequirement:
    """技能要求"""
    skill_name: str
    chinese_name: str
    importance: float  # 0-1，重要性權重
    proficiency_level: str  # "basic", "intermediate", "advanced", "expert"
    description: str


@dataclass
class DevelopmentSuggestion:
    """發展建議"""
    suggestion_id: str
    title: str
    description: str
    priority: str  # "high", "medium", "low"
    category: str  # "technical", "leadership", "communication", etc.
    time_investment: str  # "short-term", "medium-term", "long-term"
    resources: List[str] = field(default_factory=list)


@dataclass
class CareerRole:
    """職涯角色定義"""
    role_id: str
    role_name: str
    chinese_name: str
    industry_sector: IndustrySector
    experience_levels: List[ExperienceLevel]
    description: str

    # 優勢要求
    primary_strengths: List[str]     # 核心必備優勢
    secondary_strengths: List[str]   # 有助益的優勢
    strength_weights: Dict[str, float]  # 各優勢的權重

    # 技能要求
    required_skills: List[SkillRequirement]
    beneficial_skills: List[SkillRequirement]

    # 職涯資訊
    salary_range: str
    growth_potential: str
    work_environment: str
    key_responsibilities: List[str]

    # 發展建議
    development_paths: List[DevelopmentSuggestion]

    def get_all_required_strengths(self) -> List[str]:
        """獲取所有需要的優勢（主要+次要）"""
        return self.primary_strengths + self.secondary_strengths

    def get_strength_weight(self, strength_name: str) -> float:
        """獲取優勢權重"""
        return self.strength_weights.get(strength_name, 0.0)


@dataclass
class StrengthTheme:
    """優勢主題定義"""
    theme_id: str
    theme_name: str
    chinese_name: str
    category: StrengthCategory
    description: str

    # Big Five 映射
    primary_factor: str
    weight_formula: str

    # 職涯映射
    best_fit_roles: List[str]        # 最適合的職位角色 ID
    compatible_roles: List[str]      # 相容的職位角色 ID

    # 發展建議
    development_suggestions: List[DevelopmentSuggestion]

    # 行為特徵
    behavioral_indicators: List[str]
    work_style_preferences: List[str]


class CareerKnowledgeBase:
    """統一職涯知識庫"""

    def __init__(self):
        """初始化知識庫"""
        self._strength_themes: Dict[str, StrengthTheme] = {}
        self._career_roles: Dict[str, CareerRole] = {}
        self._development_library: Dict[str, DevelopmentSuggestion] = {}

        # 載入預設數據
        self._load_default_data()

    def _load_default_data(self):
        """載入預設的職涯知識庫數據"""
        self._load_strength_themes()
        self._load_career_roles()
        self._load_development_library()

    def _load_strength_themes(self):
        """載入優勢主題定義"""

        # 1. 結構化執行
        self._strength_themes["structured_execution"] = StrengthTheme(
            theme_id="structured_execution",
            theme_name="Structured Execution",
            chinese_name="結構化執行",
            category=StrengthCategory.EXECUTION,
            description="擅長建立系統、流程，確保工作有條不紊地完成",
            primary_factor="conscientiousness",
            weight_formula="0.8 * C + 0.2 * (100 - N)",
            best_fit_roles=["T002", "O001", "O002", "F002"],  # 產品經理、專案經理、營運經理、財務分析師
            compatible_roles=["T001", "H001"],
            development_suggestions=[],  # 稍後填入
            behavioral_indicators=[
                "喜歡制定詳細的計劃和時程",
                "能有效組織和管理資源",
                "重視品質和準確性"
            ],
            work_style_preferences=[
                "結構化的工作環境",
                "清楚的目標和期限",
                "系統化的工作流程"
            ]
        )

        # 2. 品質與完備
        self._strength_themes["quality_perfectionism"] = StrengthTheme(
            theme_id="quality_perfectionism",
            theme_name="Quality Perfectionism",
            chinese_name="品質與完備",
            category=StrengthCategory.EXECUTION,
            description="對品質有高標準，追求工作的完整性與精確性",
            primary_factor="conscientiousness",
            weight_formula="0.7 * C + 0.3 * O",
            best_fit_roles=["T001", "F002"],  # 軟體工程師、財務分析師
            compatible_roles=["T003", "O002"],
            development_suggestions=[],
            behavioral_indicators=[
                "注重細節和準確性",
                "不滿意平庸的工作成果",
                "願意投入額外時間確保品質"
            ],
            work_style_preferences=[
                "有充足時間完善工作",
                "品質導向的文化",
                "明確的標準和規範"
            ]
        )

        # 3. 探索與創新
        self._strength_themes["exploration_innovation"] = StrengthTheme(
            theme_id="exploration_innovation",
            theme_name="Exploration Innovation",
            chinese_name="探索與創新",
            category=StrengthCategory.THINKING,
            description="具有強烈的好奇心，善於探索新想法和創新解決方案",
            primary_factor="openness",
            weight_formula="0.8 * O + 0.2 * E",
            best_fit_roles=["T002", "M002"],  # 產品經理、行銷專員
            compatible_roles=["T003", "H001"],
            development_suggestions=[],
            behavioral_indicators=[
                "喜歡嘗試新的方法和工具",
                "對未知領域充滿好奇",
                "能從不同角度思考問題"
            ],
            work_style_preferences=[
                "創新和實驗的空間",
                "多元化的專案",
                "開放的溝通文化"
            ]
        )

        # 4. 分析與洞察
        self._strength_themes["analytical_insight"] = StrengthTheme(
            theme_id="analytical_insight",
            theme_name="Analytical Insight",
            chinese_name="分析與洞察",
            category=StrengthCategory.THINKING,
            description="能深入分析複雜問題，從資料中發現重要洞察",
            primary_factor="openness",
            weight_formula="0.6 * O + 0.4 * C",
            best_fit_roles=["T003", "F001", "F002"],  # 資料科學家、管理顧問、財務分析師
            compatible_roles=["T001", "T002"],
            development_suggestions=[],
            behavioral_indicators=[
                "善於發現資料中的模式",
                "喜歡深入研究複雜問題",
                "能提出基於證據的建議"
            ],
            work_style_preferences=[
                "獨立思考的時間",
                "豐富的資料和資源",
                "重視分析的組織文化"
            ]
        )

        # 5. 影響與倡議
        self._strength_themes["influence_advocacy"] = StrengthTheme(
            theme_id="influence_advocacy",
            theme_name="Influence Advocacy",
            chinese_name="影響與倡議",
            category=StrengthCategory.INFLUENCING,
            description="能有效影響他人，推動重要倡議並獲得支持",
            primary_factor="extraversion",
            weight_formula="0.7 * E + 0.3 * C",
            best_fit_roles=["M001", "M002", "F001"],  # 業務經理、行銷專員、管理顧問
            compatible_roles=["T002", "H001"],
            development_suggestions=[],
            behavioral_indicators=[
                "能清楚表達想法和願景",
                "善於說服和影響他人",
                "喜歡推動變革和改進"
            ],
            work_style_preferences=[
                "與人互動的機會",
                "展示和簡報的場合",
                "能發揮影響力的角色"
            ]
        )

        # 6. 協作與共好
        self._strength_themes["collaboration_harmony"] = StrengthTheme(
            theme_id="collaboration_harmony",
            theme_name="Collaboration Harmony",
            chinese_name="協作與共好",
            category=StrengthCategory.RELATIONSHIP,
            description="擅長團隊合作，促進和諧關係並達成共同目標",
            primary_factor="agreeableness",
            weight_formula="0.7 * A + 0.3 * E",
            best_fit_roles=["H001", "O001"],  # 人力資源夥伴、專案經理
            compatible_roles=["T002", "M002"],
            development_suggestions=[],
            behavioral_indicators=[
                "重視團隊和諧與合作",
                "善於協調不同觀點",
                "關心團隊成員的福祉"
            ],
            work_style_preferences=[
                "團隊導向的工作環境",
                "合作式的決策過程",
                "支持性的組織文化"
            ]
        )

        # 繼續載入其他優勢主題...
        self._load_additional_strength_themes()

    def _load_additional_strength_themes(self):
        """載入其他優勢主題"""

        # 7. 客戶導向
        self._strength_themes["customer_orientation"] = StrengthTheme(
            theme_id="customer_orientation",
            theme_name="Customer Orientation",
            chinese_name="客戶導向",
            category=StrengthCategory.RELATIONSHIP,
            description="以客戶需求為中心，建立長期信任關係",
            primary_factor="agreeableness",
            weight_formula="0.6 * A + 0.4 * E",
            best_fit_roles=["M001", "M002"],  # 業務經理、行銷專員
            compatible_roles=["H001"],
            development_suggestions=[],
            behavioral_indicators=[
                "深度理解客戶需求",
                "建立長期信任關係",
                "以客戶成功為導向"
            ],
            work_style_preferences=[
                "直接接觸客戶的機會",
                "客戶成功導向的文化",
                "服務品質的重視"
            ]
        )

        # 8. 學習與成長
        self._strength_themes["learning_growth"] = StrengthTheme(
            theme_id="learning_growth",
            theme_name="Learning Growth",
            chinese_name="學習與成長",
            category=StrengthCategory.THINKING,
            description="持續學習新知識，追求個人與專業成長",
            primary_factor="openness",
            weight_formula="0.7 * O + 0.3 * C",
            best_fit_roles=["T001", "T003", "H001"],  # 軟體工程師、資料科學家、人力資源夥伴
            compatible_roles=["F001", "T002"],
            development_suggestions=[],
            behavioral_indicators=[
                "主動尋求學習機會",
                "喜歡掌握新技能",
                "重視知識的累積"
            ],
            work_style_preferences=[
                "豐富的學習資源",
                "成長導向的組織",
                "知識分享的文化"
            ]
        )

        # 9. 紀律與信任
        self._strength_themes["discipline_trust"] = StrengthTheme(
            theme_id="discipline_trust",
            theme_name="Discipline Trust",
            chinese_name="紀律與信任",
            category=StrengthCategory.EXECUTION,
            description="具有強烈的自律精神，值得他人信任與依賴",
            primary_factor="conscientiousness",
            weight_formula="0.8 * C + 0.2 * A",
            best_fit_roles=["F002", "O002"],  # 財務分析師、營運經理
            compatible_roles=["O001", "T001"],
            development_suggestions=[],
            behavioral_indicators=[
                "嚴格遵守承諾和期限",
                "具有高度自律性",
                "值得他人信任依賴"
            ],
            work_style_preferences=[
                "明確的規範和流程",
                "重視誠信的文化",
                "穩定的工作環境"
            ]
        )

        # 10. 壓力調節
        self._strength_themes["stress_regulation"] = StrengthTheme(
            theme_id="stress_regulation",
            theme_name="Stress Regulation",
            chinese_name="壓力調節",
            category=StrengthCategory.EXECUTION,
            description="在高壓環境中保持冷靜，有效調節壓力",
            primary_factor="neuroticism_reversed",
            weight_formula="0.8 * (100 - N) + 0.2 * C",
            best_fit_roles=["F001", "M001"],  # 管理顧問、業務經理
            compatible_roles=["O001", "T002"],
            development_suggestions=[],
            behavioral_indicators=[
                "在壓力下保持冷靜",
                "能有效管理情緒",
                "面對挑戰時不易慌亂"
            ],
            work_style_preferences=[
                "高挑戰性的工作",
                "快節奏的環境",
                "重視韌性的文化"
            ]
        )

        # 11. 衝突整合
        self._strength_themes["conflict_integration"] = StrengthTheme(
            theme_id="conflict_integration",
            theme_name="Conflict Integration",
            chinese_name="衝突整合",
            category=StrengthCategory.RELATIONSHIP,
            description="善於處理衝突，將不同觀點整合為共識",
            primary_factor="agreeableness",
            weight_formula="0.6 * A + 0.4 * (100 - N)",
            best_fit_roles=["H001", "F001"],  # 人力資源夥伴、管理顧問
            compatible_roles=["O001"],
            development_suggestions=[],
            behavioral_indicators=[
                "善於調解不同意見",
                "能找到共同利益點",
                "促進團隊和諧"
            ],
            work_style_preferences=[
                "多元觀點的環境",
                "協商和調解的機會",
                "包容性的組織文化"
            ]
        )

        # 12. 責任與當責
        self._strength_themes["responsibility_accountability"] = StrengthTheme(
            theme_id="responsibility_accountability",
            theme_name="Responsibility Accountability",
            chinese_name="責任與當責",
            category=StrengthCategory.EXECUTION,
            description="承擔責任，對結果負責，值得信賴",
            primary_factor="conscientiousness",
            weight_formula="0.7 * C + 0.3 * A",
            best_fit_roles=["O001", "O002", "F002"],  # 專案經理、營運經理、財務分析師
            compatible_roles=["T002", "H001"],
            development_suggestions=[],
            behavioral_indicators=[
                "主動承擔責任",
                "對工作成果負責",
                "可靠且值得信賴"
            ],
            work_style_preferences=[
                "明確的責任範圍",
                "結果導向的文化",
                "當責制的組織"
            ]
        )

    def _load_career_roles(self):
        """載入職涯角色定義"""

        # T001: 軟體工程師
        self._career_roles["T001"] = CareerRole(
            role_id="T001",
            role_name="Software Engineer",
            chinese_name="軟體工程師",
            industry_sector=IndustrySector.TECHNOLOGY,
            experience_levels=[ExperienceLevel.ENTRY, ExperienceLevel.JUNIOR, ExperienceLevel.MID, ExperienceLevel.SENIOR],
            description="設計、開發和維護軟體系統，解決技術問題並創建創新解決方案",
            primary_strengths=["analytical_insight", "quality_perfectionism", "learning_growth"],
            secondary_strengths=["discipline_trust", "structured_execution"],
            strength_weights={
                "analytical_insight": 0.4,
                "quality_perfectionism": 0.3,
                "learning_growth": 0.3,
                "discipline_trust": 0.2,
                "structured_execution": 0.2
            },
            required_skills=[
                SkillRequirement("programming", "程式設計", 0.9, "advanced", "多種程式語言的熟練使用"),
                SkillRequirement("system_design", "系統設計", 0.8, "intermediate", "軟體架構和系統設計能力"),
                SkillRequirement("debugging", "除錯技能", 0.8, "advanced", "問題診斷和解決能力")
            ],
            beneficial_skills=[
                SkillRequirement("project_management", "專案管理", 0.6, "basic", "基礎專案管理知識"),
                SkillRequirement("communication", "溝通表達", 0.7, "intermediate", "技術溝通和協作能力")
            ],
            salary_range="60-150萬",
            growth_potential="高",
            work_environment="辦公室/遠距",
            key_responsibilities=["系統設計", "程式碼開發", "測試除錯", "技術文件", "團隊協作"],
            development_paths=[]  # 稍後填入
        )

        # T002: 產品經理
        self._career_roles["T002"] = CareerRole(
            role_id="T002",
            role_name="Product Manager",
            chinese_name="產品經理",
            industry_sector=IndustrySector.TECHNOLOGY,
            experience_levels=[ExperienceLevel.MID, ExperienceLevel.SENIOR],
            description="負責產品策略、開發流程管理，協調跨部門合作實現產品目標",
            primary_strengths=["structured_execution", "exploration_innovation", "influence_advocacy"],
            secondary_strengths=["analytical_insight", "collaboration_harmony"],
            strength_weights={
                "structured_execution": 0.35,
                "exploration_innovation": 0.3,
                "influence_advocacy": 0.25,
                "analytical_insight": 0.2,
                "collaboration_harmony": 0.15
            },
            required_skills=[
                SkillRequirement("product_strategy", "產品策略", 0.9, "advanced", "產品規劃和策略制定"),
                SkillRequirement("data_analysis", "數據分析", 0.8, "intermediate", "產品數據分析和決策支援"),
                SkillRequirement("stakeholder_management", "利害關係人管理", 0.8, "advanced", "跨部門協調和溝通")
            ],
            beneficial_skills=[
                SkillRequirement("technical_knowledge", "技術理解", 0.6, "intermediate", "基礎技術概念理解"),
                SkillRequirement("user_research", "用戶研究", 0.7, "intermediate", "用戶需求調研和分析")
            ],
            salary_range="80-200萬",
            growth_potential="高",
            work_environment="辦公室",
            key_responsibilities=["產品策略", "需求分析", "專案管理", "跨部門協調", "市場研究"],
            development_paths=[]
        )

        # 載入其他職涯角色...
        self._load_additional_career_roles()

    def _load_additional_career_roles(self):
        """載入其他職涯角色"""

        # T003: 資料科學家
        self._career_roles["T003"] = CareerRole(
            role_id="T003",
            role_name="Data Scientist",
            chinese_name="資料科學家",
            industry_sector=IndustrySector.TECHNOLOGY,
            experience_levels=[ExperienceLevel.JUNIOR, ExperienceLevel.MID, ExperienceLevel.SENIOR],
            description="運用統計學和機器學習分析大數據，提供商業洞察和預測模型",
            primary_strengths=["analytical_insight", "learning_growth"],
            secondary_strengths=["quality_perfectionism", "exploration_innovation"],
            strength_weights={
                "analytical_insight": 0.6,
                "learning_growth": 0.3,
                "quality_perfectionism": 0.2,
                "exploration_innovation": 0.2
            },
            required_skills=[
                SkillRequirement("statistics", "統計學", 0.9, "advanced", "統計分析和推論能力"),
                SkillRequirement("machine_learning", "機器學習", 0.8, "advanced", "ML模型建構和優化"),
                SkillRequirement("data_visualization", "數據視覺化", 0.7, "intermediate", "數據呈現和溝通")
            ],
            beneficial_skills=[
                SkillRequirement("domain_expertise", "領域知識", 0.6, "intermediate", "特定業務領域的深度理解"),
                SkillRequirement("cloud_computing", "雲端運算", 0.5, "basic", "雲端平台和工具使用")
            ],
            salary_range="70-180萬",
            growth_potential="高",
            work_environment="辦公室/混合",
            key_responsibilities=["資料分析", "模型建構", "統計推論", "可視化報告", "業務諮詢"],
            development_paths=[]
        )

        # F001: 管理顧問
        self._career_roles["F001"] = CareerRole(
            role_id="F001",
            role_name="Management Consultant",
            chinese_name="管理顧問",
            industry_sector=IndustrySector.CONSULTING,
            experience_levels=[ExperienceLevel.JUNIOR, ExperienceLevel.MID, ExperienceLevel.SENIOR],
            description="為企業提供策略建議，協助解決營運問題並優化商業流程",
            primary_strengths=["analytical_insight", "influence_advocacy", "stress_regulation"],
            secondary_strengths=["structured_execution", "conflict_integration"],
            strength_weights={
                "analytical_insight": 0.4,
                "influence_advocacy": 0.3,
                "stress_regulation": 0.2,
                "structured_execution": 0.2,
                "conflict_integration": 0.1
            },
            required_skills=[
                SkillRequirement("business_analysis", "商業分析", 0.9, "advanced", "商業問題分析和解決"),
                SkillRequirement("presentation", "簡報技巧", 0.8, "advanced", "專業簡報和溝通"),
                SkillRequirement("strategic_thinking", "策略思維", 0.9, "advanced", "策略規劃和執行")
            ],
            beneficial_skills=[
                SkillRequirement("industry_knowledge", "產業知識", 0.7, "intermediate", "多元產業的理解"),
                SkillRequirement("change_management", "變革管理", 0.6, "intermediate", "組織變革的推動")
            ],
            salary_range="80-250萬",
            growth_potential="高",
            work_environment="客戶現場/差旅",
            key_responsibilities=["問題分析", "策略規劃", "客戶簡報", "專案執行", "團隊領導"],
            development_paths=[]
        )

        # F002: 財務分析師
        self._career_roles["F002"] = CareerRole(
            role_id="F002",
            role_name="Financial Analyst",
            chinese_name="財務分析師",
            industry_sector=IndustrySector.FINANCE,
            experience_levels=[ExperienceLevel.ENTRY, ExperienceLevel.JUNIOR, ExperienceLevel.MID],
            description="分析財務數據，評估投資機會，支援財務決策制定",
            primary_strengths=["analytical_insight", "discipline_trust", "quality_perfectionism"],
            secondary_strengths=["structured_execution", "responsibility_accountability"],
            strength_weights={
                "analytical_insight": 0.4,
                "discipline_trust": 0.3,
                "quality_perfectionism": 0.2,
                "structured_execution": 0.2,
                "responsibility_accountability": 0.1
            },
            required_skills=[
                SkillRequirement("financial_modeling", "財務建模", 0.9, "advanced", "財務模型建構和分析"),
                SkillRequirement("accounting", "會計學", 0.8, "intermediate", "會計原理和財務報表"),
                SkillRequirement("excel_advanced", "進階Excel", 0.8, "advanced", "Excel高級功能和分析")
            ],
            beneficial_skills=[
                SkillRequirement("sql", "SQL數據庫", 0.6, "intermediate", "數據查詢和分析"),
                SkillRequirement("risk_analysis", "風險分析", 0.7, "intermediate", "投資風險評估")
            ],
            salary_range="55-120萬",
            growth_potential="中高",
            work_environment="辦公室",
            key_responsibilities=["財報分析", "預算規劃", "風險評估", "投資建議", "合規檢核"],
            development_paths=[]
        )

        # M001: 業務經理
        self._career_roles["M001"] = CareerRole(
            role_id="M001",
            role_name="Sales Manager",
            chinese_name="業務經理",
            industry_sector=IndustrySector.CORPORATE,
            experience_levels=[ExperienceLevel.MID, ExperienceLevel.SENIOR],
            description="領導銷售團隊，制定銷售策略，達成營收目標並建立客戶關係",
            primary_strengths=["influence_advocacy", "customer_orientation", "stress_regulation"],
            secondary_strengths=["structured_execution", "collaboration_harmony"],
            strength_weights={
                "influence_advocacy": 0.45,
                "customer_orientation": 0.3,
                "stress_regulation": 0.2,
                "structured_execution": 0.15,
                "collaboration_harmony": 0.1
            },
            required_skills=[
                SkillRequirement("sales_strategy", "銷售策略", 0.9, "advanced", "銷售策略制定和執行"),
                SkillRequirement("negotiation", "談判技巧", 0.8, "advanced", "商業談判和協商"),
                SkillRequirement("team_leadership", "團隊領導", 0.8, "advanced", "銷售團隊管理和激勵")
            ],
            beneficial_skills=[
                SkillRequirement("crm_systems", "CRM系統", 0.6, "intermediate", "客戶關係管理系統"),
                SkillRequirement("market_analysis", "市場分析", 0.7, "intermediate", "市場趨勢和競爭分析")
            ],
            salary_range="70-180萬",
            growth_potential="高",
            work_environment="辦公室/客戶拜訪",
            key_responsibilities=["團隊管理", "銷售策略", "客戶開發", "業績達成", "市場分析"],
            development_paths=[]
        )

        # M002: 行銷專員
        self._career_roles["M002"] = CareerRole(
            role_id="M002",
            role_name="Marketing Specialist",
            chinese_name="行銷專員",
            industry_sector=IndustrySector.CORPORATE,
            experience_levels=[ExperienceLevel.ENTRY, ExperienceLevel.JUNIOR, ExperienceLevel.MID],
            description="規劃執行行銷活動，管理品牌形象，分析市場趨勢並制定行銷策略",
            primary_strengths=["exploration_innovation", "influence_advocacy", "customer_orientation"],
            secondary_strengths=["analytical_insight", "collaboration_harmony"],
            strength_weights={
                "exploration_innovation": 0.35,
                "influence_advocacy": 0.3,
                "customer_orientation": 0.25,
                "analytical_insight": 0.2,
                "collaboration_harmony": 0.15
            },
            required_skills=[
                SkillRequirement("digital_marketing", "數位行銷", 0.9, "advanced", "線上行銷策略和執行"),
                SkillRequirement("content_creation", "內容創作", 0.8, "intermediate", "行銷內容創作和管理"),
                SkillRequirement("analytics", "數據分析", 0.7, "intermediate", "行銷成效分析和優化")
            ],
            beneficial_skills=[
                SkillRequirement("design_tools", "設計工具", 0.6, "basic", "基礎視覺設計能力"),
                SkillRequirement("social_media", "社群媒體", 0.7, "intermediate", "社群媒體經營和管理")
            ],
            salary_range="45-100萬",
            growth_potential="中高",
            work_environment="辦公室",
            key_responsibilities=["活動企劃", "內容創作", "數據分析", "品牌管理", "媒體合作"],
            development_paths=[]
        )

        # H001: 人力資源夥伴
        self._career_roles["H001"] = CareerRole(
            role_id="H001",
            role_name="HR Business Partner",
            chinese_name="人力資源夥伴",
            industry_sector=IndustrySector.CORPORATE,
            experience_levels=[ExperienceLevel.MID, ExperienceLevel.SENIOR],
            description="支援業務單位人力資源策略，協助組織發展與人才管理",
            primary_strengths=["collaboration_harmony", "conflict_integration", "learning_growth"],
            secondary_strengths=["structured_execution", "customer_orientation"],
            strength_weights={
                "collaboration_harmony": 0.35,
                "conflict_integration": 0.3,
                "learning_growth": 0.25,
                "structured_execution": 0.2,
                "customer_orientation": 0.15
            },
            required_skills=[
                SkillRequirement("hr_strategy", "人力資源策略", 0.9, "advanced", "HR策略規劃和執行"),
                SkillRequirement("talent_development", "人才發展", 0.8, "advanced", "員工發展和培訓"),
                SkillRequirement("organizational_psychology", "組織心理學", 0.7, "intermediate", "組織行為和心理學")
            ],
            beneficial_skills=[
                SkillRequirement("hr_systems", "人資系統", 0.6, "intermediate", "HRIS和數位化工具"),
                SkillRequirement("employment_law", "勞動法規", 0.7, "intermediate", "相關法規和合規要求")
            ],
            salary_range="60-140萬",
            growth_potential="中高",
            work_environment="辦公室",
            key_responsibilities=["人才發展", "組織設計", "員工關係", "績效管理", "策略規劃"],
            development_paths=[]
        )

        # O001: 專案經理
        self._career_roles["O001"] = CareerRole(
            role_id="O001",
            role_name="Project Manager",
            chinese_name="專案經理",
            industry_sector=IndustrySector.CORPORATE,
            experience_levels=[ExperienceLevel.MID, ExperienceLevel.SENIOR],
            description="負責專案規劃執行，協調資源配置，確保專案按時按質完成",
            primary_strengths=["structured_execution", "responsibility_accountability", "collaboration_harmony"],
            secondary_strengths=["stress_regulation", "influence_advocacy"],
            strength_weights={
                "structured_execution": 0.4,
                "responsibility_accountability": 0.3,
                "collaboration_harmony": 0.2,
                "stress_regulation": 0.15,
                "influence_advocacy": 0.1
            },
            required_skills=[
                SkillRequirement("project_management", "專案管理", 0.9, "advanced", "PMP或相關專案管理認證"),
                SkillRequirement("resource_planning", "資源規劃", 0.8, "advanced", "人力和資源配置管理"),
                SkillRequirement("risk_management", "風險管理", 0.8, "intermediate", "專案風險識別和控制")
            ],
            beneficial_skills=[
                SkillRequirement("agile_methodology", "敏捷方法論", 0.7, "intermediate", "Scrum或其他敏捷框架"),
                SkillRequirement("stakeholder_communication", "利害關係人溝通", 0.8, "advanced", "多方溝通和協調")
            ],
            salary_range="60-150萬",
            growth_potential="中高",
            work_environment="辦公室",
            key_responsibilities=["專案規劃", "進度管控", "資源協調", "風險管理", "團隊溝通"],
            development_paths=[]
        )

        # O002: 營運經理
        self._career_roles["O002"] = CareerRole(
            role_id="O002",
            role_name="Operations Manager",
            chinese_name="營運經理",
            industry_sector=IndustrySector.MANUFACTURING,
            experience_levels=[ExperienceLevel.MID, ExperienceLevel.SENIOR],
            description="優化營運流程，提升效率品質，管理日常營運活動",
            primary_strengths=["discipline_trust", "structured_execution", "responsibility_accountability"],
            secondary_strengths=["analytical_insight", "stress_regulation"],
            strength_weights={
                "discipline_trust": 0.35,
                "structured_execution": 0.3,
                "responsibility_accountability": 0.25,
                "analytical_insight": 0.2,
                "stress_regulation": 0.15
            },
            required_skills=[
                SkillRequirement("operations_management", "營運管理", 0.9, "advanced", "營運流程設計和優化"),
                SkillRequirement("quality_control", "品質控制", 0.8, "advanced", "品質管理系統和方法"),
                SkillRequirement("supply_chain", "供應鏈管理", 0.8, "intermediate", "供應鏈協調和管理")
            ],
            beneficial_skills=[
                SkillRequirement("lean_manufacturing", "精實生產", 0.7, "intermediate", "精實管理方法論"),
                SkillRequirement("cost_analysis", "成本分析", 0.7, "intermediate", "成本控制和分析")
            ],
            salary_range="55-130萬",
            growth_potential="中",
            work_environment="工廠/辦公室",
            key_responsibilities=["流程優化", "品質管控", "成本控制", "團隊管理", "供應鏈協調"],
            development_paths=[]
        )

    def _load_development_library(self):
        """載入發展建議庫"""

        # 技術類發展建議
        self._development_library["tech_001"] = DevelopmentSuggestion(
            suggestion_id="tech_001",
            title="學習先進的專案管理方法論",
            description="掌握PMP、Scrum、Kanban等現代專案管理框架，提升專案執行效率",
            priority="high",
            category="technical",
            time_investment="medium-term",
            resources=["PMP認證課程", "Scrum Master培訓", "專案管理工具實作"]
        )

        self._development_library["tech_002"] = DevelopmentSuggestion(
            suggestion_id="tech_002",
            title="培養跨部門協調能力",
            description="發展跨功能團隊合作技能，學習利害關係人管理和溝通技巧",
            priority="high",
            category="communication",
            time_investment="medium-term",
            resources=["跨部門協作工作坊", "溝通技巧培訓", "實際專案實習"]
        )

        self._development_library["tech_003"] = DevelopmentSuggestion(
            suggestion_id="tech_003",
            title="提升數據分析與決策技能",
            description="加強數據分析能力，學習商業智慧工具，提升數據驅動決策能力",
            priority="medium",
            category="technical",
            time_investment="short-term",
            resources=["Excel高級課程", "SQL資料庫課程", "商業分析證照"]
        )

        # 領導類發展建議
        self._development_library["leadership_001"] = DevelopmentSuggestion(
            suggestion_id="leadership_001",
            title="發展領導他人追求卓越的能力",
            description="學習如何激勵團隊追求高品質標準，建立卓越文化",
            priority="high",
            category="leadership",
            time_investment="long-term",
            resources=["領導力發展課程", "教練技能培訓", "導師制度參與"]
        )

        self._development_library["leadership_002"] = DevelopmentSuggestion(
            suggestion_id="leadership_002",
            title="培養創新思維以提升品質標準",
            description="結合創新思維與品質管理，推動持續改善和創新",
            priority="medium",
            category="innovation",
            time_investment="medium-term",
            resources=["設計思考工作坊", "創新管理課程", "品質改善專案"]
        )

        # 繼續添加更多發展建議...
        self._add_more_development_suggestions()

    def _add_more_development_suggestions(self):
        """添加更多發展建議"""

        # 創新類
        self._development_library["innovation_001"] = DevelopmentSuggestion(
            suggestion_id="innovation_001",
            title="參與跨領域學習與合作",
            description="接觸不同領域的知識和專家，拓展視野並激發創新靈感",
            priority="medium",
            category="innovation",
            time_investment="long-term",
            resources=["跨領域研習營", "產業交流活動", "多元學習平台"]
        )

        self._development_library["innovation_002"] = DevelopmentSuggestion(
            suggestion_id="innovation_002",
            title="建立創新想法的實作能力",
            description="將創意轉化為可執行的方案，學習原型開發和測試方法",
            priority="high",
            category="innovation",
            time_investment="medium-term",
            resources=["原型開發工具", "MVP開發方法", "使用者測試技巧"]
        )

        # 溝通類
        self._development_library["communication_001"] = DevelopmentSuggestion(
            suggestion_id="communication_001",
            title="提升演講與簡報技巧",
            description="加強公開演講能力，學習專業簡報設計和表達技巧",
            priority="high",
            category="communication",
            time_investment="short-term",
            resources=["演講技巧課程", "簡報設計培訓", "Toastmasters國際演講會"]
        )

        self._development_library["communication_002"] = DevelopmentSuggestion(
            suggestion_id="communication_002",
            title="學習談判與說服技術",
            description="掌握商業談判技巧，提升影響力和說服能力",
            priority="medium",
            category="communication",
            time_investment="medium-term",
            resources=["談判技巧課程", "影響力心理學", "實戰案例研習"]
        )

        # 分析類
        self._development_library["analytical_001"] = DevelopmentSuggestion(
            suggestion_id="analytical_001",
            title="加強數據科學與統計技能",
            description="深化統計分析能力，學習機器學習和預測模型建構",
            priority="high",
            category="technical",
            time_investment="long-term",
            resources=["統計學進階課程", "機器學習認證", "數據科學實作專案"]
        )

        self._development_library["analytical_002"] = DevelopmentSuggestion(
            suggestion_id="analytical_002",
            title="學習商業分析與決策支援",
            description="結合技術分析與商業洞察，提供有價值的決策建議",
            priority="medium",
            category="business",
            time_investment="medium-term",
            resources=["商業分析證照", "案例研究方法", "企業實習機會"]
        )

    # 公開方法
    def get_strength_theme(self, theme_id: str) -> Optional[StrengthTheme]:
        """獲取優勢主題"""
        return self._strength_themes.get(theme_id)

    def get_career_role(self, role_id: str) -> Optional[CareerRole]:
        """獲取職涯角色"""
        return self._career_roles.get(role_id)

    def get_development_suggestion(self, suggestion_id: str) -> Optional[DevelopmentSuggestion]:
        """獲取發展建議"""
        return self._development_library.get(suggestion_id)

    def get_all_strength_themes(self) -> Dict[str, StrengthTheme]:
        """獲取所有優勢主題"""
        return self._strength_themes.copy()

    def get_all_career_roles(self) -> Dict[str, CareerRole]:
        """獲取所有職涯角色"""
        return self._career_roles.copy()

    def get_roles_for_strength(self, strength_id: str) -> List[CareerRole]:
        """根據優勢獲取適合的職涯角色"""
        strength_theme = self.get_strength_theme(strength_id)
        if not strength_theme:
            return []

        # 獲取最適合和相容的角色
        role_ids = strength_theme.best_fit_roles + strength_theme.compatible_roles
        roles = []
        for role_id in role_ids:
            role = self.get_career_role(role_id)
            if role:
                roles.append(role)

        return roles

    def get_strengths_for_role(self, role_id: str) -> List[StrengthTheme]:
        """根據職涯角色獲取需要的優勢"""
        role = self.get_career_role(role_id)
        if not role:
            return []

        strength_ids = role.get_all_required_strengths()
        strengths = []
        for strength_id in strength_ids:
            strength = self.get_strength_theme(strength_id)
            if strength:
                strengths.append(strength)

        return strengths

    def get_development_suggestions_for_strength(self, strength_id: str) -> List[DevelopmentSuggestion]:
        """根據優勢獲取發展建議"""
        strength_theme = self.get_strength_theme(strength_id)
        if not strength_theme:
            return []

        return strength_theme.development_suggestions.copy()

    def get_development_suggestions_for_role(self, role_id: str) -> List[DevelopmentSuggestion]:
        """根據職涯角色獲取發展建議"""
        role = self.get_career_role(role_id)
        if not role:
            return []

        return role.development_paths.copy()

    def find_career_matches_by_strengths(self, user_strengths: List[str], top_n: int = 5) -> List[Tuple[CareerRole, float]]:
        """根據用戶優勢找到匹配的職涯角色"""
        matches = []

        for role in self._career_roles.values():
            # 計算匹配分數
            match_score = 0.0
            total_weight = 0.0

            for strength_id in user_strengths:
                weight = role.get_strength_weight(strength_id)
                if weight > 0:
                    match_score += weight
                total_weight += weight

            # 正規化分數
            if total_weight > 0:
                normalized_score = match_score / total_weight
                matches.append((role, normalized_score))

        # 按分數排序並返回前N個
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:top_n]


# 全域實例
_knowledge_base = None

def get_career_knowledge_base() -> CareerKnowledgeBase:
    """獲取職涯知識庫實例（單例模式）"""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = CareerKnowledgeBase()
    return _knowledge_base