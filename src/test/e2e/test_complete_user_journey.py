#!/usr/bin/env python3
"""
End-to-End Test Suite - Complete User Journey
Phase 5.3: 端到端測試

Tests the complete user flow from consent to report generation
"""

import asyncio
import aiohttp
import pytest
import time
from datetime import datetime
from typing import Dict, List, Any

class E2ETestSuite:
    def __init__(self, base_url: str = "http://localhost:8004/api/v1"):
        self.base_url = base_url
        self.session_id = None
        self.test_results = []

    async def setup_session(self):
        """Setup aiohttp session for async requests"""
        self.session = aiohttp.ClientSession()

    async def teardown_session(self):
        """Cleanup session"""
        if self.session:
            await self.session.close()

    async def log_test_result(self, test_name: str, success: bool,
                            response_time: float = 0, details: str = ""):
        """Log test result with timing"""
        result = {
            "test": test_name,
            "success": success,
            "response_time_ms": round(response_time * 1000, 2),
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)

        status = "✅" if success else "❌"
        print(f"{status} {test_name} ({result['response_time_ms']}ms)")
        if details:
            print(f"   {details}")

    async def test_health_check(self):
        """Test system health"""
        start_time = time.time()
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                response_time = time.time() - start_time

                if response.status == 200:
                    data = await response.json()
                    await self.log_test_result(
                        "Health Check", True, response_time,
                        f"Status: {data.get('status', 'unknown')}"
                    )
                    return True
                else:
                    await self.log_test_result(
                        "Health Check", False, response_time,
                        f"HTTP {response.status}"
                    )
                    return False
        except Exception as e:
            response_time = time.time() - start_time
            await self.log_test_result(
                "Health Check", False, response_time, str(e)
            )
            return False

    async def test_consent_submission(self):
        """Test user consent submission"""
        start_time = time.time()
        try:
            consent_data = {
                "user_agrees": True,
                "data_usage_consent": True,
                "age_verification": True,
                "user_email": "test@example.com",
                "user_name": "Test User"
            }

            async with self.session.post(
                f"{self.base_url}/consent",
                json=consent_data
            ) as response:
                response_time = time.time() - start_time

                if response.status == 200:
                    data = await response.json()
                    self.session_id = data.get('session_id')
                    await self.log_test_result(
                        "Consent Submission", True, response_time,
                        f"Session ID: {self.session_id}"
                    )
                    return True
                else:
                    await self.log_test_result(
                        "Consent Submission", False, response_time,
                        f"HTTP {response.status}"
                    )
                    return False
        except Exception as e:
            response_time = time.time() - start_time
            await self.log_test_result(
                "Consent Submission", False, response_time, str(e)
            )
            return False

    async def test_session_creation(self):
        """Test session creation if consent didn't create one"""
        if self.session_id:
            return True

        start_time = time.time()
        try:
            async with self.session.post(f"{self.base_url}/sessions") as response:
                response_time = time.time() - start_time

                if response.status == 201:
                    data = await response.json()
                    self.session_id = data.get('session_id')
                    await self.log_test_result(
                        "Session Creation", True, response_time,
                        f"Session ID: {self.session_id}"
                    )
                    return True
                else:
                    await self.log_test_result(
                        "Session Creation", False, response_time,
                        f"HTTP {response.status}"
                    )
                    return False
        except Exception as e:
            response_time = time.time() - start_time
            await self.log_test_result(
                "Session Creation", False, response_time, str(e)
            )
            return False

    async def test_get_questions(self):
        """Test getting assessment questions"""
        start_time = time.time()
        try:
            async with self.session.get(f"{self.base_url}/scoring/questions") as response:
                response_time = time.time() - start_time

                if response.status == 200:
                    data = await response.json()
                    questions = data.get('questions', [])
                    await self.log_test_result(
                        "Get Questions", True, response_time,
                        f"Found {len(questions)} questions"
                    )
                    return questions
                else:
                    await self.log_test_result(
                        "Get Questions", False, response_time,
                        f"HTTP {response.status}"
                    )
                    return None
        except Exception as e:
            response_time = time.time() - start_time
            await self.log_test_result(
                "Get Questions", False, response_time, str(e)
            )
            return None

    async def test_submit_responses(self, questions: List[Dict]):
        """Test submitting assessment responses"""
        if not questions or not self.session_id:
            return False

        # Create sample responses
        responses = []
        for i, question in enumerate(questions[:20]):  # Test with first 20 questions
            response_data = {
                "question_id": question.get('id', i + 1),
                "score": (i % 5) + 1  # Vary responses 1-5
            }
            responses.append(response_data)

        start_time = time.time()
        try:
            payload = {
                "session_id": self.session_id,
                "responses": responses
            }

            async with self.session.post(
                f"{self.base_url}/scoring/submit",
                json=payload
            ) as response:
                response_time = time.time() - start_time

                if response.status == 200:
                    data = await response.json()
                    await self.log_test_result(
                        "Submit Responses", True, response_time,
                        f"Submitted {len(responses)} responses"
                    )
                    return True
                else:
                    await self.log_test_result(
                        "Submit Responses", False, response_time,
                        f"HTTP {response.status}"
                    )
                    return False
        except Exception as e:
            response_time = time.time() - start_time
            await self.log_test_result(
                "Submit Responses", False, response_time, str(e)
            )
            return False

    async def test_get_results(self):
        """Test getting assessment results"""
        if not self.session_id:
            return False

        start_time = time.time()
        try:
            async with self.session.get(
                f"{self.base_url}/sessions/{self.session_id}/results"
            ) as response:
                response_time = time.time() - start_time

                if response.status == 200:
                    data = await response.json()
                    results = data.get('results', {})
                    strengths = results.get('strengths', [])
                    await self.log_test_result(
                        "Get Results", True, response_time,
                        f"Found {len(strengths)} strengths"
                    )
                    return data
                else:
                    await self.log_test_result(
                        "Get Results", False, response_time,
                        f"HTTP {response.status}"
                    )
                    return None
        except Exception as e:
            response_time = time.time() - start_time
            await self.log_test_result(
                "Get Results", False, response_time, str(e)
            )
            return None

    async def test_get_recommendations(self):
        """Test getting career and development recommendations"""
        if not self.session_id:
            return False

        # Test career recommendations
        start_time = time.time()
        try:
            async with self.session.get(
                f"{self.base_url}/recommendations/{self.session_id}/careers"
            ) as response:
                response_time = time.time() - start_time

                if response.status in [200, 404]:  # 404 is acceptable if no recommendations yet
                    await self.log_test_result(
                        "Career Recommendations", True, response_time,
                        f"Status: {response.status}"
                    )
                    career_success = True
                else:
                    await self.log_test_result(
                        "Career Recommendations", False, response_time,
                        f"HTTP {response.status}"
                    )
                    career_success = False
        except Exception as e:
            response_time = time.time() - start_time
            await self.log_test_result(
                "Career Recommendations", False, response_time, str(e)
            )
            career_success = False

        # Test development recommendations
        start_time = time.time()
        try:
            async with self.session.get(
                f"{self.base_url}/recommendations/{self.session_id}/development"
            ) as response:
                response_time = time.time() - start_time

                if response.status in [200, 404]:  # 404 is acceptable if no recommendations yet
                    await self.log_test_result(
                        "Development Recommendations", True, response_time,
                        f"Status: {response.status}"
                    )
                    dev_success = True
                else:
                    await self.log_test_result(
                        "Development Recommendations", False, response_time,
                        f"HTTP {response.status}"
                    )
                    dev_success = False
        except Exception as e:
            response_time = time.time() - start_time
            await self.log_test_result(
                "Development Recommendations", False, response_time, str(e)
            )
            dev_success = False

        return career_success and dev_success

    async def test_report_generation(self):
        """Test PDF report generation"""
        if not self.session_id:
            return False

        start_time = time.time()
        try:
            payload = {
                "session_id": self.session_id,
                "user_name": "Test User",
                "report_type": "comprehensive",
                "report_format": "pdf"
            }

            async with self.session.post(
                f"{self.base_url}/reports/generate/session",
                json=payload
            ) as response:
                response_time = time.time() - start_time

                if response.status in [200, 201]:
                    data = await response.json()
                    report_id = data.get('data', {}).get('report_id')
                    await self.log_test_result(
                        "Report Generation", True, response_time,
                        f"Report ID: {report_id}"
                    )
                    return True
                else:
                    await self.log_test_result(
                        "Report Generation", False, response_time,
                        f"HTTP {response.status}"
                    )
                    return False
        except Exception as e:
            response_time = time.time() - start_time
            await self.log_test_result(
                "Report Generation", False, response_time, str(e)
            )
            return False

    async def test_cache_functionality(self):
        """Test cache system functionality"""
        start_time = time.time()
        try:
            async with self.session.get(f"{self.base_url}/cache/health") as response:
                response_time = time.time() - start_time

                if response.status == 200:
                    data = await response.json()
                    is_healthy = data.get('is_healthy', False)
                    await self.log_test_result(
                        "Cache Health", True, response_time,
                        f"Healthy: {is_healthy}"
                    )
                    return True
                else:
                    await self.log_test_result(
                        "Cache Health", False, response_time,
                        f"HTTP {response.status}"
                    )
                    return False
        except Exception as e:
            response_time = time.time() - start_time
            await self.log_test_result(
                "Cache Health", False, response_time, str(e)
            )
            return False

    async def run_complete_journey(self):
        """Run the complete end-to-end user journey"""
        print("🚀 Starting Complete User Journey Test")
        print("=" * 50)

        await self.setup_session()

        try:
            # Step 1: Health check
            if not await self.test_health_check():
                print("❌ System health check failed - aborting")
                return False

            # Step 2: Consent submission
            await self.test_consent_submission()

            # Step 3: Session creation (if needed)
            await self.test_session_creation()

            # Step 4: Get questions
            questions = await self.test_get_questions()

            # Step 5: Submit responses
            if questions:
                await self.test_submit_responses(questions)

            # Step 6: Get results
            await self.test_get_results()

            # Step 7: Get recommendations
            await self.test_get_recommendations()

            # Step 8: Generate report
            await self.test_report_generation()

            # Step 9: Test cache
            await self.test_cache_functionality()

            # Generate summary
            self.generate_test_summary()

        finally:
            await self.teardown_session()

    def generate_test_summary(self):
        """Generate test execution summary"""
        print("\n" + "=" * 50)
        print("📊 END-TO-END TEST SUMMARY")
        print("=" * 50)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests

        avg_response_time = sum(r['response_time_ms'] for r in self.test_results) / total_tests

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Average Response Time: {avg_response_time:.1f}ms")
        print()

        # Performance analysis
        slow_tests = [r for r in self.test_results if r['response_time_ms'] > 1000]
        if slow_tests:
            print("⚠️  Slow Tests (>1000ms):")
            for test in slow_tests:
                print(f"   - {test['test']}: {test['response_time_ms']}ms")
            print()

        # Failed tests analysis
        failed_test_results = [r for r in self.test_results if not r['success']]
        if failed_test_results:
            print("❌ Failed Tests:")
            for test in failed_test_results:
                print(f"   - {test['test']}: {test['details']}")
            print()

        if failed_tests == 0:
            print("🎉 ALL E2E TESTS PASSED!")
        else:
            print(f"⚠️  {failed_tests} tests failed. Review issues above.")

        return failed_tests == 0

async def main():
    """Main test execution"""
    tester = E2ETestSuite()
    await tester.run_complete_journey()

if __name__ == "__main__":
    asyncio.run(main())