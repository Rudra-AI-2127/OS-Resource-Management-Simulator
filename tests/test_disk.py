"""
Comprehensive Unit Test Suite for Module 4: Disk Scheduling.
Tests FCFS, SSTF, SCAN, and C-SCAN algorithms across standard workloads,
edge boundaries (0, 199), single requests, initial head matching requests,
one-sided workloads, bidirectional sweeps, left/right direction switches,
duplicate requests, SSTF distance ties, and input validation.
"""

import copy
import sys
import unittest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modules.disk_scheduling import (
    fcfs_disk,
    sstf,
    scan,
    cscan,
    calculate_head_movement,
    compare_disk_algorithms,
    display_disk_result,
    DiskSchedulingResult,
)


class TestDiskSchedulingExhaustive(unittest.TestCase):
    def setUp(self):
        # Blueprint page 4 & 7 standard workload
        self.requests = [98, 183, 37, 122, 14, 124, 65, 67]
        self.initial_head = 53
        self.total_cylinders = 200

    def test_fcfs_standard_workload(self):
        """TC01: Verify FCFS services requests strictly in arrival order."""
        res = fcfs_disk(self.requests, self.initial_head)
        self.assertEqual(res.algorithm, "FCFS")
        self.assertEqual(res.seek_sequence[0], 53)
        self.assertEqual(res.seek_sequence[1:], self.requests)
        self.assertEqual(res.service_sequence, self.requests)
        # Expected seek steps: |98-53|=45, |183-98|=85, |37-183|=146, |122-37|=85,
        # |14-122|=108, |124-14|=110, |65-124|=59, |67-65|=2 -> sum = 640
        self.assertEqual(res.total_head_movement, 640)
        self.assertAlmostEqual(res.average_head_movement, 80.0, places=2)
        self.assertEqual(res.requests_serviced, 8)

    def test_sstf_standard_workload(self):
        """TC08: Verify SSTF greedy shortest seek trajectory and minimal movement."""
        res = sstf(self.requests, self.initial_head)
        self.assertEqual(res.algorithm, "SSTF")
        expected_seq = [53, 65, 67, 37, 14, 98, 122, 124, 183]
        self.assertEqual(res.seek_sequence, expected_seq)
        self.assertEqual(res.service_sequence, expected_seq[1:])
        # 12 + 2 + 30 + 23 + 84 + 24 + 2 + 59 = 236
        self.assertEqual(res.total_head_movement, 236)
        self.assertAlmostEqual(res.average_head_movement, 29.5, places=2)
        self.assertEqual(res.requests_serviced, 8)

    def test_scan_standard_workload_up_right(self):
        """TC09: Verify SCAN elevator sweeps up to boundary 199, reverses, and sweeps down."""
        res = scan(self.requests, self.initial_head, total_cylinders=200, direction="up")
        self.assertEqual(res.algorithm, "SCAN")
        expected_seq = [53, 65, 67, 98, 122, 124, 183, 199, 37, 14]
        self.assertEqual(res.seek_sequence, expected_seq)
        expected_serviced = [65, 67, 98, 122, 124, 183, 37, 14]
        self.assertEqual(res.service_sequence, expected_serviced)
        # (199 - 53) + (199 - 14) = 146 + 185 = 331
        self.assertEqual(res.total_head_movement, 331)
        self.assertAlmostEqual(res.average_head_movement, round(331 / 8, 2), places=2)
        self.assertEqual(res.requests_serviced, 8)

    def test_scan_direction_left_down(self):
        """Verify SCAN elevator sweeps down to boundary 0, reverses, and sweeps up."""
        res = scan(self.requests, self.initial_head, total_cylinders=200, direction="left")
        self.assertEqual(res.algorithm, "SCAN")
        expected_seq = [53, 37, 14, 0, 65, 67, 98, 122, 124, 183]
        self.assertEqual(res.seek_sequence, expected_seq)
        expected_serviced = [37, 14, 65, 67, 98, 122, 124, 183]
        self.assertEqual(res.service_sequence, expected_serviced)
        # (53 - 0) + (183 - 0) = 53 + 183 = 236
        self.assertEqual(res.total_head_movement, 236)
        self.assertAlmostEqual(res.average_head_movement, round(236 / 8, 2), places=2)

    def test_cscan_standard_workload_up_right(self):
        """Verify C-SCAN sweeps up to 199, circular jumps to 0, and sweeps up."""
        res = cscan(self.requests, self.initial_head, total_cylinders=200, direction="right")
        self.assertEqual(res.algorithm, "C-SCAN")
        expected_seq = [53, 65, 67, 98, 122, 124, 183, 199, 0, 14, 37]
        self.assertEqual(res.seek_sequence, expected_seq)
        expected_serviced = [65, 67, 98, 122, 124, 183, 14, 37]
        self.assertEqual(res.service_sequence, expected_serviced)
        # (199 - 53) + (199 - 0) + (37 - 0) = 146 + 199 + 37 = 382
        self.assertEqual(res.total_head_movement, 382)
        self.assertAlmostEqual(res.average_head_movement, round(382 / 8, 2), places=2)

    def test_cscan_direction_left_down(self):
        """Verify C-SCAN sweeps down to 0, circular jumps to 199, and sweeps down."""
        res = cscan(self.requests, self.initial_head, total_cylinders=200, direction="down")
        self.assertEqual(res.algorithm, "C-SCAN")
        expected_seq = [53, 37, 14, 0, 199, 183, 124, 122, 98, 67, 65]
        self.assertEqual(res.seek_sequence, expected_seq)
        expected_serviced = [37, 14, 183, 124, 122, 98, 67, 65]
        self.assertEqual(res.service_sequence, expected_serviced)
        # (53 - 0) + (199 - 0) + (199 - 65) = 53 + 199 + 134 = 386
        self.assertEqual(res.total_head_movement, 386)
        self.assertAlmostEqual(res.average_head_movement, round(386 / 8, 2), places=2)

    def test_empty_request_queue(self):
        """Empty request queue raises ValueError across all algorithms."""
        for fn in (fcfs_disk, sstf, scan, cscan):
            with self.subTest(algorithm=fn.__name__):
                with self.assertRaises(ValueError):
                    fn([], self.initial_head)

    def test_one_request(self):
        """Verify behavior with a single request."""
        res_fcfs = fcfs_disk([100], 53)
        self.assertEqual(res_fcfs.seek_sequence, [53, 100])
        self.assertEqual(res_fcfs.total_head_movement, 47)
        self.assertEqual(res_fcfs.average_head_movement, 47.0)

        res_sstf = sstf([100], 53)
        self.assertEqual(res_sstf.seek_sequence, [53, 100])
        self.assertEqual(res_sstf.total_head_movement, 47)

        # Single request with SCAN moving towards it
        res_scan = scan([100], 53, direction="up")
        self.assertEqual(res_scan.seek_sequence, [53, 100])
        self.assertEqual(res_scan.total_head_movement, 47)

    def test_initial_head_equal_to_request(self):
        """Verify head starting exactly on a requested cylinder services it with 0 distance."""
        res_fcfs = fcfs_disk([53, 98, 37], 53)
        self.assertEqual(res_fcfs.seek_sequence, [53, 53, 98, 37])
        self.assertEqual(res_fcfs.step_movements[0], 0)
        # 0 + 45 + 61 = 106
        self.assertEqual(res_fcfs.total_head_movement, 106)

        res_sstf = sstf([53, 98, 37], 53)
        self.assertEqual(res_sstf.seek_sequence[1], 53)  # serviced first
        self.assertEqual(res_sstf.step_movements[0], 0)

    def test_requests_on_one_side_only(self):
        """Verify algorithms when all requests lie strictly on one side of head."""
        reqs = [60, 70, 80]
        # FCFS
        res_fcfs = fcfs_disk(reqs, 50)
        self.assertEqual(res_fcfs.total_head_movement, 30)

        # SCAN moving towards requests: does not touch boundary because left is empty
        res_scan_up = scan(reqs, 50, direction="up")
        self.assertEqual(res_scan_up.seek_sequence, [50, 60, 70, 80])
        self.assertEqual(res_scan_up.total_head_movement, 30)

        # SCAN moving away from requests: sweeps to 0, reverses, and services all
        res_scan_down = scan(reqs, 50, direction="down")
        self.assertEqual(res_scan_down.seek_sequence, [50, 0, 60, 70, 80])
        # (50 - 0) + (80 - 0) = 50 + 80 = 130
        self.assertEqual(res_scan_down.total_head_movement, 130)

    def test_minimum_and_maximum_boundary_requests(self):
        """Verify requests placed exactly at cylinder 0 and cylinder 199."""
        reqs = [0, 199]
        res_scan_up = scan(reqs, 50, direction="up")
        # 199 is visited as a request; no duplicate boundary added; reverses to 0
        self.assertEqual(res_scan_up.seek_sequence, [50, 199, 0])
        # (199 - 50) + (199 - 0) = 149 + 199 = 348
        self.assertEqual(res_scan_up.total_head_movement, 348)

        res_scan_down = scan(reqs, 50, direction="down")
        self.assertEqual(res_scan_down.seek_sequence, [50, 0, 199])
        # (50 - 0) + (199 - 0) = 50 + 199 = 249
        self.assertEqual(res_scan_down.total_head_movement, 249)

    def test_invalid_cylinder_values(self):
        """Verify out-of-bounds, negative, or excessive cylinder requests raise ValueError."""
        # Negative cylinder
        with self.assertRaises(ValueError):
            fcfs_disk([50, -5], 53)

        # Cylinder >= total_cylinders
        with self.assertRaises(ValueError):
            sstf([50, 200], 53, total_cylinders=200)

        # Head out of bounds
        with self.assertRaises(ValueError):
            scan([50], initial_head=250, total_cylinders=200)

        # Invalid direction string
        with self.assertRaises(ValueError):
            scan([50], initial_head=53, direction="diagonal")

    def test_duplicate_requests(self):
        """Verify duplicate requests are all serviced without dropping."""
        reqs = [40, 40, 60]
        res_sstf = sstf(reqs, 50)
        # From 50 to 40 (10), 40 to 40 (0), 40 to 60 (20) -> total 30
        self.assertEqual(res_sstf.requests_serviced, 3)
        self.assertEqual(res_sstf.seek_sequence, [50, 40, 40, 60])
        self.assertEqual(res_sstf.total_head_movement, 30)
        self.assertEqual(res_sstf.average_head_movement, 10.0)

    def test_sstf_equal_distance_ties(self):
        """Verify SSTF breaks equal-distance ties deterministically by lower cylinder number."""
        # Head is 50; requests at 40 (dist 10) and 60 (dist 10)
        # Lower cylinder (40) must be chosen first
        res = sstf([60, 40], 50)
        self.assertEqual(res.seek_sequence, [50, 40, 60])
        # |40 - 50| = 10, |60 - 40| = 20 -> total 30
        self.assertEqual(res.total_head_movement, 30)

        # Symmetric check with reverse arrival order [40, 60]
        res2 = sstf([40, 60], 50)
        self.assertEqual(res2.seek_sequence, [50, 40, 60])

    def test_caller_immutability(self):
        """Verify executing algorithms does not mutate the caller's request list."""
        original_reqs = [98, 183, 37, 122, 14, 124, 65, 67]
        reqs_copy = list(original_reqs)
        sstf(reqs_copy, 53)
        scan(reqs_copy, 53)
        cscan(reqs_copy, 53)
        self.assertEqual(reqs_copy, original_reqs)

    def test_compare_disk_algorithms(self):
        """Verify comparison driver produces side-by-side metrics across all 4 algorithms."""
        comp = compare_disk_algorithms(self.requests, self.initial_head, total_cylinders=200)
        self.assertIn("results", comp)
        self.assertIn("comparison_table", comp)
        self.assertEqual(len(comp["comparison_table"]), 4)
        # On standard blueprint workload, SSTF achieves minimal head movement (236)
        self.assertEqual(comp["best_algorithm"], "SSTF")
        self.assertEqual(comp["results"]["SSTF"].total_head_movement, 236)

    def test_display_disk_result(self):
        """Verify ASCII display function contains seek path, step table, and metrics."""
        res = sstf(self.requests, self.initial_head)
        output = display_disk_result(res)
        self.assertIn("DISK SCHEDULING: SSTF", output)
        self.assertIn("Head Seek Path", output)
        self.assertIn("Step Seek Table", output)
        self.assertIn("236 cylinders", output)


if __name__ == "__main__":
    unittest.main()
