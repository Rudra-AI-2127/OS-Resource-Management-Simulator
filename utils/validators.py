"""
Defensive input validation gateway for OS Resource Management Simulator.
Enforces data types, range bounds, collection integrity, and dimensional consistency.
"""

from dataclasses import dataclass, field
from typing import Any, Optional, Union
from utils.logger import get_logger

logger = get_logger()


@dataclass
class Process:
    """Models an OS process throughout its scheduling lifecycle."""
    pid: str
    arrival_time: int
    burst_time: int
    priority: int = 0
    remaining_time: int = 0
    start_time: Optional[int] = None
    completion_time: int = 0
    turnaround_time: int = 0
    waiting_time: int = 0
    response_time: int = 0

    def __post_init__(self):
        if self.remaining_time == 0 and self.burst_time > 0:
            self.remaining_time = self.burst_time

    def to_dict(self) -> dict:
        return {
            "pid": self.pid,
            "arrival_time": self.arrival_time,
            "burst_time": self.burst_time,
            "priority": self.priority,
            "completion_time": self.completion_time,
            "turnaround_time": self.turnaround_time,
            "waiting_time": self.waiting_time,
            "response_time": self.response_time,
        }


@dataclass
class DeadlockState:
    """Encapsulates system resource state for Banker's Algorithm."""
    process_ids: list[str]
    resource_ids: list[str]
    available: list[int]
    allocation: list[list[int]]
    max_demand: list[list[int]]
    need: list[list[int]] = field(default_factory=list)

    def __post_init__(self):
        if not self.need:
            self.calculate_need()

    def calculate_need(self) -> list[list[int]]:
        n = len(self.process_ids)
        m = len(self.resource_ids)
        self.need = [
            [self.max_demand[i][j] - self.allocation[i][j] for j in range(m)]
            for i in range(n)
        ]
        return self.need


def validate_positive_int(value: Any, field_name: str) -> int:
    """Validates that a value can be converted to an integer and is strictly positive (> 0)."""
    try:
        val = int(value)
    except (ValueError, TypeError):
        err_msg = f"{field_name} must be an integer, got: {value!r}"
        logger.warning(err_msg)
        raise ValueError(err_msg)

    if val <= 0:
        err_msg = f"{field_name} must be strictly positive (> 0), got: {val}"
        logger.warning(err_msg)
        raise ValueError(err_msg)

    return val


def validate_non_negative_int(value: Any, field_name: str) -> int:
    """Validates that a value can be converted to an integer and is non-negative (>= 0)."""
    try:
        val = int(value)
    except (ValueError, TypeError):
        err_msg = f"{field_name} must be an integer, got: {value!r}"
        logger.warning(err_msg)
        raise ValueError(err_msg)

    if val < 0:
        err_msg = f"{field_name} must be non-negative (>= 0), got: {val}"
        logger.warning(err_msg)
        raise ValueError(err_msg)

    return val


def validate_process_list(raw_processes: list[Union[dict, Process]]) -> list[Process]:
    """
    Validates a collection of processes.
    Enforces non-empty collection, unique PIDs, arrival_time >= 0, and burst_time > 0.
    """
    if not raw_processes:
        err_msg = "Process list cannot be empty."
        logger.warning(err_msg)
        raise ValueError(err_msg)

    validated_processes: list[Process] = []
    seen_pids: set[str] = set()

    for idx, item in enumerate(raw_processes):
        if isinstance(item, Process):
            pid = str(item.pid).strip()
            at = item.arrival_time
            bt = item.burst_time
            prio = item.priority
        elif isinstance(item, dict):
            pid = str(item.get("pid", f"P{idx + 1}")).strip()
            at = item.get("arrival_time", item.get("at", 0))
            bt = item.get("burst_time", item.get("bt"))
            prio = item.get("priority", item.get("prio", 0))
        else:
            err_msg = f"Invalid process element format at index {idx}: {item!r}"
            logger.warning(err_msg)
            raise ValueError(err_msg)

        if not pid:
            err_msg = f"Process at index {idx} has an empty PID."
            logger.warning(err_msg)
            raise ValueError(err_msg)

        if pid in seen_pids:
            err_msg = f"Duplicate Process ID detected: {pid!r}."
            logger.warning(err_msg)
            raise ValueError(err_msg)
        seen_pids.add(pid)

        valid_at = validate_non_negative_int(at, f"Arrival time for {pid}")
        valid_bt = validate_positive_int(bt, f"Burst time for {pid}")
        valid_prio = validate_non_negative_int(prio, f"Priority for {pid}")

        validated_processes.append(
            Process(pid=pid, arrival_time=valid_at, burst_time=valid_bt, priority=valid_prio)
        )

    return validated_processes


def validate_memory_inputs(
    blocks: list[Any], requests: list[Union[tuple[str, Any], dict[str, Any]]]
) -> tuple[list[int], list[tuple[str, int]]]:
    """
    Validates memory blocks and process allocation requests.
    Enforces non-empty collections and positive sizes.
    """
    if not blocks:
        err_msg = "Memory block list cannot be empty."
        logger.warning(err_msg)
        raise ValueError(err_msg)

    if not requests:
        err_msg = "Memory request list cannot be empty."
        logger.warning(err_msg)
        raise ValueError(err_msg)

    valid_blocks: list[int] = []
    for idx, b in enumerate(blocks):
        valid_blocks.append(validate_positive_int(b, f"Memory block #{idx + 1} size"))

    valid_requests: list[tuple[str, int]] = []
    for idx, r in enumerate(requests):
        if isinstance(r, (tuple, list)) and len(r) == 2:
            pid, size = r[0], r[1]
        elif isinstance(r, dict):
            pid = r.get("pid", f"P{idx + 1}")
            size = r.get("size", r.get("size_kb"))
        else:
            err_msg = f"Invalid memory request format at index {idx}: {r!r}"
            logger.warning(err_msg)
            raise ValueError(err_msg)

        valid_size = validate_positive_int(size, f"Memory request for {pid}")
        valid_requests.append((str(pid), valid_size))

    return valid_blocks, valid_requests


def validate_bankers_matrix(
    allocation: list[list[int]],
    max_demand: list[list[int]],
    available: list[int],
    process_ids: Optional[list[str]] = None,
    resource_ids: Optional[list[str]] = None,
) -> DeadlockState:
    """
    Validates Banker's Algorithm matrix dimensions and consistency.
    Enforces allocation[i][j] <= max_demand[i][j] and available[j] >= 0.
    """
    if not allocation or not max_demand or not available:
        err_msg = "Allocation, Max Demand, and Available structures cannot be empty."
        logger.warning(err_msg)
        raise ValueError(err_msg)

    n = len(allocation)
    m = len(available)

    if len(max_demand) != n:
        err_msg = f"Dimension mismatch: Allocation rows ({n}) != Max Demand rows ({len(max_demand)})."
        logger.warning(err_msg)
        raise ValueError(err_msg)

    for i in range(n):
        if len(allocation[i]) != m:
            err_msg = f"Row {i} in Allocation has {len(allocation[i])} resources, expected {m}."
            logger.warning(err_msg)
            raise ValueError(err_msg)
        if len(max_demand[i]) != m:
            err_msg = f"Row {i} in Max Demand has {len(max_demand[i])} resources, expected {m}."
            logger.warning(err_msg)
            raise ValueError(err_msg)

        for j in range(m):
            alloc_val = validate_non_negative_int(allocation[i][j], f"Allocation[{i}][{j}]")
            max_val = validate_non_negative_int(max_demand[i][j], f"MaxDemand[{i}][{j}]")
            if alloc_val > max_val:
                err_msg = (
                    f"Allocation exceeds Max Demand at Process {i}, Resource {j}: "
                    f"Alloc={alloc_val} > Max={max_val}."
                )
                logger.warning(err_msg)
                raise ValueError(err_msg)

    for j in range(m):
        validate_non_negative_int(available[j], f"Available[{j}]")

    p_ids = process_ids or [f"P{i}" for i in range(n)]
    r_ids = resource_ids or [chr(ord('A') + j) for j in range(m)]

    state = DeadlockState(
        process_ids=p_ids,
        resource_ids=r_ids,
        available=list(available),
        allocation=[list(row) for row in allocation],
        max_demand=[list(row) for row in max_demand],
    )
    return state


def validate_cylinder_requests(
    requests: list[Any],
    initial_head: Any,
    total_cylinders: Any = 200,
    direction: str = "up",
) -> tuple[list[int], int, int, str]:
    """
    Validates disk cylinder requests, head position, and boundaries.
    Enforces head and requests in [0, total_cylinders - 1].
    """
    if not requests:
        err_msg = "Disk cylinder request queue cannot be empty."
        logger.warning(err_msg)
        raise ValueError(err_msg)

    max_c = validate_positive_int(total_cylinders, "Total Cylinders")
    head = validate_non_negative_int(initial_head, "Initial Head Position")

    if head >= max_c:
        err_msg = f"Initial head position ({head}) out of bounds [0, {max_c - 1}]."
        logger.warning(err_msg)
        raise ValueError(err_msg)

    valid_reqs: list[int] = []
    for idx, r in enumerate(requests):
        cyl = validate_non_negative_int(r, f"Cylinder request #{idx + 1}")
        if cyl >= max_c:
            err_msg = f"Cylinder request ({cyl}) at index {idx} out of bounds [0, {max_c - 1}]."
            logger.warning(err_msg)
            raise ValueError(err_msg)
        valid_reqs.append(cyl)

    dir_clean = str(direction).strip().lower()
    if dir_clean not in ("up", "down"):
        err_msg = f"Invalid disk head direction '{direction}'. Must be 'up' or 'down'."
        logger.warning(err_msg)
        raise ValueError(err_msg)

    return valid_reqs, head, max_c, dir_clean


def validate_menu_choice(choice: Any, min_val: int = 1, max_val: int = 6) -> int:
    """Validates user menu numeric selection."""
    try:
        val = int(choice)
    except (ValueError, TypeError):
        raise ValueError(f"Menu choice must be a number between {min_val} and {max_val}.")

    if val < min_val or val > max_val:
        raise ValueError(f"Invalid option {val}. Please enter a choice between {min_val} and {max_val}.")

    return val
