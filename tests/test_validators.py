import unittest
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.validators import (
    validate_positive_int,
    validate_non_negative_int,
    validate_process_list,
    validate_memory_inputs,
    validate_bankers_matrix,
    validate_cylinder_requests,
    validate_menu_choice,
)


class TestValidators(unittest.TestCase):
    def test_validate_positive_int_valid(self):
        self.assertEqual(validate_positive_int(5, "Burst time"), 5)
        self.assertEqual(validate_positive_int("10", "Quantum"), 10)

    def test_validate_positive_int_invalid(self):
        with self.assertRaises(ValueError):
            validate_positive_int(0, "Burst time")
        with self.assertRaises(ValueError):
            validate_positive_int(-3, "Burst time")
        with self.assertRaises(ValueError):
            validate_positive_int("abc", "Burst time")

    def test_validate_non_negative_int_valid(self):
        self.assertEqual(validate_non_negative_int(0, "Arrival time"), 0)
        self.assertEqual(validate_non_negative_int(7, "Arrival time"), 7)
        self.assertEqual(validate_non_negative_int("4", "Priority"), 4)

    def test_validate_non_negative_int_invalid(self):
        with self.assertRaises(ValueError):
            validate_non_negative_int(-1, "Arrival time")
        with self.assertRaises(ValueError):
            validate_non_negative_int("xyz", "Arrival time")

    def test_validate_process_list_valid(self):
        raw = [
            {"pid": "P1", "arrival_time": 0, "burst_time": 5, "priority": 1},
            {"pid": "P2", "arrival_time": 1, "burst_time": 3, "priority": 2},
        ]
        processes = validate_process_list(raw)
        self.assertEqual(len(processes), 2)
        self.assertEqual(processes[0].pid, "P1")
        self.assertEqual(processes[1].burst_time, 3)

    def test_validate_process_list_empty(self):
        with self.assertRaises(ValueError):
            validate_process_list([])

    def test_validate_process_list_duplicate_pid(self):
        raw = [
            {"pid": "P1", "arrival_time": 0, "burst_time": 5},
            {"pid": "P1", "arrival_time": 2, "burst_time": 3},
        ]
        with self.assertRaises(ValueError):
            validate_process_list(raw)

    def test_validate_process_list_negative_values(self):
        raw = [{"pid": "P1", "arrival_time": -1, "burst_time": 5}]
        with self.assertRaises(ValueError):
            validate_process_list(raw)

        raw2 = [{"pid": "P1", "arrival_time": 0, "burst_time": 0}]
        with self.assertRaises(ValueError):
            validate_process_list(raw2)

    def test_validate_memory_inputs_valid(self):
        blocks = [100, 500, 200, 300, 600]
        requests = [("P1", 212), ("P2", 417), ("P3", 112), ("P4", 426)]
        valid_b, valid_r = validate_memory_inputs(blocks, requests)
        self.assertEqual(len(valid_b), 5)
        self.assertEqual(len(valid_r), 4)

    def test_validate_memory_inputs_empty(self):
        with self.assertRaises(ValueError):
            validate_memory_inputs([], [("P1", 100)])
        with self.assertRaises(ValueError):
            validate_memory_inputs([100], [])

    def test_validate_memory_inputs_non_positive(self):
        with self.assertRaises(ValueError):
            validate_memory_inputs([100, -50], [("P1", 100)])
        with self.assertRaises(ValueError):
            validate_memory_inputs([100], [("P1", 0)])

    def test_validate_bankers_matrix_valid(self):
        allocation = [
            [0, 1, 0],
            [2, 0, 0],
            [3, 0, 2],
            [2, 1, 1],
            [0, 0, 2],
        ]
        max_demand = [
            [7, 5, 3],
            [3, 2, 2],
            [9, 0, 2],
            [2, 2, 2],
            [4, 3, 3],
        ]
        available = [3, 3, 2]
        p_ids = ["P0", "P1", "P2", "P3", "P4"]
        r_ids = ["A", "B", "C"]
        state = validate_bankers_matrix(allocation, max_demand, available, p_ids, r_ids)
        self.assertEqual(len(state.need), 5)
        self.assertEqual(state.need[0], [7, 4, 3])

    def test_validate_bankers_matrix_allocation_exceeds_max(self):
        allocation = [[5, 2]]
        max_demand = [[4, 2]]
        available = [3, 3]
        with self.assertRaises(ValueError):
            validate_bankers_matrix(allocation, max_demand, available, ["P0"], ["A", "B"])

    def test_validate_bankers_matrix_dimension_mismatch(self):
        allocation = [[1, 2, 3]]
        max_demand = [[1, 2]]
        available = [1, 2]
        with self.assertRaises(ValueError):
            validate_bankers_matrix(allocation, max_demand, available, ["P0"], ["A", "B"])

    def test_validate_cylinder_requests_valid(self):
        reqs = [98, 183, 37, 122, 14, 124, 65, 67]
        valid_reqs, head, max_c, dir_str = validate_cylinder_requests(
            reqs, initial_head=53, total_cylinders=200, direction="up"
        )
        self.assertEqual(len(valid_reqs), 8)
        self.assertEqual(head, 53)
        self.assertEqual(max_c, 200)
        self.assertEqual(dir_str, "up")

    def test_validate_cylinder_requests_out_of_bounds(self):
        with self.assertRaises(ValueError):
            validate_cylinder_requests([98, 205], 53, 200)
        with self.assertRaises(ValueError):
            validate_cylinder_requests([98, -5], 53, 200)
        with self.assertRaises(ValueError):
            validate_cylinder_requests([98], initial_head=250, total_cylinders=200)

    def test_validate_cylinder_requests_empty(self):
        with self.assertRaises(ValueError):
            validate_cylinder_requests([], 53, 200)

    def test_validate_menu_choice(self):
        self.assertEqual(validate_menu_choice("1", 1, 6), 1)
        self.assertEqual(validate_menu_choice("6", 1, 6), 6)
        with self.assertRaises(ValueError):
            validate_menu_choice("0", 1, 6)
        with self.assertRaises(ValueError):
            validate_menu_choice("7", 1, 6)
        with self.assertRaises(ValueError):
            validate_menu_choice("abc", 1, 6)


if __name__ == "__main__":
    unittest.main()
