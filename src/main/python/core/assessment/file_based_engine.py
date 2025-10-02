"""
File-based Assessment Engine
基於文件存儲的評測引擎，整合評測基準、出題規則和才幹映射系統

Author: Claude Code AI
Date: 2025-10-02
Version: 1.0
"""

import json
import random
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class TalentScore:
    """才幹分數"""
    talent_id: str
    talent_name: str
    raw_score: float
    percentile: int
    domain: str


@dataclass
class DomainScore:
    """領域分數"""
    domain_id: str
    domain_name: str
    percentile: int
    talents: List[TalentScore]


@dataclass
class BalanceMetrics:
    """均衡指標"""
    dbi: float
    relative_entropy: float
    gini_coefficient: float
    profile_type: str


@dataclass
class ArchetypeClassification:
    """原型分類結果"""
    primary_archetype: Dict[str, Any]
    secondary_archetype: Dict[str, Any]
    archetype_scores: Dict[str, float]
    classification_details: Dict[str, Any]
    career_recommendations: Dict[str, List[str]]


@dataclass
class AssessmentResult:
    """評測結果"""
    session_id: str
    timestamp: datetime
    talent_scores: List[TalentScore]
    domain_scores: List[DomainScore]
    balance_metrics: BalanceMetrics
    archetype_classification: ArchetypeClassification
    confidence: float
    metadata: Dict[str, Any]


class FileBasedAssessmentEngine:
    """基於文件的評測引擎"""

    def __init__(self, resources_path: str = "src/main/resources/assessment"):
        """
        初始化評測引擎

        Args:
            resources_path: 資源文件路徑
        """
        self.resources_path = Path(resources_path)
        self.methodology = self._load_methodology()
        self.statement_bank = self._load_statement_bank()
        self.generation_rules = self._load_generation_rules()
        self.mapping_rules = self._load_mapping_rules()

        # 才幹定義
        self.talent_definitions = self.statement_bank["talent_definitions"]
        self.domain_mapping = self._build_domain_mapping()

    def _load_methodology(self) -> Dict:
        """載入評測基準方法論"""
        with open(self.resources_path / "assessment_benchmark_methodology.json", 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_statement_bank(self) -> Dict:
        """載入語句庫"""
        with open(self.resources_path / "statement_bank.json", 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_generation_rules(self) -> Dict:
        """載入出題規則"""
        with open(self.resources_path / "block_generation_rules.json", 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_mapping_rules(self) -> Dict:
        """載入才幹映射規則"""
        with open(self.resources_path / "talent_mapping_rules.json", 'r', encoding='utf-8') as f:
            return json.load(f)

    def _build_domain_mapping(self) -> Dict[str, str]:
        """建立才幹到領域的映射"""
        mapping = {}
        for talent_id, talent_info in self.talent_definitions.items():
            mapping[talent_id] = talent_info["domain"]
        return mapping

    def generate_questionnaire(self, method: str = "systematic_rotation",
                             random_seed: Optional[int] = None) -> Dict[str, Any]:
        """
        生成問卷

        Args:
            method: 生成方法 (systematic_rotation, ilp, heuristic)
            random_seed: 隨機種子

        Returns:
            問卷配置
        """
        if random_seed:
            random.seed(random_seed)

        if method == "systematic_rotation":
            return self._generate_systematic_questionnaire()
        elif method == "heuristic":
            return self._generate_heuristic_questionnaire()
        else:
            raise ValueError(f"不支持的生成方法: {method}")

    def _generate_systematic_questionnaire(self) -> Dict[str, Any]:
        """系統化輪轉生成問卷"""
        blocks = []
        total_blocks = 30
        offsets = [0, 3, 6, 9]

        # 為每個才幹準備語句
        talent_statements = {}
        for talent_id in range(1, 13):
            talent_key = f"T{talent_id}"
            talent_statements[talent_key] = list(range(1, 11))  # 每個才幹10個語句

        for block_idx in range(total_blocks):
            block_talents = []
            block_statements = []

            for offset in offsets:
                talent_idx = (block_idx + offset) % 12 + 1
                talent_id = f"T{talent_idx}"

                # 獲取下一個可用語句
                if talent_statements[talent_id]:
                    statement_idx = talent_statements[talent_id].pop(0)
                    statement_id = f"S_{talent_id}_{statement_idx:02d}"

                    # 從語句庫獲取語句信息
                    talent_name = self.talent_definitions[talent_id]["name"]
                    domain = self.talent_definitions[talent_id]["domain"]

                    # 查找語句內容
                    statement_text = self._find_statement_text(talent_id, statement_id)

                    block_talents.append(talent_id)
                    block_statements.append({
                        "statement_id": statement_id,
                        "talent": talent_id,
                        "talent_name": talent_name,
                        "domain": domain,
                        "text": statement_text
                    })

            # 驗證區塊
            validation = self._validate_block(block_statements)

            blocks.append({
                "block_id": f"Q{block_idx + 1:02d}",
                "statements": block_statements,
                "validation": validation
            })

        return {
            "questionnaire_id": f"systematic_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generation_method": "systematic_rotation",
            "generation_timestamp": datetime.now().isoformat(),
            "total_blocks": total_blocks,
            "blocks": blocks,
            "summary_statistics": self._calculate_summary_statistics(blocks)
        }

    def _generate_heuristic_questionnaire(self) -> Dict[str, Any]:
        """啟發式生成問卷"""
        # 簡化的啟發式方法：隨機但保持平衡
        blocks = []
        total_blocks = 30

        # 才幹使用計數
        talent_usage = {f"T{i}": 0 for i in range(1, 13)}
        target_usage = 10  # 每個才幹出現10次

        for block_idx in range(total_blocks):
            # 選擇最需要的才幹
            available_talents = [t for t, count in talent_usage.items()
                               if count < target_usage]

            if len(available_talents) < 4:
                # 補充才幹
                all_talents = [f"T{i}" for i in range(1, 13)]
                available_talents.extend(all_talents)

            # 隨機選擇4個才幹，但確保領域多樣性
            selected_talents = self._select_diverse_talents(available_talents[:12])

            block_statements = []
            for talent_id in selected_talents:
                statement_idx = (talent_usage[talent_id] % 10) + 1
                statement_id = f"S_{talent_id}_{statement_idx:02d}"

                talent_name = self.talent_definitions[talent_id]["name"]
                domain = self.talent_definitions[talent_id]["domain"]
                statement_text = self._find_statement_text(talent_id, statement_id)

                block_statements.append({
                    "statement_id": statement_id,
                    "talent": talent_id,
                    "talent_name": talent_name,
                    "domain": domain,
                    "text": statement_text
                })

                talent_usage[talent_id] += 1

            validation = self._validate_block(block_statements)

            blocks.append({
                "block_id": f"Q{block_idx + 1:02d}",
                "statements": block_statements,
                "validation": validation
            })

        return {
            "questionnaire_id": f"heuristic_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generation_method": "heuristic_search",
            "generation_timestamp": datetime.now().isoformat(),
            "total_blocks": total_blocks,
            "blocks": blocks,
            "summary_statistics": self._calculate_summary_statistics(blocks)
        }

    def _select_diverse_talents(self, available_talents: List[str]) -> List[str]:
        """選擇領域多樣化的才幹組合"""
        domain_groups = {
            "EXECUTING": ["T1", "T2", "T12"],
            "INFLUENCING": ["T5", "T7", "T11"],
            "RELATIONSHIP_BUILDING": ["T6", "T9", "T10"],
            "STRATEGIC_THINKING": ["T3", "T4", "T8"]
        }

        selected = []
        used_domains = set()

        # 優先從不同領域選擇
        for domain, talents in domain_groups.items():
            if len(selected) >= 4:
                break
            available_in_domain = [t for t in talents if t in available_talents and domain not in used_domains]
            if available_in_domain:
                selected.append(random.choice(available_in_domain))
                used_domains.add(domain)

        # 如果不足4個，隨機補充
        while len(selected) < 4:
            remaining = [t for t in available_talents if t not in selected]
            if remaining:
                selected.append(random.choice(remaining))
            else:
                break

        return selected[:4]

    def _find_statement_text(self, talent_id: str, statement_id: str) -> str:
        """查找語句內容"""
        talent_name = self.talent_definitions[talent_id]["name"]
        talent_key = f"{talent_id}_{talent_name}"

        if talent_key in self.statement_bank["statement_bank"]:
            statements = self.statement_bank["statement_bank"][talent_key]
            for stmt in statements:
                if stmt["id"] == statement_id:
                    return stmt["text"]

        return f"語句 {statement_id} 未找到"

    def _validate_block(self, statements: List[Dict]) -> Dict[str, Any]:
        """驗證區塊"""
        domains = set(stmt["domain"] for stmt in statements)
        talents = set(stmt["talent"] for stmt in statements)

        return {
            "domain_count": len(domains),
            "talent_uniqueness": len(talents) == len(statements),
            "domain_diversity_met": len(domains) >= 3,
            "domains": list(domains)
        }

    def _calculate_summary_statistics(self, blocks: List[Dict]) -> Dict[str, Any]:
        """計算摘要統計"""
        talent_frequency = {}
        domain_frequency = {}

        for block in blocks:
            for stmt in block["statements"]:
                talent = stmt["talent"]
                domain = stmt["domain"]

                talent_frequency[talent] = talent_frequency.get(talent, 0) + 1
                domain_frequency[domain] = domain_frequency.get(domain, 0) + 1

        return {
            "talent_frequency": talent_frequency,
            "domain_frequency": domain_frequency,
            "total_statements": sum(talent_frequency.values()),
            "balance_score": self._calculate_balance_score(talent_frequency)
        }

    def _calculate_balance_score(self, frequency: Dict[str, int]) -> float:
        """計算平衡分數"""
        if not frequency:
            return 0.0

        values = list(frequency.values())
        target = 10  # 每個才幹目標出現次數
        variance = np.var(values)
        max_variance = target ** 2  # 最大可能變異數

        return max(0, 1 - variance / max_variance)

    def calculate_scores(self, responses: List[Dict[str, Any]]) -> AssessmentResult:
        """
        計算評測分數

        Args:
            responses: 用戶回應 [{"block_id": "Q01", "most_like": "S_T1_01", "least_like": "S_T3_01"}]

        Returns:
            評測結果
        """
        # 簡化的計分邏輯（實際應使用 Thurstonian IRT）
        talent_counts = {f"T{i}": {"most": 0, "least": 0} for i in range(1, 13)}

        # 統計選擇
        for response in responses:
            most_like = response.get("most_like", "")
            least_like = response.get("least_like", "")

            # 提取才幹ID
            if most_like.startswith("S_"):
                talent_id = most_like.split("_")[1]
                if talent_id in talent_counts:
                    talent_counts[talent_id]["most"] += 1

            if least_like.startswith("S_"):
                talent_id = least_like.split("_")[1]
                if talent_id in talent_counts:
                    talent_counts[talent_id]["least"] += 1

        # 計算才幹分數
        talent_scores = []
        for talent_id, counts in talent_counts.items():
            raw_score = counts["most"] - counts["least"]  # 簡化計分
            percentile = max(0, min(100, 50 + raw_score * 10))  # 簡化百分位

            talent_info = self.talent_definitions[talent_id]
            talent_scores.append(TalentScore(
                talent_id=talent_id,
                talent_name=talent_info["name"],
                raw_score=raw_score,
                percentile=int(percentile),
                domain=talent_info["domain"]
            ))

        # 計算領域分數
        domain_scores = self._calculate_domain_scores(talent_scores)

        # 計算均衡指標
        balance_metrics = self._calculate_balance_metrics(domain_scores)

        # 分類原型
        archetype_classification = self._classify_archetype(talent_scores, domain_scores, balance_metrics)

        # 計算信心度
        confidence = self._calculate_confidence(talent_scores, archetype_classification)

        return AssessmentResult(
            session_id=f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            talent_scores=talent_scores,
            domain_scores=domain_scores,
            balance_metrics=balance_metrics,
            archetype_classification=archetype_classification,
            confidence=confidence,
            metadata={
                "methodology_version": self.methodology["methodology_metadata"]["version"],
                "total_responses": len(responses),
                "calculation_method": "simplified_scoring"
            }
        )

    def _calculate_domain_scores(self, talent_scores: List[TalentScore]) -> List[DomainScore]:
        """計算領域分數"""
        domain_groups = {
            "EXECUTING": [],
            "INFLUENCING": [],
            "RELATIONSHIP_BUILDING": [],
            "STRATEGIC_THINKING": []
        }

        # 分組才幹
        for talent in talent_scores:
            domain_groups[talent.domain].append(talent)

        domain_scores = []
        for domain_id, talents in domain_groups.items():
            if talents:
                avg_percentile = sum(t.percentile for t in talents) / len(talents)
                domain_name = domain_id.replace("_", " ").title()

                domain_scores.append(DomainScore(
                    domain_id=domain_id,
                    domain_name=domain_name,
                    percentile=int(avg_percentile),
                    talents=talents
                ))

        return domain_scores

    def _calculate_balance_metrics(self, domain_scores: List[DomainScore]) -> BalanceMetrics:
        """計算均衡指標"""
        if not domain_scores:
            return BalanceMetrics(dbi=0, relative_entropy=0, gini_coefficient=0, profile_type="unknown")

        percentiles = [ds.percentile for ds in domain_scores]
        p = np.array(percentiles) / 100.0

        # DBI (Domain Balance Index)
        var_max = np.var([1, 0, 0, 0])
        dbi = 1 - (np.var(p) / var_max) if var_max > 0 else 1.0

        # 相對熵
        p_norm = p / p.sum() if p.sum() > 0 else np.full(p.shape, 1/len(p))
        entropy = -np.sum(p_norm * np.log(p_norm + 1e-9))
        rel_entropy = entropy / np.log(len(p))

        # Gini 係數
        num = np.sum(np.abs(p[:, None] - p[None, :]))
        den = 2 * len(p) * np.sum(p)
        gini = num / den if den > 0 else 0.0

        # 確定檔案類型
        if dbi > 0.70 and rel_entropy > 0.70:
            profile_type = "balanced"
        elif dbi < 0.50 and rel_entropy < 0.50:
            profile_type = "specialized"
        else:
            profile_type = "complementary"

        return BalanceMetrics(
            dbi=dbi,
            relative_entropy=rel_entropy,
            gini_coefficient=gini,
            profile_type=profile_type
        )

    def _classify_archetype(self, talent_scores: List[TalentScore],
                          domain_scores: List[DomainScore],
                          balance_metrics: BalanceMetrics) -> ArchetypeClassification:
        """分類職業原型"""
        # 獲取前4名才幹
        top_talents = sorted(talent_scores, key=lambda x: x.percentile, reverse=True)[:4]

        archetype_scores = {}
        archetype_definitions = self.mapping_rules["archetype_definitions"]

        # 計算每個原型分數
        for archetype_id, archetype_info in archetype_definitions.items():
            score = self._calculate_archetype_score(
                top_talents, domain_scores, archetype_info, balance_metrics
            )
            archetype_scores[archetype_id] = score

        # 找出主要和次要原型
        sorted_archetypes = sorted(archetype_scores.items(), key=lambda x: x[1], reverse=True)
        primary_id, primary_score = sorted_archetypes[0]
        secondary_id, secondary_score = sorted_archetypes[1]

        primary_archetype = {
            "archetype_id": primary_id,
            "archetype_name": archetype_definitions[primary_id]["name"],
            "probability": primary_score,
            "confidence": "high" if primary_score > 0.80 else "medium" if primary_score > 0.60 else "low",
            "key_supporting_talents": [t.talent_id for t in top_talents[:3]]
        }

        secondary_archetype = {
            "archetype_id": secondary_id,
            "archetype_name": archetype_definitions[secondary_id]["name"],
            "probability": secondary_score
        }

        return ArchetypeClassification(
            primary_archetype=primary_archetype,
            secondary_archetype=secondary_archetype,
            archetype_scores=archetype_scores,
            classification_details={
                "top_talents": [{"talent": t.talent_id, "percentile": t.percentile} for t in top_talents],
                "balance_profile": balance_metrics.profile_type
            },
            career_recommendations={
                "primary_suggestions": archetype_definitions[primary_id]["career_suggestions"][:4],
                "alternative_paths": archetype_definitions[secondary_id]["career_suggestions"][:3]
            }
        )

    def _calculate_archetype_score(self, top_talents: List[TalentScore],
                                 domain_scores: List[DomainScore],
                                 archetype_info: Dict,
                                 balance_metrics: BalanceMetrics) -> float:
        """計算原型匹配分數"""
        score = 0.0

        # 才幹匹配分數
        primary_talents = archetype_info.get("primary_talents", [])
        secondary_talents = archetype_info.get("secondary_talents", [])

        for i, talent in enumerate(top_talents):
            weight = 0.4 if i == 0 else 0.3 if i == 1 else 0.2 if i == 2 else 0.1

            if talent.talent_id in primary_talents:
                score += weight * 1.0
            elif talent.talent_id in secondary_talents:
                score += weight * 0.7

        # 領域偏好分數
        domain_preference = archetype_info.get("domain_preference", "")
        for domain_score in domain_scores:
            if domain_score.domain_id in domain_preference:
                score += domain_score.percentile / 100.0 * 0.3

        # 均衡度調整
        balance_modifier = self.mapping_rules["mapping_rules"]["balance_profile_modifiers"]
        if balance_metrics.profile_type in balance_modifier:
            modifier = balance_modifier[balance_metrics.profile_type]["modifier"]
            score *= modifier

        return min(1.0, max(0.0, score))

    def _calculate_confidence(self, talent_scores: List[TalentScore],
                            archetype_classification: ArchetypeClassification) -> float:
        """計算整體信心度"""
        # 基於才幹分數的清晰度
        top_talents = sorted(talent_scores, key=lambda x: x.percentile, reverse=True)[:4]
        talent_clarity = np.std([t.percentile for t in top_talents]) / 100.0

        # 基於原型分類的確定性
        primary_prob = archetype_classification.primary_archetype["probability"]
        secondary_prob = archetype_classification.secondary_archetype["probability"]
        archetype_clarity = primary_prob - secondary_prob

        # 綜合信心度
        confidence = (talent_clarity + archetype_clarity) / 2
        return min(1.0, max(0.0, confidence))

    def export_result(self, result: AssessmentResult, format: str = "json") -> str:
        """匯出結果"""
        if format == "json":
            return json.dumps(asdict(result), default=str, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"不支持的匯出格式: {format}")

    def get_benchmark_criteria(self) -> Dict[str, Any]:
        """獲取評測基準"""
        return self.methodology["quality_benchmarks"]

    def validate_responses(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """驗證回應資料"""
        issues = []

        # 檢查回應數量
        expected_blocks = 30
        if len(responses) != expected_blocks:
            issues.append(f"回應數量不正確，期望 {expected_blocks}，實際 {len(responses)}")

        # 檢查回應格式
        for i, response in enumerate(responses):
            if "most_like" not in response or "least_like" not in response:
                issues.append(f"區塊 {i+1} 缺少必要欄位")

            if response.get("most_like") == response.get("least_like"):
                issues.append(f"區塊 {i+1} 最喜歡和最不喜歡不能相同")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "total_responses": len(responses)
        }


# 使用示例
if __name__ == "__main__":
    # 初始化引擎
    engine = FileBasedAssessmentEngine()

    # 生成問卷
    questionnaire = engine.generate_questionnaire(method="systematic_rotation")
    print("生成問卷成功，包含", len(questionnaire["blocks"]), "個區塊")

    # 模擬回應
    mock_responses = []
    for block in questionnaire["blocks"][:5]:  # 只測試前5個區塊
        statements = block["statements"]
        mock_responses.append({
            "block_id": block["block_id"],
            "most_like": statements[0]["statement_id"],
            "least_like": statements[-1]["statement_id"]
        })

    # 計算分數
    if mock_responses:
        result = engine.calculate_scores(mock_responses)
        print(f"評測完成，主要原型：{result.archetype_classification.primary_archetype['archetype_name']}")
        print(f"信心度：{result.confidence:.2f}")