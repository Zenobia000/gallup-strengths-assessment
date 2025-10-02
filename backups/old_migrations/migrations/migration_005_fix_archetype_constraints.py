"""
Migration 005: Fix Archetype Foreign Key Constraints

修復職業原型系統的外鍵約束問題：
- 移除對 sessions/assessment_sessions 的強依賴
- 允許直接使用 v4_sessions 中的 session_id
- 確保職業原型分析能正常運作
"""

def apply_migration(conn):
    """Apply migration 005: Fix archetype constraints"""

    # 1. 移除現有的 user_archetype_results 表（如果存在）
    conn.execute("DROP TABLE IF EXISTS user_archetype_results")

    # 2. 重新建立沒有嚴格外鍵約束的版本
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_archetype_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,  -- 移除外鍵約束，允許任何有效的 session_id
            primary_archetype_id TEXT NOT NULL,
            secondary_archetype_id TEXT,
            archetype_scores TEXT NOT NULL,  -- JSON object with all 4 scores
            dominant_talents TEXT NOT NULL,  -- JSON array
            supporting_talents TEXT NOT NULL,  -- JSON array
            lesser_talents TEXT NOT NULL,  -- JSON array
            confidence_score REAL NOT NULL,
            analysis_metadata TEXT,  -- JSON object
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (primary_archetype_id) REFERENCES career_archetypes(archetype_id),
            FOREIGN KEY (secondary_archetype_id) REFERENCES career_archetypes(archetype_id),
            CONSTRAINT valid_confidence CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
            CONSTRAINT unique_session_result UNIQUE (session_id)
        )
    """)

    # 3. 同樣處理 job_recommendations 表
    conn.execute("DROP TABLE IF EXISTS job_recommendations")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS job_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,  -- 移除外鍵約束
            role_id TEXT NOT NULL,
            recommendation_type TEXT NOT NULL,  -- primary, stretch, development
            match_score REAL NOT NULL,
            strength_alignment TEXT NOT NULL,  -- JSON object
            development_gaps TEXT,  -- JSON array
            recommendation_reasoning TEXT NOT NULL,  -- JSON object
            priority_rank INTEGER NOT NULL,
            confidence_level REAL NOT NULL,
            is_featured BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (role_id) REFERENCES job_roles(role_id),
            CONSTRAINT valid_recommendation_type CHECK (recommendation_type IN ('primary', 'stretch', 'development')),
            CONSTRAINT valid_match_score CHECK (match_score >= 0.0 AND match_score <= 1.0),
            CONSTRAINT valid_confidence CHECK (confidence_level >= 0.0 AND confidence_level <= 1.0),
            CONSTRAINT unique_session_role UNIQUE (session_id, role_id)
        )
    """)

    # 4. 重新建立索引
    conn.execute("CREATE INDEX IF NOT EXISTS idx_user_results_session ON user_archetype_results(session_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_job_recommendations_session ON job_recommendations(session_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_job_recommendations_score ON job_recommendations(match_score DESC)")

    # 5. 記錄遷移完成
    conn.execute("""
        INSERT INTO migrations (version, description)
        VALUES ('005', 'Fix Archetype Foreign Key Constraints for v4 compatibility')
    """)

    print("✅ Migration 005: 職業原型外鍵約束修復完成")