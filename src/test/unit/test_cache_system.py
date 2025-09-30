"""
Cache System Tests - Comprehensive Testing for Caching Components

This module provides comprehensive tests for the caching system, including
unit tests for cache utilities, integration tests for cache managers,
and performance tests for cache operations.

Test Coverage:
- Cache utilities and key generation
- Memory cache operations and TTL
- Report cache manager functionality
- Cache service layer operations
- Performance and concurrency tests

Author: TaskMaster Agent (3.4.7)
Date: 2025-09-30
Version: 1.0
"""

import asyncio
import pytest
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import Mock, patch, AsyncMock

from utils.cache import (
    MemoryCache, CacheKeyBuilder, CacheManager, CacheStats,
    get_cache_manager, build_report_cache_key
)
from core.report.cache_manager import (
    ReportCacheManager, CacheConfiguration, ReportCacheEntry,
    get_report_cache_manager
)
from services.cache_service import CacheService, CacheHealthStatus
from models.schemas import QuestionResponse
from models.report_models import ReportType, ReportFormat, ReportQuality


class TestCacheKeyBuilder:
    """Test cache key generation functionality."""

    def test_build_report_key_deterministic(self):
        """Test that report keys are deterministic."""
        scores = {"openness": 15.0, "conscientiousness": 18.0, "extraversion": 12.0,
                 "agreeableness": 16.0, "neuroticism": 8.0}

        key1 = CacheKeyBuilder.build_report_key(scores, "full_assessment", "pdf", "v1")
        key2 = CacheKeyBuilder.build_report_key(scores, "full_assessment", "pdf", "v1")

        assert key1 == key2
        assert key1.startswith("report:")
        assert "full_assessment" in key1
        assert "pdf" in key1
        assert "v1" in key1

    def test_build_report_key_different_scores(self):
        """Test that different scores produce different keys."""
        scores1 = {"openness": 15.0, "conscientiousness": 18.0, "extraversion": 12.0,
                  "agreeableness": 16.0, "neuroticism": 8.0}
        scores2 = {"openness": 16.0, "conscientiousness": 18.0, "extraversion": 12.0,
                  "agreeableness": 16.0, "neuroticism": 8.0}

        key1 = CacheKeyBuilder.build_report_key(scores1, "full_assessment", "pdf", "v1")
        key2 = CacheKeyBuilder.build_report_key(scores2, "full_assessment", "pdf", "v1")

        assert key1 != key2

    def test_build_session_key(self):
        """Test session key generation."""
        key = CacheKeyBuilder.build_session_key("sess_123", "responses")

        assert key == "session:sess_123:responses"

    def test_build_content_key(self):
        """Test content key generation."""
        parameters = {"trait": "openness", "score": 15.0}
        key = CacheKeyBuilder.build_content_key("executive_summary", parameters, "zh")

        assert key.startswith("content:executive_summary:")
        assert key.endswith(":zh")

    def test_build_chart_key(self):
        """Test chart key generation."""
        data = {"type": "radar", "scores": [15, 18, 12, 16, 8]}
        key = CacheKeyBuilder.build_chart_key("radar", data, "default")

        assert key.startswith("chart:radar:")
        assert key.endswith(":default")


class TestMemoryCache:
    """Test memory cache implementation."""

    @pytest.fixture
    def cache(self):
        """Create a memory cache instance for testing."""
        return MemoryCache(max_size=10, default_ttl=3600)

    @pytest.mark.asyncio
    async def test_basic_set_get(self, cache):
        """Test basic cache set and get operations."""
        await cache.set("test_key", "test_value")
        value = await cache.get("test_key")

        assert value == "test_value"

    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self, cache):
        """Test getting a non-existent key returns None."""
        value = await cache.get("nonexistent")

        assert value is None

    @pytest.mark.asyncio
    async def test_ttl_expiration(self, cache):
        """Test TTL expiration functionality."""
        await cache.set("expire_key", "expire_value", ttl=1)  # 1 second TTL

        # Should exist immediately
        value = await cache.get("expire_key")
        assert value == "expire_value"

        # Wait for expiration
        await asyncio.sleep(1.1)

        # Should be expired
        value = await cache.get("expire_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_exists_functionality(self, cache):
        """Test the exists method."""
        await cache.set("exists_key", "exists_value")

        assert await cache.exists("exists_key") is True
        assert await cache.exists("nonexistent") is False

    @pytest.mark.asyncio
    async def test_delete_functionality(self, cache):
        """Test the delete method."""
        await cache.set("delete_key", "delete_value")

        assert await cache.delete("delete_key") is True
        assert await cache.get("delete_key") is None
        assert await cache.delete("nonexistent") is False

    @pytest.mark.asyncio
    async def test_clear_functionality(self, cache):
        """Test the clear method."""
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")

        assert await cache.clear() is True
        assert await cache.get("key1") is None
        assert await cache.get("key2") is None

    @pytest.mark.asyncio
    async def test_lru_eviction(self, cache):
        """Test LRU eviction when cache is full."""
        # Fill cache to max size
        for i in range(10):
            await cache.set(f"key_{i}", f"value_{i}")

        # Add one more item to trigger eviction
        await cache.set("key_10", "value_10")

        # First item should be evicted
        assert await cache.get("key_0") is None
        assert await cache.get("key_10") == "value_10"

    @pytest.mark.asyncio
    async def test_keys_functionality(self, cache):
        """Test the keys method with pattern matching."""
        await cache.set("test_key_1", "value1")
        await cache.set("test_key_2", "value2")
        await cache.set("other_key", "value3")

        all_keys = await cache.keys()
        assert len(all_keys) == 3

        pattern_keys = await cache.keys("test_key_*")
        assert len(pattern_keys) == 2

    def test_cache_stats(self, cache):
        """Test cache statistics tracking."""
        stats = cache.get_stats()

        assert isinstance(stats, CacheStats)
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.sets == 0


class TestCacheConfiguration:
    """Test cache configuration validation."""

    def test_default_configuration(self):
        """Test default configuration values."""
        config = CacheConfiguration()

        assert config.report_ttl == 24 * 3600
        assert config.max_cached_reports == 1000
        assert config.cache_if_generation_time_gt == 5.0

    def test_invalid_configuration(self):
        """Test configuration validation."""
        with pytest.raises(ValueError):
            CacheConfiguration(report_ttl=1800)  # Less than minimum

        with pytest.raises(ValueError):
            CacheConfiguration(max_cached_reports=50)  # Less than minimum


class TestReportCacheManager:
    """Test report cache manager functionality."""

    @pytest.fixture
    def cache_manager(self):
        """Create a report cache manager for testing."""
        config = CacheConfiguration(
            report_ttl=3600,
            max_cached_reports=100,
            cache_if_generation_time_gt=1.0
        )
        return ReportCacheManager(config)

    @pytest.fixture
    def sample_responses(self):
        """Create sample assessment responses."""
        return [
            QuestionResponse(question_id=i, score=3)
            for i in range(1, 21)
        ]

    @pytest.mark.asyncio
    async def test_cache_report_and_retrieve(self, cache_manager, sample_responses):
        """Test caching and retrieving a report."""
        big_five_scores = {
            "openness": 15.0,
            "conscientiousness": 18.0,
            "extraversion": 12.0,
            "agreeableness": 16.0,
            "neuroticism": 8.0
        }

        # Cache a report
        success = await cache_manager.cache_report(
            responses=sample_responses,
            report_type=ReportType.FULL_ASSESSMENT,
            report_data={"test": "data"},
            file_path="/tmp/test.pdf",
            file_size_bytes=1024,
            generation_time_seconds=10.0,
            big_five_scores=big_five_scores,
            report_metadata={"user": "test"}
        )

        assert success is True

        # Retrieve the cached report
        cached_report = await cache_manager.get_cached_report(
            responses=sample_responses,
            report_type=ReportType.FULL_ASSESSMENT
        )

        assert cached_report is not None
        assert cached_report.report_data == {"test": "data"}
        assert cached_report.generation_time_seconds == 10.0

    @pytest.mark.asyncio
    async def test_cache_miss(self, cache_manager, sample_responses):
        """Test cache miss for non-existent report."""
        cached_report = await cache_manager.get_cached_report(
            responses=sample_responses,
            report_type=ReportType.FULL_ASSESSMENT
        )

        assert cached_report is None

    @pytest.mark.asyncio
    async def test_skip_cache_for_fast_generation(self, cache_manager, sample_responses):
        """Test that fast generation is not cached."""
        big_five_scores = {"openness": 15.0, "conscientiousness": 18.0,
                          "extraversion": 12.0, "agreeableness": 16.0, "neuroticism": 8.0}

        # Try to cache a fast generation (should be skipped)
        success = await cache_manager.cache_report(
            responses=sample_responses,
            report_type=ReportType.FULL_ASSESSMENT,
            report_data={"test": "data"},
            file_path="/tmp/test.pdf",
            file_size_bytes=1024,
            generation_time_seconds=0.5,  # Too fast
            big_five_scores=big_five_scores,
            report_metadata={"user": "test"}
        )

        assert success is False

    @pytest.mark.asyncio
    async def test_cache_content_components(self, cache_manager):
        """Test caching content components."""
        content_data = {"summary": "Test executive summary"}
        parameters = {"trait": "openness", "score": 15.0}

        success = await cache_manager.cache_report_content(
            "executive_summary",
            content_data,
            parameters
        )

        assert success is True

        retrieved_content = await cache_manager.get_cached_content(
            "executive_summary",
            parameters
        )

        assert retrieved_content == content_data

    @pytest.mark.asyncio
    async def test_cache_chart_data(self, cache_manager):
        """Test caching chart data."""
        chart_data = {"scores": [15, 18, 12, 16, 8]}
        rendered_chart = {"svg": "<svg>test chart</svg>"}

        success = await cache_manager.cache_chart_data(
            "radar",
            chart_data,
            rendered_chart
        )

        assert success is True

        retrieved_chart = await cache_manager.get_cached_chart(
            "radar",
            chart_data
        )

        assert retrieved_chart == rendered_chart

    def test_performance_stats(self, cache_manager):
        """Test performance statistics collection."""
        stats = cache_manager.get_performance_stats()

        assert isinstance(stats, dict)
        assert 'cache_hit_rate_percent' in stats
        assert 'total_requests' in stats
        assert 'cache_hits' in stats
        assert 'cache_misses' in stats


class TestCacheService:
    """Test cache service layer functionality."""

    @pytest.fixture
    def cache_service(self):
        """Create a cache service for testing."""
        config = CacheConfiguration(
            report_ttl=3600,
            max_cached_reports=100
        )
        return CacheService(config)

    @pytest.mark.asyncio
    async def test_health_check(self, cache_service):
        """Test cache health check functionality."""
        health_status = await cache_service.perform_health_check()

        assert isinstance(health_status, CacheHealthStatus)
        assert hasattr(health_status, 'is_healthy')
        assert hasattr(health_status, 'hit_rate_percent')
        assert hasattr(health_status, 'response_time_ms')

    @pytest.mark.asyncio
    async def test_performance_optimization(self, cache_service):
        """Test cache performance optimization."""
        result = await cache_service.optimize_cache_performance()

        assert isinstance(result, dict)
        assert 'actions_taken' in result
        assert 'recommendations' in result

    def test_comprehensive_stats(self, cache_service):
        """Test comprehensive statistics collection."""
        stats = cache_service.get_comprehensive_stats()

        assert isinstance(stats, dict)
        assert 'service_stats' in stats
        assert 'report_cache_stats' in stats
        assert 'health_status' in stats
        assert 'configuration' in stats


class TestCacheIntegration:
    """Integration tests for cache system components."""

    @pytest.mark.asyncio
    async def test_end_to_end_cache_flow(self):
        """Test complete cache flow from request to response."""
        # This would test the full integration with ReportService
        # For now, we'll test the key components work together

        # Setup cache manager
        cache_manager = get_cache_manager()
        assert cache_manager is not None

        # Test basic cache operations
        await cache_manager.set("integration_test", "test_value", 300)
        value = await cache_manager.get("integration_test")
        assert value == "test_value"

    @pytest.mark.asyncio
    async def test_concurrent_cache_operations(self):
        """Test cache operations under concurrent load."""
        cache = MemoryCache(max_size=100, default_ttl=3600)

        async def cache_worker(worker_id: int):
            for i in range(10):
                key = f"worker_{worker_id}_key_{i}"
                value = f"worker_{worker_id}_value_{i}"
                await cache.set(key, value)
                retrieved = await cache.get(key)
                assert retrieved == value

        # Run multiple workers concurrently
        tasks = [cache_worker(i) for i in range(5)]
        await asyncio.gather(*tasks)

    @pytest.mark.asyncio
    async def test_cache_performance_under_load(self):
        """Test cache performance with high load."""
        cache = MemoryCache(max_size=1000, default_ttl=3600)

        start_time = time.time()

        # Perform many cache operations
        for i in range(1000):
            await cache.set(f"perf_key_{i}", f"perf_value_{i}")

        for i in range(1000):
            value = await cache.get(f"perf_key_{i}")
            assert value == f"perf_value_{i}"

        end_time = time.time()
        total_time = end_time - start_time

        # Should complete 2000 operations in reasonable time
        assert total_time < 5.0  # Should be much faster in practice

        # Check cache statistics
        stats = cache.get_stats()
        assert stats.hits == 1000
        assert stats.sets == 1000


class TestCacheErrorHandling:
    """Test cache error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_cache_with_invalid_data(self):
        """Test cache behavior with invalid data types."""
        cache = MemoryCache(max_size=10, default_ttl=3600)

        # Test with None value
        await cache.set("none_key", None)
        assert await cache.get("none_key") is None

        # Test with complex objects
        complex_object = {"nested": {"data": [1, 2, 3]}}
        await cache.set("complex_key", complex_object)
        retrieved = await cache.get("complex_key")
        assert retrieved == complex_object

    @pytest.mark.asyncio
    async def test_cache_manager_fallback(self):
        """Test cache manager fallback mechanisms."""
        manager = CacheManager()

        # Test behavior when no caches are registered
        value = await manager.get("test_key")
        assert value is None

        # Register a cache and test
        manager.register_cache("test", MemoryCache())
        manager.set_primary("test")

        success = await manager.set("test_key", "test_value")
        assert success is True

        value = await manager.get("test_key")
        assert value == "test_value"

    @pytest.mark.asyncio
    async def test_corrupted_cache_recovery(self):
        """Test recovery from corrupted cache entries."""
        cache_manager = ReportCacheManager()

        # This test would simulate corrupted cache data recovery
        # For now, we'll test basic error handling
        try:
            # Attempt to get from empty cache
            result = await cache_manager.get_cached_report(
                responses=[QuestionResponse(question_id=1, score=3)],
                report_type=ReportType.FULL_ASSESSMENT
            )
            assert result is None
        except Exception as e:
            pytest.fail(f"Should handle missing cache gracefully: {e}")


if __name__ == "__main__":
    # Run specific test categories
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-k", "not test_cache_performance_under_load"  # Skip performance tests in normal runs
    ])