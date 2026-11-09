import unittest
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modules.memory_management import (
    first_fit,
    best_fit,
    worst_fit,
    calculate_fragmentation,
    display_allocation,
    MemoryBlock,
    MemoryAllocationResult,
)


class TestMemoryManagement(unittest.TestCase):
    def setUp(self):
        # Blueprint page 3 & 6 example
        self.blocks = [100, 500, 200, 300, 600]
        self.requests = [("P1", 212), ("P2", 417), ("P3", 112), ("P4", 426)]

    def test_first_fit_blueprint(self):
        """TC04: Verify First Fit allocation on blueprint workload."""
        res = first_fit(self.blocks, self.requests)
        self.assertEqual(res.algorithm, "First Fit")
        self.assertEqual(len(res.allocations), 3)  # P1, P2, P3 allocated, P4 fails
        self.assertIn("P4", res.unallocated_processes)

        alloc_p1 = next(a for a in res.allocations if a["pid"] == "P1")
        self.assertEqual(alloc_p1["allocated_kb"], 212)
        self.assertEqual(alloc_p1["initial_block_kb"], 500)
        self.assertEqual(alloc_p1["remaining_block_kb"], 288)

        alloc_p2 = next(a for a in res.allocations if a["pid"] == "P2")
        self.assertEqual(alloc_p2["allocated_kb"], 417)
        self.assertEqual(alloc_p2["initial_block_kb"], 600)
        self.assertEqual(alloc_p2["remaining_block_kb"], 183)

    def test_best_fit_blueprint(self):
        """Verify Best Fit picks smallest suitable block."""
        res = best_fit(self.blocks, self.requests)
        self.assertEqual(res.algorithm, "Best Fit")

        # P1 (212) best fits in 300 (leaving 88)
        alloc_p1 = next(a for a in res.allocations if a["pid"] == "P1")
        self.assertEqual(alloc_p1["initial_block_kb"], 300)
        self.assertEqual(alloc_p1["remaining_block_kb"], 88)

        # P2 (417) best fits in 500 (leaving 83)
        alloc_p2 = next(a for a in res.allocations if a["pid"] == "P2")
        self.assertEqual(alloc_p2["initial_block_kb"], 500)
        self.assertEqual(alloc_p2["remaining_block_kb"], 83)

        # P3 (112) best fits in 200 (leaving 88)
        alloc_p3 = next(a for a in res.allocations if a["pid"] == "P3")
        self.assertEqual(alloc_p3["initial_block_kb"], 200)
        self.assertEqual(alloc_p3["remaining_block_kb"], 88)

        # P4 (426) best fits in 600 (leaving 174)
        alloc_p4 = next(a for a in res.allocations if a["pid"] == "P4")
        self.assertEqual(alloc_p4["initial_block_kb"], 600)
        self.assertEqual(alloc_p4["remaining_block_kb"], 174)

        # In Best Fit, all 4 processes are allocated!
        self.assertEqual(len(res.unallocated_processes), 0)

    def test_worst_fit_blueprint(self):
        """Verify Worst Fit picks largest available block."""
        res = worst_fit(self.blocks, self.requests)
        self.assertEqual(res.algorithm, "Worst Fit")

        # P1 (212) goes into 600 (leaving 388)
        alloc_p1 = next(a for a in res.allocations if a["pid"] == "P1")
        self.assertEqual(alloc_p1["initial_block_kb"], 600)
        self.assertEqual(alloc_p1["remaining_block_kb"], 388)

    def test_insufficient_memory(self):
        """TC05: Allocation failure and external fragmentation calculation."""
        blocks = [100, 100]
        requests = [("P1", 150)]
        res = first_fit(blocks, requests)
        self.assertIn("P1", res.unallocated_processes)
        # Total free memory is 200 KB >= 150 KB, but no block >= 150 KB -> External Frag = 200 KB
        self.assertEqual(res.external_fragmentation_kb, 200)

    def test_display_allocation_output(self):
        """Verify display_allocation returns formatted table."""
        res = first_fit(self.blocks, self.requests)
        table_str = display_allocation(res)
        self.assertIn("P1", table_str)
        self.assertIn("212", table_str)
        self.assertIn("MEMORY ALLOCATION RESULTS", table_str)


if __name__ == "__main__":
    unittest.main()
