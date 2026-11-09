import unittest
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.validators import DeadlockState
from modules.deadlock import (
    calculate_need,
    bankers_algorithm,
    check_safe_state,
    request_resources,
    display_safe_sequence,
)


def _verify_safe_sequence(state: DeadlockState, sequence: list[str]) -> bool:
    """Verifies that an execution sequence satisfies all Banker's safety invariants."""
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


class TestDeadlockManagement(unittest.TestCase):
    def setUp(self):
        # Blueprint page 4 & 7 standard workload
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
            process_ids=self.p_ids,
            resource_ids=self.r_ids,
            available=list(self.available),
            allocation=[list(r) for r in self.allocation],
            max_demand=[list(r) for r in self.max_demand],
        )

    def test_calculate_need_matrix(self):
        """Verify Need = Max - Allocation."""
        need = calculate_need(self.max_demand, self.allocation)
        self.assertEqual(need[0], [7, 4, 3])
        self.assertEqual(need[1], [1, 2, 2])
        self.assertEqual(need[2], [6, 0, 0])
        self.assertEqual(need[3], [0, 1, 1])
        self.assertEqual(need[4], [4, 3, 1])

    def test_bankers_algorithm_safe_state(self):
        """TC06: Verify safe state detection and valid safe sequence."""
        is_safe, seq = bankers_algorithm(self.state)
        self.assertTrue(is_safe)
        self.assertEqual(len(seq), 5)
        # Verify mathematically valid safe sequence
        self.assertTrue(_verify_safe_sequence(self.state, seq))
        self.assertEqual(seq[0], "P1")  # First process must be P1

    def test_bankers_algorithm_unsafe_state(self):
        """TC07: Verify detection of unsafe state."""
        # Restrict available resources so no process can complete
        unsafe_state = DeadlockState(
            process_ids=self.p_ids,
            resource_ids=self.r_ids,
            available=[0, 0, 0],
            allocation=[list(r) for r in self.allocation],
            max_demand=[list(r) for r in self.max_demand],
        )
        is_safe, seq = bankers_algorithm(unsafe_state)
        self.assertFalse(is_safe)
        self.assertEqual(seq, [])

    def test_dynamic_resource_request_granted(self):
        """Verify resource request algorithm grants safe request."""
        # P1 requests [1, 0, 2]
        granted, msg, seq = request_resources(self.state, "P1", [1, 0, 2])
        self.assertTrue(granted)
        self.assertIn("granted", msg.lower())
        self.assertTrue(len(seq) > 0)
        self.assertTrue(_verify_safe_sequence(self.state, seq))

    def test_dynamic_resource_request_exceeds_need(self):
        """Verify request exceeding declared max claim is rejected."""
        # P1's need is [1, 2, 2]. Request [2, 0, 0] exceeds need for resource A
        granted, msg, seq = request_resources(self.state, "P1", [2, 0, 0])
        self.assertFalse(granted)
        self.assertIn("exceed", msg.lower())

    def test_dynamic_resource_request_insufficient_available(self):
        """Verify request exceeding available resources must wait."""
        # Available is [3, 3, 2]. P0 requests [4, 0, 0]
        granted, msg, seq = request_resources(self.state, "P0", [4, 0, 0])
        self.assertFalse(granted)
        self.assertIn("wait", msg.lower())

    def test_display_safe_sequence(self):
        seq = ["P1", "P3", "P4", "P0", "P2"]
        seq_str = display_safe_sequence(seq)
        self.assertEqual(seq_str, "P1 -> P3 -> P4 -> P0 -> P2")


if __name__ == "__main__":
    unittest.main()
