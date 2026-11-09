# Shared Data Structures Specification

**Project Title**: OS Resource Management Simulator  
**Subtitle**: Integrated Operating System Resource Management Simulator  
**Phase**: Phase 1 — System Design and Planning (20 Marks)  
**Deliverable**: `Phase_1_Design/data_structures.md`  

---

## 1. Overview and Design Rationale

To maintain strict typing, eliminate dictionary-key typo bugs, and avoid unnecessary object-oriented bloat (adhering to **ponytail** principles), the simulator uses Python's standard `dataclasses` alongside standard collections (`list`, `deque`, `dict`, and 2D matrices).

| Primitive / Collection | Purpose in OS Simulator | Architectural Justification |
|---|---|---|
| **`dataclass`** | Process, MemoryBlock, DeadlockState, DiskResult | Strong type safety, auto-generated representations, clear field contracts. |
| **`list`** | Process pools, cylinder tracks, memory block lists | Sequential ordering, indexable access, native serialization to CSV. |
| **`collections.deque`** | Round Robin Ready Queue | $O(1)$ amortized FIFO enqueuing and dequeuing operations. |
| **`dict`** | Quick PID-to-metric lookups & summary aggregation | $O(1)$ key access and flexible mapping for comparative tables. |
| **2D `list[list[int]]`** | Banker's matrices ($Allocation$, $Max$, $Need$) | Matrix arithmetic without heavy binary dependencies; portable across Python 3.11+. |

---

## 2. Core Data Models

### 2.1 CPU Scheduling Domain

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Process:
    """Models an OS process throughout its scheduling lifecycle."""
    pid: str
    arrival_time: int
    burst_time: int
    priority: int = 0
    remaining_time: int = field(init=False)
    start_time: Optional[int] = None
    completion_time: int = 0
    turnaround_time: int = 0
    waiting_time: int = 0
    response_time: int = 0

    def __post_init__(self):
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
class TimelineSegment:
    """Represents a continuous CPU execution slice on the Gantt chart."""
    pid: str          # Process ID or "IDLE"
    start_time: int
    end_time: int

    @property
    def duration(self) -> int:
        return self.end_time - self.start_time
```

### 2.2 Memory Management Domain

```python
@dataclass
class MemoryBlock:
    """Models a physical memory block or split partition in RAM."""
    block_id: int
    start_address: int
    size: int                         # Size of the partition in KB
    is_free: bool = True
    allocated_pid: Optional[str] = None
    internal_fragmentation: int = 0   # 0 under dynamic partition splitting

@dataclass
class ProcessMemoryRequest:
    """Models a process memory allocation demand."""
    pid: str
    size_kb: int

@dataclass
class MemoryAllocationResult:
    """Encapsulates the global outcome of a memory allocation policy."""
    algorithm: str
    initial_blocks: list[MemoryBlock]
    final_blocks: list[MemoryBlock]
    allocations: list[dict]           # [{"pid": str, "block_id": int, "allocated_kb": int, "remaining_kb": int}]
    unallocated_processes: list[str]  # PIDs that could not be satisfied
    total_memory_kb: int
    allocated_memory_kb: int
    free_memory_kb: int
    external_fragmentation_kb: int
    internal_fragmentation_kb: int = 0
```

### 2.3 Deadlock Management Domain

```python
@dataclass
class DeadlockState:
    """Encapsulates the multi-resource allocation state for Banker's Algorithm."""
    process_ids: list[str]                 # ["P0", "P1", ..., "Pn-1"]
    resource_ids: list[str]                # ["A", "B", "C", ...]
    available: list[int]                   # Length m: Available units per resource type
    max_demand: list[list[int]]            # n x m Matrix: Maximum resource demand
    allocation: list[list[int]]            # n x m Matrix: Currently allocated resources
    need: list[list[int]] = field(init=False) # n x m Matrix: Need = Max - Allocation

    def __post_init__(self):
        self.calculate_need()

    def calculate_need(self) -> list[list[int]]:
        n = len(self.process_ids)
        m = len(self.resource_ids)
        self.need = [
            [self.max_demand[i][j] - self.allocation[i][j] for j in range(m)]
            for i in range(n)
        ]
        return self.need

@dataclass
class DeadlockSafetyResult:
    """Encapsulates the result of Dijkstra's Banker's Safety evaluation."""
    is_safe: bool
    safe_sequence: list[str]               # Ordered list of PIDs or empty list if unsafe
    work_history: list[list[int]]          # Step-by-step Work vector progression
    explanation: str
```

### 2.4 Disk Scheduling Domain

```python
@dataclass
class DiskSchedulingResult:
    """Encapsulates the results of a disk head scheduling algorithm."""
    algorithm: str
    initial_head: int
    seek_sequence: list[int]               # Ordered cylinders: [H0, r1, r2, ..., rk]
    step_movements: list[int]              # Absolute cylinder steps: [|r1 - H0|, ...]
    total_head_movement: int               # Sum of seek steps
    average_head_movement: float           # total_movement / count_of_requests
    requests_serviced: int                 # Count of distinct I/O requests processed
```

### 2.5 Reporting & Analytics Domain

```python
@dataclass
class BenchmarkSummary:
    """Holds aggregate comparative metrics across algorithms for reporting."""
    module_name: str
    baseline_dataset_name: str
    results_table: list[dict]              # Tabular comparison records
    generated_charts: list[str]            # Filepaths of saved Matplotlib PNGs
    exported_csv: str                      # Filepath of saved CSV data
    key_observations: list[str]            # Analytical findings
```

---

## 3. Data Invariants and Boundary Constraints

1. **CPU Invariant**:
   - $\forall p \in Processes: AT(p) \ge 0 \land BT(p) > 0$.
   - $\forall p \in Processes: TAT(p) = CT(p) - AT(p) \land WT(p) = TAT(p) - BT(p)$.
2. **Memory Invariant**:
   - $\sum Block.size = TotalMemory_{initial}$ (splitting preserves the conservation of memory).
   - $ExternalFragmentation = \sum FreeBlock.size$ if and only if $\exists p_{failed}$ such that $\sum FreeBlock.size \ge p_{failed}.size$.
3. **Deadlock Invariant**:
   - $\forall i, j: 0 \le Allocation[i][j] \le Max[i][j]$.
   - $\forall i, j: Need[i][j] = Max[i][j] - Allocation[i][j] \ge 0$.
4. **Disk Invariant**:
   - $\forall r \in Requests: 0 \le r < MaxCylinders$ (default $[0, 199]$).
   - $TotalHeadMovement = \sum_{k=1}^{N} |Sequence[k] - Sequence[k-1]|$.
