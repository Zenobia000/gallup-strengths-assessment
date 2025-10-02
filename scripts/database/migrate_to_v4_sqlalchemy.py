#!/usr/bin/env python3
"""
Database Migration to V4 SQLAlchemy
從舊 SQLite 實現遷移到統一 SQLAlchemy + V4 支援

執行步驟：
1. 備份現有資料庫
2. 分析現有資料
3. 初始化新的 SQLAlchemy 結構
4. 提供回滾選項

使用方法：
    python scripts/database/migrate_to_v4_sqlalchemy.py [--dry-run] [--backup-only]

設計原則：Never break userspace - 確保資料安全
"""

import sys
import os
import shutil
import logging
from datetime import datetime
from pathlib import Path
import argparse

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root / "src" / "main" / "python"))

from core.config import get_settings


def setup_logging():
    """設置日誌"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        ]
    )
    return logging.getLogger(__name__)


class DatabaseMigration:
    """資料庫遷移管理器"""

    def __init__(self, dry_run: bool = False):
        self.logger = setup_logging()
        self.dry_run = dry_run
        self.settings = get_settings()
        self.backup_dir = Path("backups") / f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 原始資料庫路徑
        self.old_db_path = Path(self.settings.database_url.replace("sqlite:///", ""))

        self.logger.info(f"Migration initialized - Dry run: {dry_run}")
        self.logger.info(f"Database path: {self.old_db_path}")

    def backup_existing_database(self) -> bool:
        """備份現有資料庫"""
        try:
            if not self.old_db_path.exists():
                self.logger.info("No existing database found - clean installation")
                return True

            # 建立備份目錄
            self.backup_dir.mkdir(parents=True, exist_ok=True)

            # 備份資料庫檔案
            backup_path = self.backup_dir / "database_backup.sqlite"

            if not self.dry_run:
                shutil.copy2(self.old_db_path, backup_path)

            self.logger.info(f"Database backed up to: {backup_path}")

            # 備份相關檔案
            related_files = [
                self.old_db_path.with_suffix('.sqlite-wal'),
                self.old_db_path.with_suffix('.sqlite-shm')
            ]

            for file_path in related_files:
                if file_path.exists():
                    backup_file = self.backup_dir / file_path.name
                    if not self.dry_run:
                        shutil.copy2(file_path, backup_file)
                    self.logger.info(f"Backed up: {file_path.name}")

            return True

        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            return False

    def analyze_existing_data(self) -> dict:
        """分析現有資料"""
        analysis = {
            "tables": {},
            "total_records": 0,
            "has_data": False
        }

        if not self.old_db_path.exists():
            self.logger.info("No existing database to analyze")
            return analysis

        try:
            import sqlite3
            with sqlite3.connect(str(self.old_db_path)) as conn:
                cursor = conn.cursor()

                # 獲取所有資料表
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()

                for (table_name,) in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    analysis["tables"][table_name] = count
                    analysis["total_records"] += count

                analysis["has_data"] = analysis["total_records"] > 0

                self.logger.info(f"Found {len(tables)} tables with {analysis['total_records']} total records")
                for table, count in analysis["tables"].items():
                    self.logger.info(f"  {table}: {count} records")

        except Exception as e:
            self.logger.error(f"Data analysis failed: {e}")

        return analysis

    def initialize_new_database(self) -> bool:
        """初始化新的 SQLAlchemy 資料庫"""
        try:
            if self.dry_run:
                self.logger.info("DRY RUN: Would initialize new SQLAlchemy database")
                return True

            # 刪除舊資料庫
            if self.old_db_path.exists():
                self.old_db_path.unlink()
                self.logger.info("Old database removed")

            # 清理 WAL 和 SHM 檔案
            for suffix in ['.sqlite-wal', '.sqlite-shm']:
                wal_file = self.old_db_path.with_suffix(suffix)
                if wal_file.exists():
                    wal_file.unlink()
                    self.logger.info(f"Removed {wal_file.name}")

            # 初始化新的資料庫系統
            from database.engine import init_database
            engine = init_database(force_recreate=True)

            # 驗證新資料庫
            health = engine.health_check()
            if health["status"] == "healthy":
                self.logger.info("New SQLAlchemy database initialized successfully")
                self.logger.info(f"Tables created: {health['table_count']}")
                return True
            else:
                self.logger.error(f"New database health check failed: {health}")
                return False

        except Exception as e:
            self.logger.error(f"New database initialization failed: {e}")
            return False

    def create_rollback_script(self):
        """建立回滾腳本"""
        rollback_script = self.backup_dir / "rollback.py"

        script_content = f'''#!/usr/bin/env python3
"""
Rollback script for database migration

This script restores the database to its pre-migration state.
Generated on: {datetime.now().isoformat()}
"""

import sys
import shutil
from pathlib import Path

def rollback():
    """Restore database from backup"""
    backup_db = Path("{self.backup_dir}/database_backup.sqlite")
    target_db = Path("{self.old_db_path}")

    if backup_db.exists():
        # Remove current database
        if target_db.exists():
            target_db.unlink()

        # Restore backup
        shutil.copy2(backup_db, target_db)
        print(f"Database restored from {{backup_db}}")

        # Restore WAL and SHM files if they exist
        for suffix in ['.sqlite-wal', '.sqlite-shm']:
            backup_file = Path("{self.backup_dir}/database_backup{{suffix}}")
            target_file = target_db.with_suffix(suffix)

            if backup_file.exists():
                shutil.copy2(backup_file, target_file)
                print(f"Restored {{target_file.name}}")
    else:
        print("No backup found!")
        return False

    print("Rollback completed successfully")
    return True

if __name__ == "__main__":
    rollback()
'''

        if not self.dry_run:
            rollback_script.write_text(script_content)
            rollback_script.chmod(0o755)

        self.logger.info(f"Rollback script created: {rollback_script}")

    def run_migration(self) -> bool:
        """執行完整遷移"""
        self.logger.info("="*60)
        self.logger.info("Starting Database Migration to V4 SQLAlchemy")
        self.logger.info("="*60)

        # 步驟 1: 備份
        self.logger.info("Step 1: Backing up existing database...")
        if not self.backup_existing_database():
            self.logger.error("Backup failed - aborting migration")
            return False

        # 步驟 2: 分析現有資料
        self.logger.info("Step 2: Analyzing existing data...")
        analysis = self.analyze_existing_data()

        if analysis["has_data"]:
            self.logger.warning(f"Found {analysis['total_records']} existing records")
            self.logger.warning("These will be LOST in the migration!")

            if not self.dry_run:
                confirm = input("Continue with migration? (yes/no): ")
                if confirm.lower() != 'yes':
                    self.logger.info("Migration aborted by user")
                    return False

        # 步驟 3: 初始化新資料庫
        self.logger.info("Step 3: Initializing new SQLAlchemy database...")
        if not self.initialize_new_database():
            self.logger.error("New database initialization failed")
            return False

        # 步驟 4: 建立回滾腳本
        self.logger.info("Step 4: Creating rollback script...")
        self.create_rollback_script()

        self.logger.info("="*60)
        self.logger.info("Migration completed successfully!")
        self.logger.info(f"Backup location: {self.backup_dir}")
        self.logger.info(f"Rollback script: {self.backup_dir}/rollback.py")
        self.logger.info("="*60)

        return True


def main():
    """主程式"""
    parser = argparse.ArgumentParser(description="Migrate to V4 SQLAlchemy Database")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--backup-only", action="store_true", help="Only backup the database")

    args = parser.parse_args()

    migration = DatabaseMigration(dry_run=args.dry_run)

    if args.backup_only:
        print("Backup-only mode")
        success = migration.backup_existing_database()
        print(f"Backup {'successful' if success else 'failed'}")
        return 0 if success else 1

    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")

    success = migration.run_migration()

    if success:
        if not args.dry_run:
            print("\\n🎉 Migration completed successfully!")
            print("\\n⚠️  IMPORTANT:")
            print("1. Test your application thoroughly")
            print("2. Keep the backup until you're confident everything works")
            print(f"3. Use the rollback script if needed: {migration.backup_dir}/rollback.py")
        return 0
    else:
        print("\\n❌ Migration failed!")
        print("Check the logs for details")
        return 1


if __name__ == "__main__":
    sys.exit(main())