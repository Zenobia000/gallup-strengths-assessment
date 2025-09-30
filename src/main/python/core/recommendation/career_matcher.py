"""
Career Matcher - Job Role Matching Based on Strengths

基於統一職涯知識庫的智能職涯匹配系統
分析優勢檔案並與適合的職位角色和發展路徑進行匹配

設計原則：
- 使用統一知識庫確保數據一致性
- 透明的評分算法
- 實用的職涯建議
- 支援本地化和文化背景

主要功能：
- 統一的職位角色資料庫
- 優勢導向的匹配算法
- 產業分類和經驗等級考量
- 文化和市場背景支援
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

from .strength_mapper import StrengthProfile, StrengthScore, StrengthDomain
from ..knowledge.career_knowledge_base import (
    get_career_knowledge_base,
    CareerRole,
    StrengthCategory,
    IndustrySector,
    ExperienceLevel
)


# 移除重複的枚舉定義，使用統一知識庫中的定義


# 移除重複的 JobRole 定義，使用統一知識庫中的 CareerRole


@dataclass
class CareerMatch:
    """A career match result with scoring details."""
    job_role: CareerRole
    role_name: str
    chinese_name: str
    industry_sector: str
    match_score: float
    strength_alignment: Dict[str, float]
    domain_fit: Dict[StrengthDomain, float]
    confidence: float
    matching_strengths: List[str]
    development_needs: List[str]
    description: str
    required_strengths: List[str]
    reasons: List[str]

    def __str__(self) -> str:
        return f"{self.chinese_name} - 匹配度: {self.match_score:.1f}% (信心: {self.confidence:.2f})"


class CareerMatcher:
    """
    基於優勢檔案的智能職涯匹配系統

    使用統一職涯知識庫分析優勢檔案，並與職位角色進行匹配，
    提供評分建議和詳細說明。
    """

    def __init__(self):
        """Initialize the career matcher with unified knowledge base."""
        self.knowledge_base = get_career_knowledge_base()

        # 保留舊的載入邏輯作為備用
        # self.job_roles = self._load_job_roles()  # 已廢棄，改用統一知識庫

    def _load_job_roles(self) -> List[CareerRole]:
        """Load comprehensive job role database."""
        roles = []

        # Technology Sector
        roles.append(JobRole(
            role_id="T001",
            role_name="Software Engineer",
            chinese_name="軟體工程師",
            industry_sector=IndustrySector.TECHNOLOGY,
            experience_levels=[ExperienceLevel.ENTRY, ExperienceLevel.JUNIOR, ExperienceLevel.MID, ExperienceLevel.SENIOR],
            description="設計、開發和維護軟體系統，解決技術問題並創建創新解決方案",
            required_strengths=["analytical", "learner", "focus", "restorative"],
            beneficial_strengths=["strategic", "achiever", "deliberative"],
            domain_weights={
                StrengthDomain.STRATEGIC_THINKING: 0.4,
                StrengthDomain.EXECUTING: 0.3,
                StrengthDomain.INFLUENCING: 0.1,
                StrengthDomain.RELATIONSHIP_BUILDING: 0.2
            },
            min_education="學士",
            typical_salary_range="60-150萬",
            growth_potential="高",
            work_environment="辦公室/遠距",
            key_responsibilities=["系統設計", "程式碼開發", "測試除錯", "技術文件", "團隊協作"]
        ))

        roles.append(JobRole(
            role_id="T002",
            role_name="Product Manager",
            chinese_name="產品經理",
            industry_sector=IndustrySector.TECHNOLOGY,
            experience_levels=[ExperienceLevel.MID, ExperienceLevel.SENIOR],
            description="負責產品策略、開發流程管理，協調跨部門合作實現產品目標",
            required_strengths=["strategic", "activator", "communication", "arranger"],
            beneficial_strengths=["futuristic", "maximizer", "analytical"],
            domain_weights={
                StrengthDomain.STRATEGIC_THINKING: 0.35,
                StrengthDomain.EXECUTING: 0.25,
                StrengthDomain.INFLUENCING: 0.25,
                StrengthDomain.RELATIONSHIP_BUILDING: 0.15
            },
            min_education="學士",
            typical_salary_range="80-200萬",
            growth_potential="高",
            work_environment="辦公室",
            key_responsibilities=["產品策略", "需求分析", "專案管理", "跨部門協調", "市場研究"]
        ))

        roles.append(JobRole(
            role_id="T003",
            role_name="Data Scientist",
            chinese_name="資料科學家",
            industry_sector=IndustrySector.TECHNOLOGY,
            experience_levels=[ExperienceLevel.JUNIOR, ExperienceLevel.MID, ExperienceLevel.SENIOR],
            description="運用統計學和機器學習分析大數據，提供商業洞察和預測模型",
            required_strengths=["analytical", "input", "intellection", "strategic"],
            beneficial_strengths=["learner", "context", "deliberative"],
            domain_weights={
                StrengthDomain.STRATEGIC_THINKING: 0.6,
                StrengthDomain.EXECUTING: 0.2,
                StrengthDomain.INFLUENCING: 0.1,
                StrengthDomain.RELATIONSHIP_BUILDING: 0.1
            },
            min_education="碩士",
            typical_salary_range="70-180萬",
            growth_potential="高",
            work_environment="辦公室/混合",
            key_responsibilities=["資料分析", "模型建構", "統計推論", "可視化報告", "業務諮詢"]
        ))

        # Business & Finance
        roles.append(JobRole(
            role_id="F001",
            role_name="Management Consultant",
            chinese_name="管理顧問",
            industry_sector=IndustrySector.CONSULTING,
            experience_levels=[ExperienceLevel.JUNIOR, ExperienceLevel.MID, ExperienceLevel.SENIOR],
            description="為企業提供策略建議，協助解決營運問題並優化商業流程",
            required_strengths=["analytical", "strategic", "communication", "maximizer"],
            beneficial_strengths=["achiever", "command", "significance"],
            domain_weights={
                StrengthDomain.STRATEGIC_THINKING: 0.4,
                StrengthDomain.EXECUTING: 0.2,
                StrengthDomain.INFLUENCING: 0.3,
                StrengthDomain.RELATIONSHIP_BUILDING: 0.1
            },
            min_education="碩士",
            typical_salary_range="80-250萬",
            growth_potential="高",
            work_environment="客戶現場/差旅",
            key_responsibilities=["問題分析", "策略規劃", "客戶簡報", "專案執行", "團隊領導"]
        ))

        roles.append(JobRole(
            role_id="F002",
            role_name="Financial Analyst",
            chinese_name="財務分析師",
            industry_sector=IndustrySector.FINANCE,
            experience_levels=[ExperienceLevel.ENTRY, ExperienceLevel.JUNIOR, ExperienceLevel.MID],
            description="分析財務數據，評估投資機會，支援財務決策制定",
            required_strengths=["analytical", "discipline", "deliberative", "focus"],
            beneficial_strengths=["achiever", "consistency", "input"],
            domain_weights={
                StrengthDomain.STRATEGIC_THINKING: 0.4,
                StrengthDomain.EXECUTING: 0.4,
                StrengthDomain.INFLUENCING: 0.1,
                StrengthDomain.RELATIONSHIP_BUILDING: 0.1
            },
            min_education="學士",
            typical_salary_range="55-120萬",
            growth_potential="中高",
            work_environment="辦公室",
            key_responsibilities=["財報分析", "預算規劃", "風險評估", "投資建議", "合規檢核"]
        ))

        # Sales & Marketing
        roles.append(JobRole(
            role_id="M001",
            role_name="Sales Manager",
            chinese_name="業務經理",
            industry_sector=IndustrySector.CORPORATE,
            experience_levels=[ExperienceLevel.MID, ExperienceLevel.SENIOR],
            description="領導銷售團隊，制定銷售策略，達成營收目標並建立客戶關係",
            required_strengths=["woo", "activator", "communication", "achiever"],
            beneficial_strengths=["competition", "maximizer", "positivity"],
            domain_weights={
                StrengthDomain.STRATEGIC_THINKING: 0.15,
                StrengthDomain.EXECUTING: 0.25,
                StrengthDomain.INFLUENCING: 0.45,
                StrengthDomain.RELATIONSHIP_BUILDING: 0.15
            },
            min_education="學士",
            typical_salary_range="70-180萬",
            growth_potential="高",
            work_environment="辦公室/客戶拜訪",
            key_responsibilities=["團隊管理", "銷售策略", "客戶開發", "業績達成", "市場分析"]
        ))

        roles.append(JobRole(
            role_id="M002",
            role_name="Marketing Specialist",
            chinese_name="行銷專員",
            industry_sector=IndustrySector.CORPORATE,
            experience_levels=[ExperienceLevel.ENTRY, ExperienceLevel.JUNIOR, ExperienceLevel.MID],
            description="規劃執行行銷活動，管理品牌形象，分析市場趨勢並制定行銷策略",
            required_strengths=["ideation", "communication", "strategic", "activator"],
            beneficial_strengths=["futuristic", "woo", "maximizer"],
            domain_weights={
                StrengthDomain.STRATEGIC_THINKING: 0.3,
                StrengthDomain.EXECUTING: 0.2,
                StrengthDomain.INFLUENCING: 0.35,
                StrengthDomain.RELATIONSHIP_BUILDING: 0.15
            },
            min_education="學士",
            typical_salary_range="45-100萬",
            growth_potential="中高",
            work_environment="辦公室",
            key_responsibilities=["活動企劃", "內容創作", "數據分析", "品牌管理", "媒體合作"]
        ))

        # Human Resources
        roles.append(JobRole(
            role_id="H001",
            role_name="HR Business Partner",
            chinese_name="人力資源夥伴",
            industry_sector=IndustrySector.CORPORATE,
            experience_levels=[ExperienceLevel.MID, ExperienceLevel.SENIOR],
            description="支援業務單位人力資源策略，協助組織發展與人才管理",
            required_strengths=["developer", "empathy", "strategic", "relator"],
            beneficial_strengths=["individualization", "harmony", "communication"],
            domain_weights={
                StrengthDomain.STRATEGIC_THINKING: 0.25,
                StrengthDomain.EXECUTING: 0.2,
                StrengthDomain.INFLUENCING: 0.2,
                StrengthDomain.RELATIONSHIP_BUILDING: 0.35
            },
            min_education="學士",
            typical_salary_range="60-140萬",
            growth_potential="中高",
            work_environment="辦公室",
            key_responsibilities=["人才發展", "組織設計", "員工關係", "績效管理", "策略規劃"]
        ))

        # Operations & Project Management
        roles.append(JobRole(
            role_id="O001",
            role_name="Project Manager",
            chinese_name="專案經理",
            industry_sector=IndustrySector.CORPORATE,
            experience_levels=[ExperienceLevel.MID, ExperienceLevel.SENIOR],
            description="負責專案規劃執行，協調資源配置，確保專案按時按質完成",
            required_strengths=["arranger", "responsibility", "focus", "activator"],
            beneficial_strengths=["discipline", "achiever", "communication"],
            domain_weights={
                StrengthDomain.STRATEGIC_THINKING: 0.2,
                StrengthDomain.EXECUTING: 0.45,
                StrengthDomain.INFLUENCING: 0.25,
                StrengthDomain.RELATIONSHIP_BUILDING: 0.1
            },
            min_education="學士",
            typical_salary_range="60-150萬",
            growth_potential="中高",
            work_environment="辦公室",
            key_responsibilities=["專案規劃", "進度管控", "資源協調", "風險管理", "團隊溝通"]
        ))

        roles.append(JobRole(
            role_id="O002",
            role_name="Operations Manager",
            chinese_name="營運經理",
            industry_sector=IndustrySector.MANUFACTURING,
            experience_levels=[ExperienceLevel.MID, ExperienceLevel.SENIOR],
            description="優化營運流程，提升效率品質，管理日常營運活動",
            required_strengths=["discipline", "consistency", "analytical", "arranger"],
            beneficial_strengths=["maximizer", "focus", "responsibility"],
            domain_weights={
                StrengthDomain.STRATEGIC_THINKING: 0.2,
                StrengthDomain.EXECUTING: 0.5,
                StrengthDomain.INFLUENCING: 0.2,
                StrengthDomain.RELATIONSHIP_BUILDING: 0.1
            },
            min_education="學士",
            typical_salary_range="55-130萬",
            growth_potential="中",
            work_environment="工廠/辦公室",
            key_responsibilities=["流程優化", "品質管控", "成本控制", "團隊管理", "供應鏈協調"]
        ))

        return roles

    def find_career_matches(
        self,
        strength_profile: StrengthProfile,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[CareerMatch]:
        """
        根據優勢檔案和用戶背景尋找職涯匹配

        Args:
            strength_profile: StrengthMapper 產生的完整優勢檔案
            user_context: 用戶偏好和背景（經驗、產業等）

        Returns:
            依匹配分數排序的 CareerMatch 列表（最高分在前）
        """
        if user_context is None:
            user_context = {}

        matches = []

        # 從統一知識庫獲取所有職涯角色
        career_roles = self.knowledge_base.get_all_career_roles()

        for role_id, career_role in career_roles.items():
            match = self._calculate_job_match_from_knowledge_base(
                career_role, strength_profile, user_context
            )
            matches.append(match)

        # 依匹配分數排序（最高在前）
        return sorted(matches, key=lambda x: x.match_score, reverse=True)

    def _calculate_job_match_from_knowledge_base(
        self,
        career_role: CareerRole,
        strength_profile: StrengthProfile,
        user_context: Dict[str, Any]
    ) -> CareerMatch:
        """根據統一知識庫計算職位匹配分數"""

        # 1. 計算優勢對齊度
        strength_alignment = self._calculate_strength_alignment_from_kb(career_role, strength_profile)

        # 2. 計算領域適配度
        domain_fit = self._calculate_domain_fit_from_kb(career_role, strength_profile)

        # 3. 應用情境獎勵（經驗、產業偏好等）
        context_bonus = self._calculate_context_bonus_from_kb(career_role, user_context)

        # 4. 計算整體匹配分數
        base_score = (
            sum(strength_alignment.values()) * 0.6 +  # 優勢對齊最重要
            sum(domain_fit.values()) * 0.3 +          # 領域適配次要
            context_bonus * 0.1                       # 情境獎勵最少
        )

        # 正規化至 0-100 範圍
        match_score = min(100, max(0, base_score))

        # 5. 基於優勢檔案信心計算匹配信心
        confidence = self._calculate_match_confidence_from_kb(
            strength_profile, strength_alignment, domain_fit
        )

        # 6. 識別匹配優勢和發展需求
        matching_strengths, development_needs = self._analyze_strength_gaps_from_kb(
            career_role, strength_profile
        )

        # 7. 生成匹配原因
        reasons = self._generate_match_reasons_from_kb(
            career_role, strength_alignment, domain_fit, matching_strengths
        )

        return CareerMatch(
            job_role=career_role,
            role_name=career_role.role_name,
            chinese_name=career_role.chinese_name,
            industry_sector=career_role.industry_sector.value,
            match_score=match_score,
            strength_alignment=strength_alignment,
            domain_fit=domain_fit,
            confidence=confidence,
            matching_strengths=matching_strengths,
            development_needs=development_needs,
            description=career_role.description,
            required_strengths=career_role.primary_strengths,
            reasons=reasons
        )

    def _calculate_job_match(
        self,
        job_role: CareerRole,  # 修正型別
        strength_profile: StrengthProfile,
        user_context: Dict[str, Any]
    ) -> CareerMatch:
        """Calculate match score for a specific job role."""

        # 1. Calculate strength alignment
        strength_alignment = self._calculate_strength_alignment(job_role, strength_profile)

        # 2. Calculate domain fit
        domain_fit = self._calculate_domain_fit(job_role, strength_profile)

        # 3. Apply context filters (experience, industry preference, etc.)
        context_bonus = self._calculate_context_bonus(job_role, user_context)

        # 4. Calculate overall match score
        base_score = (
            sum(strength_alignment.values()) * 0.6 +  # Strength alignment is most important
            sum(domain_fit.values()) * 0.3 +          # Domain fit secondary
            context_bonus * 0.1                       # Context bonus least weight
        )

        # Normalize to 0-100 scale
        match_score = min(100, max(0, base_score))

        # 5. Calculate confidence based on strength profile confidence
        confidence = self._calculate_match_confidence(strength_profile, strength_alignment, domain_fit)

        # 6. Identify matching strengths and development needs
        matching_strengths, development_needs = self._analyze_strength_gaps(
            job_role, strength_profile
        )

        # 7. Generate reasons for the match
        reasons = self._generate_match_reasons(job_role, strength_alignment, domain_fit, matching_strengths)

        return CareerMatch(
            job_role=job_role,
            role_name=job_role.role_name,
            chinese_name=job_role.chinese_name,
            industry_sector=job_role.industry_sector.value,
            match_score=match_score,
            strength_alignment=strength_alignment,
            domain_fit=domain_fit,
            confidence=confidence,
            matching_strengths=matching_strengths,
            development_needs=development_needs,
            description=job_role.description,
            required_strengths=job_role.required_strengths,
            reasons=reasons
        )

    def _calculate_strength_alignment(
        self,
        job_role: JobRole,
        strength_profile: StrengthProfile
    ) -> Dict[str, float]:
        """Calculate how well user strengths align with job requirements."""
        alignment = {}

        # Get user's strength themes as a lookup
        user_strengths = {
            s.theme.name.lower(): s.percentile_score
            for s in strength_profile.all_strengths
        }

        # Calculate alignment for required strengths (higher weight)
        required_alignment = 0
        for required_strength in job_role.required_strengths:
            strength_score = user_strengths.get(required_strength.lower(), 0)
            # Convert to 0-1 scale and apply as match factor
            alignment[f"required_{required_strength}"] = strength_score / 100
            required_alignment += strength_score / 100

        # Calculate alignment for beneficial strengths (lower weight)
        beneficial_alignment = 0
        for beneficial_strength in job_role.beneficial_strengths:
            strength_score = user_strengths.get(beneficial_strength.lower(), 0)
            alignment[f"beneficial_{beneficial_strength}"] = strength_score / 100 * 0.5
            beneficial_alignment += strength_score / 100 * 0.5

        # Normalize by number of strengths considered
        total_required = len(job_role.required_strengths)
        total_beneficial = len(job_role.beneficial_strengths)

        if total_required > 0:
            alignment["required_average"] = required_alignment / total_required
        if total_beneficial > 0:
            alignment["beneficial_average"] = beneficial_alignment / total_beneficial

        return alignment

    def _calculate_domain_fit(
        self,
        job_role: JobRole,
        strength_profile: StrengthProfile
    ) -> Dict[StrengthDomain, float]:
        """Calculate how well user's domain distribution fits job requirements."""
        domain_fit = {}

        for domain, job_weight in job_role.domain_weights.items():
            user_percentage = strength_profile.domain_distribution.get(domain, 0)

            # Calculate fit as correlation between job requirement and user strength
            # Higher fit when user strength matches job requirement
            fit_score = min(1.0, user_percentage / 100) * job_weight
            domain_fit[domain] = fit_score

        return domain_fit

    def _calculate_context_bonus(
        self,
        job_role: JobRole,
        user_context: Dict[str, Any]
    ) -> float:
        """Calculate bonus/penalty based on user context preferences."""
        bonus = 0

        # Industry preference bonus
        preferred_industry = user_context.get("industry_preference", "").lower()
        if preferred_industry and preferred_industry in job_role.industry_sector.value.lower():
            bonus += 10

        # Experience level match
        user_experience = user_context.get("experience_level", "").lower()
        if user_experience:
            try:
                user_exp_level = ExperienceLevel(user_experience)
                if user_exp_level in job_role.experience_levels:
                    bonus += 15
            except ValueError:
                pass  # Invalid experience level

        # Salary expectation match
        salary_expectation = user_context.get("salary_expectation", 0)
        if salary_expectation > 0:
            # Simple heuristic: extract numbers from salary range
            salary_range = job_role.typical_salary_range
            try:
                # Extract min and max from range like "60-150萬"
                numbers = [int(s) for s in salary_range.replace("萬", "").split("-") if s.isdigit()]
                if len(numbers) == 2:
                    min_salary, max_salary = numbers
                    if min_salary <= salary_expectation <= max_salary:
                        bonus += 10
                    elif salary_expectation < min_salary:
                        bonus -= 5  # Below expectations
            except:
                pass

        return bonus

    def _calculate_match_confidence(
        self,
        strength_profile: StrengthProfile,
        strength_alignment: Dict[str, float],
        domain_fit: Dict[StrengthDomain, float]
    ) -> float:
        """Calculate confidence in the match quality."""

        # Base confidence from strength profile
        base_confidence = strength_profile.profile_confidence

        # Alignment confidence - higher when key strengths are well-aligned
        alignment_confidence = 0
        if "required_average" in strength_alignment:
            alignment_confidence = strength_alignment["required_average"]

        # Domain fit confidence - higher when domains are well-matched
        domain_confidence = sum(domain_fit.values()) / len(domain_fit) if domain_fit else 0

        # Combined confidence
        overall_confidence = (
            base_confidence * 0.4 +
            alignment_confidence * 0.4 +
            domain_confidence * 0.2
        )

        return min(1.0, max(0.0, overall_confidence))

    def _analyze_strength_gaps(
        self,
        job_role: JobRole,
        strength_profile: StrengthProfile
    ) -> Tuple[List[str], List[str]]:
        """Analyze which strengths match and which need development."""
        user_strength_names = [s.theme.name.lower() for s in strength_profile.top_5_strengths]

        matching_strengths = []
        development_needs = []

        # Check required strengths
        for required in job_role.required_strengths:
            if required.lower() in user_strength_names:
                matching_strengths.append(required)
            else:
                development_needs.append(required)

        # Check beneficial strengths
        for beneficial in job_role.beneficial_strengths:
            if beneficial.lower() in user_strength_names and beneficial not in matching_strengths:
                matching_strengths.append(beneficial)

        return matching_strengths, development_needs

    def _generate_match_reasons(
        self,
        job_role: JobRole,
        strength_alignment: Dict[str, float],
        domain_fit: Dict[StrengthDomain, float],
        matching_strengths: List[str]
    ) -> List[str]:
        """Generate human-readable reasons for the career match."""
        reasons = []

        # Strong strength matches
        if matching_strengths:
            reasons.append(f"您的{', '.join(matching_strengths[:2])}優勢與此職位高度匹配")

        # Domain alignment
        top_domain = max(domain_fit.items(), key=lambda x: x[1]) if domain_fit else None
        if top_domain and top_domain[1] > 0.3:
            domain_names = {
                StrengthDomain.EXECUTING: "執行力",
                StrengthDomain.INFLUENCING: "影響力",
                StrengthDomain.RELATIONSHIP_BUILDING: "關係建立",
                StrengthDomain.STRATEGIC_THINKING: "戰略思維"
            }
            domain_name = domain_names.get(top_domain[0], "")
            if domain_name:
                reasons.append(f"您在{domain_name}領域的優勢適合此職位需求")

        # Industry fit
        reasons.append(f"{job_role.industry_sector.value}產業提供良好的發展機會")

        return reasons[:3]  # Limit to top 3 reasons


    # 新增基於統一知識庫的匹配方法
    def _calculate_strength_alignment_from_kb(self, career_role: CareerRole, strength_profile: StrengthProfile) -> Dict[str, float]:
        """計算優勢對齊度 - 基於統一知識庫"""
        alignment = {}

        # 獲取用戶優勢分數
        user_strengths = {s.name: s.score for s in strength_profile.all_strengths}

        # 計算主要優勢對齊（較高權重）
        primary_alignment = 0
        for required_strength in career_role.primary_strengths:
            strength_score = user_strengths.get(required_strength, 0)
            weight = career_role.get_strength_weight(required_strength)
            alignment_score = (strength_score / 100) * weight
            alignment[f"primary_{required_strength}"] = alignment_score
            primary_alignment += alignment_score

        # 計算次要優勢對齊（較低權重）
        secondary_alignment = 0
        for beneficial_strength in career_role.secondary_strengths:
            strength_score = user_strengths.get(beneficial_strength, 0)
            weight = career_role.get_strength_weight(beneficial_strength) * 0.5  # 次要優勢權重減半
            alignment_score = (strength_score / 100) * weight
            alignment[f"secondary_{beneficial_strength}"] = alignment_score
            secondary_alignment += alignment_score

        # 計算平均對齊度
        total_primary = len(career_role.primary_strengths)
        total_secondary = len(career_role.secondary_strengths)

        if total_primary > 0:
            alignment["primary_average"] = primary_alignment / total_primary
        if total_secondary > 0:
            alignment["secondary_average"] = secondary_alignment / total_secondary

        return alignment

    def _calculate_domain_fit_from_kb(self, career_role: CareerRole, strength_profile: StrengthProfile) -> Dict[StrengthCategory, float]:
        """計算領域適配度 - 基於統一知識庫"""
        domain_fit = {}

        # 計算每個優勢類別的用戶分布
        user_category_scores = {}
        category_counts = {}

        for strength in strength_profile.all_strengths:
            # 從知識庫獲取優勢主題以確定類別
            strength_theme = self.knowledge_base.get_strength_theme(strength.name)
            if strength_theme:
                category = strength_theme.category
                if category not in user_category_scores:
                    user_category_scores[category] = 0
                    category_counts[category] = 0
                user_category_scores[category] += strength.score
                category_counts[category] += 1

        # 計算平均分數
        user_category_averages = {}
        for category, total_score in user_category_scores.items():
            user_category_averages[category] = total_score / category_counts[category]

        # 計算與職位需求的適配度
        for category in StrengthCategory:
            user_strength = user_category_averages.get(category, 0)
            # 簡化的適配度計算：用戶該類別的強度
            domain_fit[category] = user_strength / 100

        return domain_fit

    def _calculate_context_bonus_from_kb(self, career_role: CareerRole, user_context: Dict[str, Any]) -> float:
        """計算情境獎勵 - 基於統一知識庫"""
        bonus = 0

        # 產業偏好獎勵
        preferred_industry = user_context.get("industry_preference", "").lower()
        if preferred_industry and preferred_industry in career_role.industry_sector.value.lower():
            bonus += 10

        # 經驗等級匹配
        user_experience = user_context.get("experience_level", "").lower()
        if user_experience:
            try:
                user_exp_level = ExperienceLevel(user_experience)
                if user_exp_level in career_role.experience_levels:
                    bonus += 15
            except ValueError:
                pass

        # 薪資期望匹配
        salary_expectation = user_context.get("salary_expectation", 0)
        if salary_expectation > 0:
            try:
                # 從薪資範圍提取數字，如 "60-150萬"
                numbers = [int(s) for s in career_role.salary_range.replace("萬", "").split("-") if s.isdigit()]
                if len(numbers) == 2:
                    min_salary, max_salary = numbers
                    if min_salary <= salary_expectation <= max_salary:
                        bonus += 10
                    elif salary_expectation < min_salary:
                        bonus -= 5
            except:
                pass

        return bonus

    def _calculate_match_confidence_from_kb(self, strength_profile: StrengthProfile,
                                          strength_alignment: Dict[str, float],
                                          domain_fit: Dict[StrengthCategory, float]) -> float:
        """計算匹配信心 - 基於統一知識庫"""
        # 基礎信心來自優勢檔案
        base_confidence = strength_profile.profile_confidence

        # 對齊信心 - 主要優勢對齊度越高信心越高
        alignment_confidence = 0
        if "primary_average" in strength_alignment:
            alignment_confidence = strength_alignment["primary_average"]

        # 領域信心 - 領域適配度平均值
        domain_confidence = sum(domain_fit.values()) / len(domain_fit) if domain_fit else 0

        # 綜合信心
        overall_confidence = (
            base_confidence * 0.4 +
            alignment_confidence * 0.4 +
            domain_confidence * 0.2
        )

        return min(1.0, max(0.0, overall_confidence))

    def _analyze_strength_gaps_from_kb(self, career_role: CareerRole,
                                     strength_profile: StrengthProfile) -> Tuple[List[str], List[str]]:
        """分析優勢差距 - 基於統一知識庫"""
        user_strength_names = [s.name for s in strength_profile.top_5_strengths]

        matching_strengths = []
        development_needs = []

        # 檢查主要優勢
        for required in career_role.primary_strengths:
            if required in user_strength_names:
                matching_strengths.append(required)
            else:
                development_needs.append(required)

        # 檢查次要優勢
        for beneficial in career_role.secondary_strengths:
            if beneficial in user_strength_names and beneficial not in matching_strengths:
                matching_strengths.append(beneficial)

        return matching_strengths, development_needs

    def _generate_match_reasons_from_kb(self, career_role: CareerRole,
                                      strength_alignment: Dict[str, float],
                                      domain_fit: Dict[StrengthCategory, float],
                                      matching_strengths: List[str]) -> List[str]:
        """生成匹配原因 - 基於統一知識庫"""
        reasons = []

        # 優勢匹配原因
        if matching_strengths:
            # 從知識庫獲取優勢的中文名稱
            chinese_names = []
            for strength_id in matching_strengths[:2]:
                strength_theme = self.knowledge_base.get_strength_theme(strength_id)
                if strength_theme:
                    chinese_names.append(strength_theme.chinese_name)

            if chinese_names:
                reasons.append(f"您的{', '.join(chinese_names)}優勢與此職位高度匹配")

        # 領域對齊原因
        top_domain = max(domain_fit.items(), key=lambda x: x[1]) if domain_fit else None
        if top_domain and top_domain[1] > 0.3:
            domain_names = {
                StrengthCategory.EXECUTION: "執行力",
                StrengthCategory.INFLUENCING: "影響力",
                StrengthCategory.RELATIONSHIP: "關係建立",
                StrengthCategory.THINKING: "策略思維"
            }
            domain_name = domain_names.get(top_domain[0], "")
            if domain_name:
                reasons.append(f"您在{domain_name}領域的優勢適合此職位需求")

        # 產業機會原因
        reasons.append(f"{career_role.industry_sector.value}產業提供良好的發展機會")

        return reasons[:3]  # 限制為前3個原因


def get_career_matcher() -> CareerMatcher:
    """Get a configured CareerMatcher instance."""
    return CareerMatcher()