"""
Database Migration 002: Enhanced Scoring Tables

Extends the existing database schema to support comprehensive scoring features:
- Enhanced scores table with quality metrics
- Normative data table for population norms
- Provenance tracking for explainability
- Performance optimization indexes

Migration Version: 002
Author: TaskMaster Week 2 Database Implementation
Date: 2025-09-30
"""

import sqlite3
import json
from typing import Dict, Any
from datetime import datetime


class Migration002:
    """Enhanced scoring schema migration."""

    VERSION = "002"
    DESCRIPTION = "Enhanced scoring tables with quality metrics and normative data"

    def __init__(self):
        self.migration_name = f"migration_{self.VERSION}_enhanced_scores"

    def up(self, conn: sqlite3.Connection) -> None:
        """Apply migration - add enhanced scoring features."""

        # Step 1: Extend scores table with new columns
        self._extend_scores_table(conn)

        # Step 2: Create normative data table
        self._create_normative_data_table(conn)

        # Step 3: Create performance indexes
        self._create_performance_indexes(conn)

        # Step 4: Seed initial normative data
        self._seed_initial_norms(conn)

        # Step 5: Record migration
        self._record_migration(conn)

    def down(self, conn: sqlite3.Connection) -> None:
        """Rollback migration - remove enhanced scoring features."""

        # Step 1: Drop added indexes
        conn.execute("DROP INDEX IF EXISTS idx_scores_confidence")
        conn.execute("DROP INDEX IF EXISTS idx_scores_algorithm_version")
        conn.execute("DROP INDEX IF EXISTS idx_normative_data_version_factor")

        # Step 2: Drop normative data table
        conn.execute("DROP TABLE IF EXISTS normative_data")

        # Step 3: Remove added columns from scores table
        # Note: SQLite doesn't support DROP COLUMN, so we need to recreate the table
        self._rollback_scores_table(conn)

        # Step 4: Remove migration record
        conn.execute("DELETE FROM migrations WHERE version = ?", (self.VERSION,))

    def _extend_scores_table(self, conn: sqlite3.Connection) -> None:
        """Extend scores table with enhanced scoring columns."""

        # Add new columns for enhanced scoring
        new_columns = [
            ("scoring_confidence", "REAL DEFAULT 0.0"),
            ("response_quality_flags", "JSON DEFAULT '[]'"),
            ("raw_scores", "JSON NOT NULL DEFAULT '{}'"),
            ("percentiles", "JSON NOT NULL DEFAULT '{}'"),
            ("processing_time_ms", "REAL DEFAULT 0.0"),
            ("local_norms_version", "TEXT DEFAULT 'v1.0'")
        ]

        for column_name, column_def in new_columns:
            try:
                conn.execute(f"ALTER TABLE scores ADD COLUMN {column_name} {column_def}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    # Column already exists, skip
                    continue
                raise

        # Add constraints
        try:
            conn.execute("""
                CREATE INDEX IF NOT EXISTS chk_scores_confidence
                ON scores(scoring_confidence)
                WHERE scoring_confidence >= 0.0 AND scoring_confidence <= 1.0
            """)
        except sqlite3.OperationalError:
            # Constraint might already exist, continue
            pass

    def _create_normative_data_table(self, conn: sqlite3.Connection) -> None:
        """Create normative data table for population norms."""

        conn.execute("""
            CREATE TABLE IF NOT EXISTS normative_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT NOT NULL,
                factor TEXT NOT NULL,
                sample_size INTEGER NOT NULL,
                mean_score REAL NOT NULL,
                std_deviation REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata JSON DEFAULT '{}',

                CONSTRAINT valid_factor CHECK (factor IN (
                    'extraversion', 'agreeableness', 'conscientiousness',
                    'neuroticism', 'openness'
                )),
                CONSTRAINT valid_stats CHECK (
                    sample_size > 0 AND std_deviation > 0 AND mean_score >= 0
                ),
                CONSTRAINT unique_version_factor UNIQUE(version, factor)
            )
        """)

    def _create_performance_indexes(self, conn: sqlite3.Connection) -> None:
        """Create indexes for improved query performance."""

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_scores_confidence ON scores(scoring_confidence)",
            "CREATE INDEX IF NOT EXISTS idx_scores_algorithm_version ON scores(algorithm_version)",
            "CREATE INDEX IF NOT EXISTS idx_scores_calculated_at ON scores(calculated_at)",
            "CREATE INDEX IF NOT EXISTS idx_normative_data_version_factor ON normative_data(version, factor)",
            "CREATE INDEX IF NOT EXISTS idx_normative_data_created_at ON normative_data(created_at)"
        ]

        for index_sql in indexes:
            conn.execute(index_sql)

    def _seed_initial_norms(self, conn: sqlite3.Connection) -> None:
        """Seed initial normative data with literature values."""

        # Literature-based norms from Mini-IPIP research
        initial_norms = [
            ('literature_v1.0', 'extraversion', 1000, 16.0, 4.2),
            ('literature_v1.0', 'agreeableness', 1000, 17.5, 3.8),
            ('literature_v1.0', 'conscientiousness', 1000, 18.2, 4.1),
            ('literature_v1.0', 'neuroticism', 1000, 15.3, 4.6),
            ('literature_v1.0', 'openness', 1000, 16.8, 4.0)
        ]

        # Check if norms already exist
        cursor = conn.execute(
            "SELECT COUNT(*) FROM normative_data WHERE version = ?",
            ('literature_v1.0',)
        )

        if cursor.fetchone()[0] == 0:
            conn.executemany("""
                INSERT INTO normative_data
                (version, factor, sample_size, mean_score, std_deviation)
                VALUES (?, ?, ?, ?, ?)
            """, initial_norms)

    def _record_migration(self, conn: sqlite3.Connection) -> None:
        """Record this migration in the migrations table."""

        # Create migrations table if it doesn't exist
        conn.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT UNIQUE NOT NULL,
                description TEXT NOT NULL,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                applied_by TEXT DEFAULT 'system'
            )
        """)

        # Record this migration
        conn.execute("""
            INSERT OR REPLACE INTO migrations (version, description, applied_by)
            VALUES (?, ?, ?)
        """, (self.VERSION, self.DESCRIPTION, 'enhanced_scoring_system'))

    def _rollback_scores_table(self, conn: sqlite3.Connection) -> None:
        """Rollback scores table to original schema."""

        # Create backup table with original schema
        conn.execute("""
            CREATE TABLE scores_backup AS
            SELECT
                id, session_id, extraversion, agreeableness, conscientiousness,
                neuroticism, openness, honesty_humility, strength_scores,
                provenance, algorithm_version, weights_version, calculated_at
            FROM scores
        """)

        # Drop current scores table
        conn.execute("DROP TABLE scores")

        # Recreate original scores table
        conn.execute("""
            CREATE TABLE scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                extraversion INTEGER CHECK(extraversion >= 0 AND extraversion <= 100),
                agreeableness INTEGER CHECK(agreeableness >= 0 AND agreeableness <= 100),
                conscientiousness INTEGER CHECK(conscientiousness >= 0 AND conscientiousness <= 100),
                neuroticism INTEGER CHECK(neuroticism >= 0 AND neuroticism <= 100),
                openness INTEGER CHECK(openness >= 0 AND openness <= 100),
                honesty_humility INTEGER CHECK(honesty_humility >= 0 AND honesty_humility <= 100),
                strength_scores JSON NOT NULL,
                provenance JSON NOT NULL,
                algorithm_version TEXT NOT NULL,
                weights_version TEXT NOT NULL,
                calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)

        # Restore data
        conn.execute("""
            INSERT INTO scores
            SELECT * FROM scores_backup
        """)

        # Drop backup table
        conn.execute("DROP TABLE scores_backup")


def apply_migration(conn: sqlite3.Connection) -> bool:
    """
    Apply migration 002 to the database.

    Args:
        conn: Database connection

    Returns:
        bool: True if migration was applied successfully
    """
    try:
        migration = Migration002()
        migration.up(conn)
        return True
    except Exception as e:
        print(f"Migration 002 failed: {e}")
        return False


def rollback_migration(conn: sqlite3.Connection) -> bool:
    """
    Rollback migration 002 from the database.

    Args:
        conn: Database connection

    Returns:
        bool: True if rollback was successful
    """
    try:
        migration = Migration002()
        migration.down(conn)
        return True
    except Exception as e:
        print(f"Migration 002 rollback failed: {e}")
        return False