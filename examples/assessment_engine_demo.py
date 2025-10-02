"""
Assessment Engine Demo
評測引擎示範程式

Author: Claude Code AI
Date: 2025-10-02
Version: 1.0
"""

import sys
import json
from pathlib import Path

# 添加模組路徑
sys.path.append(str(Path(__file__).parent.parent / "src" / "main" / "python"))

from core.assessment import FileBasedAssessmentEngine


def demo_questionnaire_generation():
    """示範問卷生成"""
    print("=" * 60)
    print("問卷生成示範")
    print("=" * 60)

    # 初始化引擎
    engine = FileBasedAssessmentEngine()

    # 生成系統化問卷
    print("\n1. 生成系統化輪轉問卷...")
    systematic_questionnaire = engine.generate_questionnaire(
        method="systematic_rotation",
        random_seed=42
    )

    print(f"✅ 問卷ID: {systematic_questionnaire['questionnaire_id']}")
    print(f"✅ 總區塊數: {systematic_questionnaire['total_blocks']}")
    print(f"✅ 生成方法: {systematic_questionnaire['generation_method']}")

    # 顯示前3個區塊
    print("\n前3個區塊範例:")
    for i, block in enumerate(systematic_questionnaire['blocks'][:3]):
        print(f"\n區塊 {block['block_id']}:")
        for j, stmt in enumerate(block['statements']):
            print(f"  {j+1}. [{stmt['talent']}] {stmt['text']}")

        validation = block['validation']
        print(f"  驗證: 領域數={validation['domain_count']}, 領域多樣性={'✅' if validation['domain_diversity_met'] else '❌'}")

    # 顯示統計信息
    stats = systematic_questionnaire['summary_statistics']
    print(f"\n📊 統計信息:")
    print(f"  - 才幹頻率分布: {dict(list(stats['talent_frequency'].items())[:5])}...")
    print(f"  - 平衡分數: {stats['balance_score']:.3f}")

    return systematic_questionnaire


def demo_heuristic_generation():
    """示範啟發式生成"""
    print("\n2. 生成啟發式問卷...")
    engine = FileBasedAssessmentEngine()

    heuristic_questionnaire = engine.generate_questionnaire(
        method="heuristic",
        random_seed=42
    )

    print(f"✅ 問卷ID: {heuristic_questionnaire['questionnaire_id']}")
    print(f"✅ 生成方法: {heuristic_questionnaire['generation_method']}")

    # 比較平衡性
    stats = heuristic_questionnaire['summary_statistics']
    print(f"📊 啟發式平衡分數: {stats['balance_score']:.3f}")

    return heuristic_questionnaire


def demo_mock_assessment():
    """示範模擬評測"""
    print("\n=" * 60)
    print("模擬評測示範")
    print("=" * 60)

    engine = FileBasedAssessmentEngine()

    # 生成問卷
    questionnaire = engine.generate_questionnaire(method="systematic_rotation")

    # 模擬用戶回應 - 偏好 T4 (分析與洞察) 和 T1 (結構化執行)
    print("\n🤖 模擬偏好分析型和執行型才幹的用戶...")
    mock_responses = []

    for block in questionnaire['blocks']:
        statements = block['statements']

        # 策略：優先選擇 T4, T1，避免 T5, T7
        most_like = statements[0]  # 預設選第一個
        least_like = statements[-1]  # 預設選最後一個

        # 智能選擇邏輯
        for stmt in statements:
            if stmt['talent'] in ['T4', 'T1']:  # 分析與執行
                most_like = stmt
                break

        for stmt in reversed(statements):
            if stmt['talent'] in ['T5', 'T7']:  # 影響與客戶導向
                least_like = stmt
                break

        mock_responses.append({
            "block_id": block['block_id'],
            "most_like": most_like['statement_id'],
            "least_like": least_like['statement_id']
        })

    # 驗證回應
    validation = engine.validate_responses(mock_responses)
    print(f"✅ 回應驗證: {'通過' if validation['is_valid'] else '失敗'}")
    if validation['issues']:
        print(f"❌ 問題: {validation['issues']}")

    # 計算分數
    print("\n🧮 計算評測分數...")
    result = engine.calculate_scores(mock_responses)

    # 顯示才幹分數
    print("\n📊 才幹分數排名 (Top 5):")
    top_talents = sorted(result.talent_scores, key=lambda x: x.percentile, reverse=True)[:5]
    for i, talent in enumerate(top_talents):
        print(f"  {i+1}. {talent.talent_name} ({talent.talent_id}): {talent.percentile}%")

    # 顯示領域分數
    print("\n🎯 領域分數:")
    for domain in result.domain_scores:
        print(f"  {domain.domain_name}: {domain.percentile}%")

    # 顯示均衡指標
    balance = result.balance_metrics
    print(f"\n⚖️ 均衡指標:")
    print(f"  - 領域均衡指數 (DBI): {balance.dbi:.3f}")
    print(f"  - 相對熵: {balance.relative_entropy:.3f}")
    print(f"  - Gini係數: {balance.gini_coefficient:.3f}")
    print(f"  - 檔案類型: {balance.profile_type}")

    # 顯示原型分類
    archetype = result.archetype_classification
    print(f"\n🎭 職業原型分類:")
    print(f"  主要原型: {archetype.primary_archetype['archetype_name']} ({archetype.primary_archetype['probability']:.2f})")
    print(f"  次要原型: {archetype.secondary_archetype['archetype_name']} ({archetype.secondary_archetype['probability']:.2f})")
    print(f"  信心度: {archetype.primary_archetype['confidence']}")

    # 顯示職業建議
    career_recs = archetype.career_recommendations
    print(f"\n💼 職業建議:")
    print(f"  主要建議: {', '.join(career_recs['primary_suggestions'])}")
    print(f"  替代路徑: {', '.join(career_recs['alternative_paths'])}")

    print(f"\n🎯 整體信心度: {result.confidence:.2f}")

    return result


def demo_benchmark_criteria():
    """示範評測基準"""
    print("\n=" * 60)
    print("評測基準示範")
    print("=" * 60)

    engine = FileBasedAssessmentEngine()

    # 獲取基準標準
    benchmarks = engine.get_benchmark_criteria()

    print("\n📏 心理測量學標準:")
    reliability = benchmarks['psychometric_standards']['reliability']
    print(f"  Cronbach Alpha: 最低 {reliability['cronbach_alpha']['minimum']}, 目標 {reliability['cronbach_alpha']['target']}")

    validity = benchmarks['psychometric_standards']['validity']
    construct = validity['construct_validity']
    print(f"  因子載荷: 最低 {construct['factor_loading']['minimum']}, 目標 {construct['factor_loading']['target']}")

    print("\n⚡ 技術效能標準:")
    technical = benchmarks['technical_performance']
    print(f"  每區塊回應時間: {technical['response_time']['per_block']['target']}")
    print(f"  完成率目標: {technical['completion_rate']['target'] * 100}%")

    print("\n✅ 公平性標準:")
    fairness = benchmarks['psychometric_standards']['fairness']
    print(f"  DIF 最大效應值: {fairness['differential_item_functioning']['max_effect_size']}")


def main():
    """主函數"""
    print("🚀 File-based Assessment Engine Demo")
    print("基於文件存儲的評測引擎示範")

    try:
        # 1. 問卷生成示範
        systematic_q = demo_questionnaire_generation()
        heuristic_q = demo_heuristic_generation()

        # 2. 模擬評測示範
        assessment_result = demo_mock_assessment()

        # 3. 評測基準示範
        demo_benchmark_criteria()

        print("\n" + "=" * 60)
        print("✅ 所有示範完成！")
        print("=" * 60)

        # 詢問是否導出結果
        print("\n💾 是否導出評測結果到 JSON 檔案？(y/n): ", end="")

        # 簡化版本，直接導出
        output_file = "assessment_result_demo.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "systematic_questionnaire": systematic_q,
                "assessment_result": assessment_result.__dict__
            }, f, indent=2, ensure_ascii=False, default=str)

        print(f"✅ 結果已導出到 {output_file}")

    except Exception as e:
        print(f"❌ 示範過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()