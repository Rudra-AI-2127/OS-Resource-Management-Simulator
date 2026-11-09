# Module Descriptions & Subsystem Design

**Project Title**: OS Resource Management Simulator  
**Subtitle**: Integrated Operating System Resource Management Simulator  
**Phase**: Phase 1 — System Design and Planning (20 Marks)  
**Deliverable**: `Phase_1_Design/module_description.md`  

---

## 1. Overview of Modules

The simulation engine is structured into five core functional modules supported by three common utility components. Each module operates with decoupled inputs and outputs, allowing standalone execution, automated unit testing, or coordinated multi-algorithm benchmarking.

---

## 2. Detailed Module Breakdown

### 2.1 Module A: CPU Scheduling (`modules/cpu_scheduling.py`)
- **Primary Responsibility**: Models uniprocessor CPU arbitration, executing scheduling policies over discrete time domains, calculating process lifecycle metrics ($CT, TAT, WT, RT$), and formatting visual Gantt chart timelines.
- **Implemented Algorithms**:
  1. `fcfs(processes)`: First-Come First-Served non-preemptive queue scheduling.
  2. `sjf(processes)`: Shortest Job First non-preemptive scheduling with burst time arbitration.
  3. `round_robin(processes, quantum)`: Preemptive time-slice scheduling with arrival priority over preempted re-queuing.
  4. `priority_scheduling(processes)`: Priority-based non-preemptive scheduling (lower numeric value = higher priority).
- **Core Auxiliary Functions**:
  - `calculate_metrics(processes)`: Computes Average Waiting Time and Average Turnaround Time.
  - `generate_gantt_chart(segments)`: Formats execution segments into an ASCII timeline string.
- **Edge Case & Boundary Defenses**:
  - CPU idle intervals between process arrival gaps are explicitly logged as `[IDLE]` blocks.
  - Simultaneous arrivals are resolved deterministically using PID alphabetical ordering.
  - Quantum $q=1$ stress testing for Round Robin.

### 2.2 Module B: Memory Management (`modules/memory_management.py`)
- **Primary Responsibility**: Models contiguous physical memory allocation, dynamic partition splitting, free block tracking, and quantitative fragmentation auditing.
- **Implemented Algorithms**:
  1. `first_fit(blocks, requests)`: Traverses free blocks sequentially, allocating the first partition large enough.
  2. `best_fit(blocks, requests)`: Evaluates all candidate free blocks, allocating the block with the smallest excess capacity.
  3. `worst_fit(blocks, requests)`: Allocates the largest candidate free block, leaving the largest remaining contiguous chunk.
- **Core Auxiliary Functions**:
  - `calculate_fragmentation(blocks, unallocated_requests)`: Audits external fragmentation when total free space exceeds an unserviced request size.
  - `display_allocation(result)`: Renders ASCII tabular results of block allocations, process IDs, and partition sizes.
- **Edge Case & Boundary Defenses**:
  - Dynamic partition splitting: split partition remainder is retained in the free pool without erroneously labeling it as internal fragmentation.
  - Requests exceeding total physical memory capacity are flagged without interrupting simulation.

### 2.3 Module C: Deadlock Management (`modules/deadlock.py`)
- **Primary Responsibility**: Implements Dijkstra's Banker's Algorithm for multi-instance resource systems to detect unsafe states, generate safe sequences, and audit dynamic resource requests.
- **Implemented Algorithms**:
  1. `calculate_need(max_matrix, allocation_matrix)`: Derives the $Need$ matrix via matrix subtraction.
  2. `bankers_algorithm(state)`: Executes Dijkstra's Safety Algorithm, returning safety boolean, complete safe sequence, and step-by-step $Work$ progression vectors.
  3. `check_safe_state(state)`: Quick boolean check for system safety.
  4. `request_resources(state, pid, request_vector)`: Implements the Resource-Request algorithm with bounds verification ($Request \le Need \land Request \le Available$), speculative state update, and automatic rollback upon unsafe results.
- **Core Auxiliary Functions**:
  - `display_safe_sequence(safe_sequence)`: Formats safe sequences (e.g., `P1 -> P3 -> P4 -> P0 -> P2`).
- **Edge Case & Boundary Defenses**:
  - Catches requests exceeding declared maximum claims.
  - Manages zero-need and zero-allocation processes cleanly.

### 2.4 Module D: Disk Scheduling (`modules/disk_scheduling.py`)
- **Primary Responsibility**: Models mechanical hard disk head seek operations across concentric track cylinders, optimizing seek distances and servicing latency.
- **Implemented Algorithms**:
  1. `fcfs_disk(requests, initial_head)`: Services track cylinder requests strictly in arrival order.
  2. `sstf(requests, initial_head)`: Greedily seeks the nearest cylinder to minimize immediate seek distance.
  3. `scan(requests, initial_head, total_cylinders=200, direction='up')`: Elevator algorithm sweeping to the physical disk boundary ($199$ moving up, $0$ moving down) before reversing.
  4. `cscan(requests, initial_head, total_cylinders=200, direction='up')`: Circular SCAN sweeping to boundary, jumping to opposite boundary without servicing requests, and continuing upward.
- **Core Auxiliary Functions**:
  - `calculate_head_movement(sequence)`: Computes step-by-step seeks, total head movement, and average seek distance ($\frac{\text{Total Seek}}{\text{Requests Serviced}}$).
- **Edge Case & Boundary Defenses**:
  - Rejection of negative cylinders or cylinders $\ge MaxCylinders$.
  - Correct inclusion of C-SCAN boundary wraparound seek jump ($|199 - 0| = 199$).

### 2.5 Module E: Reporting and Analysis (`modules/reporting.py`)
- **Primary Responsibility**: Unifies benchmark execution across standardized workloads, creates comparative tables, persists CSV results, and renders Matplotlib figures.
- **Core Functions**:
  - `run_cpu_comparison(input_csv)`: Compares FCFS, SJF, RR, and Priority on identical process sets.
  - `run_memory_comparison(input_csv)`: Compares First, Best, and Worst Fit on identical request batches.
  - `run_disk_comparison(input_csv)`: Compares FCFS, SSTF, SCAN, and C-SCAN on identical track sequences.
  - `export_results_to_csv(data, filepath)`: Exports structured telemetry to `results/*.csv`.
  - `generate_comparison_charts(charts_dir)`: Generates `cpu_comparison.png`, `memory_comparison.png`, `disk_comparison.png`, and `overall_analysis.png`.

---

## 3. Cross-Cutting Utilities

### 3.1 Input Validators (`utils/validators.py`)
- `validate_positive_int(val, name)`: Enforces $val > 0$.
- `validate_non_negative_int(val, name)`: Enforces $val \ge 0$.
- `validate_process_list(processes)`: Checks unique PIDs, non-negative arrival, positive burst.
- `validate_memory_inputs(blocks, requests)`: Verifies all sizes $> 0$.
- `validate_bankers_matrix(allocation, max_demand, available)`: Verifies dimensional consistency and $Allocation \le Max$.
- `validate_cylinder_requests(requests, initial_head, max_cylinders)`: Verifies tracks within $[0, MaxCylinders - 1]$.

### 3.2 Activity Logger (`utils/logger.py`)
- Initializes and provides `logger` writing to `logs/activity.log`.
- Captures system lifecycle events, execution benchmarks, warnings, and errors.

### 3.3 Presentation Helpers (`utils/helpers.py`)
- `format_table(headers, rows)`: Renders clean ASCII tables with borders.
- `render_gantt_ascii(segments)`: Renders textual timeline bars for process execution.

---

## 4. Main Controller (`main.py`)

- Coordinates user navigation via an interactive terminal loop:
  ```
  =============================================
         OS RESOURCE MANAGEMENT SIMULATOR
  =============================================
  1. CPU Scheduling (FCFS, SJF, RR, Priority)
  2. Memory Management (First, Best, Worst Fit)
  3. Deadlock Management (Banker's Algorithm)
  4. Disk Scheduling (FCFS, SSTF, SCAN, C-SCAN)
  5. Performance Analysis & Reporting
  6. Exit
  =============================================
  ```
- Catches and reports errors gracefully, dispatches to appropriate module workflows, and handles graceful application shutdown.
