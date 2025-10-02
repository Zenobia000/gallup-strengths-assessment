#!/usr/bin/env python3
"""
Export SQLite database to CSV/JSON files for file-based storage system
"""

import sqlite3
import json
import csv
import os
from pathlib import Path
from datetime import datetime
import pandas as pd

def export_database_to_files():
    """Export all database tables to CSV and JSON files"""

    # Paths
    db_path = "/home/os-sunnie.gd.weng/python_workstation/side-project/strength-system/data/gallup_assessment.db"
    export_dir = "/home/os-sunnie.gd.weng/python_workstation/side-project/strength-system/data/file_storage"

    # Create export directory
    Path(export_dir).mkdir(exist_ok=True)

    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # This enables column access by name

    # Get all table names
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    print(f"Found {len(tables)} tables to export")

    export_summary = {
        "export_timestamp": datetime.now().isoformat(),
        "source_database": db_path,
        "tables_exported": {}
    }

    for table_name in tables:
        print(f"\nExporting table: {table_name}")

        # Read table data
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        if not rows:
            print(f"  - Table {table_name} is empty, skipping")
            continue

        # Convert to list of dictionaries
        data = [dict(row) for row in rows]

        # Export to JSON
        json_path = f"{export_dir}/{table_name}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        # Export to CSV
        csv_path = f"{export_dir}/{table_name}.csv"
        if data:
            df = pd.DataFrame(data)
            df.to_csv(csv_path, index=False, encoding='utf-8')

        export_summary["tables_exported"][table_name] = {
            "rows_count": len(data),
            "json_file": json_path,
            "csv_file": csv_path
        }

        print(f"  - Exported {len(data)} rows to JSON and CSV")

    # Save export summary
    summary_path = f"{export_dir}/export_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(export_summary, f, indent=2, ensure_ascii=False)

    conn.close()

    print(f"\n✅ Export completed!")
    print(f"📁 Files saved to: {export_dir}")
    print(f"📊 Export summary: {summary_path}")

    return export_summary

if __name__ == "__main__":
    try:
        summary = export_database_to_files()
        print("\n" + "="*50)
        print("EXPORT SUMMARY")
        print("="*50)
        for table, info in summary["tables_exported"].items():
            print(f"{table}: {info['rows_count']} rows")
    except Exception as e:
        print(f"❌ Export failed: {e}")
        import traceback
        traceback.print_exc()