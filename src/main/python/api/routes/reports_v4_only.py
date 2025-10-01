"""
V4 Reports API - Simplified

只保留 V4 所需的報告功能：
- PDF 報告生成（簡化版）
- 結果分享連結
- 基本報告管理

移除所有舊系統依賴
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from core.data_access.unified_repository import get_score_repository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reports", tags=["Reports V4"])


@router.post("/generate/{session_id}")
async def generate_report(session_id: str):
    """生成 V4 評測報告"""
    try:
        # 獲取評測結果
        score_repo = get_score_repository()
        results = score_repo.find_by_session(session_id)

        if not results:
            raise HTTPException(status_code=404, detail="評測結果不存在")

        # 簡化的報告生成
        report_data = {
            "session_id": session_id,
            "report_type": "v4_strength_analysis",
            "generated_at": datetime.utcnow().isoformat(),
            "status": "completed",
            "download_url": f"/reports/{session_id}/download"
        }

        return {
            "success": True,
            "data": report_data,
            "message": "報告生成完成"
        }

    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise HTTPException(status_code=500, detail="報告生成失敗")


@router.get("/{session_id}/download")
async def download_report(session_id: str):
    """下載報告（占位符）"""
    return {
        "message": "PDF 下載功能開發中",
        "session_id": session_id,
        "status": "pending"
    }


@router.get("/health")
async def reports_health():
    """報告系統健康檢查"""
    return {
        "status": "operational",
        "version": "v4_only",
        "features": ["basic_reports", "download_placeholder"]
    }