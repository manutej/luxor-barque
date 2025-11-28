#!/usr/bin/env python3
"""
BARQUE Performance Test Suite

Comprehensive performance testing for PDF generation and email delivery.
Tracks timing, memory usage, and identifies bottlenecks.
"""

import time
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json
import psutil
import subprocess

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from barque.core.generator import PDFGenerator
from barque.core.config import BarqueConfig
from barque.core.email import EmailSender, EmailConfig, EmailProvider, EmailMessage
from barque.core.user_config import UserConfig


@dataclass
class PerformanceMetric:
    """Performance measurement result"""
    operation: str
    duration_seconds: float
    memory_mb: float
    cpu_percent: float
    success: bool
    error: Optional[str] = None
    metadata: Optional[Dict] = None


@dataclass
class TestResult:
    """Complete test result with metrics"""
    test_name: str
    total_duration: float
    metrics: List[PerformanceMetric]
    success: bool
    timestamp: str


class PerformanceTracker:
    """Track performance metrics during operations"""

    def __init__(self):
        self.process = psutil.Process()
        self.start_time = None
        self.start_memory = None
        self.start_cpu = None

    def start(self):
        """Begin tracking"""
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.start_cpu = self.process.cpu_percent()

    def end(self) -> Tuple[float, float, float]:
        """End tracking and return metrics"""
        duration = time.time() - self.start_time
        memory = self.process.memory_info().rss / 1024 / 1024  # MB
        cpu = self.process.cpu_percent()

        return (
            duration,
            memory - self.start_memory,
            cpu
        )


class PerformanceTestSuite:
    """Complete performance testing suite"""

    def __init__(self, test_files_dir: Path):
        self.test_files_dir = test_files_dir
        self.results: List[TestResult] = []
        self.output_dir = Path("test_output")
        self.output_dir.mkdir(exist_ok=True)

    def create_test_file(self, size: str, word_count: int) -> Path:
        """Create test markdown file of specified size"""
        filename = f"test_{size}_{word_count}w.md"
        filepath = self.test_files_dir / filename

        # Generate content
        content = f"# Performance Test Document - {size.upper()}\n\n"
        content += f"**Word Count Target**: {word_count:,}\n\n"

        # Add sections with lorem ipsum
        words = ["Lorem", "ipsum", "dolor", "sit", "amet", "consectetur",
                 "adipiscing", "elit", "sed", "do", "eiusmod", "tempor"]

        current_words = len(content.split())
        section = 1

        while current_words < word_count:
            content += f"## Section {section}\n\n"

            # Add paragraph
            paragraph = " ".join(words * 50)  # ~600 words per paragraph
            content += paragraph + "\n\n"

            # Add code block occasionally
            if section % 3 == 0:
                content += "```python\n"
                content += "def example_function():\n"
                content += "    return 'performance test'\n"
                content += "```\n\n"

            # Add table occasionally
            if section % 5 == 0:
                content += "| Column 1 | Column 2 | Column 3 |\n"
                content += "|----------|----------|----------|\n"
                content += "| Data 1   | Data 2   | Data 3   |\n\n"

            current_words = len(content.split())
            section += 1

        filepath.write_text(content)
        return filepath

    def test_pdf_generation(self, file_path: Path, theme: str) -> PerformanceMetric:
        """Test PDF generation performance"""
        tracker = PerformanceTracker()

        try:
            config = BarqueConfig.load()
            config.output_dir = self.output_dir
            generator = PDFGenerator(config)

            tracker.start()
            result = generator.generate(input_file=file_path, theme=theme)
            duration, memory, cpu = tracker.end()

            return PerformanceMetric(
                operation=f"pdf_generation_{theme}",
                duration_seconds=duration,
                memory_mb=memory,
                cpu_percent=cpu,
                success=result.success,
                error=result.error if not result.success else None,
                metadata={
                    "file_size_kb": file_path.stat().st_size / 1024,
                    "word_count": len(file_path.read_text().split()),
                    "output_files": result.files if result.success else []
                }
            )

        except Exception as e:
            duration, memory, cpu = tracker.end()
            return PerformanceMetric(
                operation=f"pdf_generation_{theme}",
                duration_seconds=duration,
                memory_mb=memory,
                cpu_percent=cpu,
                success=False,
                error=str(e)
            )

    def test_email_delivery(self, pdf_files: List[Path]) -> PerformanceMetric:
        """Test email delivery performance"""
        tracker = PerformanceTracker()

        try:
            # Load user config
            user_config = UserConfig.load()

            config = EmailConfig(
                provider=EmailProvider.RESEND,
                from_email=user_config.default_from_email,
                resend_api_key=user_config.resend_api_key
            )

            sender = EmailSender(config)

            message = EmailMessage(
                to=[user_config.default_to_email or "test@example.com"],
                subject="BARQUE Performance Test",
                body="Performance test email with PDF attachments",
                attachments=pdf_files
            )

            tracker.start()
            result = sender.send(message)
            duration, memory, cpu = tracker.end()

            total_size_mb = sum(f.stat().st_size for f in pdf_files) / 1024 / 1024

            return PerformanceMetric(
                operation="email_delivery",
                duration_seconds=duration,
                memory_mb=memory,
                cpu_percent=cpu,
                success=result.success,
                error=result.error if not result.success else None,
                metadata={
                    "attachment_count": len(pdf_files),
                    "total_size_mb": round(total_size_mb, 2),
                    "recipients": result.recipients
                }
            )

        except Exception as e:
            duration, memory, cpu = tracker.end()
            return PerformanceMetric(
                operation="email_delivery",
                duration_seconds=duration,
                memory_mb=memory,
                cpu_percent=cpu,
                success=False,
                error=str(e)
            )

    def test_end_to_end(self, file_path: Path) -> TestResult:
        """Test complete workflow: generate PDFs + send email"""
        test_start = time.time()
        metrics = []

        # Test PDF generation (both themes)
        light_metric = self.test_pdf_generation(file_path, "light")
        metrics.append(light_metric)

        dark_metric = self.test_pdf_generation(file_path, "dark")
        metrics.append(dark_metric)

        # Collect PDF files
        pdf_files = []
        if light_metric.success and light_metric.metadata:
            pdf_files.extend([Path(f) for f in light_metric.metadata["output_files"]])
        if dark_metric.success and dark_metric.metadata:
            pdf_files.extend([Path(f) for f in dark_metric.metadata["output_files"]])

        # Test email delivery
        if pdf_files:
            email_metric = self.test_email_delivery(pdf_files)
            metrics.append(email_metric)

        total_duration = time.time() - test_start
        success = all(m.success for m in metrics)

        return TestResult(
            test_name=f"end_to_end_{file_path.stem}",
            total_duration=total_duration,
            metrics=metrics,
            success=success,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )

    def test_shell_wrapper(self, file_path: Path) -> PerformanceMetric:
        """Test shell wrapper performance"""
        tracker = PerformanceTracker()

        script_path = Path(__file__).parent.parent.parent / "scripts" / "barque-send"

        if not script_path.exists():
            return PerformanceMetric(
                operation="shell_wrapper",
                duration_seconds=0,
                memory_mb=0,
                cpu_percent=0,
                success=False,
                error="Shell wrapper not found"
            )

        try:
            tracker.start()
            result = subprocess.run(
                [str(script_path), str(file_path), "--quiet"],
                capture_output=True,
                text=True,
                timeout=60
            )
            duration, memory, cpu = tracker.end()

            return PerformanceMetric(
                operation="shell_wrapper",
                duration_seconds=duration,
                memory_mb=memory,
                cpu_percent=cpu,
                success=result.returncode == 0,
                error=result.stderr if result.returncode != 0 else None
            )

        except Exception as e:
            duration, memory, cpu = tracker.end()
            return PerformanceMetric(
                operation="shell_wrapper",
                duration_seconds=duration,
                memory_mb=memory,
                cpu_percent=cpu,
                success=False,
                error=str(e)
            )

    def run_battery_tests(self) -> List[TestResult]:
        """Run complete battery of tests"""
        print("=" * 60)
        print("BARQUE Performance Test Suite")
        print("=" * 60)
        print()

        # Create test files of various sizes
        test_configs = [
            ("small", 500),
            ("medium", 2000),
            ("large", 5000),
            ("xlarge", 10000)
        ]

        for size, word_count in test_configs:
            print(f"Running tests for {size} file ({word_count:,} words)...")

            # Create test file
            file_path = self.create_test_file(size, word_count)
            print(f"  Created: {file_path}")

            # Run end-to-end test
            result = self.test_end_to_end(file_path)
            self.results.append(result)

            # Print results
            print(f"  Total time: {result.total_duration:.2f}s")
            for metric in result.metrics:
                status = "✓" if metric.success else "✗"
                print(f"    {status} {metric.operation}: {metric.duration_seconds:.2f}s")
            print()

        return self.results

    def generate_report(self) -> Dict:
        """Generate comprehensive performance report"""
        report = {
            "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": len(self.results),
            "successful_tests": sum(1 for r in self.results if r.success),
            "results": []
        }

        for result in self.results:
            result_data = {
                "test_name": result.test_name,
                "total_duration": round(result.total_duration, 2),
                "success": result.success,
                "timestamp": result.timestamp,
                "metrics": []
            }

            for metric in result.metrics:
                metric_data = {
                    "operation": metric.operation,
                    "duration_seconds": round(metric.duration_seconds, 2),
                    "memory_mb": round(metric.memory_mb, 2),
                    "cpu_percent": round(metric.cpu_percent, 2),
                    "success": metric.success,
                    "error": metric.error,
                    "metadata": metric.metadata
                }
                result_data["metrics"].append(metric_data)

            report["results"].append(result_data)

        return report

    def save_report(self, output_file: Path):
        """Save performance report to file"""
        report = self.generate_report()

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Report saved to: {output_file}")

    def print_summary(self):
        """Print test summary"""
        print()
        print("=" * 60)
        print("PERFORMANCE TEST SUMMARY")
        print("=" * 60)
        print()

        report = self.generate_report()

        print(f"Total Tests: {report['total_tests']}")
        print(f"Successful: {report['successful_tests']}")
        print(f"Failed: {report['total_tests'] - report['successful_tests']}")
        print()

        # Calculate averages by operation
        operation_times = {}
        for result in report["results"]:
            for metric in result["metrics"]:
                op = metric["operation"]
                if op not in operation_times:
                    operation_times[op] = []
                if metric["success"]:
                    operation_times[op].append(metric["duration_seconds"])

        print("Average Timings by Operation:")
        print("-" * 60)
        for op, times in sorted(operation_times.items()):
            if times:
                avg = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)
                print(f"  {op:30s} {avg:6.2f}s (min: {min_time:.2f}s, max: {max_time:.2f}s)")
        print()


def main():
    """Run performance tests"""
    # Setup
    test_dir = Path(__file__).parent / "test_files"
    test_dir.mkdir(exist_ok=True)

    # Create test suite
    suite = PerformanceTestSuite(test_dir)

    # Run tests
    suite.run_battery_tests()

    # Generate report
    report_file = Path(__file__).parent / "performance_report.json"
    suite.save_report(report_file)

    # Print summary
    suite.print_summary()


if __name__ == "__main__":
    main()
