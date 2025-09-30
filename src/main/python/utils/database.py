"""
Database Utilities and Connection Management - Gallup Strengths Assessment

Implements SQLite database management following Linus Torvalds principles:
- Simple and pragmatic (SQLite for MVP)
- Fail-fast on errors
- Clean separation of concerns
- No unnecessary abstraction layers

Provides connection management, schema initialization, and basic CRUD operations.
"""

import sqlite3
import json
import os
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from core.config import get_settings


class DatabaseError(Exception):
    """Custom database error for better error handling."""
    pass


class DatabaseManager:
    """
    SQLite database manager with connection pooling and schema management.

    Implements the Repository pattern for clean data access.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database manager.

        Args:
            db_path: Database file path (optional, uses config default)
        """
        settings = get_settings()
        if db_path is None:
            # Extract path from database URL (sqlite:///./data/...)
            db_path = settings.database_url.replace("sqlite:///", "")

        self.db_path = Path(db_path)
        self.ensure_database_directory()
        self.initialize_schema()

    def ensure_database_directory(self):
        """Create database directory if it doesn't exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.

        Provides automatic connection cleanup and error handling.
        Uses WAL mode for better concurrent performance.
        """
        conn = None
        try:
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=30.0,  # 30 second timeout
                isolation_level=None  # Autocommit mode
            )

            # Configure SQLite for better performance
            conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
            conn.execute("PRAGMA synchronous=NORMAL")  # Balanced performance/safety
            conn.execute("PRAGMA cache_size=10000")  # 10MB cache
            conn.execute("PRAGMA foreign_keys=ON")  # Enable foreign key constraints

            # Set row factory for easier data access
            conn.row_factory = sqlite3.Row

            yield conn

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Database error: {e}")

        finally:
            if conn:
                conn.close()

    def initialize_schema(self):
        """
        Initialize database schema with all required tables.

        Creates tables following the architecture document specifications.
        """
        with self.get_connection() as conn:
            # Consent management table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS consents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    consent_id TEXT UNIQUE NOT NULL,
                    agreed BOOLEAN NOT NULL,
                    user_agent TEXT NOT NULL,
                    ip_address TEXT,
                    consent_version TEXT NOT NULL DEFAULT 'v1.0',
                    agreed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                    CONSTRAINT valid_consent_id CHECK (length(consent_id) > 0),
                    CONSTRAINT valid_expiry CHECK (expires_at > agreed_at)
                )
            """)

            # Assessment sessions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    consent_id TEXT NOT NULL,
                    instrument_version TEXT NOT NULL DEFAULT 'mini_ipip_v1.0',
                    status TEXT NOT NULL DEFAULT 'PENDING',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME NOT NULL,
                    completed_at DATETIME,
                    metadata JSON,

                    FOREIGN KEY (consent_id) REFERENCES consents(consent_id),
                    CONSTRAINT valid_session_id CHECK (length(session_id) > 0),
                    CONSTRAINT valid_status CHECK (status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'EXPIRED')),
                    CONSTRAINT valid_expiry CHECK (expires_at > created_at)
                )
            """)

            # Assessment responses table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    item_id TEXT NOT NULL,
                    response INTEGER NOT NULL,
                    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
                    CONSTRAINT valid_likert_response CHECK (response >= 1 AND response <= 7),
                    CONSTRAINT unique_session_item UNIQUE (session_id, item_id)
                )
            """)

            # Scores table for computed results
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,

                    -- Big Five scores (0-100)
                    extraversion INTEGER CHECK(extraversion >= 0 AND extraversion <= 100),
                    agreeableness INTEGER CHECK(agreeableness >= 0 AND agreeableness <= 100),
                    conscientiousness INTEGER CHECK(conscientiousness >= 0 AND conscientiousness <= 100),
                    neuroticism INTEGER CHECK(neuroticism >= 0 AND neuroticism <= 100),
                    openness INTEGER CHECK(openness >= 0 AND openness <= 100),
                    honesty_humility INTEGER CHECK(honesty_humility >= 0 AND honesty_humility <= 100),

                    -- 12 strength facets (JSON)
                    strength_scores JSON NOT NULL,

                    -- Provenance and metadata
                    provenance JSON NOT NULL,
                    algorithm_version TEXT NOT NULL,
                    weights_version TEXT NOT NULL,
                    calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """)

            # Assessment items (seed data)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS assessment_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id TEXT UNIQUE NOT NULL,
                    instrument_version TEXT NOT NULL,
                    item_order INTEGER NOT NULL,
                    text_chinese TEXT NOT NULL,
                    text_english TEXT,
                    dimension TEXT NOT NULL,
                    reverse_scored BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                    CONSTRAINT valid_order CHECK (item_order > 0),
                    CONSTRAINT unique_item_order UNIQUE (instrument_version, item_order)
                )
            """)

            # Create indices for better query performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_consent_id ON sessions(consent_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_responses_session_id ON responses(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_scores_session_id ON scores(session_id)")

            # Seed data within the same connection/transaction
            self.seed_assessment_items(conn)

        # Apply migrations after schema and seeding are completed
        self.apply_migrations()

    def apply_migrations(self):
        """Apply any pending database migrations."""
        try:
            from utils.migrations.migration_002_enhanced_scores import apply_migration

            with self.get_connection() as conn:
                # Check if migration 002 has been applied
                cursor = conn.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name='migrations'
                """)

                if cursor.fetchone():
                    cursor = conn.execute("""
                        SELECT version FROM migrations
                        WHERE version = '002'
                    """)
                    if not cursor.fetchone():
                        apply_migration(conn)
                else:
                    apply_migration(conn)

        except ImportError:
            # Migration file doesn't exist yet, skip
            pass
        except Exception as e:
            print(f"Migration error: {e}")

    def seed_assessment_items(self, conn=None):
        """
        Seed the database with Mini-IPIP assessment items.

        Uses the standard 20-item Mini-IPIP with Chinese translations.

        Args:
            conn: Optional database connection to use. If None, creates new connection.
        """
        items = [
            # Extraversion items (E)
            ("ipip_001", "mini_ipip_v1.0", 1, "我是聚會的核心人物", "I am the life of the party", "extraversion", False),
            ("ipip_002", "mini_ipip_v1.0", 2, "我不太愛說話", "I don't talk a lot", "extraversion", True),
            ("ipip_003", "mini_ipip_v1.0", 3, "我很容易和陌生人交談", "I feel comfortable around people", "extraversion", False),
            ("ipip_004", "mini_ipip_v1.0", 4, "我不喜歡引起注意", "I keep in the background", "extraversion", True),

            # Agreeableness items (A)
            ("ipip_005", "mini_ipip_v1.0", 5, "我對他人的需求很敏感", "I feel others' emotions", "agreeableness", False),
            ("ipip_006", "mini_ipip_v1.0", 6, "我對別人的問題不感興趣", "I'm not interested in other people's problems", "agreeableness", True),
            ("ipip_007", "mini_ipip_v1.0", 7, "我喜歡幫助別人", "I feel others' emotions", "agreeableness", False),
            ("ipip_008", "mini_ipip_v1.0", 8, "我對別人的感受漠不關心", "I'm not interested in other people's problems", "agreeableness", True),

            # Conscientiousness items (C)
            ("ipip_009", "mini_ipip_v1.0", 9, "我總是做好準備", "I am always prepared", "conscientiousness", False),
            ("ipip_010", "mini_ipip_v1.0", 10, "我經常忘記把東西放回原位", "I leave my belongings around", "conscientiousness", True),
            ("ipip_011", "mini_ipip_v1.0", 11, "我很注意細節", "I pay attention to details", "conscientiousness", False),
            ("ipip_012", "mini_ipip_v1.0", 12, "我把事情搞得一團糟", "I make a mess of things", "conscientiousness", True),

            # Neuroticism items (N)
            ("ipip_013", "mini_ipip_v1.0", 13, "我經常感到沮喪", "I get stressed out easily", "neuroticism", False),
            ("ipip_014", "mini_ipip_v1.0", 14, "我很少感到憂鬱", "I am relaxed most of the time", "neuroticism", True),
            ("ipip_015", "mini_ipip_v1.0", 15, "我容易被打擾", "I worry about things", "neuroticism", False),
            ("ipip_016", "mini_ipip_v1.0", 16, "我在壓力下很冷靜", "I seldom feel blue", "neuroticism", True),

            # Openness items (O)
            ("ipip_017", "mini_ipip_v1.0", 17, "我有豐富的想像力", "I have a rich vocabulary", "openness", False),
            ("ipip_018", "mini_ipip_v1.0", 18, "我很少做白日夢", "I have difficulty understanding abstract ideas", "openness", True),
            ("ipip_019", "mini_ipip_v1.0", 19, "我有很好的想法", "I have excellent ideas", "openness", False),
            ("ipip_020", "mini_ipip_v1.0", 20, "我不善於抽象思維", "I do not have a good imagination", "openness", True),
        ]

        def _seed_with_connection(conn_to_use):
            # Check if items already exist
            cursor = conn_to_use.execute("SELECT COUNT(*) FROM assessment_items WHERE instrument_version = ?", ("mini_ipip_v1.0",))
            count = cursor.fetchone()[0]

            if count == 0:
                conn_to_use.executemany("""
                    INSERT INTO assessment_items
                    (item_id, instrument_version, item_order, text_chinese, text_english, dimension, reverse_scored)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, items)

        if conn is not None:
            # Use the provided connection (from schema initialization)
            _seed_with_connection(conn)
        else:
            # Create a new connection
            with self.get_connection() as new_conn:
                _seed_with_connection(new_conn)

    # CRUD Operations
    def create_consent(self, consent_data: Dict[str, Any]) -> str:
        """Create a new consent record."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO consents (consent_id, agreed, user_agent, ip_address, consent_version, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                consent_data["consent_id"],
                consent_data["agreed"],
                consent_data["user_agent"],
                consent_data.get("ip_address"),
                consent_data["consent_version"],
                consent_data["expires_at"]
            ))
            return consent_data["consent_id"]

    def create_session(self, session_data: Dict[str, Any]) -> str:
        """Create a new assessment session."""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO sessions (session_id, consent_id, instrument_version, status, expires_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_data["session_id"],
                session_data["consent_id"],
                session_data["instrument_version"],
                session_data["status"],
                session_data["expires_at"],
                json.dumps(session_data.get("metadata", {}))
            ))
            return session_data["session_id"]

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM sessions WHERE session_id = ?
            """, (session_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def get_assessment_items(self, instrument_version: str = "mini_ipip_v1.0") -> List[Dict[str, Any]]:
        """Get assessment items for given instrument version."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM assessment_items
                WHERE instrument_version = ?
                ORDER BY item_order
            """, (instrument_version,))
            return [dict(row) for row in cursor.fetchall()]

    def save_responses(self, session_id: str, responses: List[Dict[str, Any]]):
        """Save assessment responses."""
        with self.get_connection() as conn:
            # Update session status
            conn.execute("""
                UPDATE sessions SET status = 'COMPLETED', completed_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (session_id,))

            # Save individual responses
            response_data = [
                (session_id, resp["item_id"], resp["response"])
                for resp in responses
            ]

            conn.executemany("""
                INSERT INTO responses (session_id, item_id, response)
                VALUES (?, ?, ?)
            """, response_data)

    def save_scores(self, session_id: str, scores_data: Dict[str, Any]):
        """Save computed scores."""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO scores
                (session_id, extraversion, agreeableness, conscientiousness,
                 neuroticism, openness, honesty_humility, strength_scores,
                 provenance, algorithm_version, weights_version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                scores_data["extraversion"],
                scores_data["agreeableness"],
                scores_data["conscientiousness"],
                scores_data["neuroticism"],
                scores_data["openness"],
                scores_data["honesty_humility"],
                json.dumps(scores_data["strength_scores"]),
                json.dumps(scores_data["provenance"]),
                scores_data["algorithm_version"],
                scores_data["weights_version"]
            ))

    def save_enhanced_scores(self, session_id: str, scores_data: Dict[str, Any]):
        """Save enhanced scores with quality metrics and provenance."""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO scores
                (session_id, extraversion, agreeableness, conscientiousness,
                 neuroticism, openness, honesty_humility, strength_scores,
                 provenance, algorithm_version, weights_version,
                 scoring_confidence, response_quality_flags, raw_scores,
                 percentiles, processing_time_ms, local_norms_version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                scores_data["extraversion"],
                scores_data["agreeableness"],
                scores_data["conscientiousness"],
                scores_data["neuroticism"],
                scores_data["openness"],
                scores_data["honesty_humility"],
                json.dumps(scores_data["strength_scores"]),
                json.dumps(scores_data["provenance"]),
                scores_data["algorithm_version"],
                scores_data["weights_version"],
                scores_data["scoring_confidence"],
                json.dumps(scores_data["response_quality_flags"]),
                json.dumps(scores_data["raw_scores"]),
                json.dumps(scores_data["percentiles"]),
                scores_data["processing_time_ms"],
                scores_data.get("local_norms_version", "v1.0")
            ))

    def get_enhanced_scores(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get enhanced scores with all quality metrics."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM scores WHERE session_id = ?
            """, (session_id,))
            row = cursor.fetchone()
            if row:
                result = dict(row)
                # Parse JSON fields
                if result.get("strength_scores"):
                    result["strength_scores"] = json.loads(result["strength_scores"])
                if result.get("provenance"):
                    result["provenance"] = json.loads(result["provenance"])
                if result.get("response_quality_flags"):
                    result["response_quality_flags"] = json.loads(result["response_quality_flags"])
                if result.get("raw_scores"):
                    result["raw_scores"] = json.loads(result["raw_scores"])
                if result.get("percentiles"):
                    result["percentiles"] = json.loads(result["percentiles"])
                return result
            return None

    def get_normative_data(self, version: str = "literature_v1.0") -> Dict[str, Dict[str, float]]:
        """Get normative data for score standardization."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT factor, mean_score, std_deviation
                FROM normative_data
                WHERE version = ?
            """, (version,))

            norms = {}
            for row in cursor.fetchall():
                norms[row["factor"]] = {
                    "mean": row["mean_score"],
                    "std": row["std_deviation"]
                }

            return norms

    def update_normative_data(self, version: str, factor: str, sample_size: int,
                            mean_score: float, std_deviation: float,
                            metadata: Optional[Dict] = None):
        """Update normative data with new population statistics."""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO normative_data
                (version, factor, sample_size, mean_score, std_deviation,
                 updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
            """, (
                version, factor, sample_size, mean_score, std_deviation,
                json.dumps(metadata or {})
            ))

    def get_responses_for_session(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all responses for a session."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT item_id, response, submitted_at
                FROM responses
                WHERE session_id = ?
                ORDER BY submitted_at
            """, (session_id,))
            return [dict(row) for row in cursor.fetchall()]


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """Get or create database manager singleton."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


@contextmanager
def get_db_connection():
    """Convenience function for getting database connection."""
    db_manager = get_database_manager()
    with db_manager.get_connection() as conn:
        yield conn