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
    HEXACOScores
)
from utils.database import get_database_manager
from core.config import get_settings, get_psychometric_settings


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
    ) -> HEXACOScores:
        """
        Submit assessment responses and calculate basic scores.

        Args:
            session_id: Session identifier
            responses: Item responses
            completion_time: Completion time in seconds
            metadata: Additional metadata

        Returns:
            HEXACOScores: Basic personality scores

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

            # Quality control checks
            self._validate_responses(responses, completion_time)

            # Save responses to database
            response_data = [
                {"item_id": resp.item_id, "response": resp.response}
                for resp in responses
            ]

            self.db_manager.save_responses(session_id, response_data)

            # Calculate basic scores
            basic_scores = self._calculate_basic_scores(responses)

            return basic_scores

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

    def _calculate_basic_scores(self, responses: List[ItemResponse]) -> HEXACOScores:
        """
        Calculate basic Big Five + Honesty-Humility scores.

        This is a simplified implementation for Week 1 MVP.
        Will be replaced with proper psychometric algorithms in Week 2.

        Args:
            responses: Item responses

        Returns:
            HEXACOScores: Calculated personality scores
        """
        # Convert to dictionary for easier lookup
        response_dict = {resp.item_id: resp.response for resp in responses}

        # Define item mappings (simplified for MVP)
        dimension_items = {
            "extraversion": ["ipip_001", "ipip_002", "ipip_003", "ipip_004"],
            "agreeableness": ["ipip_005", "ipip_006", "ipip_007", "ipip_008"],
            "conscientiousness": ["ipip_009", "ipip_010", "ipip_011", "ipip_012"],
            "neuroticism": ["ipip_013", "ipip_014", "ipip_015", "ipip_016"],
            "openness": ["ipip_017", "ipip_018", "ipip_019", "ipip_020"]
        }

        # Calculate dimension scores
        dimension_scores = {}

        for dimension, items in dimension_items.items():
            total_score = 0
            for item_id in items:
                raw_response = response_dict.get(item_id, 4)  # Default to neutral

                # Apply reverse scoring for even-numbered items (simplified)
                if int(item_id.split("_")[1]) % 2 == 0:
                    score = 8 - raw_response  # Reverse 1-7 scale
                else:
                    score = raw_response

                total_score += score

            # Convert to 0-100 scale
            dimension_scores[dimension] = min(100, max(0, int(
                (total_score / (len(items) * 7)) * 100
            )))

        # Calculate Honesty-Humility as combination of Agreeableness and Conscientiousness
        honesty_humility = min(100, max(0, int(
            (dimension_scores["agreeableness"] +
             dimension_scores["conscientiousness"]) / 2
        )))

        return HEXACOScores(
            extraversion=dimension_scores["extraversion"],
            agreeableness=dimension_scores["agreeableness"],
            conscientiousness=dimension_scores["conscientiousness"],
            neuroticism=dimension_scores["neuroticism"],
            openness=dimension_scores["openness"],
            honesty_humility=honesty_humility
        )

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


# Convenience function for dependency injection
def get_assessment_service() -> AssessmentService:
    """Get assessment service instance."""
    return AssessmentService()