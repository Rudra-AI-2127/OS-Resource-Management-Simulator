# Algorithmic Assumptions, Boundaries & Architectural Decisions

**Project Title**: OS Resource Management Simulator  
**Document**: Algorithmic Assumptions and Limitations  
**Document Version**: 1.0.0 (Phase 1A Discovery)  
**Source of Truth**: Course Faculty Blueprint & Systematic Requirement Discovery  

---

## 1. Overview and Intent

This document establishes the precise mathematical models, default behaviors, edge-case resolution rules, and structural assumptions governing all 12 algorithms implemented in the **OS Resource Management Simulator**. 

Where textbook definitions or faculty blueprints offer multiple valid interpretations, this document defines a single, consistent engineering default to guarantee mathematical repeatability, consistent testing, and clear defense during the academic viva.

---

## 2. Module A: CPU Scheduling Assumptions

### 2.1 Preemption Policies
- **First-Come, First-Served (FCFS)**: Strictly **non-preemptive**. The CPU executes the arriving process until full completion.
- **Shortest Job First (SJF)**: Default is **non-preemptive**. Once a process with the shortest burst time among ready processes acquires the CPU, it runs to completion without interruption.
  - *Rationale*: Non-preemptive SJF provides a distinct contrast to preemptive Round Robin and prevents frequent context-switching overhead simulation in non-real-time workloads. Preemptive SJF (Shortest Remaining Time First / SRTF) is treated as an optional comparison extension.
- **Priority Scheduling**: Default is **non-preemptive**. The ready process with the highest priority acquires the CPU and runs to completion.
- **Round Robin (RR)**: Strictly **preemptive**. Each process executes for at most a time slice equal to the configured Time Quantum $q$ ($q \ge 1$, default $q = 2$). If a process does not complete within $q$, it is preempted and returned to the tail of the ready queue.

### 2.2 Priority Convention
- **Lower Numerical Value = Higher Priority**:
  - Priority `0` or `1` represents the highest priority, while higher numbers (`2, 3, 4, ...`) represent lower priority levels (standard UNIX/POSIX convention).
  - *Rationale*: Aligns with standard operating system conventions (e.g., nice values where lower indicates higher urgency) and Silberschatz OS concepts.

### 2.3 Ready Queue & Arrival Tie-Breaking
- **Tie-Breaking Rule**: When two or more processes have identical priority (in Priority Scheduling), identical burst time (in SJF), or arrive simultaneously at time $t$:
  1. Primary tie-breaker: Earlier `Arrival Time` ($AT$).
  2. Secondary tie-breaker: Lexicographical order of `Process ID` (e.g., `P1` before `P2`).
- **Simultaneous Arrival vs Preemption in Round Robin**:
  - If process $P_a$ is preempted at time $t$, and process $P_b$ arrives fresh at time $t$, the fresh arrival $P_b$ is enqueued into the ready queue *before* the preempted process $P_a$ is re-appended.
  - *Rationale*: Prevents starvation of newly arriving jobs and ensures fair queue dispatching.

### 2.4 CPU Idle Time Handling
- When all arrived processes have completed execution and the ready queue is empty, but future processes are scheduled to arrive at $AT > t_{current}$, the CPU enters an **IDLE** state until the next arrival time.
- The timeline and Gantt chart explicitly log `[IDLE]` intervals.
- Metrics are calculated such that idle periods contribute to system timeline duration but do not distort individual process waiting times ($WT = TAT - BT$).

### 2.5 Metric Definitions
- $CT$ (**Completion Time**): Time instant when process completes execution.
- $TAT$ (**Turnaround Time**): Total elapsed time from arrival to completion ($TAT = CT - AT$).
- $WT$ (**Waiting Time**): Total time spent waiting in the ready queue ($WT = TAT - BT$).
- $RT$ (**Response Time**): Time elapsed from arrival to the first time the process is granted CPU execution ($RT = t_{first\_dispatch} - AT$).
- For non-preemptive algorithms, $RT = WT$. For preemptive Round Robin, $RT \le WT$.

---

## 3. Module B: Memory Management Assumptions

### 3.1 Dynamic Variable-Sized Partitioning (Splitting Model)
- Memory is modeled as an array of contiguous, variable-sized free blocks.
- **Partition Splitting Rule**: When an incoming process of size $S_{req}$ is allocated to a block of size $S_{block}$ where $S_{block} > S_{req}$:
  1. The block is split into an allocated partition of size $S_{req}$.
  2. The remaining partition of size $S_{rem} = S_{block} - S_{req}$ remains in the free memory pool as an independent free block at the adjusted memory address.
- **Internal vs External Fragmentation**:
  - **Internal Fragmentation**: Because free blocks are split exactly to the process's requested size, dynamic partitioning produces **0 internal fragmentation** ($IF = 0$). Leftover space from a split block is **not** internal fragmentation; it is available for subsequent allocations.
  - If a static fixed-partition scenario is explicitly evaluated for educational comparison, internal fragmentation is recorded as $S_{block} - S_{req}$.
  - **External Fragmentation**: Occurs when total free memory across all unallocated blocks is greater than or equal to an unallocated process request ($\sum S_{free} \ge S_{req}$), but no single contiguous free block is large enough to accommodate the request.

### 3.2 Allocation Search Policies
- **First Fit**: Scans the free block pool in linear index order (lowest physical address first). Allocates the very first block satisfying $S_{block} \ge S_{req}$.
- **Best Fit**: Scans all available blocks in the pool. Selects the block that satisfies $S_{block} \ge S_{req}$ with the minimum remaining space ($\min(S_{block} - S_{req})$). Ties broken by lowest block index.
- **Worst Fit**: Scans all available blocks in the pool. Selects the block that satisfies $S_{block} \ge S_{req}$ with the maximum remaining space ($\max(S_{block} - S_{req})$). Ties broken by lowest block index.

### 3.3 Deallocation and Coalescing (Optional Extension)
- In single-pass batch simulations, allocations are processed in sequential arrival order without pre-mature deallocation.
- In interactive/dynamic simulation mode, process deallocation triggers immediate coalescing (merging) of physically adjacent free blocks into a single consolidated free block.

---

## 4. Module C: Deadlock Management Assumptions (Banker's Algorithm)

### 4.1 System Model
- The system manages $n$ concurrent processes ($P_0, P_1, \dots, P_{n-1}$) and $m$ distinct resource types ($R_0, R_1, \dots, R_{m-1}$).
- Resources are multi-instance: each resource type $R_j$ has a finite integer quantity of available units.
- State vectors and matrices:
  - $Available[j]$: Count of currently unallocated units of resource type $R_j$.
  - $Max[i][j]$: Maximum potential units of resource $R_j$ that process $P_i$ may request during execution.
  - $Allocation[i][j]$: Units of resource $R_j$ currently held by process $P_i$.
  - $Need[i][j]$: Remaining units of resource $R_j$ that process $P_i$ may request ($Need[i][j] = Max[i][j] - Allocation[i][j]$).

### 4.2 Safety Invariant
- A system state is **SAFE** if there exists at least one order $\langle P_{s_0}, P_{s_1}, \dots, P_{s_{n-1}} \rangle$ (the *Safe Sequence*) in which all processes can sequentially obtain their maximum remaining requirements ($Need_i \le Work$), terminate, and release all currently held resources back into the pool ($Work = Work + Allocation_i$).
- If no such permutation exists, the state is classified as **UNSAFE** (indicating deadlock or imminent risk of deadlock).

### 4.3 Resource Request Protocol
- When process $P_i$ makes a dynamic request vector $Request_i$:
  1. **Condition 1**: If $\exists j$ such that $Request_i[j] > Need_i[j]$, the request is **rejected** with an error: process exceeded its declared maximum claim.
  2. **Condition 2**: If $\exists j$ such that $Request_i[j] > Available[j]$, the process must **wait** (insufficient resources currently available).
  3. **Speculative Allocation**:
     $$Available' = Available - Request_i$$
     $$Allocation'_i = Allocation_i + Request_i$$
     $$Need'_i = Need_i - Request_i$$
  4. Run Safety Algorithm on tentative state:
     - If state is **SAFE**: Grant request immediately and update official system state.
     - If state is **UNSAFE**: Roll back tentative state to original values. Process $P_i$ must wait; request cannot be granted safely.

---

## 5. Module D: Disk Scheduling Assumptions

### 5.1 Physical Geometry and Cylinder Boundaries
- **Cylinder Range**: Cylinders are indexed from $0$ to $MaxCylinders - 1$.
- Default configuration: $MaxCylinders = 200$, spanning tracks $[0, 199]$.
- **Initial Head Position**: Default is $53$ (or user-specified within $[0, 199]$).
- **Initial Direction**: Default is **Upward** (`up` / towards higher cylinder index, e.g., moving toward $199$). Configurable to `down` (towards cylinder $0$).

### 5.2 Algorithm Traversal Rules
- **FCFS (First-Come, First-Served)**:
  - Traverses the request sequence in strict chronological arrival order.
  - Head seek between successive requests $r_a$ and $r_b$ is $|r_b - r_a|$.
- **SSTF (Shortest Seek Time First)**:
  - At current head position $H$, greedily selects unvisited request $r^*$ where $|r^* - H| = \min_{r \in Pending} |r - H|$.
  - In case of equidistant requests (e.g., $H=50$, candidates $40$ and $60$), tie-breaker favors the request in the current direction of movement.
- **SCAN (Elevator Algorithm)**:
  - Moves in the initial direction servicing all pending requests encountered along the way.
  - Upon servicing the final pending request in that direction, the head **continues to the physical boundary cylinder** ($199$ if moving up, or $0$ if moving down) before reversing direction.
  - *Rationale*: Standard textbook SCAN (Silberschatz) visits the boundary end-stop before sweeping backwards, distinguishing it from LOOK (which reverses immediately at the furthest pending request).
- **C-SCAN (Circular SCAN)**:
  - Moves in the initial direction towards the upper boundary ($199$), servicing pending requests.
  - Upon reaching the upper boundary ($199$), the head jumps immediately across the disk to the lower boundary ($0$) **without servicing any requests on the return trip**.
  - From cylinder $0$, it resumes servicing pending requests in the original upward direction.
  - **Wraparound Head Movement Accounting**: The cylinder seek distance for the rapid return trip from $199$ to $0$ ($|199 - 0| = 199$ cylinders) **is included** in the total head movement calculation (consistent with standard academic benchmarking and Silberschatz Chapter 11).

### 5.3 Average Head Movement Formula
- The average head movement is defined as:
  $$\text{Average Head Movement} = \frac{\text{Total Head Movement}}{\text{Number of Unique Requests Serviced}}$$
- The initial head position $H_0$ is the starting origin and is not counted as a serviced request in the denominator.

---

## 6. Summary of Architectural Decisions & Traceability

| Decision Point | Option Selected | Justification & Faculty Blueprint Mapping |
|---|---|---|
| **CPU: SJF Preemption** | Non-preemptive | Matches Blueprint Page 3 and standard lab conventions; avoids duplicate logic with Round Robin. |
| **CPU: Priority Preemption** | Non-preemptive | Matches Blueprint Page 3; focuses on priority queue arbitration. |
| **CPU: Priority Ordering** | Lower integer = Higher priority | Standard POSIX and Silberschatz convention (e.g. Priority 1 beats Priority 2). |
| **Memory: Partitioning** | Variable-sized with splitting | Blueprint Page 7 explicitly distinguishes internal from external fragmentation. Split space is returned to free pool. |
| **Disk: SCAN Boundary** | Full boundary sweep (to 199/0) | Distinguishes classic SCAN from LOOK. |
| **Disk: C-SCAN Wraparound** | Include jump seek ($|199 - 0|$) | Standard academic benchmark methodology. |
| **Disk: Average Movement** | Total Movement / Count of Requests | Explicitly requested formula in Blueprint Section 2.2 / Module D. |
