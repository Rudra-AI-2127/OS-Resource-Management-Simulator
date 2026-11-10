"""
Smoke test suite for OS Resource Management Simulator.
Verifies project bootstrap: module imports, directory structure, logging, and environment checks.
"""

import unittest
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestSmokeBootstrap(unittest.TestCase):
    def test_python_compatibility_function(self):
        """Verify check_python_compatibility runs without raising errors."""
        import main
        result = main.check_python_compatibility()
        self.assertIsInstance(result, bool)

    def test_module_imports(self):
        """Verify all core modules and utilities can be imported cleanly."""
        try:
            import modules.cpu_scheduling as cpu
            import modules.memory_management as mem
            import modules.deadlock as dlk
            import modules.disk_scheduling as dsk
            import utils.validators as val
            import utils.logger as log
            import utils.helpers as help_util
        except ImportError as e:
            self.fail(f"Module import failed: {e}")

    def test_project_directory_structure(self):
        """Verify all mandatory project directories exist."""
        mandatory_dirs = [
            "modules",
            "utils",
            "tests",
            "data",
            "results",
            "charts",
            "logs",
            "screenshots",
            "Phase_1_Design",
            "Phase_3_Analysis",
            "Phase_4_Testing",
        ]
        for d in mandatory_dirs:
            dir_path = PROJECT_ROOT / d
            self.assertTrue(dir_path.is_dir(), f"Missing required directory: {d}")

    def test_mandatory_files_exist(self):
        """Verify presence of bootstrap files."""
        mandatory_files = [
            "main.py",
            "run.sh",
            "run_tests.sh",
            "requirements.txt",
            ".gitignore",
        ]
        for f in mandatory_files:
            file_path = PROJECT_ROOT / f
            self.assertTrue(file_path.is_file(), f"Missing required file: {f}")

    def test_logging_initialization(self):
        """Verify logger initializes and records test entry."""
        from utils.logger import get_logger
        logger = get_logger()
        self.assertIsNotNone(logger)
        logger.info("Smoke test verification executed successfully.")
        log_file = PROJECT_ROOT / "logs" / "activity.log"
        self.assertTrue(log_file.is_file())


if __name__ == "__main__":
    unittest.main()
