#!/usr/bin/env python3
"""
Sync Statement Bank from JSON to File Storage
將 statement_bank.json 的120語句庫同步到 file storage CSV/JSON 格式
確保每個維度有10個語句，支援30題組生成
"""

import json
import csv
import os
from pathlib import Path
from datetime import datetime

def load_statement_bank():
    """載入標準120語句庫"""
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    statement_bank_path = project_root / "src" / "main" / "resources" / "assessment" / "statement_bank.json"

    if not statement_bank_path.exists():
        print(f"Error: Statement bank not found at {statement_bank_path}")
        return {}

    with open(statement_bank_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def convert_to_file_storage_format(statement_bank):
    """轉換為 file storage 格式"""
    statements = []
    current_id = 1

    if "statement_bank" not in statement_bank:
        print("Error: No statement_bank key found")
        return statements

    for talent_key, talent_statements in statement_bank["statement_bank"].items():
        # Extract talent ID from key like "T1_結構化執行"
        talent_id = talent_key.split("_")[0]
        talent_name = talent_key.split("_", 1)[1] if "_" in talent_key else talent_id

        print(f"Processing {talent_id}: {len(talent_statements)} statements")

        for stmt in talent_statements:
            statement = {
                "id": current_id,
                "statement_id": stmt["id"],  # Original ID like S_T1_01
                "dimension": talent_id,
                "text": stmt["text"],
                "social_desirability": 4.5,  # Default neutral
                "context": "work",
                "factor_loading": 0.75,  # Default good loading
                "discrimination": 1.0,
                "difficulty": 0.0,
                "is_calibrated": 0,
                "calibration_version": "v4_2025",
                "complexity": stmt.get("complexity", "medium"),
                "behavioral_focus": stmt.get("behavioral_focus", "general"),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            statements.append(statement)
            current_id += 1

    return statements

def save_to_file_storage(statements):
    """保存到 file storage 格式"""
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    file_storage_dir = project_root / "data" / "file_storage"

    # Ensure directory exists
    file_storage_dir.mkdir(parents=True, exist_ok=True)

    # Save JSON format
    json_path = file_storage_dir / "v4_statements.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(statements, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(statements)} statements to {json_path}")

    # Save CSV format
    csv_path = file_storage_dir / "v4_statements.csv"
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        if statements:
            fieldnames = statements[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(statements)

    print(f"✅ Saved {len(statements)} statements to {csv_path}")

    return len(statements)

def validate_statement_distribution(statements):
    """驗證語句分布是否平衡"""
    dimension_counts = {}
    for stmt in statements:
        dim = stmt["dimension"]
        dimension_counts[dim] = dimension_counts.get(dim, 0) + 1

    print("\n📊 語句分布驗證:")
    total = 0
    for dim in sorted(dimension_counts.keys()):
        count = dimension_counts[dim]
        total += count
        status = "✅" if count == 10 else "❌"
        print(f"  {status} {dim}: {count} 語句")

    print(f"\n總計: {total} 語句")

    # Check if all dimensions have 10 statements
    is_balanced = all(count == 10 for count in dimension_counts.values())
    target_total = 120  # 12 dimensions × 10 statements

    if is_balanced and total == target_total:
        print("✅ 語句庫完全平衡！每維度10語句，總計120語句")
        return True
    else:
        print(f"❌ 語句庫不平衡！目標：{target_total}語句，實際：{total}語句")
        return False

def main():
    """主函數"""
    print("🔄 開始同步 statement_bank.json 到 file storage...")

    # Load statement bank
    statement_bank = load_statement_bank()
    if not statement_bank:
        print("❌ 無法載入 statement_bank.json")
        return False

    # Convert to file storage format
    statements = convert_to_file_storage_format(statement_bank)
    if not statements:
        print("❌ 轉換失敗")
        return False

    # Validate distribution
    is_balanced = validate_statement_distribution(statements)

    # Save to file storage
    saved_count = save_to_file_storage(statements)

    print(f"\n🎯 同步完成:")
    print(f"  - 處理語句: {saved_count}")
    print(f"  - 平衡狀態: {'✅ 完美平衡' if is_balanced else '❌ 需要調整'}")
    print(f"  - 預期題組: {saved_count // 4} 個題組")

    return is_balanced

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)