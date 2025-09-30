"""
Career Matcher - Job Role Matching Based on Strengths

This module provides intelligent career matching by analyzing strength profiles
and matching them with suitable job roles and career paths. The matching
algorithm considers both strength alignment and industry context.

Design Philosophy:
Following Linus Torvalds' principle of "good taste" - clear matching logic
without overengineering, transparent scoring, and practical job recommendations.

Key Features:
- Comprehensive job role database
- Strength-based matching algorithm
- Industry sector categorization
- Experience level consideration
- Cultural and market context awareness
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

from .strength_mapper import StrengthProfile, StrengthScore, StrengthDomain


class ExperienceLevel(Enum):
    """Experience levels for job matching."""
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    EXECUTIVE = "executive"


class IndustrySector(Enum):
    """Industry sectors for job categorization."""
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


@dataclass
class JobRole:
    """Definition of a job role with strength requirements."""
    role_id: str
    role_name: str
    chinese_name: str
    industry_sector: IndustrySector
    experience_levels: List[ExperienceLevel]
    description: str
    required_strengths: List[str]  # Primary strength themes needed
    beneficial_strengths: List[str]  # Secondary strengths that help
    domain_weights: Dict[StrengthDomain, float]  # Weight for each domain
    min_education: str
    typical_salary_range: str
    growth_potential: str
    work_environment: str
    key_responsibilities: List[str]

    def __str__(self) -> str:
        return f"{self.chinese_name} ({self.role_name}) - {self.industry_sector.value}"


@dataclass
class CareerMatch:
    """A career match result with scoring details."""
    job_role: JobRole
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
    Intelligent career matching based on strength profiles.

    This class analyzes strength profiles and matches them against a database
    of job roles, providing scored recommendations with explanations.
    """

    def __init__(self):
        """Initialize the career matcher with job role database."""
        self.job_roles = self._load_job_roles()

    def _load_job_roles(self) -> List[JobRole]:
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
        Find career matches based on strength profile and user context.

        Args:
            strength_profile: Complete strength profile from StrengthMapper
            user_context: User preferences and context (experience, industry, etc.)

        Returns:
            List of CareerMatch objects sorted by match score (highest first)
        """
        if user_context is None:
            user_context = {}

        matches = []

        for job_role in self.job_roles:
            match = self._calculate_job_match(job_role, strength_profile, user_context)
            matches.append(match)

        # Sort by match score (highest first)
        return sorted(matches, key=lambda x: x.match_score, reverse=True)

    def _calculate_job_match(
        self,
        job_role: JobRole,
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


def get_career_matcher() -> CareerMatcher:
    """Get a configured CareerMatcher instance."""
    return CareerMatcher()