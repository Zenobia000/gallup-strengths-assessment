"""
Data Model Unit Tests - Task 5.1.2

Tests Pydantic data models and schemas for validation, serialization, and business logic.
Follows Linus Torvalds principles: fail-fast validation, clear error messages, simple tests.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List
import json

from models.schemas import (
    # Response Models
    APIResponse, HealthResponse,
    # Consent Models
    ConsentRequest, ConsentResponse,
    # Session Models
    SessionStartRequest, SessionStartResponse, SessionStatus,
    # Assessment Models
    AssessmentItem, ItemResponse, AssessmentSubmission, QuestionResponse,
    # Scoring Models
    BigFiveScores, HEXACOScores, StrengthScores, ProvenanceInfo,
    ScoringRequest, ScoringResponse, ResponseItem,
    # Recommendation Models
    JobRecommendation, ImprovementAction, ImprovementRecommendation,
    # Error Models
    PsychometricError,
    # Enums
    ScaleType, JobCategory
)


class TestAPIResponseModels:
    """Test basic API response models."""

    def test_api_response_success(self):
        """Test successful API response creation."""
        response = APIResponse(
            success=True,
            data={"test": "value"},
            meta={"version": "1.0"}
        )

        assert response.success is True
        assert response.data == {"test": "value"}
        assert response.error is None
        assert response.meta["version"] == "1.0"

    def test_api_response_error(self):
        """Test error API response creation."""
        response = APIResponse(
            success=False,
            error={"code": "VALIDATION_ERROR", "message": "Invalid input"},
            meta={"request_id": "12345"}
        )

        assert response.success is False
        assert response.data is None
        assert response.error["code"] == "VALIDATION_ERROR"

    def test_health_response(self):
        """Test health check response model."""
        now = datetime.now()
        health = HealthResponse(
            status="healthy",
            timestamp=now,
            version="1.0.0",
            database_status="connected",
            services={"scoring": "up", "api": "up"}
        )

        assert health.status == "healthy"
        assert health.timestamp == now
        assert health.services["scoring"] == "up"


class TestConsentModels:
    """Test privacy consent models."""

    def test_consent_request_valid(self):
        """Test valid consent request."""
        consent = ConsentRequest(
            agreed=True,
            user_agent="Mozilla/5.0 Test Browser",
            ip_address="127.0.0.1",
            consent_version="v1.0"
        )

        assert consent.agreed is True
        assert consent.user_agent == "Mozilla/5.0 Test Browser"
        assert consent.ip_address == "127.0.0.1"

    def test_consent_request_must_agree(self):
        """Test consent request requires agreement."""
        with pytest.raises(ValueError, match="Consent must be explicitly agreed"):
            ConsentRequest(
                agreed=False,
                user_agent="Test Browser"
            )

    def test_consent_response(self):
        """Test consent response model."""
        now = datetime.now()
        expires = now + timedelta(days=365)

        response = ConsentResponse(
            consent_id="consent_12345",
            agreed_at=now,
            expires_at=expires,
            consent_version="v1.0"
        )

        assert response.consent_id == "consent_12345"
        assert response.agreed_at == now
        assert response.expires_at == expires


class TestSessionModels:
    """Test assessment session models."""

    def test_session_start_request_valid(self):
        """Test valid session start request."""
        request = SessionStartRequest(
            consent_id="consent_12345",
            instrument="mini_ipip_v1.0"
        )

        assert request.consent_id == "consent_12345"
        assert request.instrument == "mini_ipip_v1.0"

    def test_session_start_request_invalid_instrument(self):
        """Test session start with unsupported instrument."""
        with pytest.raises(ValueError, match="Unsupported instrument"):
            SessionStartRequest(
                consent_id="consent_12345",
                instrument="invalid_instrument"
            )

    def test_session_start_response(self):
        """Test session start response."""
        now = datetime.now()
        expires = now + timedelta(hours=2)

        response = SessionStartResponse(
            session_id="session_12345",
            instrument_version="mini_ipip_v1.0",
            total_items=20,
            estimated_duration=300,
            created_at=now,
            expires_at=expires
        )

        assert response.session_id == "session_12345"
        assert response.total_items == 20
        assert response.estimated_duration == 300

    def test_session_status_enum(self):
        """Test session status enumeration."""
        assert SessionStatus.PENDING == "PENDING"
        assert SessionStatus.IN_PROGRESS == "IN_PROGRESS"
        assert SessionStatus.COMPLETED == "COMPLETED"
        assert SessionStatus.EXPIRED == "EXPIRED"


class TestAssessmentModels:
    """Test assessment item and response models."""

    def test_assessment_item(self):
        """Test assessment item model."""
        item = AssessmentItem(
            item_id="ipip_001",
            text="我是聚會的核心人物",
            scale_type=ScaleType.LIKERT_7,
            reverse_scored=False,
            dimension="extraversion"
        )

        assert item.item_id == "ipip_001"
        assert item.scale_type == ScaleType.LIKERT_7
        assert item.reverse_scored is False

    def test_item_response_valid(self):
        """Test valid item response."""
        response = ItemResponse(
            item_id="ipip_001",
            response=7
        )

        assert response.item_id == "ipip_001"
        assert response.response == 7

    def test_item_response_invalid_range(self):
        """Test item response validation for range."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ItemResponse(item_id="ipip_001", response=8)

        with pytest.raises(ValidationError):
            ItemResponse(item_id="ipip_001", response=0)

    def test_question_response_valid(self):
        """Test valid question response for scoring engine."""
        response = QuestionResponse(
            question_id=1,
            score=5
        )

        assert response.question_id == 1
        assert response.score == 5

    def test_question_response_invalid_range(self):
        """Test question response validation."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            QuestionResponse(question_id=1, score=6)

    def test_assessment_submission_valid(self, sample_assessment_responses):
        """Test valid assessment submission."""
        submission = AssessmentSubmission(
            responses=sample_assessment_responses,
            completion_time=300,
            metadata={"browser": "chrome"}
        )

        assert len(submission.responses) == 20
        assert submission.completion_time == 300

    def test_assessment_submission_incomplete(self):
        """Test assessment submission with incomplete responses."""
        incomplete_responses = [
            ItemResponse(item_id="ipip_001", response=7),
            ItemResponse(item_id="ipip_002", response=3)
        ]

        with pytest.raises(ValueError, match="All 20 items must be answered"):
            AssessmentSubmission(
                responses=incomplete_responses,
                completion_time=300
            )

    def test_assessment_submission_duplicate_items(self):
        """Test assessment submission with duplicate item responses."""
        from pydantic import ValidationError

        duplicate_responses = [
            ItemResponse(item_id="ipip_001", response=7),
            ItemResponse(item_id="ipip_001", response=3)  # Duplicate
        ] + [ItemResponse(item_id=f"ipip_{i:03d}", response=5) for i in range(2, 21)]

        with pytest.raises(ValidationError):
            AssessmentSubmission(
                responses=duplicate_responses,
                completion_time=300
            )

    def test_assessment_submission_invalid_completion_time(self):
        """Test assessment submission with invalid completion times."""
        responses = [ItemResponse(item_id=f"ipip_{i:03d}", response=5) for i in range(1, 21)]

        # Too fast
        with pytest.raises(ValueError, match="Completion time suspiciously fast"):
            AssessmentSubmission(responses=responses, completion_time=30)

        # Too slow
        with pytest.raises(ValueError, match="Completion time suspiciously slow"):
            AssessmentSubmission(responses=responses, completion_time=2000)


class TestScoringModels:
    """Test scoring and results models."""

    def test_big_five_scores_valid(self):
        """Test valid Big Five scores."""
        scores = BigFiveScores(
            extraversion=75,
            agreeableness=82,
            conscientiousness=88,
            neuroticism=25,
            openness=90
        )

        assert scores.extraversion == 75
        assert scores.agreeableness == 82
        assert scores.neuroticism == 25

    def test_big_five_scores_invalid_range(self):
        """Test Big Five scores range validation."""
        with pytest.raises(ValueError):
            BigFiveScores(
                extraversion=101,  # Invalid - over 100
                agreeableness=82,
                conscientiousness=88,
                neuroticism=25,
                openness=90
            )

        with pytest.raises(ValueError):
            BigFiveScores(
                extraversion=75,
                agreeableness=-1,  # Invalid - below 0
                conscientiousness=88,
                neuroticism=25,
                openness=90
            )

    def test_hexaco_scores(self):
        """Test HEXACO scores extending Big Five."""
        scores = HEXACOScores(
            extraversion=75,
            agreeableness=82,
            conscientiousness=88,
            neuroticism=25,
            openness=90,
            honesty_humility=70
        )

        assert scores.honesty_humility == 70
        assert isinstance(scores, BigFiveScores)  # Inheritance check

    def test_strength_scores_valid(self, sample_strength_scores):
        """Test valid strength scores."""
        scores = StrengthScores(**sample_strength_scores)

        assert scores.結構化執行 == 85
        assert scores.探索與創新 == 92
        assert scores.學習與成長 == 90

    def test_strength_scores_invalid_range(self):
        """Test strength scores range validation."""
        with pytest.raises(ValueError):
            StrengthScores(
                結構化執行=101,  # Invalid
                品質與完備=78,
                探索與創新=92,
                分析與洞察=88,
                影響與倡議=72,
                協作與共好=85,
                客戶導向=80,
                學習與成長=90,
                紀律與信任=82,
                壓力調節=75,
                衝突整合=70,
                責任與當責=88
            )

    def test_provenance_info(self):
        """Test provenance tracking model."""
        now = datetime.now()
        provenance = ProvenanceInfo(
            algorithm_version="v1.0.0",
            weights_version="v1.0.0",
            calculated_at=now,
            confidence_level=0.85
        )

        assert provenance.algorithm_version == "v1.0.0"
        assert provenance.confidence_level == 0.85
        assert 0.0 <= provenance.confidence_level <= 1.0

    def test_scoring_request_valid(self):
        """Test valid scoring request."""
        responses = [
            ResponseItem(question_id=i, response_value=5)
            for i in range(1, 21)
        ]

        request = ScoringRequest(
            session_id="session_123",
            responses=responses
        )

        assert request.session_id == "session_123"
        assert len(request.responses) == 20

    def test_scoring_request_incomplete(self):
        """Test scoring request with incomplete responses."""
        responses = [
            ResponseItem(question_id=i, response_value=5)
            for i in range(1, 19)  # Only 18 responses
        ]

        with pytest.raises(ValueError):
            ScoringRequest(
                session_id="session_123",
                responses=responses
            )

    def test_scoring_request_invalid_question_ids(self):
        """Test scoring request with invalid question IDs."""
        from pydantic import ValidationError

        # Test with invalid question ID that exceeds range (21 > 20)
        with pytest.raises(ValidationError):
            ResponseItem(question_id=21, response_value=5)

        # Test with valid individual items but invalid set for ScoringRequest
        responses = [
            ResponseItem(question_id=i, response_value=5)
            for i in range(1, 20)  # Only 19 responses, missing question 20
        ]

        with pytest.raises(ValidationError):
            ScoringRequest(
                session_id="session_123",
                responses=responses
            )


class TestRecommendationModels:
    """Test recommendation and improvement models."""

    def test_job_recommendation(self):
        """Test job recommendation model."""
        recommendation = JobRecommendation(
            role_id="role_001",
            title="Product Manager",
            match_score=0.85,
            reasoning={"strength_match": "High analytical skills"},
            requirements={"experience": "3+ years", "education": "Bachelor's degree"}
        )

        assert recommendation.role_id == "role_001"
        assert recommendation.match_score == 0.85
        assert 0.0 <= recommendation.match_score <= 1.0

    def test_improvement_action(self):
        """Test improvement action model."""
        action = ImprovementAction(
            action="Practice active listening in meetings",
            timeframe="2-4 weeks",
            expected_impact="Improved team collaboration scores"
        )

        assert action.action == "Practice active listening in meetings"
        assert action.timeframe == "2-4 weeks"

    def test_improvement_recommendation(self):
        """Test improvement recommendation model."""
        actions = [
            ImprovementAction(
                action="Practice active listening",
                timeframe="2 weeks",
                expected_impact="Better relationships"
            )
        ]

        recommendation = ImprovementRecommendation(
            area="協作與共好",
            current_score=65,
            target_score=80,
            priority="High",
            actions=actions
        )

        assert recommendation.area == "協作與共好"
        assert recommendation.current_score == 65
        assert recommendation.target_score == 80
        assert len(recommendation.actions) == 1

    def test_job_category_enum(self):
        """Test job category enumeration."""
        assert JobCategory.PRODUCT_STRATEGY == "product_strategy"
        assert JobCategory.TECHNICAL_LEADERSHIP == "technical_leadership"
        assert JobCategory.CREATIVE_INNOVATION == "creative_innovation"


class TestErrorModels:
    """Test error handling models."""

    def test_psychometric_error(self):
        """Test psychometric error model."""
        error = PsychometricError(
            code="VALIDATION_ERROR",
            message="Invalid Likert scale response",
            details={"field": "response", "value": 8, "valid_range": "1-7"},
            trace_id="trace_12345"
        )

        assert error.code == "VALIDATION_ERROR"
        assert error.trace_id == "trace_12345"
        assert error.details["valid_range"] == "1-7"


class TestModelSerialization:
    """Test model serialization and deserialization."""

    def test_big_five_scores_json_serialization(self, sample_big_five_scores):
        """Test Big Five scores JSON serialization."""
        scores = BigFiveScores(**sample_big_five_scores)

        # Serialize to JSON
        json_data = scores.model_dump()
        json_str = json.dumps(json_data)

        # Deserialize from JSON
        parsed_data = json.loads(json_str)
        restored_scores = BigFiveScores(**parsed_data)

        assert restored_scores.extraversion == scores.extraversion
        assert restored_scores.agreeableness == scores.agreeableness

    def test_strength_scores_json_serialization(self, sample_strength_scores):
        """Test strength scores JSON serialization."""
        scores = StrengthScores(**sample_strength_scores)

        # Serialize to JSON
        json_data = scores.model_dump()
        json_str = json.dumps(json_data, ensure_ascii=False)

        # Deserialize from JSON
        parsed_data = json.loads(json_str)
        restored_scores = StrengthScores(**parsed_data)

        assert restored_scores.結構化執行 == scores.結構化執行
        assert restored_scores.探索與創新 == scores.探索與創新

    def test_assessment_submission_json_roundtrip(self, sample_assessment_responses):
        """Test assessment submission JSON round-trip."""
        submission = AssessmentSubmission(
            responses=sample_assessment_responses,
            completion_time=300,
            metadata={"browser": "chrome", "device": "desktop"}
        )

        # Serialize to JSON
        json_data = submission.model_dump()
        json_str = json.dumps(json_data)

        # Deserialize from JSON
        parsed_data = json.loads(json_str)
        restored_submission = AssessmentSubmission(**parsed_data)

        assert len(restored_submission.responses) == len(submission.responses)
        assert restored_submission.completion_time == submission.completion_time
        assert restored_submission.metadata["browser"] == "chrome"


class TestModelValidation:
    """Test advanced model validation scenarios."""

    def test_datetime_fields_serialization(self):
        """Test datetime field serialization."""
        now = datetime.now()
        expires = now + timedelta(hours=2)

        response = SessionStartResponse(
            session_id="session_123",
            instrument_version="mini_ipip_v1.0",
            total_items=20,
            estimated_duration=300,
            created_at=now,
            expires_at=expires
        )

        # Serialize with datetime handling
        json_data = response.model_dump(mode='json')

        # Check that datetimes are properly formatted
        assert isinstance(json_data['created_at'], str)
        assert isinstance(json_data['expires_at'], str)

    def test_nested_model_validation(self):
        """Test validation of nested models."""
        # Create a complex nested structure
        actions = [
            ImprovementAction(
                action="Practice daily reflection",
                timeframe="1 month",
                expected_impact="Increased self-awareness"
            )
        ]

        recommendation = ImprovementRecommendation(
            area="自我認知",
            current_score=60,
            target_score=80,
            priority="Medium",
            actions=actions
        )

        # Test that nested validation works
        assert len(recommendation.actions) == 1
        assert recommendation.actions[0].action == "Practice daily reflection"

    def test_optional_fields_handling(self):
        """Test handling of optional fields."""
        # Test with minimal required fields
        response = APIResponse(success=True)

        assert response.success is True
        assert response.data is None
        assert response.error is None
        assert response.meta == {}

    def test_field_constraints_enforcement(self):
        """Test that field constraints are properly enforced."""
        # Test ge (greater than or equal) constraint
        with pytest.raises(ValueError):
            ResponseItem(question_id=0, response_value=5)  # question_id must be >= 1

        # Test le (less than or equal) constraint
        with pytest.raises(ValueError):
            ResponseItem(question_id=21, response_value=5)  # question_id must be <= 20


if __name__ == "__main__":
    pytest.main([__file__, "-v"])