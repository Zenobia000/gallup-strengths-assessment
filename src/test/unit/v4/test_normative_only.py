"""
簡化測試 - 僅測試常模計分功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../main/python'))

import numpy as np
from pathlib import Path

from core.v4.normative_scoring import NormativeScorer, create_sample_norms


def test_normative_scoring():
    """測試常模計分功能"""
    print("=" * 60)
    print("常模計分功能測試")
    print("=" * 60)

    # 創建範例常模
    print("\n1. 創建範例常模資料...")
    norm_data = create_sample_norms()
    print(f"   已創建 {len(norm_data)} 個維度的常模")

    # 創建計分器
    scorer = NormativeScorer(Path('data/v4_normative_data.json'))

    # 測試不同水平的分數
    test_cases = [
        ("高水平", 1.5),
        ("平均水平", 0.0),
        ("低水平", -1.5),
    ]

    print("\n2. 測試不同水平的分數轉換:")
    dimensions = ['Achiever', 'Communication', 'Analytical']

    for level_name, theta_value in test_cases:
        print(f"\n   {level_name} (θ = {theta_value}):")

        theta_scores = {dim: theta_value for dim in dimensions}
        norm_scores = scorer.compute_norm_scores(theta_scores)

        for dim in dimensions:
            score = norm_scores[dim]
            print(f"   - {dim:15} 百分位: {score.percentile:5.1f}%, "
                  f"T分數: {score.t_score:5.1f}, "
                  f"九分: {score.stanine}, "
                  f"{score.interpretation}")

    # 測試個人概況
    print("\n3. 測試個人優勢概況生成:")

    # 生成隨機概況
    np.random.seed(42)
    all_dimensions = [
        'Achiever', 'Activator', 'Adaptability',
        'Analytical', 'Arranger', 'Belief',
        'Command', 'Communication', 'Competition',
        'Connectedness', 'Consistency', 'Context'
    ]

    theta_scores = {}
    for i, dim in enumerate(all_dimensions):
        # 創造有差異的分數
        if i < 3:
            theta_scores[dim] = np.random.uniform(1.0, 2.0)  # 高分
        elif i < 6:
            theta_scores[dim] = np.random.uniform(-0.5, 0.5)  # 中等
        else:
            theta_scores[dim] = np.random.uniform(-2.0, -1.0)  # 低分

    norm_scores = scorer.compute_norm_scores(theta_scores)
    profile = scorer.get_strength_profile(norm_scores)

    print("\n   前5優勢:")
    for i, strength in enumerate(profile['top_strengths'], 1):
        print(f"   {i}. {strength['dimension']:15} "
              f"百分位: {strength['percentile']:5.1f}% - "
              f"{strength['interpretation']}")

    print("\n   發展領域:")
    for area in profile['development_areas'][:3]:
        print(f"   - {area['dimension']:15} "
              f"百分位: {area['percentile']:5.1f}%")

    print(f"\n   概況類型: {profile['profile_type']}")
    print(f"   平均百分位: {profile['profile_statistics']['mean_percentile']:.1f}%")
    print(f"   分數範圍: {profile['profile_statistics']['range']:.1f}")

    # 測試類別分析
    print("\n4. 優勢類別分析:")
    cat_dist = profile['category_distribution']
    for category, stats in cat_dist.items():
        print(f"   - {category:12} 平均百分位: {stats['mean_percentile']:5.1f}%, "
              f"最高: {stats['max_percentile']:5.1f}%")

    print("\n" + "=" * 60)
    print("✅ 常模計分測試完成!")
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = test_normative_scoring()
    sys.exit(0 if success else 1)