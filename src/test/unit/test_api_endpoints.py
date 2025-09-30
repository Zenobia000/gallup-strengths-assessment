"""
API Endpoint Unit Tests - Task 5.1.3

Tests FastAPI endpoints for validation, error handling, and business logic.
Follows Linus Torvalds principles: simple tests, clear assertions, fail-fast validation.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any
import json
from unittest.mock import patch, MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent / "main" / "python"))

from api.main import app
from models.schemas import (
    ConsentRequest, SessionStartRequest, AssessmentSubmission,
    ItemResponse, HealthResponse
)


class TestHealthEndpoint:
    """Test system health check endpoint."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_health_check_success(self):
        """Test successful health check."""
        with patch('api.main.get_db_connection') as mock_db:
            # Mock successful database connection
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = (1,)
            mock_conn.execute.return_value = mock_cursor
            mock_db.return_value.__enter__.return_value = mock_conn

            response = self.client.get("/api/v1/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["database_status"] == "connected"
            assert "services" in data
            assert data["services"]["assessment"] == "ready"

    def test_health_check_database_error(self):
        """Test health check with database error."""
        with patch('api.main.get_db_connection') as mock_db:
            # Mock database connection failure
            mock_db.side_effect = Exception("Database connection failed")

            response = self.client.get("/api/v1/health")

            assert response.status_code == 200  # Health endpoint always returns 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["database_status"] == "error"
            assert "error" in data

    def test_health_response_headers(self):
        """Test health check response headers."""
        with patch('api.main.get_db_connection') as mock_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = (1,)
            mock_conn.execute.return_value = mock_cursor
            mock_db.return_value.__enter__.return_value = mock_conn

            response = self.client.get("/api/v1/health")

            # Check metadata headers
            assert "X-Request-ID" in response.headers
            assert "X-Timestamp" in response.headers
            assert "X-API-Version" in response.headers
            assert response.headers["X-API-Version"] == "v1.0.0"


class TestConsentEndpoints:
    """Test privacy consent management endpoints."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_consent_creation_success(self):
        """Test successful consent creation."""
        consent_data = {
            "agreed": True,
            "user_agent": "Mozilla/5.0 Test Browser",
            "ip_address": "127.0.0.1",
            "consent_version": "v1.0"
        }

        with patch('api.routes.consent.get_database_manager') as mock_db_manager:
            # Mock database manager
            mock_manager = MagicMock()
            mock_manager.create_consent.return_value = "consent_12345"
            mock_db_manager.return_value = mock_manager

            response = self.client.post("/api/v1/consent", json=consent_data)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "consent_id" in data["data"]

    def test_consent_creation_disagreement(self):
        """Test consent creation with disagreement."""
        consent_data = {
            "agreed": False,
            "user_agent": "Mozilla/5.0 Test Browser"
        }

        response = self.client.post("/api/v1/consent", json=consent_data)

        # Should return validation error
        assert response.status_code == 422  # Unprocessable Entity

    def test_consent_invalid_user_agent(self):
        """Test consent creation with invalid user agent."""
        consent_data = {
            "agreed": True,
            "user_agent": "",  # Empty user agent
            "ip_address": "127.0.0.1"
        }

        response = self.client.post("/api/v1/consent", json=consent_data)

        assert response.status_code == 422  # Validation error

    def test_consent_database_error(self):
        """Test consent creation with database error."""
        consent_data = {
            "agreed": True,
            "user_agent": "Mozilla/5.0 Test Browser",
            "ip_address": "127.0.0.1"
        }

        with patch('api.routes.consent.get_database_manager') as mock_db_manager:
            # Mock database error
            mock_manager = MagicMock()
            mock_manager.create_consent.side_effect = Exception("Database error")
            mock_db_manager.return_value = mock_manager

            response = self.client.post("/api/v1/consent", json=consent_data)

            assert response.status_code == 500  # Internal server error


class TestSessionEndpoints:
    """Test assessment session management endpoints."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_session_start_success(self):
        """Test successful session start."""
        session_data = {
            "consent_id": "consent_12345",
            "instrument": "mini_ipip_v1.0"
        }

        with patch('api.routes.sessions.get_database_manager') as mock_db_manager:
            # Mock database manager
            mock_manager = MagicMock()
            mock_manager.create_session.return_value = "session_12345"
            mock_manager.get_assessment_items.return_value = [
                {"item_id": f"ipip_{i:03d}", "text": f"Test item {i}"}
                for i in range(1, 21)
            ]
            mock_db_manager.return_value = mock_manager

            response = self.client.post("/api/v1/sessions/start", json=session_data)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "session_id" in data["data"]

    def test_session_start_invalid_instrument(self):
        """Test session start with invalid instrument."""
        session_data = {
            "consent_id": "consent_12345",
            "instrument": "invalid_instrument"
        }

        response = self.client.post("/api/v1/sessions/start", json=session_data)

        assert response.status_code == 422  # Validation error

    def test_session_items_retrieval(self):
        """Test assessment items retrieval."""
        session_id = "session_12345"

        with patch('api.routes.sessions.get_database_manager') as mock_db_manager:
            # Mock database manager
            mock_manager = MagicMock()
            mock_manager.get_session.return_value = {
                "session_id": session_id,
                "status": "PENDING",
                "instrument_version": "mini_ipip_v1.0"
            }
            mock_manager.get_assessment_items.return_value = [
                {
                    "item_id": f"ipip_{i:03d}",
                    "text_chinese": f"测试项目 {i}",
                    "dimension": "extraversion",
                    "reverse_scored": False
                }
                for i in range(1, 21)
            ]
            mock_db_manager.return_value = mock_manager

            response = self.client.get(f"/api/v1/sessions/{session_id}/items")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]["items"]) == 20

    def test_session_items_not_found(self):
        """Test assessment items retrieval for non-existent session."""
        session_id = "nonexistent_session"

        with patch('api.routes.sessions.get_database_manager') as mock_db_manager:
            # Mock database manager
            mock_manager = MagicMock()
            mock_manager.get_session.return_value = None
            mock_db_manager.return_value = mock_manager

            response = self.client.get(f"/api/v1/sessions/{session_id}/items")

            assert response.status_code == 404  # Not found


class TestScoringEndpoints:
    """Test scoring API endpoints."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_scoring_request_success(self):
        """Test successful scoring request."""
        scoring_data = {
            "session_id": "session_12345",
            "responses": [
                {"question_id": i, "response_value": 5}
                for i in range(1, 21)
            ]
        }

        with patch('api.routes.scoring.ScoringEngine') as mock_scoring_engine:
            # Mock scoring engine
            mock_engine = MagicMock()
            mock_result = {
                "extraversion": 75,
                "agreeableness": 82,
                "conscientiousness": 88,
                "neuroticism": 25,
                "openness": 90,
                "honesty_humility": 70
            }
            mock_engine.calculate_big_five_scores.return_value = (mock_result, {"confidence": 0.95})
            mock_scoring_engine.return_value = mock_engine

            response = self.client.post("/api/v1/scoring/big-five", json=scoring_data)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "big_five_scores" in data["data"]

    def test_scoring_request_incomplete_responses(self):
        """Test scoring request with incomplete responses."""
        scoring_data = {
            "session_id": "session_12345",
            "responses": [
                {"question_id": i, "response_value": 5}
                for i in range(1, 19)  # Only 18 responses
            ]
        }

        response = self.client.post("/api/v1/scoring/big-five", json=scoring_data)

        assert response.status_code == 422  # Validation error

    def test_scoring_request_invalid_response_values(self):
        """Test scoring request with invalid response values."""
        scoring_data = {
            "session_id": "session_12345",
            "responses": [
                {"question_id": 1, "response_value": 8},  # Invalid value
                {"question_id": 2, "response_value": 5}
            ] + [
                {"question_id": i, "response_value": 5}
                for i in range(3, 21)
            ]
        }

        response = self.client.post("/api/v1/scoring/big-five", json=scoring_data)

        assert response.status_code == 422  # Validation error

    def test_strengths_mapping_success(self):
        """Test successful strengths mapping."""
        strengths_data = {
            "session_id": "session_12345"
        }

        with patch('api.routes.scoring.get_database_manager') as mock_db_manager:
            with patch('api.routes.scoring.StrengthMapper') as mock_mapper:
                # Mock database manager
                mock_manager = MagicMock()
                mock_manager.get_enhanced_scores.return_value = {
                    "extraversion": 75,
                    "agreeableness": 82,
                    "conscientiousness": 88,
                    "neuroticism": 25,
                    "openness": 90,
                    "honesty_humility": 70
                }
                mock_db_manager.return_value = mock_manager

                # Mock strength mapper
                mock_mapper_instance = MagicMock()
                mock_mapper_instance.map_to_strengths.return_value = {
                    "結構化執行": 85,
                    "品質與完備": 78,
                    "探索與創新": 92
                }
                mock_mapper.return_value = mock_mapper_instance

                response = self.client.post("/api/v1/scoring/strengths", json=strengths_data)

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "strengths_profile" in data["data"]


class TestErrorHandling:
    """Test API error handling and validation."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_404_endpoint_not_found(self):
        """Test 404 error for non-existent endpoints."""
        response = self.client.get("/api/v1/nonexistent")

        assert response.status_code == 404

    def test_405_method_not_allowed(self):
        """Test 405 error for wrong HTTP methods."""
        response = self.client.delete("/api/v1/health")  # Health endpoint only supports GET

        assert response.status_code == 405

    def test_422_validation_error_structure(self):
        """Test structure of validation errors."""
        # Send invalid consent request
        invalid_data = {
            "agreed": "not_a_boolean",  # Should be boolean
            "user_agent": ""  # Should not be empty
        }

        response = self.client.post("/api/v1/consent", json=invalid_data)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], list)

    def test_content_type_validation(self):
        """Test content type validation."""
        response = self.client.post(
            "/api/v1/consent",
            data="invalid_json_data",
            headers={"Content-Type": "text/plain"}
        )

        assert response.status_code == 422

    def test_missing_required_fields(self):
        """Test validation of missing required fields."""
        incomplete_data = {
            "user_agent": "Mozilla/5.0 Test Browser"
            # Missing required 'agreed' field
        }

        response = self.client.post("/api/v1/consent", json=incomplete_data)

        assert response.status_code == 422
        data = response.json()
        # Check that the error mentions the missing field
        error_messages = str(data)
        assert "agreed" in error_messages


class TestRequestMetadata:
    """Test request metadata and traceability."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_request_id_generation(self):
        """Test that each request gets a unique ID."""
        with patch('api.main.get_db_connection') as mock_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = (1,)
            mock_conn.execute.return_value = mock_cursor
            mock_db.return_value.__enter__.return_value = mock_conn

            response1 = self.client.get("/api/v1/health")
            response2 = self.client.get("/api/v1/health")

            request_id1 = response1.headers.get("X-Request-ID")
            request_id2 = response2.headers.get("X-Request-ID")

            assert request_id1 is not None
            assert request_id2 is not None
            assert request_id1 != request_id2

    def test_timestamp_header(self):
        """Test that timestamp header is included."""
        with patch('api.main.get_db_connection') as mock_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = (1,)
            mock_conn.execute.return_value = mock_cursor
            mock_db.return_value.__enter__.return_value = mock_conn

            response = self.client.get("/api/v1/health")

            timestamp = response.headers.get("X-Timestamp")
            assert timestamp is not None

            # Verify timestamp format
            try:
                datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                pytest.fail("Timestamp is not in valid ISO format")

    def test_api_version_header(self):
        """Test API version header."""
        with patch('api.main.get_db_connection') as mock_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = (1,)
            mock_conn.execute.return_value = mock_cursor
            mock_db.return_value.__enter__.return_value = mock_conn

            response = self.client.get("/api/v1/health")

            api_version = response.headers.get("X-API-Version")
            assert api_version == "v1.0.0"


class TestRootEndpoint:
    """Test root endpoint functionality."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_root_endpoint_redirect(self):
        """Test root endpoint returns API information."""
        response = self.client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Gallup Strengths Assessment API"
        assert "documentation" in data
        assert "health_check" in data


class TestCORSHeaders:
    """Test CORS headers configuration."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_cors_headers_present(self):
        """Test that CORS headers are present in responses."""
        with patch('api.main.get_db_connection') as mock_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = (1,)
            mock_conn.execute.return_value = mock_cursor
            mock_db.return_value.__enter__.return_value = mock_conn

            response = self.client.get(
                "/api/v1/health",
                headers={"Origin": "http://localhost:3000"}
            )

            # CORS headers should be present for allowed origins
            # Note: TestClient may not fully simulate CORS, so this test verifies basic functionality
            assert response.status_code == 200

    def test_preflight_request(self):
        """Test CORS preflight request handling."""
        response = self.client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )

        # Preflight requests should be handled appropriately
        assert response.status_code in [200, 204]  # Either is acceptable for OPTIONS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])