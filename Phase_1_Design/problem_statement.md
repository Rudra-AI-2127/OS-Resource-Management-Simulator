# Problem Statement — OS Resource Management Simulator

**Course**: Operating Systems Lab  
**Project**: OS Resource Management Simulator  
**Subtitle**: Integrated Operating System Resource Management Simulator  
**Phase**: Phase 1 — System Design and Planning (20 Marks)  

---

## 1. Context and Domain Background

An operating system acts as the intermediary between hardware resources and user applications. Its core responsibility is resource abstraction, arbitration, and scheduling. Modern computing workloads demand high CPU throughput, efficient volatile memory allocation, deadlock-free concurrency, and minimal secondary storage seek latency.

Operating systems utilize four primary resource-management subsystems to achieve these goals:
1. **CPU Scheduler**: Dictates the chronological dispatch order of ready processes onto available processor cores.
2. **Memory Manager**: Allocates variable-sized contiguous physical memory segments to requesting tasks, reclaiming freed partitions and mitigating fragmentation.
3. **Deadlock Manager**: Governs shared, non-preemptible resource allocation vectors to prevent circular waiting and system-wide lockups.
4. **Disk Scheduler**: Optimizes the physical movement of electro-mechanical disk arm read/write heads across track cylinders to maximize I/O throughput.

---

## 2. Problem Definition

In undergraduate and graduate academic operating systems curricula, the mathematical mechanics and performance trade-offs of these algorithms are frequently studied purely in theoretical abstraction or through disconnected, one-off toy scripts. This creates several acute educational challenges:

1. **Lack of Integrated System Perspective**: Real-world operating systems manage resources concurrently. Evaluating scheduling, memory allocation, and concurrency in isolated, ad-hoc scripts conceals the interconnected nature of OS resource management.
2. **Empirical Verification Deficit**: Without empirical benchmarking under identical workloads, students cannot visualize why an algorithm such as Shortest Job First (SJF) minimizes mean waiting time while introducing starvation risks, or how the convoy effect degrades First-Come, First-Served (FCFS) performance.
3. **Misconceptions in Resource Accounting**: Conceptual confusions frequently occur—such as conflating leftover space from a split variable partition with internal fragmentation, or miscalculating C-SCAN wraparound cylinder seek movement.
4. **Absence of Standardized Benchmarking**: Toy implementations rarely produce reproducible data exports (CSVs), standardized execution timelines (Gantt charts), or automated regression tests.

---

## 3. The Proposed Solution

The **OS Resource Management Simulator** solves this problem by providing an integrated, robust, Python-based academic simulation platform that models all four resource management domains in a single modular architecture.

The platform provides:
- **Comprehensive Algorithm Coverage**: 12 algorithms implemented across CPU, memory, deadlock, and disk domains.
- **Strict Mathematical Accuracy**: Exact calculation of completion times, turnaround times, waiting times, response times, memory utilization, fragmentation audits, safe execution vectors, and total/average cylinder seek counts.
- **Dual Operating Modes**:
  1. *Interactive Exploratory Mode*: Allows users to input custom parameters, evaluate edge cases, and view step-by-step execution traces and Gantt charts.
  2. *Automated Comparative Benchmarking Mode*: Ingests standardized baseline workloads from CSV files, executes competing algorithms under identical initial conditions, and produces side-by-side comparison tables.
- **Analytical Visualizations**: Automatically generates publication-quality Matplotlib figures illustrating metric trade-offs across all modules.
- **Engineering Rigor**: Built on Python 3.11+, defensive validation gateways, structured audit logging, 100% automated `unittest` test coverage, and POSIX Bash execution automation.
