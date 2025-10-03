"""
會員系統 API 路由 (Member System Routes)

提供會員相關的 RESTful API 端點:
- 健康檢查
- 會員資訊查詢
- 會員管理 (CRUD)

Note:
- 認證功能將在 Week 2 實作
- 本檔案為 Week 1 基礎架構

設計原則:
- RESTful API 設計
- OpenAPI/Swagger 文檔
- 錯誤處理標準化
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# 資料庫依賴 (假設已在 main.py 設定)
def get_db():
    """取得資料庫 Session (佔位符)"""
    # TODO: 實作資料庫連線邏輯
    pass


# ==================== Pydantic Models (Request/Response Schemas) ====================

class MemberBase(BaseModel):
    """會員基礎 Schema"""
    email: EmailStr
    full_name: Optional[str] = None
    display_name: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    company: Optional[str] = None


class MemberCreate(MemberBase):
    """創建會員 Request Schema"""
    password: str = Field(..., min_length=8, description="密碼 (最少8字元)")


class MemberUpdate(BaseModel):
    """更新會員 Request Schema"""
    full_name: Optional[str] = None
    display_name: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    company: Optional[str] = None


class MemberResponse(MemberBase):
    """會員 Response Schema"""
    member_id: str
    email_verified: bool
    account_status: str
    account_type: str
    login_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic V2 (orm_mode in V1)


class HealthResponse(BaseModel):
    """健康檢查 Response"""
    status: str
    service: str
    version: str
    timestamp: datetime


# ==================== Router 初始化 ====================

router = APIRouter(
    prefix="/api/members",
    tags=["members"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)


# ==================== API Endpoints ====================

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="健康檢查",
    description="檢查會員系統 API 是否正常運作"
)
async def health_check():
    """
    健康檢查端點

    Returns:
        HealthResponse: 服務狀態資訊
    """
    return HealthResponse(
        status="healthy",
        service="member-system",
        version="1.0.0-week1",
        timestamp=datetime.utcnow()
    )


@router.get(
    "/",
    response_model=List[MemberResponse],
    summary="列出會員",
    description="取得會員清單 (分頁)"
)
async def list_members(
    skip: int = 0,
    limit: int = 100,
    account_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    列出會員清單

    Args:
        skip: 跳過筆數 (用於分頁)
        limit: 限制筆數 (最多100)
        account_status: 篩選帳號狀態 (active/suspended/deleted)
        db: 資料庫 Session

    Returns:
        List[MemberResponse]: 會員清單
    """
    # TODO: 實作查詢邏輯 (Week 1 佔位符)
    return []


@router.get(
    "/{member_id}",
    response_model=MemberResponse,
    summary="取得會員資訊",
    description="根據會員 ID 取得詳細資訊"
)
async def get_member(
    member_id: str,
    db: Session = Depends(get_db)
):
    """
    取得會員資訊

    Args:
        member_id: 會員 ID
        db: 資料庫 Session

    Returns:
        MemberResponse: 會員資訊

    Raises:
        HTTPException: 404 會員不存在
    """
    # TODO: 實作查詢邏輯
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not implemented yet (Week 2)"
    )


@router.post(
    "/",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="創建會員",
    description="註冊新會員 (Week 2 實作)"
)
async def create_member(
    member_data: MemberCreate,
    db: Session = Depends(get_db)
):
    """
    創建新會員

    Args:
        member_data: 會員註冊資料
        db: 資料庫 Session

    Returns:
        MemberResponse: 新建的會員資訊

    Raises:
        HTTPException: 400 Email 已存在
    """
    # TODO: Week 2 實作註冊邏輯
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Registration endpoint will be implemented in Week 2"
    )


@router.put(
    "/{member_id}",
    response_model=MemberResponse,
    summary="更新會員資訊",
    description="更新會員個人檔案"
)
async def update_member(
    member_id: str,
    member_data: MemberUpdate,
    db: Session = Depends(get_db)
):
    """
    更新會員資訊

    Args:
        member_id: 會員 ID
        member_data: 更新資料
        db: 資料庫 Session

    Returns:
        MemberResponse: 更新後的會員資訊

    Raises:
        HTTPException: 404 會員不存在
    """
    # TODO: Week 3 實作
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not implemented yet (Week 3)"
    )


@router.delete(
    "/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="刪除會員",
    description="軟刪除會員 (GDPR 合規)"
)
async def delete_member(
    member_id: str,
    db: Session = Depends(get_db)
):
    """
    刪除會員 (軟刪除)

    Args:
        member_id: 會員 ID
        db: 資料庫 Session

    Returns:
        None (204 No Content)

    Raises:
        HTTPException: 404 會員不存在
    """
    # TODO: Week 3 實作
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not implemented yet (Week 3)"
    )


# ==================== 統計與搜尋端點 ====================

@router.get(
    "/stats/count",
    summary="會員統計",
    description="取得會員數量統計"
)
async def get_member_stats(
    account_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    會員統計

    Args:
        account_status: 篩選帳號狀態
        db: 資料庫 Session

    Returns:
        dict: 統計資訊
    """
    # TODO: 實作統計邏輯
    return {
        "total": 0,
        "active": 0,
        "suspended": 0,
        "deleted": 0
    }


@router.get(
    "/search",
    response_model=List[MemberResponse],
    summary="搜尋會員",
    description="根據姓名搜尋會員"
)
async def search_members(
    q: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    搜尋會員

    Args:
        q: 搜尋關鍵字
        limit: 限制筆數
        db: 資料庫 Session

    Returns:
        List[MemberResponse]: 符合的會員清單
    """
    # TODO: 實作搜尋邏輯
    return []


# ==================== 錯誤處理範例 ====================

class ErrorResponse(BaseModel):
    """錯誤 Response Schema"""
    error: str
    detail: str
    timestamp: datetime


@router.get("/error-example", include_in_schema=False)
async def error_example():
    """錯誤處理範例 (不包含在 API 文檔中)"""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="This is an example error response"
    )


# ==================== 路由資訊 ====================

def get_router_info():
    """取得路由資訊 (用於測試)"""
    return {
        "prefix": router.prefix,
        "tags": router.tags,
        "routes_count": len(router.routes)
    }
