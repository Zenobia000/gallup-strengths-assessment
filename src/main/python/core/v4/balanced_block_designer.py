"""
Balanced Block Designer for Objective T1-T12 Assessment

客觀平衡的題組設計器，確保：
1. 所有 T1-T12 維度均等曝光
2. 每個維度至少出現在 3 個題組中
3. 維度對比次數盡可能平衡
4. 總題組數最小化（效率與客觀性平衡）

設計原則：
- 客觀性 > 效率性
- 完整性 > 簡潔性
- 均衡性 > 隨機性
"""

from typing import List, Dict, Set, Tuple
from itertools import combinations
from collections import defaultdict
import random
import numpy as np

from models.v4.forced_choice import Statement
from .block_designer import QuartetBlock


class BalancedBlockDesigner:
    """客觀平衡的四選二題組設計器"""

    def __init__(self, statements: List[Statement], min_exposure_per_dimension: int = 3):
        """
        初始化平衡題組設計器

        Args:
            statements: 所有可用的陳述
            min_exposure_per_dimension: 每個維度的最小曝光次數
        """
        self.statements = statements
        self.min_exposure_per_dimension = min_exposure_per_dimension
        self.n_blocks = 12  # 預設值，會被外部設定

        # 按維度分組 statements
        self.statements_by_dim = defaultdict(list)
        for stmt in statements:
            self.statements_by_dim[stmt.dimension].append(stmt)

        print(f"維度數量: {len(self.statements_by_dim)}")
        print(f"各維度 statement 數量: {dict((dim, len(stmts)) for dim, stmts in self.statements_by_dim.items())}")

    def create_objective_blocks(self) -> List[QuartetBlock]:
        """
        創建客觀平衡的題組

        策略：
        1. 確保每個維度至少曝光 min_exposure_per_dimension 次
        2. 使用貪婪算法最小化總題組數
        3. 平衡維度對比次數
        """

        # 計算需要的最小題組數
        total_dimensions = len(self.statements_by_dim)
        min_blocks_needed = (total_dimensions * self.min_exposure_per_dimension) // 4

        print(f"理論最小題組數: {min_blocks_needed}")

        # 使用系統化方法確保完整覆蓋
        blocks = self._create_systematic_balanced_blocks()

        # 驗證覆蓋度
        coverage = self._validate_dimension_coverage(blocks)

        if not coverage['is_complete']:
            print(f"⚠️ 維度覆蓋不完整，補充額外題組")
            additional_blocks = self._create_supplementary_blocks(coverage['missing_dimensions'])
            blocks.extend(additional_blocks)

        # 最終驗證
        final_coverage = self._validate_dimension_coverage(blocks)
        print(f"✅ 最終題組數: {len(blocks)}")
        print(f"✅ 維度覆蓋完整性: {final_coverage['is_complete']}")

        return blocks

    def _create_systematic_balanced_blocks(self) -> List[QuartetBlock]:
        """系統化創建平衡題組"""
        blocks = []
        dimension_usage = defaultdict(int)
        pair_usage = defaultdict(int)
        used_statements = set()

        dimensions = list(self.statements_by_dim.keys())

        # 第一階段：確保每個維度都被包含
        # 使用輪轉方式創建基礎題組
        base_combinations = self._generate_base_combinations(dimensions)

        for combo in base_combinations:
            block = self._create_block_from_dimensions(combo, used_statements)
            if block:
                blocks.append(block)

                # 更新使用計數
                for dim in combo:
                    dimension_usage[dim] += 1
                for pair in combinations(combo, 2):
                    pair_usage[tuple(sorted(pair))] += 1

                # 更新已使用的 statements
                for stmt in block.statements:
                    used_statements.add(stmt.statement_id)

        # 第二階段：補強低曝光維度
        while min(dimension_usage.values()) < self.min_exposure_per_dimension:
            # 找出曝光不足的維度
            under_exposed = [dim for dim, count in dimension_usage.items()
                           if count < self.min_exposure_per_dimension]

            if not under_exposed:
                break

            # 創建包含低曝光維度的題組
            combo = self._select_balancing_combination(under_exposed, dimension_usage, pair_usage)
            block = self._create_block_from_dimensions(combo, used_statements)

            if block:
                blocks.append(block)

                # 更新計數
                for dim in combo:
                    dimension_usage[dim] += 1
                for pair in combinations(combo, 2):
                    pair_usage[tuple(sorted(pair))] += 1

                for stmt in block.statements:
                    used_statements.add(stmt.statement_id)
            else:
                break  # 無法創建更多題組

        return blocks

    def _generate_base_combinations(self, dimensions: List[str]) -> List[Tuple[str, ...]]:
        """生成基礎維度組合，確保所有維度都被包含"""
        combinations_list = []

        # 12 個維度，每組 4 個，理論上需要 3 組來覆蓋所有維度
        # 使用循環分配確保均勻分布

        # 方法：創建3個基礎組合，每組包含4個維度，盡可能不重疊
        shuffled_dims = dimensions.copy()
        random.shuffle(shuffled_dims)

        for i in range(0, len(shuffled_dims), 4):
            combo = tuple(shuffled_dims[i:i+4])
            if len(combo) == 4:  # 確保是完整的4維度組合
                combinations_list.append(combo)

        # 如果還有剩餘維度，創建混合組合
        if len(shuffled_dims) % 4 != 0:
            remaining = shuffled_dims[-(len(shuffled_dims) % 4):]
            # 與前面的維度混合創建新組合
            front_dims = shuffled_dims[:4-len(remaining)]
            mixed_combo = tuple(remaining + front_dims)
            combinations_list.append(mixed_combo)

        return combinations_list

    def _select_balancing_combination(self, under_exposed: List[str],
                                    dimension_usage: Dict[str, int],
                                    pair_usage: Dict[Tuple[str, str], int]) -> Tuple[str, ...]:
        """選擇平衡的維度組合，優先包含低曝光維度"""

        # 選擇 2-3 個低曝光維度
        target_dims = under_exposed[:3]

        # 補足到 4 個維度
        all_dims = list(self.statements_by_dim.keys())
        remaining_slots = 4 - len(target_dims)

        # 選擇使用次數較少的維度來補足
        other_dims = [dim for dim in all_dims if dim not in target_dims]
        other_dims.sort(key=lambda d: dimension_usage.get(d, 0))

        final_combo = target_dims + other_dims[:remaining_slots]

        # 確保正好 4 個維度
        if len(final_combo) < 4:
            # 如果不足4個，隨機補足
            available = [dim for dim in all_dims if dim not in final_combo]
            final_combo.extend(random.sample(available, 4 - len(final_combo)))

        return tuple(final_combo[:4])

    def _create_block_from_dimensions(self, dimensions: Tuple[str, ...],
                                    used_statements: Set[str]) -> QuartetBlock:
        """從指定維度創建題組"""
        block_statements = []

        for dim in dimensions:
            # 獲取該維度的可用 statements
            available = [s for s in self.statements_by_dim[dim]
                        if s.statement_id not in used_statements]

            if not available:
                # 如果沒有未使用的，從所有 statements 中選擇
                available = self.statements_by_dim[dim]

            if available:
                # 選擇 social desirability 最接近已選 statements 的
                if block_statements:
                    target_sd = np.mean([s.social_desirability for s in block_statements])
                    best_stmt = min(available,
                                  key=lambda s: abs(s.social_desirability - target_sd))
                else:
                    best_stmt = random.choice(available)

                block_statements.append(best_stmt)
            else:
                print(f"⚠️ 維度 {dim} 沒有可用的 statements")
                return None

        if len(block_statements) == 4:
            return QuartetBlock(
                block_id=len(used_statements),  # 臨時 ID
                statements=block_statements,
                dimensions=list(dimensions)
            )

        return None

    def _create_supplementary_blocks(self, missing_dimensions: List[str]) -> List[QuartetBlock]:
        """創建補充題組覆蓋缺失的維度"""
        supplementary_blocks = []

        while missing_dimensions:
            # 每次取最多4個缺失維度
            combo_dims = missing_dimensions[:4]

            # 如果不足4個，補充其他維度
            if len(combo_dims) < 4:
                all_dims = list(self.statements_by_dim.keys())
                available = [dim for dim in all_dims if dim not in combo_dims]
                combo_dims.extend(random.sample(available, 4 - len(combo_dims)))

            # 創建題組
            block = self._create_block_from_dimensions(tuple(combo_dims), set())
            if block:
                supplementary_blocks.append(block)

            # 移除已處理的維度
            missing_dimensions = missing_dimensions[4:]

        return supplementary_blocks

    def _validate_dimension_coverage(self, blocks: List[QuartetBlock]) -> Dict:
        """驗證維度覆蓋度"""
        dimension_counts = defaultdict(int)

        for block in blocks:
            for dim in block.dimensions:
                dimension_counts[dim] += 1

        all_dimensions = set(self.statements_by_dim.keys())
        covered_dimensions = set(dimension_counts.keys())
        missing_dimensions = list(all_dimensions - covered_dimensions)

        # 檢查是否每個維度都達到最小曝光要求
        under_exposed = [dim for dim, count in dimension_counts.items()
                        if count < self.min_exposure_per_dimension]

        is_complete = (len(missing_dimensions) == 0 and len(under_exposed) == 0)

        coverage_report = {
            'is_complete': is_complete,
            'total_blocks': len(blocks),
            'covered_dimensions': len(covered_dimensions),
            'missing_dimensions': missing_dimensions,
            'under_exposed_dimensions': under_exposed,
            'dimension_counts': dict(dimension_counts)
        }

        print(f"維度覆蓋報告:")
        print(f"  總題組數: {coverage_report['total_blocks']}")
        print(f"  覆蓋維度: {coverage_report['covered_dimensions']}/12")
        if missing_dimensions:
            print(f"  缺失維度: {missing_dimensions}")
        if under_exposed:
            print(f"  曝光不足維度: {under_exposed}")

        return coverage_report

    def get_optimal_block_count(self) -> int:
        """計算達到完整覆蓋的最優題組數"""
        # 12個維度，每組4個，每個維度至少3次曝光
        # 理論最小值：(12 * 3) / 4 = 9
        # 考慮平衡性，建議 12-15 題組

        dimensions_count = len(self.statements_by_dim)
        theoretical_min = (dimensions_count * self.min_exposure_per_dimension) // 4
        practical_optimum = theoretical_min + 3  # 加3個題組提升平衡性

        return practical_optimum


def create_objective_assessment_blocks(statements: List[Statement],
                                     target_blocks: int = None) -> List[QuartetBlock]:
    """
    創建客觀的評測題組

    Args:
        statements: 所有可用陳述
        target_blocks: 目標題組數（None 時自動計算最優值）

    Returns:
        平衡的題組列表
    """
    designer = BalancedBlockDesigner(statements, min_exposure_per_dimension=3)

    if target_blocks is None:
        target_blocks = designer.get_optimal_block_count()
        print(f"自動計算最優題組數: {target_blocks}")

    # 設定題組數並創建
    designer.n_blocks = target_blocks
    blocks = designer.create_objective_blocks()

    return blocks


if __name__ == "__main__":
    # 測試平衡題組設計
    from data.v4_statements import get_all_statements
    from models.v4.forced_choice import Statement as FCStatement

    # 準備測試資料
    statements_list = []
    for stmt in get_all_statements():
        statements_list.append(FCStatement(
            statement_id=stmt.statement_id,
            text=stmt.text,
            dimension=stmt.dimension,
            factor_loading=stmt.factor_loading,
            social_desirability=stmt.social_desirability
        ))

    # 測試平衡設計
    blocks = create_objective_assessment_blocks(statements_list)

    print(f"\n=== 平衡性驗證 ===")
    dimension_counts = defaultdict(int)
    for block in blocks:
        for dim in block.dimensions:
            dimension_counts[dim] += 1

    print("各維度曝光次數:")
    for dim in sorted(dimension_counts.keys()):
        print(f"  {dim}: {dimension_counts[dim]} 次")

    min_exposure = min(dimension_counts.values())
    max_exposure = max(dimension_counts.values())
    print(f"\n曝光分布: 最少 {min_exposure}, 最多 {max_exposure}")
    print(f"平衡程度: {'優秀' if max_exposure - min_exposure <= 1 else '可接受' if max_exposure - min_exposure <= 2 else '需改進'}")