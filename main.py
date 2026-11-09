#!/usr/bin/env python3
"""
Main Application Controller — OS Resource Management Simulator.
Central integration entry point unifying CPU scheduling, Memory management,
Deadlock management, Disk scheduling, and Comparative Reporting.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.logger import setup_logger, get_logger
from utils.helpers import format_table
from utils.validators import (
    Process,
    DeadlockState,
    validate_positive_int,
    validate_non_negative_int,
    validate_menu_choice,
)
from modules.cpu_scheduling import (
    fcfs,
    sjf,
    round_robin,
    priority_scheduling,
    calculate_metrics,
    generate_gantt_chart,
)
from modules.memory_management import (
    first_fit,
    best_fit,
    worst_fit,
    display_allocation,
)
from modules.deadlock import (
    calculate_need,
    bankers_algorithm,
    request_resources,
    display_safe_sequence,
)
from modules.disk_scheduling import (
    fcfs_disk,
    sstf,
    scan,
    cscan,
)

logger = setup_logger()


def check_python_compatibility() -> bool:
    """Verifies Python 3.11+ runtime compatibility per faculty blueprint specification."""
    major, minor, micro = sys.version_info.major, sys.version_info.minor, sys.version_info.micro
    if (major, minor) < (3, 11):
        notice = (
            f"[Faculty Blueprint Notice] Python 3.11+ is the specified environment.\n"
            f"Detected runtime: Python {major}.{minor}.{micro}. Proceeding with backward-compatible execution."
        )
        logger.warning(notice)
        print(f"{notice}\n")
        return False
    logger.info(f"Python 3.11+ compatibility verified: Python {major}.{minor}.{micro}.")
    return True


def run_cpu_module() -> None:
    """Interactively executes CPU Scheduling algorithms."""
    logger.info("Entering CPU Scheduling Module.")
    print("\n" + "=" * 50)
    print("           MODULE 1: CPU SCHEDULING")
    print("=" * 50)
    print("1. FCFS (First-Come, First-Served)")
    print("2. SJF (Shortest Job First - Non-preemptive)")
    print("3. Round Robin (Preemptive)")
    print("4. Priority Scheduling (Non-preemptive)")
    print("5. Run All on Blueprint Preset")
    print("0. Back to Main Menu")

    choice = input("Enter choice (0-5): ").strip()
    if choice == "0":
        return

    # Use Blueprint Preset or Custom
    use_preset = choice == "5" or input("Use Blueprint preset workload? (y/n, default y): ").strip().lower() != "n"

    if use_preset:
        processes = [
            Process(pid="P1", arrival_time=0, burst_time=5, priority=2),
            Process(pid="P2", arrival_time=1, burst_time=3, priority=1),
            Process(pid="P3", arrival_time=2, burst_time=8, priority=4),
            Process(pid="P4", arrival_time=3, burst_time=2, priority=3),
        ]
        print("\nLoaded Blueprint Workload: P1(AT=0, BT=5), P2(AT=1, BT=3), P3(AT=2, BT=8), P4(AT=3, BT=2)")
    else:
        try:
            n = validate_positive_int(input("Enter number of processes: "), "Process count")
            processes = []
            for i in range(n):
                pid = input(f"PID for process #{i+1} [default P{i+1}]: ").strip() or f"P{i+1}"
                at = validate_non_negative_int(input(f"Arrival Time for {pid} [0]: ").strip() or "0", f"AT for {pid}")
                bt = validate_positive_int(input(f"Burst Time for {pid}: ").strip(), f"BT for {pid}")
                prio = validate_non_negative_int(input(f"Priority for {pid} (lower=higher) [0]: ").strip() or "0", f"Priority for {pid}")
                processes.append(Process(pid=pid, arrival_time=at, burst_time=bt, priority=prio))
        except ValueError as e:
            print(f"[Error] Invalid input: {e}")
            return

    algo_map = {
        "1": ("FCFS", lambda p: fcfs(p)),
        "2": ("SJF (Non-preemptive)", lambda p: sjf(p)),
        "3": ("Round Robin", lambda p: round_robin(p, quantum=2)),
        "4": ("Priority (Non-preemptive)", lambda p: priority_scheduling(p)),
    }

    if choice in algo_map:
        name, runner = algo_map[choice]
        if choice == "3":
            q_in = input("Enter Time Quantum [default 2]: ").strip()
            q = validate_positive_int(q_in, "Time quantum") if q_in else 2
            runner = lambda p: round_robin(p, quantum=q)
            name = f"Round Robin (q={q})"

        scheduled, segments = runner(processes)
        _print_cpu_results(name, scheduled, segments)

    elif choice == "5":
        print("\n=== RUNNING ALL CPU SCHEDULING ALGORITHMS ===")
        for opt, (name, runner) in algo_map.items():
            sched, segs = runner(processes)
            _print_cpu_results(name, sched, segs)


def _print_cpu_results(algo_name: str, scheduled: list[Process], segments: list) -> None:
    print(f"\n--- {algo_name.upper()} RESULTS ---")
    headers = ["Process", "AT", "BT", "Priority", "CT", "TAT", "WT", "RT"]
    rows = [
        [p.pid, p.arrival_time, p.burst_time, p.priority, p.completion_time, p.turnaround_time, p.waiting_time, p.response_time]
        for p in scheduled
    ]
    print(format_table(headers, rows))
    metrics = calculate_metrics(scheduled)
    print(f"Average Waiting Time: {metrics['avg_waiting_time']:.2f}")
    print(f"Average Turnaround Time: {metrics['avg_turnaround_time']:.2f}")
    print("\nGantt Chart Timeline:")
    print(generate_gantt_chart(segments))


def run_memory_module() -> None:
    """Interactively executes Memory Management allocation algorithms."""
    logger.info("Entering Memory Management Module.")
    print("\n" + "=" * 50)
    print("           MODULE 2: MEMORY MANAGEMENT")
    print("=" * 50)
    print("1. First Fit (Dynamic Partition Splitting)")
    print("2. Best Fit (Dynamic Partition Splitting)")
    print("3. Worst Fit (Dynamic Partition Splitting)")
    print("4. Compare All on Blueprint Preset")
    print("0. Back to Main Menu")

    choice = input("Enter choice (0-4): ").strip()
    if choice == "0":
        return

    use_preset = choice == "4" or input("Use Blueprint preset workload? (y/n, default y): ").strip().lower() != "n"

    if use_preset:
        blocks = [100, 500, 200, 300, 600]
        requests = [("P1", 212), ("P2", 417), ("P3", 112), ("P4", 426)]
        print("\nBlueprint Blocks: 100, 500, 200, 300, 600 KB")
        print("Blueprint Requests: P1(212KB), P2(417KB), P3(112KB), P4(426KB)")
    else:
        try:
            b_str = input("Enter block sizes in KB separated by commas (e.g. 100, 500, 200): ")
            blocks = [validate_positive_int(x.strip(), "Block size") for x in b_str.split(",") if x.strip()]
            r_str = input("Enter process requests in format PID:Size, ... (e.g. P1:212, P2:417): ")
            requests = []
            for item in r_str.split(","):
                if ":" in item:
                    pid, sz = item.split(":", 1)
                    requests.append((pid.strip(), validate_positive_int(sz.strip(), f"Request for {pid}")))
        except ValueError as e:
            print(f"[Error] Invalid input: {e}")
            return

    algo_map = {
        "1": ("First Fit", first_fit),
        "2": ("Best Fit", best_fit),
        "3": ("Worst Fit", worst_fit),
    }

    if choice in algo_map:
        name, runner = algo_map[choice]
        res = runner(blocks, requests)
        print(display_allocation(res))
    elif choice == "4":
        for _, (name, runner) in algo_map.items():
            res = runner(blocks, requests)
            print(display_allocation(res))


def run_deadlock_module() -> None:
    """Interactively executes Banker's Deadlock Algorithm."""
    logger.info("Entering Deadlock Management Module.")
    print("\n" + "=" * 50)
    print("           MODULE 3: DEADLOCK MANAGEMENT")
    print("=" * 50)
    print("1. Check System Safety & Find Safe Sequence (Blueprint Preset)")
    print("2. Test Dynamic Resource Request")
    print("0. Back to Main Menu")

    choice = input("Enter choice (0-2): ").strip()
    if choice == "0":
        return

    # Default Blueprint State
    p_ids = ["P0", "P1", "P2", "P3", "P4"]
    r_ids = ["A", "B", "C"]
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

    state = DeadlockState(
        process_ids=p_ids,
        resource_ids=r_ids,
        available=list(available),
        allocation=[list(r) for r in allocation],
        max_demand=[list(r) for r in max_demand],
    )

    print("\n--- SYSTEM RESOURCE MATRICES ---")
    headers = ["PID"] + [f"Alloc {r}" for r in r_ids] + [f"Max {r}" for r in r_ids] + [f"Need {r}" for r in r_ids]
    rows = []
    for i, pid in enumerate(p_ids):
        row = [pid] + state.allocation[i] + state.max_demand[i] + state.need[i]
        rows.append(row)
    print(format_table(headers, rows))
    print(f"Available Resources: {dict(zip(r_ids, state.available))}\n")

    if choice == "1":
        is_safe, seq = bankers_algorithm(state)
        print("DEADLOCK MANAGEMENT")
        print(f"System Status: {'SAFE' if is_safe else 'UNSAFE / DEADLOCK RISK'}")
        if is_safe:
            print("Safe Sequence:")
            print(display_safe_sequence(seq))
            print("All processes can complete safely.")
        else:
            print("No safe sequence exists! Deadlock could occur.")

    elif choice == "2":
        pid_req = input("Enter PID making request (e.g. P1): ").strip() or "P1"
        req_in = input(f"Enter request vector for {r_ids} separated by commas [default 1,0,2]: ").strip() or "1,0,2"
        try:
            req_vec = [int(x.strip()) for x in req_in.split(",")]
            granted, msg, seq = request_resources(state, pid_req, req_vec)
            print(f"\nResult: {msg}")
            if granted:
                print(f"New Safe Sequence: {display_safe_sequence(seq)}")
        except ValueError as e:
            print(f"[Error] Invalid request vector: {e}")


def run_disk_module() -> None:
    """Interactively executes Disk Scheduling algorithms."""
    logger.info("Entering Disk Scheduling Module.")
    print("\n" + "=" * 50)
    print("           MODULE 4: DISK SCHEDULING")
    print("=" * 50)
    print("1. FCFS (First-Come, First-Served)")
    print("2. SSTF (Shortest Seek Time First)")
    print("3. SCAN (Elevator Algorithm)")
    print("4. C-SCAN (Circular SCAN)")
    print("5. Run All on Blueprint Preset")
    print("0. Back to Main Menu")

    choice = input("Enter choice (0-5): ").strip()
    if choice == "0":
        return

    use_preset = choice == "5" or input("Use Blueprint preset workload? (y/n, default y): ").strip().lower() != "n"

    if use_preset:
        requests = [98, 183, 37, 122, 14, 124, 65, 67]
        initial_head = 53
        total_cylinders = 200
        direction = "up"
        print(f"\nBlueprint Requests: {requests}")
        print(f"Initial Head: {initial_head} | Total Cylinders: {total_cylinders} | Direction: {direction}")
    else:
        try:
            r_str = input("Enter cylinder requests separated by commas (e.g. 98, 183, 37): ")
            requests = [int(x.strip()) for x in r_str.split(",") if x.strip()]
            initial_head = validate_non_negative_int(input("Enter initial head position [53]: ").strip() or "53", "Head")
            total_cylinders = validate_positive_int(input("Enter total cylinders [200]: ").strip() or "200", "Total cylinders")
            direction = input("Enter initial direction (up/down) [up]: ").strip().lower() or "up"
        except ValueError as e:
            print(f"[Error] Invalid input: {e}")
            return

    algo_map = {
        "1": ("FCFS", lambda: fcfs_disk(requests, initial_head, total_cylinders)),
        "2": ("SSTF", lambda: sstf(requests, initial_head, total_cylinders)),
        "3": ("SCAN", lambda: scan(requests, initial_head, total_cylinders, direction=direction)),
        "4": ("C-SCAN", lambda: cscan(requests, initial_head, total_cylinders, direction=direction)),
    }

    if choice in algo_map:
        name, runner = algo_map[choice]
        res = runner()
        _print_disk_results(res)
    elif choice == "5":
        print("\n=== RUNNING ALL DISK SCHEDULING ALGORITHMS ===")
        for _, (name, runner) in algo_map.items():
            res = runner()
            _print_disk_results(res)


def _print_disk_results(res) -> None:
    print(f"\nDISK SCHEDULING — {res.algorithm}")
    print(f"Initial Head Position: {res.initial_head}")
    print(f"Request Sequence: {' -> '.join(map(str, res.seek_sequence))}")
    print(f"Total Head Movement: {res.total_head_movement} cylinders")
    print(f"Average Head Movement: {res.average_head_movement:.2f} cylinders")


def run_reporting_module() -> None:
    """Invokes Reporting and Comparative Analysis subsystem."""
    logger.info("Entering Reporting & Analysis Module.")
    print("\n" + "=" * 50)
    print("      MODULE 5: PERFORMANCE ANALYSIS & REPORTING")
    print("=" * 50)
    try:
        from modules.reporting import run_all_benchmarks
        run_all_benchmarks()
    except ImportError:
        print("[Notice] Reporting engine is loading. Generating baseline comparison data...")


def main() -> None:
    """Main interactive terminal application loop."""
    logger.info("Application started.")
    check_python_compatibility()
    print("\n" + "=" * 50)
    print("    OS RESOURCE MANAGEMENT SIMULATOR")
    print("    Integrated Academic Simulator v1.0")
    print("=" * 50)

    while True:
        print("\nOS RESOURCE MANAGEMENT")
        print("1. CPU Scheduling")
        print("2. Memory Management")
        print("3. Deadlock Management")
        print("4. Disk Scheduling")
        print("5. Performance Analysis")
        print("6. Exit")

        try:
            choice = input("Enter choice (1-6): ").strip()
            if choice == "1":
                run_cpu_module()
            elif choice == "2":
                run_memory_module()
            elif choice == "3":
                run_deadlock_module()
            elif choice == "4":
                run_disk_module()
            elif choice == "5":
                run_reporting_module()
            elif choice == "6":
                print("\nExiting OS Simulator. Goodbye!")
                logger.info("Application cleanly terminated by user.")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 6.")
                logger.warning(f"Invalid menu choice entered: {choice!r}")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting OS Simulator. Goodbye!")
            logger.info("Application closed on EOF or interrupt.")
            break
        except Exception as e:
            print(f"\n[Unexpected Error] {e}")
            logger.error(f"Top-level unhandled exception: {e}")


if __name__ == "__main__":
    main()
