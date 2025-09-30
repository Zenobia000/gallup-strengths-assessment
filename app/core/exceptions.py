"""
Custom exception classes for the Gallup Strengths Assessment system.
Provides psychology-specific and compliance-related error handling.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class BaseCustomException(Exception):
    """Base exception for all custom application exceptions."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


# Database and Connection Exceptions
class DatabaseException(BaseCustomException):
    """Database operation failures."""
    pass


class ConnectionException(BaseCustomException):
    """Database connection failures."""
    pass


# Session Management Exceptions
class SessionException(BaseCustomException):
    """Base class for session-related exceptions."""
    pass


class SessionNotFoundError(SessionException):
    """Session does not exist."""
    pass


class SessionExpiredError(SessionException):
    """Session has expired according to TTL."""
    pass


class SessionInactiveError(SessionException):
    """Session is not in active state."""
    pass


class DuplicateSessionError(SessionException):
    """Attempt to create duplicate session."""
    pass


# Consent Management Exceptions
class ConsentException(BaseCustomException):
    """Base class for consent-related exceptions."""
    pass


class ConsentRequiredError(ConsentException):
    """Required consent not provided."""
    pass


class ConsentWithdrawnError(ConsentException):
    """Consent has been withdrawn."""
    pass


class InvalidConsentTypeError(ConsentException):
    """Invalid consent type specified."""
    pass


class ConsentNotFoundError(ConsentException):
    """Consent record not found."""
    pass


class ConsentValidationError(ConsentException):
    """Consent validation failed."""
    pass


# Assessment Flow Exceptions
class AssessmentException(BaseCustomException):
    """Base class for assessment-related exceptions."""
    pass


class AssessmentNotStartedError(AssessmentException):
    """Assessment has not been started."""
    pass


class AssessmentAlreadyCompletedError(AssessmentException):
    """Assessment has already been completed."""
    pass


class InvalidQuestionError(AssessmentException):
    """Invalid question ID or question not found."""
    pass


class InvalidResponseError(AssessmentException):
    """Invalid response value or format."""
    pass


class AssessmentTimeoutError(AssessmentException):
    """Assessment timed out."""
    pass


class DuplicateResponseError(AssessmentException):
    """Duplicate response to same question."""
    pass


# Results and Calculation Exceptions
class ResultsException(BaseCustomException):
    """Base class for results-related exceptions."""
    pass


class ResultsNotAvailableError(ResultsException):
    """Assessment results not available."""
    pass


class CalculationError(ResultsException):
    """Error in strength score calculation."""
    pass


class InsufficientDataError(ResultsException):
    """Insufficient data for reliable results."""
    pass


# Privacy and Compliance Exceptions
class PrivacyException(BaseCustomException):
    """Base class for privacy-related exceptions."""
    pass


class DataRetentionError(PrivacyException):
    """Data retention policy violation."""
    pass


class PersonalDataError(PrivacyException):
    """Personal data handling violation."""
    pass


class AuditException(PrivacyException):
    """Audit trail or compliance issue."""
    pass


class PrivacyRequestError(PrivacyException):
    """Privacy request processing error."""
    pass


# Validation Exceptions
class ValidationException(BaseCustomException):
    """Base class for validation exceptions."""
    pass


class InvalidParameterError(ValidationException):
    """Invalid parameter value."""
    pass


class MissingParameterError(ValidationException):
    """Required parameter missing."""
    pass


class InvalidFormatError(ValidationException):
    """Invalid data format."""
    pass


# Authentication and Authorization Exceptions
class AuthenticationException(BaseCustomException):
    """Authentication-related exceptions."""
    pass


class AuthorizationException(BaseCustomException):
    """Authorization-related exceptions."""
    pass


# Rate Limiting and Security Exceptions
class SecurityException(BaseCustomException):
    """Security-related exceptions."""
    pass


class RateLimitExceeded(SecurityException):
    """Rate limit exceeded."""
    pass


class SuspiciousActivityError(SecurityException):
    """Suspicious activity detected."""
    pass


# HTTP Exception Mappers
def map_exception_to_http_exception(exc: BaseCustomException) -> HTTPException:
    """
    Map custom exceptions to appropriate HTTP exceptions.

    Args:
        exc: The custom exception to map

    Returns:
        HTTPException: Appropriate HTTP exception
    """
    exception_mapping = {
        # Session exceptions
        SessionNotFoundError: (status.HTTP_404_NOT_FOUND, "Session not found"),
        SessionExpiredError: (status.HTTP_410_GONE, "Session has expired"),
        SessionInactiveError: (status.HTTP_409_CONFLICT, "Session is not active"),
        DuplicateSessionError: (status.HTTP_409_CONFLICT, "Session already exists"),

        # Consent exceptions
        ConsentRequiredError: (status.HTTP_403_FORBIDDEN, "Required consent not provided"),
        ConsentWithdrawnError: (status.HTTP_403_FORBIDDEN, "Consent has been withdrawn"),
        InvalidConsentTypeError: (status.HTTP_400_BAD_REQUEST, "Invalid consent type"),
        ConsentNotFoundError: (status.HTTP_404_NOT_FOUND, "Consent record not found"),
        ConsentValidationError: (status.HTTP_400_BAD_REQUEST, "Consent validation failed"),

        # Assessment exceptions
        AssessmentNotStartedError: (status.HTTP_409_CONFLICT, "Assessment not started"),
        AssessmentAlreadyCompletedError: (status.HTTP_409_CONFLICT, "Assessment already completed"),
        InvalidQuestionError: (status.HTTP_404_NOT_FOUND, "Question not found"),
        InvalidResponseError: (status.HTTP_400_BAD_REQUEST, "Invalid response"),
        AssessmentTimeoutError: (status.HTTP_408_REQUEST_TIMEOUT, "Assessment timed out"),
        DuplicateResponseError: (status.HTTP_409_CONFLICT, "Duplicate response not allowed"),

        # Results exceptions
        ResultsNotAvailableError: (status.HTTP_404_NOT_FOUND, "Results not available"),
        CalculationError: (status.HTTP_500_INTERNAL_SERVER_ERROR, "Calculation error"),
        InsufficientDataError: (status.HTTP_422_UNPROCESSABLE_ENTITY, "Insufficient data"),

        # Privacy exceptions
        DataRetentionError: (status.HTTP_403_FORBIDDEN, "Data retention policy violation"),
        PersonalDataError: (status.HTTP_403_FORBIDDEN, "Personal data handling error"),
        AuditException: (status.HTTP_500_INTERNAL_SERVER_ERROR, "Audit compliance issue"),
        PrivacyRequestError: (status.HTTP_400_BAD_REQUEST, "Privacy request processing error"),

        # Validation exceptions
        InvalidParameterError: (status.HTTP_400_BAD_REQUEST, "Invalid parameter"),
        MissingParameterError: (status.HTTP_400_BAD_REQUEST, "Missing required parameter"),
        InvalidFormatError: (status.HTTP_400_BAD_REQUEST, "Invalid format"),

        # Security exceptions
        RateLimitExceeded: (status.HTTP_429_TOO_MANY_REQUESTS, "Rate limit exceeded"),
        SuspiciousActivityError: (status.HTTP_403_FORBIDDEN, "Suspicious activity detected"),

        # Authentication/Authorization
        AuthenticationException: (status.HTTP_401_UNAUTHORIZED, "Authentication required"),
        AuthorizationException: (status.HTTP_403_FORBIDDEN, "Access denied"),

        # Database exceptions
        DatabaseException: (status.HTTP_500_INTERNAL_SERVER_ERROR, "Database error"),
        ConnectionException: (status.HTTP_503_SERVICE_UNAVAILABLE, "Database connection error"),
    }

    status_code, default_detail = exception_mapping.get(
        type(exc),
        (status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error")
    )

    return HTTPException(
        status_code=status_code,
        detail={
            "error": type(exc).__name__,
            "message": exc.message,
            "details": exc.details
        }
    )


# Psychology-specific validators
class PsychologyValidationError(ValidationException):
    """Psychology assessment-specific validation errors."""
    pass


def validate_response_time(response_time_ms: int) -> None:
    """
    Validate response time for psychological validity.

    Args:
        response_time_ms: Response time in milliseconds

    Raises:
        PsychologyValidationError: If response time is suspicious
    """
    MIN_RESPONSE_TIME = 500  # 500ms minimum for valid human response
    MAX_RESPONSE_TIME = 300000  # 5 minutes maximum

    if response_time_ms < MIN_RESPONSE_TIME:
        raise PsychologyValidationError(
            f"Response time too fast: {response_time_ms}ms (minimum: {MIN_RESPONSE_TIME}ms)",
            {"response_time_ms": response_time_ms, "minimum": MIN_RESPONSE_TIME}
        )

    if response_time_ms > MAX_RESPONSE_TIME:
        raise PsychologyValidationError(
            f"Response time too slow: {response_time_ms}ms (maximum: {MAX_RESPONSE_TIME}ms)",
            {"response_time_ms": response_time_ms, "maximum": MAX_RESPONSE_TIME}
        )


def validate_confidence_level(confidence: Optional[int]) -> None:
    """
    Validate confidence level if provided.

    Args:
        confidence: Confidence level (1-5 scale)

    Raises:
        PsychologyValidationError: If confidence level is invalid
    """
    if confidence is not None and (confidence < 1 or confidence > 5):
        raise PsychologyValidationError(
            f"Invalid confidence level: {confidence} (must be 1-5)",
            {"confidence": confidence}
        )


def validate_session_age(session_created_at: str, max_hours: int = 24) -> None:
    """
    Validate that session is within acceptable age limits.

    Args:
        session_created_at: ISO timestamp of session creation
        max_hours: Maximum allowed hours

    Raises:
        SessionExpiredError: If session is too old
    """
    from datetime import datetime, timedelta

    try:
        created_time = datetime.fromisoformat(session_created_at.replace('Z', '+00:00'))
        max_age = timedelta(hours=max_hours)

        if datetime.now() - created_time > max_age:
            raise SessionExpiredError(
                f"Session expired (created {session_created_at}, max age: {max_hours}h)",
                {"created_at": session_created_at, "max_hours": max_hours}
            )
    except ValueError as e:
        raise InvalidFormatError(
            f"Invalid timestamp format: {session_created_at}",
            {"timestamp": session_created_at, "error": str(e)}
        )


# Context managers for exception handling
class ExceptionContext:
    """Context manager for consistent exception handling."""

    def __init__(self, operation_name: str, session_id: Optional[str] = None):
        self.operation_name = operation_name
        self.session_id = session_id

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and issubclass(exc_type, BaseCustomException):
            # Log the exception for audit purposes
            import logging
            logger = logging.getLogger(__name__)

            logger.error(
                f"Operation {self.operation_name} failed: {exc_val.message}",
                extra={
                    "session_id": self.session_id,
                    "operation": self.operation_name,
                    "exception_type": exc_type.__name__,
                    "details": exc_val.details
                }
            )

        # Don't suppress the exception
        return False