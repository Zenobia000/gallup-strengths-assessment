"""
Session management service with comprehensive business logic.
Handles session lifecycle, validation, and compliance requirements.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.models.database import AssessmentSession, ConsentRecord, AuditTrail
from app.core.exceptions import (
    SessionNotFoundError, SessionExpiredError, SessionInactiveError,
    ConsentRequiredError, ValidationException
)
from app.core.security import security_manager, audit_logger
from app.core.config import get_settings

settings = get_settings()


class SessionService:
    """
    Session management service with psychology compliance features.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.security_manager = security_manager
        self.audit_logger = audit_logger

    async def create_session(
        self,
        participant_type: str = "individual",
        language: str = "en",
        timezone: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        client_info: Optional[Dict[str, str]] = None
    ) -> AssessmentSession:
        """
        Create a new assessment session with compliance tracking.

        Args:
            participant_type: Type of participant
            language: Language preference
            timezone: Client timezone
            metadata: Additional session metadata
            client_info: Anonymized client information

        Returns:
            AssessmentSession: Created session

        Raises:
            ValidationException: If parameters are invalid
        """
        try:
            # Create new session
            session = AssessmentSession(
                participant_type=participant_type,
                language=language,
                timezone=timezone,
                ip_address_hash=client_info.get("ip_address_hash") if client_info else None,
                user_agent_hash=client_info.get("user_agent_hash") if client_info else None
            )

            # Set metadata if provided
            if metadata:
                session.metadata_dict = metadata

            # Add to database
            self.db.add(session)
            await self.db.commit()
            await self.db.refresh(session)

            # Create audit trail
            await self._create_audit_record(
                session_id=session.session_id,
                action_type="session_created",
                entity_type="session",
                entity_id=session.session_id,
                new_values={
                    "participant_type": participant_type,
                    "language": language,
                    "timezone": timezone
                }
            )

            return session

        except Exception as e:
            await self.db.rollback()
            raise ValidationException(f"Failed to create session: {str(e)}")

    async def get_session(self, session_id: str) -> AssessmentSession:
        """
        Get session by ID with validation.

        Args:
            session_id: Session identifier

        Returns:
            AssessmentSession: Found session

        Raises:
            SessionNotFoundError: If session doesn't exist
            SessionExpiredError: If session has expired
        """
        query = select(AssessmentSession).where(
            AssessmentSession.session_id == session_id
        ).options(
            selectinload(AssessmentSession.consent_records),
            selectinload(AssessmentSession.assessment_responses)
        )

        result = await self.db.execute(query)
        session = result.scalar_one_or_none()

        if not session:
            raise SessionNotFoundError(f"Session {session_id} not found")

        if session.is_expired:
            # Update status to expired
            session.status = "expired"
            await self.db.commit()
            raise SessionExpiredError(f"Session {session_id} has expired")

        return session

    async def update_session(
        self,
        session_id: str,
        status: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AssessmentSession:
        """
        Update session with validation and audit trail.

        Args:
            session_id: Session identifier
            status: New status
            metadata: Updated metadata

        Returns:
            AssessmentSession: Updated session

        Raises:
            SessionNotFoundError: If session doesn't exist
        """
        session = await self.get_session(session_id)
        old_values = {
            "status": session.status,
            "metadata": session.metadata_dict
        }

        if status:
            session.status = status
        if metadata:
            session.metadata_dict = metadata

        session.update_activity()
        await self.db.commit()
        await self.db.refresh(session)

        # Audit trail
        await self._create_audit_record(
            session_id=session_id,
            action_type="data_updated",
            entity_type="session",
            entity_id=session_id,
            old_values=old_values,
            new_values={
                "status": session.status,
                "metadata": session.metadata_dict
            }
        )

        return session

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete session and all related data with audit trail.

        Args:
            session_id: Session identifier

        Returns:
            bool: True if deleted successfully

        Raises:
            SessionNotFoundError: If session doesn't exist
        """
        session = await self.get_session(session_id)

        # Create audit record before deletion
        await self._create_audit_record(
            session_id=session_id,
            action_type="data_deleted",
            entity_type="session",
            entity_id=session_id,
            old_values=session.to_dict(include_sensitive=False)
        )

        # Delete session (cascades to related records)
        await self.db.delete(session)
        await self.db.commit()

        return True

    async def check_session_status(self, session_id: str) -> Dict[str, Any]:
        """
        Check session status with comprehensive information.

        Args:
            session_id: Session identifier

        Returns:
            Dict: Session status information
        """
        session = await self.get_session(session_id)

        return {
            "session_id": session_id,
            "status": session.status,
            "is_expired": session.is_expired,
            "is_active": session.is_active,
            "time_remaining_minutes": session.time_remaining_minutes,
            "can_continue_assessment": session.can_continue_assessment(),
            "has_valid_consent": session.has_valid_consent(),
            "completion_percentage": session.completion_percentage,
            "response_count": session.response_count
        }

    async def validate_session_for_assessment(self, session_id: str) -> AssessmentSession:
        """
        Validate session is ready for assessment activities.

        Args:
            session_id: Session identifier

        Returns:
            AssessmentSession: Validated session

        Raises:
            SessionNotFoundError: If session doesn't exist
            SessionExpiredError: If session has expired
            SessionInactiveError: If session is not active
            ConsentRequiredError: If consent is required but not given
        """
        session = await self.get_session(session_id)

        # Check if session can continue assessment
        if not session.can_continue_assessment():
            if session.status == "completed":
                raise SessionInactiveError("Assessment already completed")
            elif session.status == "abandoned":
                raise SessionInactiveError("Session was abandoned")
            else:
                raise SessionInactiveError(f"Session status '{session.status}' does not allow assessment")

        # Check consent if required
        if settings.consent_required and not session.has_valid_consent():
            raise ConsentRequiredError("Valid consent required to continue assessment")

        return session

    async def extend_session(self, session_id: str, hours: int = 24) -> AssessmentSession:
        """
        Extend session expiration time.

        Args:
            session_id: Session identifier
            hours: Number of hours to extend

        Returns:
            AssessmentSession: Extended session
        """
        session = await self.get_session(session_id)
        old_expires_at = session.expires_at

        session.extend_expiration(hours)
        await self.db.commit()

        # Audit trail
        await self._create_audit_record(
            session_id=session_id,
            action_type="data_updated",
            entity_type="session",
            entity_id=session_id,
            old_values={"expires_at": old_expires_at.isoformat()},
            new_values={"expires_at": session.expires_at.isoformat()}
        )

        return session

    async def get_sessions_by_status(
        self,
        status: str,
        limit: int = 100
    ) -> List[AssessmentSession]:
        """
        Get sessions by status for administrative purposes.

        Args:
            status: Session status to filter by
            limit: Maximum number of sessions to return

        Returns:
            List[AssessmentSession]: Found sessions
        """
        query = select(AssessmentSession).where(
            AssessmentSession.status == status
        ).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions according to TTL policies.

        Returns:
            int: Number of sessions cleaned up
        """
        # Find expired sessions
        query = select(AssessmentSession).where(
            AssessmentSession.expires_at < datetime.utcnow()
        )

        result = await self.db.execute(query)
        expired_sessions = result.scalars().all()

        cleanup_count = 0
        for session in expired_sessions:
            # Update status to expired
            if session.status not in ["expired", "completed"]:
                session.status = "expired"
                cleanup_count += 1

                # Create audit record
                await self._create_audit_record(
                    session_id=session.session_id,
                    action_type="session_expired",
                    entity_type="session",
                    entity_id=session.session_id,
                    new_values={"status": "expired", "reason": "ttl_expiration"}
                )

        if cleanup_count > 0:
            await self.db.commit()

        return cleanup_count

    async def _create_audit_record(
        self,
        session_id: Optional[str],
        action_type: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> None:
        """Create audit trail record."""
        import json

        audit_record = AuditTrail(
            session_id=session_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            success=success,
            error_message=error_message
        )

        self.db.add(audit_record)
        # Note: commit is handled by calling method