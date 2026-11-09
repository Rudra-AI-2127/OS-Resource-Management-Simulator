import unittest
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modules.disk_scheduling import (
    fcfs_disk,
    sstf,
    scan,
    cscan,
    calculate_head_movement,
    DiskSchedulingResult,
)


class TestDiskScheduling(unittest.TestCase):
    def setUp(self):
        # Blueprint page 4 & 7 standard workload
        self.requests = [98, 183, 37, 122, 14, 124, 65, 67]
        self.initial_head = 53
        self.total_cylinders = 200

    def test_fcfs_disk(self):
        """Verify FCFS disk scheduling trajectory and movement."""
        res = fcfs_disk(self.requests, self.initial_head)
        self.assertEqual(res.algorithm, "FCFS")
        self.assertEqual(res.seek_sequence[0], 53)
        self.assertEqual(res.seek_sequence[1:], self.requests)
        self.assertEqual(res.total_head_movement, 640)
        self.assertAlmostEqual(res.average_head_movement, 80.0, places=2)
        self.assertEqual(res.requests_serviced, 8)

    def test_sstf_disk(self):
        """TC08: Verify SSTF sequence and head movement."""
        res = sstf(self.requests, self.initial_head)
        self.assertEqual(res.algorithm, "SSTF")
        expected_seq = [53, 65, 67, 37, 14, 98, 122, 124, 183]
        self.assertEqual(res.seek_sequence, expected_seq)
        self.assertEqual(res.total_head_movement, 236)
        self.assertAlmostEqual(res.average_head_movement, 29.5, places=2)

    def test_scan_disk(self):
        """Verify SCAN elevator algorithm with boundary sweep."""
        res = scan(self.requests, self.initial_head, total_cylinders=200, direction="up")
        self.assertEqual(res.algorithm, "SCAN")
        expected_seq = [53, 65, 67, 98, 122, 124, 183, 199, 37, 14]
        self.assertEqual(res.seek_sequence, expected_seq)
        # (199 - 53) + (199 - 14) = 146 + 185 = 331
        self.assertEqual(res.total_head_movement, 331)
        self.assertAlmostEqual(res.average_head_movement, round(331 / 8, 2), places=2)

    def test_cscan_disk(self):
        """Verify C-SCAN with boundary jump accounting."""
        res = cscan(self.requests, self.initial_head, total_cylinders=200, direction="up")
        self.assertEqual(res.algorithm, "C-SCAN")
        expected_seq = [53, 65, 67, 98, 122, 124, 183, 199, 0, 14, 37]
        self.assertEqual(res.seek_sequence, expected_seq)
        # (199 - 53) + (199 - 0) + (37 - 0) = 146 + 199 + 37 = 382
        self.assertEqual(res.total_head_movement, 382)
        self.assertAlmostEqual(res.average_head_movement, round(382 / 8, 2), places=2)

    def test_invalid_cylinder_request(self):
        """Verify out-of-bounds cylinder requests raise ValueError."""
        with self.assertRaises(ValueError):
            fcfs_disk([98, 250], self.initial_head)
        with self.assertRaises(ValueError):
            sstf([98, -1], self.initial_head)

    def test_empty_requests(self):
        """Verify empty requests raise ValueError."""
        with self.assertRaises(ValueError):
            scan([], self.initial_head)


if __name__ == "__main__":
    unittest.main()
