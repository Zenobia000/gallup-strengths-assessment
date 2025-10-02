"""
V4.0 Test Data Collection System
Task 8.1.4: 小規模預測試設計 (n=100)

Collects and manages test data for IRT calibration.
Supports small-scale pilot testing and parameter estimation.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import numpy as np
import pandas as pd
from dataclasses import dataclass, asdict
import logging

from database.engine import get_database_engine

logger = logging.getLogger(__name__)


@dataclass
class TestParticipant:
    """Test participant information"""
    participant_id: str
    age: Optional[int]
    gender: Optional[str]
    education: Optional[str]
    test_group: str  # 'pilot', 'calibration', 'validation'
    created_at: datetime
    metadata: Dict[str, Any]


@dataclass
class TestSession:
    """Test session data"""
    session_id: str
    participant_id: str
    test_version: str  # 'v3' or 'v4'
    blocks_data: List[Dict]
    responses: List[Dict]
    completion_time_seconds: float
    started_at: datetime
    completed_at: datetime
    is_complete: bool
    quality_flags: Dict[str, Any]


class DataCollector:
    """
    Manages test data collection for v4.0 calibration.

    Responsibilities:
    1. Participant recruitment tracking
    2. Response data collection
    3. Data quality validation
    4. Export for calibration
    """

    def __init__(self, target_sample_size: int = 100):
        """
        Initialize data collector.

        Args:
            target_sample_size: Target number of participants
        """
        self.target_sample_size = target_sample_size
        self.db_engine = get_database_engine()
        self._init_tables()

    def _init_tables(self):
        """Initialize data collection tables"""
        with self.db_engine.get_session() as session:
            # Participants table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS v4_test_participants (
                    participant_id TEXT PRIMARY KEY,
                    age INTEGER,
                    gender TEXT,
                    education TEXT,
                    test_group TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)

            # Test sessions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS v4_test_sessions (
                    session_id TEXT PRIMARY KEY,
                    participant_id TEXT NOT NULL,
                    test_version TEXT NOT NULL,
                    blocks_data TEXT NOT NULL,
                    responses TEXT NOT NULL,
                    completion_time_seconds REAL,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    is_complete BOOLEAN DEFAULT FALSE,
                    quality_flags TEXT,
                    FOREIGN KEY (participant_id) REFERENCES v4_test_participants(participant_id)
                )
            """)

            # Create indices
            conn.execute("CREATE INDEX IF NOT EXISTS idx_test_sessions_participant ON v4_test_sessions(participant_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_test_sessions_complete ON v4_test_sessions(is_complete)")

            conn.commit()

    def register_participant(self,
                           age: Optional[int] = None,
                           gender: Optional[str] = None,
                           education: Optional[str] = None,
                           test_group: str = 'pilot',
                           **metadata) -> str:
        """
        Register a new test participant.

        Args:
            age: Participant age
            gender: Participant gender
            education: Education level
            test_group: Testing group ('pilot', 'calibration', 'validation')
            **metadata: Additional metadata

        Returns:
            Participant ID
        """
        participant_id = f"P{uuid.uuid4().hex[:8].upper()}"

        with self.db_engine.get_session() as session:
            conn.execute("""
                INSERT INTO v4_test_participants
                (participant_id, age, gender, education, test_group, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                participant_id,
                age,
                gender,
                education,
                test_group,
                json.dumps(metadata)
            ))
            conn.commit()

        logger.info(f"Registered participant {participant_id} in {test_group} group")
        return participant_id

    def start_test_session(self,
                          participant_id: str,
                          test_version: str,
                          blocks_data: List[Dict]) -> str:
        """
        Start a new test session.

        Args:
            participant_id: Participant ID
            test_version: Test version ('v3' or 'v4')
            blocks_data: Block configuration

        Returns:
            Session ID
        """
        session_id = f"TS{uuid.uuid4().hex[:8].upper()}"

        with self.db_engine.get_session() as session:
            conn.execute("""
                INSERT INTO v4_test_sessions
                (session_id, participant_id, test_version, blocks_data,
                 responses, started_at, is_complete)
                VALUES (?, ?, ?, ?, '[]', datetime('now'), FALSE)
            """, (
                session_id,
                participant_id,
                test_version,
                json.dumps(blocks_data)
            ))
            conn.commit()

        logger.info(f"Started {test_version} session {session_id} for participant {participant_id}")
        return session_id

    def save_responses(self,
                      session_id: str,
                      responses: List[Dict],
                      completion_time_seconds: float) -> bool:
        """
        Save test responses.

        Args:
            session_id: Session ID
            responses: Response data
            completion_time_seconds: Time to complete

        Returns:
            Success status
        """
        # Validate responses
        quality_flags = self._validate_responses(responses, completion_time_seconds)

        with self.db_engine.get_session() as session:
            conn.execute("""
                UPDATE v4_test_sessions
                SET responses = ?,
                    completion_time_seconds = ?,
                    completed_at = datetime('now'),
                    is_complete = TRUE,
                    quality_flags = ?
                WHERE session_id = ?
            """, (
                json.dumps(responses),
                completion_time_seconds,
                json.dumps(quality_flags),
                session_id
            ))
            conn.commit()

        logger.info(f"Saved responses for session {session_id}")
        return True

    def _validate_responses(self,
                           responses: List[Dict],
                           completion_time: float) -> Dict[str, Any]:
        """
        Validate response quality.

        Args:
            responses: Response data
            completion_time: Completion time in seconds

        Returns:
            Quality flags dictionary
        """
        flags = {
            'too_fast': False,
            'too_slow': False,
            'straight_lining': False,
            'missing_responses': False,
            'inconsistent_patterns': False,
            'quality_score': 1.0
        }

        # Check completion time (expected: 10-30 minutes)
        if completion_time < 300:  # Less than 5 minutes
            flags['too_fast'] = True
            flags['quality_score'] *= 0.7
        elif completion_time > 2400:  # More than 40 minutes
            flags['too_slow'] = True
            flags['quality_score'] *= 0.9

        # Check for missing responses
        if not responses or len(responses) == 0:
            flags['missing_responses'] = True
            flags['quality_score'] = 0.0
            return flags

        # Check for straight-lining (same response pattern)
        if len(responses) > 5:
            most_like_indices = [r.get('most_like_index', -1) for r in responses]
            least_like_indices = [r.get('least_like_index', -1) for r in responses]

            # Check if all most_like are the same position
            if len(set(most_like_indices)) == 1:
                flags['straight_lining'] = True
                flags['quality_score'] *= 0.5

            # Check if all least_like are the same position
            if len(set(least_like_indices)) == 1:
                flags['straight_lining'] = True
                flags['quality_score'] *= 0.5

        return flags

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get data collection statistics.

        Returns:
            Statistics dictionary
        """
        with self.db_engine.get_session() as session:
            # Total participants
            cursor = conn.execute("SELECT COUNT(*) FROM v4_test_participants")
            total_participants = cursor.fetchone()[0]

            # Participants by group
            cursor = conn.execute("""
                SELECT test_group, COUNT(*)
                FROM v4_test_participants
                GROUP BY test_group
            """)
            group_counts = dict(cursor.fetchall())

            # Complete sessions
            cursor = conn.execute("""
                SELECT test_version, COUNT(*)
                FROM v4_test_sessions
                WHERE is_complete = TRUE
                GROUP BY test_version
            """)
            complete_counts = dict(cursor.fetchall())

            # Quality stats
            cursor = conn.execute("""
                SELECT AVG(completion_time_seconds) as avg_time,
                       MIN(completion_time_seconds) as min_time,
                       MAX(completion_time_seconds) as max_time
                FROM v4_test_sessions
                WHERE is_complete = TRUE
            """)
            time_stats = cursor.fetchone()

            # Quality flags analysis
            cursor = conn.execute("""
                SELECT quality_flags
                FROM v4_test_sessions
                WHERE is_complete = TRUE AND quality_flags IS NOT NULL
            """)
            quality_data = []
            for row in cursor.fetchall():
                if row[0]:
                    quality_data.append(json.loads(row[0]))

        # Calculate quality metrics
        if quality_data:
            avg_quality = np.mean([d.get('quality_score', 1.0) for d in quality_data])
            flagged_sessions = sum(1 for d in quality_data if d.get('quality_score', 1.0) < 0.9)
        else:
            avg_quality = 1.0
            flagged_sessions = 0

        return {
            'total_participants': total_participants,
            'target_sample_size': self.target_sample_size,
            'completion_rate': (total_participants / self.target_sample_size * 100) if self.target_sample_size > 0 else 0,
            'participants_by_group': group_counts,
            'complete_sessions': complete_counts,
            'timing': {
                'avg_seconds': time_stats[0] if time_stats[0] else 0,
                'min_seconds': time_stats[1] if time_stats[1] else 0,
                'max_seconds': time_stats[2] if time_stats[2] else 0
            },
            'quality': {
                'average_quality_score': avg_quality,
                'flagged_sessions': flagged_sessions,
                'total_quality_checks': len(quality_data)
            }
        }

    def export_for_calibration(self,
                               min_quality_score: float = 0.7,
                               test_version: str = 'v4') -> Tuple[List[Dict], List[Dict]]:
        """
        Export clean data for IRT calibration.

        Args:
            min_quality_score: Minimum quality score to include
            test_version: Test version to export

        Returns:
            Tuple of (responses, blocks)
        """
        with self.db_engine.get_session() as session:
            cursor = conn.execute("""
                SELECT responses, blocks_data, quality_flags
                FROM v4_test_sessions
                WHERE is_complete = TRUE
                AND test_version = ?
            """, (test_version,))

            all_responses = []
            all_blocks = []
            included_sessions = 0
            excluded_sessions = 0

            for row in cursor.fetchall():
                quality_flags = json.loads(row[2]) if row[2] else {}
                quality_score = quality_flags.get('quality_score', 1.0)

                if quality_score >= min_quality_score:
                    responses = json.loads(row[0])
                    blocks = json.loads(row[1])

                    all_responses.extend(responses)
                    all_blocks.extend(blocks)
                    included_sessions += 1
                else:
                    excluded_sessions += 1

        logger.info(f"Exported {included_sessions} sessions for calibration "
                   f"(excluded {excluded_sessions} low-quality sessions)")

        return all_responses, all_blocks

    def get_participant_progress(self, participant_id: str) -> Dict[str, Any]:
        """
        Get progress for a specific participant.

        Args:
            participant_id: Participant ID

        Returns:
            Progress information
        """
        with self.db_engine.get_session() as session:
            # Get participant info
            cursor = conn.execute("""
                SELECT * FROM v4_test_participants
                WHERE participant_id = ?
            """, (participant_id,))
            participant = cursor.fetchone()

            if not participant:
                return {'error': 'Participant not found'}

            # Get sessions
            cursor = conn.execute("""
                SELECT session_id, test_version, is_complete,
                       started_at, completed_at, completion_time_seconds
                FROM v4_test_sessions
                WHERE participant_id = ?
                ORDER BY started_at DESC
            """, (participant_id,))

            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'session_id': row[0],
                    'test_version': row[1],
                    'is_complete': bool(row[2]),
                    'started_at': row[3],
                    'completed_at': row[4],
                    'completion_time_seconds': row[5]
                })

        return {
            'participant_id': participant_id,
            'test_group': participant[4],
            'created_at': participant[5],
            'sessions': sessions,
            'total_sessions': len(sessions),
            'completed_sessions': sum(1 for s in sessions if s['is_complete'])
        }


# Singleton instance
_collector_instance: Optional[DataCollector] = None


def get_data_collector(target_size: int = 100) -> DataCollector:
    """Get or create the singleton data collector instance"""
    global _collector_instance
    if _collector_instance is None:
        _collector_instance = DataCollector(target_sample_size=target_size)
    return _collector_instance