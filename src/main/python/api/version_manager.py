"""
API Version Management Strategy

統一的API版本管理，實現：
- 清晰的版本路由策略
- 向後相容性保證
- 版本廢棄管理
- 統一的回應格式

遵循 Linus "Never break userspace" 原則
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse


class APIVersion(str, Enum):
    """支援的 API 版本"""
    V1 = "v1"  # Legacy Mini-IPIP
    V4 = "v4"  # Current Thurstonian IRT


class DeprecationLevel(str, Enum):
    """版本廢棄等級"""
    ACTIVE = "active"          # 積極維護
    MAINTENANCE = "maintenance" # 僅安全修復
    DEPRECATED = "deprecated"   # 計劃廢棄
    SUNSET = "sunset"          # 即將移除


# 版本配置
VERSION_CONFIG = {
    APIVersion.V1: {
        "status": DeprecationLevel.MAINTENANCE,
        "sunset_date": "2025-12-31",
        "description": "Mini-IPIP 傳統評測系統",
        "prefix": "/api/v1",
        "features": ["basic_assessment", "simple_scoring", "pdf_reports"]
    },
    APIVersion.V4: {
        "status": DeprecationLevel.ACTIVE,
        "sunset_date": None,
        "description": "Thurstonian IRT 進階評測系統",
        "prefix": "/api/v4",
        "features": ["forced_choice", "irt_scoring", "career_archetypes", "strength_dna"]
    }
}


class APIVersionManager:
    """API 版本管理器"""

    @staticmethod
    def get_router(version: APIVersion, tags: Optional[list] = None) -> APIRouter:
        """獲取指定版本的路由器"""
        config = VERSION_CONFIG[version]

        router = APIRouter(
            prefix=config["prefix"],
            tags=tags or [f"API {version.value.upper()}"]
        )

        # 為廢棄版本添加警告中間件
        if config["status"] in [DeprecationLevel.DEPRECATED, DeprecationLevel.SUNSET]:
            router.middleware("http")(APIVersionManager._deprecation_middleware)

        return router

    @staticmethod
    def _deprecation_middleware(request: Request, call_next):
        """廢棄版本警告中間件"""
        # 提取版本信息
        path = request.url.path
        version = None

        if "/api/v1/" in path:
            version = APIVersion.V1
        elif "/api/v4/" in path:
            version = APIVersion.V4

        response = call_next(request)

        # 添加廢棄警告頭
        if version and VERSION_CONFIG[version]["status"] == DeprecationLevel.DEPRECATED:
            sunset_date = VERSION_CONFIG[version]["sunset_date"]
            response.headers["X-API-Deprecated"] = "true"
            response.headers["X-API-Sunset-Date"] = sunset_date
            response.headers["X-API-Migration-Guide"] = f"/docs/migration/{version.value}-to-v4"

        return response

    @staticmethod
    def get_version_info() -> Dict[str, Any]:
        """獲取所有版本資訊"""
        info = {}

        for version, config in VERSION_CONFIG.items():
            info[version.value] = {
                "status": config["status"].value,
                "description": config["description"],
                "prefix": config["prefix"],
                "features": config["features"],
                "sunset_date": config["sunset_date"],
                "is_active": config["status"] == DeprecationLevel.ACTIVE
            }

        return info

    @staticmethod
    def validate_version_compatibility(version: APIVersion, feature: str) -> bool:
        """驗證版本是否支援指定功能"""
        config = VERSION_CONFIG.get(version)
        if not config:
            return False

        return feature in config["features"]


class StandardAPIResponse:
    """標準化 API 回應格式"""

    @staticmethod
    def success(data: Any = None, message: str = None, meta: Dict[str, Any] = None) -> Dict[str, Any]:
        """成功回應格式"""
        return {
            "success": True,
            "data": data,
            "message": message,
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
                "version": "v4.0",
                **(meta or {})
            },
            "error": None
        }

    @staticmethod
    def error(code: str, message: str, details: Dict[str, Any] = None,
              status_code: int = 400) -> JSONResponse:
        """錯誤回應格式"""
        error_response = {
            "success": False,
            "data": None,
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
                "timestamp": datetime.utcnow().isoformat()
            },
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
                "version": "v4.0"
            }
        }

        return JSONResponse(
            content=error_response,
            status_code=status_code
        )

    @staticmethod
    def validation_error(details: Dict[str, Any]) -> JSONResponse:
        """驗證錯誤的標準格式"""
        return StandardAPIResponse.error(
            code="VALIDATION_ERROR",
            message="請求資料驗證失敗",
            details=details,
            status_code=422
        )

    @staticmethod
    def not_found(resource: str, identifier: str) -> JSONResponse:
        """資源不存在的標準格式"""
        return StandardAPIResponse.error(
            code="NOT_FOUND",
            message=f"{resource} 不存在",
            details={"resource": resource, "identifier": identifier},
            status_code=404
        )

    @staticmethod
    def internal_error(message: str, trace_id: str = None) -> JSONResponse:
        """內部錯誤的標準格式"""
        return StandardAPIResponse.error(
            code="INTERNAL_ERROR",
            message="系統內部錯誤",
            details={
                "internal_message": message,
                "trace_id": trace_id or str(uuid.uuid4())
            },
            status_code=500
        )


# 版本遷移助手
class VersionMigrationHelper:
    """版本遷移助手"""

    @staticmethod
    def get_migration_path(from_version: APIVersion, to_version: APIVersion) -> Dict[str, Any]:
        """獲取版本遷移路徑"""
        if from_version == APIVersion.V1 and to_version == APIVersion.V4:
            return {
                "migration_type": "major_upgrade",
                "breaking_changes": [
                    "評測格式從 Likert 改為強制選擇",
                    "計分算法從簡單加權改為 IRT 模型",
                    "回應格式重大變更"
                ],
                "compatibility_layer": "/api/v1/migrate-to-v4",
                "data_migration_required": True
            }

        return {"migration_type": "not_supported"}


def get_version_router(version: APIVersion, tags: Optional[list] = None) -> APIRouter:
    """便利函式：獲取版本化路由器"""
    return APIVersionManager.get_router(version, tags)


def require_version_feature(version: APIVersion, feature: str):
    """裝飾器：要求特定版本和功能"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not APIVersionManager.validate_version_compatibility(version, feature):
                raise HTTPException(
                    status_code=501,
                    detail=f"Feature '{feature}' not supported in API {version.value}"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator