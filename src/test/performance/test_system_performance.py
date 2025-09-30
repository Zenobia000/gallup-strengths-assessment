#!/usr/bin/env python3
"""
Performance Test Suite - System Load and Stress Testing
Phase 5.4: 效能測試

Tests system performance under various load conditions
"""

import asyncio
import aiohttp
import time
import statistics
from datetime import datetime
from typing import List, Dict, Any
import json


class PerformanceTestSuite:
    def __init__(self, base_url: str = "http://localhost:8002/api/v1"):
        self.base_url = base_url
        self.performance_results = []

    async def setup_session(self):
        """Setup aiohttp session with performance optimizations"""
        timeout = aiohttp.ClientTimeout(total=30)
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector
        )

    async def teardown_session(self):
        """Cleanup session"""
        if self.session:
            await self.session.close()

    async def log_performance_result(self, test_name: str, metrics: Dict[str, Any]):
        """Log performance test result"""
        result = {
            "test": test_name,
            "timestamp": datetime.now().isoformat(),
            **metrics
        }
        self.performance_results.append(result)

        print(f"📊 {test_name}")
        print(f"   Avg Response: {metrics.get('avg_response_time', 0):.1f}ms")
        print(f"   Success Rate: {metrics.get('success_rate', 0):.1f}%")
        if 'throughput' in metrics:
            print(f"   Throughput: {metrics['throughput']:.1f} req/s")

    async def single_request_benchmark(self, endpoint: str, method: str = "GET",
                                     data: Dict = None, iterations: int = 10):
        """Benchmark a single endpoint with multiple iterations"""
        response_times = []
        success_count = 0

        for i in range(iterations):
            start_time = time.time()
            try:
                if method == "GET":
                    async with self.session.get(f"{self.base_url}{endpoint}") as response:
                        response_time = (time.time() - start_time) * 1000
                        response_times.append(response_time)
                        if response.status < 400:
                            success_count += 1
                elif method == "POST":
                    async with self.session.post(
                        f"{self.base_url}{endpoint}",
                        json=data
                    ) as response:
                        response_time = (time.time() - start_time) * 1000
                        response_times.append(response_time)
                        if response.status < 400:
                            success_count += 1

            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                response_times.append(response_time)

        return {
            "avg_response_time": statistics.mean(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "p95_response_time": statistics.quantiles(response_times, n=20)[18],
            "success_rate": (success_count / iterations) * 100,
            "total_requests": iterations
        }

    async def concurrent_load_test(self, endpoint: str, concurrent_users: int = 10,
                                 requests_per_user: int = 5, method: str = "GET",
                                 data: Dict = None):
        """Test endpoint under concurrent load"""
        async def user_session(user_id: int):
            user_response_times = []
            user_success_count = 0

            for request_num in range(requests_per_user):
                start_time = time.time()
                try:
                    if method == "GET":
                        async with self.session.get(f"{self.base_url}{endpoint}") as response:
                            response_time = (time.time() - start_time) * 1000
                            user_response_times.append(response_time)
                            if response.status < 400:
                                user_success_count += 1
                    elif method == "POST":
                        async with self.session.post(
                            f"{self.base_url}{endpoint}",
                            json=data
                        ) as response:
                            response_time = (time.time() - start_time) * 1000
                            user_response_times.append(response_time)
                            if response.status < 400:
                                user_success_count += 1

                except Exception as e:
                    response_time = (time.time() - start_time) * 1000
                    user_response_times.append(response_time)

            return {
                "user_id": user_id,
                "response_times": user_response_times,
                "success_count": user_success_count,
                "total_requests": requests_per_user
            }

        # Execute concurrent user sessions
        start_time = time.time()
        user_tasks = [user_session(i) for i in range(concurrent_users)]
        user_results = await asyncio.gather(*user_tasks)
        total_time = time.time() - start_time

        # Aggregate results
        all_response_times = []
        total_success = 0
        total_requests = 0

        for user_result in user_results:
            all_response_times.extend(user_result["response_times"])
            total_success += user_result["success_count"]
            total_requests += user_result["total_requests"]

        return {
            "concurrent_users": concurrent_users,
            "avg_response_time": statistics.mean(all_response_times) if all_response_times else 0,
            "min_response_time": min(all_response_times) if all_response_times else 0,
            "max_response_time": max(all_response_times) if all_response_times else 0,
            "p95_response_time": statistics.quantiles(all_response_times, n=20)[18] if len(all_response_times) >= 20 else max(all_response_times) if all_response_times else 0,
            "success_rate": (total_success / total_requests) * 100 if total_requests > 0 else 0,
            "total_requests": total_requests,
            "throughput": total_requests / total_time,
            "total_time": total_time
        }

    async def test_health_endpoint_performance(self):
        """Test health endpoint performance"""
        print("🏥 Testing Health Endpoint Performance")

        # Single request benchmark
        metrics = await self.single_request_benchmark("/health", iterations=20)
        await self.log_performance_result("Health Endpoint - Single Request", metrics)

        # Concurrent load test
        load_metrics = await self.concurrent_load_test(
            "/health", concurrent_users=20, requests_per_user=5
        )
        await self.log_performance_result("Health Endpoint - Concurrent Load", load_metrics)

    async def test_scoring_endpoint_performance(self):
        """Test scoring endpoint performance"""
        print("🎯 Testing Scoring Endpoint Performance")

        # Test getting questions
        questions_metrics = await self.single_request_benchmark(
            "/scoring/questions", iterations=10
        )
        await self.log_performance_result("Get Questions", questions_metrics)

        # Test scoring submission
        sample_responses = {
            "session_id": "test-session-123",
            "responses": [
                {"question_id": i, "score": (i % 5) + 1} for i in range(1, 21)
            ]
        }

        scoring_metrics = await self.single_request_benchmark(
            "/scoring/submit", method="POST", data=sample_responses, iterations=10
        )
        await self.log_performance_result("Submit Scoring", scoring_metrics)

    async def test_report_generation_performance(self):
        """Test report generation performance"""
        print("📄 Testing Report Generation Performance")

        report_request = {
            "session_id": "test-session-456",
            "user_name": "Test User",
            "report_type": "comprehensive",
            "report_format": "pdf"
        }

        # Test single report generation
        report_metrics = await self.single_request_benchmark(
            "/reports/generate/session", method="POST", data=report_request, iterations=5
        )
        await self.log_performance_result("Report Generation", report_metrics)

    async def test_cache_performance(self):
        """Test cache system performance"""
        print("🚀 Testing Cache System Performance")

        # Test cache health
        cache_health_metrics = await self.single_request_benchmark(
            "/cache/health", iterations=15
        )
        await self.log_performance_result("Cache Health Check", cache_health_metrics)

        # Test cache stats
        cache_stats_metrics = await self.single_request_benchmark(
            "/cache/stats", iterations=15
        )
        await self.log_performance_result("Cache Statistics", cache_stats_metrics)

    async def test_recommendations_performance(self):
        """Test recommendations endpoint performance"""
        print("💡 Testing Recommendations Performance")

        session_id = "test-session-789"

        # Test career recommendations
        career_metrics = await self.single_request_benchmark(
            f"/recommendations/{session_id}/careers", iterations=10
        )
        await self.log_performance_result("Career Recommendations", career_metrics)

        # Test development recommendations
        dev_metrics = await self.single_request_benchmark(
            f"/recommendations/{session_id}/development", iterations=10
        )
        await self.log_performance_result("Development Recommendations", dev_metrics)

    async def stress_test_concurrent_users(self):
        """Stress test with high concurrent load"""
        print("🔥 Running Stress Test - High Concurrent Load")

        test_scenarios = [
            {"users": 10, "requests": 3},
            {"users": 25, "requests": 2},
            {"users": 50, "requests": 2},
            {"users": 100, "requests": 1}
        ]

        for scenario in test_scenarios:
            print(f"\n   Testing {scenario['users']} concurrent users...")

            stress_metrics = await self.concurrent_load_test(
                "/health",
                concurrent_users=scenario["users"],
                requests_per_user=scenario["requests"]
            )

            await self.log_performance_result(
                f"Stress Test - {scenario['users']} Users",
                stress_metrics
            )

    async def test_memory_intensive_operations(self):
        """Test memory-intensive operations"""
        print("🧠 Testing Memory-Intensive Operations")

        # Test multiple report generations simultaneously
        report_request = {
            "session_id": "memory-test-session",
            "user_name": "Memory Test User",
            "report_type": "comprehensive",
            "report_format": "pdf"
        }

        memory_metrics = await self.concurrent_load_test(
            "/reports/generate/session",
            method="POST",
            data=report_request,
            concurrent_users=5,
            requests_per_user=2
        )
        await self.log_performance_result("Memory Intensive - Report Generation", memory_metrics)

    def analyze_performance_trends(self):
        """Analyze performance trends and identify bottlenecks"""
        print("\n" + "=" * 60)
        print("📈 PERFORMANCE ANALYSIS")
        print("=" * 60)

        if not self.performance_results:
            print("No performance data available")
            return

        # Response time analysis
        response_times = [r.get('avg_response_time', 0) for r in self.performance_results]
        avg_system_response = statistics.mean(response_times)

        print(f"Overall System Performance:")
        print(f"  Average Response Time: {avg_system_response:.1f}ms")
        print(f"  Best Performer: {min(response_times):.1f}ms")
        print(f"  Worst Performer: {max(response_times):.1f}ms")
        print()

        # Success rate analysis
        success_rates = [r.get('success_rate', 0) for r in self.performance_results]
        avg_success_rate = statistics.mean(success_rates)

        print(f"System Reliability:")
        print(f"  Average Success Rate: {avg_success_rate:.1f}%")
        print(f"  Lowest Success Rate: {min(success_rates):.1f}%")
        print()

        # Identify slow endpoints
        slow_tests = [r for r in self.performance_results if r.get('avg_response_time', 0) > 1000]
        if slow_tests:
            print("⚠️  Slow Endpoints (>1000ms):")
            for test in slow_tests:
                print(f"  - {test['test']}: {test['avg_response_time']:.1f}ms")
            print()

        # Identify unreliable endpoints
        unreliable_tests = [r for r in self.performance_results if r.get('success_rate', 100) < 95]
        if unreliable_tests:
            print("⚠️  Unreliable Endpoints (<95% success):")
            for test in unreliable_tests:
                print(f"  - {test['test']}: {test['success_rate']:.1f}%")
            print()

        # Performance grade
        if avg_system_response < 200 and avg_success_rate > 98:
            grade = "A+ (Excellent)"
        elif avg_system_response < 500 and avg_success_rate > 95:
            grade = "A (Good)"
        elif avg_system_response < 1000 and avg_success_rate > 90:
            grade = "B (Acceptable)"
        else:
            grade = "C (Needs Improvement)"

        print(f"🏆 Overall Performance Grade: {grade}")

    def generate_performance_report(self):
        """Generate detailed performance report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"performance_report_{timestamp}.json"

        report_data = {
            "test_execution": {
                "timestamp": datetime.now().isoformat(),
                "total_tests": len(self.performance_results),
                "test_duration": "N/A"  # Could be calculated if we track start/end times
            },
            "performance_results": self.performance_results,
            "summary": {
                "avg_response_time": statistics.mean([r.get('avg_response_time', 0) for r in self.performance_results]),
                "avg_success_rate": statistics.mean([r.get('success_rate', 0) for r in self.performance_results])
            }
        }

        try:
            with open(report_filename, 'w') as f:
                json.dump(report_data, f, indent=2)
            print(f"\n📄 Performance report saved: {report_filename}")
        except Exception as e:
            print(f"\n❌ Failed to save report: {e}")

    async def run_complete_performance_suite(self):
        """Run the complete performance test suite"""
        print("🚀 Starting Complete Performance Test Suite")
        print("=" * 60)

        await self.setup_session()

        try:
            # Core endpoint performance
            await self.test_health_endpoint_performance()
            await self.test_scoring_endpoint_performance()
            await self.test_cache_performance()
            await self.test_recommendations_performance()
            await self.test_report_generation_performance()

            # Stress testing
            await self.stress_test_concurrent_users()
            await self.test_memory_intensive_operations()

            # Analysis and reporting
            self.analyze_performance_trends()
            self.generate_performance_report()

        except Exception as e:
            print(f"❌ Performance testing error: {e}")
        finally:
            await self.teardown_session()


async def main():
    """Main performance test execution"""
    tester = PerformanceTestSuite()
    await tester.run_complete_performance_suite()


if __name__ == "__main__":
    asyncio.run(main())