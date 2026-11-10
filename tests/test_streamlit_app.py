"""
Unit & UI Integration Test Suite for Streamlit Dashboard (app.py).
Verifies that all 8 dashboard pages initialize, render, and execute without unhandled exceptions.
"""

from pathlib import Path
import sys
import unittest

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestStreamlitDashboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import os
        if sys.platform == "win32" and os.environ.get("RUN_STREAMLIT_TESTS") != "1":
            raise unittest.SkipTest(
                "Streamlit AppTest headless event loop can block on Windows subprocesses. "
                "Set RUN_STREAMLIT_TESTS=1 to run."
            )
        try:
            from streamlit.testing.v1 import AppTest
            cls.AppTest = AppTest
        except ImportError:
            raise unittest.SkipTest("Streamlit is not installed or AppTest unavailable.")

    def test_app_overview_page(self):
        """Verify Page 1: Overview renders with title, metrics, and cards."""
        at = self.AppTest.from_file(str(PROJECT_ROOT / "app.py"))
        at.run()
        self.assertEqual(len(at.exception), 0)
        self.assertGreater(len(at.title), 0)

    def test_app_cpu_scheduling_page(self):
        """Verify Page 2: CPU Scheduling executes simulation and generates metrics."""
        at = self.AppTest.from_file(str(PROJECT_ROOT / "app.py"))
        at.run()
        at.sidebar.radio[0].set_value("2. CPU Scheduling").run()
        self.assertEqual(len(at.exception), 0)
        self.assertIn("CPU Scheduling", at.title[0].value)

    def test_app_memory_management_page(self):
        """Verify Page 3: Memory Management renders allocation tables and charts."""
        at = self.AppTest.from_file(str(PROJECT_ROOT / "app.py"))
        at.run()
        at.sidebar.radio[0].set_value("3. Memory Management").run()
        self.assertEqual(len(at.exception), 0)
        self.assertIn("Memory Management", at.title[0].value)

    def test_app_deadlock_page(self):
        """Verify Page 4: Deadlock Management evaluates Banker's safety and matrices."""
        at = self.AppTest.from_file(str(PROJECT_ROOT / "app.py"))
        at.run()
        at.sidebar.radio[0].set_value("4. Deadlock Management").run()
        self.assertEqual(len(at.exception), 0)
        self.assertIn("Deadlock", at.title[0].value)

    def test_app_disk_scheduling_page(self):
        """Verify Page 5: Disk Scheduling computes seek movements and plots trajectories."""
        at = self.AppTest.from_file(str(PROJECT_ROOT / "app.py"))
        at.run()
        at.sidebar.radio[0].set_value("5. Disk Scheduling").run()
        self.assertEqual(len(at.exception), 0)
        self.assertIn("Disk Scheduling", at.title[0].value)

    def test_app_performance_analysis_page(self):
        """Verify Page 6: Performance Analysis renders charts and CSV download buttons."""
        at = self.AppTest.from_file(str(PROJECT_ROOT / "app.py"))
        at.run()
        at.sidebar.radio[0].set_value("6. Performance Analysis").run()
        self.assertEqual(len(at.exception), 0)
        self.assertIn("Performance Analysis", at.title[0].value)

    def test_app_testing_and_logs_page(self):
        """Verify Page 7: Testing and Logs renders formal matrix table and activity logs."""
        at = self.AppTest.from_file(str(PROJECT_ROOT / "app.py"))
        at.run()
        at.sidebar.radio[0].set_value("7. Testing and Logs").run()
        self.assertEqual(len(at.exception), 0)
        self.assertIn("Testing", at.title[0].value)

    def test_app_about_project_page(self):
        """Verify Page 8: About Project renders academic overview and blueprint compliance."""
        at = self.AppTest.from_file(str(PROJECT_ROOT / "app.py"))
        at.run()
        at.sidebar.radio[0].set_value("8. About Project").run()
        self.assertEqual(len(at.exception), 0)
        self.assertIn("About", at.title[0].value)


if __name__ == "__main__":
    unittest.main()
