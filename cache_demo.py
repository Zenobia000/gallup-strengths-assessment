#!/usr/bin/env python3
"""
Cache System Demonstration Script

This script demonstrates the cache system functionality implemented for
the report generation system. It shows cache hits, misses, performance
improvements, and administration features.

Usage:
    python cache_demo.py

Features demonstrated:
- Basic cache operations
- Report generation with caching
- Cache performance monitoring
- Cache warming strategies
- Administration and optimization

Author: TaskMaster Agent (3.4.7)
Date: 2025-09-30
Version: 1.0
"""

import asyncio
import time
import json
from datetime import datetime
from typing import List, Dict, Any

# Add src to path for imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'main', 'python'))

from models.schemas import QuestionResponse
from models.report_models import (
    ReportGenerationRequest, ReportType, ReportFormat, ReportQuality
)
from services.report_service import create_report_service
from services.cache_service import get_cache_service
from core.report.cache_manager import CacheConfiguration
from utils.cache import CacheKeyBuilder


class CacheDemo:
    """Main demonstration class for cache system."""

    def __init__(self):
        """Initialize the demo with cache-enabled services."""
        print("🚀 Initializing Cache System Demo")
        print("=" * 50)

        # Create cache configuration
        self.cache_config = CacheConfiguration(
            report_ttl=3600,  # 1 hour
            max_cached_reports=100,
            cache_if_generation_time_gt=2.0  # Cache if generation > 2 seconds
        )

        # Initialize services
        self.report_service = create_report_service(
            output_directory="/tmp/cache_demo_reports",
            enable_cache=True
        )
        self.cache_service = get_cache_service(self.cache_config)

        print(f"✅ Cache configuration loaded")
        print(f"   - Report TTL: {self.cache_config.report_ttl} seconds")
        print(f"   - Max cached reports: {self.cache_config.max_cached_reports}")
        print(f"   - Cache threshold: {self.cache_config.cache_if_generation_time_gt}s")
        print()

    def create_sample_responses(self, variation: int = 0) -> List[QuestionResponse]:
        """Create sample assessment responses with optional variation."""
        base_scores = [3, 4, 2, 5, 3, 4, 2, 1, 5, 4, 3, 2, 4, 5, 3, 2, 4, 3, 5, 2]

        return [
            QuestionResponse(
                question_id=i + 1,
                score=min(5, max(1, base_scores[i] + (variation % 3) - 1))
            )
            for i in range(20)
        ]

    def create_sample_request(
        self,
        user_name: str = "Demo User",
        variation: int = 0
    ) -> ReportGenerationRequest:
        """Create a sample report generation request."""
        return ReportGenerationRequest(
            responses=self.create_sample_responses(variation),
            user_name=user_name,
            report_type=ReportType.FULL_ASSESSMENT,
            report_format=ReportFormat.PDF,
            report_quality=ReportQuality.STANDARD,
            include_charts=True,
            include_recommendations=True,
            user_context={"demo": True, "variation": variation}
        )

    async def demonstrate_basic_cache_operations(self):
        """Demonstrate basic cache operations."""
        print("📦 Demonstrating Basic Cache Operations")
        print("-" * 40)

        # Test cache key generation
        big_five_scores = {
            "openness": 15.0,
            "conscientiousness": 18.0,
            "extraversion": 12.0,
            "agreeableness": 16.0,
            "neuroticism": 8.0
        }

        cache_key = CacheKeyBuilder.build_report_key(
            big_five_scores, "full_assessment", "pdf", "v1"
        )
        print(f"✅ Generated cache key: {cache_key}")

        # Test different key variations
        different_scores = big_five_scores.copy()
        different_scores["openness"] = 16.0

        different_key = CacheKeyBuilder.build_report_key(
            different_scores, "full_assessment", "pdf", "v1"
        )
        print(f"✅ Different scores produce different key: {different_key}")
        print(f"   Keys are different: {cache_key != different_key}")
        print()

    async def demonstrate_cache_miss_and_hit(self):
        """Demonstrate cache miss followed by cache hit."""
        print("🎯 Demonstrating Cache Miss and Hit")
        print("-" * 40)

        # Create a sample request
        request = self.create_sample_request("Cache Demo User", 0)

        # Mock the PDF generation to simulate different timing
        from unittest.mock import patch, Mock

        # First request - should be a cache miss
        print("⏱️  First request (cache miss expected)...")
        start_time = time.time()

        with patch.object(
            self.report_service.pdf_generator,
            'generate_report_from_responses'
        ) as mock_pdf_gen:
            # Mock a slow generation (will be cached)
            mock_result = Mock()
            mock_result.success = True
            mock_result.file_path = "/tmp/demo_report.pdf"
            mock_result.file_size_bytes = 2048
            mock_pdf_gen.return_value = mock_result

            # Simulate generation delay
            await asyncio.sleep(0.1)  # Simulate some processing time

            response1 = await self.report_service.generate_report_from_responses(request)

        first_request_time = time.time() - start_time

        print(f"✅ First request completed:")
        print(f"   - Success: {response1.success}")
        print(f"   - Cached: {response1.cached}")
        print(f"   - Cache hit: {response1.cache_hit}")
        print(f"   - Response time: {first_request_time:.3f}s")
        print()

        # Second request - should be a cache hit
        print("⚡ Second request (cache hit expected)...")
        start_time = time.time()

        response2 = await self.report_service.generate_report_from_responses(request)

        second_request_time = time.time() - start_time

        print(f"✅ Second request completed:")
        print(f"   - Success: {response2.success}")
        print(f"   - Cached: {response2.cached}")
        print(f"   - Cache hit: {response2.cache_hit}")
        print(f"   - Response time: {second_request_time:.3f}s")
        print(f"   - Speed improvement: {(first_request_time / second_request_time):.1f}x faster")
        print()

    async def demonstrate_cache_performance(self):
        """Demonstrate cache performance with multiple requests."""
        print("📊 Demonstrating Cache Performance")
        print("-" * 40)

        # Generate multiple similar requests
        requests = [
            self.create_sample_request(f"User {i}", i % 3)  # 3 different patterns
            for i in range(10)
        ]

        # Mock PDF generation for all requests
        from unittest.mock import patch, Mock

        with patch.object(
            self.report_service.pdf_generator,
            'generate_report_from_responses'
        ) as mock_pdf_gen:
            mock_result = Mock()
            mock_result.success = True
            mock_result.file_path = "/tmp/perf_test.pdf"
            mock_result.file_size_bytes = 1024
            mock_pdf_gen.return_value = mock_result

            print(f"🔄 Processing {len(requests)} requests...")
            start_time = time.time()

            responses = []
            for i, request in enumerate(requests):
                response = await self.report_service.generate_report_from_responses(request)
                responses.append(response)
                print(f"   Request {i+1}: {'HIT' if response.cache_hit else 'MISS'}")

            total_time = time.time() - start_time

        # Analyze results
        cache_hits = sum(1 for r in responses if r.cache_hit)
        cache_misses = len(responses) - cache_hits
        hit_rate = (cache_hits / len(responses)) * 100

        print(f"\n📈 Performance Summary:")
        print(f"   - Total requests: {len(requests)}")
        print(f"   - Cache hits: {cache_hits}")
        print(f"   - Cache misses: {cache_misses}")
        print(f"   - Hit rate: {hit_rate:.1f}%")
        print(f"   - Total time: {total_time:.3f}s")
        print(f"   - Average time per request: {(total_time / len(requests)):.3f}s")
        print()

    async def demonstrate_cache_statistics(self):
        """Demonstrate cache statistics and monitoring."""
        print("📊 Cache Statistics and Monitoring")
        print("-" * 40)

        # Get comprehensive cache statistics
        stats = await self.report_service.get_cache_performance_stats()

        if stats.get('cache_enabled'):
            print("✅ Cache is enabled")
            print(f"📊 Service Statistics:")

            service_stats = stats.get('service_stats', {})
            print(f"   - Total operations: {service_stats.get('total_operations', 0)}")
            print(f"   - Successful operations: {service_stats.get('successful_operations', 0)}")
            print(f"   - Failed operations: {service_stats.get('failed_operations', 0)}")

            report_stats = stats.get('report_cache_stats', {})
            if report_stats:
                print(f"📈 Report Cache Statistics:")
                print(f"   - Hit rate: {report_stats.get('cache_hit_rate_percent', 0):.1f}%")
                print(f"   - Total requests: {report_stats.get('total_requests', 0)}")
                print(f"   - Cache hits: {report_stats.get('cache_hits', 0)}")
                print(f"   - Cache misses: {report_stats.get('cache_misses', 0)}")

            config = stats.get('configuration', {})
            if config:
                print(f"⚙️  Configuration:")
                print(f"   - Report TTL: {config.get('report_ttl', 0)} seconds")
                print(f"   - Max cached reports: {config.get('max_cached_reports', 0)}")
        else:
            print("❌ Cache is disabled")

        print()

    async def demonstrate_cache_health_check(self):
        """Demonstrate cache health monitoring."""
        print("🏥 Cache Health Check")
        print("-" * 40)

        health_result = await self.report_service.perform_cache_health_check()

        if health_result.get('cache_enabled'):
            print(f"🏥 Health Status: {'✅ HEALTHY' if health_result['is_healthy'] else '❌ UNHEALTHY'}")
            print(f"📊 Metrics:")
            print(f"   - Hit rate: {health_result['hit_rate_percent']:.1f}%")
            print(f"   - Response time: {health_result['response_time_ms']:.1f}ms")
            print(f"   - Memory usage: {health_result['memory_usage_percent']:.1f}%")
            print(f"   - Error rate: {health_result['error_rate_percent']:.1f}%")
            print(f"   - Last check: {health_result['last_check']}")
        else:
            print("❌ Cache health check skipped - caching disabled")

        print()

    async def demonstrate_cache_warming(self):
        """Demonstrate cache warming functionality."""
        print("🔥 Cache Warming")
        print("-" * 40)

        print("🔄 Starting cache warming...")
        warming_result = await self.report_service.warm_report_cache()

        if warming_result.get('cache_enabled'):
            print(f"✅ Cache warming completed")
            print(f"📊 Results:")
            if 'patterns_warmed' in warming_result:
                print(f"   - Patterns warmed: {warming_result.get('patterns_warmed', 0)}")
            if 'time_taken_seconds' in warming_result:
                print(f"   - Time taken: {warming_result.get('time_taken_seconds', 0):.3f}s")
            if 'errors' in warming_result and warming_result['errors']:
                print(f"   - Errors: {len(warming_result['errors'])}")
        else:
            print("❌ Cache warming skipped - caching disabled")

        print()

    async def demonstrate_cache_optimization(self):
        """Demonstrate cache optimization."""
        print("⚡ Cache Optimization")
        print("-" * 40)

        print("🔄 Running cache optimization...")
        optimization_result = await self.report_service.optimize_cache_performance()

        if optimization_result.get('cache_enabled'):
            print(f"✅ Cache optimization completed")
            print(f"📊 Results:")

            actions = optimization_result.get('actions_taken', [])
            if actions:
                print(f"   Actions taken:")
                for action in actions:
                    print(f"     - {action}")
            else:
                print(f"   - No optimization actions needed")

            recommendations = optimization_result.get('recommendations', [])
            if recommendations:
                print(f"   Recommendations:")
                for rec in recommendations:
                    print(f"     - {rec}")
        else:
            print("❌ Cache optimization skipped - caching disabled")

        print()

    async def demonstrate_cache_invalidation(self):
        """Demonstrate cache invalidation."""
        print("🗑️  Cache Invalidation")
        print("-" * 40)

        # First, ensure we have some cached data
        request = self.create_sample_request("Invalidation Test User")

        from unittest.mock import patch, Mock
        with patch.object(
            self.report_service.pdf_generator,
            'generate_report_from_responses'
        ) as mock_pdf_gen:
            mock_result = Mock()
            mock_result.success = True
            mock_result.file_path = "/tmp/invalidation_test.pdf"
            mock_result.file_size_bytes = 1024
            mock_pdf_gen.return_value = mock_result

            # Generate a report to cache
            await self.report_service.generate_report_from_responses(request)

        # Now invalidate cache with pattern
        pattern = "report:*"
        print(f"🔄 Invalidating cache entries matching pattern: {pattern}")

        invalidation_result = await self.report_service.invalidate_cache_pattern(pattern)

        if invalidation_result.get('cache_enabled'):
            print(f"✅ Cache invalidation completed")
            print(f"📊 Results:")
            print(f"   - Success: {invalidation_result.get('success', False)}")
            print(f"   - Entries invalidated: {invalidation_result.get('invalidated_count', 0)}")
            print(f"   - Pattern: {invalidation_result.get('pattern', 'N/A')}")
        else:
            print("❌ Cache invalidation skipped - caching disabled")

        print()

    async def run_comprehensive_demo(self):
        """Run the complete cache system demonstration."""
        print("🎪 CACHE SYSTEM COMPREHENSIVE DEMO")
        print("=" * 50)
        print()

        try:
            # Run all demonstrations
            await self.demonstrate_basic_cache_operations()
            await self.demonstrate_cache_miss_and_hit()
            await self.demonstrate_cache_performance()
            await self.demonstrate_cache_statistics()
            await self.demonstrate_cache_health_check()
            await self.demonstrate_cache_warming()
            await self.demonstrate_cache_optimization()
            await self.demonstrate_cache_invalidation()

            print("🎉 Demo completed successfully!")
            print("=" * 50)

            # Final statistics
            final_stats = await self.report_service.get_cache_performance_stats()
            if final_stats.get('cache_enabled'):
                report_stats = final_stats.get('report_cache_stats', {})
                print(f"🏆 Final Cache Performance:")
                print(f"   - Hit rate: {report_stats.get('cache_hit_rate_percent', 0):.1f}%")
                print(f"   - Total requests: {report_stats.get('total_requests', 0)}")
                print(f"   - Time saved: {report_stats.get('total_generation_time_saved_seconds', 0):.1f}s")

        except Exception as e:
            print(f"❌ Demo failed with error: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """Main demo function."""
    demo = CacheDemo()
    await demo.run_comprehensive_demo()


if __name__ == "__main__":
    asyncio.run(main())