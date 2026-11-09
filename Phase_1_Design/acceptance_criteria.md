# Acceptance Criteria & Verification Matrix

**Project Title**: OS Resource Management Simulator  
**Document**: Quality Assurance & Acceptance Specification  
**Document Version**: 1.0.0 (Phase 1A Discovery)  
**Source of Truth**: Course Faculty Blueprint & Assessment Criteria (5 Phases @ 20 Marks Each = 100 Marks)  

---

## 1. Quality Assurance Strategy

To ensure full compliance with academic grading standards and eliminate any risk of fabricated or unsubstantiated claims, every requirement must satisfy explicit, verifiable acceptance criteria. No feature or milestone shall be marked complete without passing automated unit tests, edge-case checks, and empirical output verification.

---

## 2. Phase-by-Phase Acceptance Criteria

### 2.1 Phase 1: System Design and Planning (20 Marks)
- [ ] **AC-P1-01 (Architecture Completeness)**: `Phase_1_Design/` contains all mandatory documents:
  - `problem_statement.md`
  - `objectives.md`
  - `system_architecture.png` (high-resolution schematic generated via design guidelines)
  - `workflow_diagram.png` (detailed process lifecycle and dataflow diagram)
  - `data_structures.md`
  - `module_description.md`
  - `implementation_plan.md`
  - `requirements.md`
  - `assumptions.md`
  - `acceptance_criteria.md`
- [ ] **AC-P1-02 (Boundary & Algorithmic Clarity)**: Algorithmic defaults (non-preemptive SJF/Priority, variable memory splitting, disk geometry, C-SCAN wraparound) are documented with mathematical rationale and zero ambiguous assumptions.
- [ ] **AC-P1-03 (Faculty Blueprint Alignment)**: The design directly mirrors Section 2.5 and Section 7 of the course blueprint.

### 2.2 Phase 2: Core Resource-Management Modules (20 Marks)
- [ ] **AC-P2-01 (CPU Scheduling)**:
  - Implements `fcfs()`, `sjf()`, `round_robin()`, `priority_scheduling()`, `calculate_metrics()`, and `generate_gantt_chart()`.
  - Accurately handles staggered arrival times, CPU idle intervals, and tie-breakers.
  - Generates mathematical metrics: $TAT = CT - AT$, $WT = TAT - BT$, and response time.
  - Verification: Blueprint example workload ($P_1(0,5), P_2(1,3), P_3(2,8), P_4(3,2)$) matches manual theoretical values.
- [ ] **AC-P2-02 (Memory Management)**:
  - Implements `first_fit()`, `best_fit()`, `worst_fit()`, `calculate_fragmentation()`, and `display_allocation()`.
  - Free block dynamic splitting is enforced; leftover space is correctly returned to the free pool.
  - Distinguishes external fragmentation from internal fragmentation with exact mathematical audits.
  - Verification: Blueprint workload (Blocks: $100, 500, 200, 300, 600$; Requests: $212, 417, 112, 426$) allocates identically to standard OS memory allocation behavior.
- [ ] **AC-P2-03 (Deadlock Management)**:
  - Implements `calculate_need()`, `bankers_algorithm()`, `check_safe_state()`, and `display_safe_sequence()`.
  - Accurately derives $Need = Max - Allocation$.
  - Detects safe states and returns valid safe sequences (e.g., $P_1 \to P_3 \to P_4 \to P_0 \to P_2$).
  - Detects unsafe states when allocation cannot proceed without risking deadlock.
  - Implements dynamic resource-request safety verification with speculative state rollback.
- [ ] **AC-P2-04 (Disk Scheduling)**:
  - Implements `fcfs_disk()`, `sstf()`, `scan()`, `cscan()`, and `calculate_head_movement()`.
  - Verification: Blueprint sample (Requests: $98, 183, 37, 122, 14, 124, 65, 67$; Initial Head: $53$) yields exact textbook seek sequences and head movements (e.g., SSTF produces $299$ cylinders).
- [ ] **AC-P2-05 (Unified Main Controller)**:
  - `main.py` provides an interactive menu (Options 1–6) dispatching cleanly to all modules without unhandled exceptions.
- [ ] **AC-P2-06 (Bash Automation)**:
  - `run.sh` and `run_tests.sh` execute successfully with POSIX line endings (`LF`) in Bash/WSL.

### 2.3 Phase 3: Performance Analysis and Comparison (20 Marks)
- [ ] **AC-P3-01 (Identical Baseline Benchmarking)**:
  - All algorithms within a module execute against identical input workloads stored in `data/` (`cpu_input.csv`, `memory_input.csv`, `disk_input.csv`).
- [ ] **AC-P3-02 (Tabular and CSV Output)**:
  - Comparison tables are generated in console and exported to CSV files (`results/cpu_results.csv`, `results/memory_results.csv`, `results/disk_results.csv`).
- [ ] **AC-P3-03 (Visualizations Engine)**:
  - At least 4 distinct high-resolution Matplotlib figures are automatically generated in `charts/`:
    1. `cpu_comparison.png` (Average Waiting Time & Turnaround Time grouped bar chart).
    2. `memory_comparison.png` (Allocation success count, memory utilized, and fragmentation).
    3. `disk_comparison.png` (Total head movement per algorithm).
    4. `overall_analysis.png` (Executive multi-domain summary dashboard).
- [ ] **AC-P3-04 (Technical Observations)**:
  - `Phase_3_Analysis/observations.md` provides in-depth academic explanations of results, trade-offs (e.g., FCFS convoy effect vs SJF starvation risk), and workload sensitivity.

### 2.4 Phase 4: Testing and Reliability (20 Marks)
- [ ] **AC-P4-01 (Automated Test Suite)**:
  - `tests/` contains automated unit tests: `test_cpu.py`, `test_memory.py`, `test_deadlock.py`, and `test_disk.py`.
  - 100% of test cases pass cleanly under `python -m unittest discover -s tests`.
- [ ] **AC-P4-02 (Blueprint Test Matrix Fulfillment)**:
  - Test matrix TC01–TC09 implemented and verified:
    - `TC01`: Normal CPU scheduling correctness.
    - `TC02`: Rejection of negative burst times.
    - `TC03`: Graceful handling of empty process queues.
    - `TC04`: Correct memory block allocation.
    - `TC05`: Handled rejection when memory is insufficient.
    - `TC06`: Valid safe sequence under safe deadlock conditions.
    - `TC07`: Detection and warning on unsafe state.
    - `TC08`: Disk seek sequence and cylinder count accuracy.
    - `TC09`: Menu validation for invalid options.
- [ ] **AC-P4-03 (Test Case Documentation)**:
  - `Phase_4_Testing/test_cases.xlsx` and `Phase_4_Testing/test_results.csv` present every test case ID, description, input, expected result, actual result, and PASS status.
- [ ] **AC-P4-04 (Activity Audit Logging)**:
  - `logs/activity.log` captures timestamps, execution levels (`INFO`, `WARNING`, `ERROR`), algorithm invocations, and validation events without cluttering calculation internals.

### 2.5 Phase 5: Documentation and Demonstration (20 Marks)
- [ ] **AC-P5-01 (Complete Source Repository)**:
  - Submission includes the entire structured folder tree per Blueprint Section 7.
- [ ] **AC-P5-02 (Root README.md)**:
  - Comprehensive guide covering overview, technologies, installation, execution commands, testing instructions, and architecture breakdown.
- [ ] **AC-P5-03 (Sample Traces & Screenshots)**:
  - `screenshots/` contains real captured execution runs for CLI navigation, CPU scheduling, memory allocation, deadlock verification, disk scheduling, and charts.
  - Reproducible sample I/O traces documented in text format.
- [ ] **AC-P5-04 (Academic Project Report)**:
  - 15–25 page formal academic report covering Introduction, Problem Statement, Objectives, System Design, Technologies, Implementation, Results, Analysis, Testing, Conclusion, and References.
- [ ] **AC-P5-05 (Viva Readiness)**:
  - Documented viva defense question-and-answer preparation guide covering all faculty viva questions in Blueprint Section 6.6.

---

## 3. Requirement-to-Test Traceability Matrix

| Requirement ID | Description | Primary Test Case | Verification Method |
|---|---|---|---|
| **FR-CPU-01 / 02** | FCFS, SJF, RR, Priority Algorithm Execution | `TC01`, `TC10` | Unit test assertions on CT, TAT, WT against analytical benchmark. |
| **VR-01 / VR-02** | CPU Input Validation (Negative Burst/Arrival) | `TC02` | `assertRaises(ValueError)` on invalid process parameters. |
| **VR-06** | Empty CPU Process Collection | `TC03` | Exception handling returning descriptive validation error. |
| **FR-MEM-01 / 02** | First, Best, Worst Fit Memory Allocation | `TC04` | Assert process-to-block mapping against theoretical trace. |
| **FR-MEM-04** | Insufficient Memory & External Frag | `TC05` | Assert failed allocation flag and external fragmentation calculation. |
| **FR-DLK-01 / 02** | Deadlock Need Matrix & Safe Sequence | `TC06` | Assert generated safe sequence satisfies all process claims. |
| **FR-DLK-03 / 04** | Unsafe State Detection | `TC07` | Assert system returns `is_safe=False` and empty sequence. |
| **FR-DSK-01 / 02** | Disk Scheduling Algorithms (SSTF, SCAN, etc.) | `TC08` | Assert seek path and total head movement match 299 cylinders. |
| **VR-07** | Interactive Menu Validation | `TC09` | CLI mock input test verifying error message on invalid choice. |
| **FR-REP-02 / 03** | CSV Generation and Plotting Engine | `TC11` | Assert existence and non-zero byte size of generated CSVs and PNGs. |
| **FR-CLI-04** | Structured Activity Logging | `TC12` | Inspect `logs/activity.log` for expected log signatures. |
