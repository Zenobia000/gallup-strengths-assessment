#!/usr/bin/env python3
"""
Test Execution Script for Phase 5.3-5.4
Runs End-to-End and Performance Tests

Usage:
    python run_all_tests.py [--e2e] [--performance] [--all]
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path
import subprocess
import time
import requests

def check_server_health(base_url: str = "http://localhost:8004/api/v1", timeout: int = 30):
    """Check if the backend server is running"""
    print(f"🔍 Checking server health at {base_url}...")

    for attempt in range(timeout):
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Server is healthy and ready!")
                return True
        except requests.exceptions.RequestException:
            pass

        if attempt < timeout - 1:
            print(f"⏳ Server not ready, waiting... (attempt {attempt + 1}/{timeout})")
            time.sleep(1)

    print(f"❌ Server is not responding after {timeout} seconds")
    return False

def setup_python_path():
    """Setup Python path for test imports"""
    project_root = Path(__file__).parent
    src_path = project_root / "src" / "main" / "python"

    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    # Also set environment variable for subprocess
    env = os.environ.copy()
    pythonpath = env.get('PYTHONPATH', '')
    if str(src_path) not in pythonpath:
        env['PYTHONPATH'] = f"{src_path}:{pythonpath}" if pythonpath else str(src_path)

    return env

async def run_e2e_tests():
    """Run end-to-end tests"""
    print("\n" + "=" * 60)
    print("🧪 RUNNING END-TO-END TESTS (Phase 5.3)")
    print("=" * 60)

    try:
        # Add project root to Python path
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root / "src" / "test" / "e2e"))

        # Import and run E2E tests
        from test_complete_user_journey import E2ETestSuite

        tester = E2ETestSuite()
        await tester.run_complete_journey()

        return True
    except Exception as e:
        print(f"❌ E2E tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_performance_tests():
    """Run performance tests"""
    print("\n" + "=" * 60)
    print("📊 RUNNING PERFORMANCE TESTS (Phase 5.4)")
    print("=" * 60)

    try:
        # Add project root to Python path
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root / "src" / "test" / "performance"))

        # Import and run performance tests
        from test_system_performance import PerformanceTestSuite

        tester = PerformanceTestSuite()
        await tester.run_complete_performance_suite()

        return True
    except Exception as e:
        print(f"❌ Performance tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_unit_tests():
    """Run existing unit tests using pytest"""
    print("\n" + "=" * 60)
    print("🔬 RUNNING UNIT TESTS")
    print("=" * 60)

    try:
        project_root = Path(__file__).parent
        env = setup_python_path()

        # Find all test files
        test_dirs = [
            project_root / "src" / "test" / "unit",
            project_root / "tests"  # Legacy test directory
        ]

        test_files = []
        for test_dir in test_dirs:
            if test_dir.exists():
                test_files.extend(test_dir.glob("test_*.py"))

        if test_files:
            print(f"Found {len(test_files)} unit test files")

            # Run pytest
            cmd = [sys.executable, "-m", "pytest"] + [str(f) for f in test_files] + ["-v"]
            result = subprocess.run(cmd, env=env, cwd=str(project_root))

            return result.returncode == 0
        else:
            print("⚠️  No unit test files found")
            return True

    except Exception as e:
        print(f"❌ Unit tests failed: {e}")
        return False

def install_dependencies():
    """Install required test dependencies"""
    dependencies = ["aiohttp", "pytest", "pytest-asyncio"]

    print("📦 Installing test dependencies...")
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep],
                         check=True, capture_output=True)
            print(f"✅ Installed {dep}")
        except subprocess.CalledProcessError:
            print(f"⚠️  Failed to install {dep} (might already be installed)")

async def main():
    """Main test execution function"""
    parser = argparse.ArgumentParser(description="Run strength system tests")
    parser.add_argument("--e2e", action="store_true", help="Run end-to-end tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--install-deps", action="store_true", help="Install test dependencies")
    parser.add_argument("--skip-health-check", action="store_true", help="Skip server health check")

    args = parser.parse_args()

    # If no specific test type is specified, run all
    if not any([args.e2e, args.performance, args.unit]):
        args.all = True

    print("🚀 Strength System Test Suite")
    print("=" * 60)
    print(f"📅 Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Install dependencies if requested
    if args.install_deps:
        install_dependencies()
        return

    # Check server health unless skipped
    if not args.skip_health_check:
        if not check_server_health():
            print("\n💡 To start the server, run:")
            print("   cd src/main/python && python -m uvicorn api.main:app --host 0.0.0.0 --port 8002")
            print("\nOr skip health check with: --skip-health-check")
            return 1

    # Track test results
    test_results = {}

    # Run unit tests
    if args.unit or args.all:
        test_results["unit"] = run_unit_tests()

    # Run E2E tests
    if args.e2e or args.all:
        test_results["e2e"] = await run_e2e_tests()

    # Run performance tests
    if args.performance or args.all:
        test_results["performance"] = await run_performance_tests()

    # Generate summary
    print("\n" + "=" * 60)
    print("📋 TEST EXECUTION SUMMARY")
    print("=" * 60)

    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    failed_tests = total_tests - passed_tests

    for test_type, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_type.upper()} Tests: {status}")

    print(f"\nOverall: {passed_tests}/{total_tests} test suites passed")

    if failed_tests == 0:
        print("🎉 ALL TEST SUITES PASSED!")
        print("\n✅ Phase 5.3-5.4 (End-to-End & Performance Testing) COMPLETE")
        return 0
    else:
        print(f"⚠️  {failed_tests} test suite(s) failed")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)