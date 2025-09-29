"""
Unified Error Handling Middleware - Gallup Strengths Assessment

This module implements comprehensive error handling following Linus Torvalds
philosophy of "good taste" - consistent error responses without exposing
internal implementation details.

Design by Contract (DbC):
- Preconditions: All exceptions are caught and handled appropriately
- Postconditions: Consistent error response format for all API errors
- Invariants: No internal details leaked to clients
"""

import logging
import traceback
from typing import Dict, Any, Optional, Union
from datetime import datetime
import uuid

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DatabaseError
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.config import get_settings

# Configure logger for error handling
logger = logging.getLogger(__name__)


class ErrorResponse:
    """Standardized error response structure."""

    def __init__(
        self,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.request_id = request_id or str(uuid.uuid4())
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response."""
        response = {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "request_id": self.request_id,
                "timestamp": self.timestamp.isoformat()
            }
        }

        if self.details:
            response["error"]["details"] = self.details

        return response


class SecureErrorHandler:
    """Secure error handler that prevents information disclosure."""

    @staticmethod
    def get_request_id(request: Request) -> str:
        """Extract request ID from request state."""
        return getattr(request.state, 'request_id', str(uuid.uuid4()))

    @staticmethod
    def log_error(
        error_type: str,
        error: Exception,
        request: Request,
        additional_context: Optional[Dict] = None
    ) -> None:
        """Log error with full context for debugging."""
        settings = get_settings()
        request_id = SecureErrorHandler.get_request_id(request)

        log_data = {
            "error_type": error_type,
            "error_message": str(error),
            "request_id": request_id,
            "url": str(request.url),
            "method": request.method,
            "user_agent": request.headers.get("user-agent", "unknown"),
            "timestamp": datetime.utcnow().isoformat()
        }

        if additional_context:
            log_data.update(additional_context)

        if settings.debug_mode:
            # In debug mode, include stack trace
            log_data["traceback"] = traceback.format_exc()

        logger.error(f"API Error: {error_type}", extra=log_data)

    @staticmethod
    def handle_validation_error(
        error: Union[RequestValidationError, ValidationError],
        request: Request
    ) -> JSONResponse:
        """Handle Pydantic validation errors securely."""
        SecureErrorHandler.log_error("validation_error", error, request)

        # Extract safe validation error details
        error_details = []
        if hasattr(error, 'errors'):
            for validation_error in error.errors():
                safe_error = {
                    "field": ".".join(str(loc) for loc in validation_error.get("loc", [])),
                    "type": validation_error.get("type", "validation_error"),
                    "message": "Invalid input format or value"
                }
                error_details.append(safe_error)

        error_response = ErrorResponse(
            error_code="VALIDATION_ERROR",
            message="Request validation failed",
            details={"validation_errors": error_details},
            request_id=SecureErrorHandler.get_request_id(request)
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.to_dict()
        )

    @staticmethod
    def handle_database_error(
        error: SQLAlchemyError,
        request: Request
    ) -> JSONResponse:
        """Handle database errors securely."""
        SecureErrorHandler.log_error("database_error", error, request)

        # Determine specific database error type
        if isinstance(error, IntegrityError):
            error_response = ErrorResponse(
                error_code="DATA_INTEGRITY_ERROR",
                message="Data integrity constraint violation",
                request_id=SecureErrorHandler.get_request_id(request)
            )
            status_code = status.HTTP_409_CONFLICT
        elif isinstance(error, DatabaseError):
            error_response = ErrorResponse(
                error_code="DATABASE_ERROR",
                message="Database operation failed",
                request_id=SecureErrorHandler.get_request_id(request)
            )
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        else:
            error_response = ErrorResponse(
                error_code="INTERNAL_ERROR",
                message="An internal error occurred",
                request_id=SecureErrorHandler.get_request_id(request)
            )
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        return JSONResponse(
            status_code=status_code,
            content=error_response.to_dict()
        )

    @staticmethod
    def handle_http_exception(
        error: Union[HTTPException, StarletteHTTPException],
        request: Request
    ) -> JSONResponse:
        """Handle HTTP exceptions with consistent format."""
        SecureErrorHandler.log_error("http_exception", error, request)

        error_response = ErrorResponse(
            error_code=f"HTTP_{error.status_code}",
            message=error.detail if hasattr(error, 'detail') else "HTTP error",
            request_id=SecureErrorHandler.get_request_id(request)
        )

        return JSONResponse(
            status_code=error.status_code,
            content=error_response.to_dict()
        )

    @staticmethod
    def handle_assessment_error(
        error: Exception,
        request: Request
    ) -> JSONResponse:
        """Handle assessment-specific errors."""
        SecureErrorHandler.log_error("assessment_error", error, request)

        # Map specific assessment errors to user-friendly messages
        error_message = str(error)
        if "question_id" in error_message.lower():
            safe_message = "Invalid question identifier"
            error_code = "INVALID_QUESTION"
        elif "response" in error_message.lower():
            safe_message = "Invalid response format"
            error_code = "INVALID_RESPONSE"
        elif "session" in error_message.lower():
            safe_message = "Session not found or expired"
            error_code = "SESSION_ERROR"
        else:
            safe_message = "Assessment processing error"
            error_code = "ASSESSMENT_ERROR"

        error_response = ErrorResponse(
            error_code=error_code,
            message=safe_message,
            request_id=SecureErrorHandler.get_request_id(request)
        )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response.to_dict()
        )

    @staticmethod
    def handle_generic_exception(
        error: Exception,
        request: Request
    ) -> JSONResponse:
        """Handle unexpected exceptions securely."""
        SecureErrorHandler.log_error("unexpected_error", error, request, {
            "error_class": error.__class__.__name__
        })

        error_response = ErrorResponse(
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred",
            request_id=SecureErrorHandler.get_request_id(request)
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.to_dict()
        )


# Exception handler functions for FastAPI
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """FastAPI validation exception handler."""
    return SecureErrorHandler.handle_validation_error(exc, request)


async def http_exception_handler(
    request: Request,
    exc: HTTPException
) -> JSONResponse:
    """FastAPI HTTP exception handler."""
    return SecureErrorHandler.handle_http_exception(exc, request)


async def starlette_http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
) -> JSONResponse:
    """Starlette HTTP exception handler."""
    return SecureErrorHandler.handle_http_exception(exc, request)


async def database_exception_handler(
    request: Request,
    exc: SQLAlchemyError
) -> JSONResponse:
    """Database exception handler."""
    return SecureErrorHandler.handle_database_error(exc, request)


async def generic_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Generic exception handler for unexpected errors."""
    return SecureErrorHandler.handle_generic_exception(exc, request)


# Assessment-specific exception types
class AssessmentError(Exception):
    """Base exception for assessment-related errors."""
    pass


class InvalidQuestionError(AssessmentError):
    """Raised when question ID is invalid."""
    pass


class InvalidResponseError(AssessmentError):
    """Raised when response format or value is invalid."""
    pass


class SessionNotFoundError(AssessmentError):
    """Raised when assessment session is not found."""
    pass


class ScoringError(AssessmentError):
    """Raised when scoring calculation fails."""
    pass


# Exception handler registration helper
def register_error_handlers(app):
    """Register all error handlers with FastAPI app."""
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Assessment-specific handlers
    app.add_exception_handler(AssessmentError, lambda req, exc:
        SecureErrorHandler.handle_assessment_error(exc, req))


# Utility functions for raising errors in application code
def raise_validation_error(message: str, field: Optional[str] = None):
    """Raise a validation error with consistent formatting."""
    if field:
        raise InvalidResponseError(f"Validation failed for field '{field}': {message}")
    else:
        raise InvalidResponseError(f"Validation failed: {message}")


def raise_not_found_error(resource_type: str, resource_id: str):
    """Raise a not found error with consistent formatting."""
    if resource_type == "session":
        raise SessionNotFoundError(f"Session '{resource_id}' not found")
    else:
        raise AssessmentError(f"{resource_type.title()} '{resource_id}' not found")


def raise_scoring_error(operation: str, details: Optional[str] = None):
    """Raise a scoring error with consistent formatting."""
    message = f"Scoring operation '{operation}' failed"
    if details:
        message += f": {details}"
    raise ScoringError(message)