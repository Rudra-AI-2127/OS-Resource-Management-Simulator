# System Architecture & Technical Specification

**Project Title**: OS Resource Management Simulator  
**Subtitle**: Integrated Operating System Resource Management Simulator  
**Phase**: Phase 1 — System Design and Planning (20 Marks)  
**Deliverable**: `Phase_1_Design/system_architecture.md`  

---

## 1. Architectural Overview & System Topology

The **OS Resource Management Simulator** is engineered as a modular, layered system adhering to the Separation of Concerns (SoC) principle. The software is organized into six well-defined architectural layers:

```
+---------------------------------------------------------------------------------+
|                         1. PRESENTATION & INTERFACES                            |
|       - main.py (CLI Interactive Terminal)                                      |
|       - run.sh (Automated Bash Launcher)                                        |
|       - app.py (Streamlit Web Dashboard - Optional Enhancement)                 |
+---------------------------------------------------------------------------------+
                                         |
                                         v
+---------------------------------------------------------------------------------+
|                    2. CONTROLLER & ORCHESTRATION LAYER                          |
|       - Navigation dispatch loop                                                |
|       - Workload router (Interactive Console vs CSV Batch Loading)              |
+---------------------------------------------------------------------------------+
                                         |
                                         v
+---------------------------------------------------------------------------------+
|                        3. SHARED UTILITY LAYER                                  |
|       - utils/validators.py (Defensive type and range verification)             |
|       - utils/logger.py (Centralized file and stream activity logging)          |
|       - utils/helpers.py (Tabular ASCII formatting & Gantt chart rendering)     |
+---------------------------------------------------------------------------------+
                                         |
                                         v
+---------------------------------------------------------------------------------+
|                    4. CORE RESOURCE-MANAGEMENT ENGINES                          |
|   +-------------------+  +-------------------+  +-------------------+  +------+ |
|   | cpu_scheduling.py |  | memory_mgmt.py    |  | deadlock.py       |  | disk | |
|   +-------------------+  +-------------------+  +-------------------+  +------+ |
+---------------------------------------------------------------------------------+
                                         |
                                         v
+---------------------------------------------------------------------------------+
|                     5. REPORTING & ANALYTICS SUBSYSTEM                          |
|       - modules/reporting.py (Benchmark driver, comparative tables, charts)     |
+---------------------------------------------------------------------------------+
                                         |
                                         v
+---------------------------------------------------------------------------------+
|                       6. PERSISTENCE & OUTPUT ARTIFACTS                         |
|       - data/*.csv (Input Workloads)                                            |
|       - results/*.csv (Tabular Execution Datasets)                              |
|       - charts/*.png (Matplotlib Analytical Plots)                              |
|       - logs/activity.log (Audit Trail)                                         |
+---------------------------------------------------------------------------------+
```

Visual diagram references:
- High-Resolution Architecture Diagram: [system_architecture.png](file:///C:/Users/rpsra/Downloads/Operating-Systems-Lab/Phase_1_Design/system_architecture.png)
- Editable Mermaid Specification: [system_architecture.mmd](file:///C:/Users/rpsra/Downloads/Operating-Systems-Lab/Phase_1_Design/diagrams/system_architecture.mmd)

---

## 2. Subsystem Descriptions & Function Signatures

### 2.1 CPU Scheduling (`modules/cpu_scheduling.py`)
Responsible for modeling CPU process execution queues, context switches, timing metrics, and Gantt charts.

```python
def fcfs(processes: list[Process]) -> tuple[list[Process], list[TimelineSegment]]:
    """Executes First-Come First-Served scheduling non-preemptively."""

def sjf(processes: list[Process]) -> tuple[list[Process], list[TimelineSegment]]:
    """Executes Shortest Job First scheduling non-preemptively."""

def round_robin(processes: list[Process], quantum: int) -> tuple[list[Process], list[TimelineSegment]]:
    """Executes Round Robin scheduling preemptively with given time quantum."""

def priority_scheduling(processes: list[Process]) -> tuple[list[Process], list[TimelineSegment]]:
    """Executes Priority Scheduling non-preemptively (lower numeric value = higher priority)."""

def calculate_metrics(processes: list[Process]) -> dict[str, float]:
    """Calculates Average Waiting Time and Average Turnaround Time."""

def generate_gantt_chart(segments: list[TimelineSegment]) -> str:
    """Renders an ASCII text-based Gantt chart representation of the execution timeline."""
```

### 2.2 Memory Management (`modules/memory_management.py`)
Responsible for modeling dynamic variable-partition allocation, partition splitting, and fragmentation auditing.

```python
def first_fit(blocks: list[MemoryBlock], requests: list[tuple[str, int]]) -> MemoryAllocationResult:
    """Allocates memory using the First Fit strategy with dynamic block splitting."""

def best_fit(blocks: list[MemoryBlock], requests: list[tuple[str, int]]) -> MemoryAllocationResult:
    """Allocates memory using the Best Fit strategy with dynamic block splitting."""

def worst_fit(blocks: list[MemoryBlock], requests: list[tuple[str, int]]) -> MemoryAllocationResult:
    """Allocates memory using the Worst Fit strategy with dynamic block splitting."""

def calculate_fragmentation(blocks: list[MemoryBlock], unallocated_requests: list[tuple[str, int]]) -> tuple[int, int]:
    """Computes internal fragmentation and external fragmentation in KB."""

def display_allocation(result: MemoryAllocationResult) -> str:
    """Formats memory allocation results into a clear summary table."""
```

### 2.3 Deadlock Management (`modules/deadlock.py`)
Responsible for modeling multi-resource state, Banker's Safety Algorithm, safe sequence derivation, and dynamic resource-request safety checks.

```python
def calculate_need(max_matrix: list[list[int]], allocation_matrix: list[list[int]]) -> list[list[int]]:
    """Computes the Need matrix: Need[i][j] = Max[i][j] - Allocation[i][j]."""

def bankers_algorithm(state: DeadlockState) -> tuple[bool, list[str]]:
    """Runs Dijkstra's Banker's Algorithm returning (is_safe, safe_sequence)."""

def check_safe_state(state: DeadlockState) -> bool:
    """Returns True if the system is in a safe state, False otherwise."""

def request_resources(state: DeadlockState, pid: str, request_vector: list[int]) -> tuple[bool, str, list[str]]:
    """Evaluates dynamic resource request using speculative allocation and safety check."""

def display_safe_sequence(safe_sequence: list[str]) -> str:
    """Formats safe sequence into 'P1 -> P3 -> P4 -> P0 -> P2' string representation."""
```

### 2.4 Disk Scheduling (`modules/disk_scheduling.py`)
Responsible for simulating disk arm head seeks across cylinders, computing seek sequences, total head movement, and average seek distance.

```python
def fcfs_disk(requests: list[int], initial_head: int) -> DiskSchedulingResult:
    """Executes First-Come First-Served disk scheduling."""

def sstf(requests: list[int], initial_head: int) -> DiskSchedulingResult:
    """Executes Shortest Seek Time First disk scheduling."""

def scan(requests: list[int], initial_head: int, total_cylinders: int = 200, direction: str = 'up') -> DiskSchedulingResult:
    """Executes SCAN (Elevator) disk scheduling with boundary sweep."""

def cscan(requests: list[int], initial_head: int, total_cylinders: int = 200, direction: str = 'up') -> DiskSchedulingResult:
    """Executes Circular SCAN (C-SCAN) disk scheduling with rapid boundary wraparound."""

def calculate_head_movement(sequence: list[int]) -> tuple[int, float]:
    """Computes total head movement and average seek distance."""
```

### 2.5 Reporting & Analytics Engine (`modules/reporting.py`)
Responsible for running baseline comparisons on standardized workloads, saving CSV data, and rendering Matplotlib figures.

```python
def run_cpu_comparison(input_csv: str) -> dict:
    """Runs all 4 CPU scheduling algorithms on a single workload and compares metrics."""

def run_memory_comparison(input_csv: str) -> dict:
    """Runs First, Best, and Worst fit on a single memory workload and compares metrics."""

def run_disk_comparison(input_csv: str) -> dict:
    """Runs all 4 disk scheduling algorithms on a single request sequence and compares metrics."""

def export_results_to_csv(data: list[dict], output_filepath: str) -> None:
    """Persists structured simulation results to a CSV file."""

def generate_comparison_charts(charts_dir: str = "charts") -> list[str]:
    """Generates the four mandatory Matplotlib charts (cpu, memory, disk, overall)."""
```

---

## 3. Exception & Error Handling Strategy

To satisfy **NFR-REL** and the blueprint requirements, the system strictly isolates validation and simulation errors through a tiered exception architecture:

1. **Defensive Validation Boundary (`utils/validators.py`)**:
   - All user inputs (interactive console or CSV) pass through strict validator functions.
   - Raises informative, standard `ValueError` or custom `SimulationValidationError` exceptions with explicit error messages (e.g., `"Burst time must be positive (> 0), received -5"`).
2. **Controller Safeguard (`main.py`)**:
   - Menu dispatches and module entry points are wrapped in `try-except` blocks.
   - Catches `ValueError`, `FileNotFoundError`, and `IndexError` gracefully, displaying a formatted error box to the user and returning to the menu instead of crashing.
3. **Audit Logging on Errors**:
   - Every caught exception is recorded via `logger.warning()` or `logger.error()` in `logs/activity.log` with timestamp and contextual details.

---

## 4. Logging Strategy

The logging subsystem (`utils/logger.py`) utilizes the standard Python `logging` library configured to write to `logs/activity.log`:

```python
import logging
from pathlib import Path

def setup_logger(log_file: str = "logs/activity.log") -> logging.Logger:
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("OSSimulator")
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers on re-initialization
    if not logger.handlers:
        handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
```

**Logging Policy**:
- Application events (`Application started`, `Application terminated cleanly`).
- Module execution events (`CPU Scheduling executed: Algorithm=FCFS, ProcessCount=4`).
- Input warnings (`Invalid input detected: negative burst time`).
- Critical execution failures (`Module execution failed: DivisionByZero in disk module`).
- Tiny inner-loop step calculations are **not** logged to keep `activity.log` concise and auditable.

---

## 5. CSV Data Formats

### 5.1 Input CSV Schemas (`data/`)
- **`data/cpu_input.csv`**:
  ```csv
  pid,arrival_time,burst_time,priority
  P1,0,5,2
  P2,1,3,1
  P3,2,8,4
  P4,3,2,3
  ```
- **`data/memory_input.csv`**:
  ```csv
  type,id,size
  block,B1,100
  block,B2,500
  block,B3,200
  block,B4,300
  block,B5,600
  process,P1,212
  process,P2,417
  process,P3,112
  process,P4,426
  ```
- **`data/disk_input.csv`**:
  ```csv
  initial_head,direction,total_cylinders,requests
  53,up,200,"98,183,37,122,14,124,65,67"
  ```

### 5.2 Results CSV Schemas (`results/`)
- **`results/cpu_results.csv`**:
  `algorithm,pid,arrival_time,burst_time,priority,completion_time,turnaround_time,waiting_time,response_time,avg_waiting_time,avg_turnaround_time`
- **`results/memory_results.csv`**:
  `algorithm,pid,requested_kb,allocated_block,remaining_kb,status,total_memory_kb,used_memory_kb,external_frag_kb`
- **`results/disk_results.csv`**:
  `algorithm,initial_head,total_head_movement,avg_head_movement,requests_serviced,seek_sequence`

---

## 6. Testing Strategy

- **Test Suite Location**: `tests/` (`test_cpu.py`, `test_memory.py`, `test_deadlock.py`, `test_disk.py`, `test_reporting.py`).
- **Framework**: Standard library `unittest`.
- **Test Automation Runner**: `run_tests.sh` (`python3 -m unittest discover -s tests`).
- **Test Matrix (TC01–TC09+)**: Full implementation and verification of valid, invalid, boundary, and edge cases.
- **TDD Principle**: For each algorithm in Phase 2, unit test assertions are defined and confirmed failing prior to implementation.
