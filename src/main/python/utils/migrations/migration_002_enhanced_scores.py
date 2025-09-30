"""
Migration 002: Enhanced Scores Schema
Migrates from simple scores table to enhanced scores table with quality metrics and provenance.
"""

def apply_migration(conn):
    """Apply migration 002 - Enhanced Scores Schema"""

    # First, backup existing scores table if it exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scores_backup AS
        SELECT * FROM scores
    """)

    # Drop the old scores table
    conn.execute("DROP TABLE IF EXISTS scores")

    # Create the new enhanced scores table matching SQLAlchemy models
    conn.execute("""
        CREATE TABLE scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,

            -- Big Five raw scores (4-28 for 7-point scale)
            raw_scores TEXT NOT NULL,

            -- Standardized scores (0-100)
            standardized_scores TEXT NOT NULL,

            -- Percentiles (0-100)
            percentiles TEXT NOT NULL,

            -- Scoring quality indicators
            confidence_level TEXT NOT NULL CHECK(confidence_level IN ('high', 'medium', 'low')),
            quality_flags TEXT,
            scoring_confidence REAL,

            -- Scoring metadata
            scoring_version TEXT NOT NULL,
            computation_time_ms REAL NOT NULL,
            norms_version TEXT NOT NULL DEFAULT 'taiwan_2025',

            -- Strengths profile (optional)
            strengths_profile TEXT,
            top_strengths TEXT,

            -- Timestamps
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
    """)

    # Create indices for performance
    conn.execute("CREATE INDEX IF NOT EXISTS idx_scores_session_id ON scores(session_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_scores_confidence ON scores(confidence_level)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_scores_created ON scores(created_at)")

    # Record migration
    conn.execute("""
        INSERT INTO migrations (version, description)
        VALUES ('002', 'Enhanced scores schema with quality metrics and provenance')
    """)

    print(" Migration 002: Enhanced scores schema applied successfully")