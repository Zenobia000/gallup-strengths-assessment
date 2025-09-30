"""
Session management API endpoints.
Handles session lifecycle, validation, and compliance requirements.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.exceptions import (
    BaseCustomException, map_exception_to_http_exception
)
from app.core.security import security_manager
from app.services.session_service import SessionService
from app.schemas.sessions import (
    SessionCreate, SessionResponse, SessionUpdate, SessionStatusResponse
)
from app.schemas.common import SuccessResponse, ErrorResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])


def get_session_service(db: AsyncSession = Depends(get_async_db)) -> SessionService:
    """Dependency to get session service instance."""
    return SessionService(db)


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new assessment session",
    description="""
    Create a new assessment session for psychological evaluation.

    Features:
    - Automatic session ID generation
    - TTL compliance (24-hour expiration)
    - Client information anonymization
    - Comprehensive audit logging
    - Psychology compliance validation

    The session must be activated and have consent recorded before
    assessment activities can begin.
    """
)
async def create_session(
    session_data: SessionCreate,
    request: Request,
    session_service: SessionService = Depends(get_session_service)
) -> SessionResponse:
    """Create a new assessment session."""
    try:
        # Extract and anonymize client information
        client_info = security_manager.extract_client_info(request)

        # Create session
        session = await session_service.create_session(
            participant_type=session_data.participant_type.value,
            language=session_data.language,
            timezone=session_data.timezone,
            metadata=session_data.metadata,
            client_info=client_info
        )

        return SessionResponse.from_orm(session)

    except BaseCustomException as e:
        raise map_exception_to_http_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    summary="Get session details",
    description="""
    Retrieve comprehensive session information including:
    - Session status and lifecycle data
    - Progress tracking and completion percentage
    - Consent status and compliance information
    - Time remaining before expiration
    - Response count and assessment progress
    """
)
async def get_session(
    session_id: str,
    session_service: SessionService = Depends(get_session_service)
) -> SessionResponse:
    """Get session details by ID."""
    try:
        session = await session_service.get_session(session_id)
        return SessionResponse.from_orm(session)

    except BaseCustomException as e:
        raise map_exception_to_http_exception(e)


@router.put(
    "/{session_id}",
    response_model=SessionResponse,
    summary="Update session",
    description="""
    Update session information with audit trail creation.

    Supports updating:
    - Session status (created -> active -> completed/abandoned)
    - Session metadata for tracking custom information
    - Activity timestamp (automatically updated)

    All updates are logged for compliance and audit purposes.
    """
)
async def update_session(
    session_id: str,
    update_data: SessionUpdate,
    session_service: SessionService = Depends(get_session_service)
) -> SessionResponse:
    """Update session information."""
    try:
        session = await session_service.update_session(
            session_id=session_id,
            status=update_data.status.value if update_data.status else None,
            metadata=update_data.metadata
        )

        return SessionResponse.from_orm(session)

    except BaseCustomException as e:
        raise map_exception_to_http_exception(e)


@router.delete(
    "/{session_id}",
    response_model=SuccessResponse[Dict[str, str]],
    summary="Delete session",
    description="""
    Permanently delete session and all associated data.

    This action:
    - Removes all session data including responses and scores
    - Creates audit trail before deletion
    - Cannot be undone
    - Complies with GDPR "right to erasure"

    Use with caution - this is a destructive operation.
    """
)
async def delete_session(
    session_id: str,
    session_service: SessionService = Depends(get_session_service)
) -> SuccessResponse[Dict[str, str]]:
    """Delete session and all related data."""
    try:
        await session_service.delete_session(session_id)

        return SuccessResponse(
            message="Session deleted successfully",
            data={"session_id": session_id, "deleted": True}
        )

    except BaseCustomException as e:
        raise map_exception_to_http_exception(e)


@router.get(
    "/{session_id}/status",
    response_model=SessionStatusResponse,
    summary="Check session status",
    description="""
    Quick session status check for monitoring and validation.

    Returns lightweight status information including:
    - Current session state and validity
    - Time remaining before expiration
    - Assessment readiness (consent + active status)
    - Progress indicators

    Ideal for periodic status checks and assessment flow validation.
    """
)
async def get_session_status(
    session_id: str,
    session_service: SessionService = Depends(get_session_service)
) -> SessionStatusResponse:
    """Get session status information."""
    try:
        status_info = await session_service.check_session_status(session_id)
        return SessionStatusResponse(**status_info)

    except BaseCustomException as e:
        raise map_exception_to_http_exception(e)


@router.post(
    "/{session_id}/extend",
    response_model=SessionResponse,
    summary="Extend session expiration",
    description="""
    Extend session TTL expiration time.

    Default extension is 24 hours from current time.
    Can be used to prevent session expiration during long assessments
    or to accommodate special circumstances.

    Creates audit trail for compliance tracking.
    """
)
async def extend_session(
    session_id: str,
    hours: int = 24,
    session_service: SessionService = Depends(get_session_service)
) -> SessionResponse:
    """Extend session expiration time."""
    try:
        # Validate hours parameter
        if hours < 1 or hours > 168:  # Max 1 week
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Extension hours must be between 1 and 168 (1 week)"
            )

        session = await session_service.extend_session(session_id, hours)
        return SessionResponse.from_orm(session)

    except BaseCustomException as e:
        raise map_exception_to_http_exception(e)


@router.post(
    "/{session_id}/validate",
    response_model=SuccessResponse[Dict[str, Any]],
    summary="Validate session for assessment",
    description="""
    Comprehensive session validation for assessment readiness.

    Checks:
    - Session existence and validity
    - Expiration status
    - Consent requirements (if enabled)
    - Session state compatibility with assessment activities

    Returns detailed validation results and recommendations.
    Use before starting assessment activities to ensure compliance.
    """
)
async def validate_session_for_assessment(
    session_id: str,
    session_service: SessionService = Depends(get_session_service)
) -> SuccessResponse[Dict[str, Any]]:
    """Validate session is ready for assessment activities."""
    try:
        session = await session_service.validate_session_for_assessment(session_id)

        validation_result = {
            "session_id": session_id,
            "valid": True,
            "status": session.status,
            "can_continue": session.can_continue_assessment(),
            "has_consent": session.has_valid_consent(),
            "time_remaining_minutes": session.time_remaining_minutes,
            "response_count": session.response_count,
            "completion_percentage": session.completion_percentage
        }

        return SuccessResponse(
            message="Session validation successful",
            data=validation_result
        )

    except BaseCustomException as e:
        raise map_exception_to_http_exception(e)


# Note: Exception handlers are managed at the application level in main.py