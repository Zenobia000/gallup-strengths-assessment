#!/usr/bin/env python3
"""
Migration 003: Situational Questions Support

Extends the assessment_items table to support situational questions
with custom response options and multi-dimensional scoring.

Author: Gallup Assessment System
Date: 2025-09-30
"""

import sqlite3
import json
from typing import Dict, Any


def apply_migration(conn: sqlite3.Connection) -> None:
    """
    Apply migration 003: Add situational questions support.

    Args:
        conn: SQLite database connection
    """

    # 1. Add new columns to assessment_items table
    try:
        conn.execute("ALTER TABLE assessment_items ADD COLUMN question_type TEXT DEFAULT 'traditional'")
    except sqlite3.OperationalError:
        pass  # Column already exists

    try:
        conn.execute("ALTER TABLE assessment_items ADD COLUMN scenario_context TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    try:
        conn.execute("ALTER TABLE assessment_items ADD COLUMN response_options TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    try:
        conn.execute("ALTER TABLE assessment_items ADD COLUMN dimension_weights TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # 2. Create index for efficient querying by question type
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_question_type
        ON assessment_items(question_type)
    """)

    # 3. Update existing traditional questions
    conn.execute("""
        UPDATE assessment_items
        SET question_type = 'traditional'
        WHERE question_type IS NULL
    """)

    # 4. Create situational questions table for complex scenarios
    conn.execute("""
        CREATE TABLE IF NOT EXISTS situational_scenarios (
            scenario_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            context_type TEXT NOT NULL,  -- 'workplace', 'social', 'stress', etc.
            difficulty_level INTEGER DEFAULT 1,  -- 1-5 complexity rating
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            version TEXT DEFAULT 'v1.0'
        )
    """)

    # 5. Seed initial situational questions
    seed_situational_questions(conn)

    # 6. Record migration
    conn.execute("""
        INSERT OR REPLACE INTO migrations (version, applied_at, description)
        VALUES ('003', datetime('now'), 'Add situational questions support')
    """)


def seed_situational_questions(conn: sqlite3.Connection) -> None:
    """
    Seed database with initial situational questions.

    Args:
        conn: SQLite database connection
    """

    # Define situational scenarios
    scenarios = [
        {
            "scenario_id": "workplace_001",
            "title": "會議衝突處理",
            "description": "在重要專案會議中，兩位同事對於解決方案產生激烈爭執",
            "context_type": "workplace",
            "difficulty_level": 2
        },
        {
            "scenario_id": "social_001",
            "title": "團隊聚餐安排",
            "description": "部門要舉辦季度聚餐，需要有人負責籌劃和協調",
            "context_type": "social",
            "difficulty_level": 1
        },
        {
            "scenario_id": "stress_001",
            "title": "緊急專案交付",
            "description": "客戶突然要求提前一週交付重要專案，團隊壓力很大",
            "context_type": "stress",
            "difficulty_level": 3
        }
    ]

    # Insert scenarios
    for scenario in scenarios:
        conn.execute("""
            INSERT OR IGNORE INTO situational_scenarios
            (scenario_id, title, description, context_type, difficulty_level)
            VALUES (?, ?, ?, ?, ?)
        """, (
            scenario["scenario_id"],
            scenario["title"],
            scenario["description"],
            scenario["context_type"],
            scenario["difficulty_level"]
        ))

    # Define situational questions with multi-dimensional weights
    situational_items = [
        {
            "item_id": "sit_001",
            "instrument_version": "mini_ipip_v1.0",
            "item_order": 21,
            "question_type": "situational",
            "scenario_context": "workplace_001",
            "text_chinese": "在這種情況下，你最可能採取什麼行動？",
            "text_english": "In this situation, what action would you most likely take?",
            "dimension": "mixed",  # Multi-dimensional
            "reverse_scored": False,
            "response_options": json.dumps([
                {
                    "value": 1,
                    "text": "立即介入調解，嘗試找出雙方共識",
                    "dimensions": {"extraversion": 0.7, "agreeableness": 0.8, "conscientiousness": 0.5}
                },
                {
                    "value": 2,
                    "text": "建議先暫停討論，各自冷靜後再繼續",
                    "dimensions": {"conscientiousness": 0.8, "neuroticism": -0.4, "agreeableness": 0.3}
                },
                {
                    "value": 3,
                    "text": "保持中立，讓主管或會議主持人處理",
                    "dimensions": {"neuroticism": 0.2, "extraversion": -0.3, "conscientiousness": 0.4}
                },
                {
                    "value": 4,
                    "text": "提出創新的第三種解決方案",
                    "dimensions": {"openness": 0.9, "extraversion": 0.6, "conscientiousness": 0.7}
                }
            ]),
            "dimension_weights": json.dumps({
                "extraversion": 0.3,
                "agreeableness": 0.4,
                "conscientiousness": 0.2,
                "neuroticism": 0.1,
                "openness": 0.2
            })
        },
        {
            "item_id": "sit_002",
            "instrument_version": "mini_ipip_v1.0",
            "item_order": 22,
            "question_type": "situational",
            "scenario_context": "social_001",
            "text_chinese": "關於籌劃團隊聚餐，你的參與程度會是？",
            "text_english": "Regarding organizing the team gathering, your level of involvement would be?",
            "dimension": "mixed",
            "reverse_scored": False,
            "response_options": json.dumps([
                {
                    "value": 1,
                    "text": "主動承擔主要籌劃責任",
                    "dimensions": {"extraversion": 0.9, "conscientiousness": 0.8, "agreeableness": 0.6}
                },
                {
                    "value": 2,
                    "text": "願意協助但不想當主負責人",
                    "dimensions": {"agreeableness": 0.7, "conscientiousness": 0.6, "extraversion": 0.3}
                },
                {
                    "value": 3,
                    "text": "參與討論提供意見和建議",
                    "dimensions": {"openness": 0.6, "agreeableness": 0.5, "extraversion": 0.4}
                },
                {
                    "value": 4,
                    "text": "等待安排通知即可",
                    "dimensions": {"extraversion": -0.4, "neuroticism": 0.2, "conscientiousness": -0.2}
                }
            ]),
            "dimension_weights": json.dumps({
                "extraversion": 0.5,
                "agreeableness": 0.3,
                "conscientiousness": 0.3,
                "neuroticism": 0.1,
                "openness": 0.2
            })
        },
        {
            "item_id": "sit_003",
            "instrument_version": "mini_ipip_v1.0",
            "item_order": 23,
            "question_type": "situational",
            "scenario_context": "stress_001",
            "text_chinese": "面對突如其來的時間壓力，你的第一反應是？",
            "text_english": "When faced with sudden time pressure, your first reaction is?",
            "dimension": "mixed",
            "reverse_scored": False,
            "response_options": json.dumps([
                {
                    "value": 1,
                    "text": "立即制定詳細的行動計劃和時程",
                    "dimensions": {"conscientiousness": 0.9, "neuroticism": -0.3, "openness": 0.4}
                },
                {
                    "value": 2,
                    "text": "和團隊開會討論如何重新分配工作",
                    "dimensions": {"extraversion": 0.6, "agreeableness": 0.7, "conscientiousness": 0.5}
                },
                {
                    "value": 3,
                    "text": "感到焦慮但努力保持冷靜",
                    "dimensions": {"neuroticism": 0.6, "conscientiousness": 0.4, "agreeableness": 0.2}
                },
                {
                    "value": 4,
                    "text": "尋找創新方法來提升效率",
                    "dimensions": {"openness": 0.8, "conscientiousness": 0.6, "extraversion": 0.3}
                }
            ]),
            "dimension_weights": json.dumps({
                "extraversion": 0.2,
                "agreeableness": 0.2,
                "conscientiousness": 0.4,
                "neuroticism": 0.3,
                "openness": 0.3
            })
        }
    ]

    # Insert situational items
    for item in situational_items:
        conn.execute("""
            INSERT OR IGNORE INTO assessment_items
            (item_id, instrument_version, item_order, question_type, scenario_context,
             text_chinese, text_english, dimension, reverse_scored,
             response_options, dimension_weights)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item["item_id"],
            item["instrument_version"],
            item["item_order"],
            item["question_type"],
            item["scenario_context"],
            item["text_chinese"],
            item["text_english"],
            item["dimension"],
            item["reverse_scored"],
            item["response_options"],
            item["dimension_weights"]
        ))


def rollback_migration(conn: sqlite3.Connection) -> None:
    """
    Rollback migration 003.

    Args:
        conn: SQLite database connection
    """

    # Remove added columns (SQLite doesn't support DROP COLUMN directly)
    # Instead, we mark them as deprecated in the migration record
    conn.execute("""
        UPDATE migrations
        SET description = description || ' [ROLLED BACK]'
        WHERE version = '003'
    """)

    # Drop situational scenarios table
    conn.execute("DROP TABLE IF EXISTS situational_scenarios")

    # Remove situational questions
    conn.execute("""
        DELETE FROM assessment_items
        WHERE question_type = 'situational'
    """)


if __name__ == "__main__":
    # Test migration
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        test_db = tmp.name

    try:
        conn = sqlite3.connect(test_db)

        # Create minimal schema for testing
        conn.execute("""
            CREATE TABLE assessment_items (
                item_id TEXT PRIMARY KEY,
                instrument_version TEXT,
                item_order INTEGER,
                text_chinese TEXT,
                text_english TEXT,
                dimension TEXT,
                reverse_scored BOOLEAN
            )
        """)

        conn.execute("""
            CREATE TABLE migrations (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMP,
                description TEXT
            )
        """)

        # Apply migration
        apply_migration(conn)

        # Verify
        cursor = conn.execute("SELECT COUNT(*) FROM assessment_items WHERE question_type = 'situational'")
        count = cursor.fetchone()[0]
        print(f"✅ Migration 003 applied successfully. Added {count} situational questions.")

        conn.close()

    finally:
        os.unlink(test_db)