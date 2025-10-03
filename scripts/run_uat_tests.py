#!/usr/bin/env python3
"""
自動化 UAT 測試腳本
模擬 4 組不同主導領域的使用者完成測驗
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# API 基礎 URL
BASE_URL = "http://localhost:8005"

# 領域與維度映射
DOMAIN_MAPPING = {
    "EXECUTING": ["T1", "T2", "T12"],
    "STRATEGIC_THINKING": ["T3", "T4", "T8"],
    "INFLUENCING": ["T5", "T7", "T11"],
    "RELATIONSHIP_BUILDING": ["T6", "T9", "T10"]
}

DIMENSION_NAMES = {
    "T1": "structured_execution",
    "T2": "quality_perfectionism",
    "T3": "exploration_innovation",
    "T4": "analytical_insight",
    "T5": "influence_advocacy",
    "T6": "collaboration_harmony",
    "T7": "customer_orientation",
    "T8": "learning_growth",
    "T9": "discipline_trust",
    "T10": "pressure_regulation",
    "T11": "conflict_integration",
    "T12": "responsibility_accountability"
}

class UATTester:
    """UAT 測試執行器"""

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.results = []

    def log(self, message: str):
        """記錄訊息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)

    def get_assessment_blocks(self) -> Tuple[str, List[Dict]]:
        """獲取評測題組"""
        try:
            response = requests.get(f"{BASE_URL}/api/assessment/blocks?v=1")
            response.raise_for_status()
            data = response.json()

            session_id = data.get("session_id")
            blocks = data.get("blocks", [])

            self.log(f"✅ 獲取題組成功 - Session: {session_id}, 題組數: {len(blocks)}")
            return session_id, blocks

        except Exception as e:
            self.log(f"❌ 獲取題組失敗: {e}")
            return None, []

    def identify_target_statement(self, block: Dict, target_talents: List[str]) -> int:
        """識別題組中屬於目標領域的語句"""
        statements = block.get("statements", [])
        statement_ids = block.get("statement_ids", [])

        for idx, stmt_id in enumerate(statement_ids):
            # 從 statement_id 提取維度 (例如 S_T1_01_Enhanced -> T1)
            parts = stmt_id.split("_")
            if len(parts) >= 2:
                talent = parts[1]  # T1, T2, etc.
                if talent in target_talents:
                    return idx

        # 如果沒找到目標維度，返回第一個
        return 0

    def identify_non_target_statement(self, block: Dict, target_talents: List[str]) -> int:
        """識別題組中不屬於目標領域的語句"""
        statements = block.get("statements", [])
        statement_ids = block.get("statement_ids", [])

        for idx, stmt_id in enumerate(statement_ids):
            parts = stmt_id.split("_")
            if len(parts) >= 2:
                talent = parts[1]
                if talent not in target_talents:
                    return idx

        # 如果全是目標維度，返回最後一個
        return len(statement_ids) - 1

    def simulate_user_responses(self, blocks: List[Dict], target_domain: str) -> List[Dict]:
        """模擬使用者根據目標領域作答"""
        target_talents = DOMAIN_MAPPING[target_domain]
        responses = []

        self.log(f"📝 模擬 {target_domain} 主導的使用者作答")
        self.log(f"   目標維度: {', '.join(target_talents)}")

        start_time = time.time()

        for idx, block in enumerate(blocks):
            block_id = block.get("block_id", idx)

            # 選擇最符合：優先選目標領域
            most_like_index = self.identify_target_statement(block, target_talents)

            # 選擇最不符合：優先選非目標領域
            least_like_index = self.identify_non_target_statement(block, target_talents)

            # 確保不重複
            if most_like_index == least_like_index:
                least_like_index = (most_like_index + 1) % len(block.get("statement_ids", []))

            response_time = int((time.time() - start_time) * 1000)

            response = {
                "question_id": f"q{idx}",
                "most_like_index": most_like_index,
                "least_like_index": least_like_index,
                "block_id": block_id,
                "response_time_ms": response_time
            }

            responses.append(response)

        total_time = int(time.time() - start_time)
        self.log(f"   完成 {len(responses)} 題，總耗時: {total_time} 秒")

        return responses

    def submit_assessment(self, session_id: str, responses: List[Dict]) -> Dict:
        """提交評測"""
        try:
            total_time = responses[-1]["response_time_ms"] // 1000 if responses else 0

            payload = {
                "session_id": session_id,
                "responses": responses,
                "completion_time_seconds": total_time
            }

            response = requests.post(
                f"{BASE_URL}/api/assessment/submit?v=1",
                json=payload
            )
            response.raise_for_status()

            self.log(f"✅ 提交成功")
            return response.json()

        except Exception as e:
            self.log(f"❌ 提交失敗: {e}")
            return {}

    def get_results(self, session_id: str) -> Dict:
        """獲取評測結果"""
        try:
            response = requests.get(f"{BASE_URL}/api/assessment/results/{session_id}")
            response.raise_for_status()
            data = response.json()

            self.log(f"✅ 獲取結果成功")
            return data

        except Exception as e:
            self.log(f"❌ 獲取結果失敗: {e}")
            return {}

    def analyze_results(self, results: Dict, target_domain: str) -> Dict:
        """分析測試結果"""
        target_talents = DOMAIN_MAPPING[target_domain]

        # 提取維度分數 - API 返回格式為 scores 而不是 dimension_scores
        dimension_scores = results.get("scores", results.get("dimension_scores", {}))

        # 按分數排序
        sorted_scores = sorted(dimension_scores.items(), key=lambda x: x[1], reverse=True)

        # 提取主導才幹、支援才幹、待管理領域
        dominant = sorted_scores[:4]
        supporting = sorted_scores[4:8]
        lesser = sorted_scores[8:]

        # 檢查主導才幹中包含多少目標維度
        # 處理 API 返回的格式：t1_structured_execution 或 structured_execution
        dominant_names = [name.split('_', 1)[-1] if '_' in name else name for name, score in dominant]
        target_in_dominant = sum(1 for talent in target_talents if DIMENSION_NAMES[talent] in dominant_names)

        # 計算百分位差距
        max_percentile = dominant[0][1] if dominant else 0
        min_percentile = lesser[-1][1] if lesser else 0
        gap = max_percentile - min_percentile

        analysis = {
            "target_domain": target_domain,
            "target_talents": target_talents,
            "dominant_talents": dominant,
            "supporting_talents": supporting,
            "lesser_talents": lesser,
            "target_coverage": f"{target_in_dominant}/3",
            "percentile_gap": round(gap, 1),
            "passed": target_in_dominant >= 2
        }

        return analysis

    def format_test_result(self, test_num: int, domain: str, session_id: str, analysis: Dict) -> str:
        """格式化測試結果"""
        lines = []
        lines.append(f"\n{'='*80}")
        lines.append(f"測試組 {test_num}：{domain}")
        lines.append(f"{'='*80}")
        lines.append(f"Session ID: {session_id}")
        lines.append(f"目標維度: {', '.join(analysis['target_talents'])}")
        lines.append(f"")

        lines.append(f"主導才幹 (Top 4):")
        for idx, (name, score) in enumerate(analysis['dominant_talents'], 1):
            marker = "🎯" if any(DIMENSION_NAMES[t] == name for t in analysis['target_talents']) else "  "
            lines.append(f"  {idx}. {marker} {name} - {score:.1f}")

        lines.append(f"")
        lines.append(f"支援才幹 (Middle 4):")
        for idx, (name, score) in enumerate(analysis['supporting_talents'], 5):
            lines.append(f"  {idx}. {name} - {score:.1f}")

        lines.append(f"")
        lines.append(f"待管理領域 (Bottom 4):")
        for idx, (name, score) in enumerate(analysis['lesser_talents'], 9):
            lines.append(f"  {idx}. {name} - {score:.1f}")

        lines.append(f"")
        lines.append(f"驗證結果:")
        lines.append(f"  主導才幹覆蓋率: {analysis['target_coverage']}")
        lines.append(f"  百分位差距: {analysis['percentile_gap']}")
        lines.append(f"  測試通過: {'✅ 是' if analysis['passed'] else '❌ 否'}")

        return "\n".join(lines)

    def run_test_case(self, test_num: int, domain: str) -> Dict:
        """執行單個測試案例"""
        self.log(f"\n{'='*80}")
        self.log(f"開始測試組 {test_num}: {domain}")
        self.log(f"{'='*80}")

        # 1. 獲取題組
        session_id, blocks = self.get_assessment_blocks()
        if not session_id or not blocks:
            return {"error": "無法獲取題組"}

        # 2. 模擬作答
        responses = self.simulate_user_responses(blocks, domain)

        # 3. 提交
        submit_result = self.submit_assessment(session_id, responses)

        # 等待評分完成
        time.sleep(2)

        # 4. 獲取結果
        results = self.get_results(session_id)

        # 5. 分析結果
        analysis = self.analyze_results(results, domain)
        analysis["session_id"] = session_id

        # 6. 格式化輸出
        result_text = self.format_test_result(test_num, domain, session_id, analysis)
        self.log(result_text)

        # 7. 保存到日誌
        log_file = self.log_dir / f"test_{test_num}_{domain.lower()}.log"
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(result_text)

        return analysis

    def run_all_tests(self):
        """執行所有 4 組測試"""
        test_cases = [
            (1, "EXECUTING"),
            (2, "STRATEGIC_THINKING"),
            (3, "INFLUENCING"),
            (4, "RELATIONSHIP_BUILDING")
        ]

        all_results = []

        for test_num, domain in test_cases:
            result = self.run_test_case(test_num, domain)
            all_results.append(result)
            time.sleep(2)  # 間隔 2 秒

        # 生成總結報告
        self.generate_summary_report(all_results)

        return all_results

    def generate_summary_report(self, results: List[Dict]):
        """生成總結報告"""
        lines = []
        lines.append(f"\n{'='*80}")
        lines.append(f"UAT 測試總結報告")
        lines.append(f"{'='*80}")
        lines.append(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"")

        passed_count = sum(1 for r in results if r.get("passed", False))
        total_count = len(results)

        lines.append(f"通過率: {passed_count}/{total_count} ({passed_count*100//total_count}%)")
        lines.append(f"")

        lines.append(f"{'測試組':<5} {'領域':<25} {'覆蓋率':<10} {'百分位差':<12} {'通過':<6}")
        lines.append(f"{'-'*80}")

        for idx, result in enumerate(results, 1):
            domain = result.get("target_domain", "N/A")
            coverage = result.get("target_coverage", "0/3")
            gap = result.get("percentile_gap", 0)
            passed = "✅" if result.get("passed", False) else "❌"

            lines.append(f"{idx:<5} {domain:<25} {coverage:<10} {gap:<12.1f} {passed:<6}")

        lines.append(f"")
        lines.append(f"測試結論:")
        if passed_count == total_count:
            lines.append(f"  ✅ 所有測試通過！評分系統正確識別不同主導領域。")
        elif passed_count >= total_count * 0.75:
            lines.append(f"  ⚠️ 大部分測試通過，但有 {total_count - passed_count} 個案例需要改進。")
        else:
            lines.append(f"  ❌ 測試失敗，評分系統需要調整。")

        report_text = "\n".join(lines)
        print(report_text)

        # 保存總結報告
        summary_file = self.log_dir / "uat_summary_report.log"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(report_text)

        self.log(f"\n📊 總結報告已保存到: {summary_file}")


def main():
    """主函數"""
    print("\n" + "="*80)
    print("🚀 開始 UAT 自動化測試")
    print("="*80 + "\n")

    tester = UATTester(log_dir="logs")
    results = tester.run_all_tests()

    print("\n" + "="*80)
    print("✅ UAT 測試完成！")
    print("="*80)
    print(f"\n📁 日誌位置: logs/")
    print(f"   - test_1_executing.log")
    print(f"   - test_2_strategic_thinking.log")
    print(f"   - test_3_influencing.log")
    print(f"   - test_4_relationship_building.log")
    print(f"   - uat_summary_report.log")


if __name__ == "__main__":
    main()
