"""
Unit Test Suite for Module 5: Performance Analysis & Reporting Subsystem.
Verifies benchmarking drivers, dataset loaders across 4 tiers, CSV exports,
Pandas structured comparison tables, 300 DPI chart generation, and error robustness.
"""

from pathlib import Path
import os
import sys
import unittest

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modules.reporting import (
    load_cpu_dataset,
    load_memory_dataset,
    load_disk_dataset,
    load_deadlock_dataset,
    benchmark_cpu,
    benchmark_memory,
    benchmark_disk,
    analyze_deadlock,
    generate_overall_dashboard,
    benchmark_all_workloads,
    run_all_benchmarks,
    RESULTS_DIR,
    CHARTS_DIR,
    ANALYSIS_RESULTS_DIR,
    ANALYSIS_CHARTS_DIR,
)


class TestReportingSubsystem(unittest.TestCase):
    def test_dataset_loaders(self):
        """Verify dataset loaders properly load all 4 workload tiers."""
        tiers = ["normal", "small", "large", "edge"]
        for tier in tiers:
            # CPU
            procs = load_cpu_dataset(tier)
            self.assertGreater(len(procs), 0)
            self.assertTrue(all(hasattr(p, "pid") for p in procs))

            # Memory
            blocks, reqs = load_memory_dataset(tier)
            self.assertGreater(len(blocks), 0)
            self.assertGreater(len(reqs), 0)

            # Disk
            cyls = load_disk_dataset(tier)
            self.assertGreater(len(cyls), 0)

            # Deadlock
            state, req_tuple = load_deadlock_dataset(tier)
            self.assertGreater(len(state.process_ids), 0)
            self.assertGreater(len(state.resource_ids), 0)
            self.assertEqual(len(state.available), len(state.resource_ids))
            self.assertEqual(len(req_tuple[1]), len(state.resource_ids))

    def test_benchmark_cpu(self):
        """Verify CPU benchmarking runs all 4 algorithms and produces valid metrics, CSV, and PNG."""
        res = benchmark_cpu()
        self.assertEqual(len(res), 4)
        algos = [r["algorithm"] for r in res]
        self.assertIn("FCFS", algos)
        self.assertIn("SJF", algos)
        self.assertIn("Round Robin (q=2)", algos)
        self.assertIn("Priority", algos)

        for r in res:
            self.assertIn("avg_waiting_time", r)
            self.assertIn("avg_turnaround_time", r)
            self.assertIn("avg_response_time", r)
            self.assertIn("cpu_utilization", r)
            self.assertGreaterEqual(r["cpu_utilization"], 0.0)

        for dest_dir in (RESULTS_DIR, ANALYSIS_RESULTS_DIR):
            csv_path = dest_dir / "cpu_results.csv"
            self.assertTrue(csv_path.exists())
            self.assertGreater(csv_path.stat().st_size, 0)

        for chart_dir in (CHARTS_DIR, ANALYSIS_CHARTS_DIR):
            chart_path = chart_dir / "cpu_comparison.png"
            self.assertTrue(chart_path.exists())
            self.assertGreater(chart_path.stat().st_size, 1000)

    def test_benchmark_memory(self):
        """Verify Memory benchmarking runs all 3 algorithms and produces valid metrics, CSV, and PNG."""
        res = benchmark_memory()
        self.assertEqual(len(res), 3)
        algos = [r["algorithm"] for r in res]
        self.assertIn("First Fit", algos)
        self.assertIn("Best Fit", algos)
        self.assertIn("Worst Fit", algos)

        for r in res:
            self.assertIn("successful_allocations", r)
            self.assertIn("failed_allocations", r)
            self.assertIn("success_rate_percent", r)
            self.assertIn("total_allocated_kb", r)
            self.assertIn("free_memory_kb", r)
            self.assertIn("external_fragmentation_kb", r)

        for dest_dir in (RESULTS_DIR, ANALYSIS_RESULTS_DIR):
            csv_path = dest_dir / "memory_results.csv"
            self.assertTrue(csv_path.exists())
            self.assertGreater(csv_path.stat().st_size, 0)

        for chart_dir in (CHARTS_DIR, ANALYSIS_CHARTS_DIR):
            chart_path = chart_dir / "memory_comparison.png"
            self.assertTrue(chart_path.exists())
            self.assertGreater(chart_path.stat().st_size, 1000)

    def test_benchmark_disk(self):
        """Verify Disk benchmarking runs all 4 algorithms and produces valid metrics, CSV, and PNG."""
        res = benchmark_disk()
        self.assertEqual(len(res), 4)
        algos = [r["algorithm"] for r in res]
        self.assertIn("FCFS", algos)
        self.assertIn("SSTF", algos)
        self.assertIn("SCAN", algos)
        self.assertIn("C-SCAN", algos)

        for r in res:
            self.assertIn("total_head_movement", r)
            self.assertIn("average_head_movement", r)
            self.assertIn("requests_serviced", r)

        for dest_dir in (RESULTS_DIR, ANALYSIS_RESULTS_DIR):
            csv_path = dest_dir / "disk_results.csv"
            self.assertTrue(csv_path.exists())
            self.assertGreater(csv_path.stat().st_size, 0)

        for chart_dir in (CHARTS_DIR, ANALYSIS_CHARTS_DIR):
            chart_path = chart_dir / "disk_comparison.png"
            self.assertTrue(chart_path.exists())
            self.assertGreater(chart_path.stat().st_size, 1000)

    def test_analyze_deadlock(self):
        """Verify Deadlock Analysis calculates Need, evaluates Safe Sequence, and exports results."""
        res = analyze_deadlock()
        self.assertTrue(res["is_safe"])
        self.assertIsInstance(res["safe_sequence"], list)
        self.assertGreater(len(res["safe_sequence"]), 0)
        self.assertIn("P1", res["safe_sequence"])
        self.assertTrue(res["request_granted"])
        self.assertEqual(len(res["need_matrix"]), len(res["allocation_matrix"]))

        for dest_dir in (RESULTS_DIR, ANALYSIS_RESULTS_DIR):
            csv_path = dest_dir / "deadlock_results.csv"
            self.assertTrue(csv_path.exists())
            self.assertGreater(csv_path.stat().st_size, 0)

    def test_generate_overall_dashboard(self):
        """Verify 4-panel dashboard is rendered cleanly at 300 DPI."""
        generate_overall_dashboard()
        for chart_dir in (CHARTS_DIR, ANALYSIS_CHARTS_DIR):
            chart_path = chart_dir / "overall_analysis.png"
            self.assertTrue(chart_path.exists())
            self.assertGreater(chart_path.stat().st_size, 50000)

    def test_benchmark_all_workloads(self):
        """Verify multi-workload benchmarks execute across all tiers and output CSVs."""
        workload_res = benchmark_all_workloads()
        self.assertIn("cpu_workloads", workload_res)
        self.assertIn("rr_sensitivity", workload_res)
        self.assertIn("memory_workloads", workload_res)
        self.assertIn("disk_workloads", workload_res)
        self.assertIn("deadlock_workloads", workload_res)

        self.assertTrue((RESULTS_DIR / "cpu_workloads_comparison.csv").exists())
        self.assertTrue((RESULTS_DIR / "rr_quantum_sensitivity.csv").exists())
        self.assertTrue((RESULTS_DIR / "memory_workloads_comparison.csv").exists())
        self.assertTrue((RESULTS_DIR / "disk_workloads_comparison.csv").exists())
        self.assertTrue((RESULTS_DIR / "deadlock_workloads_comparison.csv").exists())

    def test_empty_datasets(self):
        """Verify benchmarking functions gracefully reject empty datasets with descriptive ValueError."""
        with self.assertRaises(ValueError):
            benchmark_cpu([])

        with self.assertRaises(ValueError):
            benchmark_memory([], [("P1", 100)])

        with self.assertRaises(ValueError):
            benchmark_memory([100], [])

        with self.assertRaises(ValueError):
            benchmark_disk([])

        from utils.validators import DeadlockState
        empty_state = DeadlockState(
            process_ids=[],
            resource_ids=[],
            available=[],
            allocation=[],
            max_demand=[],
            need=[],
        )
        with self.assertRaises(ValueError):
            analyze_deadlock(empty_state)

    def test_run_all_benchmarks(self):
        """Verify run_all_benchmarks pipeline completes cleanly without error."""
        run_all_benchmarks()


if __name__ == "__main__":
    unittest.main()
