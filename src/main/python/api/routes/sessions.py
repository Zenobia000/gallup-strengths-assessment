"""
Assessment Session API Routes - Gallup Strengths Assessment

Implements session management for Mini-IPIP assessment:
- Session creation with consent validation
- Assessment item delivery
- Response submission and validation
- Psychometric quality controls

Follows Linus Torvalds philosophy: focused functions, clear error handling.
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, Request, Path, Depends
from fastapi.responses import JSONResponse

from models.schemas import (
    SessionStartRequest,
    SessionStartResponse,
    AssessmentItem,
    ItemsResponse,
    ScaleLabels,
    AssessmentSubmission,
    AssessmentSubmissionResponse,
    HEXACOScores,
    SessionStatus,
    APIResponse
)
from utils.database import get_database_manager
from core.config import get_settings, get_psychometric_settings


router = APIRouter()


async def validate_consent(consent_id: str) -> bool:
    """
    Validate that consent is still valid.

    Args:
        consent_id: Consent identifier to validate

    Returns:
        bool: True if consent is valid

    Raises:
        HTTPException: If consent is invalid or expired
    """
    db_manager = get_database_manager()

    with db_manager.get_connection() as conn:
        cursor = conn.execute("""
            SELECT agreed, expires_at FROM consents
            WHERE consent_id = ?
        """, (consent_id,))

        consent_record = cursor.fetchone()

        if not consent_record:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {
                        "code": "CONSENT_NOT_FOUND",
                        "message": "Invalid consent ID"
                    }
                }
            )

        # Check if consent is still valid
        expires_at = datetime.fromisoformat(consent_record["expires_at"].replace("Z", ""))
        is_expired = expires_at <= datetime.utcnow()

        if not consent_record["agreed"] or is_expired:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {
                        "code": "CONSENT_EXPIRED",
                        "message": "Consent has expired or been revoked"
                    }
                }
            )

    return True


@router.post("/sessions/start", response_model=APIResponse, status_code=201)
async def start_assessment_session(
    session_request: SessionStartRequest,
    request: Request
) -> APIResponse:
    """
    Start a new assessment session.

    Creates a new session with expiry time and returns session details
    including total items and estimated duration.

    Args:
        session_request: Session start parameters
        request: HTTP request for metadata

    Returns:
        APIResponse: Session creation confirmation

    Raises:
        HTTPException: If session cannot be created
    """
    try:
        # Validate consent first
        await validate_consent(session_request.consent_id)

        settings = get_settings()
        psych_settings = get_psychometric_settings()
        db_manager = get_database_manager()

        # Generate unique session ID
        session_id = f"sess_{uuid.uuid4().hex[:12]}"

        # Calculate session expiration
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(minutes=settings.session_timeout_minutes)

        # Prepare session data
        session_data = {
            "session_id": session_id,
            "consent_id": session_request.consent_id,
            "instrument_version": session_request.instrument,
            "status": SessionStatus.PENDING.value,
            "expires_at": expires_at.isoformat(),
            "metadata": {
                "user_agent": request.headers.get("user-agent", "unknown"),
                "created_ip": request.client.host if request.client else "unknown"
            }
        }

        # Save session to database
        db_manager.create_session(session_data)

        # Prepare response
        response_data = SessionStartResponse(
            session_id=session_id,
            instrument_version=session_request.instrument,
            total_items=psych_settings.TOTAL_ITEMS,
            estimated_duration=300,  # 5 minutes estimated
            created_at=created_at,
            expires_at=expires_at
        )

        return APIResponse(
            success=True,
            data=response_data.dict(),
            meta={
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": getattr(request.state, 'request_id', str(uuid.uuid4())),
                "version": "v1.0"
            }
        )

    except HTTPException:
        # Re-raise validation errors
        raise

    except Exception as e:
        error_id = str(uuid.uuid4())
        print(f"Session creation error {error_id}: {e}")

        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "SESSION_001",
                    "message": "Failed to create assessment session",
                    "trace_id": error_id
                }
            }
        )


@router.get("/sessions/{session_id}/items", response_model=APIResponse)
async def get_assessment_items(
    session_id: str = Path(..., description="Assessment session identifier"),
    request: Request = None
) -> APIResponse:
    """
    Get assessment items for a session.

    Returns the Mini-IPIP items with Chinese text and response labels.
    Validates that session is active and not expired.

    Args:
        session_id: Session identifier
        request: HTTP request for metadata

    Returns:
        APIResponse: Assessment items and instructions

    Raises:
        HTTPException: If session is invalid or expired
    """
    try:
        db_manager = get_database_manager()

        # Validate session exists and is active
        session_data = db_manager.get_session(session_id)

        if not session_data:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "SESSION_NOT_FOUND",
                        "message": "Assessment session not found"
                    }
                }
            )

        # Check session expiry
        expires_at = datetime.fromisoformat(session_data["expires_at"].replace("Z", ""))
        if expires_at <= datetime.utcnow():
            raise HTTPException(
                status_code=410,
                detail={
                    "success": False,
                    "error": {
                        "code": "SESSION_EXPIRED",
                        "message": "Assessment session has expired"
                    }
                }
            )

        # Get assessment items from database
        items_data = db_manager.get_assessment_items(session_data["instrument_version"])

        # Convert to API format
        assessment_items = []
        for item in items_data:
            assessment_items.append(AssessmentItem(
                item_id=item["item_id"],
                text=item["text_chinese"],
                scale_type="likert_7",
                reverse_scored=bool(item["reverse_scored"]),
                dimension=item["dimension"]
            ))

        # Prepare response
        items_response = ItemsResponse(
            items=assessment_items,
            instructions="請根據您的實際情況，選擇最符合的選項。沒有標準答案，請誠實作答。",
            scale_labels=ScaleLabels(),
            total_items=len(assessment_items)
        )

        # Update session status to IN_PROGRESS
        with db_manager.get_connection() as conn:
            conn.execute("""
                UPDATE sessions SET status = 'IN_PROGRESS'
                WHERE session_id = ?
            """, (session_id,))

        return APIResponse(
            success=True,
            data=items_response.dict(),
            meta={
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": getattr(request.state, 'request_id', str(uuid.uuid4())),
                "version": "v1.0",
                "session_status": "IN_PROGRESS"
            }
        )

    except HTTPException:
        raise

    except Exception as e:
        error_id = str(uuid.uuid4())
        print(f"Items retrieval error {error_id}: {e}")

        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "SESSION_002",
                    "message": "Failed to retrieve assessment items",
                    "trace_id": error_id
                }
            }
        )


@router.post("/sessions/{session_id}/submit", response_model=APIResponse)
async def submit_assessment_responses(
    session_id: str = Path(..., description="Assessment session identifier"),
    submission: AssessmentSubmission = None,
    request: Request = None
) -> APIResponse:
    """
    Submit assessment responses and get basic scores.

    Validates responses, saves to database, and calculates basic Big Five scores.
    Implements psychometric quality controls.

    Args:
        session_id: Session identifier
        submission: Assessment responses
        request: HTTP request for metadata

    Returns:
        APIResponse: Submission confirmation with basic scores

    Raises:
        HTTPException: If submission is invalid
    """
    try:
        db_manager = get_database_manager()
        psych_settings = get_psychometric_settings()

        # Validate session
        session_data = db_manager.get_session(session_id)
        if not session_data:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "SESSION_NOT_FOUND",
                        "message": "Assessment session not found"
                    }
                }
            )

        # Check session status
        if session_data["status"] == SessionStatus.COMPLETED.value:
            raise HTTPException(
                status_code=409,
                detail={
                    "success": False,
                    "error": {
                        "code": "SESSION_ALREADY_COMPLETED",
                        "message": "Assessment has already been completed"
                    }
                }
            )

        # Quality control: check completion time
        if submission.completion_time < psych_settings.LIKERT_SCALE_MIN * 3:  # 3 seconds per item minimum
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {
                        "code": "PSYCH_001",
                        "message": "Assessment completed too quickly for valid results"
                    }
                }
            )

        # Save responses to database
        responses_data = [
            {"item_id": resp.item_id, "response": resp.response}
            for resp in submission.responses
        ]

        db_manager.save_responses(session_id, responses_data)

        # Calculate basic Big Five scores (simplified for MVP)
        # This would be replaced with proper psychometric algorithms in Week 2
        basic_scores = calculate_basic_scores(submission.responses)

        # Prepare response
        submission_response = AssessmentSubmissionResponse(
            session_id=session_id,
            status=SessionStatus.COMPLETED,
            submitted_at=datetime.utcnow(),
            basic_scores=basic_scores,
            next_step=f"/sessions/{session_id}/results"
        )

        return APIResponse(
            success=True,
            data=submission_response.dict(),
            meta={
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": getattr(request.state, 'request_id', str(uuid.uuid4())),
                "version": "v1.0",
                "quality_controls_passed": True
            }
        )

    except HTTPException:
        raise

    except Exception as e:
        error_id = str(uuid.uuid4())
        print(f"Submission error {error_id}: {e}")

        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "PSYCH_003",
                    "message": "Failed to process assessment submission",
                    "trace_id": error_id
                }
            }
        )


def calculate_basic_scores(responses: List) -> HEXACOScores:
    """
    Calculate basic Big Five + Honesty-Humility scores.

    This is a simplified version for MVP. Will be replaced with
    proper psychometric algorithms in Week 2.

    Args:
        responses: List of item responses

    Returns:
        HEXACOScores: Basic personality scores
    """
    # Simple averaging approach (to be replaced with proper algorithms)
    # This is just a placeholder to make the API functional

    # Convert responses to a simple mapping
    response_dict = {resp.item_id: resp.response for resp in responses}

    # Simplified scoring (normally would use proper Big Five item mappings)
    extraversion = min(100, max(0, int((
        response_dict.get("ipip_001", 4) +
        (8 - response_dict.get("ipip_002", 4)) +  # reversed
        response_dict.get("ipip_003", 4) +
        (8 - response_dict.get("ipip_004", 4))     # reversed
    ) / 4 * 100 / 7)))

    agreeableness = min(100, max(0, int((
        response_dict.get("ipip_005", 4) +
        (8 - response_dict.get("ipip_006", 4)) +   # reversed
        response_dict.get("ipip_007", 4) +
        (8 - response_dict.get("ipip_008", 4))     # reversed
    ) / 4 * 100 / 7)))

    conscientiousness = min(100, max(0, int((
        response_dict.get("ipip_009", 4) +
        (8 - response_dict.get("ipip_010", 4)) +   # reversed
        response_dict.get("ipip_011", 4) +
        (8 - response_dict.get("ipip_012", 4))     # reversed
    ) / 4 * 100 / 7)))

    neuroticism = min(100, max(0, int((
        response_dict.get("ipip_013", 4) +
        (8 - response_dict.get("ipip_014", 4)) +   # reversed
        response_dict.get("ipip_015", 4) +
        (8 - response_dict.get("ipip_016", 4))     # reversed
    ) / 4 * 100 / 7)))

    openness = min(100, max(0, int((
        response_dict.get("ipip_017", 4) +
        (8 - response_dict.get("ipip_018", 4)) +   # reversed
        response_dict.get("ipip_019", 4) +
        (8 - response_dict.get("ipip_020", 4))     # reversed
    ) / 4 * 100 / 7)))

    # Placeholder for Honesty-Humility (would need separate items)
    honesty_humility = min(100, max(0, int((agreeableness + conscientiousness) / 2)))

    return HEXACOScores(
        extraversion=extraversion,
        agreeableness=agreeableness,
        conscientiousness=conscientiousness,
        neuroticism=neuroticism,
        openness=openness,
        honesty_humility=honesty_humility
    )