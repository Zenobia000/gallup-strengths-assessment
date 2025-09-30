"""
Security utilities for the Gallup Strengths Assessment system.
Provides hashing, anonymization, and audit logging capabilities.
"""

import hashlib
import json
import logging
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Request

from .config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security constants
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class SecurityManager:
    """
    Centralized security management for the assessment system.
    Handles hashing, anonymization, and audit logging.
    """

    def __init__(self):
        self.settings = get_settings()

    def hash_sensitive_data(self, data: str, salt: Optional[str] = None) -> str:
        """
        Create a secure hash of sensitive data for anonymization.

        Args:
            data: The sensitive data to hash
            salt: Optional salt (generates random if not provided)

        Returns:
            str: Hexadecimal hash string
        """
        if not data:
            return ""

        if not salt:
            salt = secrets.token_hex(16)

        # Use PBKDF2 with SHA-256 for secure hashing
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            data.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100k iterations
        )

        return f"{salt}:{hash_obj.hex()}"

    def anonymize_ip_address(self, ip_address: str) -> str:
        """
        Anonymize IP address by zeroing the last octet for IPv4.

        Args:
            ip_address: IP address to anonymize

        Returns:
            str: Anonymized IP address
        """
        if not ip_address or ip_address == "unknown":
            return "unknown"

        try:
            # Handle IPv4
            parts = ip_address.split('.')
            if len(parts) == 4:
                # Zero out last octet for anonymization
                return f"{parts[0]}.{parts[1]}.{parts[2]}.0"

            # For IPv6 or other formats, just hash them
            return self.hash_sensitive_data(ip_address)[:16]

        except Exception:
            return "unknown"

    def anonymize_user_agent(self, user_agent: str) -> str:
        """
        Anonymize user agent string while preserving some analytical value.

        Args:
            user_agent: User agent string to anonymize

        Returns:
            str: Anonymized user agent hash
        """
        if not user_agent:
            return ""

        # Extract basic browser family and OS for analytics
        # Then hash the full string for privacy
        return self.hash_sensitive_data(user_agent)[:32]

    def generate_session_id(self) -> str:
        """
        Generate a cryptographically secure session ID.

        Returns:
            str: Unique session ID
        """
        return secrets.token_urlsafe(32)

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token.

        Args:
            data: Data to encode in token
            expires_delta: Optional expiration time delta

        Returns:
            str: JWT token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token to verify

        Returns:
            Optional[Dict]: Decoded payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None

    def extract_client_info(self, request: Request) -> Dict[str, str]:
        """
        Extract and anonymize client information from request.

        Args:
            request: FastAPI request object

        Returns:
            Dict: Anonymized client information
        """
        client_ip = "unknown"
        if request.client:
            client_ip = request.client.host

        user_agent = request.headers.get("user-agent", "")

        return {
            "ip_address_hash": self.anonymize_ip_address(client_ip),
            "user_agent_hash": self.anonymize_user_agent(user_agent),
            "original_ip": client_ip if not settings.anonymize_ip_addresses else None,
        }


class AuditLogger:
    """
    Audit logging system for compliance and security monitoring.
    """

    def __init__(self):
        self.logger = logging.getLogger("audit")
        self.security_manager = SecurityManager()

    def log_event(
        self,
        action_type: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        session_id: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        request: Optional[Request] = None
    ) -> None:
        """
        Log an audit event with comprehensive details.

        Args:
            action_type: Type of action performed
            entity_type: Type of entity affected
            entity_id: ID of the specific entity
            session_id: Associated session ID
            old_values: Previous values (for updates)
            new_values: New values (for creates/updates)
            success: Whether the operation succeeded
            error_message: Error message if operation failed
            request: FastAPI request for client info
        """
        try:
            client_info = {}
            if request:
                client_info = self.security_manager.extract_client_info(request)

            audit_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "action_type": action_type,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "session_id": session_id,
                "success": success,
                "error_message": error_message,
                **client_info
            }

            # Only include data changes if they exist and logging is enabled
            if old_values and not settings.log_personal_data:
                # Sanitize personal data from old values
                audit_record["old_values"] = self._sanitize_values(old_values)
            elif old_values:
                audit_record["old_values"] = old_values

            if new_values and not settings.log_personal_data:
                # Sanitize personal data from new values
                audit_record["new_values"] = self._sanitize_values(new_values)
            elif new_values:
                audit_record["new_values"] = new_values

            # Log the audit record
            self.logger.info(
                f"AUDIT: {action_type} on {entity_type}",
                extra=audit_record
            )

        except Exception as e:
            # Never let audit logging break the main flow
            logger.error(f"Audit logging failed: {e}")

    def _sanitize_values(self, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize values to remove or hash personal data.

        Args:
            values: Values dictionary to sanitize

        Returns:
            Dict: Sanitized values
        """
        sensitive_fields = {
            "ip_address", "email", "name", "phone", "address",
            "user_agent", "metadata", "personal_info"
        }

        sanitized = {}
        for key, value in values.items():
            if key.lower() in sensitive_fields:
                if isinstance(value, str):
                    sanitized[key] = self.security_manager.hash_sensitive_data(value)[:16]
                else:
                    sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value

        return sanitized


class SecurityValidator:
    """
    Security validation utilities for request validation.
    """

    @staticmethod
    def validate_session_id(session_id: str) -> bool:
        """
        Validate session ID format and security.

        Args:
            session_id: Session ID to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not session_id or len(session_id) < 32:
            return False

        # Check for URL-safe base64 characters
        import string
        allowed_chars = string.ascii_letters + string.digits + "-_"
        return all(c in allowed_chars for c in session_id)

    @staticmethod
    def validate_request_rate(
        request: Request,
        max_requests_per_minute: int = 60
    ) -> Tuple[bool, Optional[str]]:
        """
        Simple rate limiting validation.

        Args:
            request: FastAPI request object
            max_requests_per_minute: Maximum requests per minute

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        # This is a simple implementation
        # In production, use Redis or similar for distributed rate limiting
        client_ip = "unknown"
        if request.client:
            client_ip = request.client.host

        # For now, we'll just validate the IP format
        if client_ip == "unknown":
            return True, None  # Allow unknown IPs

        # Could implement actual rate limiting here
        return True, None

    @staticmethod
    def detect_suspicious_patterns(
        session_id: str,
        response_times: list[int],
        responses: list[int]
    ) -> Tuple[bool, list[str]]:
        """
        Detect suspicious response patterns that might indicate bot activity.

        Args:
            session_id: Session ID
            response_times: List of response times in milliseconds
            responses: List of response values

        Returns:
            Tuple[bool, list[str]]: (is_suspicious, list of reasons)
        """
        suspicious_indicators = []

        # Check for extremely fast response times
        fast_responses = [rt for rt in response_times if rt < 500]  # Less than 500ms
        if len(fast_responses) > len(response_times) * 0.5:  # More than 50% fast
            suspicious_indicators.append("Too many fast responses (possible bot)")

        # Check for identical response times (very suspicious)
        if len(set(response_times)) == 1 and len(response_times) > 5:
            suspicious_indicators.append("Identical response times (likely automated)")

        # Check for patterns in responses (e.g., all 1s, all 5s, or strict patterns)
        if len(set(responses)) <= 2 and len(responses) > 10:
            suspicious_indicators.append("Limited response variety (possible pattern)")

        # Check for extremely consistent response times
        if response_times and len(response_times) > 10:
            avg_time = sum(response_times) / len(response_times)
            variance = sum((rt - avg_time) ** 2 for rt in response_times) / len(response_times)
            if variance < 100:  # Very low variance
                suspicious_indicators.append("Extremely consistent timing (suspicious)")

        return len(suspicious_indicators) > 0, suspicious_indicators


# Global instances
security_manager = SecurityManager()
audit_logger = AuditLogger()
security_validator = SecurityValidator()


# Convenience functions
def hash_sensitive_data(data: str) -> str:
    """Convenience function for hashing sensitive data."""
    return security_manager.hash_sensitive_data(data)


def anonymize_ip(ip_address: str) -> str:
    """Convenience function for IP anonymization."""
    return security_manager.anonymize_ip_address(ip_address)


def generate_session_id() -> str:
    """Convenience function for session ID generation."""
    return security_manager.generate_session_id()


def log_audit_event(**kwargs) -> None:
    """Convenience function for audit logging."""
    audit_logger.log_event(**kwargs)