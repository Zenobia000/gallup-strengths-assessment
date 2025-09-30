"""
Cache Administration API - Cache Management and Monitoring

This module provides API endpoints for cache administration, monitoring,
and management. It includes cache statistics, health checks, optimization,
and management operations.

Key Endpoints:
- GET /cache/stats - Cache performance statistics
- GET /cache/health - Cache health check
- POST /cache/warm - Warm cache with common patterns
- POST /cache/optimize - Optimize cache performance
- DELETE /cache/invalidate - Invalidate cache patterns

Security Notes:
- These endpoints should be protected in production
- Consider rate limiting for cache operations
- Log all cache management operations

Author: TaskMaster Agent (3.4.7)
Date: 2025-09-30
Version: 1.0
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field

from services.report_service import ReportService, create_report_service
from services.cache_service import get_cache_service

router = APIRouter(prefix="/cache", tags=["Cache Administration"])


# Request/Response Models
class CacheStatsResponse(BaseModel):
    """Response model for cache statistics."""
    timestamp: datetime = Field(default_factory=datetime.now)
    cache_enabled: bool
    service_stats: Dict[str, Any]
    report_cache_stats: Dict[str, Any]
    cache_manager_stats: Dict[str, Any]
    health_status: Dict[str, Any]
    configuration: Dict[str, Any]


class CacheHealthResponse(BaseModel):
    """Response model for cache health check."""
    timestamp: datetime = Field(default_factory=datetime.now)
    is_healthy: bool
    hit_rate_percent: float
    response_time_ms: float
    memory_usage_percent: float
    error_rate_percent: float
    last_check: str
    recommendations: List[str] = Field(default_factory=list)


class CacheWarmingRequest(BaseModel):
    """Request model for cache warming operations."""
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    max_duration_seconds: int = Field(default=300, ge=30, le=1800)
    warm_common_patterns: bool = Field(default=True)


class CacheWarmingResponse(BaseModel):
    """Response model for cache warming results."""
    timestamp: datetime = Field(default_factory=datetime.now)
    success: bool
    patterns_warmed: int
    time_taken_seconds: float
    errors: List[str]
    recommendations: List[str] = Field(default_factory=list)


class CacheOptimizationResponse(BaseModel):
    """Response model for cache optimization results."""
    timestamp: datetime = Field(default_factory=datetime.now)
    actions_taken: List[str]
    recommendations: List[str]
    performance_improvement: Dict[str, Any]


class CacheInvalidationRequest(BaseModel):
    """Request model for cache invalidation."""
    pattern: str = Field(..., min_length=1, description="Pattern to match for invalidation")
    confirm: bool = Field(default=False, description="Confirmation flag for destructive operation")


class CacheInvalidationResponse(BaseModel):
    """Response model for cache invalidation results."""
    timestamp: datetime = Field(default_factory=datetime.now)
    success: bool
    invalidated_count: int
    pattern: str
    message: str


# Dependency for getting report service
async def get_report_service() -> ReportService:
    """Dependency to get the report service instance."""
    return create_report_service()


@router.get(
    "/stats",
    response_model=CacheStatsResponse,
    summary="Get Cache Statistics",
    description="Retrieve comprehensive cache performance statistics and metrics"
)
async def get_cache_statistics(
    report_service: ReportService = Depends(get_report_service)
) -> CacheStatsResponse:
    """
    Get comprehensive cache statistics.

    Returns detailed performance metrics, hit rates, memory usage,
    and configuration information for all cache components.
    """
    try:
        stats = await report_service.get_cache_performance_stats()

        if not stats.get('cache_enabled', True):
            return CacheStatsResponse(
                cache_enabled=False,
                service_stats={},
                report_cache_stats={},
                cache_manager_stats={},
                health_status={'message': 'Caching is disabled'},
                configuration={}
            )

        return CacheStatsResponse(
            cache_enabled=True,
            service_stats=stats.get('service_stats', {}),
            report_cache_stats=stats.get('report_cache_stats', {}),
            cache_manager_stats=stats.get('cache_manager_stats', {}),
            health_status=stats.get('health_status', {}),
            configuration=stats.get('configuration', {})
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve cache statistics: {str(e)}"
        )


@router.get(
    "/health",
    response_model=CacheHealthResponse,
    summary="Cache Health Check",
    description="Perform comprehensive cache health check with recommendations"
)
async def check_cache_health(
    report_service: ReportService = Depends(get_report_service)
) -> CacheHealthResponse:
    """
    Perform cache health check.

    Evaluates cache performance, responsiveness, and overall health.
    Provides recommendations for optimization if issues are detected.
    """
    try:
        health_result = await report_service.perform_cache_health_check()

        if 'error' in health_result:
            raise HTTPException(
                status_code=500,
                detail=health_result['error']
            )

        if not health_result.get('cache_enabled', True):
            return CacheHealthResponse(
                is_healthy=False,
                hit_rate_percent=0,
                response_time_ms=0,
                memory_usage_percent=0,
                error_rate_percent=0,
                last_check=datetime.now().isoformat(),
                recommendations=["Enable caching to improve performance"]
            )

        # Generate recommendations based on health metrics
        recommendations = []
        if health_result['hit_rate_percent'] < 70:
            recommendations.append("Consider cache warming or increasing TTL values")
        if health_result['response_time_ms'] > 100:
            recommendations.append("Cache response time is high - check system resources")
        if health_result['memory_usage_percent'] > 80:
            recommendations.append("High memory usage - consider increasing cache size limits")
        if health_result['error_rate_percent'] > 5:
            recommendations.append("High error rate detected - investigate cache errors")

        return CacheHealthResponse(
            is_healthy=health_result['is_healthy'],
            hit_rate_percent=health_result['hit_rate_percent'],
            response_time_ms=health_result['response_time_ms'],
            memory_usage_percent=health_result['memory_usage_percent'],
            error_rate_percent=health_result['error_rate_percent'],
            last_check=health_result['last_check'],
            recommendations=recommendations
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform health check: {str(e)}"
        )


@router.post(
    "/warm",
    response_model=CacheWarmingResponse,
    summary="Warm Cache",
    description="Preload cache with common report patterns to improve hit rates"
)
async def warm_cache(
    request: CacheWarmingRequest = Body(...),
    report_service: ReportService = Depends(get_report_service)
) -> CacheWarmingResponse:
    """
    Warm the cache with common patterns.

    Preloads the cache with frequently requested report combinations
    to improve cache hit rates and overall system performance.
    """
    try:
        warming_result = await report_service.warm_report_cache()

        if 'error' in warming_result:
            return CacheWarmingResponse(
                success=False,
                patterns_warmed=0,
                time_taken_seconds=0,
                errors=[warming_result['error']],
                recommendations=["Check cache configuration and system resources"]
            )

        if not warming_result.get('cache_enabled', True):
            return CacheWarmingResponse(
                success=False,
                patterns_warmed=0,
                time_taken_seconds=0,
                errors=["Caching is disabled"],
                recommendations=["Enable caching to use warming functionality"]
            )

        recommendations = []
        if warming_result.get('patterns_warmed', 0) == 0:
            recommendations.append("No patterns were warmed - consider manual cache seeding")

        time_taken = warming_result.get('time_taken_seconds', 0)
        if time_taken > request.max_duration_seconds:
            recommendations.append("Warming took longer than expected - consider reducing scope")

        return CacheWarmingResponse(
            success=True,
            patterns_warmed=warming_result.get('patterns_warmed', 0),
            time_taken_seconds=time_taken,
            errors=warming_result.get('errors', []),
            recommendations=recommendations
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to warm cache: {str(e)}"
        )


@router.post(
    "/optimize",
    response_model=CacheOptimizationResponse,
    summary="Optimize Cache",
    description="Analyze and optimize cache performance automatically"
)
async def optimize_cache(
    report_service: ReportService = Depends(get_report_service)
) -> CacheOptimizationResponse:
    """
    Optimize cache performance.

    Analyzes current cache performance and automatically applies
    optimizations such as cleanup, rebalancing, and configuration tuning.
    """
    try:
        optimization_result = await report_service.optimize_cache_performance()

        if 'error' in optimization_result:
            raise HTTPException(
                status_code=500,
                detail=optimization_result['error']
            )

        if not optimization_result.get('cache_enabled', True):
            return CacheOptimizationResponse(
                actions_taken=["Cache optimization skipped - caching disabled"],
                recommendations=["Enable caching to use optimization features"],
                performance_improvement={}
            )

        return CacheOptimizationResponse(
            actions_taken=optimization_result.get('actions_taken', []),
            recommendations=optimization_result.get('recommendations', []),
            performance_improvement=optimization_result.get('performance_improvement', {})
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to optimize cache: {str(e)}"
        )


@router.delete(
    "/invalidate",
    response_model=CacheInvalidationResponse,
    summary="Invalidate Cache Pattern",
    description="Invalidate cache entries matching a specific pattern"
)
async def invalidate_cache_pattern(
    request: CacheInvalidationRequest = Body(...),
    report_service: ReportService = Depends(get_report_service)
) -> CacheInvalidationResponse:
    """
    Invalidate cache entries matching a pattern.

    WARNING: This is a destructive operation that will remove cached data.
    Use with caution, especially in production environments.
    """
    if not request.confirm:
        raise HTTPException(
            status_code=400,
            detail="Confirmation required for cache invalidation. Set 'confirm' to true."
        )

    try:
        invalidation_result = await report_service.invalidate_cache_pattern(request.pattern)

        if 'error' in invalidation_result:
            return CacheInvalidationResponse(
                success=False,
                invalidated_count=0,
                pattern=request.pattern,
                message=invalidation_result['error']
            )

        if not invalidation_result.get('cache_enabled', True):
            return CacheInvalidationResponse(
                success=False,
                invalidated_count=0,
                pattern=request.pattern,
                message="Caching is disabled"
            )

        return CacheInvalidationResponse(
            success=invalidation_result['success'],
            invalidated_count=invalidation_result['invalidated_count'],
            pattern=request.pattern,
            message=f"Successfully invalidated {invalidation_result['invalidated_count']} entries"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to invalidate cache: {str(e)}"
        )


@router.get(
    "/patterns",
    summary="Get Cache Key Patterns",
    description="Retrieve common cache key patterns for debugging and analysis"
)
async def get_cache_patterns(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of patterns to return"),
    report_service: ReportService = Depends(get_report_service)
) -> Dict[str, Any]:
    """
    Get common cache key patterns.

    Useful for debugging, monitoring, and understanding cache usage patterns.
    """
    try:
        cache_service = get_cache_service()

        if cache_service is None:
            return {
                'cache_enabled': False,
                'patterns': [],
                'message': 'Caching is disabled'
            }

        # Get cache statistics to understand patterns
        stats = cache_service.get_comprehensive_stats()

        return {
            'cache_enabled': True,
            'patterns': [],  # This would be implemented based on cache manager capabilities
            'total_entries': stats.get('report_cache_stats', {}).get('total_requests', 0),
            'hit_rate': stats.get('report_cache_stats', {}).get('cache_hit_rate_percent', 0),
            'message': f'Found cache statistics (limit: {limit})'
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve cache patterns: {str(e)}"
        )


@router.post(
    "/clear",
    summary="Clear All Cache",
    description="Clear all cached data (DESTRUCTIVE OPERATION)"
)
async def clear_all_cache(
    confirm: bool = Body(..., description="Confirmation flag for destructive operation"),
    report_service: ReportService = Depends(get_report_service)
) -> Dict[str, Any]:
    """
    Clear all cached data.

    WARNING: This is a DESTRUCTIVE operation that will remove ALL cached data.
    Use with extreme caution.
    """
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Confirmation required for cache clearing. Set 'confirm' to true."
        )

    try:
        # Clear all cache patterns - this is a simplified implementation
        result = await report_service.invalidate_cache_pattern("*")

        return {
            'success': result.get('success', False),
            'message': 'Cache clearing completed',
            'invalidated_count': result.get('invalidated_count', 0),
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cache: {str(e)}"
        )