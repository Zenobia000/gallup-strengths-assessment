"""
Common Pydantic schemas for shared response formats.
"""

from datetime import datetime
from typing import Any, Dict, Optional, Generic, TypeVar
from pydantic import BaseModel, Field


T = TypeVar('T')


class BaseResponse(BaseModel):
    """Base response model with common fields."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SuccessResponse(BaseResponse, Generic[T]):
    """Generic success response wrapper."""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[T] = None


class ErrorResponse(BaseResponse):
    """Error response model."""
    success: bool = False
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    size: int = Field(20, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.size


class PaginatedResponse(BaseResponse, Generic[T]):
    """Paginated response wrapper."""
    items: list[T]
    total: int
    page: int
    size: int
    pages: int
    
    @classmethod
    def create(
        cls, 
        items: list[T], 
        total: int, 
        pagination: PaginationParams
    ) -> "PaginatedResponse[T]":
        pages = (total + pagination.size - 1) // pagination.size
        return cls(
            items=items,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=pages
        )


class HealthCheck(BaseModel):
    """Health check response model."""
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    database: str
    features: Dict[str, bool] = {}