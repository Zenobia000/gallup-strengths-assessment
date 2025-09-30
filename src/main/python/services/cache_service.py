"""
Cache Service - Business Logic Layer for Caching Operations

This module provides the service layer for caching operations, integrating
cache management with the application's business logic and providing a
clean interface for cache-related operations.

Key Responsibilities:
- Orchestrate cache operations across different components
- Provide cache warming and optimization strategies
- Handle cache monitoring and health checks
- Implement cache policies and governance
- Integrate with application lifecycle

Design Philosophy:
- Service-oriented architecture
- Clean separation of concerns
- Comprehensive monitoring and observability
- Graceful degradation and fallback strategies

Author: TaskMaster Agent (3.4.7)
Date: 2025-09-30
Version: 1.0
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

from core.report.cache_manager import (
    ReportCacheManager, CacheConfiguration, ReportCacheEntry,
    get_report_cache_manager
)
from utils.cache import CacheStats, CacheManager, get_cache_manager
from models.schemas import QuestionResponse
from models.report_models import ReportType, ReportFormat, ReportQuality

logger = logging.getLogger(__name__)


@dataclass
class CacheHealthStatus:
    """Cache health and performance status."""
    is_healthy: bool
    hit_rate_percent: float
    response_time_ms: float
    memory_usage_percent: float
    error_rate_percent: float
    last_check: datetime

    def __post_init__(self):
        """Validate health status values."""
        if not 0 <= self.hit_rate_percent <= 100:
            raise ValueError("Hit rate must be between 0 and 100")
        if not 0 <= self.memory_usage_percent <= 100:
            raise ValueError("Memory usage must be between 0 and 100")


@dataclass
class CacheWarmingPlan:
    """Plan for cache warming operations."""
    target_patterns: List[Dict[str, Any]]
    estimated_duration_seconds: int
    priority_level: str  # "high", "medium", "low"
    warm_on_startup: bool = True
    warm_on_schedule: bool = False
    schedule_interval_hours: int = 24


class CacheService:
    """
    High-level cache service providing business logic for caching operations.

    This service orchestrates cache operations across the application,
    providing optimization strategies, monitoring, and management capabilities.
    """

    def __init__(self, config: Optional[CacheConfiguration] = None):
        """
        Initialize the cache service.

        Args:
            config: Cache configuration options
        """
        self.config = config or CacheConfiguration()
        self.cache_manager = get_cache_manager()
        self.report_cache_manager = get_report_cache_manager(config)

        # Service state
        self._is_healthy = True
        self._last_health_check = datetime.now()
        self._warming_in_progress = False

        # Performance tracking
        self._service_stats = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'avg_response_time_ms': 0.0,
            'last_operation_time': None
        }

        logger.info("Cache service initialized")

    async def get_report_from_cache(
        self,
        responses: List[QuestionResponse],
        report_type: ReportType,
        report_format: ReportFormat = ReportFormat.PDF,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get a report from cache with service-level logic.

        Args:
            responses: Assessment responses
            report_type: Type of report
            report_format: Output format
            user_context: User context

        Returns:
            Cached report data if available
        """
        start_time = time.time()
        self._service_stats['total_operations'] += 1

        try:
            cache_entry = await self.report_cache_manager.get_cached_report(
                responses, report_type, report_format, user_context
            )

            if cache_entry:
                self._service_stats['successful_operations'] += 1

                # Return formatted response
                return {
                    'success': True,
                    'cached': True,
                    'report_data': cache_entry.report_data,
                    'file_path': cache_entry.file_path,
                    'file_size_bytes': cache_entry.file_size_bytes,
                    'metadata': cache_entry.report_metadata,
                    'generation_time_seconds': cache_entry.generation_time_seconds,
                    'cache_created_at': cache_entry.created_at,
                    'access_count': cache_entry.access_count
                }

            return None

        except Exception as e:
            self._service_stats['failed_operations'] += 1
            logger.error(f"Error retrieving report from cache: {e}")
            return None

        finally:
            # Update performance stats
            response_time = (time.time() - start_time) * 1000
            self._update_response_time(response_time)
            self._service_stats['last_operation_time'] = datetime.now()

    async def cache_generated_report(
        self,
        responses: List[QuestionResponse],
        report_type: ReportType,
        report_data: Dict[str, Any],
        file_path: Optional[str],
        file_size_bytes: int,
        generation_time_seconds: float,
        big_five_scores: Dict[str, float],
        report_metadata: Dict[str, Any],
        report_format: ReportFormat = ReportFormat.PDF,
        user_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Cache a generated report with service-level logic.

        Args:
            responses: Assessment responses
            report_type: Type of report
            report_data: Generated report data
            file_path: Path to generated file
            file_size_bytes: Size of generated file
            generation_time_seconds: Time taken to generate
            big_five_scores: Computed Big Five scores
            report_metadata: Additional metadata
            report_format: Output format
            user_context: User context

        Returns:
            True if caching successful
        """
        start_time = time.time()
        self._service_stats['total_operations'] += 1

        try:
            success = await self.report_cache_manager.cache_report(
                responses=responses,
                report_type=report_type,
                report_data=report_data,
                file_path=file_path,
                file_size_bytes=file_size_bytes,
                generation_time_seconds=generation_time_seconds,
                big_five_scores=big_five_scores,
                report_metadata=report_metadata,
                report_format=report_format,
                user_context=user_context
            )

            if success:
                self._service_stats['successful_operations'] += 1
                logger.info(f"Successfully cached report (generation time: {generation_time_seconds}s)")
            else:
                self._service_stats['failed_operations'] += 1

            return success

        except Exception as e:
            self._service_stats['failed_operations'] += 1
            logger.error(f"Error caching generated report: {e}")
            return False

        finally:
            response_time = (time.time() - start_time) * 1000
            self._update_response_time(response_time)
            self._service_stats['last_operation_time'] = datetime.now()

    async def warm_cache_strategically(
        self,
        warming_plan: Optional[CacheWarmingPlan] = None
    ) -> Dict[str, Any]:
        """
        Execute strategic cache warming based on usage patterns.

        Args:
            warming_plan: Custom warming plan, or None for default

        Returns:
            Warming execution results
        """
        if self._warming_in_progress:
            return {'status': 'already_in_progress'}

        self._warming_in_progress = True
        start_time = time.time()

        try:
            logger.info("Starting strategic cache warming")

            # Use default warming plan if none provided
            if warming_plan is None:
                warming_plan = await self._create_default_warming_plan()

            warming_results = {
                'plan_executed': warming_plan.priority_level,
                'patterns_warmed': 0,
                'time_taken_seconds': 0.0,
                'errors': []
            }

            # Execute warming for each pattern
            for pattern in warming_plan.target_patterns:
                try:
                    await self._warm_pattern(pattern)
                    warming_results['patterns_warmed'] += 1
                except Exception as e:
                    error_msg = f"Failed to warm pattern {pattern}: {str(e)}"
                    warming_results['errors'].append(error_msg)
                    logger.warning(error_msg)

            # Delegate to report cache manager for additional warming
            report_warming_stats = await self.report_cache_manager.warm_cache_for_common_patterns()
            warming_results['report_patterns'] = report_warming_stats

            warming_results['time_taken_seconds'] = time.time() - start_time
            logger.info(f"Cache warming completed: {warming_results}")

            return warming_results

        except Exception as e:
            logger.error(f"Error during strategic cache warming: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'time_taken_seconds': time.time() - start_time
            }

        finally:
            self._warming_in_progress = False

    async def perform_health_check(self) -> CacheHealthStatus:
        """
        Perform comprehensive cache health check.

        Returns:
            Cache health status
        """
        try:
            # Get performance stats
            performance_stats = self.report_cache_manager.get_performance_stats()
            cache_stats = self.cache_manager.get_all_stats()

            # Test cache responsiveness
            test_start = time.time()
            test_key = f"health_check_{int(time.time())}"
            await self.cache_manager.set(test_key, "test_value", 60)
            retrieved_value = await self.cache_manager.get(test_key)
            await self.cache_manager._caches[self.cache_manager._primary_cache].delete(test_key)
            response_time_ms = (time.time() - test_start) * 1000

            # Calculate health metrics
            hit_rate = performance_stats.get('cache_hit_rate_percent', 0)
            error_rate = self._calculate_error_rate()
            memory_usage = self._estimate_memory_usage(cache_stats)

            # Determine overall health
            is_healthy = (
                hit_rate >= 70 and  # At least 70% hit rate
                response_time_ms <= 100 and  # Response under 100ms
                error_rate <= 5 and  # Error rate under 5%
                memory_usage <= 80 and  # Memory under 80%
                retrieved_value == "test_value"  # Basic functionality works
            )

            health_status = CacheHealthStatus(
                is_healthy=is_healthy,
                hit_rate_percent=hit_rate,
                response_time_ms=response_time_ms,
                memory_usage_percent=memory_usage,
                error_rate_percent=error_rate,
                last_check=datetime.now()
            )

            self._is_healthy = is_healthy
            self._last_health_check = datetime.now()

            if not is_healthy:
                logger.warning(f"Cache health check failed: {health_status}")
            else:
                logger.info(f"Cache health check passed: hit_rate={hit_rate:.1f}%, response_time={response_time_ms:.1f}ms")

            return health_status

        except Exception as e:
            logger.error(f"Error during cache health check: {e}")
            return CacheHealthStatus(
                is_healthy=False,
                hit_rate_percent=0,
                response_time_ms=0,
                memory_usage_percent=0,
                error_rate_percent=100,
                last_check=datetime.now()
            )

    async def optimize_cache_performance(self) -> Dict[str, Any]:
        """
        Analyze and optimize cache performance.

        Returns:
            Optimization results and recommendations
        """
        try:
            logger.info("Starting cache performance optimization")

            optimization_results = {
                'actions_taken': [],
                'recommendations': [],
                'performance_improvement': {}
            }

            # Get current performance baseline
            baseline_stats = self.report_cache_manager.get_performance_stats()

            # Cleanup expired entries
            cleanup_stats = await self.report_cache_manager.cleanup_expired_entries()
            if cleanup_stats.get('cache_entries_removed', 0) > 0:
                optimization_results['actions_taken'].append(
                    f"Cleaned up {cleanup_stats['cache_entries_removed']} expired entries"
                )

            # Analyze hit rate and suggest optimizations
            hit_rate = baseline_stats.get('cache_hit_rate_percent', 0)
            if hit_rate < 80:
                optimization_results['recommendations'].append(
                    "Consider increasing cache TTL or implementing cache warming"
                )

            if hit_rate < 50:
                optimization_results['recommendations'].append(
                    "Review cache key generation - low hit rate suggests poor key strategy"
                )

            # Check memory usage
            cache_stats = self.cache_manager.get_all_stats()
            memory_usage = self._estimate_memory_usage(cache_stats)
            if memory_usage > 85:
                optimization_results['recommendations'].append(
                    "Consider increasing cache size limits or reducing TTL"
                )

            # Performance recommendations based on error rate
            error_rate = self._calculate_error_rate()
            if error_rate > 2:
                optimization_results['recommendations'].append(
                    "Investigate cache errors - consider implementing fallback strategies"
                )

            logger.info(f"Cache optimization completed: {optimization_results}")
            return optimization_results

        except Exception as e:
            logger.error(f"Error during cache optimization: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'actions_taken': [],
                'recommendations': ['Manual investigation required']
            }

    async def invalidate_cache_by_pattern(self, pattern: str) -> int:
        """
        Invalidate cache entries matching a pattern.

        Args:
            pattern: Pattern to match for invalidation

        Returns:
            Number of entries invalidated
        """
        try:
            invalidated = await self.report_cache_manager.invalidate_report_cache(
                pattern=pattern
            )

            logger.info(f"Invalidated {invalidated} cache entries matching pattern: {pattern}")
            return invalidated

        except Exception as e:
            logger.error(f"Error invalidating cache by pattern {pattern}: {e}")
            return 0

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics across all components.

        Returns:
            Complete statistics dictionary
        """
        try:
            report_stats = self.report_cache_manager.get_performance_stats()
            cache_manager_stats = self.cache_manager.get_all_stats()

            return {
                'service_stats': self._service_stats,
                'report_cache_stats': report_stats,
                'cache_manager_stats': cache_manager_stats,
                'health_status': {
                    'is_healthy': self._is_healthy,
                    'last_health_check': self._last_health_check,
                    'warming_in_progress': self._warming_in_progress
                },
                'configuration': {
                    'report_ttl': self.config.report_ttl,
                    'max_cached_reports': self.config.max_cached_reports,
                    'max_memory_mb': self.config.max_memory_mb,
                    'cache_if_generation_time_gt': self.config.cache_if_generation_time_gt
                }
            }

        except Exception as e:
            logger.error(f"Error getting comprehensive stats: {e}")
            return {'error': str(e)}

    async def _create_default_warming_plan(self) -> CacheWarmingPlan:
        """Create a default cache warming plan based on common patterns."""
        # Define common Big Five score patterns for warming
        common_patterns = [
            # Balanced profiles
            {"openness": 15, "conscientiousness": 15, "extraversion": 15, "agreeableness": 15, "neuroticism": 10},
            # High openness, creativity-focused
            {"openness": 20, "conscientiousness": 12, "extraversion": 14, "agreeableness": 16, "neuroticism": 8},
            # High conscientiousness, detail-oriented
            {"openness": 12, "conscientiousness": 20, "extraversion": 13, "agreeableness": 15, "neuroticism": 9},
            # High extraversion, people-focused
            {"openness": 14, "conscientiousness": 13, "extraversion": 20, "agreeableness": 18, "neuroticism": 7},
            # Analytical profile
            {"openness": 18, "conscientiousness": 17, "extraversion": 10, "agreeableness": 12, "neuroticism": 11}
        ]

        return CacheWarmingPlan(
            target_patterns=common_patterns,
            estimated_duration_seconds=300,  # 5 minutes
            priority_level="medium",
            warm_on_startup=True,
            warm_on_schedule=True,
            schedule_interval_hours=24
        )

    async def _warm_pattern(self, pattern: Dict[str, Any]) -> bool:
        """Warm cache for a specific score pattern."""
        # This would integrate with the report generation system
        # For now, we simulate the warming process
        await asyncio.sleep(0.1)  # Simulate work
        return True

    def _update_response_time(self, response_time_ms: float):
        """Update average response time tracking."""
        total_ops = self._service_stats['total_operations']
        current_avg = self._service_stats['avg_response_time_ms']

        if total_ops == 1:
            self._service_stats['avg_response_time_ms'] = response_time_ms
        else:
            # Simple moving average
            self._service_stats['avg_response_time_ms'] = (
                (current_avg * (total_ops - 1) + response_time_ms) / total_ops
            )

    def _calculate_error_rate(self) -> float:
        """Calculate current error rate percentage."""
        total_ops = self._service_stats['total_operations']
        if total_ops == 0:
            return 0.0

        failed_ops = self._service_stats['failed_operations']
        return (failed_ops / total_ops) * 100

    def _estimate_memory_usage(self, cache_stats: Dict[str, Any]) -> float:
        """Estimate memory usage percentage based on cache statistics."""
        # This is a simplified estimation
        # In production, you might want more sophisticated memory monitoring
        max_memory_bytes = self.config.max_memory_mb * 1024 * 1024

        total_memory_used = 0
        for cache_name, stats in cache_stats.items():
            if hasattr(stats, 'memory_usage_bytes'):
                total_memory_used += stats.memory_usage_bytes

        return min((total_memory_used / max_memory_bytes) * 100, 100)


# Global service instance
_cache_service: Optional[CacheService] = None


def get_cache_service(config: Optional[CacheConfiguration] = None) -> CacheService:
    """
    Get or create the global cache service instance.

    Args:
        config: Optional configuration for initialization

    Returns:
        Cache service instance
    """
    global _cache_service

    if _cache_service is None:
        _cache_service = CacheService(config)

    return _cache_service


# Convenience functions for common operations
async def get_cached_report_data(
    responses: List[QuestionResponse],
    report_type: ReportType,
    report_format: ReportFormat = ReportFormat.PDF,
    user_context: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """Convenience function to get cached report data."""
    service = get_cache_service()
    return await service.get_report_from_cache(
        responses, report_type, report_format, user_context
    )


async def cache_report_data(
    responses: List[QuestionResponse],
    report_type: ReportType,
    report_data: Dict[str, Any],
    file_path: Optional[str],
    file_size_bytes: int,
    generation_time_seconds: float,
    big_five_scores: Dict[str, float],
    report_metadata: Dict[str, Any],
    report_format: ReportFormat = ReportFormat.PDF,
    user_context: Optional[Dict[str, Any]] = None
) -> bool:
    """Convenience function to cache report data."""
    service = get_cache_service()
    return await service.cache_generated_report(
        responses=responses,
        report_type=report_type,
        report_data=report_data,
        file_path=file_path,
        file_size_bytes=file_size_bytes,
        generation_time_seconds=generation_time_seconds,
        big_five_scores=big_five_scores,
        report_metadata=report_metadata,
        report_format=report_format,
        user_context=user_context
    )


async def perform_cache_health_check() -> CacheHealthStatus:
    """Convenience function to perform cache health check."""
    service = get_cache_service()
    return await service.perform_health_check()


async def warm_cache() -> Dict[str, Any]:
    """Convenience function to warm cache with default plan."""
    service = get_cache_service()
    return await service.warm_cache_strategically()


def get_cache_performance_stats() -> Dict[str, Any]:
    """Convenience function to get cache performance statistics."""
    service = get_cache_service()
    return service.get_comprehensive_stats()