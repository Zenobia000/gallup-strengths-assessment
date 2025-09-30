"""
Consent management service for GDPR compliance.
Handles consent recording, validation, and privacy request processing.
"""

import hashlib
import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.models.database.consent_records import ConsentRecord
from app.models.database.privacy_requests import PrivacyRequest
from app.models.database.assessment_sessions import AssessmentSession
from app.models.database.assessment_responses import AssessmentResponse
from app.models.database.strength_scores import StrengthScore
from app.core.exceptions import (
    ConsentNotFoundError, ConsentValidationError, PrivacyRequestError
)


class ConsentService:
    """Service for managing consent and privacy compliance."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_consent(
        self,
        session_id: str,
        consent_types: List[str],
        consent_given: bool = True,
        legal_basis: str = "consent",
        consent_version: str = "1.0",
        client_info: Optional[Dict[str, Any]] = None
    ) -> ConsentRecord:
        """Create a new consent record."""
        # Validate session exists
        session_result = await self.db.execute(
            select(AssessmentSession).where(AssessmentSession.session_id == session_id)
        )
        session = session_result.scalar_one_or_none()

        if not session:
            raise ConsentValidationError(f"Session {session_id} not found")

        # Hash client information for privacy compliance
        ip_hash = None
        user_agent_hash = None

        if client_info:
            if client_info.get('ip_address'):
                ip_hash = hashlib.sha256(
                    client_info['ip_address'].encode('utf-8')
                ).hexdigest()
            if client_info.get('user_agent'):
                user_agent_hash = hashlib.sha256(
                    client_info['user_agent'].encode('utf-8')
                ).hexdigest()

        # Create consent record
        consent_record = ConsentRecord(
            session_id=session_id,
            consent_types=json.dumps(consent_types),
            consent_given=consent_given,
            legal_basis=legal_basis,
            consent_version=consent_version,
            ip_address_hash=ip_hash,
            user_agent_hash=user_agent_hash
        )

        self.db.add(consent_record)
        await self.db.commit()
        await self.db.refresh(consent_record)

        return consent_record

    async def get_consent(self, consent_id: int) -> ConsentRecord:
        """Get consent record by ID."""
        result = await self.db.execute(
            select(ConsentRecord)
            .where(ConsentRecord.consent_id == consent_id)
            .options(selectinload(ConsentRecord.session))
        )
        consent = result.scalar_one_or_none()

        if not consent:
            raise ConsentNotFoundError(f"Consent record {consent_id} not found")

        return consent

    async def get_session_consents(self, session_id: str) -> List[ConsentRecord]:
        """Get all consent records for a session."""
        result = await self.db.execute(
            select(ConsentRecord)
            .where(ConsentRecord.session_id == session_id)
            .order_by(ConsentRecord.consent_timestamp.desc())
        )
        return result.scalars().all()

    async def withdraw_consent(
        self,
        consent_id: int,
        client_info: Optional[Dict[str, Any]] = None
    ) -> ConsentRecord:
        """Withdraw consent record."""
        consent = await self.get_consent(consent_id)

        # Validate consent can be withdrawn
        if consent.is_withdrawn:
            raise ConsentValidationError("Consent has already been withdrawn")

        # Withdraw consent
        consent.withdraw_consent()

        await self.db.commit()
        await self.db.refresh(consent)

        return consent

    async def check_session_consent_status(self, session_id: str) -> Dict[str, Any]:
        """Check comprehensive consent status for a session."""
        consents = await self.get_session_consents(session_id)

        active_consents = []
        withdrawn_consents = []
        expired_consents = []

        for consent in consents:
            consent_types = consent.consent_types_list

            if consent.is_withdrawn:
                withdrawn_consents.extend(consent_types)
            elif consent.is_expired:
                expired_consents.extend(consent_types)
            elif consent.is_valid:
                active_consents.extend(consent_types)

        # Remove duplicates while preserving order
        active_consents = list(dict.fromkeys(active_consents))
        withdrawn_consents = list(dict.fromkeys(withdrawn_consents))
        expired_consents = list(dict.fromkeys(expired_consents))

        has_valid_consent = len(active_consents) > 0

        return {
            "session_id": session_id,
            "has_valid_consent": has_valid_consent,
            "consent_count": len(consents),
            "active_consents": active_consents,
            "withdrawn_consents": withdrawn_consents,
            "expired_consents": expired_consents
        }

    async def extend_consent_ttl(
        self,
        consent_id: int,
        hours: int = 24
    ) -> ConsentRecord:
        """Extend consent TTL expiration time."""
        consent = await self.get_consent(consent_id)

        if consent.is_withdrawn:
            raise ConsentValidationError("Cannot extend withdrawn consent")

        consent.extend_ttl(hours)

        await self.db.commit()
        await self.db.refresh(consent)

        return consent

    # Privacy Request Management

    async def create_privacy_request(
        self,
        request_type: str,
        session_id: Optional[str] = None,
        requester_verification: Optional[str] = None,
        processing_notes: Optional[str] = None
    ) -> PrivacyRequest:
        """Create a new privacy request."""
        # Validate session exists if provided
        if session_id:
            session_result = await self.db.execute(
                select(AssessmentSession).where(AssessmentSession.session_id == session_id)
            )
            session = session_result.scalar_one_or_none()

            if not session:
                raise PrivacyRequestError(f"Session {session_id} not found")

        privacy_request = PrivacyRequest(
            session_id=session_id,
            request_type=request_type,
            requester_verification=requester_verification,
            processing_notes=processing_notes
        )

        self.db.add(privacy_request)
        await self.db.commit()
        await self.db.refresh(privacy_request)

        return privacy_request

    async def get_privacy_request(self, request_id: int) -> PrivacyRequest:
        """Get privacy request by ID."""
        result = await self.db.execute(
            select(PrivacyRequest)
            .where(PrivacyRequest.request_id == request_id)
            .options(selectinload(PrivacyRequest.session))
        )
        request = result.scalar_one_or_none()

        if not request:
            raise PrivacyRequestError(f"Privacy request {request_id} not found")

        return request

    async def process_data_access_request(self, session_id: str) -> Dict[str, Any]:
        """Process GDPR Article 15 - Right of access request."""
        # Get session data
        session_result = await self.db.execute(
            select(AssessmentSession)
            .where(AssessmentSession.session_id == session_id)
            .options(
                selectinload(AssessmentSession.consent_records),
                selectinload(AssessmentSession.assessment_responses),
                selectinload(AssessmentSession.strength_scores),
                selectinload(AssessmentSession.privacy_requests)
            )
        )
        session = session_result.scalar_one_or_none()

        if not session:
            raise PrivacyRequestError(f"Session {session_id} not found")

        # Compile personal data
        personal_data = session.to_dict(include_sensitive=False)

        # Assessment data (anonymized where needed)
        assessment_data = None
        if session.assessment_responses:
            assessment_data = {
                "responses": [
                    {
                        "question_id": resp.question_id,
                        "selected_option": resp.selected_option,
                        "response_time_ms": resp.response_time_ms,
                        "answered_at": resp.answered_at.isoformat()
                    }
                    for resp in session.assessment_responses
                ],
                "completion_percentage": session.completion_percentage
            }

        # Consent history
        consent_history = [
            consent.to_dict(include_sensitive=False)
            for consent in session.consent_records
        ]

        # Privacy requests history
        privacy_requests = [
            request.to_dict()
            for request in session.privacy_requests
        ]

        return {
            "session_id": session_id,
            "export_timestamp": datetime.utcnow(),
            "data_types": ["personal_data", "assessment_data", "consent_history", "privacy_requests"],
            "personal_data": personal_data,
            "assessment_data": assessment_data,
            "consent_history": consent_history,
            "privacy_requests": privacy_requests
        }

    async def process_data_erasure_request(self, session_id: str) -> Dict[str, Any]:
        """Process GDPR Article 17 - Right to erasure request."""
        # Get session with all related data
        session_result = await self.db.execute(
            select(AssessmentSession)
            .where(AssessmentSession.session_id == session_id)
            .options(
                selectinload(AssessmentSession.consent_records),
                selectinload(AssessmentSession.assessment_responses),
                selectinload(AssessmentSession.strength_scores),
                selectinload(AssessmentSession.privacy_requests),
                selectinload(AssessmentSession.audit_trails)
            )
        )
        session = session_result.scalar_one_or_none()

        if not session:
            raise PrivacyRequestError(f"Session {session_id} not found")

        # Generate erasure verification ID
        erasure_verification_id = str(uuid.uuid4())

        erased_data_types = []

        # Delete/anonymize related data
        if session.assessment_responses:
            for response in session.assessment_responses:
                await self.db.delete(response)
            erased_data_types.append("assessment_responses")

        if session.strength_scores:
            for score in session.strength_scores:
                await self.db.delete(score)
            erased_data_types.append("strength_scores")

        if session.consent_records:
            for consent in session.consent_records:
                await self.db.delete(consent)
            erased_data_types.append("consent_records")

        if session.privacy_requests:
            for request in session.privacy_requests:
                await self.db.delete(request)
            erased_data_types.append("privacy_requests")

        # Anonymize session data instead of complete deletion
        session.ip_address_hash = f"ERASED_{erasure_verification_id}"
        session.user_agent_hash = f"ERASED_{erasure_verification_id}"
        session.session_metadata = json.dumps({"erased": True, "erasure_id": erasure_verification_id})

        erased_data_types.append("session_personal_data")

        await self.db.commit()

        return {
            "session_id": session_id,
            "erasure_timestamp": datetime.utcnow(),
            "erased_data_types": erased_data_types,
            "anonymization_applied": True,
            "erasure_verification_id": erasure_verification_id
        }

    async def update_privacy_request_status(
        self,
        request_id: int,
        status: str,
        processing_notes: Optional[str] = None
    ) -> PrivacyRequest:
        """Update privacy request status."""
        request = await self.get_privacy_request(request_id)

        request.status = status
        if processing_notes:
            request.processing_notes = processing_notes

        if status in ["completed", "rejected"]:
            request.processed_timestamp = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(request)

        return request

    async def cleanup_expired_consents(self) -> int:
        """Clean up expired consent records (maintenance task)."""
        # Find expired consents
        result = await self.db.execute(
            select(ConsentRecord)
            .where(ConsentRecord.ttl_expires_at < datetime.utcnow())
        )
        expired_consents = result.scalars().all()

        count = len(expired_consents)

        # Mark as expired but keep for audit purposes
        for consent in expired_consents:
            consent.consent_given = False

        await self.db.commit()

        return count

    async def get_consent_statistics(self, session_id: str) -> Dict[str, Any]:
        """Get consent statistics for a session."""
        consents = await self.get_session_consents(session_id)

        total_consents = len(consents)
        valid_consents = sum(1 for c in consents if c.is_valid)
        expired_consents = sum(1 for c in consents if c.is_expired)
        withdrawn_consents = sum(1 for c in consents if c.is_withdrawn)

        return {
            "session_id": session_id,
            "total_consents": total_consents,
            "valid_consents": valid_consents,
            "expired_consents": expired_consents,
            "withdrawn_consents": withdrawn_consents,
            "compliance_rate": (valid_consents / total_consents) * 100 if total_consents > 0 else 0
        }