"""
Zero-Dependency Native Web Server for OS Resource Management Simulator.
Implements an HTTP/1.1 API & Static Asset Server using Python's standard library.
Serves the publication-grade Black & White Web UI and provides computational endpoints.
"""

import argparse
import copy
import csv
from http import HTTPStatus
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import mimetypes
import os
from pathlib import Path
import sys
import threading
from typing import Any, Optional, Sequence
import urllib.parse

# Configure project root
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.logger import get_logger
from utils.validators import Process, DeadlockState, validate_process_list, validate_cylinder_requests
from modules.cpu_scheduling import (
    fcfs,
    sjf,
    round_robin,
    priority_scheduling,
    calculate_metrics as calc_cpu_metrics,
)
from modules.memory_management import (
    first_fit,
    best_fit,
    worst_fit,
    compare_memory_algorithms,
    MemoryAllocationResult,
)
from modules.deadlock import (
    calculate_need,
    bankers_algorithm,
    check_safe_state,
    request_resources,
    explain_safety_steps,
)
from modules.disk_scheduling import (
    fcfs_disk,
    sstf,
    scan,
    cscan,
    compare_disk_algorithms,
    DiskSchedulingResult,
)
from modules.reporting import (
    load_cpu_dataset,
    load_memory_dataset,
    load_disk_dataset,
    load_deadlock_dataset,
    RESULTS_DIR,
    CHARTS_DIR,
)

logger = get_logger()
WEB_DIR = PROJECT_ROOT / "web"


# ============================================================================
# SERIALIZATION HELPERS
# ============================================================================

def _serialize_process(p: Process) -> dict[str, Any]:
    return {
        "pid": p.pid,
        "arrival_time": p.arrival_time,
        "burst_time": p.burst_time,
        "priority": p.priority,
        "start_time": p.start_time,
        "completion_time": p.completion_time,
        "waiting_time": p.waiting_time,
        "turnaround_time": p.turnaround_time,
        "response_time": p.response_time,
        "remaining_time": p.remaining_time,
    }


def _serialize_memory_result(res: MemoryAllocationResult) -> dict[str, Any]:
    return {
        "algorithm": res.algorithm,
        "allocations": res.allocations,
        "unallocated_processes": res.unallocated_processes,
        "total_memory_kb": res.total_memory_kb,
        "total_allocated_kb": res.total_allocated_kb,
        "total_free_memory_kb": res.total_free_memory_kb,
        "successful_allocations": res.successful_allocations,
        "failed_allocations": res.failed_allocations,
        "memory_utilization": res.memory_utilization,
        "external_fragmentation_kb": res.external_fragmentation_kb,
        "internal_fragmentation_kb": res.internal_fragmentation_kb,
        "remaining_blocks": res.remaining_blocks,
    }


def _serialize_disk_result(res: DiskSchedulingResult) -> dict[str, Any]:
    return {
        "algorithm": res.algorithm,
        "initial_head": res.initial_head,
        "seek_sequence": res.seek_sequence,
        "service_sequence": res.service_sequence,
        "step_movements": res.step_movements,
        "total_head_movement": res.total_head_movement,
        "average_head_movement": res.average_head_movement,
        "requests_serviced": res.requests_serviced,
        "direction": res.direction,
        "total_cylinders": res.total_cylinders,
    }


def _read_csv_as_dicts(csv_path: Path) -> list[dict[str, str]]:
    if not csv_path.exists():
        return []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


# ============================================================================
# HTTP REQUEST HANDLER
# ============================================================================

class OSSimulatorHTTPHandler(BaseHTTPRequestHandler):
    """Zero-dependency HTTP handler for simulator API and static assets."""

    server_version = "OS-Simulator-NativeServer/2.0"

    def log_message(self, format: str, *args: Any) -> None:
        # Suppress noisy standard HTTP access logs or route to our logger
        pass

    def _send_json(self, data: Any, status: int = 200) -> None:
        payload = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(payload)

    def _send_error(self, message: str, status: int = 400) -> None:
        self._send_json({"error": message, "status": status}, status=status)

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        # Static Assets
        if path == "/" or path == "/index.html":
            return self._serve_static_file(WEB_DIR / "index.html", "text/html; charset=utf-8")
        if path == "/styles.css":
            return self._serve_static_file(WEB_DIR / "styles.css", "text/css; charset=utf-8")
        if path == "/app.js":
            return self._serve_static_file(WEB_DIR / "app.js", "application/javascript; charset=utf-8")

        # Static folders: charts, results
        if path.startswith("/charts/"):
            rel_name = path[len("/charts/"):]
            file_path = CHARTS_DIR / rel_name
            return self._serve_static_file(file_path, "image/png")

        if path.startswith("/results/"):
            rel_name = path[len("/results/"):]
            file_path = RESULTS_DIR / rel_name
            return self._serve_static_file(file_path, "text/csv; charset=utf-8")

        # API Endpoints
        if path == "/api/presets":
            return self._handle_get_presets(query)
        if path == "/api/benchmarks":
            return self._handle_get_benchmarks()
        if path == "/api/logs":
            return self._handle_get_logs(query)
        if path == "/api/test-cases":
            return self._handle_get_test_cases(query)
        if path == "/api/health":
            return self._send_json({"status": "healthy", "service": "OS Resource Simulator"})

        self._send_error(f"Path not found: {path}", status=404)

    def do_POST(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        try:
            content_len = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_len) if content_len > 0 else b"{}"
            data = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception as e:
            return self._send_error(f"Invalid JSON payload: {str(e)}", status=400)

        try:
            if path == "/api/cpu/run":
                return self._handle_cpu_run(data)
            elif path == "/api/memory/run":
                return self._handle_memory_run(data)
            elif path == "/api/deadlock/run":
                return self._handle_deadlock_run(data)
            elif path == "/api/disk/run":
                return self._handle_disk_run(data)
            else:
                self._send_error(f"Unknown POST endpoint: {path}", status=404)
        except Exception as e:
            logger.error(f"API execution error on {path}: {str(e)}", exc_info=True)
            self._send_error(f"Execution error: {str(e)}", status=500)

    # ------------------------------------------------------------------------
    # STATIC FILE HANDLER
    # ------------------------------------------------------------------------
    def _serve_static_file(self, file_path: Path, content_type: str) -> None:
        if not file_path.exists() or not file_path.is_file():
            self._send_error(f"File not found: {file_path.name}", status=404)
            return

        try:
            content = file_path.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self._send_error(f"Failed to read file: {str(e)}", status=500)

    # ------------------------------------------------------------------------
    # API ENDPOINT HANDLERS
    # ------------------------------------------------------------------------
    def _handle_get_presets(self, query: dict[str, list[str]]) -> None:
        tier = query.get("tier", ["normal"])[0].lower()
        if tier not in ("normal", "small", "large", "edge"):
            tier = "normal"

        try:
            # CPU preset
            cpu_procs = load_cpu_dataset(tier)
            cpu_data = [
                {"pid": p.pid, "arrival_time": p.arrival_time, "burst_time": p.burst_time, "priority": p.priority}
                for p in cpu_procs
            ]

            # Memory preset
            mem_blocks, mem_reqs = load_memory_dataset(tier)
            mem_data = {
                "blocks": mem_blocks,
                "requests": [[pid, sz] for pid, sz in mem_reqs],
            }

            # Deadlock preset
            dl_state, dl_req = load_deadlock_dataset(tier)
            dl_data = {
                "process_ids": dl_state.process_ids,
                "resource_ids": dl_state.resource_ids,
                "available": dl_state.available,
                "allocation": dl_state.allocation,
                "max_demand": dl_state.max_demand,
                "need": dl_state.need,
                "sample_request": {"pid": dl_req[0], "resources": dl_req[1]},
            }

            # Disk preset
            disk_reqs = load_disk_dataset(tier)
            disk_data = {
                "requests": disk_reqs,
                "initial_head": 53,
                "direction": "up",
                "total_cylinders": 200,
            }

            self._send_json({
                "tier": tier,
                "cpu": cpu_data,
                "memory": mem_data,
                "deadlock": dl_data,
                "disk": disk_data,
            })
        except Exception as e:
            self._send_error(f"Failed to load presets for tier '{tier}': {str(e)}", status=500)

    def _handle_get_benchmarks(self) -> None:
        result = {
            "cpu_results": _read_csv_as_dicts(RESULTS_DIR / "cpu_results.csv"),
            "memory_results": _read_csv_as_dicts(RESULTS_DIR / "memory_results.csv"),
            "deadlock_results": _read_csv_as_dicts(RESULTS_DIR / "deadlock_results.csv"),
            "disk_results": _read_csv_as_dicts(RESULTS_DIR / "disk_results.csv"),
            "cpu_workloads": _read_csv_as_dicts(RESULTS_DIR / "cpu_workloads_comparison.csv"),
            "memory_workloads": _read_csv_as_dicts(RESULTS_DIR / "memory_workloads_comparison.csv"),
            "disk_workloads": _read_csv_as_dicts(RESULTS_DIR / "disk_workloads_comparison.csv"),
            "deadlock_workloads": _read_csv_as_dicts(RESULTS_DIR / "deadlock_workloads_comparison.csv"),
            "rr_sensitivity": _read_csv_as_dicts(RESULTS_DIR / "rr_quantum_sensitivity.csv"),
            "charts": [
                {"name": "Overall Analysis", "path": "/charts/overall_analysis.png"},
                {"name": "CPU Comparison", "path": "/charts/cpu_comparison.png"},
                {"name": "Memory Comparison", "path": "/charts/memory_comparison.png"},
                {"name": "Disk Comparison", "path": "/charts/disk_comparison.png"},
            ],
        }
        self._send_json(result)

    def _handle_get_logs(self, query: dict[str, list[str]]) -> None:
        count = int(query.get("count", ["50"])[0])
        level = query.get("level", ["ALL"])[0].upper()

        log_path = PROJECT_ROOT / "logs" / "activity.log"
        if not log_path.exists():
            return self._send_json({"logs": [], "total": 0})

        lines = log_path.read_text(encoding="utf-8").strip().split("\n")
        filtered = []
        for line in lines[-max(count * 3, 100):]:
            if not line.strip():
                continue
            if level == "ALL" or f"[{level}]" in line:
                filtered.append(line)

        filtered = filtered[-count:]
        self._send_json({"logs": filtered, "total": len(lines)})

    def _handle_get_test_cases(self, query: dict[str, list[str]]) -> None:
        csv_p = PROJECT_ROOT / "Phase_4_Testing" / "test_results.csv"
        cases = _read_csv_as_dicts(csv_p)
        self._send_json({"total": len(cases), "cases": cases})

    # ------------------------------------------------------------------------
    # COMPUTATIONAL ALGORITHM RUNNERS
    # ------------------------------------------------------------------------
    def _handle_cpu_run(self, data: dict[str, Any]) -> None:
        raw_procs = data.get("processes", [])
        if not raw_procs:
            return self._send_error("Process list cannot be empty.")

        processes = []
        for p in raw_procs:
            processes.append(
                Process(
                    pid=str(p.get("pid", "")).strip(),
                    arrival_time=int(p.get("arrival_time", 0)),
                    burst_time=int(p.get("burst_time", 1)),
                    priority=int(p.get("priority", 1)),
                )
            )

        algo = str(data.get("algorithm", "fcfs")).lower().strip()
        quantum = int(data.get("quantum", 2))

        def _run_single(algo_name: str):
            if algo_name == "fcfs":
                procs, segs = fcfs(processes)
                name = "First-Come, First-Served (FCFS)"
            elif algo_name == "sjf":
                procs, segs = sjf(processes)
                name = "Shortest Job First (SJF)"
            elif algo_name in ("rr", "round_robin"):
                procs, segs = round_robin(processes, quantum=quantum)
                name = f"Round Robin (q={quantum})"
            elif algo_name == "priority":
                procs, segs = priority_scheduling(processes)
                name = "Priority Scheduling (Non-preemptive)"
            else:
                raise ValueError(f"Unknown CPU algorithm: {algo_name}")

            metrics = calc_cpu_metrics(procs, segs)
            timeline = [{"pid": s.pid, "start": s.start_time, "end": s.end_time, "duration": s.duration} for s in segs]
            return {
                "algorithm": name,
                "processes": [_serialize_process(p) for p in procs],
                "timeline": timeline,
                "metrics": metrics,
            }

        if algo == "all":
            results = {
                "fcfs": _run_single("fcfs"),
                "sjf": _run_single("sjf"),
                "rr": _run_single("rr"),
                "priority": _run_single("priority"),
            }
            self._send_json({"mode": "all", "results": results})
        else:
            res = _run_single(algo)
            self._send_json({"mode": "single", **res})

    def _handle_memory_run(self, data: dict[str, Any]) -> None:
        raw_blocks = data.get("blocks", [])
        raw_requests = data.get("requests", [])
        if not raw_blocks:
            return self._send_error("Memory blocks list cannot be empty.")
        if not raw_requests:
            return self._send_error("Memory requests list cannot be empty.")

        blocks = [int(b) for b in raw_blocks]
        requests = [(str(r[0]), int(r[1])) for r in raw_requests]
        algo = str(data.get("algorithm", "all")).lower().strip()

        if algo == "all":
            cmp_res = compare_memory_algorithms(blocks, requests)
            results_list = [_serialize_memory_result(r) for r in cmp_res["results"].values()]
            self._send_json({
                "mode": "all",
                "results": results_list,
                "comparison_table": cmp_res.get("comparison_table", []),
                "best_algorithm": cmp_res.get("best_algorithm", ""),
            })
        else:
            if algo in ("first_fit", "firstfit"):
                res = first_fit(blocks, requests)
            elif algo in ("best_fit", "bestfit"):
                res = best_fit(blocks, requests)
            elif algo in ("worst_fit", "worstfit"):
                res = worst_fit(blocks, requests)
            else:
                return self._send_error(f"Unknown memory algorithm: {algo}")

            self._send_json({"mode": "single", **_serialize_memory_result(res)})

    def _handle_deadlock_run(self, data: dict[str, Any]) -> None:
        pids = [str(p).strip() for p in data.get("process_ids", [])]
        rids = [str(r).strip() for r in data.get("resource_ids", [])]
        avail = [int(a) for a in data.get("available", [])]
        alloc = [[int(x) for x in row] for row in data.get("allocation", [])]
        max_d = [[int(x) for x in row] for row in data.get("max_demand", [])]

        if not pids or not rids or not avail or not alloc or not max_d:
            return self._send_error("Allocation, Max Demand, and Available structures cannot be empty.")

        need = calculate_need(max_d, alloc)
        state = DeadlockState(
            process_ids=pids,
            resource_ids=rids,
            available=avail,
            allocation=alloc,
            max_demand=max_d,
            need=need,
        )

        is_safe, sequence = bankers_algorithm(state)
        _, _, step_trace = explain_safety_steps(state)

        response_data: dict[str, Any] = {
            "is_safe": is_safe,
            "safe_sequence": sequence,
            "need": need,
            "available": avail,
            "steps": step_trace,
        }

        # Check for dynamic request
        req = data.get("request")
        if req and isinstance(req, dict) and "pid" in req and "resources" in req and req.get("pid"):
            req_pid = str(req["pid"]).strip()
            req_vector = [int(v) for v in req["resources"]]
            # Deepcopy to preserve original state
            req_state = copy.deepcopy(state)
            is_granted, msg, post_sequence = request_resources(req_state, req_pid, req_vector, commit=True)

            response_data["request_evaluation"] = {
                "pid": req_pid,
                "request_vector": req_vector,
                "decision": "GRANTED" if is_granted else "DENIED",
                "detail": msg,
                "post_safe": is_granted,
                "post_sequence": post_sequence,
                "post_available": req_state.available,
                "post_allocation": req_state.allocation,
                "post_need": req_state.need,
            }

        self._send_json(response_data)

    def _handle_disk_run(self, data: dict[str, Any]) -> None:
        raw_reqs = data.get("requests", [])
        if not raw_reqs:
            return self._send_error("Disk cylinder requests list cannot be empty.")

        requests = [int(r) for r in raw_reqs]
        initial_head = int(data.get("initial_head", 53))
        direction = str(data.get("direction", "up")).lower().strip()
        total_cylinders = int(data.get("total_cylinders", 200))
        algo = str(data.get("algorithm", "all")).lower().strip()

        if algo == "all":
            cmp_res = compare_disk_algorithms(requests, initial_head, total_cylinders=total_cylinders, direction=direction)
            self._send_json({
                "mode": "all",
                "results": [_serialize_disk_result(r) for r in cmp_res["results"].values()],
                "comparison_table": cmp_res.get("comparison_table", []),
                "best_algorithm": cmp_res.get("best_algorithm", ""),
            })
        else:
            if algo == "fcfs":
                res = fcfs_disk(requests, initial_head, total_cylinders)
            elif algo == "sstf":
                res = sstf(requests, initial_head, total_cylinders)
            elif algo == "scan":
                res = scan(requests, initial_head, direction, total_cylinders)
            elif algo in ("cscan", "c-scan"):
                res = cscan(requests, initial_head, direction, total_cylinders)
            else:
                return self._send_error(f"Unknown disk algorithm: {algo}")

            self._send_json({"mode": "single", **_serialize_disk_result(res)})


# ============================================================================
# SERVER RUNNER & CLI INTERFACE
# ============================================================================

def run_server(host: str = "127.0.0.1", port: int = 8501) -> None:
    server_address = (host, port)
    httpd = HTTPServer(server_address, OSSimulatorHTTPHandler)
    print("=" * 72)
    print(f"  OS RESOURCE MANAGEMENT SIMULATOR — NATIVE WEB SERVER")
    print("=" * 72)
    print(f"  [STATUS] Server running at: http://{host}:{port}/")
    print(f"  [ARCH]   Pure Zero-Dependency Python HTTP + HTML5/CSS3/Vanilla JS")
    print(f"  [THEME]  Black Major / White Minor Swiss Console Aesthetic")
    print(f"  [PRESS]  Ctrl+C to safely shut down server")
    print("=" * 72)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Interrupted by user. Closing server...")
    finally:
        httpd.server_close()
        print("[SHUTDOWN] Server stopped cleanly.")


def run_self_test() -> bool:
    """Verifies that all API endpoints function correctly in memory."""
    print("[TEST] Running self-test diagnostics on API logic...")
    # Test CPU
    procs = [Process(pid="P1", arrival_time=0, burst_time=5, priority=2)]
    completed, segs = fcfs(procs)
    assert len(completed) == 1
    assert completed[0].completion_time == 5
    print("  ✓ CPU Scheduling verified")

    # Test Memory
    m_res = first_fit([100, 500], [("P1", 200)])
    assert m_res.successful_allocations == 1
    print("  ✓ Memory Management verified")

    # Test Deadlock
    need = calculate_need([[3, 2, 2]], [[2, 0, 0]])
    st = DeadlockState(
        process_ids=["P1"],
        resource_ids=["A", "B", "C"],
        available=[1, 2, 2],
        allocation=[[2, 0, 0]],
        max_demand=[[3, 2, 2]],
        need=need,
    )
    is_safe, seq = bankers_algorithm(st)
    assert is_safe is True
    print("  ✓ Deadlock Banker's algorithm verified")

    # Test Disk
    d_res = fcfs_disk([98, 183], 53)
    assert d_res.total_head_movement > 0
    print("  ✓ Disk Scheduling verified")

    # Test datasets
    cpu_d = load_cpu_dataset("normal")
    assert len(cpu_d) > 0
    print("  ✓ Workload datasets verified")

    print("[SUCCESS] All self-test diagnostics passed cleanly.")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OS Simulator Native HTTP Web Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8501, help="Port to listen on (default: 8501)")
    parser.add_argument("--test", action="store_true", help="Execute self-test verification and exit")
    args = parser.parse_args()

    if args.test:
        success = run_self_test()
        sys.exit(0 if success else 1)
    else:
        run_server(args.host, args.port)
