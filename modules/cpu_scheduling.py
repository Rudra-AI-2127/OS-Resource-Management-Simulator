"""
CPU Scheduling Module — OS Resource Management Simulator.
Implements FCFS, SJF (Non-preemptive), Round Robin (Preemptive), and Priority Scheduling (Non-preemptive).
Calculates Completion Time (CT), Turnaround Time (TAT), Waiting Time (WT), and Response Time (RT).
"""

from collections import deque
import copy
from typing import Sequence
from utils.logger import get_logger
from utils.helpers import TimelineSegment, render_gantt_ascii
from utils.validators import Process, validate_process_list, validate_positive_int

logger = get_logger()


def _clone_processes(processes: Sequence[Process]) -> list[Process]:
    """Validates and creates isolated working copies of process objects."""
    validated = validate_process_list(list(processes))
    cloned = []
    for p in validated:
        new_p = Process(
            pid=p.pid,
            arrival_time=p.arrival_time,
            burst_time=p.burst_time,
            priority=p.priority,
        )
        cloned.append(new_p)
    return cloned


def fcfs(processes: Sequence[Process]) -> tuple[list[Process], list[TimelineSegment]]:
    """
    First-Come, First-Served (FCFS) CPU Scheduling (Non-preemptive).
    Executes processes in order of arrival time; ties broken by PID.
    """
    procs = _clone_processes(processes)
    # Sort primarily by arrival time, secondarily by PID
    procs.sort(key=lambda p: (p.arrival_time, p.pid))

    segments: list[TimelineSegment] = []
    current_time = 0

    for p in procs:
        if current_time < p.arrival_time:
            # CPU idle interval
            segments.append(TimelineSegment(pid="IDLE", start_time=current_time, end_time=p.arrival_time))
            current_time = p.arrival_time

        start = current_time
        p.start_time = start
        p.response_time = start - p.arrival_time
        current_time += p.burst_time
        p.completion_time = current_time
        p.turnaround_time = p.completion_time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time
        p.remaining_time = 0

        segments.append(TimelineSegment(pid=p.pid, start_time=start, end_time=current_time))

    logger.info(f"FCFS scheduling executed for {len(procs)} processes.")
    return procs, segments


def sjf(processes: Sequence[Process]) -> tuple[list[Process], list[TimelineSegment]]:
    """
    Shortest Job First (SJF) CPU Scheduling (Non-preemptive).
    Selects the ready process with the smallest burst time.
    Ties broken by arrival time, then PID.
    """
    procs = _clone_processes(processes)
    remaining_pool = list(procs)
    segments: list[TimelineSegment] = []
    completed: list[Process] = []
    current_time = 0

    while remaining_pool:
        # Filter processes that have arrived by current_time
        ready_queue = [p for p in remaining_pool if p.arrival_time <= current_time]

        if not ready_queue:
            # Advance time to next earliest arrival
            next_arrival = min(p.arrival_time for p in remaining_pool)
            segments.append(TimelineSegment(pid="IDLE", start_time=current_time, end_time=next_arrival))
            current_time = next_arrival
            continue

        # Pick process with smallest burst time; tie-breaker: AT, PID
        selected = min(ready_queue, key=lambda p: (p.burst_time, p.arrival_time, p.pid))
        remaining_pool.remove(selected)

        start = current_time
        selected.start_time = start
        selected.response_time = start - selected.arrival_time
        current_time += selected.burst_time
        selected.completion_time = current_time
        selected.turnaround_time = selected.completion_time - selected.arrival_time
        selected.waiting_time = selected.turnaround_time - selected.burst_time
        selected.remaining_time = 0

        segments.append(TimelineSegment(pid=selected.pid, start_time=start, end_time=current_time))
        completed.append(selected)

    logger.info(f"SJF scheduling executed for {len(completed)} processes.")
    return completed, segments


def priority_scheduling(processes: Sequence[Process]) -> tuple[list[Process], list[TimelineSegment]]:
    """
    Priority CPU Scheduling (Non-preemptive).
    Lower integer value indicates higher priority (e.g. Priority 1 beats Priority 2).
    Ties broken by arrival time, then PID.
    """
    procs = _clone_processes(processes)
    remaining_pool = list(procs)
    segments: list[TimelineSegment] = []
    completed: list[Process] = []
    current_time = 0

    while remaining_pool:
        ready_queue = [p for p in remaining_pool if p.arrival_time <= current_time]

        if not ready_queue:
            next_arrival = min(p.arrival_time for p in remaining_pool)
            segments.append(TimelineSegment(pid="IDLE", start_time=current_time, end_time=next_arrival))
            current_time = next_arrival
            continue

        # Lowest numeric priority value = highest priority
        selected = min(ready_queue, key=lambda p: (p.priority, p.arrival_time, p.pid))
        remaining_pool.remove(selected)

        start = current_time
        selected.start_time = start
        selected.response_time = start - selected.arrival_time
        current_time += selected.burst_time
        selected.completion_time = current_time
        selected.turnaround_time = selected.completion_time - selected.arrival_time
        selected.waiting_time = selected.turnaround_time - selected.burst_time
        selected.remaining_time = 0

        segments.append(TimelineSegment(pid=selected.pid, start_time=start, end_time=current_time))
        completed.append(selected)

    logger.info(f"Priority scheduling executed for {len(completed)} processes.")
    return completed, segments


def round_robin(
    processes: Sequence[Process], quantum: int = 2
) -> tuple[list[Process], list[TimelineSegment]]:
    """
    Round Robin (RR) CPU Scheduling (Preemptive).
    Dispatches processes in FIFO order for time slices of length quantum.
    Arriving processes at time t enter ready queue before preempted process.
    """
    valid_quantum = validate_positive_int(quantum, "Time quantum")
    procs = _clone_processes(processes)
    # Sort initially by arrival time, then PID
    procs.sort(key=lambda p: (p.arrival_time, p.pid))

    unvisited = deque(procs)
    ready_queue: deque[Process] = deque()
    segments: list[TimelineSegment] = []
    completed: list[Process] = []
    current_time = 0

    while unvisited or ready_queue:
        # Load any jobs that have arrived by current_time
        while unvisited and unvisited[0].arrival_time <= current_time:
            ready_queue.append(unvisited.popleft())

        if not ready_queue:
            # No process ready; jump to next arrival
            next_arrival = unvisited[0].arrival_time
            segments.append(TimelineSegment(pid="IDLE", start_time=current_time, end_time=next_arrival))
            current_time = next_arrival
            while unvisited and unvisited[0].arrival_time <= current_time:
                ready_queue.append(unvisited.popleft())

        active = ready_queue.popleft()

        if active.start_time is None:
            active.start_time = current_time
            active.response_time = current_time - active.arrival_time

        exec_duration = min(active.remaining_time, valid_quantum)
        start = current_time
        current_time += exec_duration
        active.remaining_time -= exec_duration

        segments.append(TimelineSegment(pid=active.pid, start_time=start, end_time=current_time))

        # Enqueue new arrivals during this execution interval BEFORE re-queuing preempted active
        while unvisited and unvisited[0].arrival_time <= current_time:
            ready_queue.append(unvisited.popleft())

        if active.remaining_time > 0:
            ready_queue.append(active)
        else:
            active.completion_time = current_time
            active.turnaround_time = active.completion_time - active.arrival_time
            active.waiting_time = active.turnaround_time - active.burst_time
            completed.append(active)

    # Sort completed back to original order or PID order
    completed.sort(key=lambda p: p.pid)
    logger.info(f"Round Robin scheduling (q={valid_quantum}) executed for {len(completed)} processes.")
    return completed, segments


def calculate_metrics(processes: Sequence[Process]) -> dict[str, float]:
    """Calculates Average Waiting Time and Average Turnaround Time."""
    if not processes:
        return {"avg_waiting_time": 0.0, "avg_turnaround_time": 0.0, "total_processes": 0}

    total_wt = sum(p.waiting_time for p in processes)
    total_tat = sum(p.turnaround_time for p in processes)
    n = len(processes)

    return {
        "avg_waiting_time": round(total_wt / n, 2),
        "avg_turnaround_time": round(total_tat / n, 2),
        "total_processes": n,
    }


def generate_gantt_chart(segments: Sequence[TimelineSegment]) -> str:
    """Formats execution timeline segments into a textual ASCII Gantt chart."""
    return render_gantt_ascii(segments)
