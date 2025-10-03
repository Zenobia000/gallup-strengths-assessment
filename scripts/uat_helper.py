#!/usr/bin/env python3
"""
UAT 測試輔助工具
協助測試人員在做題時快速識別語句所屬的維度和領域
"""

import json
from pathlib import Path
from typing import Dict, List

# 領域與維度映射
DOMAIN_MAPPING = {
    "EXECUTING": {
        "name": "執行力",
        "talents": ["T1", "T2", "T12"],
        "color": "\033[94m"  # Blue
    },
    "STRATEGIC_THINKING": {
        "name": "戰略思維",
        "talents": ["T3", "T4", "T8"],
        "color": "\033[92m"  # Green
    },
    "INFLUENCING": {
        "name": "影響力",
        "talents": ["T5", "T7", "T11"],
        "color": "\033[93m"  # Yellow
    },
    "RELATIONSHIP_BUILDING": {
        "name": "關係建立",
        "talents": ["T6", "T9", "T10"],
        "color": "\033[95m"  # Magenta
    }
}

DIMENSION_NAMES = {
    "T1": "結構化執行",
    "T2": "品質完美主義",
    "T3": "探索創新",
    "T4": "分析洞察",
    "T5": "影響倡導",
    "T6": "協作和諧",
    "T7": "客戶導向",
    "T8": "學習成長",
    "T9": "紀律信任",
    "T10": "壓力調節",
    "T11": "衝突整合",
    "T12": "責任當責"
}

RESET = "\033[0m"

def get_domain_for_talent(talent_id: str) -> tuple:
    """獲取維度所屬的領域"""
    for domain_key, domain_info in DOMAIN_MAPPING.items():
        if talent_id in domain_info["talents"]:
            return domain_key, domain_info["name"], domain_info["color"]
    return "UNKNOWN", "未知", "\033[97m"

def load_statements():
    """載入語句庫"""
    statements_path = Path("/mnt/d/python_workspace/github/gallup-strengths-assessment/data/file_storage/v4_statements.json")

    try:
        with open(statements_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 無法載入語句庫: {e}")
        return []

def display_statement_guide():
    """顯示語句指南"""
    statements = load_statements()

    if not statements:
        return

    print("\n" + "=" * 80)
    print("📚 UAT 測試輔助工具 - 語句維度對照表")
    print("=" * 80 + "\n")

    # 按領域分組顯示
    for domain_key, domain_info in DOMAIN_MAPPING.items():
        color = domain_info["color"]
        domain_name = domain_info["name"]
        talents = domain_info["talents"]

        print(f"\n{color}【{domain_name}】{RESET}")
        print("-" * 80)

        for talent_id in talents:
            talent_name = DIMENSION_NAMES.get(talent_id, "未知")
            print(f"\n  {color}{talent_id} - {talent_name}{RESET}")

            # 找到該維度的語句
            talent_statements = [s for s in statements if s.get('dimension') == talent_id]

            for idx, stmt in enumerate(talent_statements[:3], 1):  # 只顯示前 3 條示例
                text = stmt.get('text', '').strip()
                stmt_id = stmt.get('statement_id', '')
                print(f"    {idx}. {text}")
                print(f"       ID: {stmt_id}")

    print("\n" + "=" * 80)

def display_test_strategy(target_domain: str):
    """顯示測試策略"""
    if target_domain not in DOMAIN_MAPPING:
        print(f"❌ 無效的領域: {target_domain}")
        return

    domain_info = DOMAIN_MAPPING[target_domain]
    color = domain_info["color"]
    domain_name = domain_info["name"]
    target_talents = domain_info["talents"]

    print("\n" + "=" * 80)
    print(f"🎯 測試策略：{color}{domain_name}主導{RESET}")
    print("=" * 80 + "\n")

    print(f"{color}目標維度：{RESET}")
    for talent_id in target_talents:
        talent_name = DIMENSION_NAMES.get(talent_id, "未知")
        print(f"  ✅ {talent_id} - {talent_name}")

    print(f"\n{color}選擇策略：{RESET}")
    print(f"  📌 【最符合 Most Like】：優先選擇 {', '.join(target_talents)} 的語句")

    # 找出對立領域
    opposite_talents = []
    for other_domain, other_info in DOMAIN_MAPPING.items():
        if other_domain != target_domain:
            opposite_talents.extend(other_info["talents"])

    print(f"  📌 【最不符合 Least Like】：優先選擇 {', '.join(opposite_talents[:6])} 等其他領域的語句")

    print(f"\n{color}預期結果：{RESET}")
    print(f"  🎯 主導才幹 (Top 4)：應包含 {', '.join(target_talents)} 中的至少 2-3 個")
    print(f"  📊 百分位範圍：75-95")

    print("\n" + "=" * 80)

def interactive_mode():
    """互動模式"""
    print("\n" + "=" * 80)
    print("🎮 UAT 測試輔助工具 - 互動模式")
    print("=" * 80 + "\n")

    print("選擇測試組：")
    print("  1. 執行力主導 (EXECUTING)")
    print("  2. 戰略思維主導 (STRATEGIC_THINKING)")
    print("  3. 影響力主導 (INFLUENCING)")
    print("  4. 關係建立主導 (RELATIONSHIP_BUILDING)")
    print("  5. 顯示完整語句指南")
    print("  0. 退出")

    while True:
        choice = input("\n請選擇 (0-5): ").strip()

        if choice == "0":
            print("👋 測試愉快！")
            break
        elif choice == "1":
            display_test_strategy("EXECUTING")
        elif choice == "2":
            display_test_strategy("STRATEGIC_THINKING")
        elif choice == "3":
            display_test_strategy("INFLUENCING")
        elif choice == "4":
            display_test_strategy("RELATIONSHIP_BUILDING")
        elif choice == "5":
            display_statement_guide()
        else:
            print("❌ 無效選擇，請重試")

def show_dimension_summary():
    """顯示維度摘要"""
    print("\n" + "=" * 80)
    print("📊 維度摘要表")
    print("=" * 80 + "\n")

    print(f"{'維度':<6} {'名稱':<15} {'領域':<15}")
    print("-" * 80)

    for talent_id, talent_name in DIMENSION_NAMES.items():
        domain_key, domain_name, color = get_domain_for_talent(talent_id)
        print(f"{talent_id:<6} {talent_name:<15} {color}{domain_name}{RESET}")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1].upper()

        if command in DOMAIN_MAPPING:
            display_test_strategy(command)
        elif command == "GUIDE":
            display_statement_guide()
        elif command == "SUMMARY":
            show_dimension_summary()
        else:
            print(f"❌ 未知命令: {command}")
            print("用法: python uat_helper.py [EXECUTING|STRATEGIC_THINKING|INFLUENCING|RELATIONSHIP_BUILDING|GUIDE|SUMMARY]")
    else:
        interactive_mode()
