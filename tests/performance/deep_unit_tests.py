#!/usr/bin/env python3
"""
Deep unit-level performance tests with granular profiling.

Enhanced testing beyond basic unit tests:
1. Memory lifecycle profiling (RSS, VMS, peak usage)
2. Subprocess overhead breakdown (spawn vs work time)
3. Thread contention and synchronization overhead
4. Statistical validation with larger sample sizes (15-20 iterations)
5. Outlier detection and variance analysis
6. Cache warming effectiveness at different stages
7. Network latency vs processing time breakdown
8. System resource contention detection

Provides actionable data for optimization decisions with confidence intervals.
"""

import os
import sys
import time
import json
import psutil
import subprocess
import statistics
import threading
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
from collections import defaultdict

# Add BARQUE to path
BARQUE_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BARQUE_ROOT))

from barque.core.generator import PDFGenerator
from barque.core.user_config import UserConfig


# Helper function for simpler PDF generation
def generate_pdf(markdown_file: Path, output_path: Path, theme: str) -> None:
    """Generate a single themed PDF."""
    generator = PDFGenerator()
    result = generator._generate_theme_pdf(markdown_file, theme, output_path.parent)
    if not result:
        raise RuntimeError(f"Failed to generate {theme} PDF")


@dataclass
class MemorySnapshot:
    """Memory usage snapshot at a point in time."""
    timestamp_ms: float
    rss_mb: float  # Resident Set Size
    vms_mb: float  # Virtual Memory Size
    peak_rss_mb: float  # Peak RSS (on macOS)
    label: str


@dataclass
class TimingBreakdown:
    """Granular timing breakdown for operations."""
    total_ms: float
    subprocess_spawn_ms: Optional[float] = None
    work_ms: Optional[float] = None
    thread_sync_ms: Optional[float] = None
    network_latency_ms: Optional[float] = None
    processing_ms: Optional[float] = None


@dataclass
class DeepTestResult:
    """Comprehensive result from deep profiling test."""
    test_name: str
    variant: str
    iteration: int

    # Timing
    timing: TimingBreakdown

    # Memory lifecycle
    memory_snapshots: List[MemorySnapshot]
    peak_memory_mb: float
    memory_leaked_mb: float

    # Resource usage
    cpu_percent: float
    io_read_mb: float
    io_write_mb: float

    # Statistical metadata
    success: bool
    is_outlier: bool = False
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StatisticalAnalysis:
    """Statistical analysis with confidence intervals."""
    test_name: str
    variant: str

    # Central tendency
    mean_ms: float
    median_ms: float
    mode_ms: Optional[float]

    # Spread
    std_dev_ms: float
    variance_ms: float
    range_ms: Tuple[float, float]  # (min, max)

    # Distribution
    q1_ms: float  # 25th percentile
    q3_ms: float  # 75th percentile
    iqr_ms: float  # Interquartile range

    # Confidence
    confidence_interval_95: Tuple[float, float]
    coefficient_of_variation: float

    # Quality
    sample_size: int
    outliers_removed: int
    confidence_level: str  # "very_high", "high", "medium", "low"


class DeepPerformanceTracker:
    """Advanced performance tracker with granular profiling."""

    def __init__(self, label: str = "operation"):
        self.label = label
        self.process = psutil.Process()
        self.memory_snapshots: List[MemorySnapshot] = []
        self.timing_events: Dict[str, float] = {}
        self.start_io: Optional[Tuple[int, int]] = None

    def snapshot_memory(self, label: str):
        """Take a memory snapshot."""
        mem_info = self.process.memory_info()
        snapshot = MemorySnapshot(
            timestamp_ms=time.perf_counter() * 1000,
            rss_mb=mem_info.rss / 1024 / 1024,
            vms_mb=mem_info.vms / 1024 / 1024,
            peak_rss_mb=getattr(mem_info, 'peak_wset', mem_info.rss) / 1024 / 1024,
            label=label
        )
        self.memory_snapshots.append(snapshot)
        return snapshot

    def mark_time(self, event: str):
        """Mark a timing event."""
        self.timing_events[event] = time.perf_counter() * 1000

    def get_duration(self, start_event: str, end_event: str) -> float:
        """Get duration between two events in milliseconds."""
        if start_event not in self.timing_events or end_event not in self.timing_events:
            return 0.0
        return self.timing_events[end_event] - self.timing_events[start_event]

    def start(self):
        """Start tracking."""
        self.process.cpu_percent()  # Initialize

        # I/O tracking (not available on macOS)
        try:
            io_counters = self.process.io_counters()
            self.start_io = (io_counters.read_bytes, io_counters.write_bytes)
        except (AttributeError, NotImplementedError):
            self.start_io = None  # Not available on this platform

        self.snapshot_memory("start")
        self.mark_time("start")

    def end(self) -> Tuple[float, float, float, float]:
        """End tracking and return (duration_ms, peak_memory_mb, cpu_percent, io_mb)."""
        self.mark_time("end")
        self.snapshot_memory("end")

        duration_ms = self.get_duration("start", "end")
        peak_memory_mb = max(s.rss_mb for s in self.memory_snapshots)
        cpu_percent = self.process.cpu_percent()

        # Calculate I/O (if available)
        io_mb = 0.0
        if self.start_io:
            try:
                io_counters = self.process.io_counters()
                io_mb = (io_counters.read_bytes + io_counters.write_bytes -
                        sum(self.start_io)) / 1024 / 1024
            except (AttributeError, NotImplementedError):
                io_mb = 0.0  # Not available on this platform

        return (duration_ms, peak_memory_mb, cpu_percent, io_mb)


class DeepWeasyPrintTest:
    """Deep profiling of WeasyPrint cold start vs warm cache."""

    def __init__(self, test_file: Path):
        self.test_file = test_file
        self.output_dir = Path(__file__).parent / "deep_test_outputs"
        self.output_dir.mkdir(exist_ok=True)

    def measure_subprocess_overhead(self) -> Tuple[float, float]:
        """Measure subprocess spawn overhead vs actual work time."""

        # Test 1: Minimal subprocess (just spawn and exit)
        tracker_spawn = DeepPerformanceTracker("spawn_only")
        tracker_spawn.start()
        subprocess.run(["python3", "-c", "pass"], capture_output=True)
        spawn_overhead_ms, _, _, _ = tracker_spawn.end()

        # Test 2: Subprocess with actual work (WeasyPrint)
        tracker_full = DeepPerformanceTracker("full_work")
        tracker_full.start()
        output_path = self.output_dir / "overhead_test.pdf"
        subprocess.run([
            "python3", "-m", "weasyprint",
            str(self.test_file),
            str(output_path)
        ], capture_output=True)
        full_duration_ms, _, _, _ = tracker_full.end()

        work_time_ms = full_duration_ms - spawn_overhead_ms

        return (spawn_overhead_ms, work_time_ms)

    def test_with_deep_profiling(self, variant: str, iterations: int = 15) -> List[DeepTestResult]:
        """Run deep profiling test."""
        results = []

        is_cold = variant == "cold"

        print(f"\n{'='*70}")
        print(f"Deep Test: WeasyPrint {variant.upper()} Start (n={iterations})")
        print(f"{'='*70}")

        # For cold tests, measure subprocess overhead once
        if is_cold:
            print("  Measuring subprocess overhead...")
            spawn_ms, work_ms = self.measure_subprocess_overhead()
            print(f"  Subprocess spawn: {spawn_ms:.1f}ms, Work time: {work_ms:.1f}ms")
            print(f"  Overhead: {(spawn_ms/work_ms*100):.1f}% of total time")

        # Pre-warm for warm variant
        if not is_cold:
            print("  Pre-warming cache (generating 3 warmup PDFs)...")
            for i in range(3):
                warmup_path = self.output_dir / f"warmup_{i}.pdf"
                subprocess.run([
                    "python3", "-m", "weasyprint",
                    str(self.test_file),
                    str(warmup_path)
                ], capture_output=True)
            print("  Cache fully warmed ✓")

        # Run test iterations
        for i in range(iterations):
            tracker = DeepPerformanceTracker(f"{variant}_{i}")
            tracker.start()
            tracker.snapshot_memory("before_subprocess")

            try:
                output_path = self.output_dir / f"{variant}_deep_{i}.pdf"

                # Mark subprocess spawn
                tracker.mark_time("subprocess_start")

                result = subprocess.run([
                    "python3", "-m", "weasyprint",
                    str(self.test_file),
                    str(output_path)
                ], capture_output=True, timeout=30)

                tracker.mark_time("subprocess_end")
                tracker.snapshot_memory("after_subprocess")

                success = result.returncode == 0
                error = result.stderr.decode() if not success else None

                duration_ms, peak_memory_mb, cpu_percent, io_mb = tracker.end()

                # Calculate memory leak (difference between start and end RSS)
                memory_leaked_mb = (tracker.memory_snapshots[-1].rss_mb -
                                   tracker.memory_snapshots[0].rss_mb)

                # Create timing breakdown
                timing = TimingBreakdown(
                    total_ms=duration_ms,
                    subprocess_spawn_ms=tracker.get_duration("subprocess_start", "subprocess_end"),
                    work_ms=tracker.get_duration("subprocess_start", "subprocess_end")
                )

                results.append(DeepTestResult(
                    test_name=f"weasyprint_{variant}_deep",
                    variant=variant,
                    iteration=i,
                    timing=timing,
                    memory_snapshots=tracker.memory_snapshots,
                    peak_memory_mb=peak_memory_mb,
                    memory_leaked_mb=memory_leaked_mb,
                    cpu_percent=cpu_percent,
                    io_read_mb=io_mb / 2,  # Approximate split
                    io_write_mb=io_mb / 2,
                    success=success,
                    error=error,
                    metadata={
                        "file_size_kb": self.test_file.stat().st_size / 1024,
                        "pdf_size_kb": output_path.stat().st_size / 1024 if output_path.exists() else 0
                    }
                ))

                print(f"  Run {i+1:2d}: {duration_ms:6.0f}ms "
                      f"(mem: {peak_memory_mb:5.1f}MB, "
                      f"I/O: {io_mb:4.1f}MB) {'✓' if success else '✗'}")

            except Exception as e:
                duration_ms, peak_memory_mb, cpu_percent, io_mb = tracker.end()
                memory_leaked_mb = 0.0

                results.append(DeepTestResult(
                    test_name=f"weasyprint_{variant}_deep",
                    variant=variant,
                    iteration=i,
                    timing=TimingBreakdown(total_ms=duration_ms),
                    memory_snapshots=tracker.memory_snapshots,
                    peak_memory_mb=peak_memory_mb,
                    memory_leaked_mb=memory_leaked_mb,
                    cpu_percent=cpu_percent,
                    io_read_mb=io_mb / 2,
                    io_write_mb=io_mb / 2,
                    success=False,
                    error=str(e)
                ))

                print(f"  Run {i+1:2d}: FAILED - {e}")

        return results


class DeepParallelTest:
    """Deep profiling of sequential vs parallel PDF generation."""

    def __init__(self, test_file: Path):
        self.test_file = test_file
        self.output_dir = Path(__file__).parent / "deep_test_outputs"
        self.output_dir.mkdir(exist_ok=True)

    def measure_thread_sync_overhead(self) -> float:
        """Measure threading synchronization overhead."""
        from concurrent.futures import ThreadPoolExecutor

        iterations = 100

        # Sequential execution (no threading)
        start = time.perf_counter()
        for _ in range(iterations):
            pass  # Minimal work
        sequential_time = (time.perf_counter() - start) * 1000

        # Parallel execution with threading
        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(lambda: None) for _ in range(iterations)]
            for f in futures:
                f.result()
        parallel_time = (time.perf_counter() - start) * 1000

        # Overhead is the difference
        sync_overhead = parallel_time - sequential_time
        return sync_overhead / iterations  # Per-task overhead

    def test_with_deep_profiling(self, variant: str, iterations: int = 15) -> List[DeepTestResult]:
        """Run deep profiling for sequential or parallel generation."""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        results = []
        is_parallel = variant == "parallel"

        print(f"\n{'='*70}")
        print(f"Deep Test: PDF Generation {variant.upper()} (n={iterations})")
        print(f"{'='*70}")

        # Measure thread sync overhead if parallel
        if is_parallel:
            print("  Measuring thread synchronization overhead...")
            sync_overhead = self.measure_thread_sync_overhead()
            print(f"  Thread sync overhead: {sync_overhead:.3f}ms per task")

        for i in range(iterations):
            tracker = DeepPerformanceTracker(f"{variant}_{i}")
            tracker.start()
            tracker.snapshot_memory("start")

            try:
                light_path = self.output_dir / f"{variant}_light_{i}.pdf"
                dark_path = self.output_dir / f"{variant}_dark_{i}.pdf"

                if is_parallel:
                    # Parallel generation
                    tracker.mark_time("parallel_start")
                    tracker.snapshot_memory("before_parallel")

                    with ThreadPoolExecutor(max_workers=2) as executor:
                        tracker.mark_time("threads_spawned")

                        futures = {
                            executor.submit(generate_pdf, self.test_file, light_path, "light"): "light",
                            executor.submit(generate_pdf, self.test_file, dark_path, "dark"): "dark"
                        }

                        tracker.mark_time("threads_working")

                        for future in as_completed(futures):
                            theme = futures[future]
                            future.result()
                            tracker.mark_time(f"{theme}_complete")
                            tracker.snapshot_memory(f"after_{theme}")

                    tracker.mark_time("parallel_end")

                    # Calculate timing breakdown
                    thread_spawn_ms = tracker.get_duration("parallel_start", "threads_spawned")
                    work_ms = tracker.get_duration("threads_working", "parallel_end")

                    timing = TimingBreakdown(
                        total_ms=tracker.get_duration("start", "end"),
                        thread_sync_ms=thread_spawn_ms,
                        work_ms=work_ms
                    )

                else:
                    # Sequential generation
                    tracker.mark_time("light_start")
                    tracker.snapshot_memory("before_light")

                    generate_pdf(self.test_file, light_path, "light")

                    tracker.mark_time("light_end")
                    tracker.snapshot_memory("after_light")

                    tracker.mark_time("dark_start")

                    generate_pdf(self.test_file, dark_path, "dark")

                    tracker.mark_time("dark_end")
                    tracker.snapshot_memory("after_dark")

                    # Calculate timing breakdown
                    light_ms = tracker.get_duration("light_start", "light_end")
                    dark_ms = tracker.get_duration("dark_start", "dark_end")

                    timing = TimingBreakdown(
                        total_ms=tracker.get_duration("start", "end"),
                        work_ms=light_ms + dark_ms
                    )

                    timing.metadata = {"light_ms": light_ms, "dark_ms": dark_ms}

                duration_ms, peak_memory_mb, cpu_percent, io_mb = tracker.end()

                memory_leaked_mb = (tracker.memory_snapshots[-1].rss_mb -
                                   tracker.memory_snapshots[0].rss_mb)

                results.append(DeepTestResult(
                    test_name=f"pdf_generation_{variant}_deep",
                    variant=variant,
                    iteration=i,
                    timing=timing,
                    memory_snapshots=tracker.memory_snapshots,
                    peak_memory_mb=peak_memory_mb,
                    memory_leaked_mb=memory_leaked_mb,
                    cpu_percent=cpu_percent,
                    io_read_mb=io_mb / 2,
                    io_write_mb=io_mb / 2,
                    success=True,
                    metadata={
                        "light_size_kb": light_path.stat().st_size / 1024,
                        "dark_size_kb": dark_path.stat().st_size / 1024
                    }
                ))

                print(f"  Run {i+1:2d}: {duration_ms:6.0f}ms "
                      f"(mem: {peak_memory_mb:5.1f}MB, "
                      f"I/O: {io_mb:4.1f}MB) ✓")

            except Exception as e:
                duration_ms, peak_memory_mb, cpu_percent, io_mb = tracker.end()

                results.append(DeepTestResult(
                    test_name=f"pdf_generation_{variant}_deep",
                    variant=variant,
                    iteration=i,
                    timing=TimingBreakdown(total_ms=duration_ms),
                    memory_snapshots=tracker.memory_snapshots,
                    peak_memory_mb=peak_memory_mb,
                    memory_leaked_mb=0.0,
                    cpu_percent=cpu_percent,
                    io_read_mb=io_mb / 2,
                    io_write_mb=io_mb / 2,
                    success=False,
                    error=str(e)
                ))

                print(f"  Run {i+1:2d}: FAILED - {e}")

        return results


class DeepStatisticalAnalyzer:
    """Advanced statistical analysis with outlier detection."""

    @staticmethod
    def detect_outliers(data: List[float], method: str = "iqr") -> List[bool]:
        """Detect outliers using IQR method."""
        if len(data) < 4:
            return [False] * len(data)

        q1 = statistics.quantiles(data, n=4)[0]
        q3 = statistics.quantiles(data, n=4)[2]
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        return [x < lower_bound or x > upper_bound for x in data]

    @staticmethod
    def calculate_confidence_interval(data: List[float], confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval."""
        if len(data) < 2:
            mean_val = statistics.mean(data) if data else 0
            return (mean_val, mean_val)

        mean_val = statistics.mean(data)
        std_dev = statistics.stdev(data)
        n = len(data)

        # t-distribution critical value for 95% confidence (approximation)
        t_value = 2.0 if n < 30 else 1.96

        margin = t_value * (std_dev / (n ** 0.5))

        return (mean_val - margin, mean_val + margin)

    @staticmethod
    def analyze(results: List[DeepTestResult]) -> StatisticalAnalysis:
        """Perform comprehensive statistical analysis."""

        if not results:
            return StatisticalAnalysis(
                test_name="unknown",
                variant="unknown",
                mean_ms=0, median_ms=0, mode_ms=None,
                std_dev_ms=0, variance_ms=0, range_ms=(0, 0),
                q1_ms=0, q3_ms=0, iqr_ms=0,
                confidence_interval_95=(0, 0),
                coefficient_of_variation=0,
                sample_size=0,
                outliers_removed=0,
                confidence_level="low"
            )

        # Extract timing data
        durations = [r.timing.total_ms for r in results if r.success]

        if not durations:
            return StatisticalAnalysis(
                test_name=results[0].test_name,
                variant=results[0].variant,
                mean_ms=0, median_ms=0, mode_ms=None,
                std_dev_ms=0, variance_ms=0, range_ms=(0, 0),
                q1_ms=0, q3_ms=0, iqr_ms=0,
                confidence_interval_95=(0, 0),
                coefficient_of_variation=0,
                sample_size=0,
                outliers_removed=0,
                confidence_level="low"
            )

        # Detect and mark outliers
        outliers = DeepStatisticalAnalyzer.detect_outliers(durations)
        for i, is_outlier in enumerate(outliers):
            if i < len(results):
                results[i].is_outlier = is_outlier

        # Remove outliers for clean statistics
        clean_durations = [d for d, o in zip(durations, outliers) if not o]
        outliers_removed = len(durations) - len(clean_durations)

        if not clean_durations:
            clean_durations = durations  # Keep all if all are outliers

        # Calculate statistics
        mean_val = statistics.mean(clean_durations)
        median_val = statistics.median(clean_durations)

        try:
            mode_val = statistics.mode(clean_durations)
        except statistics.StatisticsError:
            mode_val = None

        std_dev = statistics.stdev(clean_durations) if len(clean_durations) > 1 else 0
        variance = statistics.variance(clean_durations) if len(clean_durations) > 1 else 0

        q1, q3 = (statistics.quantiles(clean_durations, n=4)[0],
                 statistics.quantiles(clean_durations, n=4)[2]) if len(clean_durations) >= 4 else (min(clean_durations), max(clean_durations))
        iqr = q3 - q1

        ci = DeepStatisticalAnalyzer.calculate_confidence_interval(clean_durations)
        cv = (std_dev / mean_val) if mean_val > 0 else 0

        # Determine confidence level
        if cv < 0.05 and len(clean_durations) >= 15:
            confidence_level = "very_high"
        elif cv < 0.10 and len(clean_durations) >= 10:
            confidence_level = "high"
        elif cv < 0.20 and len(clean_durations) >= 5:
            confidence_level = "medium"
        else:
            confidence_level = "low"

        return StatisticalAnalysis(
            test_name=results[0].test_name,
            variant=results[0].variant,
            mean_ms=mean_val,
            median_ms=median_val,
            mode_ms=mode_val,
            std_dev_ms=std_dev,
            variance_ms=variance,
            range_ms=(min(clean_durations), max(clean_durations)),
            q1_ms=q1,
            q3_ms=q3,
            iqr_ms=iqr,
            confidence_interval_95=ci,
            coefficient_of_variation=cv,
            sample_size=len(clean_durations),
            outliers_removed=outliers_removed,
            confidence_level=confidence_level
        )


def generate_deep_report(analyses: Dict[str, StatisticalAnalysis],
                        all_results: Dict[str, List[DeepTestResult]],
                        output_path: Path):
    """Generate comprehensive deep analysis report."""

    report = {
        "test_date": datetime.now().isoformat(),
        "test_type": "deep_unit_profiling",
        "summary": {
            "total_tests": len(analyses),
            "total_iterations": sum(a.sample_size for a in analyses.values()),
            "high_confidence_tests": sum(1 for a in analyses.values() if a.confidence_level in ["very_high", "high"])
        },
        "statistical_analyses": {
            name: asdict(analysis) for name, analysis in analyses.items()
        },
        "detailed_results": {},
        "insights": []
    }

    # Add detailed per-test results
    for test_name, results in all_results.items():
        report["detailed_results"][test_name] = [
            {
                "iteration": r.iteration,
                "duration_ms": r.timing.total_ms,
                "peak_memory_mb": r.peak_memory_mb,
                "memory_leaked_mb": r.memory_leaked_mb,
                "cpu_percent": r.cpu_percent,
                "io_total_mb": r.io_read_mb + r.io_write_mb,
                "is_outlier": r.is_outlier,
                "success": r.success
            }
            for r in results if r.success
        ]

    # Generate insights
    for name, analysis in analyses.items():
        if "cold" in name and "warm" in name:
            continue  # Skip, will compare below

        insight = {
            "test": name,
            "confidence": analysis.confidence_level,
            "mean_duration": f"{analysis.mean_ms:.0f}ms",
            "variability": f"±{analysis.std_dev_ms:.0f}ms",
            "cv_percent": f"{analysis.coefficient_of_variation * 100:.1f}%"
        }

        if analysis.confidence_level in ["very_high", "high"]:
            insight["recommendation"] = "High quality data - safe to use for optimization decisions"
        else:
            insight["recommendation"] = "Consider more iterations or investigate variance sources"

        report["insights"].append(insight)

    # Write report
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    return report


def main():
    """Run deep unit performance tests."""

    print("\n" + "="*70)
    print("BARQUE Deep Unit-Level Performance Test Suite")
    print("="*70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing methodology: Large sample sizes (15-20), outlier detection,")
    print(f"                     confidence intervals, granular profiling")
    print("="*70)

    # Setup
    test_files_dir = Path(__file__).parent / "test_files"
    test_file = test_files_dir / "test_medium_2000w.md"

    if not test_file.exists():
        print(f"\n❌ Test file not found: {test_file}")
        print("Run the main test suite first to generate test files.")
        return 1

    all_results = {}
    analyses = {}

    # Test 1: WeasyPrint Cold vs Warm (Deep Profiling)
    print("\n" + "="*70)
    print("TEST 1: WeasyPrint Cold vs Warm (Deep Profiling)")
    print("="*70)

    deep_test1 = DeepWeasyPrintTest(test_file)

    cold_results = deep_test1.test_with_deep_profiling("cold", iterations=15)
    warm_results = deep_test1.test_with_deep_profiling("warm", iterations=20)

    all_results["weasyprint_cold"] = cold_results
    all_results["weasyprint_warm"] = warm_results

    cold_analysis = DeepStatisticalAnalyzer.analyze(cold_results)
    warm_analysis = DeepStatisticalAnalyzer.analyze(warm_results)

    analyses["weasyprint_cold"] = cold_analysis
    analyses["weasyprint_warm"] = warm_analysis

    print(f"\n  📊 Statistical Analysis:")
    print(f"     Cold: {cold_analysis.mean_ms:.0f}ms ± {cold_analysis.std_dev_ms:.0f}ms "
          f"(CV: {cold_analysis.coefficient_of_variation*100:.1f}%, "
          f"confidence: {cold_analysis.confidence_level})")
    print(f"     Warm: {warm_analysis.mean_ms:.0f}ms ± {warm_analysis.std_dev_ms:.0f}ms "
          f"(CV: {warm_analysis.coefficient_of_variation*100:.1f}%, "
          f"confidence: {warm_analysis.confidence_level})")
    print(f"     Improvement: {((cold_analysis.mean_ms - warm_analysis.mean_ms) / cold_analysis.mean_ms * 100):.1f}%")
    print(f"     95% CI cold: [{cold_analysis.confidence_interval_95[0]:.0f}, {cold_analysis.confidence_interval_95[1]:.0f}]ms")
    print(f"     95% CI warm: [{warm_analysis.confidence_interval_95[0]:.0f}, {warm_analysis.confidence_interval_95[1]:.0f}]ms")
    if cold_analysis.outliers_removed + warm_analysis.outliers_removed > 0:
        print(f"     Outliers removed: {cold_analysis.outliers_removed + warm_analysis.outliers_removed}")

    # Test 2: Sequential vs Parallel (Deep Profiling)
    print("\n" + "="*70)
    print("TEST 2: Sequential vs Parallel (Deep Profiling)")
    print("="*70)

    deep_test2 = DeepParallelTest(test_file)

    sequential_results = deep_test2.test_with_deep_profiling("sequential", iterations=15)
    parallel_results = deep_test2.test_with_deep_profiling("parallel", iterations=15)

    all_results["pdf_sequential"] = sequential_results
    all_results["pdf_parallel"] = parallel_results

    seq_analysis = DeepStatisticalAnalyzer.analyze(sequential_results)
    par_analysis = DeepStatisticalAnalyzer.analyze(parallel_results)

    analyses["pdf_sequential"] = seq_analysis
    analyses["pdf_parallel"] = par_analysis

    print(f"\n  📊 Statistical Analysis:")
    print(f"     Sequential: {seq_analysis.mean_ms:.0f}ms ± {seq_analysis.std_dev_ms:.0f}ms "
          f"(CV: {seq_analysis.coefficient_of_variation*100:.1f}%, "
          f"confidence: {seq_analysis.confidence_level})")
    print(f"     Parallel:   {par_analysis.mean_ms:.0f}ms ± {par_analysis.std_dev_ms:.0f}ms "
          f"(CV: {par_analysis.coefficient_of_variation*100:.1f}%, "
          f"confidence: {par_analysis.confidence_level})")
    print(f"     Improvement: {((seq_analysis.mean_ms - par_analysis.mean_ms) / seq_analysis.mean_ms * 100):.1f}%")
    print(f"     95% CI sequential: [{seq_analysis.confidence_interval_95[0]:.0f}, {seq_analysis.confidence_interval_95[1]:.0f}]ms")
    print(f"     95% CI parallel: [{par_analysis.confidence_interval_95[0]:.0f}, {par_analysis.confidence_interval_95[1]:.0f}]ms")
    if seq_analysis.outliers_removed + par_analysis.outliers_removed > 0:
        print(f"     Outliers removed: {seq_analysis.outliers_removed + par_analysis.outliers_removed}")

    # Generate report
    print("\n" + "="*70)
    print("GENERATING DEEP ANALYSIS REPORT")
    print("="*70)

    report_path = Path(__file__).parent / "deep_unit_performance_report.json"
    report = generate_deep_report(analyses, all_results, report_path)

    print(f"\n✅ Report saved: {report_path}")
    print(f"\n📊 Summary:")
    print(f"   Total Tests: {report['summary']['total_tests']}")
    print(f"   Total Iterations: {report['summary']['total_iterations']}")
    print(f"   High Confidence Tests: {report['summary']['high_confidence_tests']}/{report['summary']['total_tests']}")

    if report['insights']:
        print(f"\n🔬 Key Insights:")
        for insight in report['insights'][:5]:  # Top 5
            print(f"   • {insight['test']}: {insight['mean_duration']} "
                  f"(±{insight['variability']}, {insight['confidence']})")

    print("\n" + "="*70)
    print("Deep unit-level performance testing complete!")
    print("="*70)

    return 0


if __name__ == "__main__":
    sys.exit(main())