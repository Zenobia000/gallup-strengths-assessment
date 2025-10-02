"""
測試 IRT 校準與常模計分
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../main/python'))

import numpy as np
from datetime import datetime
from pathlib import Path
import json

from models.v4.forced_choice import (
    Statement,
    QuartetBlock,
    ForcedChoiceResponse,
    ForcedChoiceBlockResponse
)
from core.v4.irt_calibration import ThurstonianIRTCalibrator
from core.v4.normative_scoring import NormativeScorer
from data.v4_statements import STATEMENT_POOL


def create_simulated_responses(n_persons: int = 100,
                              blocks_file: str = 'data/v4_assessment_blocks.json') -> tuple:
    """創建模擬回應資料"""
    # 載入區塊
    blocks_path = Path(blocks_file)
    if not blocks_path.exists():
        # 如果檔案不存在，使用簡單的模擬區塊
        blocks = create_simple_blocks()
    else:
        with open(blocks_path, 'r') as f:
            blocks_data = json.load(f)
            blocks = []
            for block_data in blocks_data['blocks']:
                statements = []
                for stmt_data in block_data['statements']:
                    statements.append(Statement(
                        statement_id=stmt_data['statement_id'],
                        text=stmt_data['text'],
                        dimension=stmt_data['dimension'],
                        factor_loading=stmt_data['factor_loading'],
                        social_desirability=stmt_data['social_desirability']
                    ))
                blocks.append(QuartetBlock(
                    block_id=block_data['block_id'],
                    statements=statements,
                    dimensions=block_data['dimensions']
                ))

    # 生成模擬回應
    responses = []
    for person_id in range(n_persons):
        # 每個人有不同的潛在特質
        true_theta = np.random.randn(12) * 0.8

        person_responses = []
        for block in blocks:
            # 基於潛在特質計算選擇概率
            utilities = []
            for stmt in block.statements:
                dim_idx = get_dimension_index(stmt.dimension)
                utility = stmt.factor_loading * true_theta[dim_idx] + np.random.normal(0, 0.3)
                utilities.append(utility)

            # 選擇最高和最低效用
            utilities = np.array(utilities)
            most_like = int(np.argmax(utilities))

            # 最不喜歡從剩餘選項中選擇
            remaining_indices = [i for i in range(4) if i != most_like]
            remaining_utils = [utilities[i] for i in remaining_indices]
            least_like = remaining_indices[np.argmin(remaining_utils)]

            person_responses.append(ForcedChoiceResponse(
                block_id=block.block_id,
                most_like_index=most_like,
                least_like_index=least_like,
                response_time_ms=np.random.randint(3000, 10000)
            ))

        responses.append(ForcedChoiceBlockResponse(
            session_id=f"sim_session_{person_id:03d}",
            participant_id=f"sim_participant_{person_id:03d}",
            responses=person_responses,
            blocks=blocks,
            start_time=datetime.now()
        ))

    return responses, blocks


def create_simple_blocks() -> list:
    """創建簡單的測試區塊"""
    blocks = []
    dimensions = list(STATEMENT_POOL.keys())

    for i in range(10):  # 10個區塊
        # 隨機選擇4個不同維度
        selected_dims = np.random.choice(dimensions, 4, replace=False)
        statements = []

        for dim in selected_dims:
            # 從該維度選擇一個語句
            stmt_data = STATEMENT_POOL[dim][0]  # 使用第一個語句
            statements.append(Statement(
                statement_id=stmt_data['statement_id'],
                text=stmt_data['text'],
                dimension=dim,
                factor_loading=stmt_data['factor_loading'],
                social_desirability=stmt_data['social_desirability']
            ))

        blocks.append(QuartetBlock(
            block_id=i,
            statements=statements,
            dimensions=list(selected_dims)
        ))

    return blocks


def get_dimension_index(dimension: str) -> int:
    """獲取維度索引"""
    dimensions = [
        'Achiever', 'Activator', 'Adaptability',
        'Analytical', 'Arranger', 'Belief',
        'Command', 'Communication', 'Competition',
        'Connectedness', 'Consistency', 'Context'
    ]
    return dimensions.index(dimension)


def test_irt_calibration():
    """測試 IRT 參數校準"""
    print("\n=== 測試 IRT 參數校準 ===\n")

    # 生成模擬資料
    print("生成模擬回應資料...")
    responses, blocks = create_simulated_responses(n_persons=50)
    print(f"  - 人數: {len(responses)}")
    print(f"  - 區塊數: {len(blocks)}")
    print(f"  - 每人回應數: {len(responses[0].responses)}")

    # 創建校準器
    calibrator = ThurstonianIRTCalibrator(
        n_dimensions=12,
        estimation_method='MMLE'
    )

    # 執行校準
    print("\n執行參數校準...")
    result = calibrator.calibrate(
        responses=responses,
        blocks=blocks,
        max_iter=20,  # 減少迭代次數以加快測試
        tol=1e-3
    )

    print(f"\n校準結果:")
    print(f"  - 收斂: {'是' if result.convergence else '否'}")
    print(f"  - 迭代次數: {result.iterations}")
    print(f"  - 樣本數: {result.sample_size}")

    print(f"\n模型擬合指標:")
    for metric, value in result.model_fit.items():
        print(f"  - {metric}: {value:.3f}")

    print(f"\n維度參數摘要:")
    for dim, params in list(result.dimension_parameters.items())[:3]:
        print(f"  {dim}:")
        print(f"    - 平均區分度: {params['mean_discrimination']:.3f}")
        print(f"    - 平均難度: {params['mean_difficulty']:.3f}")
        print(f"    - 信度: {params['reliability']:.3f}")

    # 儲存參數
    save_path = Path('data/v4_calibration_test.json')
    calibrator.save_parameters(result, save_path)
    print(f"\n參數已儲存至: {save_path}")

    return result


def test_normative_scoring():
    """測試常模計分"""
    print("\n=== 測試常模計分 ===\n")

    # 創建常模計分器
    scorer = NormativeScorer()

    # 生成模擬 θ 分數
    print("生成模擬 θ 分數...")
    dimensions = [
        'Achiever', 'Activator', 'Adaptability',
        'Analytical', 'Arranger', 'Belief',
        'Command', 'Communication', 'Competition',
        'Connectedness', 'Consistency', 'Context'
    ]

    # 模擬一個人的 θ 分數
    theta_scores = {}
    np.random.seed(42)
    for dim in dimensions:
        theta_scores[dim] = np.random.randn() * 0.8

    print(f"原始 θ 分數 (前3個):")
    for dim in dimensions[:3]:
        print(f"  - {dim}: {theta_scores[dim]:.3f}")

    # 計算常模分數
    print("\n計算常模分數...")
    norm_scores = scorer.compute_norm_scores(theta_scores)

    print(f"\n常模分數 (前3個):")
    for dim in dimensions[:3]:
        score = norm_scores[dim]
        print(f"  {dim}:")
        print(f"    - 百分位數: {score.percentile}%")
        print(f"    - T分數: {score.t_score}")
        print(f"    - 九分制: {score.stanine}")
        print(f"    - 解釋: {score.interpretation}")

    # 生成優勢概況
    print("\n生成優勢概況...")
    profile = scorer.get_strength_profile(norm_scores, top_n=5)

    print(f"\n前5優勢:")
    for i, strength in enumerate(profile['top_strengths'], 1):
        print(f"  {i}. {strength['dimension']}: "
              f"{strength['percentile']}% - {strength['interpretation']}")

    print(f"\n概況統計:")
    stats = profile['profile_statistics']
    print(f"  - 平均百分位: {stats['mean_percentile']:.1f}%")
    print(f"  - 範圍: {stats['range']:.1f}")
    print(f"  - 類型: {profile['profile_type']}")

    return norm_scores


def test_integration():
    """整合測試：校準到計分"""
    print("\n=== 整合測試 ===\n")

    # 1. 生成資料
    print("步驟1: 生成模擬資料")
    responses, blocks = create_simulated_responses(n_persons=30)

    # 2. 校準參數
    print("\n步驟2: 校準 IRT 參數")
    calibrator = ThurstonianIRTCalibrator()
    calibration_result = calibrator.calibrate(
        responses=responses[:20],  # 使用前20個作為校準樣本
        blocks=blocks,
        max_iter=10
    )

    # 3. 估計新受試者的 θ
    print("\n步驟3: 估計新受試者的 θ 分數")
    from core.v4.irt_scorer import ThurstonianIRTScorer

    scorer = ThurstonianIRTScorer()
    test_response = responses[20]  # 使用第21個作為測試

    theta_estimate = scorer.estimate_theta(
        test_response,
        method='MLE',
        use_prior=True
    )

    # 4. 轉換為常模分數
    print("\n步驟4: 轉換為常模分數")
    norm_scorer = NormativeScorer()

    # 將 theta array 轉換為 dict
    dimensions = [
        'Achiever', 'Activator', 'Adaptability',
        'Analytical', 'Arranger', 'Belief',
        'Command', 'Communication', 'Competition',
        'Connectedness', 'Consistency', 'Context'
    ]
    theta_dict = {dim: theta_estimate.theta[i] for i, dim in enumerate(dimensions)}

    norm_scores = norm_scorer.compute_norm_scores(theta_dict)

    # 5. 輸出結果
    print("\n最終結果:")
    print(f"參與者: {test_response.participant_id}")
    print(f"估計收斂: {theta_estimate.convergence}")

    sorted_scores = sorted(
        norm_scores.items(),
        key=lambda x: x[1].percentile,
        reverse=True
    )

    print(f"\n前3優勢:")
    for dim, score in sorted_scores[:3]:
        print(f"  - {dim}: {score.percentile}% ({score.interpretation})")

    return True


def run_all_tests():
    """執行所有測試"""
    print("=" * 60)
    print("IRT 校準與常模計分測試")
    print("=" * 60)

    try:
        # 測試校準
        calibration_result = test_irt_calibration()

        # 測試常模計分
        norm_scores = test_normative_scoring()

        # 整合測試
        integration_success = test_integration()

        print("\n" + "=" * 60)
        print("✅ 所有測試完成!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)