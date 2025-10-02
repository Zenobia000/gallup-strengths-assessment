"""
Migration 004: V4.0 Thurstonian IRT Tables

Creates database tables for the v4.0 forced-choice assessment system.
"""

def up(conn):
    """Apply migration - create v4 tables"""

    # V4 Sessions table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS v4_sessions (
            session_id TEXT PRIMARY KEY,
            blocks_data TEXT NOT NULL,  -- JSON array of blocks
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # V4 Assessment Results table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS v4_assessment_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            responses TEXT NOT NULL,      -- JSON array of responses
            theta_scores TEXT NOT NULL,   -- JSON object of dimension -> theta
            norm_scores TEXT,              -- JSON object of normative scores
            profile TEXT,                  -- JSON strength profile
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES v4_sessions(session_id)
        )
    """)

    # V4 Calibration Data table (for storing calibration samples)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS v4_calibration_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            response_data TEXT NOT NULL,  -- JSON response data
            block_data TEXT NOT NULL,      -- JSON block configuration
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # V4 Parameters table (for storing calibrated IRT parameters)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS v4_parameters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parameter_set TEXT NOT NULL,   -- JSON of all parameters
            calibration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sample_size INTEGER,
            iterations INTEGER,
            converged BOOLEAN,
            log_likelihood REAL
        )
    """)

    # Create indices for performance
    conn.execute("CREATE INDEX IF NOT EXISTS idx_v4_sessions_created ON v4_sessions(created_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_v4_results_session ON v4_assessment_results(session_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_v4_results_completed ON v4_assessment_results(completed_at)")

    conn.commit()
    print("Migration 004: V4.0 Thurstonian IRT tables created successfully")


def down(conn):
    """Rollback migration - drop v4 tables"""

    conn.execute("DROP INDEX IF EXISTS idx_v4_results_completed")
    conn.execute("DROP INDEX IF EXISTS idx_v4_results_session")
    conn.execute("DROP INDEX IF EXISTS idx_v4_sessions_created")

    conn.execute("DROP TABLE IF EXISTS v4_parameters")
    conn.execute("DROP TABLE IF EXISTS v4_calibration_data")
    conn.execute("DROP TABLE IF EXISTS v4_assessment_results")
    conn.execute("DROP TABLE IF EXISTS v4_sessions")

    conn.commit()
    print("Migration 004: V4.0 Thurstonian IRT tables removed")