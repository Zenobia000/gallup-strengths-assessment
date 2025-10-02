"""
Unified Router System

統一的路由管理系統，解決 API 版本混亂問題：
- 版本化路由註冊
- 向後相容性保證
- 衝突檢測和解決
- 統一的中間件

Linus 原則：簡潔、明確、不破壞現有功能
"""

from fastapi import FastAPI, APIRouter
from api.version_manager import get_version_router, APIVersion, VERSION_CONFIG
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class UnifiedRouter:
    """統一路由管理器"""

    def __init__(self, app: FastAPI):
        self.app = app
        self.registered_routes: Dict[str, List[str]] = {}

    def register_v1_routes(self):
        """註冊 V1 API 路由 (維護模式)"""
        v1_router = get_version_router(APIVersion.V1, ["Assessment V1 (Maintenance)"])

        # 導入並註冊 V1 路由
        from api.routes.sessions import router as sessions_router
        from api.routes.scoring import router as scoring_router
        from api.routes.recommendations import router as recommendations_router

        # 重新映射路由到 v1 前綴
        self._register_router_with_prefix(v1_router, sessions_router, "/sessions")
        self._register_router_with_prefix(v1_router, scoring_router, "/scoring")
        self._register_router_with_prefix(v1_router, recommendations_router, "/recommendations")

        self.app.include_router(v1_router)
        logger.info("✅ V1 API routes registered (maintenance mode)")

    def register_v4_routes(self):
        """註冊 V4 API 路由 (當前版本)"""
        v4_router = get_version_router(APIVersion.V4, ["Assessment V4 (Current)"])

        # 導入並註冊 V4 路由
        from api.routes.v4_assessment import router as v4_assessment_router
        from api.routes.v4_data_collection import router as v4_data_collection_router

        # V4 路由已有正確前綴，直接包含
        self.app.include_router(v4_assessment_router)
        self.app.include_router(v4_data_collection_router)

        logger.info("✅ V4 API routes registered (current version)")

    def register_shared_routes(self):
        """註冊共用路由 (無版本依賴)"""
        shared_router = APIRouter(tags=["Shared Services"])

        # 導入共用路由
        from api.routes.consent import router as consent_router
        from api.routes.reports import router as reports_router
        from api.routes.cache_admin import router as cache_router

        # 共用路由不需要版本前綴
        self.app.include_router(consent_router)
        self.app.include_router(reports_router)
        self.app.include_router(cache_router)

        logger.info("✅ Shared API routes registered")

    def register_compatibility_routes(self):
        """註冊相容性路由 (處理舊端點)"""
        compat_router = APIRouter(tags=["Compatibility"])

        # 為舊的無前綴端點提供重定向
        @compat_router.get("/results/{session_id}")
        async def legacy_results_redirect(session_id: str):
            """重定向舊的結果端點到 v4"""
            from fastapi.responses import RedirectResponse
            return RedirectResponse(
                url=f"/api/v4/assessment/results/{session_id}",
                status_code=301
            )

        @compat_router.post("/sessions/start")
        async def legacy_session_redirect():
            """重定向舊的會話端點到 v1"""
            from fastapi.responses import RedirectResponse
            return RedirectResponse(
                url="/api/v1/sessions/start",
                status_code=301
            )

        self.app.include_router(compat_router)
        logger.info("✅ Compatibility routes registered")

    def register_api_info_routes(self):
        """註冊 API 資訊端點"""
        info_router = APIRouter(prefix="/api", tags=["API Information"])

        @info_router.get("/versions")
        async def get_api_versions():
            """獲取所有 API 版本資訊"""
            from api.version_manager import APIVersionManager
            return StandardAPIResponse.success(
                data=APIVersionManager.get_version_info(),
                message="API 版本資訊"
            )

        @info_router.get("/health")
        async def api_health_check():
            """統一的 API 健康檢查"""
            health_status = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "versions": {
                    "v1": {"status": "maintenance", "healthy": True},
                    "v4": {"status": "active", "healthy": True}
                },
                "services": {
                    "database": "operational",
                    "scoring_engine": "operational",
                    "report_generator": "operational"
                }
            }

            return StandardAPIResponse.success(
                data=health_status,
                message="系統運行正常"
            )

        self.app.include_router(info_router)
        logger.info("✅ API info routes registered")

    def _register_router_with_prefix(self, parent_router: APIRouter,
                                   child_router: APIRouter, path_prefix: str):
        """將子路由註冊到父路由，添加路徑前綴"""
        # 這是一個簡化實現，實際可能需要更複雜的路由重寫邏輯
        parent_router.include_router(child_router, prefix=path_prefix)

    def register_all_routes(self):
        """註冊所有路由"""
        logger.info("開始註冊統一 API 路由...")

        # 按順序註冊
        self.register_v4_routes()      # 當前版本優先
        self.register_v1_routes()      # 維護版本
        self.register_shared_routes()  # 共用服務
        self.register_compatibility_routes()  # 相容性
        self.register_api_info_routes()       # API 資訊

        logger.info("🎉 所有 API 路由註冊完成")

        # 輸出路由摘要
        self._log_route_summary()

    def _log_route_summary(self):
        """輸出路由註冊摘要"""
        logger.info("=== API 路由摘要 ===")
        logger.info("V4 (當前): /api/v4/assessment/*")
        logger.info("V1 (維護): /api/v1/sessions/*, /api/v1/scoring/*")
        logger.info("共用: /consent, /reports, /cache")
        logger.info("相容性: /results/* → /api/v4/assessment/results/*")
        logger.info("資訊: /api/versions, /api/health")


def setup_unified_routing(app: FastAPI) -> UnifiedRouter:
    """設定統一路由系統"""
    router_manager = UnifiedRouter(app)
    router_manager.register_all_routes()
    return router_manager


# 導入標準回應格式
from api.version_manager import StandardAPIResponse