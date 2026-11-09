"""
Deadlock Management Module — OS Resource Management Simulator.
Implements Dijkstra's Banker's Algorithm for multi-instance resource systems.
Computes Need Matrix, checks system safety, generates Safe Execution Sequences,
and validates dynamic resource requests with rollback protection.
"""

import copy
from typing import Optional, Sequence
from utils.logger import get_logger
from utils.validators import DeadlockState, validate_bankers_matrix, validate_non_negative_int

logger = get_logger()


def calculate_need(
    max_matrix: Sequence[Sequence[int]], allocation_matrix: Sequence[Sequence[int]]
) -> list[list[int]]:
    """
    Computes the Need matrix: Need[i][j] = Max[i][j] - Allocation[i][j].
    """
    n = len(max_matrix)
    m = len(max_matrix[0]) if n > 0 else 0
    need: list[list[int]] = []

    for i in range(n):
        row: list[int] = []
        for j in range(m):
            alloc = allocation_matrix[i][j]
            maximum = max_matrix[i][j]
            if alloc > maximum:
                raise ValueError(f"Allocation ({alloc}) exceeds Max Demand ({maximum}) at P{i}, R{j}.")
            row.append(maximum - alloc)
        need.append(row)

    return need


def bankers_algorithm(state: DeadlockState) -> tuple[bool, list[str]]:
    """
    Executes Dijkstra's Banker's Safety Algorithm.
    Returns:
        (is_safe, safe_sequence): Tuple where is_safe is True if a safe sequence
        exists that allows all processes to finish without deadlock, False otherwise.
    """
    n = len(state.process_ids)
    m = len(state.resource_ids)

    # Step 1: Initialize Work and Finish vectors
    work = list(state.available)
    finish = [False] * n
    safe_sequence: list[str] = []

    # Step 2: Iteratively find a process Pi such that:
    # Finish[i] == False and Need[i][j] <= Work[j] for all j
    while len(safe_sequence) < n:
        found_candidate = False
        for i in range(n):
            if not finish[i]:
                # Check if Need[i] <= Work
                can_allocate = True
                for j in range(m):
                    if state.need[i][j] > work[j]:
                        can_allocate = False
                        break

                if can_allocate:
                    # Step 3: Speculatively assume Pi finishes and releases resources
                    for j in range(m):
                        work[j] += state.allocation[i][j]
                    finish[i] = True
                    safe_sequence.append(state.process_ids[i])
                    found_candidate = True
                    break

        if not found_candidate:
            # Cannot find any candidate process; system is in unsafe state
            logger.warning("Banker's Algorithm: System is in UNSAFE state. No safe sequence exists.")
            return False, []

    logger.info(f"Banker's Algorithm: SAFE state detected. Safe sequence: {' -> '.join(safe_sequence)}")
    return True, safe_sequence


def check_safe_state(state: DeadlockState) -> bool:
    """Returns True if the system state is SAFE, False otherwise."""
    is_safe, _ = bankers_algorithm(state)
    return is_safe


def request_resources(
    state: DeadlockState, pid: str, request_vector: Sequence[int]
) -> tuple[bool, str, list[str]]:
    """
    Evaluates a dynamic resource request from a process.
    Adheres strictly to the Banker's Resource-Request protocol:
    1. Check Request <= Need
    2. Check Request <= Available
    3. Speculative allocation
    4. Run Safety Algorithm: commit if safe, rollback if unsafe.
    """
    if pid not in state.process_ids:
        err = f"Process {pid!r} not found in system state."
        logger.warning(err)
        return False, err, []

    p_idx = state.process_ids.index(pid)
    m = len(state.resource_ids)

    if len(request_vector) != m:
        err = f"Request vector length ({len(request_vector)}) does not match resource count ({m})."
        logger.warning(err)
        return False, err, []

    # Condition 1: Check Request <= Need
    for j in range(m):
        req_val = validate_non_negative_int(request_vector[j], f"Request for {state.resource_ids[j]}")
        if req_val > state.need[p_idx][j]:
            err = (
                f"Error: Process {pid} has exceeded its maximum claim! "
                f"Requested {req_val} for {state.resource_ids[j]}, Need is {state.need[p_idx][j]}."
            )
            logger.warning(err)
            return False, err, []

    # Condition 2: Check Request <= Available
    for j in range(m):
        if request_vector[j] > state.available[j]:
            msg = (
                f"Process {pid} must wait: Resources currently unavailable. "
                f"Requested {request_vector[j]} of {state.resource_ids[j]}, Available is {state.available[j]}."
            )
            logger.info(msg)
            return False, msg, []

    # Step 3: Speculative Allocation
    temp_state = copy.deepcopy(state)
    for j in range(m):
        temp_state.available[j] -= request_vector[j]
        temp_state.allocation[p_idx][j] += request_vector[j]
        temp_state.need[p_idx][j] -= request_vector[j]

    # Step 4: Run Safety Check on tentative state
    is_safe, safe_seq = bankers_algorithm(temp_state)

    if is_safe:
        # Commit changes to official state
        for j in range(m):
            state.available[j] = temp_state.available[j]
            state.allocation[p_idx][j] = temp_state.allocation[p_idx][j]
            state.need[p_idx][j] = temp_state.need[p_idx][j]
        msg = f"Resource request granted for {pid}. System remains in a SAFE state."
        logger.info(msg)
        return True, msg, safe_seq
    else:
        # Rollback (temp_state is discarded)
        msg = f"Resource request denied for {pid}: Granting would transition system into an UNSAFE state."
        logger.warning(msg)
        return False, msg, []


def display_safe_sequence(safe_sequence: Sequence[str]) -> str:
    """Formats safe sequence into 'P1 -> P3 -> P4 -> P0 -> P2' string."""
    if not safe_sequence:
        return "None (System is in an UNSAFE state)"
    return " -> ".join(safe_sequence)
