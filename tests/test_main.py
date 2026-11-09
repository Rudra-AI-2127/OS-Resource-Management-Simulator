import unittest
from unittest.mock import patch
import sys
from pathlib import Path
from io import StringIO

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import main


class TestMainController(unittest.TestCase):
    @patch("builtins.input", side_effect=["6"])
    @patch("sys.stdout", new_callable=StringIO)
    def test_main_exit(self, mock_stdout, mock_input):
        """TC09: Verify menu exit option."""
        main.main()
        output = mock_stdout.getvalue()
        self.assertIn("OS RESOURCE MANAGEMENT", output)
        self.assertIn("Exiting OS Simulator", output)

    @patch("builtins.input", side_effect=["99", "6"])
    @patch("sys.stdout", new_callable=StringIO)
    def test_main_invalid_choice(self, mock_stdout, mock_input):
        """TC09: Verify invalid choice handling."""
        main.main()
        output = mock_stdout.getvalue()
        self.assertIn("Invalid choice", output)

    @patch("builtins.input", side_effect=["1", "5", "0", "6"])
    @patch("sys.stdout", new_callable=StringIO)
    def test_main_cpu_module_quick_run(self, mock_stdout, mock_input):
        """Verify CPU module execution through main menu."""
        main.main()
        output = mock_stdout.getvalue()
        self.assertIn("CPU SCHEDULING", output)


if __name__ == "__main__":
    unittest.main()
