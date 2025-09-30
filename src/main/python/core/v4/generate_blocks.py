"""
生成四選二平衡區塊
使用語句池和 BlockDesigner 創建測驗區塊
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from typing import List
import json
from pathlib import Path
import numpy as np

from data.v4_statements import get_all_statements, get_pool_statistics, STATEMENT_POOL
from models.v4.forced_choice import Statement, QuartetBlock
from core.v4.block_designer import QuartetBlockDesigner, BlockDesignCriteria


def convert_to_statement_objects() -> List[Statement]:
    """將語句資料轉換為 Statement 物件"""
    statements = []
    for dimension, dimension_statements in STATEMENT_POOL.items():
        for stmt_dict in dimension_statements:
            statements.append(Statement(
                statement_id=stmt_dict["statement_id"],
                text=stmt_dict["text"],
                dimension=dimension,
                factor_loading=stmt_dict["factor_loading"],
                social_desirability=stmt_dict["social_desirability"]
            ))
    return statements


def generate_balanced_blocks(n_blocks: int = 30, method: str = 'balanced') -> List[QuartetBlock]:
    """
    生成平衡的四選二區塊

    Args:
        n_blocks: 區塊數量
        method: 設計方法 ('balanced', 'random', 'optimal')

    Returns:
        List of QuartetBlock objects
    """
    # 獲取語句
    statements = convert_to_statement_objects()
    print(f"\n📊 語句池統計:")
    stats = get_pool_statistics()
    print(f"  - 總語句數: {stats['total_statements']}")
    print(f"  - 維度數: {stats['dimensions']}")
    print(f"  - 社會期望性: {stats['social_desirability']['mean']:.2f} "
          f"(範圍: {stats['social_desirability']['min']:.1f}-{stats['social_desirability']['max']:.1f})")
    print(f"  - 情境分布: {stats['context_distribution']}")

    # 創建區塊設計器
    designer = QuartetBlockDesigner(
        statements=statements,
        n_blocks=n_blocks,
        random_seed=42
    )

    # 生成區塊
    print(f"\n🔨 生成 {n_blocks} 個四選二區塊 (方法: {method})...")
    blocks = designer.create_blocks(method=method)

    # 驗證設計
    print("\n✅ 驗證區塊設計品質...")
    validation = designer.validate_blocks(blocks)

    print(f"\n📈 設計品質指標:")
    print(f"  - 維度平衡性: {validation['dimension_balance']:.3f} (越小越好)")
    print(f"  - 配對平衡性: {validation['pair_balance']:.3f} (越小越好)")
    print(f"  - 社會期望性變異: {validation['mean_sd_variance']:.3f} (越小越好)")
    print(f"  - 設計有效: {'✅' if validation['is_valid'] else '❌'}")

    if validation['violations']:
        print(f"\n⚠️ 設計違規:")
        for violation in validation['violations'][:5]:
            print(f"  - {violation}")

    return blocks


def analyze_blocks(blocks: List[QuartetBlock]):
    """分析區塊特性"""
    print("\n📊 區塊分析:")

    # 維度覆蓋統計
    dimension_counts = {}
    pair_counts = {}
    sd_values = []

    for block in blocks:
        # 統計維度出現次數
        for stmt in block.statements:
            dimension_counts[stmt.dimension] = dimension_counts.get(stmt.dimension, 0) + 1

        # 統計維度配對
        dims = sorted(set(stmt.dimension for stmt in block.statements))
        for i in range(len(dims)):
            for j in range(i+1, len(dims)):
                pair = (dims[i], dims[j])
                pair_counts[pair] = pair_counts.get(pair, 0) + 1

        # 計算社會期望性
        sd_mean = np.mean([stmt.social_desirability for stmt in block.statements])
        sd_values.append(sd_mean)

    # 輸出統計
    print(f"\n維度出現頻率:")
    for dim, count in sorted(dimension_counts.items(), key=lambda x: x[1], reverse=True):
        expected = len(blocks) * 4 / 12  # 期望頻率
        deviation = ((count - expected) / expected) * 100
        print(f"  - {dim:15} {count:3}次 (偏差: {deviation:+.1f}%)")

    print(f"\n社會期望性分布:")
    print(f"  - 平均值: {np.mean(sd_values):.2f}")
    print(f"  - 標準差: {np.std(sd_values):.2f}")
    print(f"  - 範圍: {np.min(sd_values):.2f} - {np.max(sd_values):.2f}")

    # 顯示範例區塊
    print(f"\n📝 範例區塊 (前3個):")
    for i, block in enumerate(blocks[:3]):
        print(f"\n區塊 {i+1} (ID: {block.block_id}):")
        for j, stmt in enumerate(block.statements):
            print(f"  {j+1}. [{stmt.dimension:12}] {stmt.text[:30]}... (SD={stmt.social_desirability:.1f})")


def export_blocks_to_json(blocks: List[QuartetBlock], output_path: str = None):
    """將區塊匯出為 JSON 格式"""
    if output_path is None:
        output_path = "data/v4_assessment_blocks.json"

    export_data = {
        "version": "4.0-prototype",
        "n_blocks": len(blocks),
        "n_dimensions": 12,
        "blocks": []
    }

    for block in blocks:
        block_data = {
            "block_id": block.block_id,
            "dimensions": block.dimensions,
            "statements": []
        }

        for stmt in block.statements:
            block_data["statements"].append({
                "statement_id": stmt.statement_id,
                "text": stmt.text,
                "dimension": stmt.dimension,
                "factor_loading": stmt.factor_loading,
                "social_desirability": stmt.social_desirability
            })

        export_data["blocks"].append(block_data)

    # 創建輸出目錄
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 寫入檔案
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 區塊已匯出至: {output_file}")
    return output_file


def main():
    """主程式"""
    print("=" * 60)
    print("V4.0 四選二區塊生成器")
    print("=" * 60)

    # 生成平衡區塊
    blocks = generate_balanced_blocks(n_blocks=30, method='balanced')

    # 分析區塊
    analyze_blocks(blocks)

    # 匯出區塊
    output_file = export_blocks_to_json(blocks)

    print("\n" + "=" * 60)
    print("✅ 區塊生成完成!")
    print(f"   - 生成 {len(blocks)} 個區塊")
    print(f"   - 每區塊 4 個語句")
    print(f"   - 總計 {len(blocks) * 4} 個語句位置")
    print(f"   - 檔案: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()