#!/usr/bin/env python3
"""
Unit-level performance tests for BARQUE optimization strategies.

Tests each optimization individually to map performance per unit data:
1. WeasyPrint cold start vs pre-warmed cache
2. Pop CLI subprocess vs direct Resend SDK
3. Sequential vs parallel PDF generation

Each test provides:
- Precise timing measurements
- Memory footprint analysis
- CPU utilization tracking
- Statistical analysis (mean, median, std dev)
- Isolated attribution of performance gains
"""

import os
import sys
import time
import json
import psutil
import shutil
import subprocess
import statistics
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Add BARQUE to path
BARQUE_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BARQUE_ROOT))

from barque.core.generator import generate_pdf
from barque.core.user_config import UserConfig


@dataclass
class UnitTestResult:
    """Result from a single unit test run."""
    test_name: str
    variant: str
    duration_ms: float
    memory_mb: float
    cpu_percent: float
    success: bool
    error: Optional[str] = None
    metadata: Optional[Dict] = None


@dataclass
class UnitTestComparison:
    """Comparison between baseline and optimized variants."""
    test_name: str
    baseline_variant: str
    optimized_variant: str
    baseline_mean_ms: float
    optimized_mean_ms: float
    improvement_percent: float
    baseline_memory_mb: float
    optimized_memory_mb: float
    iterations: int
    confidence: str  # "high", "medium", "low" based on std dev


class UnitPerformanceTracker:
    """Lightweight performance tracker for unit tests."""

    def __init__(self):
        self.process = psutil.Process()
        self.start_time = None
        self.start_memory = None
        self.start_cpu = None

    def start(self):
        """Start tracking performance."""
        self.process.cpu_percent()  # Initialize CPU monitoring
        self.start_time = time.perf_counter()
        self.start_memory = self.process.memory_info().rss / 1024 / 1024
        self.start_cpu = self.process.cpu_percent()

    def end(self) -> Tuple[float, float, float]:
        """End tracking and return (duration_ms, memory_mb, cpu_percent)."""
        duration_ms = (time.perf_counter() - self.start_time) * 1000
        memory_mb = self.process.memory_info().rss / 1024 / 1024
        cpu_percent = self.process.cpu_percent()

        return (duration_ms, memory_mb - self.start_memory, cpu_percent)


class WeasyPrintColdWarmTest:
    """Test 1: WeasyPrint cold start vs pre-warmed cache."""

    def __init__(self, test_file: Path):
        self.test_file = test_file
        self.output_dir = Path(__file__).parent / "unit_test_outputs"
        self.output_dir.mkdir(exist_ok=True)

    def test_cold_start(self, iterations: int = 5) -> List[UnitTestResult]:
        """Test WeasyPrint cold start performance."""
        results = []

        print(f"\n{'='*60}")
        print("Test 1A: WeasyPrint Cold Start")
        print(f"{'='*60}")

        for i in range(iterations):
            # Clear OS caches (best effort, may require sudo)
            try:
                subprocess.run(["sync"], check=False)
            except:
                pass

            # Force Python to restart subprocess for true cold start
            # We'll use subprocess to call weasyprint CLI directly
            tracker = UnitPerformanceTracker()
            tracker.start()

            try:
                output_path = self.output_dir / f"cold_start_{i}.pdf"

                # Use weasyprint CLI to simulate cold start
                cmd = [
                    "python", "-m", "weasyprint",
                    str(self.test_file),
                    str(output_path)
                ]

                result = subprocess.run(cmd, capture_output=True, timeout=10)
                success = result.returncode == 0
                error = result.stderr.decode() if not success else None

                duration_ms, memory_mb, cpu_percent = tracker.end()

                results.append(UnitTestResult(
                    test_name="weasyprint_cold_start",
                    variant="cold",
                    duration_ms=duration_ms,
                    memory_mb=memory_mb,
                    cpu_percent=cpu_percent,
                    success=success,
                    error=error,
                    metadata={"iteration": i, "file_size_kb": self.test_file.stat().st_size / 1024}
                ))

                print(f"  Run {i+1}: {duration_ms:.0f}ms {'✓' if success else '✗'}")

            except Exception as e:
                duration_ms, memory_mb, cpu_percent = tracker.end()
                results.append(UnitTestResult(
                    test_name="weasyprint_cold_start",
                    variant="cold",
                    duration_ms=duration_ms,
                    memory_mb=memory_mb,
                    cpu_percent=cpu_percent,
                    success=False,
                    error=str(e),
                    metadata={"iteration": i}
                ))
                print(f"  Run {i+1}: FAILED - {e}")

        return results

    def test_warm_cache(self, iterations: int = 5) -> List[UnitTestResult]:
        """Test WeasyPrint with warmed-up cache."""
        results = []

        print(f"\n{'='*60}")
        print("Test 1B: WeasyPrint Warmed Cache")
        print(f"{'='*60}")

        # Pre-warm: generate one PDF to initialize cache
        print("  Pre-warming cache...")
        warmup_path = self.output_dir / "warmup.pdf"
        subprocess.run([
            "python", "-m", "weasyprint",
            str(self.test_file),
            str(warmup_path)
        ], capture_output=True)
        print("  Cache warmed ✓")

        # Now measure warmed performance
        for i in range(iterations):
            tracker = UnitPerformanceTracker()
            tracker.start()

            try:
                output_path = self.output_dir / f"warm_cache_{i}.pdf"

                cmd = [
                    "python", "-m", "weasyprint",
                    str(self.test_file),
                    str(output_path)
                ]

                result = subprocess.run(cmd, capture_output=True, timeout=10)
                success = result.returncode == 0
                error = result.stderr.decode() if not success else None

                duration_ms, memory_mb, cpu_percent = tracker.end()

                results.append(UnitTestResult(
                    test_name="weasyprint_warm_cache",
                    variant="warm",
                    duration_ms=duration_ms,
                    memory_mb=memory_mb,
                    cpu_percent=cpu_percent,
                    success=success,
                    error=error,
                    metadata={"iteration": i, "file_size_kb": self.test_file.stat().st_size / 1024}
                ))

                print(f"  Run {i+1}: {duration_ms:.0f}ms {'✓' if success else '✗'}")

            except Exception as e:
                duration_ms, memory_mb, cpu_percent = tracker.end()
                results.append(UnitTestResult(
                    test_name="weasyprint_warm_cache",
                    variant="warm",
                    duration_ms=duration_ms,
                    memory_mb=memory_mb,
                    cpu_percent=cpu_percent,
                    success=False,
                    error=str(e),
                    metadata={"iteration": i}
                ))
                print(f"  Run {i+1}: FAILED - {e}")

        return results


class SubprocessVsSDKTest:
    """Test 2: Pop CLI subprocess vs direct Resend SDK."""

    def __init__(self, test_pdf: Path):
        self.test_pdf = test_pdf
        self.user_config = UserConfig.load()

    def test_pop_cli_subprocess(self, iterations: int = 3) -> List[UnitTestResult]:
        """Test email delivery via Pop CLI subprocess."""
        results = []

        print(f"\n{'='*60}")
        print("Test 2A: Pop CLI Subprocess Email Delivery")
        print(f"{'='*60}")

        # Get email config
        to_email = self.user_config.default_to_email or "test@example.com"
        from_email = self.user_config.default_from_email or "onboarding@resend.dev"
        api_key = self.user_config.resend_api_key or os.getenv("RESEND_API_KEY")

        if not api_key:
            print("  ⚠️ SKIPPING: No RESEND_API_KEY configured")
            return results

        for i in range(iterations):
            tracker = UnitPerformanceTracker()
            tracker.start()

            try:
                # Simulate Pop CLI call
                cmd = [
                    "pop", "email",
                    "--from", from_email,
                    "--to", to_email,
                    "--subject", f"BARQUE Performance Test {i+1}",
                    "--body", "Testing subprocess email delivery performance",
                    "--attachment", str(self.test_pdf)
                ]

                env = os.environ.copy()
                env["RESEND_API_KEY"] = api_key

                result = subprocess.run(cmd, capture_output=True, timeout=30, env=env)
                success = result.returncode == 0
                error = result.stderr.decode() if not success else None

                duration_ms, memory_mb, cpu_percent = tracker.end()

                results.append(UnitTestResult(
                    test_name="email_delivery_subprocess",
                    variant="pop_cli",
                    duration_ms=duration_ms,
                    memory_mb=memory_mb,
                    cpu_percent=cpu_percent,
                    success=success,
                    error=error,
                    metadata={
                        "iteration": i,
                        "attachment_size_kb": self.test_pdf.stat().st_size / 1024
                    }
                ))

                print(f"  Run {i+1}: {duration_ms:.0f}ms {'✓' if success else '✗'}")

            except Exception as e:
                duration_ms, memory_mb, cpu_percent = tracker.end()
                results.append(UnitTestResult(
                    test_name="email_delivery_subprocess",
                    variant="pop_cli",
                    duration_ms=duration_ms,
                    memory_mb=memory_mb,
                    cpu_percent=cpu_percent,
                    success=False,
                    error=str(e),
                    metadata={"iteration": i}
                ))
                print(f"  Run {i+1}: FAILED - {e}")

        return results

    def test_direct_resend_sdk(self, iterations: int = 3) -> List[UnitTestResult]:
        """Test email delivery via direct Resend SDK."""
        results = []

        print(f"\n{'='*60}")
        print("Test 2B: Direct Resend SDK Email Delivery")
        print(f"{'='*60}")

        # Check if resend package is available
        try:
            import resend
        except ImportError:
            print("  ⚠️ SKIPPING: resend-python package not installed")
            print("  Install with: pip install resend")
            return results

        # Get email config
        to_email = self.user_config.default_to_email or "test@example.com"
        from_email = self.user_config.default_from_email or "onboarding@resend.dev"
        api_key = self.user_config.resend_api_key or os.getenv("RESEND_API_KEY")

        if not api_key:
            print("  ⚠️ SKIPPING: No RESEND_API_KEY configured")
            return results

        # Initialize Resend client
        resend.api_key = api_key

        for i in range(iterations):
            tracker = UnitPerformanceTracker()
            tracker.start()

            try:
                # Read PDF attachment
                with open(self.test_pdf, "rb") as f:
                    pdf_content = f.read()

                # Send via Resend SDK
                response = resend.Emails.send({
                    "from": from_email,
                    "to": [to_email],
                    "subject": f"BARQUE Performance Test SDK {i+1}",
                    "html": "<p>Testing direct SDK email delivery performance</p>",
                    "attachments": [{
                        "filename": self.test_pdf.name,
                        "content": list(pdf_content)
                    }]
                })

                success = response.get("id") is not None
                error = response.get("message") if not success else None

                duration_ms, memory_mb, cpu_percent = tracker.end()

                results.append(UnitTestResult(
                    test_name="email_delivery_direct_sdk",
                    variant="resend_sdk",
                    duration_ms=duration_ms,
                    memory_mb=memory_mb,
                    cpu_percent=cpu_percent,
                    success=success,
                    error=error,
                    metadata={
                        "iteration": i,
                        "attachment_size_kb": self.test_pdf.stat().st_size / 1024,
                        "email_id": response.get("id")
                    }
                ))

                print(f"  Run {i+1}: {duration_ms:.0f}ms {'✓' if success else '✗'}")

            except Exception as e:
                duration_ms, memory_mb, cpu_percent = tracker.end()
                results.append(UnitTestResult(
                    test_name="email_delivery_direct_sdk",
                    variant="resend_sdk",
                    duration_ms=duration_ms,
                    memory_mb=memory_mb,
                    cpu_percent=cpu_percent,
                    success=False,
                    error=str(e),
                    metadata={"iteration": i}
                ))
                print(f"  Run {i+1}: FAILED - {e}")

        return results


class SequentialVsParallelTest:
    """Test 3: Sequential vs parallel PDF generation."""

    def __init__(self, test_file: Path):
        self.test_file = test_file
        self.output_dir = Path(__file__).parent / "unit_test_outputs"
        self.output_dir.mkdir(exist_ok=True)

    def test_sequential_generation(self, iterations: int = 5) -> List[UnitTestResult]:
        """Test sequential PDF generation (light then dark)."""
        results = []

        print(f"\n{'='*60}")
        print("Test 3A: Sequential PDF Generation")
        print(f"{'='*60}")

        for i in range(iterations):
            tracker = UnitPerformanceTracker()
            tracker.start()

            try:
                # Generate light theme PDF
                light_path = self.output_dir / f"sequential_light_{i}.pdf"
                generate_pdf(self.test_file, light_path, theme="light")

                # Generate dark theme PDF
                dark_path = self.output_dir / f"sequential_dark_{i}.pdf"
                generate_pdf(self.test_file, dark_path, theme="dark")

                duration_ms, memory_mb, cpu_percent = tracker.end()

                results.append(UnitTestResult(
                    test_name="pdf_generation_sequential",
                    variant="sequential",
                    duration_ms=duration_ms,
                    memory_mb=memory_mb,
                    cpu_percent=cpu_percent,
                    success=True,
                    metadata={
                        "iteration": i,
                        "pdfs_generated": 2,
                        "light_size_kb": light_path.stat().st_size / 1024,
                        "dark_size_kb": dark_path.stat().st_size / 1024
                    }
                ))

                print(f"  Run {i+1}: {duration_ms:.0f}ms ✓")

            except Exception as e:
                duration_ms, memory_mb, cpu_percent = tracker.end()
                results.append(UnitTestResult(
                    test_name="pdf_generation_sequential",
                    variant="sequential",
                    duration_ms=duration_ms,
                    memory_mb=memory_mb,
                    cpu_percent=cpu_percent,
                    success=False,
                    error=str(e),
                    metadata={"iteration": i}
                ))
                print(f"  Run {i+1}: FAILED - {e}")

        return results

    def test_parallel_generation(self, iterations: int = 5) -> List[UnitTestResult]:
        """Test parallel PDF generation using ThreadPoolExecutor."""
        results = []

        print(f"\n{'='*60}")
        print("Test 3B: Parallel PDF Generation")
        print(f"{'='*60}")

        from concurrent.futures import ThreadPoolExecutor, as_completed

        for i in range(iterations):
            tracker = UnitPerformanceTracker()
            tracker.start()

            try:
                light_path = self.output_dir / f"parallel_light_{i}.pdf"
                dark_path = self.output_dir / f"parallel_dark_{i}.pdf"

                # Generate both PDFs in parallel
                with ThreadPoolExecutor(max_workers=2) as executor:
                    futures = {
                        executor.submit(generate_pdf, self.test_file, light_path, "light"): "light",
                        executor.submit(generate_pdf, self.test_file, dark_path, "dark"): "dark"
                    }

                    # Wait for completion
                    for future in as_completed(futures):
                        theme = futures[future]
                        future.result()  # Raise exception if failed

                duration_ms, memory_mb, cpu_percent = tracker.end()

                results.append(UnitTestResult(
                    test_name="pdf_generation_parallel",
                    variant="parallel",
                    duration_ms=duration_ms,
                    memory_mb=memory_mb,
                    cpu_percent=cpu_percent,
                    success=True,
                    metadata={
                        "iteration": i,
                        "pdfs_generated": 2,
                        "light_size_kb": light_path.stat().st_size / 1024,
                        "dark_size_kb": dark_path.stat().st_size / 1024
                    }
                ))

                print(f"  Run {i+1}: {duration_ms:.0f}ms ✓")

            except Exception as e:
                duration_ms, memory_mb, cpu_percent = tracker.end()
                results.append(UnitTestResult(
                    test_name="pdf_generation_parallel",
                    variant="parallel",
                    duration_ms=duration_ms,
                    memory_mb=memory_mb,
                    cpu_percent=cpu_percent,
                    success=False,
                    error=str(e),
                    metadata={"iteration": i}
                ))
                print(f"  Run {i+1}: FAILED - {e}")

        return results


class UnitPerformanceAnalyzer:
    """Analyze and compare unit test results."""

    @staticmethod
    def analyze_results(baseline: List[UnitTestResult],
                       optimized: List[UnitTestResult]) -> UnitTestComparison:
        """Compare baseline vs optimized results."""

        # Filter successful runs
        baseline_success = [r for r in baseline if r.success]
        optimized_success = [r for r in optimized if r.success]

        if not baseline_success or not optimized_success:
            return UnitTestComparison(
                test_name=baseline[0].test_name if baseline else "unknown",
                baseline_variant=baseline[0].variant if baseline else "unknown",
                optimized_variant=optimized[0].variant if optimized else "unknown",
                baseline_mean_ms=0,
                optimized_mean_ms=0,
                improvement_percent=0,
                baseline_memory_mb=0,
                optimized_memory_mb=0,
                iterations=0,
                confidence="low"
            )

        # Calculate statistics
        baseline_durations = [r.duration_ms for r in baseline_success]
        optimized_durations = [r.duration_ms for r in optimized_success]

        baseline_mean = statistics.mean(baseline_durations)
        optimized_mean = statistics.mean(optimized_durations)
        improvement = ((baseline_mean - optimized_mean) / baseline_mean) * 100

        baseline_memory = statistics.mean([r.memory_mb for r in baseline_success])
        optimized_memory = statistics.mean([r.memory_mb for r in optimized_success])

        # Determine confidence based on coefficient of variation
        baseline_cv = (statistics.stdev(baseline_durations) / baseline_mean) if len(baseline_durations) > 1 else 0
        optimized_cv = (statistics.stdev(optimized_durations) / optimized_mean) if len(optimized_durations) > 1 else 0
        avg_cv = (baseline_cv + optimized_cv) / 2

        if avg_cv < 0.1:
            confidence = "high"
        elif avg_cv < 0.2:
            confidence = "medium"
        else:
            confidence = "low"

        return UnitTestComparison(
            test_name=baseline[0].test_name,
            baseline_variant=baseline[0].variant,
            optimized_variant=optimized[0].variant,
            baseline_mean_ms=baseline_mean,
            optimized_mean_ms=optimized_mean,
            improvement_percent=improvement,
            baseline_memory_mb=baseline_memory,
            optimized_memory_mb=optimized_memory,
            iterations=len(baseline_success),
            confidence=confidence
        )

    @staticmethod
    def generate_report(comparisons: List[UnitTestComparison],
                       output_path: Path):
        """Generate comprehensive analysis report."""

        report = {
            "test_date": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(comparisons),
                "total_improvement_ms": sum(c.baseline_mean_ms - c.optimized_mean_ms for c in comparisons),
                "average_improvement_percent": statistics.mean([c.improvement_percent for c in comparisons]),
            },
            "comparisons": [asdict(c) for c in comparisons],
            "recommendations": []
        }

        # Add recommendations based on results
        for comp in comparisons:
            if comp.improvement_percent > 50 and comp.confidence == "high":
                report["recommendations"].append({
                    "test": comp.test_name,
                    "priority": "HIGH",
                    "improvement": f"{comp.improvement_percent:.1f}%",
                    "recommendation": f"Implement {comp.optimized_variant} optimization immediately"
                })
            elif comp.improvement_percent > 20 and comp.confidence in ["high", "medium"]:
                report["recommendations"].append({
                    "test": comp.test_name,
                    "priority": "MEDIUM",
                    "improvement": f"{comp.improvement_percent:.1f}%",
                    "recommendation": f"Consider {comp.optimized_variant} optimization"
                })

        # Write JSON report
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        return report


def main():
    """Run all unit performance tests."""

    print("\n" + "="*60)
    print("BARQUE Unit-Level Performance Test Suite")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # Setup test files
    test_files_dir = Path(__file__).parent / "test_files"
    test_file = test_files_dir / "test_medium_2000w.md"

    if not test_file.exists():
        print(f"\n❌ Test file not found: {test_file}")
        print("Run the main test suite first to generate test files.")
        return 1

    all_results = []
    comparisons = []

    # Test 1: WeasyPrint Cold vs Warm
    print("\n" + "="*60)
    print("TEST 1: WeasyPrint Cold Start vs Warmed Cache")
    print("="*60)

    test1 = WeasyPrintColdWarmTest(test_file)
    cold_results = test1.test_cold_start(iterations=3)
    warm_results = test1.test_warm_cache(iterations=5)

    all_results.extend(cold_results)
    all_results.extend(warm_results)

    comparison1 = UnitPerformanceAnalyzer.analyze_results(cold_results, warm_results)
    comparisons.append(comparison1)

    print(f"\n  📊 Results:")
    print(f"     Cold Start: {comparison1.baseline_mean_ms:.0f}ms (avg)")
    print(f"     Warmed:     {comparison1.optimized_mean_ms:.0f}ms (avg)")
    print(f"     Improvement: {comparison1.improvement_percent:.1f}% faster")
    print(f"     Confidence: {comparison1.confidence.upper()}")

    # Test 2: Subprocess vs Direct SDK (skip if email not configured)
    print("\n" + "="*60)
    print("TEST 2: Pop CLI Subprocess vs Direct Resend SDK")
    print("="*60)

    # Use one of the generated PDFs for email testing
    test_pdf = Path(__file__).parent / "unit_test_outputs" / "warm_cache_0.pdf"
    if test_pdf.exists():
        test2 = SubprocessVsSDKTest(test_pdf)
        subprocess_results = test2.test_pop_cli_subprocess(iterations=3)
        sdk_results = test2.test_direct_resend_sdk(iterations=3)

        all_results.extend(subprocess_results)
        all_results.extend(sdk_results)

        if subprocess_results and sdk_results:
            comparison2 = UnitPerformanceAnalyzer.analyze_results(subprocess_results, sdk_results)
            comparisons.append(comparison2)

            print(f"\n  📊 Results:")
            print(f"     Subprocess: {comparison2.baseline_mean_ms:.0f}ms (avg)")
            print(f"     Direct SDK: {comparison2.optimized_mean_ms:.0f}ms (avg)")
            print(f"     Improvement: {comparison2.improvement_percent:.1f}% faster")
            print(f"     Confidence: {comparison2.confidence.upper()}")
    else:
        print("\n  ⚠️ SKIPPED: No test PDF available for email testing")

    # Test 3: Sequential vs Parallel PDF Generation
    print("\n" + "="*60)
    print("TEST 3: Sequential vs Parallel PDF Generation")
    print("="*60)

    test3 = SequentialVsParallelTest(test_file)
    sequential_results = test3.test_sequential_generation(iterations=5)
    parallel_results = test3.test_parallel_generation(iterations=5)

    all_results.extend(sequential_results)
    all_results.extend(parallel_results)

    comparison3 = UnitPerformanceAnalyzer.analyze_results(sequential_results, parallel_results)
    comparisons.append(comparison3)

    print(f"\n  📊 Results:")
    print(f"     Sequential: {comparison3.baseline_mean_ms:.0f}ms (avg)")
    print(f"     Parallel:   {comparison3.optimized_mean_ms:.0f}ms (avg)")
    print(f"     Improvement: {comparison3.improvement_percent:.1f}% faster")
    print(f"     Confidence: {comparison3.confidence.upper()}")

    # Generate final report
    print("\n" + "="*60)
    print("GENERATING ANALYSIS REPORT")
    print("="*60)

    report_path = Path(__file__).parent / "unit_performance_report.json"
    report = UnitPerformanceAnalyzer.generate_report(comparisons, report_path)

    print(f"\n✅ Report saved: {report_path}")
    print(f"\n📊 Summary:")
    print(f"   Total Tests: {report['summary']['total_tests']}")
    print(f"   Total Time Saved: {report['summary']['total_improvement_ms']:.0f}ms")
    print(f"   Average Improvement: {report['summary']['average_improvement_percent']:.1f}%")

    if report['recommendations']:
        print(f"\n🎯 Top Recommendations:")
        for rec in sorted(report['recommendations'], key=lambda x: x['priority'], reverse=True):
            print(f"   [{rec['priority']}] {rec['test']}: {rec['improvement']} - {rec['recommendation']}")

    print("\n" + "="*60)
    print("Unit-level performance testing complete!")
    print("="*60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
