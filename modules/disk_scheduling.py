"""
Disk Scheduling Module — OS Resource Management Simulator.
Implements FCFS, SSTF, SCAN (Elevator), and C-SCAN (Circular SCAN).
Calculates seek paths, total head movement, and average seek distance.
"""

from dataclasses import dataclass, field
from typing import Any, Sequence
from utils.logger import get_logger
from utils.validators import validate_cylinder_requests

logger = get_logger()


@dataclass
class DiskSchedulingResult:
    """Encapsulates the complete trajectory and seek metrics of a disk scheduling algorithm."""
    algorithm: str
    initial_head: int
    seek_sequence: list[int]
    step_movements: list[int]
    total_head_movement: int
    average_head_movement: float
    requests_serviced: int


def calculate_head_movement(sequence: Sequence[int], num_requests: int) -> tuple[int, list[int], float]:
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
    requests: Sequence[Any], initial_head: Any, total_cylinders: Any = 200
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
        step_movements=steps,
        total_head_movement=total_seek,
        average_head_movement=avg_seek,
        requests_serviced=num_reqs,
    )


def sstf(
    requests: Sequence[Any], initial_head: Any, total_cylinders: Any = 200
) -> DiskSchedulingResult:
    """
    Shortest Seek Time First (SSTF) Disk Scheduling.
    Greedily selects the unserviced cylinder with the minimal distance to the current head.
    """
    valid_reqs, head, max_c, _ = validate_cylinder_requests(
        list(requests), initial_head, total_cylinders, direction="up"
    )

    pending = list(valid_reqs)
    sequence = [head]
    current_pos = head

    while pending:
        # Find cylinder with minimum absolute distance
        closest = min(pending, key=lambda cyl: (abs(cyl - current_pos), cyl))
        pending.remove(closest)
        sequence.append(closest)
        current_pos = closest

    num_reqs = len(valid_reqs)
    total_seek, steps, avg_seek = calculate_head_movement(sequence, num_reqs)

    logger.info(f"SSTF Disk scheduling: {num_reqs} requests, Total Seek={total_seek}.")
    return DiskSchedulingResult(
        algorithm="SSTF",
        initial_head=head,
        seek_sequence=sequence,
        step_movements=steps,
        total_head_movement=total_seek,
        average_head_movement=avg_seek,
        requests_serviced=num_reqs,
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
    servicing requests along the path, then reverses direction.
    """
    valid_reqs, head, max_c, dir_str = validate_cylinder_requests(
        list(requests), initial_head, total_cylinders, direction=direction
    )

    sequence = [head]
    upper_boundary = max_c - 1
    lower_boundary = 0

    left = sorted([r for r in valid_reqs if r < head])
    right = sorted([r for r in valid_reqs if r >= head])

    if dir_str == "up":
        # Service upward to upper boundary
        for r in right:
            sequence.append(r)
        # Touch boundary if there are requests on the left
        if left:
            sequence.append(upper_boundary)
            # Reverse and service downward
            for r in reversed(left):
                sequence.append(r)
    else:
        # Service downward to lower boundary
        for r in reversed(left):
            sequence.append(r)
        # Touch boundary if there are requests on the right
        if right:
            sequence.append(lower_boundary)
            # Reverse and service upward
            for r in right:
                sequence.append(r)

    num_reqs = len(valid_reqs)
    total_seek, steps, avg_seek = calculate_head_movement(sequence, num_reqs)

    logger.info(f"SCAN Disk scheduling ({dir_str}): Total Seek={total_seek}.")
    return DiskSchedulingResult(
        algorithm="SCAN",
        initial_head=head,
        seek_sequence=sequence,
        step_movements=steps,
        total_head_movement=total_seek,
        average_head_movement=avg_seek,
        requests_serviced=num_reqs,
    )


def cscan(
    requests: Sequence[Any],
    initial_head: Any,
    total_cylinders: Any = 200,
    direction: str = "up",
) -> DiskSchedulingResult:
    """
    Circular SCAN (C-SCAN) Disk Scheduling.
    Sweeps in initial direction to boundary, jumps to the opposite boundary without
    servicing requests, and resumes sweeping in original direction.
    Seek jump distance is included in total head movement.
    """
    valid_reqs, head, max_c, dir_str = validate_cylinder_requests(
        list(requests), initial_head, total_cylinders, direction=direction
    )

    sequence = [head]
    upper_boundary = max_c - 1
    lower_boundary = 0

    left = sorted([r for r in valid_reqs if r < head])
    right = sorted([r for r in valid_reqs if r >= head])

    if dir_str == "up":
        # Sweep upward to upper boundary
        for r in right:
            sequence.append(r)
        if left:
            sequence.append(upper_boundary)
            sequence.append(lower_boundary)  # Return jump
            for r in left:
                sequence.append(r)
    else:
        # Sweep downward to lower boundary
        for r in reversed(left):
            sequence.append(r)
        if right:
            sequence.append(lower_boundary)
            sequence.append(upper_boundary)  # Return jump
            for r in reversed(right):
                sequence.append(r)

    num_reqs = len(valid_reqs)
    total_seek, steps, avg_seek = calculate_head_movement(sequence, num_reqs)

    logger.info(f"C-SCAN Disk scheduling ({dir_str}): Total Seek={total_seek}.")
    return DiskSchedulingResult(
        algorithm="C-SCAN",
        initial_head=head,
        seek_sequence=sequence,
        step_movements=steps,
        total_head_movement=total_seek,
        average_head_movement=avg_seek,
        requests_serviced=num_reqs,
    )
