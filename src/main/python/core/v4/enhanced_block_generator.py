"""
改進版題組生成器
基於心理測量學原理，創建具有真實競爭性的強制選擇題組
"""

import json
import random
import math
from typing import List, Dict, Tuple, Any
from pathlib import Path
import logging
from utils.path_utils import get_file_storage_dir  # Cross-platform paths

logger = logging.getLogger(__name__)

class EnhancedBlockGenerator:
    """改進版題組生成器，優化強制選擇的競爭性"""

    def __init__(self, statements_path: str = None):
        """
        初始化題組生成器

        Args:
            statements_path: 語句庫路徑
        """
        self.statements = []
        self.dimensions = [f"T{i}" for i in range(1, 13)]

        if statements_path:
            self.load_statements(statements_path)
        else:
            # 嘗試載入改進版語句庫
            try:
                enhanced_path = str(get_file_storage_dir() / "v4_statements_enhanced_full.json")
                self.load_statements(enhanced_path)
                logger.info("已載入改進版語句庫")
            except:
                # 回退到原始語句庫
                fallback_path = str(get_file_storage_dir() / "v4_statements.json")
                self.load_statements(fallback_path)
                logger.info("已載入原始語句庫")

    def load_statements(self, path: str):
        """載入語句庫"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.statements = json.load(f)
            logger.info(f"載入 {len(self.statements)} 條語句")
        except Exception as e:
            logger.error(f"載入語句庫失敗: {e}")
            self.statements = []

    def calculate_social_desirability_balance(self, statements: List[Dict]) -> float:
        """
        計算語句組的社會期許平衡度

        Returns:
            平衡度分數：0-1，越接近1越平衡
        """
        if len(statements) < 2:
            return 0.0

        sd_values = [stmt.get('social_desirability', 4.0) for stmt in statements]

        # 計算標準差
        mean_sd = sum(sd_values) / len(sd_values)
        variance = sum((x - mean_sd) ** 2 for x in sd_values) / len(sd_values)
        std_dev = math.sqrt(variance)

        # 理想的標準差範圍是 0.8-1.2
        # 標準差太小表示語句過於相似，太大表示差異過大
        ideal_std = 1.0
        balance_score = 1.0 - abs(std_dev - ideal_std) / ideal_std

        return max(0.0, min(1.0, balance_score))

    def calculate_dimension_diversity(self, statements: List[Dict]) -> float:
        """
        計算維度多樣性

        Returns:
            多樣性分數：0-1，越接近1越多樣
        """
        dimensions = [stmt.get('dimension', '') for stmt in statements]
        unique_dims = len(set(dimensions))

        # 4語句題組理想情況是4個不同維度
        max_diversity = min(4, len(statements))
        diversity_score = unique_dims / max_diversity if max_diversity > 0 else 0.0

        return diversity_score

    def calculate_context_balance(self, statements: List[Dict]) -> float:
        """
        計算情境平衡度

        Returns:
            平衡度分數：0-1，越接近1越平衡
        """
        contexts = [stmt.get('context', 'general') for stmt in statements]
        unique_contexts = len(set(contexts))

        # 鼓勵多樣化的情境
        if len(statements) <= 2:
            return 1.0 if unique_contexts >= 1 else 0.5
        elif len(statements) <= 4:
            return unique_contexts / min(3, len(statements))  # 理想是3種不同情境
        else:
            return unique_contexts / len(statements)

    def calculate_statement_type_balance(self, statements: List[Dict]) -> float:
        """
        計算語句類型平衡度

        Returns:
            平衡度分數：0-1，越接近1越平衡
        """
        types = [stmt.get('statement_type', 'preference') for stmt in statements]
        unique_types = len(set(types))

        # 鼓勵不同類型的語句混合
        if len(statements) <= 2:
            return 1.0 if unique_types >= 1 else 0.5
        else:
            return unique_types / min(3, len(statements))  # 理想是3種不同類型

    def calculate_competitive_score(self, statements: List[Dict]) -> float:
        """
        計算題組的競爭性得分

        Returns:
            競爭性得分：0-1，越高表示選擇越困難
        """
        # 綜合多個因素
        sd_balance = self.calculate_social_desirability_balance(statements)
        dim_diversity = self.calculate_dimension_diversity(statements)
        context_balance = self.calculate_context_balance(statements)
        type_balance = self.calculate_statement_type_balance(statements)

        # 加權計算總分
        competitive_score = (
            sd_balance * 0.4 +          # 社會期許平衡最重要
            dim_diversity * 0.3 +       # 維度多樣性次之
            context_balance * 0.2 +     # 情境平衡
            type_balance * 0.1          # 類型平衡
        )

        return competitive_score

    def generate_competitive_blocks(self, num_blocks: int = 30, iterations: int = 1000) -> List[Dict]:
        """
        生成具有競爭性的題組

        Args:
            num_blocks: 要生成的題組數量
            iterations: 優化迭代次數

        Returns:
            優化後的題組列表
        """
        if len(self.statements) < num_blocks * 4:
            logger.warning(f"語句數量不足，需要 {num_blocks * 4} 條，實際只有 {len(self.statements)} 條")

        # 按維度分組語句
        statements_by_dim = {}
        for stmt in self.statements:
            dim = stmt.get('dimension', 'T1')
            if dim not in statements_by_dim:
                statements_by_dim[dim] = []
            statements_by_dim[dim].append(stmt)

        # 確保每個維度都有語句
        available_dims = [dim for dim in self.dimensions if dim in statements_by_dim and len(statements_by_dim[dim]) > 0]

        if len(available_dims) < 4:
            logger.error(f"可用維度數量不足，需要至少4個，實際只有 {len(available_dims)} 個")
            return []

        best_blocks = []
        best_score = 0.0

        # 多次嘗試生成最優配置
        for attempt in range(iterations):
            blocks = []
            used_statements = set()

            # 維度計數器，確保平衡覆蓋
            dimension_counts = {dim: 0 for dim in self.dimensions}
            target_per_dim = num_blocks * 4 // len(self.dimensions)

            for block_id in range(num_blocks):
                # 選擇4個不同維度
                available_for_block = []
                for dim in available_dims:
                    if dimension_counts[dim] < target_per_dim + 2:  # 允許一些彈性
                        available_for_block.extend([
                            stmt for stmt in statements_by_dim[dim]
                            if stmt['id'] not in used_statements
                        ])

                if len(available_for_block) < 4:
                    # 如果可用語句不足，放寬限制
                    available_for_block = [
                        stmt for stmt in self.statements
                        if stmt['id'] not in used_statements
                    ]

                if len(available_for_block) < 4:
                    logger.warning(f"第 {block_id} 題組：可用語句不足")
                    continue

                # 嘗試找到最佳的4語句組合
                best_block_statements = None
                best_block_score = 0.0

                for _ in range(50):  # 每個題組嘗試50次
                    # 隨機選擇4個語句，確保來自不同維度
                    candidate_statements = []
                    used_dims_in_block = set()

                    attempts = 0
                    while len(candidate_statements) < 4 and attempts < 100:
                        stmt = random.choice(available_for_block)
                        stmt_dim = stmt.get('dimension', 'T1')

                        if stmt_dim not in used_dims_in_block:
                            candidate_statements.append(stmt)
                            used_dims_in_block.add(stmt_dim)

                        attempts += 1

                    if len(candidate_statements) == 4:
                        score = self.calculate_competitive_score(candidate_statements)
                        if score > best_block_score:
                            best_block_score = score
                            best_block_statements = candidate_statements

                if best_block_statements:
                    # 記錄使用的語句
                    for stmt in best_block_statements:
                        used_statements.add(stmt['id'])
                        dimension_counts[stmt.get('dimension', 'T1')] += 1

                    # 創建題組
                    block = {
                        "block_id": block_id,
                        "statement_ids": [stmt['statement_id'] for stmt in best_block_statements],
                        "statements": best_block_statements,
                        "dimensions": [stmt['dimension'] for stmt in best_block_statements],
                        "competitive_score": best_block_score,
                        "social_desirability_range": {
                            "min": min(stmt.get('social_desirability', 4.0) for stmt in best_block_statements),
                            "max": max(stmt.get('social_desirability', 4.0) for stmt in best_block_statements),
                            "std": math.sqrt(sum((stmt.get('social_desirability', 4.0) -
                                               sum(s.get('social_desirability', 4.0) for s in best_block_statements)/4)**2
                                               for stmt in best_block_statements) / 4)
                        }
                    }
                    blocks.append(block)

            # 計算整體配置的品質
            if blocks:
                avg_competitive_score = sum(block['competitive_score'] for block in blocks) / len(blocks)
                dimension_balance = 1.0 - (max(dimension_counts.values()) - min(dimension_counts.values())) / max(dimension_counts.values())
                overall_score = avg_competitive_score * 0.7 + dimension_balance * 0.3

                if overall_score > best_score:
                    best_score = overall_score
                    best_blocks = blocks

            # 每100次迭代輸出進度
            if (attempt + 1) % 100 == 0:
                logger.info(f"優化進度: {attempt + 1}/{iterations}, 當前最佳分數: {best_score:.3f}")

        logger.info(f"✅ 生成 {len(best_blocks)} 個題組，平均競爭性得分: {best_score:.3f}")

        # 輸出統計信息
        if best_blocks:
            competitive_scores = [block['competitive_score'] for block in best_blocks]
            sd_ranges = [block['social_desirability_range']['std'] for block in best_blocks]

            logger.info(f"📊 競爭性得分範圍: {min(competitive_scores):.3f} - {max(competitive_scores):.3f}")
            logger.info(f"📊 社會期許標準差範圍: {min(sd_ranges):.3f} - {max(sd_ranges):.3f}")

        return best_blocks

    def save_blocks_to_file(self, blocks: List[Dict], filename: str):
        """保存題組到檔案"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    "blocks": blocks,
                    "metadata": {
                        "total_blocks": len(blocks),
                        "generation_timestamp": "2025-10-02",
                        "generator_version": "enhanced_v1.0",
                        "average_competitive_score": sum(b['competitive_score'] for b in blocks) / len(blocks) if blocks else 0
                    }
                }, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ 題組已保存到: {filename}")
        except Exception as e:
            logger.error(f"保存題組失敗: {e}")


def main():
    """測試函數"""
    generator = EnhancedBlockGenerator()

    if not generator.statements:
        print("❌ 無法載入語句庫")
        return

    print(f"📚 已載入 {len(generator.statements)} 條語句")

    # 生成改進版題組
    blocks = generator.generate_competitive_blocks(num_blocks=30, iterations=500)

    if blocks:
        # 保存結果
        output_path = str(get_file_storage_dir() / "v4_blocks_enhanced.json")
        generator.save_blocks_to_file(blocks, output_path)

        # 輸出摘要統計
        print(f"\n🎯 改進版題組生成完成！")
        print(f"📊 總題組數: {len(blocks)}")
        print(f"📊 平均競爭性得分: {sum(b['competitive_score'] for b in blocks) / len(blocks):.3f}")

        # 分析社會期許分布
        sd_stds = [block['social_desirability_range']['std'] for block in blocks]
        print(f"📊 社會期許標準差: 平均 {sum(sd_stds)/len(sd_stds):.3f}, 範圍 {min(sd_stds):.3f}-{max(sd_stds):.3f}")
    else:
        print("❌ 題組生成失敗")

if __name__ == "__main__":
    main()