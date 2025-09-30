"""
Pydantic schemas for the Gallup Strengths Assessment system.
Request/response validation models.
"""

from .sessions import (
    SessionCreate, SessionResponse, SessionUpdate, SessionStatus
)
from .consent import (
    ConsentCreate, ConsentResponse, ConsentUpdate, ConsentStatusResponse,
    ConsentType, LegalBasis, PrivacyRequestCreate, PrivacyRequestResponse,
    DataExportResponse, DataErasureResponse
)
from .assessments import (
    AssessmentStart, AssessmentResponse, ResponseSubmit, 
    AssessmentProgress, QuestionResponse
)
from .results import (
    StrengthResult, AssessmentResults, ResultsExport
)
from .common import (
    ErrorResponse, SuccessResponse, PaginationParams
)

__all__ = [
    # Sessions
    "SessionCreate", "SessionResponse", "SessionUpdate", "SessionStatus",
    # Consent
    "ConsentCreate", "ConsentResponse", "ConsentUpdate", "ConsentStatusResponse",
    "ConsentType", "LegalBasis", "PrivacyRequestCreate", "PrivacyRequestResponse",
    "DataExportResponse", "DataErasureResponse",
    # Assessments
    "AssessmentStart", "AssessmentResponse", "ResponseSubmit",
    "AssessmentProgress", "QuestionResponse",
    # Results
    "StrengthResult", "AssessmentResults", "ResultsExport",
    # Common
    "ErrorResponse", "SuccessResponse", "PaginationParams"
]