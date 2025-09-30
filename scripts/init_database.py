#!/usr/bin/env python3
"""
Gallup Strengths Assessment System - Database Initialization Script
===================================================================

This script provides comprehensive database initialization and management capabilities:
- Database creation and schema setup
- Seed data loading with validation
- Health checks and diagnostics
- Data migration utilities
- TTL cleanup and maintenance
- GDPR compliance utilities

Usage:
    python init_database.py [command] [options]

Commands:
    init        - Initialize database with schema and seed data
    schema      - Create schema only
    seed        - Load seed data only
    health      - Check database health
    cleanup     - Run TTL cleanup
    reset       - Drop and recreate database
    validate    - Validate database integrity
    export      - Export data for backup
    migrate     - Run data migrations

Options:
    --force     - Force operation (skip confirmations)
    --backup    - Create backup before destructive operations
    --verbose   - Verbose output
    --dry-run   - Show what would be done without executing
"""

import os
import sys
import sqlite3
import asyncio
import argparse
import json
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
import asyncio
import aiosqlite

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import get_settings
from app.core.database import sync_engine, async_engine, get_sync_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(project_root / 'logs' / 'database_init.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

settings = get_settings()


class DatabaseInitializer:
    """Comprehensive database initialization and management."""

    def __init__(self, database_path: Optional[str] = None, verbose: bool = False):
        self.database_path = database_path or settings.database_sync_url.replace('sqlite:///', '')
        self.verbose = verbose
        self.schema_path = project_root / 'src' / 'main' / 'resources' / 'database' / 'schema.sql'
        self.seed_data_path = project_root / 'src' / 'main' / 'resources' / 'database' / 'seed_data.sql'

        # Ensure logs directory exists
        (project_root / 'logs').mkdir(exist_ok=True)

        if verbose:
            logger.setLevel(logging.DEBUG)

    def _log(self, message: str, level: str = 'info') -> None:
        """Log message with appropriate level."""
        if level == 'debug' and self.verbose:
            logger.debug(message)
        elif level == 'info':
            logger.info(message)
        elif level == 'warning':
            logger.warning(message)
        elif level == 'error':
            logger.error(message)

    def _execute_sql_file(self, conn: sqlite3.Connection, file_path: Path) -> None:
        """Execute SQL file with proper error handling."""
        if not file_path.exists():
            raise FileNotFoundError(f"SQL file not found: {file_path}")

        self._log(f"Executing SQL file: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        try:
            # Use executescript for better handling of complex SQL
            conn.executescript(sql_content)
            self._log(f"Successfully executed SQL script from {file_path.name}")
        except sqlite3.Error as e:
            self._log(f"Error executing SQL script: {e}", 'error')
            raise

    def create_database(self) -> None:
        """Create database file and directory if they don't exist."""
        db_path = Path(self.database_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        if not db_path.exists():
            self._log(f"Creating database file: {db_path}")
            db_path.touch()
        else:
            self._log(f"Database file already exists: {db_path}")

    def initialize_schema(self, force: bool = False) -> bool:
        """Initialize database schema."""
        try:
            self.create_database()

            with sqlite3.connect(self.database_path) as conn:
                # Check if schema already exists
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='assessment_sessions'"
                )
                if cursor.fetchone() and not force:
                    self._log("Schema already exists. Use --force to recreate.")
                    return False

                # Execute schema
                self._execute_sql_file(conn, self.schema_path)

                # Verify schema creation
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                )
                tables = [row[0] for row in cursor.fetchall()]

                expected_tables = [
                    'assessment_configurations', 'assessment_responses', 'assessment_sessions',
                    'audit_trails', 'consent_records', 'gallup_strengths',
                    'privacy_requests', 'questions', 'question_sets', 'strength_scores'
                ]

                missing_tables = set(expected_tables) - set(tables)
                if missing_tables:
                    raise Exception(f"Missing tables after schema creation: {missing_tables}")

                self._log(f"Schema initialized successfully. Created {len(tables)} tables.")
                return True

        except Exception as e:
            self._log(f"Failed to initialize schema: {e}", 'error')
            raise

    def load_seed_data(self, force: bool = False) -> bool:
        """Load seed data into database."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                # Check if seed data already exists
                cursor = conn.execute("SELECT COUNT(*) FROM gallup_strengths")
                existing_strengths = cursor.fetchone()[0]

                if existing_strengths > 0 and not force:
                    self._log(f"Seed data already exists ({existing_strengths} strengths). Use --force to reload.")
                    return False

                # Clear existing data if force is enabled
                if force and existing_strengths > 0:
                    self._log("Clearing existing seed data...")
                    tables_to_clear = [
                        'question_sets', 'assessment_configurations',
                        'questions', 'gallup_strengths'
                    ]
                    for table in tables_to_clear:
                        conn.execute(f"DELETE FROM {table}")
                    conn.commit()

                # Load seed data
                self._execute_sql_file(conn, self.seed_data_path)

                # Verify seed data
                cursor = conn.execute("SELECT COUNT(*) FROM gallup_strengths")
                strengths_count = cursor.fetchone()[0]

                cursor = conn.execute("SELECT COUNT(*) FROM questions")
                questions_count = cursor.fetchone()[0]

                cursor = conn.execute("SELECT COUNT(*) FROM assessment_configurations")
                configs_count = cursor.fetchone()[0]

                if strengths_count != 34:
                    raise Exception(f"Expected 34 strengths, found {strengths_count}")
                if questions_count != 50:
                    raise Exception(f"Expected 50 questions, found {questions_count}")
                if configs_count != 4:
                    raise Exception(f"Expected 4 configurations, found {configs_count}")

                self._log(f"Seed data loaded successfully:")
                self._log(f"  - {strengths_count} Gallup strengths")
                self._log(f"  - {questions_count} assessment questions")
                self._log(f"  - {configs_count} assessment configurations")
                return True

        except Exception as e:
            self._log(f"Failed to load seed data: {e}", 'error')
            raise

    def check_health(self) -> Dict[str, Any]:
        """Comprehensive database health check."""
        health_status = {
            'database_exists': False,
            'schema_valid': False,
            'seed_data_complete': False,
            'performance_ok': False,
            'compliance_features': False,
            'issues': [],
            'recommendations': []
        }

        try:
            # Check database exists and is accessible
            if not Path(self.database_path).exists():
                health_status['issues'].append("Database file does not exist")
                return health_status

            health_status['database_exists'] = True

            with sqlite3.connect(self.database_path) as conn:
                # Check schema
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
                tables = set(row[0] for row in cursor.fetchall())

                expected_tables = {
                    'assessment_sessions', 'consent_records', 'assessment_responses',
                    'strength_scores', 'audit_trails', 'privacy_requests',
                    'gallup_strengths', 'questions', 'assessment_configurations',
                    'question_sets'
                }

                missing_tables = expected_tables - tables
                if missing_tables:
                    health_status['issues'].append(f"Missing tables: {missing_tables}")
                else:
                    health_status['schema_valid'] = True

                # Check seed data
                cursor = conn.execute("SELECT COUNT(*) FROM gallup_strengths")
                strengths_count = cursor.fetchone()[0]

                cursor = conn.execute("SELECT COUNT(*) FROM questions")
                questions_count = cursor.fetchone()[0]

                if strengths_count == 34 and questions_count == 50:
                    health_status['seed_data_complete'] = True
                else:
                    health_status['issues'].append(
                        f"Incomplete seed data: {strengths_count}/34 strengths, {questions_count}/50 questions"
                    )

                # Check performance indexes
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='index'"
                )
                indexes = set(row[0] for row in cursor.fetchall())

                key_indexes = {
                    'idx_session_status', 'idx_response_session', 'idx_audit_session_action_time'
                }
                missing_indexes = key_indexes - indexes
                if missing_indexes:
                    health_status['issues'].append(f"Missing performance indexes: {missing_indexes}")
                else:
                    health_status['performance_ok'] = True

                # Check compliance features
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='trigger'"
                )
                triggers = set(row[0] for row in cursor.fetchall())

                compliance_triggers = {
                    'audit_session_changes', 'audit_new_response', 'audit_consent_records'
                }
                missing_triggers = compliance_triggers - triggers
                if missing_triggers:
                    health_status['issues'].append(f"Missing compliance triggers: {missing_triggers}")
                else:
                    health_status['compliance_features'] = True

                # Check for expired data (TTL compliance)
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM assessment_sessions
                    WHERE expires_at < datetime('now')
                """)
                expired_sessions = cursor.fetchone()[0]

                if expired_sessions > 0:
                    health_status['recommendations'].append(
                        f"Found {expired_sessions} expired sessions. Consider running TTL cleanup."
                    )

                # Check database size and performance
                cursor = conn.execute("PRAGMA page_count")
                page_count = cursor.fetchone()[0]

                cursor = conn.execute("PRAGMA page_size")
                page_size = cursor.fetchone()[0]

                db_size_mb = (page_count * page_size) / (1024 * 1024)
                if db_size_mb > 100:  # 100MB threshold
                    health_status['recommendations'].append(
                        f"Database size is {db_size_mb:.1f}MB. Consider archiving old data."
                    )

        except Exception as e:
            health_status['issues'].append(f"Health check error: {e}")

        return health_status

    def cleanup_expired_data(self, dry_run: bool = False) -> Dict[str, int]:
        """Clean up expired data according to TTL policies."""
        cleanup_results = {
            'expired_sessions': 0,
            'expired_responses': 0,
            'expired_scores': 0,
            'expired_consent': 0,
            'audit_records_created': 0
        }

        try:
            with sqlite3.connect(self.database_path) as conn:
                current_time = datetime.now().isoformat()

                # Find expired data
                tables_with_ttl = [
                    ('assessment_sessions', 'expires_at'),
                    ('assessment_responses', 'ttl_expires_at'),
                    ('strength_scores', 'ttl_expires_at'),
                    ('consent_records', 'ttl_expires_at')
                ]

                for table, ttl_column in tables_with_ttl:
                    cursor = conn.execute(f"""
                        SELECT COUNT(*) FROM {table}
                        WHERE {ttl_column} < datetime('now')
                    """)
                    expired_count = cursor.fetchone()[0]

                    if expired_count > 0:
                        if not dry_run:
                            # Create audit record before deletion
                            conn.execute("""
                                INSERT INTO audit_trails (
                                    action_type, entity_type, entity_id,
                                    old_values, timestamp
                                ) VALUES (?, ?, ?, ?, ?)
                            """, (
                                'data_deleted', 'system', f'ttl_cleanup_{table}',
                                json.dumps({
                                    'expired_count': expired_count,
                                    'cleanup_time': current_time,
                                    'reason': 'ttl_expiration'
                                }),
                                current_time
                            ))
                            cleanup_results['audit_records_created'] += 1

                            # Delete expired data
                            conn.execute(f"""
                                DELETE FROM {table}
                                WHERE {ttl_column} < datetime('now')
                            """)
                            conn.commit()

                        cleanup_results[f'expired_{table.split("_")[1]}'] = expired_count

                self._log(f"TTL cleanup completed. Results: {cleanup_results}")

        except Exception as e:
            self._log(f"TTL cleanup failed: {e}", 'error')
            raise

        return cleanup_results

    def validate_integrity(self) -> Dict[str, Any]:
        """Validate database integrity and constraints."""
        validation_results = {
            'foreign_key_violations': [],
            'data_consistency_issues': [],
            'constraint_violations': [],
            'orphaned_records': [],
            'valid': True
        }

        try:
            with sqlite3.connect(self.database_path) as conn:
                # Enable foreign key checking
                conn.execute("PRAGMA foreign_keys = ON")

                # Check foreign key integrity
                cursor = conn.execute("PRAGMA foreign_key_check")
                fk_violations = cursor.fetchall()
                if fk_violations:
                    validation_results['foreign_key_violations'] = [
                        {
                            'table': row[0],
                            'rowid': row[1],
                            'parent': row[2],
                            'fkid': row[3]
                        }
                        for row in fk_violations
                    ]
                    validation_results['valid'] = False

                # Check for orphaned assessment responses
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM assessment_responses ar
                    LEFT JOIN assessment_sessions ass ON ar.session_id = ass.session_id
                    WHERE ass.session_id IS NULL
                """)
                orphaned_responses = cursor.fetchone()[0]
                if orphaned_responses > 0:
                    validation_results['orphaned_records'].append(
                        f"{orphaned_responses} orphaned assessment responses"
                    )
                    validation_results['valid'] = False

                # Check for orphaned strength scores
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM strength_scores ss
                    LEFT JOIN assessment_sessions ass ON ss.session_id = ass.session_id
                    WHERE ass.session_id IS NULL
                """)
                orphaned_scores = cursor.fetchone()[0]
                if orphaned_scores > 0:
                    validation_results['orphaned_records'].append(
                        f"{orphaned_scores} orphaned strength scores"
                    )
                    validation_results['valid'] = False

                # Check data consistency
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM assessment_sessions
                    WHERE expires_at <= created_at
                """)
                invalid_expiry = cursor.fetchone()[0]
                if invalid_expiry > 0:
                    validation_results['data_consistency_issues'].append(
                        f"{invalid_expiry} sessions with invalid expiry dates"
                    )
                    validation_results['valid'] = False

                # Check constraint violations
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM assessment_sessions
                    WHERE status NOT IN ('created', 'active', 'completed', 'expired', 'abandoned')
                """)
                invalid_status = cursor.fetchone()[0]
                if invalid_status > 0:
                    validation_results['constraint_violations'].append(
                        f"{invalid_status} sessions with invalid status"
                    )
                    validation_results['valid'] = False

        except Exception as e:
            validation_results['valid'] = False
            validation_results['error'] = str(e)
            self._log(f"Validation failed: {e}", 'error')

        return validation_results

    def create_backup(self, backup_path: Optional[str] = None) -> str:
        """Create database backup."""
        if not backup_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{self.database_path}.backup_{timestamp}"

        try:
            import shutil
            shutil.copy2(self.database_path, backup_path)
            self._log(f"Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            self._log(f"Backup failed: {e}", 'error')
            raise

    def reset_database(self, force: bool = False, backup: bool = True) -> None:
        """Reset database (drop and recreate)."""
        if not force:
            response = input("This will delete all data. Are you sure? (yes/no): ")
            if response.lower() != 'yes':
                self._log("Reset cancelled.")
                return

        try:
            if backup and Path(self.database_path).exists():
                self.create_backup()

            # Remove existing database
            if Path(self.database_path).exists():
                Path(self.database_path).unlink()
                self._log("Existing database removed.")

            # Reinitialize
            self.initialize_schema(force=True)
            self.load_seed_data(force=True)

            self._log("Database reset completed successfully.")

        except Exception as e:
            self._log(f"Database reset failed: {e}", 'error')
            raise

    async def test_async_operations(self) -> bool:
        """Test async database operations."""
        try:
            # Test async connection
            async with aiosqlite.connect(self.database_path) as db:
                await db.execute("SELECT 1")
                cursor = await db.execute("SELECT COUNT(*) FROM gallup_strengths")
                result = await cursor.fetchone()
                strengths_count = result[0] if result else 0

                self._log(f"Async test successful. Found {strengths_count} strengths.")
                return strengths_count == 34

        except Exception as e:
            self._log(f"Async test failed: {e}", 'error')
            return False


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Gallup Strengths Assessment Database Initialization Tool"
    )

    parser.add_argument(
        'command',
        choices=['init', 'schema', 'seed', 'health', 'cleanup', 'reset', 'validate', 'export', 'test'],
        help='Command to execute'
    )

    parser.add_argument('--force', action='store_true', help='Force operation')
    parser.add_argument('--backup', action='store_true', help='Create backup before destructive operations')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    parser.add_argument('--database', help='Database path (optional)')

    args = parser.parse_args()

    # Initialize the database manager
    db_init = DatabaseInitializer(args.database, args.verbose)

    try:
        if args.command == 'init':
            print("🚀 Initializing Gallup Strengths Assessment Database...")
            db_init.initialize_schema(args.force)
            db_init.load_seed_data(args.force)
            print("✅ Database initialization completed successfully!")

        elif args.command == 'schema':
            print("📋 Creating database schema...")
            db_init.initialize_schema(args.force)
            print("✅ Schema creation completed!")

        elif args.command == 'seed':
            print("🌱 Loading seed data...")
            db_init.load_seed_data(args.force)
            print("✅ Seed data loaded successfully!")

        elif args.command == 'health':
            print("🩺 Running database health check...")
            health = db_init.check_health()

            print(f"📊 Health Status:")
            print(f"  Database exists: {'✅' if health['database_exists'] else '❌'}")
            print(f"  Schema valid: {'✅' if health['schema_valid'] else '❌'}")
            print(f"  Seed data complete: {'✅' if health['seed_data_complete'] else '❌'}")
            print(f"  Performance OK: {'✅' if health['performance_ok'] else '❌'}")
            print(f"  Compliance features: {'✅' if health['compliance_features'] else '❌'}")

            if health['issues']:
                print(f"\n⚠️ Issues found:")
                for issue in health['issues']:
                    print(f"  - {issue}")

            if health['recommendations']:
                print(f"\n💡 Recommendations:")
                for rec in health['recommendations']:
                    print(f"  - {rec}")

            if not health['issues']:
                print("\n🎉 Database is healthy!")

        elif args.command == 'cleanup':
            print("🧹 Running TTL cleanup...")
            results = db_init.cleanup_expired_data(args.dry_run)

            if args.dry_run:
                print("📋 Cleanup preview (dry-run):")
            else:
                print("✅ Cleanup completed:")

            for key, count in results.items():
                if count > 0:
                    print(f"  - {key}: {count}")

        elif args.command == 'reset':
            print("🔄 Resetting database...")
            db_init.reset_database(args.force, args.backup)
            print("✅ Database reset completed!")

        elif args.command == 'validate':
            print("🔍 Validating database integrity...")
            validation = db_init.validate_integrity()

            if validation['valid']:
                print("✅ Database integrity is valid!")
            else:
                print("❌ Database integrity issues found:")

                for category, issues in validation.items():
                    if isinstance(issues, list) and issues:
                        print(f"\n{category}:")
                        for issue in issues:
                            print(f"  - {issue}")

        elif args.command == 'test':
            print("🧪 Testing database operations...")

            # Test sync operations
            health = db_init.check_health()
            sync_ok = health['database_exists'] and health['schema_valid']
            print(f"Sync operations: {'✅' if sync_ok else '❌'}")

            # Test async operations
            async_ok = asyncio.run(db_init.test_async_operations())
            print(f"Async operations: {'✅' if async_ok else '❌'}")

            if sync_ok and async_ok:
                print("🎉 All tests passed!")
            else:
                print("❌ Some tests failed. Check logs for details.")
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Operation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()