#!/usr/bin/env python3
"""
測試執行腳本 - Gallup 優勢測驗專案
提供標準化的測試執行方式，支援不同測試場景

遵循 comprehensive-testing-plan.md 的測試策略
符合 structure_guide.md 的測試架構
"""

import sys
import subprocess
import argparse
import os
from pathlib import Path
from typing import List, Optional
import time


class TestRunner:
    """測試執行器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.output_dir = project_root / "output"
        self.logs_dir = self.output_dir / "logs"
        self.coverage_dir = self.output_dir / "coverage"

        # 確保輸出目錄存在
        self.output_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        self.coverage_dir.mkdir(exist_ok=True)

    def run_unit_tests(self, verbose: bool = True) -> int:
        """執行單元測試"""
        print("🧪 執行單元測試...")

        cmd = [
            "python", "-m", "pytest",
            "src/test/unit/",
            "-m", "unit",
            "--cov=src/main/python",
            "--cov-report=term-missing",
            "--cov-report=html:output/coverage/unit",
            "--junit-xml=output/unit-tests.xml"
        ]

        if verbose:
            cmd.append("-v")

        return self._run_command(cmd, "單元測試")

    def run_integration_tests(self, verbose: bool = True) -> int:
        """執行整合測試"""
        print("🔗 執行整合測試...")

        cmd = [
            "python", "-m", "pytest",
            "src/test/integration/",
            "-m", "integration",
            "--junit-xml=output/integration-tests.xml"
        ]

        if verbose:
            cmd.append("-v")

        return self._run_command(cmd, "整合測試")

    def run_e2e_tests(self, verbose: bool = True) -> int:
        """執行端到端測試"""
        print("🌐 執行端到端測試...")

        cmd = [
            "python", "-m", "pytest",
            "src/test/e2e/",
            "-m", "e2e",
            "--junit-xml=output/e2e-tests.xml",
            "--timeout=60"  # E2E 測試較長的超時時間
        ]

        if verbose:
            cmd.append("-v")

        return self._run_command(cmd, "端到端測試")

    def run_performance_tests(self, verbose: bool = True) -> int:
        """執行效能測試"""
        print("⚡ 執行效能測試...")

        cmd = [
            "python", "-m", "pytest",
            "src/test/",
            "-m", "performance",
            "--benchmark-only",
            "--benchmark-json=output/benchmark.json",
            "--junit-xml=output/performance-tests.xml"
        ]

        if verbose:
            cmd.append("-v")

        return self._run_command(cmd, "效能測試")

    def run_smoke_tests(self, verbose: bool = True) -> int:
        """執行煙霧測試 (快速驗證)"""
        print("💨 執行煙霧測試...")

        cmd = [
            "python", "-m", "pytest",
            "src/test/",
            "-m", "smoke",
            "--maxfail=1",  # 第一個失敗就停止
            "--tb=short",
            "--junit-xml=output/smoke-tests.xml"
        ]

        if verbose:
            cmd.append("-v")

        return self._run_command(cmd, "煙霧測試")

    def run_all_tests(self, verbose: bool = True, fail_fast: bool = False) -> int:
        """執行所有測試"""
        print("🎯 執行完整測試套件...")

        cmd = [
            "python", "-m", "pytest",
            "src/test/",
            "--cov=src/main/python",
            "--cov-report=term-missing",
            "--cov-report=html:output/coverage/all",
            "--cov-report=xml:output/coverage.xml",
            "--junit-xml=output/all-tests.xml"
        ]

        if verbose:
            cmd.append("-v")

        if fail_fast:
            cmd.append("--maxfail=1")

        return self._run_command(cmd, "完整測試套件")

    def run_coverage_report(self) -> int:
        """生成覆蓋率報告"""
        print("📊 生成覆蓋率報告...")

        # 先執行測試以生成覆蓋率資料
        unit_result = self.run_unit_tests(verbose=False)
        if unit_result != 0:
            print("❌ 單元測試失敗，無法生成覆蓋率報告")
            return unit_result

        # 生成 HTML 報告
        cmd = [
            "python", "-m", "coverage", "html",
            "-d", "output/coverage/detailed",
            "--title", "Gallup 優勢測驗 - 程式碼覆蓋率報告"
        ]

        result = self._run_command(cmd, "覆蓋率報告生成")

        if result == 0:
            print(f"📈 覆蓋率報告已生成: {self.coverage_dir}/detailed/index.html")

        return result

    def run_security_tests(self, verbose: bool = True) -> int:
        """執行安全測試"""
        print("🔒 執行安全測試...")

        cmd = [
            "python", "-m", "pytest",
            "src/test/",
            "-m", "security",
            "--junit-xml=output/security-tests.xml"
        ]

        if verbose:
            cmd.append("-v")

        return self._run_command(cmd, "安全測試")

    def run_regression_tests(self, verbose: bool = True) -> int:
        """執行回歸測試"""
        print("🔄 執行回歸測試...")

        cmd = [
            "python", "-m", "pytest",
            "src/test/",
            "-m", "regression",
            "--junit-xml=output/regression-tests.xml"
        ]

        if verbose:
            cmd.append("-v")

        return self._run_command(cmd, "回歸測試")

    def _run_command(self, cmd: List[str], test_type: str) -> int:
        """執行命令並處理結果"""
        start_time = time.time()

        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=False,
                text=True,
                env=dict(os.environ, PYTHONPATH=str(self.project_root / "src" / "main" / "python"))
            )

            duration = time.time() - start_time

            if result.returncode == 0:
                print(f"✅ {test_type} 執行成功 ({duration:.2f}s)")
            else:
                print(f"❌ {test_type} 執行失敗 ({duration:.2f}s)")

            return result.returncode

        except FileNotFoundError:
            print("❌ pytest 未安裝或不在 PATH 中")
            print("請執行: pip install pytest pytest-cov pytest-xdist")
            return 1

        except KeyboardInterrupt:
            print(f"\n⏹️  {test_type} 被使用者中斷")
            return 130

    def check_dependencies(self) -> bool:
        """檢查測試依賴是否安裝"""
        required_packages = [
            "pytest",
            "pytest-cov",
            "pytest-timeout",
            "pytest-benchmark",
            "pytest-mock"
        ]

        missing_packages = []

        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            print("❌ 缺少必要的測試套件:")
            for package in missing_packages:
                print(f"   - {package}")
            print("\n請執行以下命令安裝:")
            print(f"pip install {' '.join(missing_packages)}")
            return False

        print("✅ 所有測試依賴都已安裝")
        return True

    def cleanup_output(self):
        """清理測試輸出檔案"""
        print("🧹 清理測試輸出...")

        patterns_to_clean = [
            "output/*.xml",
            "output/*.json",
            "output/coverage/*",
            "output/logs/*.log",
            "output/.pytest_cache/*",
            "**/__pycache__",
            "**/*.pyc"
        ]

        for pattern in patterns_to_clean:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    import shutil
                    shutil.rmtree(file_path, ignore_errors=True)

        print("✅ 清理完成")


def main():
    """主函式"""
    parser = argparse.ArgumentParser(
        description="Gallup 優勢測驗專案測試執行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
測試類型:
  unit        單元測試 (70% 目標覆蓋率)
  integration 整合測試 (API + 資料庫)
  e2e         端到端測試 (完整使用者流程)
  performance 效能測試 (基準測試)
  smoke       煙霧測試 (快速驗證)
  security    安全測試
  regression  回歸測試
  all         完整測試套件
  coverage    覆蓋率報告

範例:
  python scripts/run_tests.py unit -v          # 詳細單元測試
  python scripts/run_tests.py all --fail-fast  # 快速失敗模式
  python scripts/run_tests.py smoke -q         # 安靜煙霧測試
        """
    )

    parser.add_argument(
        "test_type",
        choices=["unit", "integration", "e2e", "performance", "smoke",
                "security", "regression", "all", "coverage", "cleanup"],
        help="要執行的測試類型"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="詳細輸出"
    )

    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="安靜模式"
    )

    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="第一個測試失敗時停止"
    )

    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="只檢查依賴套件"
    )

    args = parser.parse_args()

    # 設定專案根目錄
    project_root = Path(__file__).parent.parent
    runner = TestRunner(project_root)

    # 檢查依賴
    if args.check_deps or args.test_type != "cleanup":
        if not runner.check_dependencies():
            return 1

    if args.check_deps:
        return 0

    # 設定詳細程度
    verbose = args.verbose and not args.quiet

    # 執行對應的測試
    test_methods = {
        "unit": runner.run_unit_tests,
        "integration": runner.run_integration_tests,
        "e2e": runner.run_e2e_tests,
        "performance": runner.run_performance_tests,
        "smoke": runner.run_smoke_tests,
        "security": runner.run_security_tests,
        "regression": runner.run_regression_tests,
        "all": runner.run_all_tests,
        "coverage": runner.run_coverage_report,
        "cleanup": runner.cleanup_output
    }

    if args.test_type == "cleanup":
        runner.cleanup_output()
        return 0

    method = test_methods[args.test_type]

    # 特殊參數處理
    if args.test_type == "all":
        return method(verbose=verbose, fail_fast=args.fail_fast)
    elif args.test_type == "coverage":
        return method()
    else:
        return method(verbose=verbose)


if __name__ == "__main__":
    sys.exit(main())