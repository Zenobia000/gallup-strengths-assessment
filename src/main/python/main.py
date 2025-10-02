"""
Gallup Strengths Assessment System - V4 Main Application

簡化的主應用程式入口，只保留 v4 架構：
- Thurstonian IRT 評測系統
- 動態職業原型分析
- 完整 T1-T12 才幹評估
- 統一的資料存取和錯誤處理

遵循 Linus 原則：簡潔、專注、不過度設計
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import logging
from pathlib import Path
from datetime import datetime

# 導入 v4 核心組件
from api.routes.v4_assessment import router as v4_assessment_router
from api.routes.consent import router as consent_router
from api.routes.reports_v4_only import router as reports_router
# Cache admin removed to eliminate dependencies
from api.error_handlers import setup_error_handlers
from core.constants import get_system_config

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 建立 FastAPI 應用
app = FastAPI(
    title="Gallup Strengths Assessment V4",
    description="基於 Thurstonian IRT 的優勢評測系統",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 設定全域錯誤處理
setup_error_handlers(app)

# 註冊 V4 路由 (核心功能)
app.include_router(v4_assessment_router)

# 註冊共用服務路由
app.include_router(consent_router)
app.include_router(reports_router)
# Cache admin router removed

# 靜態檔案服務
static_path = Path(__file__).parent / "resources" / "static"
if static_path.exists():
    app.mount("/", StaticFiles(directory=str(static_path), html=True), name="static")

# 系統資訊端點
@app.get("/api/system/info")
async def get_system_info():
    """獲取系統資訊"""
    config = get_system_config()

    return {
        "system": "Gallup Strengths Assessment",
        "version": "4.0.0",
        "architecture": "Thurstonian IRT + Career Archetypes",
        "status": "operational",
        "features": [
            "forced_choice_assessment",
            "irt_scoring",
            "career_archetype_analysis",
            "strength_dna_visualization",
            "dynamic_job_recommendations"
        ],
        "config": {
            "dominant_threshold": config.dominant_threshold,
            "api_port": config.api_port,
            "frontend_port": config.frontend_port
        }
    }

@app.get("/api/health")
async def health_check():
    """系統健康檢查"""
    from core.data_access.unified_repository import get_unified_data_access

    try:
        # 檢查資料庫連接
        data_access = get_unified_data_access()
        db_health = data_access.health_check()

        return {
            "status": "healthy" if db_health["status"] == "healthy" else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "4.0.0",
            "components": {
                "database": db_health["status"],
                "api": "operational",
                "scoring_engine": "operational",
                "archetype_system": "operational"
            },
            "endpoints": {
                "assessment": "/api/v4/assessment/blocks",
                "submit": "/api/v4/assessment/submit",
                "results": "/api/v4/assessment/results/{session_id}"
            }
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    from datetime import datetime

    config = get_system_config()

    logger.info("🚀 啟動 Gallup Strengths Assessment V4")
    logger.info(f"📊 架構: Thurstonian IRT + 動態職業原型")
    logger.info(f"🌐 API 端點: http://localhost:{config.api_port}")
    logger.info(f"🎯 前端: http://localhost:{config.frontend_port}")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=config.api_port,
        reload=True,
        log_level="info"
    )