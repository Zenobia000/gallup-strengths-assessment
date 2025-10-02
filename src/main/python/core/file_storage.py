"""
File-based storage system for rapid development and testing
Replaces SQLAlchemy/SQLite with CSV/JSON files for flexibility
"""

import json
import csv
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import uuid
import os
from dataclasses import dataclass, asdict


@dataclass
class StorageConfig:
    """Configuration for file storage system"""
    base_path: str = "/home/os-sunnie.gd.weng/python_workstation/side-project/strength-system/data/file_storage"
    backup_enabled: bool = True
    auto_save: bool = True
    format_preference: str = "json"  # "json" or "csv"


class FileStorageManager:
    """
    File-based storage manager for rapid development
    Provides database-like operations using CSV/JSON files
    """

    def __init__(self, config: StorageConfig = None):
        self.config = config or StorageConfig()
        self.base_path = Path(self.config.base_path)
        self.base_path.mkdir(exist_ok=True)

        # In-memory cache for performance
        self._cache = {}
        self._cache_loaded = set()

    def _get_file_path(self, table_name: str, format_type: str = None) -> Path:
        """Get file path for a table"""
        format_type = format_type or self.config.format_preference
        return self.base_path / f"{table_name}.{format_type}"

    def _load_table(self, table_name: str) -> List[Dict[str, Any]]:
        """Load table data from file"""
        if table_name in self._cache_loaded:
            return self._cache.get(table_name, [])

        json_path = self._get_file_path(table_name, "json")
        csv_path = self._get_file_path(table_name, "csv")

        data = []

        # Try JSON first
        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load JSON {json_path}: {e}")

        # Fallback to CSV if JSON fails or doesn't exist
        elif csv_path.exists():
            try:
                df = pd.read_csv(csv_path)
                data = df.to_dict('records')
            except Exception as e:
                print(f"Warning: Failed to load CSV {csv_path}: {e}")

        # Cache the data
        self._cache[table_name] = data
        self._cache_loaded.add(table_name)

        return data

    def _save_table(self, table_name: str, data: List[Dict[str, Any]]):
        """Save table data to file"""
        if not data:
            data = []

        # Update cache
        self._cache[table_name] = data

        if not self.config.auto_save:
            return

        # Save to JSON
        json_path = self._get_file_path(table_name, "json")
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Error saving JSON {json_path}: {e}")

        # Save to CSV
        csv_path = self._get_file_path(table_name, "csv")
        try:
            if data:
                df = pd.DataFrame(data)
                df.to_csv(csv_path, index=False, encoding='utf-8')
        except Exception as e:
            print(f"Error saving CSV {csv_path}: {e}")

    def select_all(self, table_name: str) -> List[Dict[str, Any]]:
        """Select all records from a table"""
        return self._load_table(table_name)

    def select_by_id(self, table_name: str, id_field: str, id_value: Any) -> Optional[Dict[str, Any]]:
        """Select a record by ID"""
        data = self._load_table(table_name)
        for record in data:
            if str(record.get(id_field)) == str(id_value):
                return record
        return None

    def select_where(self, table_name: str, **conditions) -> List[Dict[str, Any]]:
        """Select records matching conditions"""
        data = self._load_table(table_name)
        results = []

        for record in data:
            match = True
            for key, value in conditions.items():
                if str(record.get(key)) != str(value):
                    match = False
                    break
            if match:
                results.append(record)

        return results

    def insert(self, table_name: str, record: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new record"""
        data = self._load_table(table_name)

        # Add timestamp and ID if not present
        if 'id' not in record:
            record['id'] = len(data) + 1
        if 'created_at' not in record:
            record['created_at'] = datetime.now().isoformat()
        if 'updated_at' not in record:
            record['updated_at'] = datetime.now().isoformat()

        data.append(record)
        self._save_table(table_name, data)

        return record

    def insert_many(self, table_name: str, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Insert multiple records"""
        data = self._load_table(table_name)

        for i, record in enumerate(records):
            if 'id' not in record:
                record['id'] = len(data) + i + 1
            if 'created_at' not in record:
                record['created_at'] = datetime.now().isoformat()
            if 'updated_at' not in record:
                record['updated_at'] = datetime.now().isoformat()

        data.extend(records)
        self._save_table(table_name, data)

        return records

    def update(self, table_name: str, id_field: str, id_value: Any, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a record"""
        data = self._load_table(table_name)

        for i, record in enumerate(data):
            if str(record.get(id_field)) == str(id_value):
                # Update the record
                data[i].update(updates)
                data[i]['updated_at'] = datetime.now().isoformat()

                self._save_table(table_name, data)
                return data[i]

        return None

    def delete(self, table_name: str, id_field: str, id_value: Any) -> bool:
        """Delete a record"""
        data = self._load_table(table_name)
        original_length = len(data)

        data[:] = [record for record in data if str(record.get(id_field)) != str(id_value)]

        if len(data) < original_length:
            self._save_table(table_name, data)
            return True

        return False

    def count(self, table_name: str, **conditions) -> int:
        """Count records matching conditions"""
        if conditions:
            return len(self.select_where(table_name, **conditions))
        else:
            return len(self._load_table(table_name))

    def create_session_id(self, prefix: str = "v4") -> str:
        """Generate a unique session ID"""
        return f"{prefix}_{uuid.uuid4().hex[:12]}"

    def backup_table(self, table_name: str) -> str:
        """Create a backup of a table"""
        if not self.config.backup_enabled:
            return ""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.base_path / "backups" / timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Copy current files
        for format_type in ["json", "csv"]:
            source_path = self._get_file_path(table_name, format_type)
            if source_path.exists():
                backup_path = backup_dir / f"{table_name}.{format_type}"
                import shutil
                shutil.copy2(source_path, backup_path)

        return str(backup_dir)

    def health_check(self) -> Dict[str, Any]:
        """Check system health"""
        try:
            tables = []
            for file_path in self.base_path.glob("*.json"):
                table_name = file_path.stem
                record_count = len(self._load_table(table_name))
                tables.append({
                    "name": table_name,
                    "records": record_count,
                    "file_size": file_path.stat().st_size
                })

            return {
                "status": "healthy",
                "storage_type": "file_based",
                "base_path": str(self.base_path),
                "table_count": len(tables),
                "tables": tables,
                "cache_loaded": list(self._cache_loaded)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# Global instance for easy access
storage = FileStorageManager()


def get_file_storage() -> FileStorageManager:
    """Get the global file storage instance"""
    return storage


# Initialize with existing data if available
def initialize_file_storage():
    """Initialize the file storage system with default data"""

    # Check if v4_statements exists, if not, create sample data
    if not storage.select_all("v4_statements"):
        print("Initializing file storage with sample data...")

        # This will be populated from existing JSON files
        sample_statements = []

        # Try to load from existing v4_statements.json
        existing_path = Path("/home/os-sunnie.gd.weng/python_workstation/side-project/strength-system/data/file_storage/v4_statements.json")
        if existing_path.exists():
            try:
                with open(existing_path, 'r', encoding='utf-8') as f:
                    sample_statements = json.load(f)
                print(f"Loaded {len(sample_statements)} statements from existing file")
            except Exception as e:
                print(f"Error loading existing statements: {e}")

        if sample_statements:
            storage.insert_many("v4_statements", sample_statements)

    print("✅ File storage system initialized!")


if __name__ == "__main__":
    # Test the file storage system
    initialize_file_storage()

    health = storage.health_check()
    print("File Storage Health Check:")
    print(json.dumps(health, indent=2, ensure_ascii=False))