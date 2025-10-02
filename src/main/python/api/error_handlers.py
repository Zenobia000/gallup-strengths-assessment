"""
Standardized Error Handling

統一的錯誤處理系統：
- 全域異常捕獲
- 結構化錯誤回應
- 日誌記錄標準化
- 用戶友善的錯誤訊息

Linus 原則：錯誤要明確，快速失敗，易於除錯
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging
import traceback
import uuid

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class ErrorCode:
    """標準化錯誤代碼"""
    # 客戶端錯誤 (4xx)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_SESSION = "INVALID_SESSION"
    MISSING_CONSENT = "MISSING_CONSENT"
    DUPLICATE_RESPONSE = "DUPLICATE_RESPONSE"
    INSUFFICIENT_RESPONSES = "INSUFFICIENT_RESPONSES"

    # 伺服器錯誤 (5xx)
    SCORING_ENGINE_ERROR = "SCORING_ENGINE_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"

    # 業務邏輯錯誤 (422)
    PSYCHOMETRIC_VIOLATION = "PSYCHOMETRIC_VIOLATION"
    QUALITY_CHECK_FAILED = "QUALITY_CHECK_FAILED"
    ARCHETYPE_ANALYSIS_FAILED = "ARCHETYPE_ANALYSIS_FAILED"


class StandardizedError:
    """標準化錯誤格式"""

    @staticmethod
    def create_error_response(
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500,
        trace_id: Optional[str] = None
    ) -> JSONResponse:
        """創建標準化錯誤回應"""

        error_response = {
            "success": False,
            "data": None,
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
                "trace_id": trace_id or str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat()
            },
            "meta": {
                "api_version": "v4.0",
                "timestamp": datetime.utcnow().isoformat()
            }
        }

        return JSONResponse(
            content=error_response,
            status_code=status_code,
            headers={
                "X-Error-Code": code,
                "X-Trace-ID": error_response["error"]["trace_id"]
            }
        )


class GlobalExceptionHandler:
    """全域異常處理器"""

    @staticmethod
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        """處理 Pydantic 驗證錯誤"""
        trace_id = str(uuid.uuid4())

        logger.warning(f"Validation error [{trace_id}]: {exc.errors()}", extra={
            "url": str(request.url),
            "method": request.method,
            "trace_id": trace_id
        })

        # 整理驗證錯誤詳情
        error_details = {
            "validation_errors": [],
            "invalid_fields": []
        }

        for error in exc.errors():
            field_path = " -> ".join(str(loc) for loc in error["loc"])
            error_details["validation_errors"].append({
                "field": field_path,
                "message": error["msg"],
                "type": error["type"]
            })
            error_details["invalid_fields"].append(field_path)

        return StandardizedError.create_error_response(
            code=ErrorCode.VALIDATION_ERROR,
            message="請求資料格式錯誤，請檢查輸入參數",
            details=error_details,
            status_code=422,
            trace_id=trace_id
        )

    @staticmethod
    async def http_exception_handler(request: Request, exc: HTTPException):
        """處理 HTTP 異常"""
        trace_id = str(uuid.uuid4())

        logger.warning(f"HTTP exception [{trace_id}]: {exc.detail}", extra={
            "status_code": exc.status_code,
            "url": str(request.url),
            "method": request.method,
            "trace_id": trace_id
        })

        # 映射常見 HTTP 狀態碼到業務錯誤碼
        code_mapping = {
            404: ErrorCode.INVALID_SESSION,
            401: ErrorCode.MISSING_CONSENT,
            409: ErrorCode.DUPLICATE_RESPONSE,
            422: ErrorCode.PSYCHOMETRIC_VIOLATION,
            503: ErrorCode.SERVICE_UNAVAILABLE
        }

        error_code = code_mapping.get(exc.status_code, ErrorCode.INTERNAL_ERROR)

        return StandardizedError.create_error_response(
            code=error_code,
            message=str(exc.detail),
            details={"http_status": exc.status_code},
            status_code=exc.status_code,
            trace_id=trace_id
        )

    @staticmethod
    async def general_exception_handler(request: Request, exc: Exception):
        """處理一般異常"""
        trace_id = str(uuid.uuid4())

        logger.error(f"Unhandled exception [{trace_id}]: {str(exc)}", extra={
            "url": str(request.url),
            "method": request.method,
            "trace_id": trace_id,
            "traceback": traceback.format_exc()
        })

        # 根據異常類型映射錯誤碼
        if "database" in str(exc).lower():
            error_code = ErrorCode.DATABASE_ERROR
            message = "資料庫操作失敗，請稍後重試"
        elif "scoring" in str(exc).lower():
            error_code = ErrorCode.SCORING_ENGINE_ERROR
            message = "計分引擎錯誤，請檢查評測資料"
        else:
            error_code = ErrorCode.INTERNAL_ERROR
            message = "系統內部錯誤，請聯繫技術支援"

        return StandardizedError.create_error_response(
            code=error_code,
            message=message,
            details={
                "exception_type": type(exc).__name__,
                "exception_message": str(exc)
            },
            status_code=500,
            trace_id=trace_id
        )


class BusinessLogicError(Exception):
    """業務邏輯異常基類"""

    def __init__(self, code: str, message: str, details: Dict[str, Any] = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class PsychometricError(BusinessLogicError):
    """心理測量相關錯誤"""

    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(ErrorCode.PSYCHOMETRIC_VIOLATION, message, details)


class ScoringEngineError(BusinessLogicError):
    """計分引擎錯誤"""

    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(ErrorCode.SCORING_ENGINE_ERROR, message, details)


class ArchetypeAnalysisError(BusinessLogicError):
    """職業原型分析錯誤"""

    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(ErrorCode.ARCHETYPE_ANALYSIS_FAILED, message, details)


def setup_error_handlers(app):
    """設定全域錯誤處理器"""

    # 註冊異常處理器
    app.add_exception_handler(RequestValidationError, GlobalExceptionHandler.validation_error_handler)
    app.add_exception_handler(HTTPException, GlobalExceptionHandler.http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, GlobalExceptionHandler.http_exception_handler)
    app.add_exception_handler(Exception, GlobalExceptionHandler.general_exception_handler)

    # 註冊業務邏輯異常處理器
    @app.exception_handler(BusinessLogicError)
    async def business_logic_error_handler(request: Request, exc: BusinessLogicError):
        trace_id = str(uuid.uuid4())

        logger.warning(f"Business logic error [{trace_id}]: {exc.message}", extra={
            "error_code": exc.code,
            "url": str(request.url),
            "method": request.method,
            "trace_id": trace_id
        })

        return StandardizedError.create_error_response(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            status_code=422,
            trace_id=trace_id
        )

    logger.info("✅ 全域錯誤處理器已設定")


# 錯誤處理裝飾器
def handle_service_errors(error_code: str = ErrorCode.INTERNAL_ERROR):
    """服務層錯誤處理裝飾器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except BusinessLogicError:
                raise  # 業務邏輯錯誤直接向上傳播
            except Exception as e:
                logger.error(f"Service error in {func.__name__}: {str(e)}")
                raise BusinessLogicError(error_code, f"服務執行失敗: {str(e)}")
        return wrapper
    return decorator