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

from .strength_mapper import StrengthProfile, StrengthScore
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
    domain_fit: Dict[StrengthCategory, float]
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

    def _load_job_roles_deprecated(self) -> List[Dict]:
        """已廢棄：載入職位角色資料庫 - 改用統一知識庫"""
        # 這個方法已不再使用，保留作為參考
        return []

    def _load_job_roles_old_implementation(self):
        """舊的實作方式，已廢棄但保留作為參考"""
        roles = []

        # 注意：以下程式碼已不再使用，因為 CareerRole 結構已改變
        # 舊的 JobRole 結構與新的 CareerRole 不相容
        # 所有角色定義已移至統一知識庫 (career_knowledge_base.py)
        return []

    def _old_job_roles_data_reference(self):
        """
        舊的角色資料結構參考，已移至統一知識庫
        保留此註釋作為資料結構轉換的參考

        舊結構包含：
        - required_strengths, beneficial_strengths (現為 primary_strengths, secondary_strengths)
        - domain_weights (現已簡化)
        - min_education, typical_salary_range 等 (現為 salary_range)

        新的統一結構在 CareerKnowledgeBase 中定義
        """
        pass

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
            required_strengths=job_role.primary_strengths,
            reasons=reasons
        )

    def _calculate_strength_alignment(
        self,
        job_role: CareerRole,
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
        for required_strength in job_role.primary_strengths:
            strength_score = user_strengths.get(required_strength.lower(), 0)
            # Convert to 0-1 scale and apply as match factor
            alignment[f"required_{required_strength}"] = strength_score / 100
            required_alignment += strength_score / 100

        # Calculate alignment for beneficial strengths (lower weight)
        beneficial_alignment = 0
        for beneficial_strength in job_role.secondary_strengths:
            strength_score = user_strengths.get(beneficial_strength.lower(), 0)
            alignment[f"beneficial_{beneficial_strength}"] = strength_score / 100 * 0.5
            beneficial_alignment += strength_score / 100 * 0.5

        # Normalize by number of strengths considered
        total_required = len(job_role.primary_strengths)
        total_beneficial = len(job_role.secondary_strengths)

        if total_required > 0:
            alignment["required_average"] = required_alignment / total_required
        if total_beneficial > 0:
            alignment["beneficial_average"] = beneficial_alignment / total_beneficial

        return alignment

    def _calculate_domain_fit(
        self,
        job_role: CareerRole,
        strength_profile: StrengthProfile
    ) -> Dict[StrengthCategory, float]:
        """已廢棄：使用新的基於知識庫的方法"""
        # 重導向到新的方法
        return self._calculate_domain_fit_from_kb(job_role, strength_profile)

    def _calculate_context_bonus(
        self,
        job_role: CareerRole,
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
            salary_range = job_role.salary_range
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
        domain_fit: Dict[StrengthCategory, float]
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
        job_role: CareerRole,
        strength_profile: StrengthProfile
    ) -> Tuple[List[str], List[str]]:
        """Analyze which strengths match and which need development."""
        user_strength_names = [s.theme.name.lower() for s in strength_profile.top_5_strengths]

        matching_strengths = []
        development_needs = []

        # Check required strengths
        for required in job_role.primary_strengths:
            if required.lower() in user_strength_names:
                matching_strengths.append(required)
            else:
                development_needs.append(required)

        # Check beneficial strengths
        for beneficial in job_role.secondary_strengths:
            if beneficial.lower() in user_strength_names and beneficial not in matching_strengths:
                matching_strengths.append(beneficial)

        return matching_strengths, development_needs

    def _generate_match_reasons(
        self,
        job_role: CareerRole,
        strength_alignment: Dict[str, float],
        domain_fit: Dict[StrengthCategory, float],
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
                StrengthCategory.EXECUTING: "執行力",
                StrengthCategory.INFLUENCING: "影響力",
                StrengthCategory.RELATIONSHIP_BUILDING: "關係建立",
                StrengthCategory.STRATEGIC_THINKING: "戰略思維"
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