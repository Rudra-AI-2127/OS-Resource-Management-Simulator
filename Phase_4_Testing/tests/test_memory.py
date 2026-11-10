"""
Unit test suite for Memory Management Module.
Covers First Fit, Best Fit, and Worst Fit with dynamic variable-sized partition splitting.
Tests exact fit, splitting, insufficient memory, input isolation, validation exceptions,
and comparison metrics across identical workloads.
"""

import unittest
import copy
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modules.memory_management import (
    first_fit,
    best_fit,
    worst_fit,
    compare_memory_algorithms,
    calculate_fragmentation,
    display_allocation,
    MemoryBlock,
    MemoryAllocationResult,
)


class TestMemoryManagementExhaustive(unittest.TestCase):
    def setUp(self):
        # Blueprint standard workload: Blocks [100, 500, 200, 300, 600], Requests [212, 417, 112, 426]
        self.blocks = [100, 500, 200, 300, 600]
        self.requests_raw = [212, 417, 112, 426]
        self.requests_tuples = [("P1", 212), ("P2", 417), ("P3", 112), ("P4", 426)]

    # 1. Exact Block Fit
    def test_exact_block_fit(self):
        """Verify allocation when request matches block size exactly (remaining = 0)."""
        blocks = [200]
        requests = [("P1", 200)]
        res = first_fit(blocks, requests)
        self.assertEqual(res.successful_allocations, 1)
        self.assertEqual(res.failed_allocations, 0)
        alloc = res.allocations[0]
        self.assertEqual(alloc["allocated_kb"], 200)
        self.assertEqual(alloc["initial_block_kb"], 200)
        self.assertEqual(alloc["remaining_block_kb"], 0)
        self.assertEqual(res.total_free_memory_kb, 0)
        self.assertEqual(res.internal_fragmentation_kb, 0)

    # 2. Smaller Request (Dynamic Splitting)
    def test_smaller_request_splitting(self):
        """Verify dynamic block splitting leaves remaining free space in the pool."""
        blocks = [500]
        requests = [("P1", 200)]
        res = first_fit(blocks, requests)
        self.assertEqual(res.successful_allocations, 1)
        alloc = res.allocations[0]
        self.assertEqual(alloc["allocated_kb"], 200)
        self.assertEqual(alloc["initial_block_kb"], 500)
        self.assertEqual(alloc["remaining_block_kb"], 300)
        self.assertEqual(res.total_free_memory_kb, 300)
        # Leftover space is in the free pool, NOT internal fragmentation
        self.assertEqual(res.internal_fragmentation_kb, 0)

    # 3. Larger Request than any single block
    def test_larger_request(self):
        """Verify request exceeding individual block capacity cannot be allocated."""
        blocks = [100, 200]
        requests = [("P1", 250)]
        res = first_fit(blocks, requests)
        self.assertEqual(res.successful_allocations, 0)
        self.assertEqual(res.failed_allocations, 1)
        self.assertIn("P1", res.unallocated_processes)
        # Total free memory is 300 KB >= 250 KB -> External Fragmentation occurs
        self.assertEqual(res.external_fragmentation_kb, 300)

    # 4. Insufficient Memory
    def test_insufficient_memory(self):
        """TC05: Handled rejection when memory is insufficient."""
        blocks = [50, 100]
        requests = [("P1", 200)]
        res = best_fit(blocks, requests)
        self.assertEqual(res.failed_allocations, 1)
        self.assertIn("P1", res.unallocated_processes)
        # Total free memory = 150 < 200, so external fragmentation is 0 (total memory is simply insufficient)
        self.assertEqual(res.external_fragmentation_kb, 0)

    # 5. Single Block
    def test_single_block(self):
        """Verify behavior with a single memory block."""
        blocks = [400]
        requests = [("P1", 100), ("P2", 200), ("P3", 150)]
        # P1 takes 100 -> block remaining = 300
        # P2 takes 200 -> block remaining = 100
        # P3 needs 150 -> cannot fit in 100 -> fails
        res = first_fit(blocks, requests)
        self.assertEqual(res.successful_allocations, 2)
        self.assertEqual(res.failed_allocations, 1)
        self.assertEqual(res.total_allocated_kb, 300)
        self.assertEqual(res.total_free_memory_kb, 100)
        self.assertIn("P3", res.unallocated_processes)

    # 6. Multiple Blocks (Blueprint First Fit)
    def test_first_fit_blueprint(self):
        """TC04: Verify First Fit allocation on blueprint workload."""
        res = first_fit(self.blocks, self.requests_tuples)
        self.assertEqual(res.algorithm, "First Fit")
        self.assertEqual(res.successful_allocations, 3)
        self.assertEqual(res.failed_allocations, 1)
        self.assertIn("P4", res.unallocated_processes)

        alloc_p1 = next(a for a in res.allocations if a["pid"] == "P1")
        self.assertEqual(alloc_p1["block_id"], 2)  # Block 2 (500)
        self.assertEqual(alloc_p1["initial_block_kb"], 500)
        self.assertEqual(alloc_p1["remaining_block_kb"], 288)

        alloc_p2 = next(a for a in res.allocations if a["pid"] == "P2")
        self.assertEqual(alloc_p2["block_id"], 5)  # Block 5 (600)
        self.assertEqual(alloc_p2["initial_block_kb"], 600)
        self.assertEqual(alloc_p2["remaining_block_kb"], 183)

        alloc_p3 = next(a for a in res.allocations if a["pid"] == "P3")
        # P3 (112) fits in remaining of Block 2 (288 KB)
        self.assertEqual(alloc_p3["block_id"], 2)
        self.assertEqual(alloc_p3["initial_block_kb"], 288)
        self.assertEqual(alloc_p3["remaining_block_kb"], 176)

        # Total free space is 100 + 176 + 200 + 300 + 183 = 959 KB >= 426 KB (P4)
        self.assertEqual(res.external_fragmentation_kb, 959)
        self.assertEqual(res.internal_fragmentation_kb, 0)

    # 7. Best Fit Blueprint
    def test_best_fit_blueprint(self):
        """Verify Best Fit finds tightest fitting block for each request."""
        res = best_fit(self.blocks, self.requests_tuples)
        self.assertEqual(res.algorithm, "Best Fit")
        self.assertEqual(res.successful_allocations, 4)
        self.assertEqual(res.failed_allocations, 0)

        # P1 (212) -> Block 4 (300) leaves 88
        alloc_p1 = next(a for a in res.allocations if a["pid"] == "P1")
        self.assertEqual(alloc_p1["block_id"], 4)
        self.assertEqual(alloc_p1["remaining_block_kb"], 88)

        # P2 (417) -> Block 2 (500) leaves 83
        alloc_p2 = next(a for a in res.allocations if a["pid"] == "P2")
        self.assertEqual(alloc_p2["block_id"], 2)
        self.assertEqual(alloc_p2["remaining_block_kb"], 83)

        # P3 (112) -> Block 3 (200) leaves 88
        alloc_p3 = next(a for a in res.allocations if a["pid"] == "P3")
        self.assertEqual(alloc_p3["block_id"], 3)
        self.assertEqual(alloc_p3["remaining_block_kb"], 88)

        # P4 (426) -> Block 5 (600) leaves 174
        alloc_p4 = next(a for a in res.allocations if a["pid"] == "P4")
        self.assertEqual(alloc_p4["block_id"], 5)
        self.assertEqual(alloc_p4["remaining_block_kb"], 174)

        self.assertEqual(res.total_allocated_kb, 212 + 417 + 112 + 426)
        self.assertAlmostEqual(res.memory_utilization, (1167 / 1700) * 100, places=1)

    # 8. Worst Fit Blueprint
    def test_worst_fit_blueprint(self):
        """Verify Worst Fit allocates to largest block leaving largest remainder."""
        res = worst_fit(self.blocks, self.requests_tuples)
        self.assertEqual(res.algorithm, "Worst Fit")
        self.assertEqual(res.successful_allocations, 3)
        self.assertEqual(res.failed_allocations, 1)

        # P1 (212) -> Block 5 (600) leaves 388
        alloc_p1 = next(a for a in res.allocations if a["pid"] == "P1")
        self.assertEqual(alloc_p1["block_id"], 5)
        self.assertEqual(alloc_p1["remaining_block_kb"], 388)

        # P2 (417) -> Block 2 (500) leaves 83
        alloc_p2 = next(a for a in res.allocations if a["pid"] == "P2")
        self.assertEqual(alloc_p2["block_id"], 2)
        self.assertEqual(alloc_p2["remaining_block_kb"], 83)

        # P3 (112) -> remaining of Block 5 (388) leaves 276
        alloc_p3 = next(a for a in res.allocations if a["pid"] == "P3")
        self.assertEqual(alloc_p3["block_id"], 5)
        self.assertEqual(alloc_p3["remaining_block_kb"], 276)

        # P4 (426) -> fails because largest free block is 300 < 426
        self.assertIn("P4", res.unallocated_processes)
        self.assertEqual(res.external_fragmentation_kb, 959)

    # 9. Support raw integers list for requests
    def test_raw_integers_request_list(self):
        """Verify requests can be passed as simple list of ints [212, 417, 112, 426]."""
        res = first_fit(self.blocks, self.requests_raw)
        self.assertEqual(len(res.allocations), 3)
        self.assertEqual(res.allocations[0]["pid"], "P1")
        self.assertEqual(res.allocations[1]["pid"], "P2")
        self.assertEqual(res.allocations[2]["pid"], "P3")
        self.assertIn("P4", res.unallocated_processes)

    # 10. Repeated Allocation in Same Block
    def test_repeated_allocation_in_same_block(self):
        """Verify a block can be repeatedly split across multiple allocations."""
        blocks = [1000]
        requests = [("P1", 200), ("P2", 300), ("P3", 400)]
        res = first_fit(blocks, requests)
        self.assertEqual(res.successful_allocations, 3)
        self.assertEqual(res.total_allocated_kb, 900)
        self.assertEqual(res.total_free_memory_kb, 100)

    # 11. Independent Copies (No Mutation of Input Data)
    def test_independent_copies_no_mutation(self):
        """Verify executing algorithms does not mutate caller's original block/request lists."""
        orig_blocks = [100, 500, 200, 300, 600]
        orig_requests = [("P1", 212), ("P2", 417), ("P3", 112), ("P4", 426)]

        blocks_copy = copy.deepcopy(orig_blocks)
        requests_copy = copy.deepcopy(orig_requests)

        first_fit(blocks_copy, requests_copy)
        self.assertEqual(blocks_copy, orig_blocks, "first_fit mutated input blocks!")
        self.assertEqual(requests_copy, orig_requests, "first_fit mutated input requests!")

        best_fit(blocks_copy, requests_copy)
        self.assertEqual(blocks_copy, orig_blocks, "best_fit mutated input blocks!")

        worst_fit(blocks_copy, requests_copy)
        self.assertEqual(blocks_copy, orig_blocks, "worst_fit mutated input blocks!")

    # 12. Cross-Algorithm Comparison Driver
    def test_compare_memory_algorithms(self):
        """Verify comparison driver produces side-by-side metrics across all 3 algorithms."""
        comparison = compare_memory_algorithms(self.blocks, self.requests_tuples)
        self.assertEqual(len(comparison["results"]), 3)

        ff_res = comparison["results"]["First Fit"]
        bf_res = comparison["results"]["Best Fit"]
        wf_res = comparison["results"]["Worst Fit"]

        self.assertEqual(ff_res.successful_allocations, 3)
        self.assertEqual(bf_res.successful_allocations, 4)
        self.assertEqual(wf_res.successful_allocations, 3)

        # Best Fit achieved the highest allocation success rate (100%)
        self.assertEqual(comparison["best_algorithm"], "Best Fit")

    # 13. Validation Exceptions
    def test_empty_block_list(self):
        """Empty block list raises ValueError."""
        with self.assertRaises(ValueError):
            first_fit([], self.requests_tuples)

    def test_empty_process_list(self):
        """Empty request list raises ValueError."""
        with self.assertRaises(ValueError):
            first_fit(self.blocks, [])

    def test_zero_and_negative_sizes(self):
        """Zero and negative sizes raise ValueError."""
        with self.assertRaises(ValueError):
            first_fit([100, 0], self.requests_tuples)
        with self.assertRaises(ValueError):
            first_fit([100, -50], self.requests_tuples)
        with self.assertRaises(ValueError):
            first_fit(self.blocks, [("P1", -10)])
        with self.assertRaises(ValueError):
            first_fit(self.blocks, [("P1", 0)])

    # 14. Display Formatter
    def test_display_allocation(self):
        """Verify display_allocation output contains table and summaries."""
        res = first_fit(self.blocks, self.requests_tuples)
        table_str = display_allocation(res)
        self.assertIn("P1", table_str)
        self.assertIn("212 KB", table_str)
        self.assertIn("500 KB", table_str)
        self.assertIn("External Fragmentation", table_str)
        self.assertIn("Memory Utilization", table_str)


if __name__ == "__main__":
    unittest.main()
