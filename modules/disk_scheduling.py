"""
Disk Scheduling Module — OS Resource Management Simulator.
Implements FCFS, SSTF, SCAN (Elevator), and C-SCAN (Circular SCAN).
Calculates complete seek paths, service sequences, total head movement,
and average seek distances. Supports comparative benchmarking and visualization data.
"""

from dataclasses import dataclass, field
import copy
from typing import Any, Optional, Sequence
from utils.logger import get_logger
from utils.helpers import format_table
from utils.validators import validate_cylinder_requests

logger = get_logger()


@dataclass
class DiskSchedulingResult:
    """Encapsulates the complete trajectory and seek metrics of a disk scheduling algorithm."""
    algorithm: str
    initial_head: int
    seek_sequence: list[int]
    service_sequence: list[int]
    step_movements: list[int]
    total_head_movement: int
    average_head_movement: float
    requests_serviced: int
    direction: str = "up"
    total_cylinders: int = 200
    min_cylinder: int = 0
    max_cylinder: int = 199


def calculate_head_movement(
    sequence: Sequence[int], num_requests: int
) -> tuple[int, list[int], float]:
    """
    Computes step-by-step cylinder movements, total head movement, and average seek distance.
    Average Seek = Total Head Movement / num_requests.
    """
    if len(sequence) <= 1:
        return 0, [], 0.0

    steps: list[int] = []
    total = 0
    for i in range(1, len(sequence)):
        diff = abs(sequence[i] - sequence[i - 1])
        steps.append(diff)
        total += diff

    avg = round(total / num_requests, 2) if num_requests > 0 else 0.0
    return total, steps, avg


def fcfs_disk(
    requests: Sequence[Any],
    initial_head: Any,
    total_cylinders: Any = 200,
) -> DiskSchedulingResult:
    """
    First-Come, First-Served (FCFS) Disk Scheduling.
    Services cylinder requests strictly in arrival order.
    """
    valid_reqs, head, max_c, _ = validate_cylinder_requests(
        list(requests), initial_head, total_cylinders, direction="up"
    )

    sequence = [head] + valid_reqs
    num_reqs = len(valid_reqs)
    total_seek, steps, avg_seek = calculate_head_movement(sequence, num_reqs)

    logger.info(f"FCFS Disk scheduling: {num_reqs} requests, Total Seek={total_seek}.")
    return DiskSchedulingResult(
        algorithm="FCFS",
        initial_head=head,
        seek_sequence=sequence,
        service_sequence=list(valid_reqs),
        step_movements=steps,
        total_head_movement=total_seek,
        average_head_movement=avg_seek,
        requests_serviced=num_reqs,
        direction="up",
        total_cylinders=max_c,
        min_cylinder=0,
        max_cylinder=max_c - 1,
    )


def sstf(
    requests: Sequence[Any],
    initial_head: Any,
    total_cylinders: Any = 200,
) -> DiskSchedulingResult:
    """
    Shortest Seek Time First (SSTF) Disk Scheduling.
    Greedily selects the unserviced cylinder with minimal distance to the current head.
    Ties broken deterministically by selecting the lower cylinder index.
    """
    valid_reqs, head, max_c, _ = validate_cylinder_requests(
        list(requests), initial_head, total_cylinders, direction="up"
    )

    pending = list(valid_reqs)
    sequence = [head]
    serviced: list[int] = []
    current_pos = head

    while pending:
        # Find cylinder with minimum absolute distance; break ties by lower cylinder number
        closest = min(pending, key=lambda cyl: (abs(cyl - current_pos), cyl))
        pending.remove(closest)
        sequence.append(closest)
        serviced.append(closest)
        current_pos = closest

    num_reqs = len(valid_reqs)
    total_seek, steps, avg_seek = calculate_head_movement(sequence, num_reqs)

    logger.info(f"SSTF Disk scheduling: {num_reqs} requests, Total Seek={total_seek}.")
    return DiskSchedulingResult(
        algorithm="SSTF",
        initial_head=head,
        seek_sequence=sequence,
        service_sequence=serviced,
        step_movements=steps,
        total_head_movement=total_seek,
        average_head_movement=avg_seek,
        requests_serviced=num_reqs,
        direction="up",
        total_cylinders=max_c,
        min_cylinder=0,
        max_cylinder=max_c - 1,
    )


def scan(
    requests: Sequence[Any],
    initial_head: Any,
    total_cylinders: Any = 200,
    direction: str = "up",
) -> DiskSchedulingResult:
    """
    SCAN (Elevator) Disk Scheduling.
    Moves in initial direction to the boundary cylinder (max_cylinders - 1 or 0),
    servicing requests along the path, then reverses direction to service remaining requests.
    """
    valid_reqs, head, max_c, dir_str = validate_cylinder_requests(
        list(requests), initial_head, total_cylinders, direction=direction
    )

    sequence = [head]
    serviced: list[int] = []
    upper_boundary = max_c - 1
    lower_boundary = 0

    left = sorted([r for r in valid_reqs if r < head])
    right = sorted([r for r in valid_reqs if r >= head])

    if dir_str == "up":
        # Service upward to upper boundary
        for r in right:
            sequence.append(r)
            serviced.append(r)
        # Touch boundary if there are requests on the left
        if left:
            if not sequence or sequence[-1] != upper_boundary:
                sequence.append(upper_boundary)
            # Reverse and service downward
            for r in reversed(left):
                sequence.append(r)
                serviced.append(r)
    else:
        # Service downward to lower boundary
        for r in reversed(left):
            sequence.append(r)
            serviced.append(r)
        # Touch boundary if there are requests on the right
        if right:
            if not sequence or sequence[-1] != lower_boundary:
                sequence.append(lower_boundary)
            # Reverse and service upward
            for r in right:
                sequence.append(r)
                serviced.append(r)

    num_reqs = len(valid_reqs)
    total_seek, steps, avg_seek = calculate_head_movement(sequence, num_reqs)

    logger.info(f"SCAN Disk scheduling ({dir_str}): Total Seek={total_seek}.")
    return DiskSchedulingResult(
        algorithm="SCAN",
        initial_head=head,
        seek_sequence=sequence,
        service_sequence=serviced,
        step_movements=steps,
        total_head_movement=total_seek,
        average_head_movement=avg_seek,
        requests_serviced=num_reqs,
        direction=dir_str,
        total_cylinders=max_c,
        min_cylinder=0,
        max_cylinder=max_c - 1,
    )


def cscan(
    requests: Sequence[Any],
    initial_head: Any,
    total_cylinders: Any = 200,
    direction: str = "up",
) -> DiskSchedulingResult:
    """
    Circular SCAN (C-SCAN) Disk Scheduling.
    Sweeps in initial direction to the boundary, jumps to the opposite boundary without
    servicing requests, and resumes sweeping in original direction.
    Boundary seek jump distance is included in total head movement.
    """
    valid_reqs, head, max_c, dir_str = validate_cylinder_requests(
        list(requests), initial_head, total_cylinders, direction=direction
    )

    sequence = [head]
    serviced: list[int] = []
    upper_boundary = max_c - 1
    lower_boundary = 0

    left = sorted([r for r in valid_reqs if r < head])
    right = sorted([r for r in valid_reqs if r >= head])

    if dir_str == "up":
        # Sweep upward to upper boundary
        for r in right:
            sequence.append(r)
            serviced.append(r)
        if left:
            if not sequence or sequence[-1] != upper_boundary:
                sequence.append(upper_boundary)
            sequence.append(lower_boundary)  # Rapid return jump
            for r in left:
                # If a request was exactly at 0, avoid double visit
                if sequence[-1] == lower_boundary and r == lower_boundary:
                    serviced.append(r)
                    continue
                sequence.append(r)
                serviced.append(r)
    else:
        # Sweep downward to lower boundary
        for r in reversed(left):
            sequence.append(r)
            serviced.append(r)
        if right:
            if not sequence or sequence[-1] != lower_boundary:
                sequence.append(lower_boundary)
            sequence.append(upper_boundary)  # Rapid return jump
            for r in reversed(right):
                if sequence[-1] == upper_boundary and r == upper_boundary:
                    serviced.append(r)
                    continue
                sequence.append(r)
                serviced.append(r)

    num_reqs = len(valid_reqs)
    total_seek, steps, avg_seek = calculate_head_movement(sequence, num_reqs)

    logger.info(f"C-SCAN Disk scheduling ({dir_str}): Total Seek={total_seek}.")
    return DiskSchedulingResult(
        algorithm="C-SCAN",
        initial_head=head,
        seek_sequence=sequence,
        service_sequence=serviced,
        step_movements=steps,
        total_head_movement=total_seek,
        average_head_movement=avg_seek,
        requests_serviced=num_reqs,
        direction=dir_str,
        total_cylinders=max_c,
        min_cylinder=0,
        max_cylinder=max_c - 1,
    )


def compare_disk_algorithms(
    requests: Sequence[Any],
    initial_head: Any,
    total_cylinders: Any = 200,
    direction: str = "up",
) -> dict[str, Any]:
    """
    Executes all four disk scheduling algorithms on identical inputs
    and produces side-by-side performance metrics.
    """
    req_copy = list(requests)
    fcfs_res = fcfs_disk(req_copy, initial_head, total_cylinders)
    sstf_res = sstf(req_copy, initial_head, total_cylinders)
    scan_res = scan(req_copy, initial_head, total_cylinders, direction=direction)
    cscan_res = cscan(req_copy, initial_head, total_cylinders, direction=direction)

    results = {
        "FCFS": fcfs_res,
        "SSTF": sstf_res,
        "SCAN": scan_res,
        "C-SCAN": cscan_res,
    }

    comparison_table = [
        {
            "algorithm": name,
            "total_head_movement": res.total_head_movement,
            "average_head_movement": res.average_head_movement,
            "requests_serviced": res.requests_serviced,
            "seek_sequence_length": len(res.seek_sequence),
        }
        for name, res in results.items()
    ]

    best_algo = min(results.items(), key=lambda item: item[1].total_head_movement)[0]

    return {
        "results": results,
        "comparison_table": comparison_table,
        "best_algorithm": best_algo,
    }


def display_disk_result(res: DiskSchedulingResult) -> str:
    """Formats disk scheduling result into a clean ASCII report."""
    headers = ["Step #", "From Cylinder", "To Cylinder", "Seek Distance"]
    rows = []
    for i in range(1, len(res.seek_sequence)):
        from_c = res.seek_sequence[i - 1]
        to_c = res.seek_sequence[i]
        diff = res.step_movements[i - 1]
        rows.append([str(i), str(from_c), str(to_c), f"{diff} cyl"])

    table_str = format_table(headers, rows)
    seq_str = " -> ".join(map(str, res.seek_sequence))
    srv_str = " -> ".join(map(str, res.service_sequence))

    return (
        f"=== DISK SCHEDULING: {res.algorithm} (Direction: {res.direction}) ===\n"
        f"Initial Head Position: {res.initial_head} | Total Cylinders: {res.total_cylinders}\n"
        f"Head Seek Path:        {seq_str}\n"
        f"Service Order:         {srv_str}\n"
        f"Step Seek Table:\n"
        f"{table_str}\n"
        f"Total Head Movement:   {res.total_head_movement} cylinders\n"
        f"Average Seek Distance: {res.average_head_movement:.2f} cylinders/request\n"
        f"Requests Serviced:     {res.requests_serviced}\n"
    )
