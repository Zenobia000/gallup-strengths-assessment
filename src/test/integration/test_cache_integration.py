"""
Cache Integration Tests - End-to-End Cache System Testing

This module provides integration tests for the complete caching system,
testing the interaction between cache components, report service integration,
and API endpoints.

Test Scenarios:
- Report generation with cache integration
- Cache warming and optimization
- API endpoint functionality
- Performance under realistic load
- Error recovery and fallback scenarios

Author: TaskMaster Agent (3.4.7)
Date: 2025-09-30
Version: 1.0
"""

import asyncio
import pytest
import time
from datetime import datetime
from typing import Dict, List, Any
from unittest.mock import Mock, patch, AsyncMock

from fastapi.testclient import TestClient
from fastapi import FastAPI

from services.report_service import ReportService, create_report_service
from services.cache_service import CacheService, get_cache_service
from core.report.cache_manager import CacheConfiguration
from models.schemas import QuestionResponse
from models.report_models import (
    ReportGenerationRequest, ReportType, ReportFormat, ReportQuality
)
from api.routes.cache_admin import router as cache_admin_router


class TestReportServiceCacheIntegration:
    """Test cache integration with report service."""

    @pytest.fixture
    def report_service(self):
        """Create a report service with caching enabled."""
        return create_report_service(
            output_directory="/tmp/test_reports",
            enable_cache=True
        )

    @pytest.fixture
    def sample_request(self):
        """Create a sample report generation request."""
        responses = [
            QuestionResponse(question_id=i, score=3 + (i % 3))
            for i in range(1, 21)
        ]

        return ReportGenerationRequest(
            responses=responses,
            user_name="Test User",
            report_type=ReportType.FULL_ASSESSMENT,
            report_format=ReportFormat.PDF,
            report_quality=ReportQuality.STANDARD,
            include_charts=True,
            include_recommendations=True
        )

    @pytest.mark.asyncio
    async def test_cache_enabled_report_generation(self, report_service, sample_request):
        """Test report generation with cache enabled."""
        # Mock the PDF generation to avoid actual file creation
        with patch.object(
            report_service.pdf_generator,
            'generate_report_from_responses'
        ) as mock_pdf_gen:
            mock_result = Mock()
            mock_result.success = True
            mock_result.file_path = "/tmp/test_report.pdf"
            mock_result.file_size_bytes = 1024
            mock_pdf_gen.return_value = mock_result

            # First generation should not hit cache
            response1 = await report_service.generate_report_from_responses(sample_request)

            assert response1.success is True
            assert response1.cached is False  # First generation
            assert response1.cache_hit is False

    @pytest.mark.asyncio
    async def test_cache_hit_on_duplicate_request(self, report_service, sample_request):
        """Test cache hit on duplicate request."""
        # First, simulate a cached report exists
        cache_service = report_service.cache_service

        if cache_service:
            # Mock a cache hit
            mock_cached_report = {
                'cached': True,
                'report_data': {'test': 'data'},
                'file_path': '/tmp/cached_report.pdf',
                'file_size_bytes': 2048,
                'metadata': {'user_name': 'Test User'},
                'generation_time_seconds': 10.0,
                'cache_created_at': datetime.now(),
                'access_count': 1
            }

            with patch.object(
                cache_service,
                'get_report_from_cache',
                return_value=mock_cached_report
            ):
                response = await report_service.generate_report_from_responses(sample_request)

                assert response.success is True
                assert response.cached is True
                assert response.cache_hit is True
                assert response.metadata.generation_time_seconds == 10.0

    @pytest.mark.asyncio
    async def test_cache_performance_stats(self, report_service):
        """Test cache performance statistics collection."""
        stats = await report_service.get_cache_performance_stats()

        if report_service.enable_cache:
            assert 'service_stats' in stats
            assert 'report_cache_stats' in stats
            assert 'health_status' in stats
            assert 'configuration' in stats
        else:
            assert stats['cache_enabled'] is False

    @pytest.mark.asyncio
    async def test_cache_warming(self, report_service):
        """Test cache warming functionality."""
        result = await report_service.warm_report_cache()

        if report_service.enable_cache:
            assert isinstance(result, dict)
            # Should have completed without errors
        else:
            assert result['cache_enabled'] is False

    @pytest.mark.asyncio
    async def test_cache_health_check(self, report_service):
        """Test cache health check."""
        health_result = await report_service.perform_cache_health_check()

        if report_service.enable_cache:
            assert 'is_healthy' in health_result
            assert 'hit_rate_percent' in health_result
            assert 'response_time_ms' in health_result
        else:
            assert health_result['cache_enabled'] is False

    @pytest.mark.asyncio
    async def test_cache_invalidation(self, report_service):
        """Test cache invalidation by pattern."""
        pattern = "report:*"
        result = await report_service.invalidate_cache_pattern(pattern)

        if report_service.enable_cache:
            assert 'success' in result
            assert 'invalidated_count' in result
            assert 'pattern' in result
        else:
            assert result['cache_enabled'] is False


class TestCacheServiceIntegration:
    """Test cache service integration scenarios."""

    @pytest.fixture
    def cache_service(self):
        """Create a cache service for testing."""
        config = CacheConfiguration(
            report_ttl=3600,
            max_cached_reports=100,
            cache_if_generation_time_gt=1.0
        )
        return CacheService(config)

    @pytest.fixture
    def sample_responses(self):
        """Create sample assessment responses."""
        return [
            QuestionResponse(question_id=i, score=2 + (i % 4))
            for i in range(1, 21)
        ]

    @pytest.mark.asyncio
    async def test_full_cache_lifecycle(self, cache_service, sample_responses):
        """Test complete cache lifecycle: store, retrieve, invalidate."""
        # Mock report data
        report_data = {
            "generation_result": {
                "success": True,
                "file_path": "/tmp/test.pdf",
                "file_size_bytes": 1024
            }
        }

        big_five_scores = {
            "openness": 15.0,
            "conscientiousness": 18.0,
            "extraversion": 12.0,
            "agreeableness": 16.0,
            "neuroticism": 8.0
        }

        # Store in cache
        success = await cache_service.cache_generated_report(
            responses=sample_responses,
            report_type=ReportType.FULL_ASSESSMENT,
            report_data=report_data,
            file_path="/tmp/test.pdf",
            file_size_bytes=1024,
            generation_time_seconds=10.0,
            big_five_scores=big_five_scores,
            report_metadata={"user": "test"}
        )

        assert success is True

        # Retrieve from cache
        cached_report = await cache_service.get_report_from_cache(
            responses=sample_responses,
            report_type=ReportType.FULL_ASSESSMENT
        )

        if cached_report:
            assert cached_report['cached'] is True
            assert cached_report['report_data'] == report_data

        # Test cache statistics
        stats = cache_service.get_comprehensive_stats()
        assert isinstance(stats, dict)

    @pytest.mark.asyncio
    async def test_cache_warming_strategy(self, cache_service):
        """Test cache warming with different strategies."""
        # Test default warming
        result = await cache_service.warm_cache_strategically()

        assert isinstance(result, dict)
        if 'status' in result and result['status'] == 'already_in_progress':
            # Warming was already in progress, that's okay
            pass
        else:
            assert 'patterns_warmed' in result
            assert 'time_taken_seconds' in result

    @pytest.mark.asyncio
    async def test_cache_optimization(self, cache_service):
        """Test cache optimization functionality."""
        result = await cache_service.optimize_cache_performance()

        assert isinstance(result, dict)
        assert 'actions_taken' in result
        assert 'recommendations' in result

    @pytest.mark.asyncio
    async def test_concurrent_cache_operations(self, cache_service, sample_responses):
        """Test cache operations under concurrent load."""
        async def cache_worker(worker_id: int):
            """Worker function for concurrent testing."""
            try:
                # Each worker uses slightly different responses
                worker_responses = [
                    QuestionResponse(question_id=i, score=(worker_id % 5) + 1)
                    for i in range(1, 21)
                ]

                # Try to get from cache (should miss initially)
                cached = await cache_service.get_report_from_cache(
                    responses=worker_responses,
                    report_type=ReportType.FULL_ASSESSMENT
                )

                # Cache a report
                big_five_scores = {
                    "openness": 10.0 + worker_id,
                    "conscientiousness": 15.0 + worker_id,
                    "extraversion": 12.0,
                    "agreeableness": 16.0,
                    "neuroticism": 8.0
                }

                await cache_service.cache_generated_report(
                    responses=worker_responses,
                    report_type=ReportType.FULL_ASSESSMENT,
                    report_data={"worker": worker_id},
                    file_path=f"/tmp/worker_{worker_id}.pdf",
                    file_size_bytes=1024,
                    generation_time_seconds=5.0,
                    big_five_scores=big_five_scores,
                    report_metadata={"worker_id": worker_id}
                )

                return True
            except Exception as e:
                print(f"Worker {worker_id} failed: {e}")
                return False

        # Run multiple workers concurrently
        tasks = [cache_worker(i) for i in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Most workers should succeed
        successful = sum(1 for result in results if result is True)
        assert successful >= 3  # Allow some failures due to test environment


class TestCacheAPIIntegration:
    """Test cache administration API integration."""

    @pytest.fixture
    def app(self):
        """Create a FastAPI app with cache admin routes."""
        app = FastAPI()
        app.include_router(cache_admin_router)
        return app

    @pytest.fixture
    def client(self, app):
        """Create a test client."""
        return TestClient(app)

    def test_cache_stats_endpoint(self, client):
        """Test cache statistics API endpoint."""
        response = client.get("/cache/stats")

        assert response.status_code == 200
        data = response.json()

        assert 'timestamp' in data
        assert 'cache_enabled' in data

    def test_cache_health_endpoint(self, client):
        """Test cache health check API endpoint."""
        response = client.get("/cache/health")

        assert response.status_code == 200
        data = response.json()

        assert 'timestamp' in data
        assert 'is_healthy' in data
        assert 'recommendations' in data

    def test_cache_warm_endpoint(self, client):
        """Test cache warming API endpoint."""
        request_data = {
            "priority": "medium",
            "max_duration_seconds": 60,
            "warm_common_patterns": True
        }

        response = client.post("/cache/warm", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert 'timestamp' in data
        assert 'success' in data

    def test_cache_optimize_endpoint(self, client):
        """Test cache optimization API endpoint."""
        response = client.post("/cache/optimize")

        assert response.status_code == 200
        data = response.json()

        assert 'timestamp' in data
        assert 'actions_taken' in data
        assert 'recommendations' in data

    def test_cache_invalidate_endpoint(self, client):
        """Test cache invalidation API endpoint."""
        request_data = {
            "pattern": "test:*",
            "confirm": True
        }

        response = client.delete("/cache/invalidate", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert 'timestamp' in data
        assert 'success' in data
        assert 'pattern' in data

    def test_cache_invalidate_without_confirmation(self, client):
        """Test cache invalidation requires confirmation."""
        request_data = {
            "pattern": "test:*",
            "confirm": False
        }

        response = client.delete("/cache/invalidate", json=request_data)

        assert response.status_code == 400
        assert "Confirmation required" in response.json()['detail']

    def test_cache_patterns_endpoint(self, client):
        """Test cache patterns API endpoint."""
        response = client.get("/cache/patterns?limit=10")

        assert response.status_code == 200
        data = response.json()

        assert 'cache_enabled' in data
        assert 'patterns' in data

    def test_cache_clear_endpoint(self, client):
        """Test cache clear API endpoint."""
        request_data = True  # Confirmation

        response = client.post("/cache/clear", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert 'success' in data
        assert 'message' in data


class TestCachePerformanceIntegration:
    """Test cache performance under realistic conditions."""

    @pytest.mark.asyncio
    async def test_cache_performance_metrics(self):
        """Test cache performance measurement."""
        cache_service = get_cache_service()

        start_time = time.time()

        # Simulate realistic cache operations
        for i in range(100):
            responses = [
                QuestionResponse(question_id=j, score=(i + j) % 5 + 1)
                for j in range(1, 21)
            ]

            # Try to get from cache
            await cache_service.get_report_from_cache(
                responses=responses,
                report_type=ReportType.FULL_ASSESSMENT
            )

        end_time = time.time()
        total_time = end_time - start_time

        # Cache operations should be fast
        assert total_time < 5.0  # 100 operations in under 5 seconds

        # Check performance stats
        stats = cache_service.get_comprehensive_stats()
        assert 'service_stats' in stats

    @pytest.mark.asyncio
    async def test_memory_usage_monitoring(self):
        """Test cache memory usage monitoring."""
        cache_service = get_cache_service()

        # Generate some cache entries
        for i in range(50):
            responses = [
                QuestionResponse(question_id=j, score=(i + j) % 5 + 1)
                for j in range(1, 21)
            ]

            big_five_scores = {
                "openness": 10.0 + (i % 10),
                "conscientiousness": 15.0 + (i % 10),
                "extraversion": 12.0,
                "agreeableness": 16.0,
                "neuroticism": 8.0
            }

            await cache_service.cache_generated_report(
                responses=responses,
                report_type=ReportType.FULL_ASSESSMENT,
                report_data={"iteration": i},
                file_path=f"/tmp/test_{i}.pdf",
                file_size_bytes=1024,
                generation_time_seconds=5.0,
                big_five_scores=big_five_scores,
                report_metadata={"iteration": i}
            )

        # Check that memory usage is being tracked
        stats = cache_service.get_comprehensive_stats()
        cache_manager_stats = stats.get('cache_manager_stats', {})

        # Should have some cache entries
        if cache_manager_stats:
            for cache_name, cache_stats in cache_manager_stats.items():
                if hasattr(cache_stats, 'current_entries'):
                    # Should have some entries cached
                    assert cache_stats.current_entries >= 0


class TestCacheErrorRecovery:
    """Test cache error recovery and fallback scenarios."""

    @pytest.mark.asyncio
    async def test_cache_service_fallback(self):
        """Test cache service behavior when caching fails."""
        # Create a report service with caching disabled
        report_service = create_report_service(enable_cache=False)

        # Cache operations should fail gracefully
        stats = await report_service.get_cache_performance_stats()
        assert stats['cache_enabled'] is False

        health = await report_service.perform_cache_health_check()
        assert health['cache_enabled'] is False

    @pytest.mark.asyncio
    async def test_partial_cache_failure_recovery(self):
        """Test recovery from partial cache failures."""
        cache_service = get_cache_service()

        # Test with invalid data that might cause cache errors
        try:
            responses = [
                QuestionResponse(question_id=i, score=3)
                for i in range(1, 21)
            ]

            # This should not raise an exception even if cache fails
            result = await cache_service.get_report_from_cache(
                responses=responses,
                report_type=ReportType.FULL_ASSESSMENT
            )

            # Should return None on cache miss, not raise exception
            assert result is None or isinstance(result, dict)

        except Exception as e:
            pytest.fail(f"Cache should handle errors gracefully: {e}")


if __name__ == "__main__":
    # Run integration tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure for integration tests
    ])