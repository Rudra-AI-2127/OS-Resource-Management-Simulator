"""
Integration Test Suite — OS Resource Management Simulator.
Verifies main application controller navigation, interactive menus,
submodule dispatches, input recovery without crash, and cross-module workflows.
"""

import io
import sys
import unittest
from unittest.mock import patch
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import main
from main import (
    main as run_app,
    check_python_compatibility,
    run_cpu_module,
    run_memory_module,
    run_deadlock_module,
    run_disk_module,
    run_reporting_module,
)


class TestApplicationIntegration(unittest.TestCase):
    def test_check_python_compatibility(self):
        """Verify Python runtime version checking returns boolean."""
        res = check_python_compatibility()
        self.assertIsInstance(res, bool)

    @patch("builtins.input", side_effect=["6"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_main_menu_clean_exit(self, mock_stdout, mock_input):
        """Verify selecting option 6 exits cleanly with goodbye message."""
        run_app()
        output = mock_stdout.getvalue()
        self.assertIn("OS RESOURCE MANAGEMENT SIMULATOR", output)
        self.assertIn("Exiting OS Simulator. Goodbye!", output)

    @patch("builtins.input", side_effect=["99", "abc", "6"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_main_menu_invalid_choice_recovery(self, mock_stdout, mock_input):
        """Verify invalid menu inputs are handled with friendly error and loop continues."""
        run_app()
        output = mock_stdout.getvalue()
        self.assertIn("Invalid choice. Please enter a number between 1 and 6.", output)
        self.assertIn("Exiting OS Simulator. Goodbye!", output)

    @patch("builtins.input", side_effect=["5", "6"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_main_menu_run_reporting_module(self, mock_stdout, mock_input):
        """Verify option 5 triggers reporting engine and returns to menu."""
        run_app()
        output = mock_stdout.getvalue()
        self.assertIn("MODULE 5: PERFORMANCE ANALYSIS & REPORTING", output)
        self.assertIn("CPU SCHEDULING BENCHMARK", output)
        self.assertIn("MEMORY ALLOCATION BENCHMARK", output)
        self.assertIn("DISK SCHEDULING BENCHMARK", output)

    @patch("builtins.input", side_effect=["1", "5", "0", "6"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_cpu_module_integration_all_preset(self, mock_stdout, mock_input):
        """Verify Option 1 (CPU Scheduling) runs all preset algorithms and returns to main menu."""
        run_app()
        output = mock_stdout.getvalue()
        self.assertIn("MODULE 1: CPU SCHEDULING", output)
        self.assertIn("FCFS RESULTS", output)
        self.assertIn("SJF (NON-PREEMPTIVE) RESULTS", output)
        self.assertIn("ROUND ROBIN RESULTS", output)
        self.assertIn("PRIORITY (NON-PREEMPTIVE) RESULTS", output)
        self.assertIn("Exiting OS Simulator. Goodbye!", output)

    @patch("builtins.input", side_effect=["2", "4", "0", "6"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_memory_module_integration_compare_preset(self, mock_stdout, mock_input):
        """Verify Option 2 (Memory Management) runs compare all on preset and returns."""
        run_app()
        output = mock_stdout.getvalue()
        self.assertIn("MODULE 2: MEMORY MANAGEMENT", output)
        self.assertIn("FIRST FIT", output)
        self.assertIn("BEST FIT", output)
        self.assertIn("WORST FIT", output)
        self.assertIn("MEMORY ALLOCATION COMPARISON SUMMARY", output)
        self.assertIn("Exiting OS Simulator. Goodbye!", output)

    @patch("builtins.input", side_effect=["3", "1", "0", "6"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_deadlock_module_integration_safety_check(self, mock_stdout, mock_input):
        """Verify Option 3 (Deadlock Management) runs safety check and returns."""
        run_app()
        output = mock_stdout.getvalue()
        self.assertIn("MODULE 3: DEADLOCK MANAGEMENT", output)
        self.assertIn("STEP-BY-STEP SAFETY TRACE", output)
        self.assertIn("System Status: SAFE", output)
        self.assertIn("Safe Sequence:", output)
        self.assertIn("Exiting OS Simulator. Goodbye!", output)

    @patch("builtins.input", side_effect=["4", "5", "0", "6"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_disk_module_integration_all_preset(self, mock_stdout, mock_input):
        """Verify Option 4 (Disk Scheduling) runs all algorithms and returns."""
        run_app()
        output = mock_stdout.getvalue()
        self.assertIn("MODULE 4: DISK SCHEDULING", output)
        self.assertIn("DISK SCHEDULING: FCFS", output)
        self.assertIn("DISK SCHEDULING: SSTF", output)
        self.assertIn("DISK SCHEDULING: SCAN", output)
        self.assertIn("DISK SCHEDULING: C-SCAN", output)
        self.assertIn("DISK SCHEDULING COMPARISON SUMMARY", output)
        self.assertIn("Exiting OS Simulator. Goodbye!", output)

    @patch("builtins.input", side_effect=[EOFError])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_main_menu_eof_handling(self, mock_stdout, mock_input):
        """Verify piped input EOF terminates cleanly without infinite error loop."""
        run_app()
        output = mock_stdout.getvalue()
        self.assertIn("Exiting OS Simulator. Goodbye!", output)


if __name__ == "__main__":
    unittest.main()
