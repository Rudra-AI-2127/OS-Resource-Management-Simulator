"""
Comprehensive Unit Test Suite for Module 3: Deadlock Management (Banker's Algorithm).
Validates Dijkstra's Banker's Algorithm, Safe/Unsafe State Detection,
Dynamic Resource Request with Speculative Rollback, Dimension & Value Constraints,
Caller Immutability, and Step-by-step Safety Traces.
"""

import copy
import sys
import unittest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.validators import DeadlockState, validate_bankers_matrix
from modules.deadlock import (
    calculate_need,
    bankers_algorithm,
    check_safe_state,
    request_resources,
    display_safe_sequence,
    format_deadlock_matrices,
    explain_safety_steps,
)


def _verify_safe_sequence(state: DeadlockState, sequence: list[str]) -> bool:
    """
    Mathematically verifies that an execution sequence satisfies all Banker's safety invariants.
    Each process must have Need <= Work at the moment of dispatch, releasing Allocation back to Work.
    """
    if set(sequence) != set(state.process_ids) or len(sequence) != len(state.process_ids):
        return False

    work = list(state.available)
    p_map = {pid: idx for idx, pid in enumerate(state.process_ids)}

    for pid in sequence:
        idx = p_map[pid]
        for j in range(len(state.resource_ids)):
            if state.need[idx][j] > work[j]:
                return False
            work[j] += state.allocation[idx][j]
    return True


class TestDeadlockManagementExhaustive(unittest.TestCase):
    def setUp(self):
        """
        Blueprint & Silberschatz canonical 5-process, 3-resource system.
        Total System Capacity: A=10, B=5, C=7.
        Allocated: A=7, B=2, C=5.
        Available: A=3, B=3, C=2.
        """
        self.p_ids = ["P0", "P1", "P2", "P3", "P4"]
        self.r_ids = ["A", "B", "C"]
        self.allocation = [
            [0, 1, 0],
            [2, 0, 0],
            [3, 0, 2],
            [2, 1, 1],
            [0, 0, 2],
        ]
        self.max_demand = [
            [7, 5, 3],
            [3, 2, 2],
            [9, 0, 2],
            [2, 2, 2],
            [4, 3, 3],
        ]
        self.available = [3, 3, 2]
        self.state = DeadlockState(
            process_ids=list(self.p_ids),
            resource_ids=list(self.r_ids),
            available=list(self.available),
            allocation=[list(r) for r in self.allocation],
            max_demand=[list(r) for r in self.max_demand],
        )

    def test_calculate_need_matrix_valid(self):
        """Verify Need = Max - Allocation across all dimensions."""
        need = calculate_need(self.max_demand, self.allocation)
        expected_need = [
            [7, 4, 3],
            [1, 2, 2],
            [6, 0, 0],
            [0, 1, 1],
            [4, 3, 1],
        ]
        self.assertEqual(need, expected_need)

    def test_calculate_need_allocation_exceeds_max(self):
        """calculate_need raises ValueError when Allocation > Max Demand."""
        invalid_alloc = [
            [0, 1, 0],
            [4, 0, 0],  # Alloc 4 > Max 3
            [3, 0, 2],
            [2, 1, 1],
            [0, 0, 2],
        ]
        with self.assertRaises(ValueError) as ctx:
            calculate_need(self.max_demand, invalid_alloc)
        self.assertIn("exceeds Max Demand", str(ctx.exception))

    def test_calculate_need_dimension_mismatch(self):
        """calculate_need raises ValueError on mismatched row or column counts."""
        # Row count mismatch
        with self.assertRaises(ValueError):
            calculate_need(self.max_demand[:4], self.allocation)

        # Column count mismatch
        bad_alloc = [list(r) for r in self.allocation]
        bad_alloc[0] = [0, 1]  # 2 columns instead of 3
        with self.assertRaises(ValueError):
            calculate_need(self.max_demand, bad_alloc)

    def test_calculate_need_empty_matrices(self):
        """calculate_need raises ValueError on empty matrices."""
        with self.assertRaises(ValueError):
            calculate_need([], [])

        with self.assertRaises(ValueError):
            calculate_need([[1, 2]], [])

    def test_bankers_algorithm_known_safe_system(self):
        """TC06: Verify known safe system correctly identifies safe state and valid sequence."""
        is_safe, seq = bankers_algorithm(self.state)
        self.assertTrue(is_safe)
        self.assertTrue(check_safe_state(self.state))
        self.assertEqual(len(seq), 5)
        self.assertTrue(_verify_safe_sequence(self.state, seq))
        # P1 is the unique process whose Need [1, 2, 2] <= Available [3, 3, 2] initially
        self.assertEqual(seq[0], "P1")

    def test_bankers_algorithm_known_unsafe_system(self):
        """TC07: Verify unsafe state detection when available resources cannot satisfy any process."""
        unsafe_state = DeadlockState(
            process_ids=list(self.p_ids),
            resource_ids=list(self.r_ids),
            available=[0, 0, 0],
            allocation=[list(r) for r in self.allocation],
            max_demand=[list(r) for r in self.max_demand],
        )
        is_safe, seq = bankers_algorithm(unsafe_state)
        self.assertFalse(is_safe)
        self.assertFalse(check_safe_state(unsafe_state))
        self.assertEqual(seq, [])

    def test_multiple_possible_safe_sequences(self):
        """
        Verify that when multiple processes can finish simultaneously,
        any chosen branch remains mathematically valid.
        """
        # Configure a state where P0, P1, and P2 can all finish from the start
        multi_state = DeadlockState(
            process_ids=["P0", "P1", "P2"],
            resource_ids=["A", "B"],
            available=[5, 5],
            allocation=[[1, 1], [1, 1], [1, 1]],
            max_demand=[[2, 2], [2, 2], [2, 2]],
        )
        is_safe, seq = bankers_algorithm(multi_state)
        self.assertTrue(is_safe)
        self.assertEqual(len(seq), 3)
        self.assertTrue(_verify_safe_sequence(multi_state, seq))

    def test_dynamic_request_safely_granted(self):
        """Verify dynamic request that maintains safety is granted and state updated."""
        # P1 requests [1, 0, 2]
        # Initial Available: [3, 3, 2] -> New Available: [2, 3, 0]
        # Initial P1 Need: [1, 2, 2] -> New P1 Need: [0, 2, 0]
        # Initial P1 Alloc: [2, 0, 0] -> New P1 Alloc: [3, 0, 2]
        granted, msg, seq = request_resources(self.state, "P1", [1, 0, 2], commit=True)
        self.assertTrue(granted)
        self.assertIn("granted", msg.lower())
        self.assertEqual(self.state.available, [2, 3, 0])
        self.assertEqual(self.state.allocation[1], [3, 0, 2])
        self.assertEqual(self.state.need[1], [0, 2, 0])
        self.assertTrue(_verify_safe_sequence(self.state, seq))

    def test_dynamic_request_makes_system_unsafe_rollback(self):
        """
        Verify request that would transition system into an unsafe state is DENIED
        and original state remains completely untouched (rollback invariant).
        """
        # P4 requests [3, 3, 0].
        # P4 Need is [4, 3, 1], Available is [3, 3, 2].
        # 3 <= 4, 3 <= 3, 0 <= 1 -> Request <= Need.
        # 3 <= 3, 3 <= 3, 0 <= 2 -> Request <= Available.
        # But if allocated, Available becomes [0, 0, 2].
        # No process can finish with Work=[0, 0, 2].
        orig_available = list(self.state.available)
        orig_alloc = [list(r) for r in self.state.allocation]
        orig_need = [list(r) for r in self.state.need]

        granted, msg, seq = request_resources(self.state, "P4", [3, 3, 0])
        self.assertFalse(granted)
        self.assertIn("unsafe", msg.lower())
        self.assertEqual(seq, [])

        # Strict rollback verification: original state is unchanged
        self.assertEqual(self.state.available, orig_available)
        self.assertEqual(self.state.allocation, orig_alloc)
        self.assertEqual(self.state.need, orig_need)

    def test_dynamic_request_exceeds_need(self):
        """Verify request exceeding declared maximum claim is immediately rejected."""
        # P1 Need is [1, 2, 2]. Request [2, 0, 0] exceeds claim for resource A
        granted, msg, seq = request_resources(self.state, "P1", [2, 0, 0])
        self.assertFalse(granted)
        self.assertIn("exceeded its maximum claim", msg)
        self.assertEqual(seq, [])

    def test_dynamic_request_exceeds_available(self):
        """Verify request exceeding available resources must wait without state corruption."""
        # Available is [3, 3, 2]. P0 requests [4, 0, 0] (Need is [7, 4, 3])
        orig_available = list(self.state.available)
        granted, msg, seq = request_resources(self.state, "P0", [4, 0, 0])
        self.assertFalse(granted)
        self.assertIn("must wait", msg.lower())
        self.assertEqual(seq, [])
        self.assertEqual(self.state.available, orig_available)

    def test_request_resources_uncommitted_leaves_state_unchanged(self):
        """Verify that passing commit=False leaves the original state unchanged even if safe."""
        orig_available = list(self.state.available)
        granted, msg, seq = request_resources(self.state, "P1", [1, 0, 2], commit=False)
        self.assertTrue(granted)
        self.assertEqual(self.state.available, orig_available)

    def test_unknown_process_request(self):
        """Verify request from non-existent PID is rejected."""
        granted, msg, seq = request_resources(self.state, "P999", [1, 0, 0])
        self.assertFalse(granted)
        self.assertIn("not found", msg.lower())

    def test_mismatched_request_vector_length(self):
        """Verify request vector with wrong number of resources is rejected."""
        granted, msg, seq = request_resources(self.state, "P1", [1, 0])  # 2 instead of 3
        self.assertFalse(granted)
        self.assertIn("does not match", msg.lower())

    def test_negative_resource_values(self):
        """Verify negative values in Available, Allocation, or Request raise ValueError."""
        # Negative in Available
        with self.assertRaises(ValueError):
            validate_bankers_matrix(
                self.allocation, self.max_demand, [-1, 3, 2]
            )

        # Negative in Allocation
        bad_alloc = [list(r) for r in self.allocation]
        bad_alloc[0][0] = -1
        with self.assertRaises(ValueError):
            validate_bankers_matrix(
                bad_alloc, self.max_demand, self.available
            )

        # Negative in Request
        with self.assertRaises(ValueError):
            request_resources(self.state, "P1", [-1, 0, 0])

    def test_inconsistent_matrix_dimensions(self):
        """Verify matrix dimension inconsistencies are rejected."""
        # 4 rows in Max, 5 rows in Alloc
        with self.assertRaises(ValueError):
            validate_bankers_matrix(
                self.allocation, self.max_demand[:4], self.available
            )

        # Inconsistent row width
        bad_max = [list(r) for r in self.max_demand]
        bad_max[1] = [3, 2]  # Missing 3rd resource
        with self.assertRaises(ValueError):
            validate_bankers_matrix(
                self.allocation, bad_max, self.available
            )

    def test_allocation_exceeding_maximum_validation(self):
        """validate_bankers_matrix rejects any state where Allocation > Max Demand."""
        bad_alloc = [list(r) for r in self.allocation]
        bad_alloc[1][0] = 5  # Max is 3
        with self.assertRaises(ValueError) as ctx:
            validate_bankers_matrix(
                bad_alloc, self.max_demand, self.available
            )
        self.assertIn("Allocation exceeds Max Demand", str(ctx.exception))

    def test_zero_processes(self):
        """Empty process list raises ValueError."""
        with self.assertRaises(ValueError):
            validate_bankers_matrix([], [], [3, 3, 2])

    def test_zero_resource_types(self):
        """Empty resource list raises ValueError."""
        with self.assertRaises(ValueError):
            validate_bankers_matrix([[1]], [[2]], [])

    def test_display_safe_sequence(self):
        """Verify safe sequence formatting."""
        seq = ["P1", "P3", "P4", "P0", "P2"]
        seq_str = display_safe_sequence(seq)
        self.assertEqual(seq_str, "P1 -> P3 -> P4 -> P0 -> P2")

        unsafe_str = display_safe_sequence([])
        self.assertIn("UNSAFE", unsafe_str)

    def test_format_deadlock_matrices(self):
        """Verify ASCII matrix representation includes all tables and headers."""
        formatted = format_deadlock_matrices(self.state)
        self.assertIn("Alloc A", formatted)
        self.assertIn("Max B", formatted)
        self.assertIn("Need C", formatted)
        self.assertIn("Available Resources", formatted)
        self.assertIn("P0", formatted)
        self.assertIn("P4", formatted)

    def test_explain_safety_steps(self):
        """Verify step-by-step trace accurately logs Work and Finish vectors."""
        is_safe, seq, trace = explain_safety_steps(self.state)
        self.assertTrue(is_safe)
        self.assertTrue(len(trace) >= 6)
        self.assertIn("Step 0: Initial Work", trace[0])
        self.assertIn("Select P1", trace[1])
        self.assertIn("Conclusion: System is in a SAFE state", trace[-1])


if __name__ == "__main__":
    unittest.main()
