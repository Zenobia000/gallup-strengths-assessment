#!/usr/bin/env python3
"""
Run database migrations
"""

import sys
import os
import sqlite3
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src' / 'main' / 'python'))

def run_migration(migration_number: int):
    """Run a specific migration"""

    # Import migration module
    migration_name = f"migration_{migration_number:03d}_v4_thurstonian" if migration_number == 4 else f"migration_{migration_number:03d}"
    migration_module = __import__(f'utils.migrations.{migration_name}', fromlist=['up', 'down'])

    # Connect to database
    db_path = project_root / 'src' / 'main' / 'python' / 'data' / 'gallup_assessment.db'
    conn = sqlite3.connect(str(db_path))

    try:
        # Run migration
        print(f"Running migration {migration_number}...")
        migration_module.up(conn)
        print(f"Migration {migration_number} completed successfully")

    except Exception as e:
        print(f"Migration {migration_number} failed: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        migration_num = int(sys.argv[1])
        run_migration(migration_num)
    else:
        # Run migration 004 for v4 tables
        run_migration(4)