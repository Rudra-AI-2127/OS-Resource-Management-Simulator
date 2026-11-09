# OS Resource Management Simulator — Comprehensive Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete, modular, thoroughly tested, and academically defensible Operating System Resource Management Simulator in Python 3.11+, satisfying all five 20-mark evaluation phases prescribed by the course faculty by 14 November 2026.

**Architecture:** Layered modular architecture separating User Interfaces (`main.py`, `app.py`), Controller & Validation (`utils/validators.py`), Core Resource-Management Engines (`modules/`), Comparative Reporting (`modules/reporting.py`), and Automated Testing (`tests/`).

**Tech Stack:** Python 3.11+, Matplotlib, Pandas, NumPy (optional), standard library (`dataclasses`, `unittest`, `logging`, `csv`, `pathlib`), POSIX Bash (`run.sh`, `run_tests.sh`).

**Spec:** [requirements.md](file:///C:/Users/rpsra/Downloads/Operating-Systems-Lab/Phase_1_Design/requirements.md), [assumptions.md](file:///C:/Users/rpsra/Downloads/Operating-Systems-Lab/Phase_1_Design/assumptions.md), and [acceptance_criteria.md](file:///C:/Users/rpsra/Downloads/Operating-Systems-Lab/Phase_1_Design/acceptance_criteria.md).

---

## Global Constraints

- **Python Version**: Strictly Python 3.11+ compatible (verified on Python 3.12.3 in WSL).
- **Core Algorithms**: Implement all 12 algorithms across CPU, Memory, Deadlock, and Disk.
- **Preemption Defaults**: Non-preemptive SJF, non-preemptive Priority (lower number = higher priority), preemptive Round Robin ($q \ge 1$), non-preemptive FCFS.
- **Memory Splitting**: Variable-sized partitioning with dynamic block splitting; internal fragmentation is 0 under dynamic splitting.
- **Disk Geometry**: Cylinders $0$ to $199$ ($200$ total); default initial head $53$; initial direction `up`; C-SCAN jump seek ($|199 - 0|$) included in total head movement.
- **Zero Fabrication**: All results, metrics, Gantt charts, and plots must be dynamically computed by the code.
- **Automation**: Executable via `run.sh` and `run_tests.sh`.

---

## Review Focus (Key Failure Modes & Edge Cases)

1. **CPU Idle Interval Handling**: Gaps between process arrival times where CPU has zero ready processes (must log `[IDLE]` without skewing waiting time calculations).
2. **Round Robin Tie-Breaking**: Fresh process arrival at time $t$ coinciding with process preemption at time $t$ (fresh arrival enqueued *before* preempted job).
3. **Memory Insufficient Space & External Fragmentation**: Process request exceeding any single free block but less than cumulative free memory (must flag process failed and report exact external fragmentation).
4. **Deadlock Matrix Inconsistency & Unsafe States**: User supplying $Allocation > Max$ or an inherently deadlocked state (must reject or detect unsafe state without infinite loops).
5. **Disk Cylinder Boundary Sweeps**: SCAN/C-SCAN hitting cylinder boundaries ($199$ or $0$) accurately without duplicate visits or off-by-one cylinder counts.

---

## Milestone-Based Task Breakdown

```
+---------------------------------------------------------------------------------+
|                               MILESTONE ROADMAP                                 |
|                                                                                 |
| Milestone 1: Phase 1 Architectural Design & Documentation (Completed)          |
| Milestone 2: Shared Utilities, Logging & Validation Layer                       |
| Milestone 3: CPU Scheduling Module & TDD Test Suite                             |
| Milestone 4: Memory Management Module & TDD Test Suite                          |
| Milestone 5: Deadlock Management Module & TDD Test Suite                        |
| Milestone 6: Disk Scheduling Module & TDD Test Suite                            |
| Milestone 7: Integration Controller (main.py) & Bash Scripts                    |
| Milestone 8: Reporting Engine, Datasets, CSV Exporters & Matplotlib Charts      |
| Milestone 9: Phase 4 Test Matrix (TC01-TC09+), Logging Verification & Excel     |
| Milestone 10: Phase 5 Documentation, README, Project Report & Viva Preparation  |
+---------------------------------------------------------------------------------+
```

---

### Task 1: Shared Utilities, Logging & Defensive Validators (Milestone 2)

- **Task ID**: `TASK-01`
- **Description**: Implement centralized logging, validation functions, ASCII tabulators, and Gantt chart renderers.
- **Dependencies**: Phase 1 approval.
- **Files Affected**:
  - Create: `utils/__init__.py`
  - Create: `utils/logger.py`
  - Create: `utils/validators.py`
  - Create: `utils/helpers.py`
  - Test: `tests/test_validators.py`
- **Acceptance Criteria**:
  - `setup_logger()` configures `logs/activity.log` and avoids duplicate handlers.
  - Validators catch negative values, empty lists, matrix mismatches, and cylinder bounds, raising descriptive `ValueError`.
  - Helpers render clean ASCII bordered tables and text Gantt bars.
- **Verification Method**: `python -m unittest tests/test_validators.py`

---

### Task 2: CPU Scheduling Engine with TDD (Milestone 3)

- **Task ID**: `TASK-02`
- **Description**: Implement FCFS, SJF (non-preemptive), Round Robin ($q$), and Priority Scheduling (non-preemptive, lower numeric value = higher priority), with metric calculations and Gantt chart assembly.
- **Dependencies**: `TASK-01`.
- **Files Affected**:
  - Create: `modules/__init__.py`
  - Create: `modules/cpu_scheduling.py`
  - Test: `tests/test_cpu.py`
- **Acceptance Criteria**:
  - Matches Blueprint example workload ($P_1(0,5), P_2(1,3), P_3(2,8), P_4(3,2)$) with exact values for $CT, TAT, WT, RT$.
  - Correctly captures `[IDLE]` periods when arrival gap occurs.
  - Round Robin $q=1$ and $q=2$ correctly time-slices processes.
  - Calculates Average Waiting Time and Average Turnaround Time.
- **Verification Method**: `python -m unittest tests/test_cpu.py`

---

### Task 3: Memory Management Engine with Dynamic Splitting & TDD (Milestone 4)

- **Task ID**: `TASK-03`
- **Description**: Implement First Fit, Best Fit, and Worst Fit dynamic partition allocation with block splitting and fragmentation auditing.
- **Dependencies**: `TASK-01`.
- **Files Affected**:
  - Create: `modules/memory_management.py`
  - Test: `tests/test_memory.py`
- **Acceptance Criteria**:
  - Dynamic block splitting implemented; remaining space returned to the active free block pool.
  - Internal fragmentation is 0 under dynamic splitting.
  - Accurately computes external fragmentation when allocation fails.
  - Matches Blueprint example (Blocks: $100, 500, 200, 300, 600$; Requests: $212, 417, 112, 426$).
- **Verification Method**: `python -m unittest tests/test_memory.py`

---

### Task 4: Deadlock Management Engine (Banker's Algorithm) with TDD (Milestone 5)

- **Task ID**: `TASK-04`
- **Description**: Implement $Need$ matrix calculation, Banker's Safety Algorithm, safe sequence derivation, and dynamic resource-request safety check with speculative rollback.
- **Dependencies**: `TASK-01`.
- **Files Affected**:
  - Create: `modules/deadlock.py`
  - Test: `tests/test_deadlock.py`
- **Acceptance Criteria**:
  - Correctly derives $Need[i][j] = Max[i][j] - Allocation[i][j]$.
  - Safely identifies safe sequence for Blueprint workload ($P_1 \to P_3 \to P_4 \to P_0 \to P_2$).
  - Detects unsafe states when no process can complete.
  - Evaluates dynamic resource requests ($Request \le Need \land Request \le Available$) and rolls back if unsafe.
- **Verification Method**: `python -m unittest tests/test_deadlock.py`

---

### Task 5: Disk Scheduling Engine with TDD (Milestone 6)

- **Task ID**: `TASK-05`
- **Description**: Implement FCFS, SSTF, SCAN, and C-SCAN over track cylinders ($0$ to $199$), calculating seek sequence, total head movement, and average seek distance.
- **Dependencies**: `TASK-01`.
- **Files Affected**:
  - Create: `modules/disk_scheduling.py`
  - Test: `tests/test_disk.py`
- **Acceptance Criteria**:
  - Blueprint trace (Requests: $98, 183, 37, 122, 14, 124, 65, 67$; Initial Head: $53$) matches textbook calculations: SSTF yields $299$ cylinders.
  - SCAN sweeps to boundary $199$ before reversing.
  - C-SCAN sweeps to boundary $199$, jumps to $0$ (accounting for $|199 - 0| = 199$ cylinders seek), and resumes upward.
  - Average head movement = Total head movement / Requests serviced.
- **Verification Method**: `python -m unittest tests/test_disk.py`

---

### Task 6: Main Application Controller & Bash Automation (Milestone 7)

- **Task ID**: `TASK-06`
- **Description**: Implement the central interactive menu in `main.py`, connecting all 5 modules, and provide `run.sh` and `run_tests.sh`.
- **Dependencies**: `TASK-02`, `TASK-03`, `TASK-04`, `TASK-05`.
- **Files Affected**:
  - Create: `main.py`
  - Create: `run.sh` (POSIX `LF`)
  - Create: `run_tests.sh` (POSIX `LF`)
- **Acceptance Criteria**:
  - Options 1 to 6 navigate smoothly with clean return-to-menu loops.
  - Handles invalid menu selections and keyboard interrupts gracefully.
  - Bash scripts execute cleanly in Linux/WSL environment.
- **Verification Method**: `bash run_tests.sh` in WSL and manual execution of `python main.py`.

---

### Task 7: Reporting Engine, Datasets & Matplotlib Charts (Milestone 8)

- **Task ID**: `TASK-07`
- **Description**: Implement standardized benchmarking on baseline datasets, CSV result exporters, and the Matplotlib figure generation engine.
- **Dependencies**: `TASK-06`.
- **Files Affected**:
  - Create: `modules/reporting.py`
  - Create: `data/cpu_input.csv`
  - Create: `data/memory_input.csv`
  - Create: `data/disk_input.csv`
  - Generate: `results/cpu_results.csv`
  - Generate: `results/memory_results.csv`
  - Generate: `results/disk_results.csv`
  - Generate: `charts/cpu_comparison.png`
  - Generate: `charts/memory_comparison.png`
  - Generate: `charts/disk_comparison.png`
  - Generate: `charts/overall_analysis.png`
  - Create: `Phase_3_Analysis/observations.md`
- **Acceptance Criteria**:
  - Exports structured CSV results for all 4 modules.
  - Automatically saves 4 publication-quality 300 DPI Matplotlib charts to `charts/`.
  - Produces detailed academic observations in `observations.md`.
- **Verification Method**: `python -c "from modules.reporting import generate_comparison_charts; generate_comparison_charts()"`

---

### Task 8: Test Matrix (TC01–TC09+) Verification & Activity Audit Log (Milestone 9)

- **Task ID**: `TASK-08`
- **Description**: Complete the formal verification suite, populate `test_cases.xlsx`, `test_results.csv`, and audit `logs/activity.log`.
- **Dependencies**: `TASK-07`.
- **Files Affected**:
  - Update: `tests/test_reporting.py`
  - Create: `Phase_4_Testing/test_cases.xlsx`
  - Create: `Phase_4_Testing/test_results.csv`
  - Verify: `logs/activity.log`
- **Acceptance Criteria**:
  - All test cases TC01–TC09 and extended cases pass with 100% assertions valid.
  - `test_results.csv` records Test ID, Scenario, Input, Expected Result, Actual Result, and PASS status.
  - `logs/activity.log` captures lifecycle events, warnings, and benchmark runs.
- **Verification Method**: `python -m unittest discover -s tests`

---

### Task 9: Academic Documentation, Screenshots & Viva Kit (Milestone 10)

- **Task ID**: `TASK-09`
- **Description**: Assemble the final comprehensive README, execution screenshots, 15–25 page Project Report, and viva defense guide.
- **Dependencies**: `TASK-08`.
- **Files Affected**:
  - Create: `README.md`
  - Create: `screenshots/*.png`
  - Create: `documentation/project_report.md` (and PDF export)
  - Create: `documentation/viva_preparation_guide.md`
- **Acceptance Criteria**:
  - Root `README.md` covers project overview, technologies, installation, execution, sample traces, and testing.
  - Captured screenshots depict real terminal sessions and generated charts.
  - Project report adheres to the 11-section format specified in Blueprint Section 6.5.
  - Viva preparation guide thoroughly answers all sample faculty viva questions.
- **Verification Method**: Complete peer review and documentation audit.
