"""
API Integration Tests for Scoring Endpoints

Tests the integration between:
- FastAPI scoring routes
- ScoringEngine core logic
- SQLAlchemy database persistence
- Pydantic request/response models

Focus Areas:
1. Scale conversion accuracy (7-point → 5-point)
2. API endpoint response formats
3. Database score storage and retrieval
4. Error handling for invalid inputs

Author: Test Automation Engineer (TaskMaster Hub)
Date: 2025-09-30
Version: 1.0
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import sys
from pathlib import Path

# Add src/main/python to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "main" / "python"))

from api.main import app  # Main FastAPI application
from utils.sqlalchemy_db import Base, get_db
from models.database import AssessmentSession, Score


# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_integration.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def test_db():
    """Create test database and tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_db):
    """Create a new database session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create FastAPI test client with test database."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_session(db_session):
    """Create a sample assessment session for testing."""
    session = AssessmentSession(
        session_id="test-session-001",
        consent_id="test-consent-001",
        status="IN_PROGRESS",
        instrument_version="mini_ipip_v1.0",
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow()
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


@pytest.fixture
def valid_7point_responses():
    """Generate valid 7-point scale responses for all 20 questions."""
    return [
        {"question_id": i, "response_value": 4}  # Neutral response
        for i in range(1, 21)
    ]


@pytest.fixture
def varied_7point_responses():
    """Generate varied 7-point scale responses."""
    # Pattern: 7,6,5,4,3,2,1 repeated
    values = [7, 6, 5, 4, 3, 2, 1] * 3 + [4]  # 20 values
    return [
        {"question_id": i, "response_value": values[i-1]}
        for i in range(1, 21)
    ]


class TestScaleConversionAccuracy:
    """Test 7-point to 5-point scale conversion accuracy."""

    def test_minimum_value_conversion(self, client, sample_session):
        """Test that 7-point value 1 converts correctly."""
        responses = [
            {"question_id": i, "response_value": 1}
            for i in range(1, 21)
        ]

        response = client.post(
            "/api/scoring/calculate",
            json={
                "session_id": sample_session.session_id,
                "responses": responses
            }
        )

        assert response.status_code == 200
        data = response.json()

        # All dimensions should have minimum score (4 questions × 1 point = 4)
        scores = data["big_five_scores"]["raw_scores"]
        assert all(score == 4.0 for score in scores.values())

    def test_maximum_value_conversion(self, client, sample_session):
        """Test that 7-point value 7 converts correctly."""
        responses = [
            {"question_id": i, "response_value": 7}
            for i in range(1, 21)
        ]

        response = client.post(
            "/api/scoring/calculate",
            json={
                "session_id": sample_session.session_id,
                "responses": responses
            }
        )

        assert response.status_code == 200
        data = response.json()

        # All dimensions should have maximum score (4 questions × 5 points = 20)
        scores = data["big_five_scores"]["raw_scores"]
        assert all(score == 20.0 for score in scores.values())

    def test_midpoint_value_conversion(self, client, sample_session):
        """Test that 7-point value 4 (midpoint) converts correctly."""
        responses = [
            {"question_id": i, "response_value": 4}
            for i in range(1, 21)
        ]

        response = client.post(
            "/api/scoring/calculate",
            json={
                "session_id": sample_session.session_id,
                "responses": responses
            }
        )

        assert response.status_code == 200
        data = response.json()

        # 7-point value 4 → 5-point value ~3 → dimension score ~12
        scores = data["big_five_scores"]["raw_scores"]
        for score in scores.values():
            assert 11.0 <= score <= 13.0  # Allow small rounding variance

    def test_conversion_formula_accuracy(self, client, sample_session):
        """Test conversion formula: 5-point = 1 + (7-point - 1) * 4/6."""
        # Test specific conversions
        test_cases = [
            (1, 4.0),   # 1 → 1 → score 4
            (7, 20.0),  # 7 → 5 → score 20
            (4, 12.0),  # 4 → 3 → score 12
        ]

        for input_7pt, expected_dimension_score in test_cases:
            responses = [
                {"question_id": i, "response_value": input_7pt}
                for i in range(1, 21)
            ]

            response = client.post(
                "/api/scoring/calculate",
                json={
                    "session_id": sample_session.session_id,
                    "responses": responses
                }
            )

            assert response.status_code == 200
            scores = response.json()["big_five_scores"]["raw_scores"]

            for dimension, score in scores.items():
                assert abs(score - expected_dimension_score) < 0.5, \
                    f"Dimension {dimension}: expected ~{expected_dimension_score}, got {score}"


class TestAPIEndpointResponseFormat:
    """Test API endpoint response structure and format."""

    def test_calculate_endpoint_response_structure(self, client, sample_session, valid_7point_responses):
        """Test /calculate endpoint returns correct response structure."""
        response = client.post(
            "/api/scoring/calculate",
            json={
                "session_id": sample_session.session_id,
                "responses": valid_7point_responses
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "session_id" in data
        assert "big_five_scores" in data
        assert "score_id" in data

        # Verify Big Five scores structure
        big_five = data["big_five_scores"]
        assert "raw_scores" in big_five
        assert "scoring_version" in big_five
        assert "timestamp" in big_five

        # Verify all 5 dimensions present
        raw_scores = big_five["raw_scores"]
        expected_dimensions = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
        assert all(dim in raw_scores for dim in expected_dimensions)

    def test_results_endpoint_response_structure(self, client, sample_session, valid_7point_responses):
        """Test /results/{session_id} endpoint returns correct structure."""
        # First calculate scores
        client.post(
            "/api/scoring/calculate",
            json={
                "session_id": sample_session.session_id,
                "responses": valid_7point_responses
            }
        )

        # Then retrieve results
        response = client.get(f"/api/scoring/results/{sample_session.session_id}")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "session_id" in data
        assert "big_five_scores" in data
        assert "metadata" in data

        # Verify metadata structure
        metadata = data["metadata"]
        assert "confidence_level" in metadata
        assert "quality_flags" in metadata
        assert "scoring_version" in metadata
        assert "created_at" in metadata

    def test_metadata_endpoint_response(self, client):
        """Test /metadata endpoint returns engine information."""
        response = client.get("/api/scoring/metadata")

        assert response.status_code == 200
        data = response.json()

        assert "scorer_metadata" in data
        assert "api_version" in data
        assert "supported_endpoints" in data
        assert "disabled_endpoints" in data

        scorer_meta = data["scorer_metadata"]
        assert scorer_meta["engine"] == "ScoringEngine"
        assert "dimensions" in scorer_meta
        assert len(scorer_meta["dimensions"]) == 5


class TestDatabaseIntegration:
    """Test database persistence and retrieval."""

    def test_score_persisted_to_database(self, client, sample_session, valid_7point_responses, db_session):
        """Test that scores are correctly saved to database."""
        response = client.post(
            "/api/scoring/calculate",
            json={
                "session_id": sample_session.session_id,
                "responses": valid_7point_responses
            }
        )

        assert response.status_code == 200
        score_id = response.json()["score_id"]

        # Query database directly
        score_record = db_session.query(Score).filter(Score.id == score_id).first()

        assert score_record is not None
        assert score_record.session_id == sample_session.session_id
        assert score_record.raw_scores is not None
        assert score_record.scoring_version == "1.0.0-basic"

    def test_raw_scores_json_format(self, client, sample_session, varied_7point_responses, db_session):
        """Test that raw scores are stored as valid JSON."""
        response = client.post(
            "/api/scoring/calculate",
            json={
                "session_id": sample_session.session_id,
                "responses": varied_7point_responses
            }
        )

        score_id = response.json()["score_id"]
        score_record = db_session.query(Score).filter(Score.id == score_id).first()

        # Verify JSON can be parsed
        raw_scores = json.loads(score_record.raw_scores)

        assert isinstance(raw_scores, dict)
        assert len(raw_scores) == 5
        assert all(isinstance(v, (int, float)) for v in raw_scores.values())

    def test_retrieve_existing_scores(self, client, sample_session, valid_7point_responses):
        """Test retrieving previously calculated scores."""
        # Calculate scores
        calc_response = client.post(
            "/api/scoring/calculate",
            json={
                "session_id": sample_session.session_id,
                "responses": valid_7point_responses
            }
        )

        original_scores = calc_response.json()["big_five_scores"]["raw_scores"]

        # Retrieve scores
        get_response = client.get(f"/api/scoring/results/{sample_session.session_id}")
        retrieved_scores = get_response.json()["big_five_scores"]["raw_scores"]

        # Scores should match
        assert original_scores == retrieved_scores


class TestErrorHandling:
    """Test error handling for invalid inputs."""

    def test_invalid_session_id(self, client, valid_7point_responses):
        """Test error when session_id doesn't exist."""
        response = client.post(
            "/api/scoring/calculate",
            json={
                "session_id": "non-existent-session",
                "responses": valid_7point_responses
            }
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_invalid_response_count(self, client, sample_session):
        """Test error when response count is not 20."""
        # Only 10 responses instead of 20
        responses = [
            {"question_id": i, "response_value": 4}
            for i in range(1, 11)
        ]

        response = client.post(
            "/api/scoring/calculate",
            json={
                "session_id": sample_session.session_id,
                "responses": responses
            }
        )

        assert response.status_code == 400
        assert "20" in response.json()["detail"]

    def test_invalid_7point_scale_value(self, client, sample_session):
        """Test error when 7-point scale value is out of range."""
        # Response value 8 is invalid for 7-point scale
        responses = [
            {"question_id": i, "response_value": 8}
            for i in range(1, 21)
        ]

        response = client.post(
            "/api/scoring/calculate",
            json={
                "session_id": sample_session.session_id,
                "responses": responses
            }
        )

        assert response.status_code == 400
        assert "7" in response.json()["detail"]

    def test_missing_session_id_in_request(self, client, valid_7point_responses):
        """Test error when session_id is missing."""
        response = client.post(
            "/api/scoring/calculate",
            json={
                "responses": valid_7point_responses
            }
        )

        assert response.status_code == 422  # Pydantic validation error

    def test_retrieve_nonexistent_results(self, client):
        """Test error when retrieving results for non-existent session."""
        response = client.get("/api/scoring/results/non-existent-session")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_duplicate_question_ids(self, client, sample_session):
        """Test error when duplicate question IDs are provided."""
        # Duplicate question ID 1
        responses = [
            {"question_id": 1, "response_value": 4}
            for _ in range(20)
        ]

        response = client.post(
            "/api/scoring/calculate",
            json={
                "session_id": sample_session.session_id,
                "responses": responses
            }
        )

        assert response.status_code == 400


class TestEndToEndScenarios:
    """Test complete end-to-end workflows."""

    def test_complete_assessment_flow(self, client, sample_session, varied_7point_responses):
        """Test complete flow: calculate → retrieve → verify."""
        # Step 1: Calculate scores
        calc_response = client.post(
            "/api/scoring/calculate",
            json={
                "session_id": sample_session.session_id,
                "responses": varied_7point_responses
            }
        )

        assert calc_response.status_code == 200
        calc_data = calc_response.json()

        # Step 2: Retrieve results
        get_response = client.get(f"/api/scoring/results/{sample_session.session_id}")

        assert get_response.status_code == 200
        get_data = get_response.json()

        # Step 3: Verify consistency
        assert calc_data["session_id"] == get_data["session_id"]
        assert calc_data["big_five_scores"]["raw_scores"] == get_data["big_five_scores"]["raw_scores"]

    def test_metadata_before_calculation(self, client):
        """Test that metadata can be retrieved before any calculations."""
        response = client.get("/api/scoring/metadata")

        assert response.status_code == 200
        assert "scorer_metadata" in response.json()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])