
# Requirements Specification — OS Resource Management Simulator

**Project Title**: OS Resource Management Simulator  
**Subtitle**: Integrated Operating System Resource Management Simulator  
**Document Version**: 1.0.0 (Phase 1A Discovery)  
**Submission Deadline**: 14 November 2026  
**Source of Truth**: *OS Resource Management Simulator Blueprint* (Course Faculty Specification)  

---

## 1. Problem Statement

Modern general-purpose operating systems depend on sophisticated resource allocation algorithms to arbitrate CPU compute cycles, partition physical memory (RAM), prevent deadlocks among concurrent entities, and schedule secondary storage I/O operations. Without concrete empirical simulations, understanding the trade-offs, starvation vulnerabilities, fragmentation behaviors, and latency profiles of these algorithms is challenging.

The **OS Resource Management Simulator** addresses this challenge by providing an integrated, modular, Python-based academic simulation platform. It enables users to supply dynamic workloads, observe step-by-step algorithm behaviors, compute standardized metrics, handle execution edge cases, export execution datasets, and perform quantitative comparative evaluations across competing strategies under identical operational workloads.

---

## 2. Project Objectives

1. **Integrated Multi-Module Architecture**: Build a single cohesive Python application unifying CPU scheduling, dynamic memory management, deadlock avoidance, disk scheduling, and comparative reporting under one centralized controller (`main.py`).
2. **Algorithm Implementation Rigor**: Accurately implement 12 classic OS resource management algorithms:
   - *CPU Scheduling*: First-Come First-Served (FCFS), Shortest Job First (SJF - Non-Preemptive), Round Robin (RR - Preemptive), and Priority Scheduling (Non-Preemptive).
   - *Memory Management*: First Fit, Best Fit, and Worst Fit dynamic partition allocation.
   - *Deadlock Management*: Dijkstra's Banker's Algorithm (Need Matrix evaluation, System Safety check, Safe Sequence generation, and Resource-Request algorithm).
   - *Disk Scheduling*: FCFS, Shortest Seek Time First (SSTF), SCAN (Elevator), and Circular SCAN (C-SCAN).
3. **Mathematical & Metric Fidelity**: Compute exact completion, turnaround, waiting, and response times; quantify internal and external fragmentation; audit resource claim vectors; and track disk head cylinder seek counts.
4. **Data-Driven Analysis & Visualization**: Enable automated comparative benchmarks on identical baseline workloads, exporting structured CSV data and rendering at least four high-resolution Matplotlib analytical figures.
5. **Software Engineering Standards**: Adhere to Python 3.11+ standards, strict type hinting, docstrings, defensive input validation, structured logging (`logs/activity.log`), comprehensive `unittest` coverage (TC01–TC09+), and automated POSIX Bash scripts (`run.sh`, `run_tests.sh`).

---

## 3. Functional Requirements

### 3.1 Module A: CPU Scheduling (FR-CPU)
- **FR-CPU-01**: The system shall accept a collection of processes, each defined by `Process ID` (PID), `Arrival Time` ($AT \ge 0$), `Burst Time` ($BT > 0$), and optional `Priority` (integer $\ge 0$).
- **FR-CPU-02**: The system shall implement four scheduling algorithms:
  - FCFS (Non-preemptive dispatch based strictly on arrival time).
  - SJF (Non-preemptive selection of the ready process with the smallest burst time; ties broken by arrival time, then PID).
  - Round Robin (Preemptive time-sliced execution using a user-specified Time Quantum $q \ge 1$; arriving processes at time $t$ enter the ready queue before preempted processes).
  - Priority Scheduling (Non-preemptive selection of the ready process with highest priority; lower integer indicates higher priority; ties broken by arrival time, then PID).
- **FR-CPU-03**: The system shall correctly handle arrival times, simultaneous process arrivals, CPU idle intervals (when no process has arrived), and preemption boundaries.
- **FR-CPU-04**: The system shall compute individual and aggregate performance metrics:
  - Completion Time ($CT$)
  - Turnaround Time ($TAT = CT - AT$)
  - Waiting Time ($WT = TAT - BT$)
  - Response Time ($RT = \text{First CPU Acquisition Time} - AT$)
  - Average Waiting Time ($\overline{WT}$)
  - Average Turnaround Time ($\overline{TAT}$)
- **FR-CPU-05**: The system shall generate a visual/textual Gantt chart illustrating timeline segments, execution order, and idle slots.

### 3.2 Module B: Memory Management (FR-MEM)
- **FR-MEM-01**: The system shall accept an initial list of free memory partition block sizes (in KB) and a sequence of process memory allocation requests (PID and size in KB).
- **FR-MEM-02**: The system shall implement three dynamic contiguous allocation strategies:
  - First Fit: Allocates the first available block large enough ($block\_size \ge request\_size$).
  - Best Fit: Allocates the smallest available block large enough, minimizing leftover space in that block.
  - Worst Fit: Allocates the largest available block, leaving the largest remaining free segment.
- **FR-MEM-03**: Dynamic Partition Splitting: When an allocated block exceeds the requested process size, the block shall be split into an allocated partition equal to the request and a remaining free block returned to the free block pool.
- **FR-MEM-04**: The system shall record and report:
  - Which process was allocated to which physical block index.
  - Which processes could not be allocated due to insufficient contiguous memory.
  - Total allocated memory and remaining free memory.
  - External fragmentation (total free memory available across all blocks when a request cannot be satisfied).
  - Internal fragmentation (defined as zero under dynamic partition splitting, or recorded if a fixed-partition policy is evaluated).

### 3.3 Module C: Deadlock Management (FR-DLK)
- **FR-DLK-01**: The system shall accept multi-resource system parameters:
  - Number of processes $n$ and resource types $m$.
  - Available resource vector $Available$ of size $m$.
  - Maximum demand matrix $Max$ of dimensions $n \times m$.
  - Current allocation matrix $Allocation$ of dimensions $n \times m$.
- **FR-DLK-02**: The system shall derive the Need matrix using the equation:
  $$Need[i][j] = Max[i][j] - Allocation[i][j] \quad \forall i \in [0, n-1], j \in [0, m-1]$$
- **FR-DLK-03**: The system shall implement the Banker's Safety Algorithm to determine whether the current state is **SAFE** or **UNSAFE**.
- **FR-DLK-04**: If the state is SAFE, the system shall output at least one valid Safe Execution Sequence (e.g., $P_1 \to P_3 \to P_4 \to P_0 \to P_2$). If UNSAFE, the system shall explain that a deadlock state could occur and no safe sequence exists.
- **FR-DLK-05**: The system shall provide a Resource Request Algorithm to evaluate a dynamic request vector $Request_i$ for process $P_i$:
  - Verify $Request_i \le Need_i$ (else raise error: exceeded maximum claim).
  - Verify $Request_i \le Available$ (else process must wait: resources unavailable).
  - Speculatively allocate resources and run the Safety Algorithm. If safe, commit allocation; if unsafe, rollback and deny immediate grant.

### 3.4 Module D: Disk Scheduling (FR-DSK)
- **FR-DSK-01**: The system shall accept a cylinder request sequence (e.g., `98, 183, 37, 122, 14, 124, 65, 67`), an initial head position (e.g., `53`), total disk cylinder capacity (default `200` cylinders, indices `0` to `199`), and initial head movement direction (`up`/`down`).
- **FR-DSK-02**: The system shall implement four disk scheduling algorithms:
  - FCFS: Services disk I/O requests strictly in order of arrival.
  - SSTF: Services the request closest to current head position ($|request - head|$ minimum).
  - SCAN (Elevator): Moves in initial direction to the disk boundary (e.g., cylinder 199), servicing pending requests along the way, then reverses direction to service remaining requests.
  - C-SCAN (Circular SCAN): Moves in initial direction to the disk boundary, servicing requests; upon reaching boundary, jumps directly to cylinder 0 without servicing on return, then resumes servicing in the original direction.
- **FR-DSK-03**: The system shall compute and output:
  - Request service sequence path.
  - Total head movement (cylinder seek distance).
  - Average head movement ($\frac{\text{Total Head Movement}}{\text{Number of Requests Serviced}}$).
  - Total requests serviced.

### 3.5 Module E: Reporting and Analysis (FR-REP)
- **FR-REP-01**: The system shall execute baseline comparison workloads across competing algorithms within each module under identical initial states.
- **FR-REP-02**: The system shall format performance comparison tables using tabular CLI displays and export results to standard CSV files (`results/cpu_results.csv`, `results/memory_results.csv`, `results/disk_results.csv`).
- **FR-REP-03**: The system shall generate at least four graphical charts using Matplotlib:
  1. *CPU Scheduling Comparison*: Grouped bar chart comparing Average Waiting Time and Average Turnaround Time across FCFS, SJF, RR, and Priority.
  2. *Memory Allocation Comparison*: Bar chart comparing allocation success count, memory utilized, and external fragmentation across First Fit, Best Fit, and Worst Fit.
  3. *Disk Scheduling Comparison*: Bar chart comparing total head movement across FCFS, SSTF, SCAN, and C-SCAN.
  4. *Overall Performance / Summary Analysis*: Multi-metric summary chart illustrating efficiency trade-offs.
- **FR-REP-04**: The system shall generate `observations.md` containing analytical deductions explaining why specific algorithms outperform others under varying workload profiles.

### 3.6 Application Controller & CLI Interface (FR-CLI)
- **FR-CLI-01**: The application shall present an interactive numeric menu in `main.py`:
  `1. CPU Scheduling`, `2. Memory Management`, `3. Deadlock Management`, `4. Disk Scheduling`, `5. Performance Analysis`, `6. Exit`.
- **FR-CLI-02**: The CLI shall support both manual interactive console inputs and automated batch execution via pre-configured CSV files (`data/cpu_input.csv`, `data/memory_input.csv`, `data/disk_input.csv`).
- **FR-CLI-03**: The system shall incorporate Bash automation scripts:
  - `run.sh`: Automated launcher for the main simulator application.
  - `run_tests.sh`: Automated discovery and execution of the `unittest` test suite.
- **FR-CLI-04**: The system shall maintain an activity audit log in `logs/activity.log` via standard Python logging.

---

## 4. Non-Functional Requirements

- **NFR-PERF (Performance)**: Algorithm simulations for workloads up to 1,000 processes/requests shall execute and generate reports within $< 2.0$ seconds on standard hardware.
- **NFR-REL (Reliability & Robustness)**: The simulator shall never crash abruptly on invalid input, non-numeric values, negative numbers, or empty datasets; it must catch errors gracefully, display helpful error diagnostics, and reprompt or return to menu.
- **NFR-MOD (Modularity & Maintainability)**: Core algorithms shall be decoupled from I/O and CLI logic into dedicated modules (`modules/`), shared utility helpers (`utils/`), and test suites (`tests/`).
- **NFR-USAB (Usability & Academic Clarity)**: CLI outputs and generated charts must be cleanly labeled with units (ms, KB, cylinders) so that results can be defended clearly during project demonstration and oral examination (viva).
- **NFR-PORT (Portability & Standards)**: The codebase shall run seamlessly on Python 3.11+ across Windows 10/11 and Linux/WSL Ubuntu with zero proprietary OS-specific dependencies outside Python standard library, Matplotlib, and Pandas.

---

## 5. Five Module Descriptions

| Module Name | File Location | Responsibility | Implemented Algorithms |
|---|---|---|---|
| **CPU Scheduling** | `modules/cpu_scheduling.py` | Simulates process dispatching on a uniprocessor system, calculating timing metrics and timeline Gantt charts. | FCFS, SJF (Non-preemptive), Round Robin (Preemptive, $q$), Priority (Non-preemptive) |
| **Memory Management** | `modules/memory_management.py` | Models contiguous RAM partitioning, dynamic block splitting, allocation tracking, and fragmentation metrics. | First Fit, Best Fit, Worst Fit |
| **Deadlock Management** | `modules/deadlock.py` | Computes resource need matrices, checks multi-resource system safety, generates safe execution sequences, and audits dynamic resource requests. | Dijkstra's Banker's Safety Algorithm & Resource-Request Algorithm |
| **Disk Scheduling** | `modules/disk_scheduling.py` | Simulates mechanical disk arm head movements across cylinder tracks, optimizing seek times. | FCFS, SSTF, SCAN (Elevator), C-SCAN (Circular SCAN) |
| **Reporting & Analysis** | `modules/reporting.py` | Runs comparative benchmarks across identical datasets, exports CSV data, and renders Matplotlib comparison charts. | Comparative metric aggregations, tabular exporters, chart generation |

---

## 6. Inputs and Outputs for Every Algorithm

### 6.1 CPU Scheduling
- **Inputs**:
  - List of Processes: $[(PID, ArrivalTime, BurstTime, Priority)]$
  - Time Quantum $q$ (for Round Robin, integer $\ge 1$)
- **Outputs**:
  - Process execution schedule: Ordered segments $[(PID, StartTime, EndTime)]$
  - Process table: $[(PID, AT, BT, Priority, CT, TAT, WT, RT)]$
  - Aggregate metrics: $\overline{WT}$, $\overline{TAT}$, CPU Utilization $\%$
  - Gantt chart string / plot representation

### 6.2 Memory Management
- **Inputs**:
  - Initial free memory blocks: List of integers $[BlockSize_0, BlockSize_1, \dots, BlockSize_{m-1}]$ (in KB)
  - Allocation requests: List of tuples $[(PID, RequestedSize)]$ (in KB)
- **Outputs**:
  - Allocation status table: Process ID, Requested Size, Allocated Block ID, Initial Block Size, Remaining Block Size, Status (`Allocated` / `Failed`)
  - Memory summary: Total Initial Memory, Total Allocated Memory, Remaining Free Memory, External Fragmentation (KB), Internal Fragmentation (KB)

### 6.3 Deadlock Management
- **Inputs**:
  - Number of processes $n$, number of resource types $m$
  - Resource vectors/matrices:
    - $Available$: $[R_0, R_1, \dots, R_{m-1}]$
    - $Max$: $n \times m$ matrix
    - $Allocation$: $n \times m$ matrix
  - Optional: Resource Request tuple $(PID, [Req_0, Req_1, \dots, Req_{m-1}])$
- **Outputs**:
  - Derived $Need$ matrix: $n \times m$ matrix
  - System Safety Status: `SAFE` or `UNSAFE`
  - Safe Sequence: $[P_{s_0}, P_{s_1}, \dots, P_{s_{n-1}}]$ (if safe)
  - Request evaluation: `Granted (Safe State Guaranteed)` or `Denied / Must Wait (Unsafe or Insufficient Resources)`

### 6.4 Disk Scheduling
- **Inputs**:
  - Request track sequence: List of integers $[t_0, t_1, \dots, t_{k-1}]$
  - Initial head position: Integer $H_0 \in [0, MaxCylinders - 1]$
  - Total cylinder count: Integer $MaxCylinders$ (default 200: $0$ to $199$)
  - Initial direction: String (`up` / `down`, default `up`)
- **Outputs**:
  - Service Sequence: Ordered list of head positions $[H_0, t_{s_0}, t_{s_1}, \dots, t_{s_{k-1}}]$
  - Total head movement: Integer cylinders
  - Average head movement: Float ($\frac{\text{Total Head Movement}}{k}$)
  - Total requests serviced: Integer $k$

---

## 7. Validation Requirements (VR)

- **VR-01 (Positive Integers)**: Burst times, block sizes, process memory requests, cylinder numbers, and time quanta must be strictly positive integers ($> 0$).
- **VR-02 (Non-negative Values)**: Arrival times, cylinder bounds, priorities, and allocation/maximum demand resource counts must be non-negative integers ($\ge 0$).
- **VR-03 (Unique Identifiers)**: Process identifiers within a single workload must be unique non-empty strings.
- **VR-04 (Matrix Consistency)**: In Deadlock Management, $Allocation[i][j] \le Max[i][j]$ must hold for all $i, j$; otherwise, input is rejected as structurally invalid.
- **VR-05 (Cylinder Boundary Enforcement)**: All disk request cylinder numbers must satisfy $0 \le t_i < MaxCylinders$.
- **VR-06 (Non-empty Collections)**: Algorithms must validate that input queues or block collections are non-empty before processing, returning clear explanatory errors rather than throwing `ZeroDivisionError` or `IndexError`.
- **VR-07 (Menu Boundary Validation)**: Interactive CLI options outside valid ranges (`1` to `6`) must trigger an informative warning and reprompt the user.
- **VR-08 (CSV File Validation)**: When reading batch CSV files, headers, column counts, and numeric parsing must be validated with specific error messages for malformed lines.

---

## 8. Reporting Requirements

- **Comparison Tables**: Formatted ASCII / tabulate console tables displaying side-by-side metric comparisons for identical workloads.
- **CSV Output Persistence**:
  - `results/cpu_results.csv`: Algorithm, PID, AT, BT, Priority, CT, TAT, WT, RT, Avg_WT, Avg_TAT
  - `results/memory_results.csv`: Algorithm, PID, Requested_KB, Allocated_Block, Remaining_Block_KB, Status, Total_Used_KB, External_Frag_KB
  - `results/disk_results.csv`: Algorithm, Initial_Head, Total_Movement, Avg_Movement, Serviced_Count, Service_Sequence
- **Visualization Artifacts (charts/)**:
  1. `charts/cpu_comparison.png`: Grouped bar chart comparing Waiting Time and Turnaround Time across FCFS, SJF, RR, and Priority.
  2. `charts/memory_comparison.png`: Comparison of memory allocation success rate and fragmentation.
  3. `charts/disk_comparison.png`: Comparison of total cylinder head movement across FCFS, SSTF, SCAN, and C-SCAN.
  4. `charts/overall_analysis.png`: Multi-panel executive summary chart across all four resource domains.
- **Analytical Observations**: Documented explanations in `Phase_3_Analysis/observations.md` analyzing algorithmic trade-offs (e.g., convoy effect in FCFS, starvation in SJF, seek optimization in SSTF vs SCAN).

---

## 9. Testing Requirements

- **Framework**: Python standard library `unittest`.
- **Execution Script**: `run_tests.sh` executing `python3 -m unittest discover -s tests`.
- **Test Matrix (TC01–TC09+)**:
  - `TC01`: Normal CPU scheduling validation against textbook manual calculations.
  - `TC02`: Validation error on negative burst time.
  - `TC03`: Empty process list validation.
  - `TC04`: Correct memory allocation under First Fit, Best Fit, and Worst Fit.
  - `TC05`: Memory allocation failure when request exceeds largest available block.
  - `TC06`: Banker's algorithm safe resource allocation producing valid safe sequence.
  - `TC07`: Banker's algorithm unsafe state detection.
  - `TC08`: Disk scheduling head movement validation against known textbook traces.
  - `TC09`: Interactive menu invalid option handling.
  - `TC10–TC15` (Extended): Boundary conditions (single process, $q=1$, simultaneous arrivals, disk head at cylinder 0/199, Banker's resource request rejection).
- **Activity Logging**: Structured logging to `logs/activity.log` capturing startup, module entry, algorithm executions, warnings, and errors.

---

## 10. Submission Deliverables Breakdown

| Phase | Marks | Specified Deliverables |
|---|---|---|
| **Phase 1: Design and Planning** | 20 | `Phase_1_Design/` containing: `problem_statement.md`, `objectives.md`, `system_architecture.png`, `workflow_diagram.png`, `data_structures.md`, `module_description.md`, `implementation_plan.md`, `requirements.md`, `assumptions.md`, `acceptance_criteria.md`. |
| **Phase 2: Implementation** | 20 | Full modular source code in `modules/`, utility helpers in `utils/`, central CLI `main.py`, Bash scripts `run.sh` & `run_tests.sh`, execution traces, and screenshots. |
| **Phase 3: Performance Analysis** | 20 | `Phase_3_Analysis/` containing: benchmark datasets (`datasets/`), CSV results (`results/`), at least four comparison charts (`charts/`), and `observations.md`. |
| **Phase 4: Testing & Reliability** | 20 | `Phase_4_Testing/` containing: automated test files (`tests/`), test case matrix (`test_cases.xlsx` & `test_results.csv`), and execution audit log (`logs/activity.log`). |
| **Phase 5: Documentation & Demonstration** | 20 | Complete root `README.md`, sample input/output execution traces, interface screenshots, comprehensive Project Report (15–25 pages), and viva defense preparation materials. |
| **Total** | **100** | **Complete Academic Capstone Package** |
