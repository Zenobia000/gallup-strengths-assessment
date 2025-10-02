"""
Consent Management API Routes - Gallup Strengths Assessment

Implements privacy consent endpoints following GDPR principles:
- Explicit consent recording
- Clear audit trail
- Automatic expiration
- Privacy-by-design

Follows Linus Torvalds philosophy: simple, focused, and reliable.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse

from models.schemas import (
    ConsentRequest,
    ConsentResponse,
    APIResponse
)
from utils.database import get_database_manager
from core.config import get_settings


router = APIRouter(prefix="/privacy")


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post("/consent", response_model=APIResponse, status_code=201)
async def record_consent(
    consent_request: ConsentRequest,
    request: Request
) -> APIResponse:
    """
    Record user consent for privacy terms.

    This endpoint implements the "privacy by design" principle by:
    1. Recording explicit consent with timestamp
    2. Storing minimal necessary data
    3. Setting automatic expiration
    4. Providing audit trail

    Args:
        consent_request: Consent data from user
        request: HTTP request for metadata

    Returns:
        APIResponse: Consent confirmation with expiry information

    Raises:
        HTTPException: If consent cannot be recorded
    """
    try:
        settings = get_settings()
        db_manager = get_database_manager()

        # Generate unique consent ID
        consent_id = f"consent_{uuid.uuid4().hex[:12]}"

        # Calculate consent expiration (1 year from now)
        agreed_at = datetime.utcnow()
        expires_at = agreed_at + timedelta(days=settings.consent_retention_days)

        # Extract client IP if not provided
        client_ip = consent_request.ip_address or get_client_ip(request)

        # Prepare consent data
        consent_data = {
            "consent_id": consent_id,
            "agreed": consent_request.agreed,
            "user_agent": consent_request.user_agent,
            "ip_address": client_ip,
            "consent_version": consent_request.consent_version,
            "expires_at": expires_at.isoformat()
        }

        # Save consent to database
        db_manager.create_consent(consent_data)

        # Prepare response
        response_data = ConsentResponse(
            consent_id=consent_id,
            agreed_at=agreed_at,
            expires_at=expires_at,
            consent_version=consent_request.consent_version
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

    except Exception as e:
        # Log error for debugging (in production, use proper logging)
        error_id = str(uuid.uuid4())
        print(f"Consent recording error {error_id}: {e}")

        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "PRIVACY_001",
                    "message": "Failed to record consent",
                    "trace_id": error_id
                },
                "meta": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": getattr(request.state, 'request_id', error_id)
                }
            }
        )


@router.get("/consent/{consent_id}", response_model=APIResponse)
async def get_consent_status(
    consent_id: str,
    request: Request
) -> APIResponse:
    """
    Check consent status and validity.

    This endpoint allows verification of consent status without
    exposing sensitive consent details.

    Args:
        consent_id: Unique consent identifier
        request: HTTP request for metadata

    Returns:
        APIResponse: Consent status information

    Raises:
        HTTPException: If consent not found or invalid
    """
    try:
        db_manager = get_database_manager()

        # Query consent from database
        with db_manager.get_connection() as conn:
            cursor = conn.execute("""
                SELECT consent_id, agreed, consent_version, agreed_at, expires_at
                FROM consents
                WHERE consent_id = ?
            """, (consent_id,))

            consent_record = cursor.fetchone()

            if not consent_record:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "success": False,
                        "error": {
                            "code": "CONSENT_NOT_FOUND",
                            "message": "Consent record not found"
                        }
                    }
                )

            # Check if consent has expired
            expires_at = datetime.fromisoformat(consent_record["expires_at"].replace("Z", ""))
            is_expired = expires_at <= datetime.utcnow()

            # Prepare response data
            consent_status = {
                "consent_id": consent_record["consent_id"],
                "is_valid": consent_record["agreed"] and not is_expired,
                "is_expired": is_expired,
                "consent_version": consent_record["consent_version"],
                "agreed_at": consent_record["agreed_at"],
                "expires_at": consent_record["expires_at"]
            }

            return APIResponse(
                success=True,
                data=consent_status,
                meta={
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": getattr(request.state, 'request_id', str(uuid.uuid4())),
                    "version": "v1.0"
                }
            )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        error_id = str(uuid.uuid4())
        print(f"Consent status error {error_id}: {e}")

        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "PRIVACY_002",
                    "message": "Failed to retrieve consent status",
                    "trace_id": error_id
                }
            }
        )


@router.delete("/consent/{consent_id}", response_model=APIResponse)
async def revoke_consent(
    consent_id: str,
    request: Request
) -> APIResponse:
    """
    Revoke user consent (GDPR right to withdraw).

    This endpoint implements the GDPR right to withdraw consent
    by marking consent as revoked and scheduling data deletion.

    Args:
        consent_id: Unique consent identifier
        request: HTTP request for metadata

    Returns:
        APIResponse: Consent revocation confirmation

    Raises:
        HTTPException: If consent cannot be revoked
    """
    try:
        db_manager = get_database_manager()

        with db_manager.get_connection() as conn:
            # Check if consent exists
            cursor = conn.execute("""
                SELECT consent_id FROM consents WHERE consent_id = ?
            """, (consent_id,))

            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail={
                        "success": False,
                        "error": {
                            "code": "CONSENT_NOT_FOUND",
                            "message": "Consent record not found"
                        }
                    }
                )

            # Mark consent as revoked (set agreed to FALSE)
            conn.execute("""
                UPDATE consents
                SET agreed = FALSE,
                    expires_at = CURRENT_TIMESTAMP,
                    revoked_at = CURRENT_TIMESTAMP
                WHERE consent_id = ?
            """, (consent_id,))

            # Also mark associated sessions as expired
            conn.execute("""
                UPDATE sessions
                SET status = 'EXPIRED'
                WHERE consent_id = ? AND status != 'COMPLETED'
            """, (consent_id,))

        return APIResponse(
            success=True,
            data={
                "consent_id": consent_id,
                "revoked_at": datetime.utcnow().isoformat(),
                "message": "Consent has been revoked and associated data will be deleted"
            },
            meta={
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": getattr(request.state, 'request_id', str(uuid.uuid4())),
                "version": "v1.0"
            }
        )

    except HTTPException:
        raise

    except Exception as e:
        error_id = str(uuid.uuid4())
        print(f"Consent revocation error {error_id}: {e}")

        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "PRIVACY_003",
                    "message": "Failed to revoke consent",
                    "trace_id": error_id
                }
            }
        )