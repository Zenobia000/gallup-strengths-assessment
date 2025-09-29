"""
Assessment Service Layer - Gallup Strengths Assessment

Implements Mini-IPIP test logic and psychometric validation:
- Session lifecycle management
- Response validation and quality control
- Basic scoring algorithms (Week 1 MVP)
- Prepares foundation for advanced scoring (Week 2)

Follows Linus Torvalds principles:
- Functions do one thing well
- Clear error handling
- No more than 3 levels of indentation
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

from models.schemas import (
    SessionData,
    AssessmentItem,
    ItemResponse,
    SessionStatus,
    HEXACOScores,
    BigFiveScores,
    StrengthScores
)
from utils.database import get_database_manager
from core.config import get_settings, get_psychometric_settings
from core.scoring import MiniIPIPScorer, StrengthsMapper


class AssessmentError(Exception):
    """Custom exception for assessment-specific errors."""
    def __init__(self, message: str, code: str = "ASSESSMENT_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class AssessmentService:
    """
    Service layer for assessment operations.

    Encapsulates business logic for Mini-IPIP assessments
    while keeping controllers thin and focused.
    """

    def __init__(self):
        """Initialize assessment service with dependencies."""
        self.db_manager = get_database_manager()
        self.settings = get_settings()
        self.psych_settings = get_psychometric_settings()

        # Initialize scoring components
        normative_data = self.db_manager.get_normative_data()
        self.scorer = MiniIPIPScorer(normative_data)
        self.strengths_mapper = StrengthsMapper()

    def create_session(self, consent_id: str, instrument: str) -> SessionData:
        """
        Create a new assessment session.

        Args:
            consent_id: Valid consent identifier
            instrument: Assessment instrument version

        Returns:
            SessionData: Created session information

        Raises:
            AssessmentError: If session cannot be created
        """
        try:
            # Validate consent is still active
            if not self._validate_consent(consent_id):
                raise AssessmentError(
                    "Consent is invalid or expired",
                    "CONSENT_INVALID"
                )

            # Generate unique session ID
            session_id = f"sess_{uuid.uuid4().hex[:12]}"

            # Calculate expiration time
            created_at = datetime.utcnow()
            expires_at = created_at + timedelta(
                minutes=self.settings.session_timeout_minutes
            )

            # Create session data
            session_data = SessionData(
                session_id=session_id,
                consent_id=consent_id,
                status=SessionStatus.PENDING,
                instrument_version=instrument,
                created_at=created_at,
                expires_at=expires_at
            )

            # Save to database
            self.db_manager.create_session({
                "session_id": session_id,
                "consent_id": consent_id,
                "instrument_version": instrument,
                "status": SessionStatus.PENDING.value,
                "expires_at": expires_at.isoformat(),
                "metadata": {}
            })

            return session_data

        except Exception as e:
            raise AssessmentError(f"Failed to create session: {e}")

    def get_session(self, session_id: str) -> Optional[SessionData]:
        """
        Retrieve session by ID.

        Args:
            session_id: Session identifier

        Returns:
            SessionData: Session information or None if not found
        """
        try:
            raw_session = self.db_manager.get_session(session_id)
            if not raw_session:
                return None

            return SessionData(
                session_id=raw_session["session_id"],
                consent_id=raw_session["consent_id"],
                status=SessionStatus(raw_session["status"]),
                instrument_version=raw_session["instrument_version"],
                created_at=datetime.fromisoformat(
                    raw_session["created_at"].replace("Z", "")
                ),
                expires_at=datetime.fromisoformat(
                    raw_session["expires_at"].replace("Z", "")
                ),
                completed_at=(
                    datetime.fromisoformat(raw_session["completed_at"].replace("Z", ""))
                    if raw_session["completed_at"]
                    else None
                ),
                metadata=raw_session.get("metadata", {})
            )

        except Exception as e:
            raise AssessmentError(f"Failed to retrieve session: {e}")

    def get_assessment_items(self, session_id: str) -> List[AssessmentItem]:
        """
        Get assessment items for a session.

        Args:
            session_id: Session identifier

        Returns:
            List[AssessmentItem]: Assessment items

        Raises:
            AssessmentError: If items cannot be retrieved
        """
        try:
            # Validate session
            session = self.get_session(session_id)
            if not session:
                raise AssessmentError("Session not found", "SESSION_NOT_FOUND")

            # Check session expiry
            if session.expires_at <= datetime.utcnow():
                raise AssessmentError("Session expired", "SESSION_EXPIRED")

            # Get items from database
            raw_items = self.db_manager.get_assessment_items(
                session.instrument_version
            )

            # Convert to domain objects
            items = []
            for item in raw_items:
                items.append(AssessmentItem(
                    item_id=item["item_id"],
                    text=item["text_chinese"],
                    scale_type="likert_7",
                    reverse_scored=bool(item["reverse_scored"]),
                    dimension=item["dimension"]
                ))

            return items

        except AssessmentError:
            raise
        except Exception as e:
            raise AssessmentError(f"Failed to get assessment items: {e}")

    def submit_responses(
        self,
        session_id: str,
        responses: List[ItemResponse],
        completion_time: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Submit assessment responses and calculate comprehensive scores.

        Args:
            session_id: Session identifier
            responses: Item responses
            completion_time: Completion time in seconds
            metadata: Additional metadata

        Returns:
            Dict: Complete scoring results with quality metrics

        Raises:
            AssessmentError: If submission is invalid
        """
        try:
            # Validate session
            session = self.get_session(session_id)
            if not session:
                raise AssessmentError("Session not found", "SESSION_NOT_FOUND")

            if session.status == SessionStatus.COMPLETED:
                raise AssessmentError(
                    "Session already completed",
                    "SESSION_ALREADY_COMPLETED"
                )

            # Quality control checks (basic validation)
            self._validate_responses(responses, completion_time)

            # Save responses to database
            response_data = [
                {"item_id": resp.item_id, "response": resp.response}
                for resp in responses
            ]
            self.db_manager.save_responses(session_id, response_data)

            # NEW: Comprehensive scoring pipeline
            scoring_result = self.scorer.score_assessment(responses, completion_time)

            # Map Big Five to strengths
            strength_mapping = self.strengths_mapper.map_to_strengths(
                scoring_result.standardized_scores
            )

            # Calculate HEXACO scores for backwards compatibility
            hexaco_scores = HEXACOScores(
                extraversion=scoring_result.standardized_scores.extraversion,
                agreeableness=scoring_result.standardized_scores.agreeableness,
                conscientiousness=scoring_result.standardized_scores.conscientiousness,
                neuroticism=scoring_result.standardized_scores.neuroticism,
                openness=scoring_result.standardized_scores.openness,
                honesty_humility=int((
                    scoring_result.standardized_scores.agreeableness +
                    scoring_result.standardized_scores.conscientiousness
                ) / 2)
            )

            # Save enhanced scores to database
            self._save_enhanced_scores(session_id, scoring_result, strength_mapping)

            # Return comprehensive results
            return {
                "session_id": session_id,
                "basic_scores": hexaco_scores,
                "big_five_scores": scoring_result.standardized_scores,
                "strength_scores": strength_mapping.strength_scores,
                "top_strengths": strength_mapping.top_strengths,
                "development_areas": strength_mapping.development_areas,
                "quality_assessment": {
                    "confidence": scoring_result.confidence,
                    "quality_flags": scoring_result.quality_flags,
                    "processing_time_ms": scoring_result.processing_time_ms
                },
                "provenance": {
                    "algorithm_version": scoring_result.algorithm_version,
                    "mapping_version": strength_mapping.mapping_version,
                    "calculated_at": scoring_result.calculated_at.isoformat(),
                    "percentiles": scoring_result.percentiles
                }
            }

        except AssessmentError:
            raise
        except Exception as e:
            raise AssessmentError(f"Failed to submit responses: {e}")

    def _validate_consent(self, consent_id: str) -> bool:
        """
        Validate that consent is still active.

        Args:
            consent_id: Consent identifier

        Returns:
            bool: True if consent is valid
        """
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT agreed, expires_at FROM consents
                    WHERE consent_id = ?
                """, (consent_id,))

                record = cursor.fetchone()
                if not record:
                    return False

                # Check expiry
                expires_at = datetime.fromisoformat(
                    record["expires_at"].replace("Z", "")
                )
                is_expired = expires_at <= datetime.utcnow()

                return record["agreed"] and not is_expired

        except Exception:
            return False

    def _validate_responses(
        self,
        responses: List[ItemResponse],
        completion_time: int
    ) -> None:
        """
        Validate assessment responses for psychometric quality.

        Args:
            responses: Item responses to validate
            completion_time: Time taken to complete

        Raises:
            AssessmentError: If responses fail quality checks
        """
        # Check response count
        if len(responses) != self.psych_settings.TOTAL_ITEMS:
            raise AssessmentError(
                f"Expected {self.psych_settings.TOTAL_ITEMS} responses, got {len(responses)}",
                "PSYCH_001"
            )

        # Check for duplicate responses
        item_ids = [r.item_id for r in responses]
        if len(set(item_ids)) != len(item_ids):
            raise AssessmentError(
                "Duplicate item responses detected",
                "PSYCH_001"
            )

        # Quality control: completion time
        min_time = self.psych_settings.TOTAL_ITEMS * 3  # 3 seconds per item
        max_time = self.settings.max_completion_time_minutes * 60

        if completion_time < min_time:
            raise AssessmentError(
                f"Completion too fast: {completion_time}s (min: {min_time}s)",
                "PSYCH_001"
            )

        if completion_time > max_time:
            raise AssessmentError(
                f"Completion too slow: {completion_time}s (max: {max_time}s)",
                "PSYCH_001"
            )

        # Check response range
        for response in responses:
            if not (self.psych_settings.LIKERT_SCALE_MIN <=
                   response.response <=
                   self.psych_settings.LIKERT_SCALE_MAX):
                raise AssessmentError(
                    f"Response {response.response} out of range",
                    "PSYCH_002"
                )

    def _save_enhanced_scores(self, session_id: str, scoring_result, strength_mapping):
        """Save enhanced scores with quality metrics and provenance."""
        scores_data = {
            "session_id": session_id,
            "extraversion": scoring_result.standardized_scores.extraversion,
            "agreeableness": scoring_result.standardized_scores.agreeableness,
            "conscientiousness": scoring_result.standardized_scores.conscientiousness,
            "neuroticism": scoring_result.standardized_scores.neuroticism,
            "openness": scoring_result.standardized_scores.openness,
            "honesty_humility": int((
                scoring_result.standardized_scores.agreeableness +
                scoring_result.standardized_scores.conscientiousness
            ) / 2),
            "strength_scores": strength_mapping.strength_scores.__dict__,
            "scoring_confidence": scoring_result.confidence,
            "response_quality_flags": scoring_result.quality_flags,
            "raw_scores": scoring_result.raw_scores.__dict__,
            "percentiles": scoring_result.percentiles,
            "processing_time_ms": scoring_result.processing_time_ms,
            "algorithm_version": scoring_result.algorithm_version,
            "weights_version": strength_mapping.mapping_version,
            "provenance": {
                "scoring_method": "mini_ipip_validated",
                "normative_data_version": "literature_v1.0",
                "strength_mapping_version": strength_mapping.mapping_version,
                "calculated_at": scoring_result.calculated_at.isoformat(),
                "top_strengths": [s["name"] for s in strength_mapping.top_strengths],
                "development_areas": [d["name"] for d in strength_mapping.development_areas],
                "confidence_scores": strength_mapping.confidence_scores
            }
        }

        self.db_manager.save_enhanced_scores(session_id, scores_data)

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get current session status and progress.

        Args:
            session_id: Session identifier

        Returns:
            Dict[str, Any]: Session status information

        Raises:
            AssessmentError: If session not found
        """
        try:
            session = self.get_session(session_id)
            if not session:
                raise AssessmentError("Session not found", "SESSION_NOT_FOUND")

            # Check if session has expired
            is_expired = session.expires_at <= datetime.utcnow()

            status = {
                "session_id": session.session_id,
                "status": session.status.value,
                "is_expired": is_expired,
                "created_at": session.created_at.isoformat(),
                "expires_at": session.expires_at.isoformat(),
                "completed_at": session.completed_at.isoformat() if session.completed_at else None,
                "instrument_version": session.instrument_version,
                "time_remaining": max(0, int(
                    (session.expires_at - datetime.utcnow()).total_seconds()
                )) if not is_expired else 0
            }

            return status

        except AssessmentError:
            raise
        except Exception as e:
            raise AssessmentError(f"Failed to get session status: {e}")

    def get_enhanced_scores(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get enhanced scoring results for a session.

        Args:
            session_id: Session identifier

        Returns:
            Dict with complete scoring results or None if not found

        Raises:
            AssessmentError: If session not found or scores not available
        """
        try:
            # Validate session exists
            session = self.get_session(session_id)
            if not session:
                raise AssessmentError("Session not found", "SESSION_NOT_FOUND")

            if session.status != SessionStatus.COMPLETED:
                raise AssessmentError(
                    "Session not completed - scores not available",
                    "SCORES_NOT_AVAILABLE"
                )

            # Get enhanced scores from database
            scores_data = self.db_manager.get_enhanced_scores(session_id)
            if not scores_data:
                raise AssessmentError(
                    "Scores not found for completed session",
                    "SCORES_NOT_FOUND"
                )

            return {
                "session_id": session_id,
                "big_five_scores": {
                    "extraversion": scores_data["extraversion"],
                    "agreeableness": scores_data["agreeableness"],
                    "conscientiousness": scores_data["conscientiousness"],
                    "neuroticism": scores_data["neuroticism"],
                    "openness": scores_data["openness"]
                },
                "strength_scores": scores_data["strength_scores"],
                "percentiles": scores_data.get("percentiles", {}),
                "raw_scores": scores_data.get("raw_scores", {}),
                "quality_assessment": {
                    "confidence": scores_data.get("scoring_confidence", 0.0),
                    "quality_flags": scores_data.get("response_quality_flags", []),
                    "processing_time_ms": scores_data.get("processing_time_ms", 0.0)
                },
                "provenance": scores_data.get("provenance", {}),
                "calculated_at": scores_data.get("calculated_at"),
                "algorithm_version": scores_data.get("algorithm_version"),
                "weights_version": scores_data.get("weights_version")
            }

        except AssessmentError:
            raise
        except Exception as e:
            raise AssessmentError(f"Failed to get enhanced scores: {e}")

    def recalculate_scores(self, session_id: str) -> Dict[str, Any]:
        """
        Recalculate scores for a completed session with latest algorithms.

        Args:
            session_id: Session identifier

        Returns:
            Dict: Updated scoring results

        Raises:
            AssessmentError: If session or responses not found
        """
        try:
            # Validate session
            session = self.get_session(session_id)
            if not session:
                raise AssessmentError("Session not found", "SESSION_NOT_FOUND")

            if session.status != SessionStatus.COMPLETED:
                raise AssessmentError(
                    "Session not completed - cannot recalculate",
                    "SESSION_NOT_COMPLETED"
                )

            # Get stored responses
            response_data = self.db_manager.get_responses_for_session(session_id)
            if len(response_data) != 20:
                raise AssessmentError(
                    "Incomplete response data - cannot recalculate",
                    "INCOMPLETE_RESPONSES"
                )

            # Convert to ItemResponse objects
            responses = [
                ItemResponse(item_id=r["item_id"], response=r["response"])
                for r in response_data
            ]

            # Calculate completion time from timestamps
            timestamps = [datetime.fromisoformat(r["submitted_at"].replace("Z", ""))
                         for r in response_data]
            completion_time = int((max(timestamps) - min(timestamps)).total_seconds())

            # Refresh normative data and reinitialize scorers
            normative_data = self.db_manager.get_normative_data()
            self.scorer = MiniIPIPScorer(normative_data)

            # Recalculate scores
            scoring_result = self.scorer.score_assessment(responses, completion_time)
            strength_mapping = self.strengths_mapper.map_to_strengths(
                scoring_result.standardized_scores
            )

            # Save updated scores
            self._save_enhanced_scores(session_id, scoring_result, strength_mapping)

            # Return updated results
            return self.get_enhanced_scores(session_id)

        except AssessmentError:
            raise
        except Exception as e:
            raise AssessmentError(f"Failed to recalculate scores: {e}")


# Convenience function for dependency injection
def get_assessment_service() -> AssessmentService:
    """Get assessment service instance."""
    return AssessmentService()