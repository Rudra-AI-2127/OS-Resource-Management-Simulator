"""
Unit & Integration Test Suite for Native Web Server (server.py).
Verifies HTTP endpoints, static asset serving, and computational REST APIs.
Uses in-memory stream request handling to guarantee 100% cross-platform determinism
with zero network socket privilege requirements.
"""

import io
import json
from pathlib import Path
import sys
import unittest

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from server import OSSimulatorHTTPHandler


class MockClient:
    @staticmethod
    def request(method: str, path: str, body_obj=None):
        if body_obj is not None:
            if isinstance(body_obj, (dict, list)):
                body_bytes = json.dumps(body_obj).encode("utf-8")
            elif isinstance(body_obj, str):
                body_bytes = body_obj.encode("utf-8")
            else:
                body_bytes = bytes(body_obj)
        else:
            body_bytes = b""

        h = OSSimulatorHTTPHandler.__new__(OSSimulatorHTTPHandler)
        h.rfile = io.BytesIO(body_bytes)
        h.wfile = io.BytesIO()
        h.headers = {
            "Content-Length": str(len(body_bytes)),
            "Content-Type": "application/json",
        }
        h.path = path
        h.command = method
        h.requestline = f"{method} {path} HTTP/1.1"
        h.request_version = "HTTP/1.1"
        h.close_connection = False

        if method == "GET":
            h.do_GET()
        elif method == "POST":
            h.do_POST()
        elif method == "OPTIONS":
            h.do_OPTIONS()
        else:
            raise ValueError(f"Unsupported mock method: {method}")

        raw = h.wfile.getvalue().decode("utf-8", errors="replace")
        parts = raw.split("\r\n\r\n", 1)
        headers = parts[0]
        body = parts[1] if len(parts) > 1 else ""
        status_line = headers.splitlines()[0]
        status = int(status_line.split()[1])
        return status, body, headers


class TestNativeWebServer(unittest.TestCase):
    # ------------------------------------------------------------------------
    # STATIC ASSET TESTS
    # ------------------------------------------------------------------------
    def test_get_root_serves_html(self):
        status, body, headers = MockClient.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn("text/html", headers)
        self.assertIn("OS Resource Management Simulator", body)
        self.assertIn("CPU Scheduling", body)

    def test_get_styles_css(self):
        status, body, headers = MockClient.request("GET", "/styles.css")
        self.assertEqual(status, 200)
        self.assertIn("text/css", headers)
        self.assertIn("--bg-primary: #000000", body)

    def test_get_app_js(self):
        status, body, headers = MockClient.request("GET", "/app.js")
        self.assertEqual(status, 200)
        self.assertIn("application/javascript", headers)
        self.assertIn("OSSimulatorApp", body)

    def test_get_health(self):
        status, body, _ = MockClient.request("GET", "/api/health")
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertEqual(data.get("status"), "healthy")

    # ------------------------------------------------------------------------
    # API PRESETS & BENCHMARK TESTS
    # ------------------------------------------------------------------------
    def test_api_presets(self):
        status, body, _ = MockClient.request("GET", "/api/presets?tier=normal")
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertIn("cpu", data)
        self.assertIn("memory", data)
        self.assertIn("deadlock", data)
        self.assertIn("disk", data)
        self.assertGreater(len(data["cpu"]), 0)

    def test_api_benchmarks(self):
        status, body, _ = MockClient.request("GET", "/api/benchmarks")
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertIn("cpu_results", data)
        self.assertIn("memory_results", data)
        self.assertIn("deadlock_results", data)
        self.assertIn("disk_results", data)

    def test_api_test_cases(self):
        status, body, _ = MockClient.request("GET", "/api/test-cases")
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertEqual(data.get("total"), 77)
        self.assertEqual(len(data.get("cases")), 77)

    def test_api_logs(self):
        status, body, _ = MockClient.request("GET", "/api/logs?count=20&level=ALL")
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertIn("logs", data)

    # ------------------------------------------------------------------------
    # COMPUTATIONAL API ENDPOINT TESTS
    # ------------------------------------------------------------------------
    def test_cpu_run_fcfs(self):
        payload = {
            "algorithm": "fcfs",
            "processes": [
                {"pid": "P1", "arrival_time": 0, "burst_time": 5, "priority": 2},
                {"pid": "P2", "arrival_time": 1, "burst_time": 3, "priority": 1},
                {"pid": "P3", "arrival_time": 2, "burst_time": 8, "priority": 4},
                {"pid": "P4", "arrival_time": 3, "burst_time": 2, "priority": 3},
            ],
        }
        status, body, _ = MockClient.request("POST", "/api/cpu/run", payload)
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertEqual(data["mode"], "single")
        self.assertEqual(data["metrics"]["avg_waiting_time"], 5.75)
        self.assertEqual(data["metrics"]["avg_turnaround_time"], 10.25)
        self.assertEqual(len(data["timeline"]), 4)

    def test_cpu_run_all(self):
        payload = {
            "algorithm": "all",
            "quantum": 2,
            "processes": [
                {"pid": "P1", "arrival_time": 0, "burst_time": 4, "priority": 1},
            ],
        }
        status, body, _ = MockClient.request("POST", "/api/cpu/run", payload)
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertEqual(data["mode"], "all")
        self.assertIn("fcfs", data["results"])
        self.assertIn("sjf", data["results"])
        self.assertIn("rr", data["results"])
        self.assertIn("priority", data["results"])

    def test_memory_run_best_fit(self):
        payload = {
            "algorithm": "best_fit",
            "blocks": [100, 500, 200, 300, 600],
            "requests": [["P1", 212], ["P2", 417], ["P3", 112], ["P4", 426]],
        }
        status, body, _ = MockClient.request("POST", "/api/memory/run", payload)
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertEqual(data["successful_allocations"], 4)
        self.assertEqual(data["failed_allocations"], 0)
        self.assertEqual(data["internal_fragmentation_kb"], 0)

    def test_deadlock_run_bankers_and_request(self):
        payload = {
            "process_ids": ["P0", "P1", "P2", "P3", "P4"],
            "resource_ids": ["A", "B", "C"],
            "available": [3, 3, 2],
            "allocation": [
                [0, 1, 0],
                [2, 0, 0],
                [3, 0, 2],
                [2, 1, 1],
                [0, 0, 2],
            ],
            "max_demand": [
                [7, 5, 3],
                [3, 2, 2],
                [9, 0, 2],
                [2, 2, 2],
                [4, 3, 3],
            ],
            "request": {
                "pid": "P1",
                "resources": [1, 0, 2],
            },
        }
        status, body, _ = MockClient.request("POST", "/api/deadlock/run", payload)
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertTrue(data["is_safe"])
        self.assertEqual(data["safe_sequence"][0], "P1")
        self.assertIn("request_evaluation", data)
        self.assertEqual(data["request_evaluation"]["decision"], "GRANTED")

    def test_disk_run_sstf(self):
        payload = {
            "algorithm": "sstf",
            "initial_head": 53,
            "requests": [98, 183, 37, 122, 14, 124, 65, 67],
            "total_cylinders": 200,
        }
        status, body, _ = MockClient.request("POST", "/api/disk/run", payload)
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertEqual(data["total_head_movement"], 236)
        self.assertEqual(data["requests_serviced"], 8)

    def test_invalid_path_404(self):
        status, body, _ = MockClient.request("GET", "/invalid_endpoint")
        self.assertEqual(status, 404)

    def test_invalid_payload_400(self):
        status, body, _ = MockClient.request("POST", "/api/cpu/run", {"processes": []})
        self.assertEqual(status, 400)
        data = json.loads(body)
        self.assertIn("error", data)


if __name__ == "__main__":
    unittest.main()
