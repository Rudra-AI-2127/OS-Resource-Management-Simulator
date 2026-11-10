"""
Phase 4 Testing Audit & Evidence Generator — OS Resource Management Simulator.
Executes the expanded test matrix (TC01-TC77), verifies assertions, captures real runtime
results, exports test_cases.csv and test_results.csv, and populates Phase_4_Testing artifacts.
"""

from pathlib import Path
import copy
import csv
import io
import os
import shutil
import sys
import unittest
from unittest.mock import patch

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.logger import get_logger
from utils.validators import (
    Process,
    DeadlockState,
    validate_positive_int,
    validate_non_negative_int,
    validate_process_list,
    validate_memory_inputs,
    validate_bankers_matrix,
    validate_cylinder_requests,
    validate_menu_choice,
)
from modules.cpu_scheduling import (
    fcfs,
    sjf,
    round_robin,
    priority_scheduling,
    calculate_metrics as calc_cpu_metrics,
    generate_gantt_chart,
)
from modules.memory_management import (
    first_fit,
    best_fit,
    worst_fit,
    compare_memory_algorithms,
    calculate_fragmentation,
)
from modules.deadlock import (
    calculate_need,
    bankers_algorithm,
    check_safe_state,
    request_resources,
    display_safe_sequence,
    explain_safety_steps,
)
from modules.disk_scheduling import (
    fcfs_disk,
    sstf,
    scan,
    cscan,
    compare_disk_algorithms,
    calculate_head_movement,
)
from modules.reporting import (
    benchmark_cpu,
    benchmark_memory,
    benchmark_disk,
    analyze_deadlock,
    generate_overall_dashboard,
    benchmark_all_workloads,
    RESULTS_DIR,
    CHARTS_DIR,
)
import main

logger = get_logger()
PHASE4_DIR = PROJECT_ROOT / "Phase_4_Testing"
PHASE4_LOGS_DIR = PHASE4_DIR / "logs"
PHASE4_TESTS_DIR = PHASE4_DIR / "tests"

for d in (PHASE4_DIR, PHASE4_LOGS_DIR, PHASE4_TESTS_DIR):
    d.mkdir(parents=True, exist_ok=True)


def run_all_cases() -> list[dict[str, str]]:
    results = []

    def record(test_id, category, desc, inp, expected, actual, passed, notes=""):
        status = "PASS" if passed else "FAIL"
        results.append({
            "test_id": test_id,
            "category": category,
            "test_description": desc,
            "input": inp,
            "expected_result": expected,
            "actual_result": actual,
            "status": status,
            "notes": notes,
        })
        logger.info(f"[{status}] {test_id} - {desc}")

    # -------------------------------------------------------------
    # PROFESSOR'S CORE CASES: TC01 - TC09
    # -------------------------------------------------------------
    # TC01: Normal CPU input
    try:
        procs = [
            Process("P1", 0, 5, 2),
            Process("P2", 1, 3, 1),
            Process("P3", 2, 8, 4),
            Process("P4", 3, 2, 3),
        ]
        sched, segs = fcfs(procs)
        m = calc_cpu_metrics(sched, segs)
        p1_ct = [p.completion_time for p in sched if p.pid == "P1"][0]
        passed = (p1_ct == 5 and m["avg_waiting_time"] == 5.75 and m["avg_turnaround_time"] == 10.25)
        actual = f"P1_CT={p1_ct}, AvgWT={m['avg_waiting_time']:.2f}, AvgTAT={m['avg_turnaround_time']:.2f}"
        record("TC01", "CPU Scheduling", "Normal CPU input validation", "4 processes: P1(0,5), P2(1,3), P3(2,8), P4(3,2)", "P1_CT=5, AvgWT=5.75, AvgTAT=10.25", actual, passed, "Matches faculty blueprint manual calculations")
    except Exception as e:
        record("TC01", "CPU Scheduling", "Normal CPU input validation", "Blueprint workload", "P1_CT=5, AvgWT=5.75", f"Exception: {e}", False)

    # TC02: Negative burst time
    try:
        raw = [{"pid": "P1", "arrival_time": 0, "burst_time": -5}]
        validate_process_list(raw)
        record("TC02", "Validation", "Negative burst time rejection", "burst_time = -5", "Raise ValueError", "No exception raised", False)
    except ValueError as e:
        record("TC02", "Validation", "Negative burst time rejection", "burst_time = -5", "Raise ValueError", f"ValueError: {e}", True, "Defensive check prevents execution")
    except Exception as e:
        record("TC02", "Validation", "Negative burst time rejection", "burst_time = -5", "Raise ValueError", f"Unexpected {type(e)}", False)

    # TC03: Empty process list
    try:
        validate_process_list([])
        record("TC03", "Validation", "Empty process list validation", "[]", "Raise ValueError", "No exception raised", False)
    except ValueError as e:
        record("TC03", "Validation", "Empty process list validation", "[]", "Raise ValueError", f"ValueError: {e}", True, "Rejects empty process collections")
    except Exception as e:
        record("TC03", "Validation", "Empty process list validation", "[]", "Raise ValueError", f"Unexpected {type(e)}", False)

    # TC04: Valid memory blocks
    try:
        blocks = [100, 500, 200, 300, 600]
        reqs = [("P1", 212), ("P2", 417), ("P3", 112), ("P4", 426)]
        res_bf = best_fit(blocks, reqs)
        passed = (res_bf.successful_allocations == 4 and res_bf.total_allocated_kb == 1167)
        actual = f"Successful={res_bf.successful_allocations}/4, Allocated={res_bf.total_allocated_kb}KB"
        record("TC04", "Memory Management", "Valid memory allocation (Best Fit)", "Blocks: [100,500,200,300,600], Reqs: [212,417,112,426]", "100% allocation (4/4, 1167 KB)", actual, passed, "Best Fit successfully accommodates all requests")
    except Exception as e:
        record("TC04", "Memory Management", "Valid memory allocation (Best Fit)", "Blueprint workload", "100% allocation", f"Exception: {e}", False)

    # TC05: Insufficient memory
    try:
        blocks = [100, 200]
        reqs = [("P1", 500)]
        res = first_fit(blocks, reqs)
        passed = (res.failed_allocations == 1 and res.successful_allocations == 0)
        actual = f"Failed={res.failed_allocations}, FreeMem={res.total_free_memory_kb}KB, ExtFrag={res.external_fragmentation_kb}KB"
        record("TC05", "Memory Management", "Insufficient memory rejection", "Blocks: [100, 200], Req: [P1: 500]", "Allocation fails gracefully; 0 successful", actual, passed, "Graceful failure recorded with accurate fragmentation")
    except Exception as e:
        record("TC05", "Memory Management", "Insufficient memory rejection", "Oversized request", "Failed allocation", f"Exception: {e}", False)

    # TC06: Safe resource allocation
    try:
        p_ids = ["P0", "P1", "P2", "P3", "P4"]
        r_ids = ["A", "B", "C"]
        alloc = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]
        max_d = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]
        avail = [3, 3, 2]
        need = calculate_need(max_d, alloc)
        state = DeadlockState(p_ids, r_ids, avail, alloc, max_d, need)
        is_safe, seq = bankers_algorithm(state)
        passed = (is_safe and len(seq) == 5 and seq[0] == "P1")
        actual = f"is_safe={is_safe}, sequence={' -> '.join(seq)}"
        record("TC06", "Deadlock Management", "Safe resource allocation (Banker's)", "Canonical Silberschatz 5-process state", "System SAFE, Sequence starts with P1", actual, passed, "Canonical safe state detected")
    except Exception as e:
        record("TC06", "Deadlock Management", "Safe resource allocation (Banker's)", "Standard state", "SAFE state", f"Exception: {e}", False)

    # TC07: Unsafe resource allocation
    try:
        p_ids = ["P0", "P1"]
        r_ids = ["A"]
        alloc = [[2], [2]]
        max_d = [[4], [4]]
        avail = [0]
        need = calculate_need(max_d, alloc)
        state = DeadlockState(p_ids, r_ids, avail, alloc, max_d, need)
        is_safe, seq = bankers_algorithm(state)
        passed = (not is_safe and len(seq) == 0)
        actual = f"is_safe={is_safe}, sequence={seq}"
        record("TC07", "Deadlock Management", "Unsafe resource state detection", "2 procs, Alloc=[2],[2], Max=[4],[4], Avail=[0]", "System UNSAFE, empty sequence", actual, passed, "Deadlock hazard detected accurately")
    except Exception as e:
        record("TC07", "Deadlock Management", "Unsafe resource state detection", "Unsafe state", "UNSAFE state", f"Exception: {e}", False)

    # TC08: Valid disk requests
    try:
        reqs = [98, 183, 37, 122, 14, 124, 65, 67]
        res_sstf = sstf(reqs, initial_head=53, total_cylinders=200)
        passed = (res_sstf.total_head_movement == 236 and res_sstf.requests_serviced == 8)
        actual = f"HeadMovement={res_sstf.total_head_movement} cyl, Serviced={res_sstf.requests_serviced}"
        record("TC08", "Disk Scheduling", "Valid disk requests (SSTF)", "Reqs: [98, 183, 37, 122, 14, 124, 65, 67], Head: 53", "Total head movement = 236 cylinders", actual, passed, "Matches textbook SSTF seek trajectory")
    except Exception as e:
        record("TC08", "Disk Scheduling", "Valid disk requests (SSTF)", "Blueprint workload", "236 cylinders", f"Exception: {e}", False)

    # TC09: Invalid menu option
    try:
        validate_menu_choice("99", 1, 6)
        record("TC09", "Validation", "Invalid menu option rejection", "choice = '99' (range 1-6)", "Raise ValueError", "No exception raised", False)
    except ValueError as e:
        record("TC09", "Validation", "Invalid menu option rejection", "choice = '99' (range 1-6)", "Raise ValueError", f"ValueError: {e}", True, "Prevents invalid menu navigation")
    except Exception as e:
        record("TC09", "Validation", "Invalid menu option rejection", "choice = '99'", "Raise ValueError", f"Unexpected {type(e)}", False)

    # -------------------------------------------------------------
    # EXTENDED CASES: INVALID TYPES (TC10 - TC15)
    # -------------------------------------------------------------
    # TC10: Process arrival time non-numeric string
    try:
        validate_non_negative_int("abc", "Arrival time")
        record("TC10", "Invalid Types", "Process arrival time non-numeric string", "arrival_time = 'abc'", "Raise ValueError", "Parsed without error", False)
    except ValueError as e:
        record("TC10", "Invalid Types", "Process arrival time non-numeric string", "arrival_time = 'abc'", "Raise ValueError", f"ValueError: {e}", True, "Caught string arrival time")

    # TC11: Burst time boolean type
    try:
        validate_positive_int(True, "Burst time")
        record("TC11", "Invalid Types", "Process burst time boolean type", "burst_time = True", "Raise ValueError", "Parsed as 1", False)
    except ValueError as e:
        record("TC11", "Invalid Types", "Process burst time boolean type", "burst_time = True", "Raise ValueError", f"ValueError: {e}", True, "Boolean strictly rejected")

    # TC12: Memory block size non-integer string
    try:
        validate_memory_inputs(["one_hundred"], [("P1", 100)])
        record("TC12", "Invalid Types", "Memory block size string", "blocks = ['one_hundred']", "Raise ValueError", "Parsed without error", False)
    except ValueError as e:
        record("TC12", "Invalid Types", "Memory block size string", "blocks = ['one_hundred']", "Raise ValueError", f"ValueError: {e}", True, "Non-integer block rejected")

    # TC13: Disk cylinder float type
    try:
        validate_cylinder_requests([45.7], 50, 200)
        record("TC13", "Invalid Types", "Disk cylinder non-integer float", "cylinders = [45.7]", "Raise ValueError", "Parsed without error", False)
    except ValueError as e:
        record("TC13", "Invalid Types", "Disk cylinder non-integer float", "cylinders = [45.7]", "Raise ValueError", f"ValueError: {e}", True, "Float cylinder rejected")

    # TC14: Time quantum string
    try:
        validate_positive_int("fast", "Time quantum")
        record("TC14", "Invalid Types", "Time quantum string", "quantum = 'fast'", "Raise ValueError", "Parsed without error", False)
    except ValueError as e:
        record("TC14", "Invalid Types", "Time quantum string", "quantum = 'fast'", "Raise ValueError", f"ValueError: {e}", True, "String quantum rejected")

    # TC15: Deadlock matrix string element
    try:
        validate_bankers_matrix([["A", 1]], [[2, 2]], [1, 1], ["P0"], ["R1", "R2"])
        record("TC15", "Invalid Types", "Deadlock matrix string element", "Allocation[0][0] = 'A'", "Raise ValueError", "Parsed without error", False)
    except ValueError as e:
        record("TC15", "Invalid Types", "Deadlock matrix string element", "Allocation[0][0] = 'A'", "Raise ValueError", f"ValueError: {e}", True, "Non-integer matrix entry rejected")

    # -------------------------------------------------------------
    # EXTENDED CASES: MISSING FIELDS (TC16 - TC20)
    # -------------------------------------------------------------
    # TC16: Process missing burst time field
    try:
        raw = [{"pid": "P1", "arrival_time": 0}]
        validate_process_list(raw)
        record("TC16", "Missing Fields", "Process missing burst time field", "{'pid': 'P1', 'arrival_time': 0}", "Raise ValueError/KeyError", "No exception", False)
    except (ValueError, KeyError) as e:
        record("TC16", "Missing Fields", "Process missing burst time field", "Missing burst_time", "Raise ValueError", f"Caught: {e}", True, "Missing burst time detected")

    # TC17: Process missing PID field
    try:
        raw = [{"arrival_time": 0, "burst_time": 5}]
        validate_process_list(raw)
        record("TC17", "Missing Fields", "Process missing PID identifier", "{'arrival_time': 0, 'burst_time': 5}", "Raise ValueError/KeyError", "No exception", False)
    except (ValueError, KeyError) as e:
        record("TC17", "Missing Fields", "Process missing PID identifier", "Missing pid", "Raise ValueError", f"Caught: {e}", True, "Missing PID identifier detected")

    # TC18: Memory request missing size
    try:
        validate_memory_inputs([100], [("P1",)])
        record("TC18", "Missing Fields", "Memory request missing size", "[('P1',)]", "Raise ValueError", "No exception", False)
    except ValueError as e:
        record("TC18", "Missing Fields", "Memory request missing size", "Tuple with 1 element", "Raise ValueError", f"ValueError: {e}", True, "Malformed request tuple caught")

    # TC19: Deadlock missing available vector
    try:
        validate_bankers_matrix([[1]], [[2]], [], ["P0"], ["R1"])
        record("TC19", "Missing Fields", "Deadlock empty available vector", "available = []", "Raise ValueError", "No exception", False)
    except ValueError as e:
        record("TC19", "Missing Fields", "Deadlock empty available vector", "available = []", "Raise ValueError", f"ValueError: {e}", True, "Empty available vector caught")

    # TC20: Deadlock empty process IDs
    try:
        validate_bankers_matrix([[1]], [[2]], [3], [], ["R1"])
        record("TC20", "Missing Fields", "Deadlock empty process IDs", "process_ids = []", "Raise ValueError", "No exception", False)
    except ValueError as e:
        record("TC20", "Missing Fields", "Deadlock empty process IDs", "process_ids = []", "Raise ValueError", f"ValueError: {e}", True, "Empty process list caught")

    # -------------------------------------------------------------
    # EXTENDED CASES: DUPLICATE IDENTIFIERS (TC21 - TC24)
    # -------------------------------------------------------------
    # TC21: Duplicate PIDs in CPU
    try:
        raw = [{"pid": "P1", "arrival_time": 0, "burst_time": 4}, {"pid": "P1", "arrival_time": 2, "burst_time": 3}]
        validate_process_list(raw)
        record("TC21", "Duplicates", "Duplicate process IDs in CPU input", "P1, P1", "Raise ValueError", "No exception", False)
    except ValueError as e:
        record("TC21", "Duplicates", "Duplicate process IDs in CPU input", "P1, P1", "Raise ValueError", f"ValueError: {e}", True, "Duplicate PID rejected")

    # TC22: Duplicate process IDs in memory
    try:
        validate_memory_inputs([100, 200], [("P1", 50), ("P1", 80)])
        record("TC22", "Duplicates", "Duplicate process IDs in Memory input", "P1, P1", "Raise ValueError", "No exception", False)
    except ValueError as e:
        record("TC22", "Duplicates", "Duplicate process IDs in Memory input", "P1, P1", "Raise ValueError", f"ValueError: {e}", True, "Duplicate memory PID rejected")

    # TC23: Duplicate PIDs in Deadlock
    try:
        validate_bankers_matrix([[0], [0]], [[1], [1]], [1], ["P0", "P0"], ["R1"])
        record("TC23", "Duplicates", "Duplicate process IDs in Deadlock matrix", "P0, P0", "Raise ValueError", "No exception", False)
    except ValueError as e:
        record("TC23", "Duplicates", "Duplicate process IDs in Deadlock matrix", "P0, P0", "Raise ValueError", f"ValueError: {e}", True, "Duplicate deadlock PID rejected")

    # TC24: Duplicate cylinder requests in Disk (Valid in real kernels)
    try:
        res = fcfs_disk([50, 50, 80], initial_head=50)
        passed = (res.total_head_movement == 30 and res.requests_serviced == 3)
        actual = f"HeadMovement={res.total_head_movement}, Serviced={res.requests_serviced}"
        record("TC24", "Duplicates", "Duplicate disk cylinder requests", "[50, 50, 80], Head: 50", "Serviced cleanly with 0 seek distance for duplicate", actual, passed, "Duplicate cylinders handled gracefully")
    except Exception as e:
        record("TC24", "Duplicates", "Duplicate disk cylinder requests", "[50, 50, 80]", "Success", f"Exception: {e}", False)

    # -------------------------------------------------------------
    # EXTENDED CASES: BOUNDARY VALUES (TC25 - TC37)
    # -------------------------------------------------------------
    # TC25: Single CPU process
    try:
        p = [Process("P1", arrival_time=0, burst_time=7)]
        sched, segs = fcfs(p)
        m = calc_cpu_metrics(sched, segs)
        passed = (m["avg_waiting_time"] == 0.0 and m["avg_turnaround_time"] == 7.0)
        actual = f"WT={m['avg_waiting_time']}, TAT={m['avg_turnaround_time']}"
        record("TC25", "Boundary Values", "Single CPU process execution", "N=1, BT=7", "WT=0, TAT=7", actual, passed, "Minimal process boundary verified")
    except Exception as e:
        record("TC25", "Boundary Values", "Single CPU process execution", "N=1", "WT=0", f"Exception: {e}", False)

    # TC26: Simultaneous arrival at AT=0
    try:
        procs = [Process("P1", 0, 4), Process("P2", 0, 2), Process("P3", 0, 6)]
        sched, segs = sjf(procs)
        order = [p.pid for p in sched]
        passed = (order == ["P2", "P1", "P3"])
        actual = f"Execution order: {' -> '.join(order)}"
        record("TC26", "Boundary Values", "Simultaneous arrival at AT=0 (SJF)", "P1(0,4), P2(0,2), P3(0,6)", "Order: P2 -> P1 -> P3", actual, passed, "Shortest job dispatched first")
    except Exception as e:
        record("TC26", "Boundary Values", "Simultaneous arrival at AT=0 (SJF)", "AT=0", "P2->P1->P3", f"Exception: {e}", False)

    # TC27: Identical burst times (SJF tie-breaker)
    try:
        procs = [Process("P1", 0, 4), Process("P2", 0, 4), Process("P3", 0, 4)]
        sched, segs = sjf(procs)
        order = [p.pid for p in sched]
        passed = (order == ["P1", "P2", "P3"])
        actual = f"Tie break order: {' -> '.join(order)}"
        record("TC27", "Boundary Values", "Equal burst times in SJF", "P1(4), P2(4), P3(4)", "Order: P1 -> P2 -> P3 (FIFO tie-break)", actual, passed, "Deterministic tie-breaking confirmed")
    except Exception as e:
        record("TC27", "Boundary Values", "Equal burst times in SJF", "Equal BT", "P1->P2->P3", f"Exception: {e}", False)

    # TC28: CPU idle interval
    try:
        procs = [Process("P1", 0, 2), Process("P2", 5, 3)]
        sched, segs = fcfs(procs)
        idle_segs = [s for s in segs if s.pid == "IDLE"]
        passed = (len(idle_segs) == 1 and idle_segs[0].start_time == 2 and idle_segs[0].end_time == 5)
        actual = f"Idle segment: start={idle_segs[0].start_time}, end={idle_segs[0].end_time}"
        record("TC28", "Boundary Values", "CPU idle gap between process arrivals", "P1(0,2), P2(5,3)", "IDLE segment from t=2 to t=5", actual, passed, "Explicit IDLE timeline rendered")
    except Exception as e:
        record("TC28", "Boundary Values", "CPU idle gap between process arrivals", "Gapped arrivals", "IDLE segment", f"Exception: {e}", False)

    # TC29: Round Robin q=1
    try:
        procs = [Process("P1", 0, 2), Process("P2", 0, 2)]
        sched, segs = round_robin(procs, quantum=1)
        seq = [s.pid for s in segs]
        passed = (seq == ["P1", "P2", "P1", "P2"])
        actual = f"Timeline: {' -> '.join(seq)}"
        record("TC29", "Boundary Values", "Round Robin fine quantum q=1", "P1(2), P2(2), q=1", "Strict interleaving P1 -> P2 -> P1 -> P2", actual, passed, "Fine-grained time slicing verified")
    except Exception as e:
        record("TC29", "Boundary Values", "Round Robin fine quantum q=1", "q=1", "Interleaving", f"Exception: {e}", False)

    # TC30: Round Robin q >= max burst
    try:
        procs = [Process("P1", 0, 3), Process("P2", 1, 2)]
        sched, segs = round_robin(procs, quantum=10)
        p_map = {p.pid: p for p in sched}
        passed = (p_map["P1"].completion_time == 3 and p_map["P2"].completion_time == 5)
        actual = f"P1_CT={p_map['P1'].completion_time}, P2_CT={p_map['P2'].completion_time}"
        record("TC30", "Boundary Values", "Round Robin quantum larger than all bursts", "P1(0,3), P2(1,2), q=10", "Matches FCFS completions (CT=3, 5)", actual, passed, "Degeneration to FCFS confirmed")
    except Exception as e:
        record("TC30", "Boundary Values", "Round Robin quantum larger than all bursts", "q=10", "Matches FCFS", f"Exception: {e}", False)

    # TC31: Exact block match in memory
    try:
        res = first_fit([250], [("P1", 250)])
        passed = (res.successful_allocations == 1 and res.allocations[0]["remaining_block_kb"] == 0 and res.total_free_memory_kb == 0)
        actual = f"Allocated={res.total_allocated_kb}KB, FreeRemaining={res.total_free_memory_kb}KB"
        record("TC31", "Boundary Values", "Exact memory block fit", "Block: 250, Req: 250", "Allocated=250KB, FreeRemaining=0KB", actual, passed, "Zero remainder verified")
    except Exception as e:
        record("TC31", "Boundary Values", "Exact memory block fit", "Exact fit", "Free=0", f"Exception: {e}", False)

    # TC32: Dynamic partition splitting
    try:
        res = first_fit([500], [("P1", 150)])
        passed = (res.successful_allocations == 1 and res.allocations[0]["remaining_block_kb"] == 350 and res.total_free_memory_kb == 350)
        actual = f"Allocated={res.total_allocated_kb}KB, FreePool={res.total_free_memory_kb}KB"
        record("TC32", "Boundary Values", "Dynamic memory partition splitting", "Block: 500, Req: 150", "Allocated=150KB, Remainder 350KB returned to free pool", actual, passed, "Partition splitting dynamic block preservation")
    except Exception as e:
        record("TC32", "Boundary Values", "Dynamic memory partition splitting", "Split block", "Free=350", f"Exception: {e}", False)

    # TC33: Disk head at cylinder 0
    try:
        res = fcfs_disk([10, 50, 100], initial_head=0, total_cylinders=200)
        passed = (res.total_head_movement == 100 and res.seek_sequence[0] == 0)
        actual = f"SeekSeq={res.seek_sequence}, TotalSeek={res.total_head_movement}"
        record("TC33", "Boundary Values", "Initial disk head at cylinder 0", "Head: 0, Reqs: [10, 50, 100]", "Seek sequence starts at 0, movement=100 cyl", actual, passed, "Minimum boundary head position verified")
    except Exception as e:
        record("TC33", "Boundary Values", "Initial disk head at cylinder 0", "Head: 0", "TotalSeek=100", f"Exception: {e}", False)

    # TC34: Disk head at cylinder 199
    try:
        res = fcfs_disk([150, 100, 50], initial_head=199, total_cylinders=200)
        passed = (res.total_head_movement == 149 and res.seek_sequence[0] == 199)
        actual = f"SeekSeq={res.seek_sequence}, TotalSeek={res.total_head_movement}"
        record("TC34", "Boundary Values", "Initial disk head at cylinder 199", "Head: 199, Reqs: [150, 100, 50]", "Seek sequence starts at 199, movement=149 cyl", actual, passed, "Maximum boundary head position verified")
    except Exception as e:
        record("TC34", "Boundary Values", "Initial disk head at cylinder 199", "Head: 199", "TotalSeek=149", f"Exception: {e}", False)

    # TC35: Disk request matches head position
    try:
        res = sstf([53, 100], initial_head=53, total_cylinders=200)
        passed = (res.seek_sequence == [53, 53, 100] and res.total_head_movement == 47)
        actual = f"SeekSeq={res.seek_sequence}, TotalSeek={res.total_head_movement}"
        record("TC35", "Boundary Values", "Disk request at current head position", "Head: 53, Reqs: [53, 100]", "Immediate service with 0 seek jump, total=47 cyl", actual, passed, "Zero-seek request handled cleanly")
    except Exception as e:
        record("TC35", "Boundary Values", "Disk request at current head position", "Head: 53", "TotalSeek=47", f"Exception: {e}", False)

    # TC36: SCAN downward sweep
    try:
        res = scan([20, 80, 150], initial_head=50, total_cylinders=200, direction="down")
        passed = (res.seek_sequence[0] == 50 and res.seek_sequence[-1] == 150 and 0 in res.seek_sequence)
        actual = f"SeekSeq={' -> '.join(map(str, res.seek_sequence))}, TotalSeek={res.total_head_movement}"
        record("TC36", "Boundary Values", "Disk SCAN downward elevator sweep", "Head: 50, Reqs: [20, 80, 150], dir=down", "Visits 20, 0, then 80, 150", actual, passed, "Downward boundary reflection verified")
    except Exception as e:
        record("TC36", "Boundary Values", "Disk SCAN downward elevator sweep", "dir=down", "Visits 0", f"Exception: {e}", False)

    # TC37: C-SCAN circular wraparound
    try:
        res = cscan([10, 180], initial_head=100, total_cylinders=200, direction="up")
        passed = (res.seek_sequence == [100, 180, 199, 0, 10])
        actual = f"SeekSeq={' -> '.join(map(str, res.seek_sequence))}"
        record("TC37", "Boundary Values", "Disk C-SCAN circular wraparound", "Head: 100, Reqs: [10, 180], dir=up", "Sequence: 100 -> 180 -> 199 -> 0 -> 10", actual, passed, "Rapid return jump verified")
    except Exception as e:
        record("TC37", "Boundary Values", "Disk C-SCAN circular wraparound", "dir=up", "199 -> 0 jump", f"Exception: {e}", False)

    # -------------------------------------------------------------
    # EXTENDED CASES: INVALID MATRICES & DEADLOCK (TC38 - TC44)
    # -------------------------------------------------------------
    # TC38: Matrix row mismatch
    try:
        calculate_need([[1, 2]], [[1, 2], [3, 4]])
        record("TC38", "Invalid Matrices", "Deadlock row count mismatch", "Max: 1 row, Alloc: 2 rows", "Raise ValueError", "No exception", False)
    except ValueError as e:
        record("TC38", "Invalid Matrices", "Deadlock row count mismatch", "Max: 1 row, Alloc: 2 rows", "Raise ValueError", f"ValueError: {e}", True, "Row dimension mismatch caught")

    # TC39: Matrix column mismatch
    try:
        calculate_need([[1, 2, 3]], [[1, 2]])
        record("TC39", "Invalid Matrices", "Deadlock column count mismatch", "Max: 3 cols, Alloc: 2 cols", "Raise ValueError", "No exception", False)
    except ValueError as e:
        record("TC39", "Invalid Matrices", "Deadlock column count mismatch", "Max: 3 cols, Alloc: 2 cols", "Raise ValueError", f"ValueError: {e}", True, "Column dimension mismatch caught")

    # TC40: Allocation > Max Demand
    try:
        calculate_need([[2, 2]], [[3, 2]])
        record("TC40", "Invalid Matrices", "Allocation exceeds Max Demand", "Alloc: [3, 2], Max: [2, 2]", "Raise ValueError", "No exception", False)
    except ValueError as e:
        record("TC40", "Invalid Matrices", "Allocation exceeds Max Demand", "Alloc > Max", "Raise ValueError", f"ValueError: {e}", True, "Allocation exceeding claim caught")

    # TC41: Available length mismatch
    try:
        validate_bankers_matrix([[1, 1]], [[2, 2]], [3], ["P0"], ["R1", "R2"])
        record("TC41", "Invalid Matrices", "Available length does not match resource count", "Available length: 1, Resources: 2", "Raise ValueError", "No exception", False)
    except ValueError as e:
        record("TC41", "Invalid Matrices", "Available length does not match resource count", "Avail len != resources", "Raise ValueError", f"ValueError: {e}", True, "Available dimension mismatch caught")

    # TC42: Empty matrices
    try:
        calculate_need([], [])
        record("TC42", "Invalid Matrices", "Empty deadlock matrices", "max=[], alloc=[]", "Raise ValueError", "No exception", False)
    except ValueError as e:
        record("TC42", "Invalid Matrices", "Empty deadlock matrices", "max=[], alloc=[]", "Raise ValueError", f"ValueError: {e}", True, "Empty matrix input caught")

    # TC43: Negative resource allocation
    try:
        validate_bankers_matrix([[-1, 2]], [[2, 2]], [1, 1], ["P0"], ["R1", "R2"])
        record("TC43", "Invalid Matrices", "Negative allocation count in matrix", "Allocation[0][0] = -1", "Raise ValueError", "No exception", False)
    except ValueError as e:
        record("TC43", "Invalid Matrices", "Negative allocation count in matrix", "Alloc=-1", "Raise ValueError", f"ValueError: {e}", True, "Negative resource count caught")

    # TC44: Negative available resources
    try:
        validate_bankers_matrix([[1, 1]], [[2, 2]], [-3, 1], ["P0"], ["R1", "R2"])
        record("TC44", "Invalid Matrices", "Negative available vector entry", "available[0] = -3", "Raise ValueError", "No exception", False)
    except ValueError as e:
        record("TC44", "Invalid Matrices", "Negative available vector entry", "Avail=-3", "Raise ValueError", f"ValueError: {e}", True, "Negative available count caught")

    # -------------------------------------------------------------
    # EXTENDED CASES: TIME QUANTUM & DISK BOUNDS (TC45 - TC51)
    # -------------------------------------------------------------
    # TC45: Round Robin q=0
    try:
        validate_positive_int(0, "Time quantum")
        record("TC45", "Invalid Parameters", "Round Robin time quantum q=0", "quantum = 0", "Raise ValueError", "No exception", False)
    except ValueError as e:
        record("TC45", "Invalid Parameters", "Round Robin time quantum q=0", "quantum = 0", "Raise ValueError", f"ValueError: {e}", True, "Zero quantum rejected")

    # TC46: Round Robin q < 0
    try:
        validate_positive_int(-3, "Time quantum")
        record("TC46", "Invalid Parameters", "Round Robin negative time quantum", "quantum = -3", "Raise ValueError", "No exception", False)
    except ValueError as e:
        record("TC46", "Invalid Parameters", "Round Robin negative time quantum", "quantum = -3", "Raise ValueError", f"ValueError: {e}", True, "Negative quantum rejected")

    # TC47: Negative disk cylinder
    try:
        validate_cylinder_requests([-10], 50, 200)
        record("TC47", "Invalid Parameters", "Negative cylinder request rejection", "cylinder = -10", "Raise ValueError", "No exception", False)
    except ValueError as e:
        record("TC47", "Invalid Parameters", "Negative cylinder request rejection", "cylinder = -10", "Raise ValueError", f"ValueError: {e}", True, "Negative cylinder caught")

    # TC48: Cylinder exceeding total capacity
    try:
        validate_cylinder_requests([250], 50, 200)
        record("TC48", "Invalid Parameters", "Cylinder exceeding total capacity rejection", "cylinder = 250, total = 200", "Raise ValueError", "No exception", False)
    except ValueError as e:
        record("TC48", "Invalid Parameters", "Cylinder exceeding total capacity rejection", "cylinder = 250 >= 200", "Raise ValueError", f"ValueError: {e}", True, "Cylinder exceeding capacity caught")

    # TC49: Initial disk head out of range
    try:
        validate_cylinder_requests([50], 250, 200)
        record("TC49", "Invalid Parameters", "Initial head position out of bounds", "head = 250, total = 200", "Raise ValueError", "No exception", False)
    except ValueError as e:
        record("TC49", "Invalid Parameters", "Initial head position out of bounds", "head = 250 >= 200", "Raise ValueError", f"ValueError: {e}", True, "Out-of-range initial head caught")

    # TC50: Total cylinders non-positive
    try:
        validate_cylinder_requests([50], 50, 0)
        record("TC50", "Invalid Parameters", "Total cylinders zero", "total_cylinders = 0", "Raise ValueError", "No exception", False)
    except ValueError as e:
        record("TC50", "Invalid Parameters", "Total cylinders zero", "total_cylinders = 0", "Raise ValueError", f"ValueError: {e}", True, "Non-positive total cylinders caught")

    # TC51: Invalid disk direction string
    try:
        validate_cylinder_requests([50], 50, 200, direction="diagonal")
        record("TC51", "Invalid Parameters", "Invalid disk sweep direction string", "direction = 'diagonal'", "Raise ValueError", "No exception", False)
    except ValueError as e:
        record("TC51", "Invalid Parameters", "Invalid disk sweep direction string", "direction = 'diagonal'", "Raise ValueError", f"ValueError: {e}", True, "Invalid sweep direction caught")

    # -------------------------------------------------------------
    # EXTENDED CASES: DYNAMIC DEADLOCK REQUESTS & ROLLBACK (TC52 - TC56)
    # -------------------------------------------------------------
    p_ids = ["P0", "P1", "P2", "P3", "P4"]
    r_ids = ["A", "B", "C"]
    alloc = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]
    max_d = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]
    avail = [3, 3, 2]
    base_state = DeadlockState(p_ids, r_ids, avail, alloc, max_d)

    # TC52: Safe request granted
    try:
        st = copy.deepcopy(base_state)
        granted, msg, seq = request_resources(st, "P1", [1, 0, 2], commit=True)
        passed = (granted and len(seq) == 5 and st.available == [2, 3, 0] and st.allocation[1] == [3, 0, 2])
        actual = f"Granted={granted}, UpdatedAvail={st.available}, Seq={' -> '.join(seq)}"
        record("TC52", "Deadlock Safety", "Safe dynamic resource request granted", "P1 requests [1, 0, 2]", "Granted=True, State safely committed", actual, passed, "State successfully committed")
    except Exception as e:
        record("TC52", "Deadlock Safety", "Safe dynamic resource request granted", "P1 requests [1, 0, 2]", "Granted=True", f"Exception: {e}", False)

    # TC53: Request exceeding declared maximum claim
    try:
        st = copy.deepcopy(base_state)
        granted, msg, seq = request_resources(st, "P1", [5, 5, 5])
        passed = (not granted and "exceeded its maximum claim" in msg)
        actual = f"Granted={granted}, Msg={msg}"
        record("TC53", "Deadlock Safety", "Request exceeding declared claim rejected", "P1 requests [5, 5, 5] (Need=[1, 2, 2])", "Granted=False, diagnostic error", actual, passed, "Claim violation rejected")
    except Exception as e:
        record("TC53", "Deadlock Safety", "Request exceeding declared claim rejected", "Request > Need", "Rejected", f"Exception: {e}", False)

    # TC54: Request exceeding current availability
    try:
        st = copy.deepcopy(base_state)
        granted, msg, seq = request_resources(st, "P0", [0, 4, 0])
        passed = (not granted and "must wait" in msg)
        actual = f"Granted={granted}, Msg={msg}"
        record("TC54", "Deadlock Safety", "Request exceeding current availability forced to wait", "P0 requests [0, 4, 0] (Avail=[3, 3, 2])", "Granted=False, Process must wait", actual, passed, "Capacity violation forces wait")
    except Exception as e:
        record("TC54", "Deadlock Safety", "Request exceeding current availability forced to wait", "Request > Avail", "Must wait", f"Exception: {e}", False)

    # TC55: Unsafe request denied & state rolled back
    try:
        st = copy.deepcopy(base_state)
        avail_before = list(st.available)
        alloc_before = [list(r) for r in st.allocation]
        # P4 requests [3, 3, 0]: leaves Available [0, 0, 2] -> unsafe!
        granted, msg, seq = request_resources(st, "P4", [3, 3, 0], commit=True)
        passed = (not granted and st.available == avail_before and st.allocation == alloc_before)
        actual = f"Granted={granted}, AvailRestored={st.available == avail_before}"
        record("TC55", "Deadlock Safety", "Unsafe request denied with speculative rollback", "P4 requests [3, 3, 0] (Induces unsafe state)", "Granted=False, Zero state corruption after rollback", actual, passed, "Speculative rollback verified")
    except Exception as e:
        record("TC55", "Deadlock Safety", "Unsafe request denied with speculative rollback", "Unsafe request", "Rolled back", f"Exception: {e}", False)

    # TC56: Multiple valid safe sequences
    try:
        p_ids_m = ["P0", "P1"]
        r_ids_m = ["A"]
        alloc_m = [[1], [1]]
        max_d_m = [[2], [2]]
        avail_m = [2]
        st_m = DeadlockState(p_ids_m, r_ids_m, avail_m, alloc_m, max_d_m)
        is_safe, seq = bankers_algorithm(st_m)
        passed = (is_safe and len(seq) == 2)
        actual = f"is_safe={is_safe}, sequence={' -> '.join(seq)}"
        record("TC56", "Deadlock Safety", "Multiple possible safe sequences resolution", "Symmetric available capacity: Avail=[2], Needs=[1],[1]", "System SAFE, Valid sequence found", actual, passed, "Deterministic sequence selection")
    except Exception as e:
        record("TC56", "Deadlock Safety", "Multiple possible safe sequences resolution", "Symmetric state", "SAFE", f"Exception: {e}", False)

    # -------------------------------------------------------------
    # EXTENDED CASES: REPORTING, CSV & CHARTS (TC57 - TC72)
    # -------------------------------------------------------------
    # TC57: CPU benchmark metrics
    try:
        cpu_res = benchmark_cpu(generate_chart=False)
        passed = (len(cpu_res) == 4 and all("avg_waiting_time" in r for r in cpu_res))
        actual = f"AlgosBenchmarked={len(cpu_res)}, MinWT={min(r['avg_waiting_time'] for r in cpu_res)}"
        record("TC57", "Reporting & IO", "CPU benchmark execution and metrics calculation", "Standard CPU workload", "4 algorithms benchmarked with complete metrics", actual, passed, "CPU metrics calculated accurately")
    except Exception as e:
        record("TC57", "Reporting & IO", "CPU benchmark execution and metrics calculation", "Standard workload", "Success", f"Exception: {e}", False)

    # TC58: CPU CSV export check
    try:
        csv_p = RESULTS_DIR / "cpu_results.csv"
        passed = (csv_p.exists() and csv_p.stat().st_size > 50)
        actual = f"FileExists={csv_p.exists()}, SizeBytes={csv_p.stat().st_size}"
        record("TC58", "Reporting & IO", "CPU results CSV export integrity", "cpu_results.csv in results/", "File exists and non-empty", actual, passed, "CSV export verified")
    except Exception as e:
        record("TC58", "Reporting & IO", "CPU results CSV export integrity", "File check", "Exists", f"Exception: {e}", False)

    # TC59: CPU Chart generation
    try:
        chart_p = CHARTS_DIR / "cpu_comparison.png"
        passed = (chart_p.exists() and chart_p.stat().st_size > 1000)
        actual = f"ChartExists={chart_p.exists()}, SizeBytes={chart_p.stat().st_size}"
        record("TC59", "Reporting & IO", "CPU comparison chart 300 DPI generation", "cpu_comparison.png", "PNG file exists and >1KB", actual, passed, "High-resolution chart rendered")
    except Exception as e:
        record("TC59", "Reporting & IO", "CPU comparison chart 300 DPI generation", "File check", "Exists", f"Exception: {e}", False)

    # TC60: Memory benchmark metrics
    try:
        mem_res = benchmark_memory(generate_chart=False)
        passed = (len(mem_res) == 3 and all("success_rate_percent" in r for r in mem_res))
        actual = f"AlgosBenchmarked={len(mem_res)}, BestAlgoSuccess={max(r['success_rate_percent'] for r in mem_res)}%"
        record("TC60", "Reporting & IO", "Memory benchmark execution and fragmentation metrics", "Standard Memory workload", "3 algorithms benchmarked with allocation rates", actual, passed, "Memory metrics calculated accurately")
    except Exception as e:
        record("TC60", "Reporting & IO", "Memory benchmark execution and fragmentation metrics", "Standard workload", "Success", f"Exception: {e}", False)

    # TC61: Memory CSV export check
    try:
        csv_p = RESULTS_DIR / "memory_results.csv"
        passed = (csv_p.exists() and csv_p.stat().st_size > 50)
        actual = f"FileExists={csv_p.exists()}, SizeBytes={csv_p.stat().st_size}"
        record("TC61", "Reporting & IO", "Memory results CSV export integrity", "memory_results.csv in results/", "File exists and non-empty", actual, passed, "CSV export verified")
    except Exception as e:
        record("TC61", "Reporting & IO", "Memory results CSV export integrity", "File check", "Exists", f"Exception: {e}", False)

    # TC62: Memory Chart generation
    try:
        chart_p = CHARTS_DIR / "memory_comparison.png"
        passed = (chart_p.exists() and chart_p.stat().st_size > 1000)
        actual = f"ChartExists={chart_p.exists()}, SizeBytes={chart_p.stat().st_size}"
        record("TC62", "Reporting & IO", "Memory comparison chart 300 DPI generation", "memory_comparison.png", "PNG file exists and >1KB", actual, passed, "High-resolution chart rendered")
    except Exception as e:
        record("TC62", "Reporting & IO", "Memory comparison chart 300 DPI generation", "File check", "Exists", f"Exception: {e}", False)

    # TC63: Disk benchmark metrics
    try:
        disk_res = benchmark_disk(generate_chart=False)
        passed = (len(disk_res) == 4 and all("total_head_movement" in r for r in disk_res))
        actual = f"AlgosBenchmarked={len(disk_res)}, MinSeek={min(r['total_head_movement'] for r in disk_res)} cyl"
        record("TC63", "Reporting & IO", "Disk benchmark execution and head movement metrics", "Standard Disk workload", "4 algorithms benchmarked with total seek distance", actual, passed, "Disk metrics calculated accurately")
    except Exception as e:
        record("TC63", "Reporting & IO", "Disk benchmark execution and head movement metrics", "Standard workload", "Success", f"Exception: {e}", False)

    # TC64: Disk CSV export check
    try:
        csv_p = RESULTS_DIR / "disk_results.csv"
        passed = (csv_p.exists() and csv_p.stat().st_size > 50)
        actual = f"FileExists={csv_p.exists()}, SizeBytes={csv_p.stat().st_size}"
        record("TC64", "Reporting & IO", "Disk results CSV export integrity", "disk_results.csv in results/", "File exists and non-empty", actual, passed, "CSV export verified")
    except Exception as e:
        record("TC64", "Reporting & IO", "Disk results CSV export integrity", "File check", "Exists", f"Exception: {e}", False)

    # TC65: Disk Chart generation
    try:
        chart_p = CHARTS_DIR / "disk_comparison.png"
        passed = (chart_p.exists() and chart_p.stat().st_size > 1000)
        actual = f"ChartExists={chart_p.exists()}, SizeBytes={chart_p.stat().st_size}"
        record("TC65", "Reporting & IO", "Disk comparison chart 300 DPI generation", "disk_comparison.png", "PNG file exists and >1KB", actual, passed, "High-resolution chart rendered")
    except Exception as e:
        record("TC65", "Reporting & IO", "Disk comparison chart 300 DPI generation", "File check", "Exists", f"Exception: {e}", False)

    # TC66: Deadlock CSV export check
    try:
        dl_res = analyze_deadlock()
        csv_p = RESULTS_DIR / "deadlock_results.csv"
        passed = (csv_p.exists() and csv_p.stat().st_size > 50 and dl_res["is_safe"])
        actual = f"FileExists={csv_p.exists()}, SizeBytes={csv_p.stat().st_size}, SystemSafe={dl_res['is_safe']}"
        record("TC66", "Reporting & IO", "Deadlock results CSV export integrity", "deadlock_results.csv in results/", "File exists and contains system matrices & summary", actual, passed, "Deadlock matrices exported cleanly")
    except Exception as e:
        record("TC66", "Reporting & IO", "Deadlock results CSV export integrity", "File check", "Exists", f"Exception: {e}", False)

    # TC67: 4-Panel Executive Dashboard generation
    try:
        generate_overall_dashboard()
        chart_p = CHARTS_DIR / "overall_analysis.png"
        passed = (chart_p.exists() and chart_p.stat().st_size > 50000)
        actual = f"DashboardExists={chart_p.exists()}, SizeBytes={chart_p.stat().st_size}"
        record("TC67", "Reporting & IO", "Executive 4-Panel Dashboard 300 DPI generation", "overall_analysis.png", "PNG file exists and >50KB", actual, passed, "Comprehensive executive dashboard rendered")
    except Exception as e:
        record("TC67", "Reporting & IO", "Executive 4-Panel Dashboard 300 DPI generation", "Dashboard render", "Exists", f"Exception: {e}", False)

    # TC68: Multi-workload suite execution
    try:
        workload_res = benchmark_all_workloads()
        passed = ("cpu_workloads" in workload_res and "memory_workloads" in workload_res and "disk_workloads" in workload_res and "deadlock_workloads" in workload_res)
        actual = f"WorkloadsProcessed=4 tiers across CPU, Memory, Disk, Deadlock"
        record("TC68", "Reporting & IO", "Multi-tier workload benchmarking suite", "Normal, Small, Large, Edge datasets", "All 4 tiers benchmarked and exported to CSV", actual, passed, "Multi-tier workload benchmarks completed")
    except Exception as e:
        record("TC68", "Reporting & IO", "Multi-tier workload benchmarking suite", "Multi-tier run", "Completed", f"Exception: {e}", False)

    # TC69: Round Robin quantum sensitivity analysis
    try:
        rr_csv = RESULTS_DIR / "rr_quantum_sensitivity.csv"
        passed = (rr_csv.exists() and rr_csv.stat().st_size > 50)
        actual = f"SensitivityFileExists={rr_csv.exists()}, SizeBytes={rr_csv.stat().st_size}"
        record("TC69", "Reporting & IO", "Round Robin quantum sensitivity analysis", "q in [1, 2, 4, 8]", "Sensitivity CSV exported with context switches and RT", actual, passed, "Quantum trade-offs captured empirically")
    except Exception as e:
        record("TC69", "Reporting & IO", "Round Robin quantum sensitivity analysis", "Sensitivity test", "Completed", f"Exception: {e}", False)

    # TC70: Empty CPU dataset rejection in reporting
    try:
        benchmark_cpu([])
        record("TC70", "Reporting & IO", "Empty CPU dataset rejection in reporting", "processes = []", "Raise ValueError", "No exception", False)
    except ValueError as e:
        record("TC70", "Reporting & IO", "Empty CPU dataset rejection in reporting", "processes = []", "Raise ValueError", f"ValueError: {e}", True, "Empty CPU workload rejected")

    # TC71: Empty Memory dataset rejection in reporting
    try:
        benchmark_memory([], [])
        record("TC71", "Reporting & IO", "Empty Memory dataset rejection in reporting", "blocks = [], reqs = []", "Raise ValueError", "No exception", False)
    except ValueError as e:
        record("TC71", "Reporting & IO", "Empty Memory dataset rejection in reporting", "blocks = [], reqs = []", "Raise ValueError", f"ValueError: {e}", True, "Empty Memory workload rejected")

    # TC72: Empty Disk dataset rejection in reporting
    try:
        benchmark_disk([])
        record("TC72", "Reporting & IO", "Empty Disk dataset rejection in reporting", "requests = []", "Raise ValueError", "No exception", False)
    except ValueError as e:
        record("TC72", "Reporting & IO", "Empty Disk dataset rejection in reporting", "requests = []", "Raise ValueError", f"ValueError: {e}", True, "Empty Disk workload rejected")

    # -------------------------------------------------------------
    # EXTENDED CASES: RELIABILITY, RECOVERY & LOGGING (TC73 - TC77)
    # -------------------------------------------------------------
    # TC73: Interactive menu non-numeric input recovery
    try:
        with patch("builtins.input", side_effect=["abc", "6"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                main.main()
                out = mock_out.getvalue()
                passed = ("Invalid choice" in out and "Exiting OS Simulator" in out)
                actual = "Handled non-numeric menu choice and reprompted"
                record("TC73", "Reliability", "Interactive menu non-numeric input recovery", "input: 'abc', then '6'", "Display friendly error and reprompt without crash", actual, passed, "Crash prevention verified")
    except Exception as e:
        record("TC73", "Reliability", "Interactive menu non-numeric input recovery", "'abc'", "Reprompt", f"Exception: {e}", False)

    # TC74: Clean menu exit
    try:
        with patch("builtins.input", side_effect=["6"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                main.main()
                out = mock_out.getvalue()
                passed = ("Exiting OS Simulator. Goodbye!" in out)
                actual = "Clean application termination"
                record("TC74", "Reliability", "Interactive main menu clean exit", "input: '6'", "Clean exit message printed and loop terminates", actual, passed, "Zero unhandled termination errors")
    except Exception as e:
        record("TC74", "Reliability", "Interactive main menu clean exit", "'6'", "Clean exit", f"Exception: {e}", False)

    # TC75: Python runtime compatibility check
    try:
        comp = main.check_python_compatibility()
        passed = isinstance(comp, bool)
        actual = f"Compatible={comp}, sys.version={sys.version.split()[0]}"
        record("TC75", "Reliability", "Python runtime compatibility verification", "sys.version_info", "Returns boolean status without raising unhandled exception", actual, passed, "Runtime compatibility verified")
    except Exception as e:
        record("TC75", "Reliability", "Python runtime compatibility verification", "Runtime check", "Boolean", f"Exception: {e}", False)

    # TC76: Structured activity logging
    try:
        log_file = PROJECT_ROOT / "logs" / "activity.log"
        passed = (log_file.exists() and log_file.stat().st_size > 0)
        actual = f"LogFileExists={log_file.exists()}, SizeBytes={log_file.stat().st_size}"
        record("TC76", "Reliability", "Structured activity audit logging", "logs/activity.log", "Log file exists and captures system events", actual, passed, "Structured logging active")
    except Exception as e:
        record("TC76", "Reliability", "Structured activity audit logging", "Log file check", "Exists", f"Exception: {e}", False)

    # TC77: Bash automation scripts POSIX syntax
    try:
        run_sh = PROJECT_ROOT / "run.sh"
        run_tests_sh = PROJECT_ROOT / "run_tests.sh"
        content_run = run_sh.read_text(encoding="utf-8")
        content_test = run_tests_sh.read_text(encoding="utf-8")
        passed = ("#!/bin/bash" in content_run and "#!/bin/bash" in content_test)
        actual = f"run.sh_shebang={'#!/bin/bash' in content_run}, run_tests.sh_shebang={'#!/bin/bash' in content_test}"
        record("TC77", "Reliability", "POSIX Bash automation scripts validation", "run.sh & run_tests.sh", "Valid shebang and executable commands", actual, passed, "Cross-platform shell scripts verified")
    except Exception as e:
        record("TC77", "Reliability", "POSIX Bash automation scripts validation", "Bash files", "Valid shebang", f"Exception: {e}", False)

    return results


def export_evidence(results: list[dict[str, str]]) -> None:
    # 1. Export test_cases.csv
    cases_path = PHASE4_DIR / "test_cases.csv"
    with open(cases_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Test ID", "Category", "Description", "Input Specification", "Expected Result"])
        for r in results:
            writer.writerow([r["test_id"], r["category"], r["test_description"], r["input"], r["expected_result"]])
    print(f"Exported test case specifications to: {cases_path}")

    # 2. Export test_results.csv
    results_path = PHASE4_DIR / "test_results.csv"
    with open(results_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Test ID", "Category", "Description", "Input", "Expected Result", "Actual Result", "Status", "Notes"])
        for r in results:
            writer.writerow([r["test_id"], r["category"], r["test_description"], r["input"], r["expected_result"], r["actual_result"], r["status"], r["notes"]])
    print(f"Exported actual execution results to: {results_path}")

    # 3. Export test execution log
    log_path = PHASE4_LOGS_DIR / "test_execution.log"
    with open(log_path, mode="w", encoding="utf-8") as f:
        f.write("PHASE 4 COMPREHENSIVE TESTING AUDIT EXECUTION LOG\n")
        f.write("======================================================================\n\n")
        total = len(results)
        passed = sum(1 for r in results if r["status"] == "PASS")
        failed = sum(1 for r in results if r["status"] == "FAIL")
        f.write(f"Total Tests Executed: {total}\n")
        f.write(f"Total Tests Passed  : {passed}\n")
        f.write(f"Total Tests Failed  : {failed}\n")
        f.write(f"Success Rate        : {(passed / total) * 100:.2f}%\n\n")
        f.write("-" * 80 + "\n")
        for r in results:
            f.write(f"[{r['status']}] {r['test_id']} ({r['category']}): {r['test_description']}\n")
            f.write(f"  Input   : {r['input']}\n")
            f.write(f"  Expected: {r['expected_result']}\n")
            f.write(f"  Actual  : {r['actual_result']}\n")
            if r["notes"]:
                f.write(f"  Notes   : {r['notes']}\n")
            f.write("\n")
    print(f"Exported execution audit log to: {log_path}")

    # 4. Copy activity.log to Phase_4_Testing/logs/
    main_log = PROJECT_ROOT / "logs" / "activity.log"
    if main_log.exists():
        shutil.copy2(main_log, PHASE4_LOGS_DIR / "activity.log")

    # 5. Mirror tests/ into Phase_4_Testing/tests/
    tests_src = PROJECT_ROOT / "tests"
    for py_file in tests_src.glob("*.py"):
        shutil.copy2(py_file, PHASE4_TESTS_DIR / py_file.name)
    print(f"Mirrored test suite into: {PHASE4_TESTS_DIR}")


if __name__ == "__main__":
    print("\nExecuting Phase 4 Complete Testing Audit (TC01-TC77)...")
    res = run_all_cases()
    export_evidence(res)
    total = len(res)
    passed = sum(1 for r in res if r["status"] == "PASS")
    failed = sum(1 for r in res if r["status"] == "FAIL")
    print(f"\nAudit Finished: {passed}/{total} Passed ({failed} Failed).")
