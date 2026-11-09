"""
Memory Management Module — OS Resource Management Simulator.
Implements First Fit, Best Fit, and Worst Fit dynamic partition allocation with block splitting.
Calculates allocated memory, remaining free memory, utilization, and external/internal fragmentation.
Provides comparative benchmarking across memory allocation strategies.
"""

from dataclasses import dataclass, field
import copy
from typing import Any, Optional, Sequence, Union
from utils.logger import get_logger
from utils.helpers import format_table
from utils.validators import validate_memory_inputs

logger = get_logger()


@dataclass
class MemoryBlock:
    """Models a physical memory block/partition in RAM."""
    block_id: int
    size: int
    allocated_pid: Optional[str] = None
    process_size: int = 0
    is_free: bool = True
    internal_fragmentation: int = 0


@dataclass
class MemoryAllocationResult:
    """Encapsulates the complete outcome of a memory allocation policy."""
    algorithm: str
    allocations: list[dict]
    unallocated_processes: list[str]
    total_memory_kb: int
    total_allocated_kb: int
    total_free_memory_kb: int
    successful_allocations: int
    failed_allocations: int
    memory_utilization: float
    external_fragmentation_kb: int
    internal_fragmentation_kb: int = 0
    remaining_blocks: list[dict] = field(default_factory=list)

    @property
    def used_memory_kb(self) -> int:
        return self.total_allocated_kb

    @property
    def free_memory_kb(self) -> int:
        return self.total_free_memory_kb


def _init_blocks(block_sizes: Sequence[int]) -> list[MemoryBlock]:
    """Initializes free memory blocks from raw size integers."""
    blocks: list[MemoryBlock] = []
    for idx, sz in enumerate(block_sizes):
        blocks.append(MemoryBlock(block_id=idx + 1, size=sz, is_free=True))
    return blocks


def _allocate(
    block_sizes: Sequence[int],
    requests: Sequence[Union[int, tuple[str, int], dict[str, Any]]],
    strategy: str,
) -> MemoryAllocationResult:
    """
    Core allocation engine supporting First Fit, Best Fit, and Worst Fit strategies.
    Implements dynamic block splitting and external fragmentation auditing.
    Guarantees input isolation by copying inputs before processing.
    """
    # Defensive isolation: deepcopy inputs so caller's structures are never mutated
    blocks_copy = copy.deepcopy(list(block_sizes))
    requests_copy = copy.deepcopy(list(requests))

    valid_blocks, valid_requests = validate_memory_inputs(blocks_copy, requests_copy)
    blocks = _init_blocks(valid_blocks)
    total_mem = sum(valid_blocks)

    allocations: list[dict] = []
    unallocated_processes: list[str] = []

    for pid, req_size in valid_requests:
        candidate_idx: Optional[int] = None

        if strategy == "First Fit":
            for idx, b in enumerate(blocks):
                if b.is_free and b.size >= req_size:
                    candidate_idx = idx
                    break

        elif strategy == "Best Fit":
            best_diff = float("inf")
            for idx, b in enumerate(blocks):
                if b.is_free and b.size >= req_size:
                    diff = b.size - req_size
                    if diff < best_diff:
                        best_diff = diff
                        candidate_idx = idx

        elif strategy == "Worst Fit":
            worst_diff = -1
            for idx, b in enumerate(blocks):
                if b.is_free and b.size >= req_size:
                    diff = b.size - req_size
                    if diff > worst_diff:
                        worst_diff = diff
                        candidate_idx = idx
        else:
            raise ValueError(f"Unknown memory allocation strategy: {strategy}")

        if candidate_idx is not None:
            chosen = blocks[candidate_idx]
            initial_sz = chosen.size
            remaining_sz = initial_sz - req_size

            allocations.append({
                "pid": pid,
                "allocated_kb": req_size,
                "block_id": chosen.block_id,
                "initial_block_kb": initial_sz,
                "remaining_block_kb": remaining_sz,
                "status": "Allocated",
            })

            # Dynamic block splitting:
            # Allocated partition takes req_size. The remaining free space stays in the free pool.
            if remaining_sz > 0:
                chosen.size = remaining_sz
                chosen.is_free = True
            else:
                chosen.size = 0
                chosen.is_free = False
        else:
            unallocated_processes.append(pid)

    used_mem = sum(a["allocated_kb"] for a in allocations)
    free_mem = sum(b.size for b in blocks if b.is_free)
    success_count = len(allocations)
    failed_count = len(unallocated_processes)
    utilization = round((used_mem / total_mem) * 100, 2) if total_mem > 0 else 0.0

    # Calculate external fragmentation:
    # Occurs when any unallocated process cannot be placed, but total free space >= process request size
    external_frag = 0
    if unallocated_processes:
        req_map = dict(valid_requests)
        for unallocated_pid in unallocated_processes:
            needed = req_map[unallocated_pid]
            if free_mem >= needed:
                external_frag = free_mem
                break

    remaining_blocks_info = [
        {"block_id": b.block_id, "remaining_kb": b.size, "is_free": b.is_free}
        for b in blocks if b.size > 0
    ]

    result = MemoryAllocationResult(
        algorithm=strategy,
        allocations=allocations,
        unallocated_processes=unallocated_processes,
        total_memory_kb=total_mem,
        total_allocated_kb=used_mem,
        total_free_memory_kb=free_mem,
        successful_allocations=success_count,
        failed_allocations=failed_count,
        memory_utilization=utilization,
        external_fragmentation_kb=external_frag,
        internal_fragmentation_kb=0,  # 0 under dynamic block splitting
        remaining_blocks=remaining_blocks_info,
    )

    logger.info(
        f"{strategy} executed: {success_count} allocated, {failed_count} failed, "
        f"Used={used_mem}KB, Free={free_mem}KB, ExtFrag={external_frag}KB."
    )
    return result


def first_fit(
    blocks: Sequence[int], requests: Sequence[Union[int, tuple[str, int], dict[str, Any]]]
) -> MemoryAllocationResult:
    """Allocates memory using First Fit strategy with dynamic block splitting."""
    return _allocate(blocks, requests, "First Fit")


def best_fit(
    blocks: Sequence[int], requests: Sequence[Union[int, tuple[str, int], dict[str, Any]]]
) -> MemoryAllocationResult:
    """Allocates memory using Best Fit strategy with dynamic block splitting."""
    return _allocate(blocks, requests, "Best Fit")


def worst_fit(
    blocks: Sequence[int], requests: Sequence[Union[int, tuple[str, int], dict[str, Any]]]
) -> MemoryAllocationResult:
    """Allocates memory using Worst Fit strategy with dynamic block splitting."""
    return _allocate(blocks, requests, "Worst Fit")


def compare_memory_algorithms(
    blocks: Sequence[int], requests: Sequence[Union[int, tuple[str, int], dict[str, Any]]]
) -> dict[str, Any]:
    """
    Executes First Fit, Best Fit, and Worst Fit on identical independent copies of the input data.
    Returns comparative evaluation metrics and identifies the best-performing algorithm.
    """
    res_ff = first_fit(blocks, requests)
    res_bf = best_fit(blocks, requests)
    res_wf = worst_fit(blocks, requests)

    results_map = {
        "First Fit": res_ff,
        "Best Fit": res_bf,
        "Worst Fit": res_wf,
    }

    comparison_records: list[dict] = []
    for name, res in results_map.items():
        total_reqs = res.successful_allocations + res.failed_allocations
        success_rate = round((res.successful_allocations / total_reqs) * 100, 2) if total_reqs > 0 else 0.0
        comparison_records.append({
            "algorithm": name,
            "success_rate_percent": success_rate,
            "total_allocated_kb": res.total_allocated_kb,
            "successful_allocations": res.successful_allocations,
            "failed_allocations": res.failed_allocations,
            "free_memory_kb": res.total_free_memory_kb,
            "memory_utilization_percent": res.memory_utilization,
            "external_fragmentation_kb": res.external_fragmentation_kb,
        })

    # Determine best algorithm: highest success count, then highest utilization, then lowest external fragmentation
    best_algo = max(
        results_map.keys(),
        key=lambda k: (
            results_map[k].successful_allocations,
            results_map[k].memory_utilization,
            -results_map[k].external_fragmentation_kb,
        ),
    )

    return {
        "results": results_map,
        "comparison_table": comparison_records,
        "best_algorithm": best_algo,
    }


def calculate_fragmentation(
    blocks: Sequence[MemoryBlock], unallocated_requests: Sequence[tuple[str, int]]
) -> tuple[int, int]:
    """
    Computes (internal_fragmentation_kb, external_fragmentation_kb).
    Internal fragmentation is 0 under dynamic partition splitting.
    """
    internal_frag = sum(b.internal_fragmentation for b in blocks)
    free_mem = sum(b.size for b in blocks if b.is_free)
    external_frag = 0
    for _, needed in unallocated_requests:
        if free_mem >= needed:
            external_frag = free_mem
            break
    return internal_frag, external_frag


def display_allocation(result: MemoryAllocationResult) -> str:
    """Renders formatted ASCII table of memory allocation results and performance metrics."""
    lines = [
        "",
        f"=== MEMORY ALLOCATION RESULTS ({result.algorithm.upper()}) ===",
    ]

    headers = ["Process", "Required", "Allocated Block", "Remaining"]
    rows = []
    for a in result.allocations:
        rows.append([
            a["pid"],
            f"{a['allocated_kb']} KB",
            f"{a['initial_block_kb']} KB (Block #{a['block_id']})",
            f"{a['remaining_block_kb']} KB",
        ])

    for p in result.unallocated_processes:
        rows.append([p, "N/A", "FAILED (No Block Fits)", "N/A"])

    lines.append(format_table(headers, rows))
    lines.append(
        f"Total Memory: {result.total_memory_kb} KB | "
        f"Allocated: {result.total_allocated_kb} KB | "
        f"Free: {result.total_free_memory_kb} KB"
    )
    lines.append(
        f"Successful Allocations: {result.successful_allocations} | "
        f"Failed Allocations: {result.failed_allocations} | "
        f"Memory Utilization: {result.memory_utilization:.2f}%"
    )
    lines.append(
        f"External Fragmentation: {result.external_fragmentation_kb} KB | "
        f"Internal Fragmentation: {result.internal_fragmentation_kb} KB"
    )

    return "\n".join(lines)
