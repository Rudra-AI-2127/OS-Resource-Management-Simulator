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


class TestCPUScheduling(unittest.TestCase):
    def setUp(self):
        # Standard blueprint 3-process workload
        self.procs_blueprint_3 = [
            Process(pid="P1", arrival_time=0, burst_time=5),
            Process(pid="P2", arrival_time=1, burst_time=3),
            Process(pid="P3", arrival_time=2, burst_time=8),
        ]
        # Standard blueprint 4-process workload
        self.procs_blueprint_4 = [
            Process(pid="P1", arrival_time=0, burst_time=5, priority=2),
            Process(pid="P2", arrival_time=1, burst_time=3, priority=1),
            Process(pid="P3", arrival_time=2, burst_time=8, priority=4),
            Process(pid="P4", arrival_time=3, burst_time=2, priority=3),
        ]

    def test_fcfs_blueprint_trace(self):
        """TC01: Verify FCFS matches Blueprint Page 6 example."""
        scheduled, segments = fcfs(self.procs_blueprint_3)
        p_map = {p.pid: p for p in scheduled}

        self.assertEqual(p_map["P1"].completion_time, 5)
        self.assertEqual(p_map["P1"].turnaround_time, 5)
        self.assertEqual(p_map["P1"].waiting_time, 0)

        self.assertEqual(p_map["P2"].completion_time, 8)
        self.assertEqual(p_map["P2"].turnaround_time, 7)
        self.assertEqual(p_map["P2"].waiting_time, 4)

        self.assertEqual(p_map["P3"].completion_time, 16)
        self.assertEqual(p_map["P3"].turnaround_time, 14)
        self.assertEqual(p_map["P3"].waiting_time, 6)

        metrics = calculate_metrics(scheduled)
        self.assertAlmostEqual(metrics["avg_waiting_time"], 3.33, places=2)
        self.assertAlmostEqual(metrics["avg_turnaround_time"], 8.67, places=2)

    def test_sjf_non_preemptive(self):
        """Verify non-preemptive SJF picks shortest ready process."""
        scheduled, segments = sjf(self.procs_blueprint_4)
        p_map = {p.pid: p for p in scheduled}

        # P1 starts at 0 and runs 5 units (completion = 5)
        self.assertEqual(p_map["P1"].completion_time, 5)
        # At t=5, P4(BT=2), P2(BT=3), P3(BT=8) are ready. P4 runs 5..7
        self.assertEqual(p_map["P4"].completion_time, 7)
        self.assertEqual(p_map["P4"].waiting_time, 2)  # TAT=4, WT=4-2=2
        # Then P2 runs 7..10
        self.assertEqual(p_map["P2"].completion_time, 10)
        self.assertEqual(p_map["P2"].waiting_time, 6)  # TAT=9, WT=9-3=6
        # Then P3 runs 10..18
        self.assertEqual(p_map["P3"].completion_time, 18)
        self.assertEqual(p_map["P3"].waiting_time, 8)  # TAT=16, WT=16-8=8

        metrics = calculate_metrics(scheduled)
        self.assertAlmostEqual(metrics["avg_waiting_time"], 4.0, places=2)

    def test_priority_scheduling_non_preemptive(self):
        """Verify Priority scheduling (lower integer = higher priority)."""
        scheduled, segments = priority_scheduling(self.procs_blueprint_4)
        p_map = {p.pid: p for p in scheduled}

        # P1 starts at 0, runs to 5
        self.assertEqual(p_map["P1"].completion_time, 5)
        # At t=5, ready: P2(prio 1), P4(prio 3), P3(prio 4). P2 has highest priority (1)
        self.assertEqual(p_map["P2"].completion_time, 8)
        # Next highest is P4 (prio 3) -> runs 8..10
        self.assertEqual(p_map["P4"].completion_time, 10)
        # Lowest is P3 (prio 4) -> runs 10..18
        self.assertEqual(p_map["P3"].completion_time, 18)

    def test_round_robin_preemptive(self):
        """Verify Round Robin with time quantum = 2."""
        procs = [
            Process(pid="P1", arrival_time=0, burst_time=5),
            Process(pid="P2", arrival_time=1, burst_time=4),
            Process(pid="P3", arrival_time=2, burst_time=2),
        ]
        scheduled, segments = round_robin(procs, quantum=2)
        p_map = {p.pid: p for p in scheduled}

        # P3 finishes in one slice: t=4..6 (CT=6, TAT=4, WT=2)
        self.assertEqual(p_map["P3"].completion_time, 6)
        self.assertEqual(p_map["P3"].waiting_time, 2)
        # All complete
        for p in scheduled:
            self.assertEqual(p.turnaround_time, p.completion_time - p.arrival_time)
            self.assertEqual(p.waiting_time, p.turnaround_time - p.burst_time)

    def test_idle_time_handling(self):
        """Verify CPU handles arrival gap with an IDLE segment."""
        procs = [
            Process(pid="P1", arrival_time=2, burst_time=3),
            Process(pid="P2", arrival_time=8, burst_time=2),
        ]
        scheduled, segments = fcfs(procs)
        self.assertEqual(segments[0].pid, "IDLE")
        self.assertEqual(segments[0].duration, 2)  # 0 to 2
        self.assertEqual(segments[1].pid, "P1")     # 2 to 5
        self.assertEqual(segments[2].pid, "IDLE")   # 5 to 8
        self.assertEqual(segments[2].duration, 3)
        self.assertEqual(segments[3].pid, "P2")     # 8 to 10

    def test_empty_process_list(self):
        """TC03: Empty process list raises ValueError."""
        with self.assertRaises(ValueError):
            fcfs([])

    def test_gantt_chart_generation(self):
        """Verify Gantt chart output string."""
        scheduled, segments = fcfs(self.procs_blueprint_3)
        chart_str = generate_gantt_chart(segments)
        self.assertIn("P1", chart_str)
        self.assertIn("P2", chart_str)
        self.assertIn("P3", chart_str)


if __name__ == "__main__":
    unittest.main()
