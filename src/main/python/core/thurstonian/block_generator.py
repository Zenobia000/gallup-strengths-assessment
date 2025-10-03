"""
Dynamic Block Generation Engine for Thurstonian IRT Assessment
基於平衡不完全區塊設計 (Balanced Incomplete Block Design) 的動態出題引擎
"""

import json
import random
import os
from typing import List, Dict, Any, Optional, Tuple
from itertools import combinations
import numpy as np
from pathlib import Path
from collections import defaultdict

# Domain mapping for balanced distribution
DOMAIN_MAPPING = {
    "EXECUTING": ["T1", "T2", "T12"],
    "INFLUENCING": ["T5", "T7", "T11"],
    "RELATIONSHIP_BUILDING": ["T6", "T9", "T10"],
    "STRATEGIC_THINKING": ["T3", "T4", "T8"]
}

# Flatten talent to domain mapping
TALENT_TO_DOMAIN = {}
for domain, talents in DOMAIN_MAPPING.items():
    for talent in talents:
        TALENT_TO_DOMAIN[talent] = domain

def load_statement_bank() -> Dict[str, Any]:
    """載入語句庫"""
    try:
        # Get project root directory
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent.parent.parent  # Navigate to project root
        statement_bank_path = project_root / "src" / "main" / "resources" / "assessment" / "statement_bank.json"

        if not statement_bank_path.exists():
            print(f"Statement bank not found at: {statement_bank_path}")
            return {}

        with open(statement_bank_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading statement bank: {e}")
        return {}

def flatten_statements_from_bank(statement_bank: Dict[str, Any]) -> List[Dict[str, Any]]:
    """將語句庫扁平化為 statement 列表"""
    statements = []

    if "statement_bank" not in statement_bank:
        print("No statement_bank key found")
        return statements

    for talent_key, talent_statements in statement_bank["statement_bank"].items():
        # Extract talent ID from key like "T1_結構化執行"
        talent_id = talent_key.split("_")[0]

        for stmt in talent_statements:
            statement = {
                "statement_id": stmt["id"],
                "text": stmt["text"],
                "dimension": talent_id,
                "domain": TALENT_TO_DOMAIN.get(talent_id, "UNKNOWN"),
                "complexity": stmt.get("complexity", "medium"),
                "behavioral_focus": stmt.get("behavioral_focus", "general")
            }
            statements.append(statement)

    return statements

def calculate_pairwise_occurrences(blocks: List[List[str]]) -> Dict[Tuple[str, str], int]:
    """計算才幹配對在同一區塊出現的次數"""
    pairwise_count = {}

    for block in blocks:
        # Get all pairs in this block
        for pair in combinations(block, 2):
            sorted_pair = tuple(sorted(pair))
            pairwise_count[sorted_pair] = pairwise_count.get(sorted_pair, 0) + 1

    return pairwise_count

def calculate_domain_distribution(blocks: List[List[str]]) -> Dict[str, int]:
    """計算領域分布統計"""
    domain_stats = {domain: 0 for domain in DOMAIN_MAPPING.keys()}

    for block in blocks:
        block_domains = set()
        for talent in block:
            domain = TALENT_TO_DOMAIN.get(talent, "UNKNOWN")
            if domain != "UNKNOWN":
                block_domains.add(domain)

        # Count domains that appear in this block
        for domain in block_domains:
            domain_stats[domain] += 1

    return domain_stats

def validate_block_quality(blocks: List[List[str]]) -> Dict[str, Any]:
    """驗證生成的區塊品質"""
    # Count talent frequencies
    talent_frequencies = {}
    for block in blocks:
        for talent in block:
            talent_frequencies[talent] = talent_frequencies.get(talent, 0) + 1

    # Calculate pairwise occurrences
    pairwise_occurrences = calculate_pairwise_occurrences(blocks)

    # Calculate domain distribution
    domain_distribution = calculate_domain_distribution(blocks)

    # Calculate statistics
    frequencies = list(talent_frequencies.values())
    freq_mean = np.mean(frequencies) if frequencies else 0
    freq_std = np.std(frequencies) if frequencies else 0

    pairwise_values = list(pairwise_occurrences.values())
    pairwise_mean = np.mean(pairwise_values) if pairwise_values else 0
    pairwise_std = np.std(pairwise_values) if pairwise_values else 0

    # Check domain diversity per block
    blocks_with_3plus_domains = 0
    for block in blocks:
        domains_in_block = set(TALENT_TO_DOMAIN.get(t, "UNKNOWN") for t in block)
        domains_in_block.discard("UNKNOWN")
        if len(domains_in_block) >= 3:
            blocks_with_3plus_domains += 1

    domain_diversity_rate = blocks_with_3plus_domains / len(blocks) if blocks else 0

    return {
        "total_blocks": len(blocks),
        "talent_frequency": {
            "mean": freq_mean,
            "std": freq_std,
            "min": min(frequencies) if frequencies else 0,
            "max": max(frequencies) if frequencies else 0,
            "distribution": talent_frequencies
        },
        "pairwise_occurrence": {
            "mean": pairwise_mean,
            "std": pairwise_std,
            "target": 2.73,
            "variance": pairwise_std ** 2
        },
        "domain_diversity": {
            "blocks_with_3plus_domains": blocks_with_3plus_domains,
            "domain_diversity_rate": domain_diversity_rate,
            "distribution": domain_distribution
        },
        "quality_score": min(1.0, (domain_diversity_rate + (1 - min(freq_std / 10, 1.0))) / 2)
    }

def generate_systematic_blocks(target_blocks: int = 30) -> List[List[str]]:
    """使用系統化輪轉規則生成區塊"""
    talents = [f"T{i}" for i in range(1, 13)]  # T1 to T12
    blocks = []

    # Systematic rotation pattern: (block_index + offset) mod 12
    offsets = [0, 3, 6, 9]  # Ensure good distribution across domains

    for block_idx in range(target_blocks):
        block_talents = []
        for offset in offsets:
            talent_idx = (block_idx + offset) % 12
            talent_id = talents[talent_idx]
            block_talents.append(talent_id)

        blocks.append(block_talents)

    return blocks

def select_statements_for_blocks(talent_blocks: List[List[str]], statements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """為才幹區塊選擇具體的語句"""
    # Group statements by dimension
    statements_by_dimension = {}
    for stmt in statements:
        dim = stmt["dimension"]
        if dim not in statements_by_dimension:
            statements_by_dimension[dim] = []
        statements_by_dimension[dim].append(stmt)

    # Track usage count for each statement
    statement_usage = {stmt["statement_id"]: 0 for stmt in statements}

    blocks = []

    for block_idx, talent_block in enumerate(talent_blocks):
        block_statements = []

        for talent in talent_block:
            # Get available statements for this talent
            available_statements = statements_by_dimension.get(talent, [])

            if not available_statements:
                print(f"No statements found for talent: {talent}")
                continue

            # Sort by usage count (prefer less used statements)
            available_statements.sort(key=lambda s: statement_usage[s["statement_id"]])

            # Select the least used statement
            selected_statement = available_statements[0]
            statement_usage[selected_statement["statement_id"]] += 1

            block_statements.append({
                "id": selected_statement["statement_id"],
                "text": selected_statement["text"],
                "dimension": selected_statement["dimension"],
                "domain": selected_statement["domain"],
                "complexity": selected_statement["complexity"]
            })

        if len(block_statements) == 4:  # Only add complete blocks
            blocks.append({
                "block_id": block_idx + 1,
                "statements": block_statements
            })

    return blocks

def generate_balanced_blocks(statements: List[Dict[str, Any]] = None, target_blocks: int = None) -> List[Dict[str, Any]]:
    """
    生成平衡的評測區塊

    Args:
        statements: Optional list of statements. If None, will load from statement bank.
        target_blocks: Number of blocks to generate (default: 30)

    Returns:
        List of blocks with statements
    """
    try:
        # Load statements if not provided from existing data
        if statements is None:
            statement_bank = load_statement_bank()
            statements = flatten_statements_from_bank(statement_bank)

        # If still no statements, try to use provided statements format
        if not statements and statements is not None:
            # Assume statements are already in correct format from file storage
            pass

        if not statements:
            print("No statements available for block generation")
            return generate_fallback_blocks()

        print(f"Loaded {len(statements)} statements for block generation")

        # Ensure target_blocks is set
        if target_blocks is None:
            target_blocks = 30

        # If statements are from file storage, use optimized approach
        if statements and len(statements) > 0 and 'statement_id' in statements[0]:
            return generate_optimized_blocks_from_statements(statements, target_blocks)

        # Otherwise use systematic approach
        statement_bank = load_statement_bank()
        if statement_bank:
            flat_statements = flatten_statements_from_bank(statement_bank)
            talent_blocks = generate_systematic_blocks(target_blocks)
            quality_metrics = validate_block_quality(talent_blocks)
            print(f"Block quality metrics: {quality_metrics}")
            final_blocks = select_statements_for_blocks(talent_blocks, flat_statements)
            print(f"Generated {len(final_blocks)} complete blocks")
            return final_blocks

        return generate_fallback_blocks()

    except Exception as e:
        print(f"Error generating blocks: {e}")
        return generate_fallback_blocks()

def generate_optimized_blocks_from_statements(statements: List[Dict[str, Any]], target_blocks: int) -> List[Dict[str, Any]]:
    """從現有 statements 生成優化的區塊（相容原有文件存儲格式）

    遵循 talent-domain-mapping.md 的要求：
    - 總題數 b=30，每題選項 k=4
    - 12個才幹，每個才幹總出現次數 r=10
    """

    # Group statements by dimension
    dimension_statements = defaultdict(list)
    for stmt in statements:
        dimension = stmt.get('dimension', 'unknown')
        dimension_statements[dimension].append(stmt)

    dimensions = list(dimension_statements.keys())
    print(f"維度數量: {len(dimensions)}")

    # Calculate minimum blocks needed
    dimension_counts = {dim: len(stmts) for dim, stmts in dimension_statements.items()}
    print(f"各維度 statement 數量: {dimension_counts}")

    # Force target_blocks to 30 for compliance with design
    target_blocks = 30
    target_occurrences_per_dimension = 10  # Each talent should appear 10 times

    blocks = []
    dimension_usage_count = {dim: 0 for dim in dimensions}

    # Use systematic rotation as specified in talent-domain-mapping.md
    # Rotation pattern: (block_index + offset) mod 12, offsets = [0, 3, 6, 9]
    offsets = [0, 3, 6, 9]

    for block_id in range(target_blocks):
        block_statements = []
        block_dimensions = []

        # Generate talent sequence for this block using rotation
        for offset in offsets:
            talent_idx = (block_id + offset) % 12
            if talent_idx < len(dimensions):
                selected_dimension = dimensions[talent_idx]
                block_dimensions.append(selected_dimension)

        # Select statements for each dimension in the block
        for dim in block_dimensions:
            if dim in dimension_statements and dimension_statements[dim]:
                # Select statement with lowest usage count to balance usage
                available_statements = dimension_statements[dim]

                # If we have enough statements, pick the least used one
                if len(available_statements) > 1:
                    # Cycle through statements to ensure even usage
                    usage_index = dimension_usage_count[dim] % len(available_statements)
                    selected = available_statements[usage_index]
                else:
                    selected = available_statements[0]

                block_statements.append(selected)
                dimension_usage_count[dim] += 1

        # Only add complete blocks (must have 4 statements)
        if len(block_statements) == 4:
            blocks.append({
                "block_id": block_id,
                "statement_ids": [stmt['statement_id'] for stmt in block_statements],
                "statements": block_statements,
                "dimensions": [stmt['dimension'] for stmt in block_statements]
            })

    # Validation and reporting
    covered_dimensions = set()
    dimension_occurrence_count = defaultdict(int)

    for block in blocks:
        covered_dimensions.update(block['dimensions'])
        for dim in block['dimensions']:
            dimension_occurrence_count[dim] += 1

    print(f"維度覆蓋報告:")
    print(f"  總題組數: {len(blocks)}")
    print(f"  覆蓋維度: {len(covered_dimensions)}/{len(dimensions)}")
    print(f"  各維度出現次數: {dict(dimension_occurrence_count)}")
    print(f"  目標出現次數: {target_occurrences_per_dimension}")

    # Check if we meet the target occurrence count
    occurrence_compliance = all(
        dimension_occurrence_count[dim] >= target_occurrences_per_dimension
        for dim in dimensions
    )

    print(f"✅ 最終題組數: {len(blocks)}")
    print(f"✅ 維度覆蓋完整性: {len(covered_dimensions) == len(dimensions)}")
    print(f"✅ 出現次數達標: {occurrence_compliance}")

    return blocks

def generate_fallback_blocks() -> List[Dict[str, Any]]:
    """生成簡單的回退區塊（用於測試）"""
    fallback_statements = [
        {"statement_id": "S_T1_01", "text": "我會把大型目標拆成週任務", "dimension": "T1", "domain": "EXECUTING"},
        {"statement_id": "S_T4_01", "text": "我先界定問題與指標", "dimension": "T4", "domain": "STRATEGIC_THINKING"},
        {"statement_id": "S_T7_01", "text": "我以客戶語言定義價值", "dimension": "T7", "domain": "INFLUENCING"},
        {"statement_id": "S_T10_01", "text": "我在壓力下保持冷靜", "dimension": "T10", "domain": "RELATIONSHIP_BUILDING"},
    ]

    return [{
        "block_id": 1,
        "statement_ids": [stmt['statement_id'] for stmt in fallback_statements],
        "statements": fallback_statements,
        "dimensions": [stmt['dimension'] for stmt in fallback_statements]
    }]

# Export main function for external use
__all__ = ["generate_balanced_blocks", "generate_fallback_blocks", "validate_block_quality"]