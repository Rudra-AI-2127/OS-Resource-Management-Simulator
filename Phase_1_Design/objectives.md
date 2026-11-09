# Project Objectives — OS Resource Management Simulator

**Course**: Operating Systems Lab  
**Project**: OS Resource Management Simulator  
**Phase**: Phase 1 — System Design and Planning (20 Marks)  

---

## 1. Primary Academic Objectives

The overarching goal of this project is to conceptualize, design, implement, benchmark, test, and document an **Integrated Operating System Resource Management Simulator** that fulfills all 5 assessment phases (100 total marks) prescribed by the course faculty.

---

## 2. Specific Technical & Operational Objectives

### 2.1 Core Subsystem Objectives
1. **CPU Scheduling Engine**:
   - Implement First-Come First-Served (FCFS), Shortest Job First (SJF - Non-Preemptive), Round Robin (RR - Preemptive with configurable quantum $q$), and Priority Scheduling (Non-Preemptive, lower numeric value = higher priority).
   - Accurately calculate individual and average Completion Time ($CT$), Turnaround Time ($TAT$), Waiting Time ($WT$), and Response Time ($RT$).
   - Explicitly identify and render CPU idle intervals on an ASCII/textual Gantt chart.
2. **Memory Management Engine**:
   - Implement First Fit, Best Fit, and Worst Fit dynamic partition allocation policies.
   - Enforce variable-sized block splitting, returning unallocated partition remainders back into the active free block pool.
   - Quantify total allocated memory, remaining free memory, and external fragmentation.
3. **Deadlock Management Engine**:
   - Model multi-resource allocation systems with $n$ processes and $m$ resource types.
   - Automatically derive the $Need$ matrix ($Need = Max - Allocation$).
   - Implement Dijkstra's Banker's Algorithm to evaluate state safety, identify complete safe execution sequences, and safely audit dynamic resource requests with rollback capabilities.
4. **Disk Scheduling Engine**:
   - Implement FCFS, Shortest Seek Time First (SSTF), SCAN (Elevator), and Circular SCAN (C-SCAN).
   - Track precise cylinder seek steps, total head movement, and average head seek distance over a 200-cylinder geometry ($0$ to $199$).
5. **Comparative Reporting & Benchmarking Engine**:
   - Ingest identical baseline datasets to evaluate competing algorithms under controlled parameters.
   - Export structured CSV telemetry to `results/`.
   - Render at least four high-resolution Matplotlib comparison charts into `charts/`.

### 2.2 Software Engineering & Reliability Objectives
1. **Centralized Architectural Controller**:
   - Integrate all modules under a unified entry point (`main.py`) with a clean, navigable interactive terminal menu.
2. **Defensive Input Validation**:
   - Build a comprehensive validation layer (`utils/validators.py`) enforcing data types, positive numbers, non-empty collections, matrix consistency, and cylinder bounds, eliminating runtime crashes.
3. **Automated Testing & Verification**:
   - Author a complete `unittest` suite (`tests/`) implementing test matrix TC01–TC09 plus extended edge cases.
   - Provide automated Bash test runner (`run_tests.sh`) exiting with 0 error codes.
4. **Traceable Audit Logging**:
   - Implement a standardized logging system (`utils/logger.py`) recording application startup, module dispatches, user input warnings, and system errors into `logs/activity.log`.
5. **Academic Documentation & Viva Preparedness**:
   - Deliver clear documentation in `Phase_1_Design/`, `Phase_3_Analysis/`, and `Phase_4_Testing/`.
   - Compile an exhaustive 15–25 page final Project Report and comprehensive viva defense guide.
