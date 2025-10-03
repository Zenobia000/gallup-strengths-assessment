#!/usr/bin/env python3
"""
Rollback script for database migration

This script restores the database to its pre-migration state.
Generated on: 2025-10-02T11:00:50.125867
"""

import sys
import shutil
from pathlib import Path

def rollback():
    """Restore database from backup"""
    backup_db = Path("backups/migration_20251002_110049/database_backup.sqlite")
    target_db = Path("data/gallup_assessment.db")

    if backup_db.exists():
        # Remove current database
        if target_db.exists():
            target_db.unlink()

        # Restore backup
        shutil.copy2(backup_db, target_db)
        print(f"Database restored from {backup_db}")

        # Restore WAL and SHM files if they exist
        for suffix in ['.sqlite-wal', '.sqlite-shm']:
            backup_file = Path("backups/migration_20251002_110049/database_backup{suffix}")
            target_file = target_db.with_suffix(suffix)

            if backup_file.exists():
                shutil.copy2(backup_file, target_file)
                print(f"Restored {target_file.name}")
    else:
        print("No backup found!")
        return False

    print("Rollback completed successfully")
    return True

if __name__ == "__main__":
    rollback()
