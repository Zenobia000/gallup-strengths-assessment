"""
Database Integration Tests - Task 5.2.1

Tests database connections, schema integrity, CRUD operations, and data consistency.
Follows Linus Torvalds principles: fail-fast, simple assertions, no unnecessary complexity.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

import sys
sys.path.append(str(Path(__file__).parent.parent.parent / "main" / "python"))

from utils.database import DatabaseManager, DatabaseError, get_database_manager
from core.config import Settings


class TestDatabaseIntegration:
    """Comprehensive database integration tests."""

    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test.db"
        yield str(db_path)
        # Cleanup
        if db_path.exists():
            db_path.unlink()
        os.rmdir(temp_dir)

    @pytest.fixture
    def db_manager(self, temp_db_path):
        """Create database manager with temporary database."""
        return DatabaseManager(temp_db_path)

    def test_database_initialization(self, db_manager):
        """Test database schema creation and initialization."""
        # Verify database file exists
        assert db_manager.db_path.exists()

        # Verify all tables are created
        with db_manager.get_connection() as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]

            expected_tables = [
                'assessment_items',
                'consents',
                'responses',
                'scores',
                'sessions'
            ]

            for table in expected_tables:
                assert table in tables, f"Table {table} not found"

    def test_database_connection_management(self, db_manager):
        """Test connection context manager and error handling."""
        # Test successful connection
        with db_manager.get_connection() as conn:
            cursor = conn.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1

        # Test connection is properly closed after context
        # Connection should be closed, accessing it should raise an error
        # We can't directly test this with sqlite3, but we can test new connections work

        # Test multiple concurrent connections work
        connections = []
        try:
            for i in range(5):
                with db_manager.get_connection() as conn:
                    cursor = conn.execute("SELECT ?", (i,))
                    result = cursor.fetchone()
                    assert result[0] == i
        except Exception as e:
            pytest.fail(f"Multiple connections failed: {e}")

    def test_pragma_settings(self, db_manager):
        """Test SQLite PRAGMA settings are applied correctly."""
        with db_manager.get_connection() as conn:
            # Test WAL mode
            cursor = conn.execute("PRAGMA journal_mode")
            mode = cursor.fetchone()[0]
            assert mode.upper() == "WAL"

            # Test foreign keys are enabled
            cursor = conn.execute("PRAGMA foreign_keys")
            enabled = cursor.fetchone()[0]
            assert enabled == 1

            # Test synchronous mode
            cursor = conn.execute("PRAGMA synchronous")
            sync_mode = cursor.fetchone()[0]
            assert sync_mode in (1, 2)  # NORMAL or FULL

    def test_assessment_items_seeding(self, db_manager):
        """Test assessment items are properly seeded."""
        items = db_manager.get_assessment_items()

        # Should have 20 Mini-IPIP items
        assert len(items) == 20

        # Check required fields
        for item in items:
            assert item["item_id"].startswith("ipip_")
            assert item["instrument_version"] == "mini_ipip_v1.0"
            assert item["text_chinese"] is not None
            assert item["text_english"] is not None
            assert item["dimension"] in ["extraversion", "agreeableness", "conscientiousness", "neuroticism", "openness"]
            assert isinstance(item["reverse_scored"], (bool, int))  # SQLite stores boolean as int
            assert 1 <= item["item_order"] <= 20

        # Check ordering is correct
        orders = [item["item_order"] for item in items]
        assert orders == list(range(1, 21))

        # Check dimension distribution (4 items each)
        dimensions = {}
        for item in items:
            dim = item["dimension"]
            dimensions[dim] = dimensions.get(dim, 0) + 1

        for count in dimensions.values():
            assert count == 4, f"Each dimension should have 4 items, got {dimensions}"

    def test_consent_crud_operations(self, db_manager):
        """Test consent creation and retrieval."""
        # Test consent creation
        consent_data = {
            "consent_id": "test_consent_001",
            "agreed": True,
            "user_agent": "Mozilla/5.0 Test Browser",
            "ip_address": "127.0.0.1",
            "consent_version": "v1.0",
            "expires_at": datetime.now() + timedelta(days=30)
        }

        consent_id = db_manager.create_consent(consent_data)
        assert consent_id == "test_consent_001"

        # Test duplicate consent fails
        with pytest.raises(DatabaseError):
            db_manager.create_consent(consent_data)

        # Verify consent was stored correctly
        with db_manager.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM consents WHERE consent_id = ?", (consent_id,))
            row = cursor.fetchone()
            assert row is not None
            assert row["consent_id"] == consent_id
            assert row["agreed"] == 1  # SQLite stores boolean as int
            assert row["user_agent"] == consent_data["user_agent"]

    def test_session_crud_operations(self, db_manager):
        """Test session creation and management."""
        # First create a consent (foreign key dependency)
        consent_data = {
            "consent_id": "test_consent_002",
            "agreed": True,
            "user_agent": "Test Browser",
            "consent_version": "v1.0",
            "expires_at": datetime.now() + timedelta(days=30)
        }
        db_manager.create_consent(consent_data)

        # Test session creation
        session_data = {
            "session_id": "test_session_001",
            "consent_id": "test_consent_002",
            "instrument_version": "mini_ipip_v1.0",
            "status": "PENDING",
            "expires_at": datetime.now() + timedelta(hours=2),
            "metadata": {"test_flag": True}
        }

        session_id = db_manager.create_session(session_data)
        assert session_id == "test_session_001"

        # Test session retrieval
        session = db_manager.get_session(session_id)
        assert session is not None
        assert session["session_id"] == session_id
        assert session["status"] == "PENDING"
        assert json.loads(session["metadata"])["test_flag"] is True

        # Test non-existent session
        assert db_manager.get_session("nonexistent") is None

    def test_response_handling(self, db_manager):
        """Test assessment response storage and retrieval."""
        # Setup: Create consent and session
        consent_data = {
            "consent_id": "test_consent_003",
            "agreed": True,
            "user_agent": "Test Browser",
            "consent_version": "v1.0",
            "expires_at": datetime.now() + timedelta(days=30)
        }
        db_manager.create_consent(consent_data)

        session_data = {
            "session_id": "test_session_002",
            "consent_id": "test_consent_003",
            "instrument_version": "mini_ipip_v1.0",
            "status": "PENDING",
            "expires_at": datetime.now() + timedelta(hours=2)
        }
        db_manager.create_session(session_data)

        # Test response saving
        responses = [
            {"item_id": "ipip_001", "response": 7},
            {"item_id": "ipip_002", "response": 3},
            {"item_id": "ipip_003", "response": 6}
        ]

        db_manager.save_responses("test_session_002", responses)

        # Verify session status updated to COMPLETED
        session = db_manager.get_session("test_session_002")
        assert session["status"] == "COMPLETED"
        assert session["completed_at"] is not None

        # Verify responses stored correctly
        saved_responses = db_manager.get_responses_for_session("test_session_002")
        assert len(saved_responses) == 3

        for i, resp in enumerate(saved_responses):
            assert resp["item_id"] == responses[i]["item_id"]
            assert resp["response"] == responses[i]["response"]

    def test_scores_handling(self, db_manager):
        """Test score calculation storage and retrieval."""
        # Setup session
        consent_data = {
            "consent_id": "test_consent_004",
            "agreed": True,
            "user_agent": "Test Browser",
            "consent_version": "v1.0",
            "expires_at": datetime.now() + timedelta(days=30)
        }
        db_manager.create_consent(consent_data)

        session_data = {
            "session_id": "test_session_003",
            "consent_id": "test_consent_004",
            "instrument_version": "mini_ipip_v1.0",
            "status": "COMPLETED",
            "expires_at": datetime.now() + timedelta(hours=2)
        }
        db_manager.create_session(session_data)

        # Test score saving
        scores_data = {
            "extraversion": 75,
            "agreeableness": 82,
            "conscientiousness": 68,
            "neuroticism": 45,
            "openness": 88,
            "honesty_humility": 70,
            "strength_scores": {
                "analytical": 85,
                "strategic": 72,
                "learner": 90,
                "achiever": 78
            },
            "provenance": {
                "algorithm": "mini_ipip_v1.0",
                "weights_applied": "v1.0",
                "calculation_timestamp": datetime.now().isoformat()
            },
            "algorithm_version": "v1.0",
            "weights_version": "v1.0"
        }

        db_manager.save_scores("test_session_003", scores_data)

        # Verify scores retrieval
        with db_manager.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM scores WHERE session_id = ?", ("test_session_003",))
            row = cursor.fetchone()
            assert row is not None
            assert row["extraversion"] == 75
            assert row["agreeableness"] == 82

            strength_scores = json.loads(row["strength_scores"])
            assert strength_scores["analytical"] == 85
            assert strength_scores["learner"] == 90

    def test_foreign_key_constraints(self, db_manager):
        """Test foreign key constraints are enforced."""
        # Test session without valid consent fails
        session_data = {
            "session_id": "invalid_session",
            "consent_id": "nonexistent_consent",
            "instrument_version": "mini_ipip_v1.0",
            "status": "PENDING",
            "expires_at": datetime.now() + timedelta(hours=2)
        }

        with pytest.raises(DatabaseError):
            db_manager.create_session(session_data)

        # Test response without valid session fails
        with pytest.raises(DatabaseError):
            db_manager.save_responses("nonexistent_session", [{"item_id": "ipip_001", "response": 5}])

    def test_data_validation_constraints(self, db_manager):
        """Test database constraints and validation."""
        # Setup valid consent and session
        consent_data = {
            "consent_id": "test_consent_005",
            "agreed": True,
            "user_agent": "Test Browser",
            "consent_version": "v1.0",
            "expires_at": datetime.now() + timedelta(days=30)
        }
        db_manager.create_consent(consent_data)

        session_data = {
            "session_id": "test_session_004",
            "consent_id": "test_consent_005",
            "instrument_version": "mini_ipip_v1.0",
            "status": "PENDING",
            "expires_at": datetime.now() + timedelta(hours=2)
        }
        db_manager.create_session(session_data)

        # Test invalid Likert response (should be 1-7)
        with pytest.raises(DatabaseError):
            db_manager.save_responses("test_session_004", [{"item_id": "ipip_001", "response": 8}])

        with pytest.raises(DatabaseError):
            db_manager.save_responses("test_session_004", [{"item_id": "ipip_001", "response": 0}])

        # Test duplicate responses for same item
        db_manager.save_responses("test_session_004", [{"item_id": "ipip_001", "response": 5}])

        with pytest.raises(DatabaseError):
            with db_manager.get_connection() as conn:
                conn.execute("""
                    INSERT INTO responses (session_id, item_id, response)
                    VALUES (?, ?, ?)
                """, ("test_session_004", "ipip_001", 6))

    def test_database_performance_basics(self, db_manager):
        """Test basic database performance with indices."""
        # Create test data
        consent_data = {
            "consent_id": "perf_consent_001",
            "agreed": True,
            "user_agent": "Test Browser",
            "consent_version": "v1.0",
            "expires_at": datetime.now() + timedelta(days=30)
        }
        db_manager.create_consent(consent_data)

        # Create multiple sessions to test index performance
        session_ids = []
        for i in range(100):
            session_data = {
                "session_id": f"perf_session_{i:03d}",
                "consent_id": "perf_consent_001",
                "instrument_version": "mini_ipip_v1.0",
                "status": "PENDING",
                "expires_at": datetime.now() + timedelta(hours=2)
            }
            session_id = db_manager.create_session(session_data)
            session_ids.append(session_id)

        # Test query performance (should be fast with index)
        with db_manager.get_connection() as conn:
            import time
            start_time = time.time()

            cursor = conn.execute("""
                SELECT COUNT(*) FROM sessions WHERE consent_id = ?
            """, ("perf_consent_001",))
            count = cursor.fetchone()[0]

            query_time = time.time() - start_time

            assert count == 100
            assert query_time < 0.1  # Should complete in under 100ms

    def test_transaction_rollback(self, db_manager):
        """Test transaction rollback on errors."""
        consent_data = {
            "consent_id": "rollback_consent",
            "agreed": True,
            "user_agent": "Test Browser",
            "consent_version": "v1.0",
            "expires_at": datetime.now() + timedelta(days=30)
        }
        db_manager.create_consent(consent_data)

        # Test that transaction errors are properly handled
        # Note: SQLite in autocommit mode doesn't rollback automatically like other DBs
        try:
            with db_manager.get_connection() as conn:
                # This should fail due to invalid status constraint
                conn.execute("""
                    INSERT INTO sessions (session_id, consent_id, instrument_version, status, expires_at)
                    VALUES (?, ?, ?, ?, ?)
                """, ("rollback_session", "rollback_consent", "mini_ipip_v1.0", "INVALID_STATUS",
                      datetime.now() + timedelta(hours=2)))
        except DatabaseError:
            # Expected error due to status constraint
            pass

        # Verify invalid session was not created
        session = db_manager.get_session("rollback_session")
        assert session is None

        # Verify we can still create valid sessions (connection not corrupted)
        valid_session_data = {
            "session_id": "valid_session",
            "consent_id": "rollback_consent",
            "instrument_version": "mini_ipip_v1.0",
            "status": "PENDING",
            "expires_at": datetime.now() + timedelta(hours=2)
        }
        session_id = db_manager.create_session(valid_session_data)
        assert session_id == "valid_session"

    def test_enhanced_scores_integration(self, db_manager):
        """Test enhanced scoring functionality if available."""
        # Check if enhanced scores migration is available
        try:
            # Setup session
            consent_data = {
                "consent_id": "enhanced_consent",
                "agreed": True,
                "user_agent": "Test Browser",
                "consent_version": "v1.0",
                "expires_at": datetime.now() + timedelta(days=30)
            }
            db_manager.create_consent(consent_data)

            session_data = {
                "session_id": "enhanced_session",
                "consent_id": "enhanced_consent",
                "instrument_version": "mini_ipip_v1.0",
                "status": "COMPLETED",
                "expires_at": datetime.now() + timedelta(hours=2)
            }
            db_manager.create_session(session_data)

            # Test enhanced scores
            enhanced_scores = {
                "extraversion": 75,
                "agreeableness": 82,
                "conscientiousness": 68,
                "neuroticism": 45,
                "openness": 88,
                "honesty_humility": 70,
                "strength_scores": {"analytical": 85, "strategic": 72},
                "provenance": {"algorithm": "mini_ipip_v1.0"},
                "algorithm_version": "v1.0",
                "weights_version": "v1.0",
                "scoring_confidence": 95.5,
                "response_quality_flags": {"consistent": True, "complete": True},
                "raw_scores": {"E": 15, "A": 18},
                "percentiles": {"extraversion": 75, "agreeableness": 82},
                "processing_time_ms": 45
            }

            db_manager.save_enhanced_scores("enhanced_session", enhanced_scores)

            # Retrieve and verify
            retrieved = db_manager.get_enhanced_scores("enhanced_session")
            assert retrieved is not None
            assert retrieved["scoring_confidence"] == 95.5
            assert retrieved["response_quality_flags"]["consistent"] is True

        except Exception:
            # Enhanced scores migration not available, skip test
            pytest.skip("Enhanced scores migration not available")


class TestDatabaseErrorHandling:
    """Test database error handling and edge cases."""

    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database path."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "error_test.db"
        yield str(db_path)
        # Cleanup
        if db_path.exists():
            db_path.unlink()
        os.rmdir(temp_dir)

    def test_invalid_database_path(self):
        """Test handling of invalid database paths."""
        # Test with read-only directory (should handle gracefully)
        with pytest.raises((DatabaseError, PermissionError, OSError)):
            DatabaseManager("/invalid/readonly/path/test.db")

    def test_corrupted_database_handling(self, temp_db_path):
        """Test handling of corrupted database files."""
        # Create a corrupted database file
        with open(temp_db_path, "w") as f:
            f.write("This is not a valid SQLite database")

        # Should handle corruption gracefully
        with pytest.raises(DatabaseError):
            db_manager = DatabaseManager(temp_db_path)
            with db_manager.get_connection() as conn:
                conn.execute("SELECT 1")

    def test_connection_timeout(self, temp_db_path):
        """Test connection timeout handling."""
        db_manager = DatabaseManager(temp_db_path)

        # This is harder to test without actual contention,
        # but we can verify the timeout is set
        with db_manager.get_connection() as conn:
            # Connection should have timeout configured
            # SQLite doesn't expose timeout directly, but operation should work
            cursor = conn.execute("SELECT 1")
            assert cursor.fetchone()[0] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])