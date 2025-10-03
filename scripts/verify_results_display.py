#!/usr/bin/env python3
"""
驗證 results.html 能正確顯示 UAT 測試結果
"""

import requests
import json
from datetime import datetime

# Test session from UAT
TEST_SESSION = "v4_2e76cae3b245"  # EXECUTING domain test
API_BASE = "http://localhost:8005"

def verify_api_response():
    """驗證 API 返回正確的評分數據"""
    print("=" * 80)
    print("驗證 API 響應")
    print("=" * 80)

    url = f"{API_BASE}/api/assessment/results/{TEST_SESSION}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"❌ API 請求失敗: {response.status_code}")
        return False

    data = response.json()
    scores = data.get("scores", {})

    print(f"✅ API 響應成功")
    print(f"Session ID: {data.get('session_id')}")
    print(f"總維度數: {len(scores)}")

    # Check score structure
    expected_talents = [f"t{i}" for i in range(1, 13)]
    found_talents = [key.split('_')[0] for key in scores.keys()]

    print(f"\n評分數據檢查:")
    for i in range(1, 13):
        talent_key = f"t{i}"
        matching_keys = [k for k in scores.keys() if k.startswith(talent_key + "_")]

        if matching_keys:
            score = scores[matching_keys[0]]
            tier = "主導" if score > 75 else ("支援" if score >= 25 else "待管理")
            print(f"  {matching_keys[0]}: {score:.1f} ({tier})")
        else:
            print(f"  ❌ 缺失 {talent_key}")

    # Verify dominant talents
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_4 = sorted_scores[:4]

    print(f"\n主導才幹 (Top 4):")
    for talent, score in top_4:
        print(f"  {talent}: {score:.1f}")

    # Check expected EXECUTING domain talents in top 4
    executing_talents = ["t1_structured_execution", "t2_quality_perfectionism", "t12_responsibility_accountability"]
    top_4_ids = [t[0] for t in top_4]

    executing_in_top = [t for t in executing_talents if t in top_4_ids]
    print(f"\n執行力維度覆蓋: {len(executing_in_top)}/{len(executing_talents)}")

    if len(executing_in_top) >= 2:
        print("✅ 正確識別執行力主導特質")
        return True
    else:
        print("❌ 執行力特質識別不足")
        return False

def verify_html_structure():
    """驗證 HTML 檔案包含必要的動態渲染邏輯"""
    print("\n" + "=" * 80)
    print("驗證 HTML 動態渲染邏輯")
    print("=" * 80)

    html_path = "/mnt/d/python_workspace/github/gallup-strengths-assessment/src/main/resources/static/results.html"

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Check critical JavaScript functions
    critical_functions = [
        "loadResults",
        "displayResults",
        "parseTalents",
        "renderTalentGrid",
        "updateKPIDashboard",
        "generateDNAVisualization"
    ]

    print("\n關鍵 JavaScript 函數檢查:")
    all_found = True
    for func in critical_functions:
        if f"function {func}" in html_content:
            print(f"  ✅ {func}")
        else:
            print(f"  ❌ {func} 缺失")
            all_found = False

    # Check API endpoint configuration
    if "api/assessment/results" in html_content:
        print(f"\n✅ API 端點配置正確")
    else:
        print(f"\n❌ API 端點配置缺失")
        all_found = False

    # Check talent definitions
    if "TALENT_DEFINITIONS" in html_content:
        print(f"✅ 才幹定義已載入")
    else:
        print(f"❌ 才幹定義缺失")
        all_found = False

    return all_found

def generate_manual_test_url():
    """生成手動測試 URL"""
    print("\n" + "=" * 80)
    print("手動測試指南")
    print("=" * 80)

    print(f"\n請在瀏覽器中打開以下 URL 進行視覺驗證:")
    print(f"\n  {API_BASE}/static/results.html?session={TEST_SESSION}")

    print(f"\n預期顯示:")
    print(f"  - 主導才幹 (Top 4): 應包含「結構化執行」、「品質與完備」")
    print(f"  - 執行力領域: 應為主導領域")
    print(f"  - 百分位分數: Top 4 應 > 80")
    print(f"  - DNA 視覺化: 應顯示 12 個才幹節點，顏色對應領域")

    print(f"\n其他測試 Session:")
    test_sessions = {
        "v4_2e76cae3b245": "執行力主導",
        "v4_d52cc95aa7e5": "戰略思維主導",
        "v4_b339d519f357": "影響力主導",
        "v4_8a76783b9eb6": "關係建立主導"
    }

    for session, domain in test_sessions.items():
        print(f"  {API_BASE}/static/results.html?session={session}")
        print(f"    → {domain}")

def main():
    print("Results Display Verification")
    print("=" * 80)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Verify API
    api_ok = verify_api_response()

    # Verify HTML
    html_ok = verify_html_structure()

    # Generate manual test instructions
    generate_manual_test_url()

    # Summary
    print("\n" + "=" * 80)
    print("驗證總結")
    print("=" * 80)

    if api_ok and html_ok:
        print("✅ API 和 HTML 結構驗證通過")
        print("✅ results.html 應能正確顯示更新後的評分結果")
        print("\n建議: 在瀏覽器中手動驗證視覺呈現")
    else:
        if not api_ok:
            print("❌ API 響應驗證失敗")
        if not html_ok:
            print("❌ HTML 結構驗證失敗")

    print()

if __name__ == "__main__":
    main()
