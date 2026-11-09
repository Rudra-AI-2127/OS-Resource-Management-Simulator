"""
Deadlock Management Module — OS Resource Management Simulator.
Implements Dijkstra's Banker's Algorithm for multi-instance resource systems.
Computes Need Matrix, checks system safety, generates Safe Execution Sequences,
and validates dynamic resource requests with speculative rollback protection.
Provides step-by-step Work/Finish tracing and formatted matrix tables.
"""

import copy
from typing import Optional, Sequence, Union
from utils.logger import get_logger
from utils.helpers import format_table
from utils.validators import (
    DeadlockState,
    validate_bankers_matrix,
    validate_non_negative_int,
)

logger = get_logger()


def calculate_need(
    max_matrix: Sequence[Sequence[int]],
    allocation_matrix: Sequence[Sequence[int]],
) -> list[list[int]]:
    """
    Computes the Need matrix: Need[i][j] = Max[i][j] - Allocation[i][j].

    Validates:
    - Matrices are non-empty.
    - Matching row counts (number of processes).
    - Matching column counts (number of resource types).
    - Resource counts are non-negative.
    - Allocation does not exceed Max Demand (Allocation[i][j] <= Max[i][j]).
    """
    if not max_matrix or not allocation_matrix:
        err = "Max Demand and Allocation matrices cannot be empty."
        logger.warning(err)
        raise ValueError(err)

    n = len(max_matrix)
    if len(allocation_matrix) != n:
        err = f"Dimension mismatch: Max rows ({n}) != Allocation rows ({len(allocation_matrix)})."
        logger.warning(err)
        raise ValueError(err)

    if n == 0 or len(max_matrix[0]) == 0:
        err = "Matrices must contain at least one process and one resource type."
        logger.warning(err)
        raise ValueError(err)

    m = len(max_matrix[0])
    need: list[list[int]] = []

    for i in range(n):
        if len(max_matrix[i]) != m:
            err = f"Max Demand row {i} has {len(max_matrix[i])} columns, expected {m}."
            logger.warning(err)
            raise ValueError(err)
        if len(allocation_matrix[i]) != m:
            err = f"Allocation row {i} has {len(allocation_matrix[i])} columns, expected {m}."
            logger.warning(err)
            raise ValueError(err)

        row: list[int] = []
        for j in range(m):
            alloc = validate_non_negative_int(
                allocation_matrix[i][j], f"Allocation[P{i}][R{j}]"
            )
            maximum = validate_non_negative_int(
                max_matrix[i][j], f"MaxDemand[P{i}][R{j}]"
            )
            if alloc > maximum:
                err = f"Allocation ({alloc}) exceeds Max Demand ({maximum}) at Process P{i}, Resource {j}."
                logger.warning(err)
                raise ValueError(err)
            row.append(maximum - alloc)
        need.append(row)

    return need


def bankers_algorithm(state: DeadlockState) -> tuple[bool, list[str]]:
    """
    Executes Dijkstra's Banker's Safety Algorithm.

    Invariants:
    - Never mutates state.available or state.allocation.
    - Uses Work and Finish vectors.
    - Returns (is_safe, safe_sequence).
    """
    n = len(state.process_ids)
    m = len(state.resource_ids)

    # Step 1: Initialize Work and Finish vectors
    work = list(state.available)
    finish = [False] * n
    safe_sequence: list[str] = []

    # Step 2: Iteratively find a process Pi such that:
    # Finish[i] == False and Need[i][j] <= Work[j] for all j in 0..m-1
    while len(safe_sequence) < n:
        found_candidate = False
        for i in range(n):
            if not finish[i]:
                can_allocate = True
                for j in range(m):
                    if state.need[i][j] > work[j]:
                        can_allocate = False
                        break

                if can_allocate:
                    # Step 3: Speculatively assume Pi finishes and returns resources
                    for j in range(m):
                        work[j] += state.allocation[i][j]
                    finish[i] = True
                    safe_sequence.append(state.process_ids[i])
                    found_candidate = True
                    break

        if not found_candidate:
            # Cannot find any candidate process; system is in unsafe state
            logger.warning("Banker's Algorithm: System is in UNSAFE state. No complete safe sequence exists.")
            return False, []

    logger.info(f"Banker's Algorithm: SAFE state detected. Safe sequence: {' -> '.join(safe_sequence)}")
    return True, safe_sequence


def check_safe_state(state: DeadlockState) -> bool:
    """Returns True if the system state is SAFE, False otherwise."""
    is_safe, _ = bankers_algorithm(state)
    return is_safe


def request_resources(
    state: DeadlockState,
    pid: str,
    request_vector: Sequence[int],
    commit: bool = True,
) -> tuple[bool, str, list[str]]:
    """
    Evaluates a dynamic resource request from process `pid`.

    Adheres strictly to the Banker's Resource-Request protocol:
    1. Condition 1: Check Request <= Need (Process claim validity).
    2. Condition 2: Check Request <= Available (Current capacity validity).
    3. Speculative Allocation: Create candidate state with resources allocated.
    4. Run Safety Check:
       - If Safe: Commit tentative allocation if `commit` is True, and return (True, msg, safe_seq).
       - If Unsafe: Rollback completely, leave original state untouched, and return (False, msg, []).
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

    # Validate non-negative numbers
    for j in range(m):
        validate_non_negative_int(
            request_vector[j], f"Request for resource {state.resource_ids[j]}"
        )

    # Condition 1: Check Request <= Need
    for j in range(m):
        req_val = request_vector[j]
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

    # Step 3: Speculative Allocation on a deep copy
    temp_state = copy.deepcopy(state)
    for j in range(m):
        temp_state.available[j] -= request_vector[j]
        temp_state.allocation[p_idx][j] += request_vector[j]
        temp_state.need[p_idx][j] -= request_vector[j]

    # Step 4: Run Safety Check on tentative state
    is_safe, safe_seq = bankers_algorithm(temp_state)

    if is_safe:
        if commit:
            # Commit changes to official state
            for j in range(m):
                state.available[j] = temp_state.available[j]
                state.allocation[p_idx][j] = temp_state.allocation[p_idx][j]
                state.need[p_idx][j] = temp_state.need[p_idx][j]
        msg = f"Resource request granted for {pid}. System remains in a SAFE state."
        logger.info(msg)
        return True, msg, safe_seq
    else:
        # Rollback: original state remains untouched
        msg = f"Resource request denied for {pid}: Granting would transition system into an UNSAFE state."
        logger.warning(msg)
        return False, msg, []


def display_safe_sequence(safe_sequence: Sequence[str]) -> str:
    """Formats safe sequence into 'P1 -> P3 -> P4 -> P0 -> P2' string."""
    if not safe_sequence:
        return "None (System is in an UNSAFE state)"
    return " -> ".join(safe_sequence)


def format_deadlock_matrices(state: DeadlockState) -> str:
    """
    Renders an ASCII tabular representation of Allocation, Max Demand,
    and Need matrices alongside the Available resource vector.
    """
    headers = (
        ["PID"]
        + [f"Alloc {r}" for r in state.resource_ids]
        + [f"Max {r}" for r in state.resource_ids]
        + [f"Need {r}" for r in state.resource_ids]
    )
    rows: list[list[Union[str, int]]] = []
    for i, pid in enumerate(state.process_ids):
        row: list[Union[str, int]] = [pid]
        row.extend(state.allocation[i])
        row.extend(state.max_demand[i])
        row.extend(state.need[i])
        rows.append(row)

    table_str = format_table(headers, rows)
    avail_str = ", ".join(
        f"{r}: {state.available[j]}" for j, r in enumerate(state.resource_ids)
    )
    return (
        f"=== SYSTEM RESOURCE MATRICES ===\n"
        f"{table_str}\n"
        f"Available Resources: [{avail_str}]"
    )


def explain_safety_steps(state: DeadlockState) -> tuple[bool, list[str], list[str]]:
    """
    Traces the execution of the Safety Algorithm step-by-step.
    Returns:
        (is_safe, safe_sequence, trace_log)
    """
    n = len(state.process_ids)
    m = len(state.resource_ids)

    work = list(state.available)
    finish = [False] * n
    safe_sequence: list[str] = []
    trace_log: list[str] = []

    trace_log.append(
        f"Step 0: Initial Work = {work}, Finish = {dict(zip(state.process_ids, finish))}"
    )

    step = 1
    while len(safe_sequence) < n:
        found = False
        for i in range(n):
            if not finish[i]:
                pid = state.process_ids[i]
                need_i = state.need[i]
                if all(need_i[j] <= work[j] for j in range(m)):
                    old_work = list(work)
                    for j in range(m):
                        work[j] += state.allocation[i][j]
                    finish[i] = True
                    safe_sequence.append(pid)
                    found = True
                    trace_log.append(
                        f"Step {step}: Select {pid} (Need={need_i} <= Work={old_work}). "
                        f"Allocated={state.allocation[i]} released -> New Work={work}"
                    )
                    step += 1
                    break

        if not found:
            unfinished = [state.process_ids[i] for i in range(n) if not finish[i]]
            trace_log.append(
                f"Deadlock detected! No remaining process can satisfy Need <= Work. "
                f"Unfinished processes: {unfinished}. Work = {work}"
            )
            return False, [], trace_log

    trace_log.append(
        f"Conclusion: System is in a SAFE state. Execution sequence: {' -> '.join(safe_sequence)}"
    )
    return True, safe_sequence, trace_log
