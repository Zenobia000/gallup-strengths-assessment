"""
Consent management API endpoints.
Handles GDPR compliance, consent recording, and privacy requests.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.exceptions import (
    BaseCustomException, map_exception_to_http_exception
)
from app.core.security import security_manager
from app.services.consent_service import ConsentService
from app.schemas.consent import (
    ConsentCreate, ConsentResponse, ConsentUpdate, ConsentStatusResponse,
    PrivacyRequestCreate, PrivacyRequestResponse, DataExportResponse, DataErasureResponse
)
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/consent", tags=["consent"])


def get_consent_service(db: AsyncSession = Depends(get_async_db)) -> ConsentService:
    """Dependency to get consent service instance."""
    return ConsentService(db)


@router.post(
    "",
    response_model=ConsentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record user consent",
    description="""
    Record user consent for psychological assessment participation.

    GDPR Compliance Features:
    - Records explicit consent with timestamp
    - Tracks legal basis (Article 6)
    - Supports consent withdrawal
    - Privacy-compliant client information hashing
    - TTL-based automatic expiration

    Required consent types:
    - data_processing: Basic data processing consent
    - psychological_assessment: Assessment participation consent
    - data_retention: Data storage consent

    Optional consent types:
    - research_participation: Anonymous research participation
    - marketing_communication: Marketing communications
    """
)
async def create_consent(
    consent_data: ConsentCreate,
    request: Request,
    consent_service: ConsentService = Depends(get_consent_service)
) -> ConsentResponse:
    """Record user consent for assessment participation."""
    try:
        # Extract client information for compliance logging
        client_info = security_manager.extract_client_info(request)

        # Create consent record
        consent = await consent_service.create_consent(
            session_id=consent_data.session_id,
            consent_types=[ct.value for ct in consent_data.consent_types],
            consent_given=consent_data.consent_given,
            legal_basis=consent_data.legal_basis.value,
            consent_version=consent_data.consent_version,
            client_info=client_info
        )

        return ConsentResponse.from_orm(consent)

    except BaseCustomException as e:
        raise map_exception_to_http_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record consent: {str(e)}"
        )


@router.get(
    "/{consent_id}",
    response_model=ConsentResponse,
    summary="Get consent record",
    description="""
    Retrieve detailed consent record information.

    Returns:
    - Consent details and status
    - Expiration information
    - Withdrawal status
    - Legal basis and version

    Used for consent verification and audit trail purposes.
    """
)
async def get_consent(
    consent_id: int,
    consent_service: ConsentService = Depends(get_consent_service)
) -> ConsentResponse:
    """Get consent record by ID."""
    try:
        consent = await consent_service.get_consent(consent_id)
        return ConsentResponse.from_orm(consent)

    except BaseCustomException as e:
        raise map_exception_to_http_exception(e)


@router.put(
    "/{consent_id}",
    response_model=ConsentResponse,
    summary="Update consent record",
    description="""
    Update existing consent record.

    Common use cases:
    - Withdraw consent (set consent_given to False)
    - Add additional consent types
    - Update consent preferences

    Note: Withdrawal creates an audit trail and cannot be undone.
    """
)
async def update_consent(
    consent_id: int,
    update_data: ConsentUpdate,
    request: Request,
    consent_service: ConsentService = Depends(get_consent_service)
) -> ConsentResponse:
    """Update consent record."""
    try:
        if update_data.consent_given is False:
            # Handle consent withdrawal
            client_info = security_manager.extract_client_info(request)
            consent = await consent_service.withdraw_consent(
                consent_id=consent_id,
                client_info=client_info
            )
        else:
            # Regular update (not implemented for security)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only consent withdrawal is supported via update"
            )

        return ConsentResponse.from_orm(consent)

    except BaseCustomException as e:
        raise map_exception_to_http_exception(e)


@router.delete(
    "/{consent_id}",
    response_model=SuccessResponse[Dict[str, str]],
    summary="Withdraw consent",
    description="""
    Withdraw consent record (GDPR Article 7.3).

    This action:
    - Sets withdrawal timestamp
    - Marks consent as invalid
    - Creates audit trail
    - Cannot be undone

    Use with caution - this may affect ongoing assessments.
    """
)
async def withdraw_consent(
    consent_id: int,
    request: Request,
    consent_service: ConsentService = Depends(get_consent_service)
) -> SuccessResponse[Dict[str, str]]:
    """Withdraw consent record."""
    try:
        client_info = security_manager.extract_client_info(request)
        consent = await consent_service.withdraw_consent(
            consent_id=consent_id,
            client_info=client_info
        )

        return SuccessResponse(
            message="Consent withdrawn successfully",
            data={
                "consent_id": str(consent_id),
                "withdrawn": True,
                "withdrawal_timestamp": consent.withdrawal_timestamp.isoformat()
            }
        )

    except BaseCustomException as e:
        raise map_exception_to_http_exception(e)


@router.get(
    "/session/{session_id}",
    response_model=List[ConsentResponse],
    summary="Get session consent history",
    description="""
    Retrieve all consent records for a specific session.

    Returns chronological list of consent records including:
    - Active consents
    - Withdrawn consents
    - Expired consents

    Useful for compliance reporting and consent audit trails.
    """
)
async def get_session_consents(
    session_id: str,
    consent_service: ConsentService = Depends(get_consent_service)
) -> List[ConsentResponse]:
    """Get all consent records for a session."""
    try:
        consents = await consent_service.get_session_consents(session_id)
        return [ConsentResponse.from_orm(consent) for consent in consents]

    except BaseCustomException as e:
        raise map_exception_to_http_exception(e)


@router.get(
    "/session/{session_id}/status",
    response_model=ConsentStatusResponse,
    summary="Check session consent status",
    description="""
    Get comprehensive consent status for session validation.

    Returns:
    - Overall consent validity
    - Active consent types
    - Withdrawn consent types
    - Expired consent types

    Used for assessment eligibility checks and compliance verification.
    """
)
async def get_session_consent_status(
    session_id: str,
    consent_service: ConsentService = Depends(get_consent_service)
) -> ConsentStatusResponse:
    """Check consent status for a session."""
    try:
        status_info = await consent_service.check_session_consent_status(session_id)
        return ConsentStatusResponse(**status_info)

    except BaseCustomException as e:
        raise map_exception_to_http_exception(e)


@router.post(
    "/{consent_id}/extend",
    response_model=ConsentResponse,
    summary="Extend consent TTL",
    description="""
    Extend consent expiration time.

    Default extension is 24 hours from current time.
    Used to accommodate longer assessment sessions
    or special circumstances requiring extended consent validity.
    """
)
async def extend_consent_ttl(
    consent_id: int,
    hours: int = 24,
    consent_service: ConsentService = Depends(get_consent_service)
) -> ConsentResponse:
    """Extend consent TTL expiration time."""
    try:
        # Validate hours parameter
        if hours < 1 or hours > 168:  # Max 1 week
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Extension hours must be between 1 and 168 (1 week)"
            )

        consent = await consent_service.extend_consent_ttl(consent_id, hours)
        return ConsentResponse.from_orm(consent)

    except BaseCustomException as e:
        raise map_exception_to_http_exception(e)


# GDPR Privacy Request Management

@router.post(
    "/privacy-request",
    response_model=PrivacyRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create GDPR privacy request",
    description="""
    Create GDPR privacy request (Articles 15-21).

    Supported request types:
    - access: Right of access (Article 15)
    - rectification: Right to rectification (Article 16)
    - erasure: Right to erasure / "right to be forgotten" (Article 17)
    - restrict_processing: Right to restrict processing (Article 18)
    - data_portability: Right to data portability (Article 20)
    - object: Right to object (Article 21)

    All requests are logged and processed according to GDPR timelines.
    """
)
async def create_privacy_request(
    request_data: PrivacyRequestCreate,
    consent_service: ConsentService = Depends(get_consent_service)
) -> PrivacyRequestResponse:
    """Create a GDPR privacy request."""
    try:
        privacy_request = await consent_service.create_privacy_request(
            request_type=request_data.request_type.value,
            session_id=request_data.session_id,
            requester_verification=request_data.requester_verification,
            processing_notes=request_data.processing_notes
        )

        return PrivacyRequestResponse.from_orm(privacy_request)

    except BaseCustomException as e:
        raise map_exception_to_http_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create privacy request: {str(e)}"
        )


@router.get(
    "/privacy-request/{request_id}",
    response_model=PrivacyRequestResponse,
    summary="Get privacy request",
    description="Retrieve privacy request details by ID."
)
async def get_privacy_request(
    request_id: int,
    consent_service: ConsentService = Depends(get_consent_service)
) -> PrivacyRequestResponse:
    """Get privacy request by ID."""
    try:
        privacy_request = await consent_service.get_privacy_request(request_id)
        return PrivacyRequestResponse.from_orm(privacy_request)

    except BaseCustomException as e:
        raise map_exception_to_http_exception(e)


@router.post(
    "/privacy-request/access/{session_id}",
    response_model=DataExportResponse,
    summary="Process data access request",
    description="""
    Process GDPR Article 15 - Right of access request.

    Returns comprehensive data export including:
    - Personal data
    - Assessment responses
    - Consent history
    - Privacy request history

    Data is anonymized where required for privacy protection.
    """
)
async def process_data_access_request(
    session_id: str,
    consent_service: ConsentService = Depends(get_consent_service)
) -> DataExportResponse:
    """Process data access request for a session."""
    try:
        export_data = await consent_service.process_data_access_request(session_id)
        return DataExportResponse(**export_data)

    except BaseCustomException as e:
        raise map_exception_to_http_exception(e)


@router.post(
    "/privacy-request/erasure/{session_id}",
    response_model=DataErasureResponse,
    summary="Process data erasure request",
    description="""
    Process GDPR Article 17 - Right to erasure request.

    This action:
    - Permanently deletes assessment data
    - Anonymizes session information
    - Removes consent records
    - Creates erasure verification ID
    - Cannot be undone

    Use with extreme caution - this is irreversible.
    """
)
async def process_data_erasure_request(
    session_id: str,
    consent_service: ConsentService = Depends(get_consent_service)
) -> DataErasureResponse:
    """Process data erasure request for a session."""
    try:
        erasure_data = await consent_service.process_data_erasure_request(session_id)
        return DataErasureResponse(**erasure_data)

    except BaseCustomException as e:
        raise map_exception_to_http_exception(e)


@router.get(
    "/statistics/{session_id}",
    response_model=SuccessResponse[Dict[str, Any]],
    summary="Get consent statistics",
    description="""
    Get consent statistics and compliance metrics for a session.

    Returns:
    - Total consent records
    - Valid/expired/withdrawn counts
    - Compliance rate percentage

    Used for reporting and compliance monitoring.
    """
)
async def get_consent_statistics(
    session_id: str,
    consent_service: ConsentService = Depends(get_consent_service)
) -> SuccessResponse[Dict[str, Any]]:
    """Get consent statistics for a session."""
    try:
        statistics = await consent_service.get_consent_statistics(session_id)
        return SuccessResponse(
            message="Consent statistics retrieved successfully",
            data=statistics
        )

    except BaseCustomException as e:
        raise map_exception_to_http_exception(e)