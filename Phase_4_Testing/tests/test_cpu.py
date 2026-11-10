"""
Unit test suite for CPU Scheduling Module.
Covers FCFS, SJF (non-preemptive), Round Robin, and Priority (non-preemptive).
Tests normal workloads, single process, simultaneous arrivals, idle gaps, ties,
quantum boundaries, invalid inputs, Gantt continuity, and metric calculations.
"""

import unittest
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.validators import Process
from modules.cpu_scheduling import (
    fcfs,
    sjf,
    round_robin,
    priority_scheduling,
    calculate_metrics,
    generate_gantt_chart,
)


class TestCPUSchedulingExhaustive(unittest.TestCase):
    def setUp(self):
        # Blueprint 4-process workload
        self.procs_blueprint = [
            Process(pid="P1", arrival_time=0, burst_time=5, priority=2),
            Process(pid="P2", arrival_time=1, burst_time=3, priority=1),
            Process(pid="P3", arrival_time=2, burst_time=8, priority=4),
            Process(pid="P4", arrival_time=3, burst_time=2, priority=3),
        ]

    def _assert_gantt_continuity(self, segments):
        """Verifies Gantt chart segments are contiguous with no time gaps or overlaps."""
        self.assertTrue(len(segments) > 0)
        for i in range(len(segments) - 1):
            self.assertEqual(
                segments[i].end_time,
                segments[i + 1].start_time,
                f"Gantt discontinuity at segment {i} ({segments[i]}) -> {segments[i+1]}",
            )
            self.assertEqual(
                segments[i].duration,
                segments[i].end_time - segments[i].start_time,
            )

    def _assert_no_execution_before_arrival(self, procs, segments):
        """Verifies no process was dispatched before its arrival time."""
        p_map = {p.pid: p for p in procs}
        for seg in segments:
            if seg.pid != "IDLE":
                orig_at = p_map[seg.pid].arrival_time
                self.assertGreaterEqual(
                    seg.start_time,
                    orig_at,
                    f"Process {seg.pid} executed at {seg.start_time} before arrival {orig_at}",
                )

    def _assert_all_processes_finish(self, procs, original_count):
        """Verifies all input processes finished execution and have valid metrics."""
        self.assertEqual(len(procs), original_count)
        for p in procs:
            self.assertEqual(p.remaining_time, 0)
            self.assertEqual(p.turnaround_time, p.completion_time - p.arrival_time)
            self.assertEqual(p.waiting_time, p.turnaround_time - p.burst_time)
            self.assertEqual(p.response_time, p.start_time - p.arrival_time)
            self.assertGreaterEqual(p.waiting_time, 0)
            self.assertGreaterEqual(p.response_time, 0)

    # 1. Normal Workload
    def test_fcfs_normal_workload(self):
        """TC01: Verify FCFS on normal workload."""
        scheduled, segments = fcfs(self.procs_blueprint)
        self._assert_gantt_continuity(segments)
        self._assert_no_execution_before_arrival(scheduled, segments)
        self._assert_all_processes_finish(scheduled, 4)

        p_map = {p.pid: p for p in scheduled}
        self.assertEqual(p_map["P1"].completion_time, 5)
        self.assertEqual(p_map["P2"].completion_time, 8)
        self.assertEqual(p_map["P3"].completion_time, 16)
        self.assertEqual(p_map["P4"].completion_time, 18)

        metrics = calculate_metrics(scheduled, segments)
        self.assertAlmostEqual(metrics["avg_waiting_time"], 5.75, places=2)
        self.assertAlmostEqual(metrics["avg_turnaround_time"], 10.25, places=2)
        self.assertAlmostEqual(metrics["avg_response_time"], 5.75, places=2)
        self.assertEqual(metrics["total_execution_time"], 18)
        self.assertAlmostEqual(metrics["cpu_utilization"], 100.0, places=2)

    def test_sjf_normal_workload(self):
        """Verify non-preemptive SJF picks shortest ready job."""
        scheduled, segments = sjf(self.procs_blueprint)
        self._assert_gantt_continuity(segments)
        self._assert_no_execution_before_arrival(scheduled, segments)
        self._assert_all_processes_finish(scheduled, 4)

        p_map = {p.pid: p for p in scheduled}
        self.assertEqual(p_map["P1"].completion_time, 5)
        self.assertEqual(p_map["P4"].completion_time, 7)  # BT=2
        self.assertEqual(p_map["P2"].completion_time, 10) # BT=3
        self.assertEqual(p_map["P3"].completion_time, 18) # BT=8

        metrics = calculate_metrics(scheduled, segments)
        self.assertAlmostEqual(metrics["avg_waiting_time"], 4.0, places=2)
        self.assertAlmostEqual(metrics["avg_turnaround_time"], 8.5, places=2)

    def test_priority_normal_workload(self):
        """Verify non-preemptive Priority (lower integer = higher priority)."""
        scheduled, segments = priority_scheduling(self.procs_blueprint)
        self._assert_gantt_continuity(segments)
        self._assert_no_execution_before_arrival(scheduled, segments)
        self._assert_all_processes_finish(scheduled, 4)

        p_map = {p.pid: p for p in scheduled}
        self.assertEqual(p_map["P1"].completion_time, 5)
        self.assertEqual(p_map["P2"].completion_time, 8)  # Priority 1
        self.assertEqual(p_map["P4"].completion_time, 10) # Priority 3
        self.assertEqual(p_map["P3"].completion_time, 18) # Priority 4

        metrics = calculate_metrics(scheduled, segments)
        self.assertAlmostEqual(metrics["avg_waiting_time"], 4.25, places=2)
        self.assertAlmostEqual(metrics["avg_turnaround_time"], 8.75, places=2)

    def test_round_robin_normal_workload(self):
        """Verify Round Robin preemptive scheduling (quantum=2)."""
        scheduled, segments = round_robin(self.procs_blueprint, quantum=2)
        self._assert_gantt_continuity(segments)
        self._assert_no_execution_before_arrival(scheduled, segments)
        self._assert_all_processes_finish(scheduled, 4)

        p_map = {p.pid: p for p in scheduled}
        self.assertEqual(p_map["P1"].completion_time, 14)
        self.assertEqual(p_map["P2"].completion_time, 11)
        self.assertEqual(p_map["P4"].completion_time, 10)
        self.assertEqual(p_map["P3"].completion_time, 18)

        metrics = calculate_metrics(scheduled, segments)
        self.assertAlmostEqual(metrics["avg_waiting_time"], 7.25, places=2)
        self.assertAlmostEqual(metrics["avg_turnaround_time"], 11.75, places=2)

    # 2. Single Process
    def test_single_process(self):
        """Verify execution when only one process is submitted."""
        single = [Process(pid="P1", arrival_time=2, burst_time=4, priority=1)]
        scheduled, segments = fcfs(single)
        self._assert_gantt_continuity(segments)
        self._assert_all_processes_finish(scheduled, 1)
        self.assertEqual(scheduled[0].completion_time, 6)
        self.assertEqual(scheduled[0].waiting_time, 0)
        self.assertEqual(scheduled[0].turnaround_time, 4)
        self.assertEqual(scheduled[0].response_time, 0)

        # Segment 0 is IDLE 0..2, Segment 1 is P1 2..6
        self.assertEqual(segments[0].pid, "IDLE")
        self.assertEqual(segments[0].duration, 2)
        self.assertEqual(segments[1].pid, "P1")
        self.assertEqual(segments[1].duration, 4)

    # 3. Simultaneous Arrivals
    def test_simultaneous_arrivals(self):
        """Verify deterministic ordering when processes arrive at the exact same instant."""
        simultaneous = [
            Process(pid="P3", arrival_time=0, burst_time=4),
            Process(pid="P1", arrival_time=0, burst_time=4),
            Process(pid="P2", arrival_time=0, burst_time=4),
        ]
        scheduled, segments = fcfs(simultaneous)
        self.assertEqual([p.pid for p in scheduled], ["P1", "P2", "P3"])

    # 4. CPU Idle Periods
    def test_cpu_idle_periods(self):
        """Verify explicit IDLE intervals when arrival gaps exist."""
        idle_procs = [
            Process(pid="P1", arrival_time=2, burst_time=3),  # runs 2..5
            Process(pid="P2", arrival_time=8, burst_time=2),  # runs 8..10
        ]
        scheduled, segments = fcfs(idle_procs)
        self._assert_gantt_continuity(segments)
        self.assertEqual(len(segments), 4)
        self.assertEqual(segments[0].pid, "IDLE")
        self.assertEqual((segments[0].start_time, segments[0].end_time), (0, 2))
        self.assertEqual(segments[1].pid, "P1")
        self.assertEqual((segments[1].start_time, segments[1].end_time), (2, 5))
        self.assertEqual(segments[2].pid, "IDLE")
        self.assertEqual((segments[2].start_time, segments[2].end_time), (5, 8))
        self.assertEqual(segments[3].pid, "P2")
        self.assertEqual((segments[3].start_time, segments[3].end_time), (8, 10))

        metrics = calculate_metrics(scheduled, segments)
        self.assertEqual(metrics["total_execution_time"], 10)
        # Busy time is 3 + 2 = 5, total time = 10 -> 50% CPU utilization
        self.assertAlmostEqual(metrics["cpu_utilization"], 50.0, places=2)

    # 5. Equal Burst Times in SJF
    def test_sjf_equal_burst_times(self):
        """Verify tie-breaker in SJF when burst times are equal (breaks by AT, then PID)."""
        procs = [
            Process(pid="P1", arrival_time=0, burst_time=4),
            Process(pid="P2", arrival_time=1, burst_time=2),
            Process(pid="P3", arrival_time=1, burst_time=2),
        ]
        scheduled, segments = sjf(procs)
        # P1 runs 0..4. At t=4, both P2 and P3 have BT=2, AT=1. Tie-breaker selects P2 by PID.
        self.assertEqual(scheduled[1].pid, "P2")
        self.assertEqual(scheduled[2].pid, "P3")

    # 6. Equal Priorities
    def test_equal_priorities(self):
        """Verify tie-breaker in Priority scheduling when priorities are equal."""
        procs = [
            Process(pid="P1", arrival_time=0, burst_time=3, priority=2),
            Process(pid="P2", arrival_time=1, burst_time=2, priority=1),
            Process(pid="P3", arrival_time=1, burst_time=4, priority=1),
        ]
        scheduled, segments = priority_scheduling(procs)
        # At t=3, both P2 and P3 have Priority 1, AT=1. Tie-breaker selects P2 by PID.
        self.assertEqual(scheduled[1].pid, "P2")
        self.assertEqual(scheduled[2].pid, "P3")

    # 7. Time Quantum = 1
    def test_round_robin_quantum_one(self):
        """Verify Round Robin with fine-grained time slice (q=1)."""
        procs = [
            Process(pid="P1", arrival_time=0, burst_time=2),
            Process(pid="P2", arrival_time=0, burst_time=2),
        ]
        scheduled, segments = round_robin(procs, quantum=1)
        self._assert_gantt_continuity(segments)
        self.assertEqual([s.pid for s in segments], ["P1", "P2", "P1", "P2"])
        self.assertEqual([s.duration for s in segments], [1, 1, 1, 1])

    # 8. Time Quantum Larger Than All Burst Times
    def test_round_robin_quantum_large(self):
        """Verify Round Robin behaves like FCFS when quantum >= all burst times."""
        procs = [
            Process(pid="P1", arrival_time=0, burst_time=3),
            Process(pid="P2", arrival_time=1, burst_time=4),
        ]
        sched_rr, segs_rr = round_robin(procs, quantum=100)
        sched_fcfs, segs_fcfs = fcfs(procs)
        self.assertEqual(
            [p.completion_time for p in sched_rr],
            [p.completion_time for p in sched_fcfs],
        )

    # 9. Validation Exceptions
    def test_invalid_burst_time(self):
        """TC02: Burst time <= 0 raises ValueError."""
        with self.assertRaises(ValueError):
            fcfs([Process(pid="P1", arrival_time=0, burst_time=0)])
        with self.assertRaises(ValueError):
            sjf([Process(pid="P1", arrival_time=0, burst_time=-4)])

    def test_negative_arrival_time(self):
        """Negative arrival time raises ValueError."""
        with self.assertRaises(ValueError):
            fcfs([Process(pid="P1", arrival_time=-2, burst_time=5)])

    def test_empty_process_list(self):
        """TC03: Empty process collection raises ValueError."""
        with self.assertRaises(ValueError):
            fcfs([])
        with self.assertRaises(ValueError):
            sjf([])
        with self.assertRaises(ValueError):
            round_robin([], quantum=2)
        with self.assertRaises(ValueError):
            priority_scheduling([])

    def test_duplicate_process_ids(self):
        """Duplicate PIDs raise ValueError."""
        with self.assertRaises(ValueError):
            fcfs([
                Process(pid="P1", arrival_time=0, burst_time=3),
                Process(pid="P1", arrival_time=1, burst_time=4),
            ])

    def test_gantt_chart_generation(self):
        """Verify ASCII Gantt chart rendering."""
        scheduled, segments = fcfs(self.procs_blueprint)
        chart_str = generate_gantt_chart(segments)
        self.assertIn("P1", chart_str)
        self.assertIn("P2", chart_str)
        self.assertIn("P3", chart_str)
        self.assertIn("P4", chart_str)


if __name__ == "__main__":
    unittest.main()
