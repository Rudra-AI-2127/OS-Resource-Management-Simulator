# Phase 3 — Technical Observations & Performance Analysis Report

## Executive Summary & System Overview

This report documents the rigorous empirical performance evaluation and comparative analysis across the four core subsystems of the **Operating Systems Resource Management Simulator**:
1. **CPU Scheduling**: Benchmarking First-Come First-Served (FCFS), Shortest Job First (SJF Non-preemptive), Round Robin (RR, $q=2$ and variable quantum), and Priority Scheduling (Non-preemptive).
2. **Memory Management**: Benchmarking contiguous allocation strategies with dynamic partition splitting — First Fit, Best Fit, and Worst Fit.
3. **Deadlock Management**: Safety verification, Need matrix computation, safe sequence determination, and dynamic speculative request evaluation with rollback using Dijkstra's Banker's Algorithm.
4. **Disk Scheduling**: Benchmarking First-Come First-Served (FCFS), Shortest Seek Time First (SSTF), SCAN (Elevator), and Circular SCAN (C-SCAN).

All benchmarks were executed on identical, controlled input datasets across **four workload tiers** (`Normal`, `Small`, `Large`, `Edge-case`), without fabricating data or assumptions. Results were tabulated using **Pandas**, exported to structured CSV files in `results/` and `Phase_3_Analysis/results/`, and rendered into publication-grade **300 DPI Matplotlib charts** in `charts/` and `Phase_3_Analysis/charts/`.

---

## 1. Metric Calculation Formulations

Each metric reported by the subsystem is mathematically defined and implemented as follows:

### 1.1 CPU Scheduling Metrics
* **Turnaround Time ($TAT_i$)**: Elapsed time from process arrival to complete termination:
  $$TAT_i = CT_i - AT_i$$
  where $CT_i$ is Completion Time and $AT_i$ is Arrival Time.
* **Waiting Time ($WT_i$)**: Total duration spent by a process waiting in the ready queue:
  $$WT_i = TAT_i - BT_i$$
  where $BT_i$ is Burst Time.
* **Response Time ($RT_i$)**: Elapsed duration from arrival to the first time CPU execution commences:
  $$RT_i = \text{Start Time}_i - AT_i$$
* **Average Waiting Time ($\overline{WT}$)**:
  $$\overline{WT} = \frac{1}{N} \sum_{i=1}^{N} WT_i$$
* **Average Turnaround Time ($\overline{TAT}$)**:
  $$\overline{TAT} = \frac{1}{N} \sum_{i=1}^{N} TAT_i$$
* **Average Response Time ($\overline{RT}$)**:
  $$\overline{RT} = \frac{1}{N} \sum_{i=1}^{N} RT_i$$
* **CPU Utilization**: Ratio of CPU active execution time to total elapsed scheduling timeline:
  $$\text{CPU Utilization} = \left( \frac{\sum_{k} \text{duration}(S_k) \text{ where } S_k \neq \text{IDLE}}{\text{Timeline End Time}} \right) \times 100\%$$

### 1.2 Memory Management Metrics
* **Allocation Success Rate**:
  $$\text{Success Rate} = \left( \frac{\text{Successful Allocations}}{\text{Total Allocation Requests}} \right) \times 100\%$$
* **Total Allocated Memory**: Sum of sizes of all processes successfully assigned to partitions:
  $$\text{Allocated Memory (KB)} = \sum_{p \in \text{Allocated}} \text{Size}(p)$$
* **Remaining Free Memory**: Total unallocated capacity across all partitions at completion:
  $$\text{Free Memory (KB)} = \sum_{b \in \text{Free Blocks}} \text{Size}(b)$$
* **Memory Utilization**: Percentage of total initial memory currently serving processes:
  $$\text{Utilization (\%)} = \left( \frac{\text{Total Allocated Memory}}{\text{Total Initial Memory Capacity}} \right) \times 100\%$$
* **Internal Fragmentation**: Unused memory inside an allocated partition. Under dynamic partition splitting, partitions are carved to the exact requested process size:
  $$\text{Internal Fragmentation} = 0\text{ KB}$$
* **External Fragmentation**: Total free memory that cannot satisfy an outstanding request because no individual contiguous partition is large enough:
  $$\text{External Frag} = \text{Total Free Memory (if any pending request failed while Total Free } \ge \text{Request Size, else } 0)$$

### 1.3 Deadlock Management Metrics (Banker's Algorithm)
* **Need Matrix**: Calculated dynamically for process $i$ and resource type $j$:
  $$Need[i][j] = MaxDemand[i][j] - Allocation[i][j]$$
* **Safety Invariant**: A system state is **SAFE** if there exists an execution sequence $\langle P_0, P_1, \dots, P_{n-1} \rangle$ such that for every $P_i$:
  $$Need[i] \le Work$$
  where $Work$ is initialized to $Available$ and updated as $Work = Work + Allocation[i]$ upon process termination.
* **Speculative Request Evaluation**: For dynamic request $Request_i$:
  1. Verify $Request_i \le Need[i]$ (claim validity).
  2. Verify $Request_i \le Available$ (capacity validity).
  3. Speculatively apply: $Available = Available - Request_i$, $Allocation[i] = Allocation[i] + Request_i$, $Need[i] = Need[i] - Request_i$.
  4. Run safety check: if SAFE, commit; if UNSAFE, rollback to pristine original state.

### 1.4 Disk Scheduling Metrics
* **Total Head Movement ($THM$)**: Cumulative absolute difference between consecutive cylinder positions along the seek sequence $\langle c_0, c_1, \dots, c_m \rangle$:
  $$THM = \sum_{k=1}^{m} |c_k - c_{k-1}|$$
* **Average Seek Distance ($\overline{HM}$)**: Mean head travel per serviced request:
  $$\overline{HM} = \frac{THM}{\text{Requests Serviced}}$$

---

## 2. CPU Scheduling Empirical Analysis

### 2.1 Comparative Empirical Results Across Workloads

The table below summarizes empirical findings across all four workload tiers:

| Workload Tier | Process Count | Algorithm | Avg Waiting Time | Avg Turnaround Time | Avg Response Time | Total Time | CPU Utilization |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **Normal** | 4 | FCFS | 5.75 | 10.25 | 5.75 | 18 | 100.0% |
| **Normal** | 4 | SJF | **4.00** | **8.50** | 4.00 | 18 | 100.0% |
| **Normal** | 4 | Round Robin (q=2) | 7.25 | 11.75 | **2.00** | 18 | 100.0% |
| **Normal** | 4 | Priority | 4.25 | 8.75 | 4.25 | 18 | 100.0% |
| **Small** | 2 | FCFS | 1.00 | 3.50 | 1.00 | 5 | 100.0% |
| **Small** | 2 | SJF | 1.00 | 3.50 | 1.00 | 5 | 100.0% |
| **Small** | 2 | Round Robin (q=2) | 1.50 | 4.00 | **0.50** | 5 | 100.0% |
| **Small** | 2 | Priority | 1.00 | 3.50 | 1.00 | 5 | 100.0% |
| **Large** | 8 | FCFS | 17.00 | 22.62 | 17.00 | 45 | 100.0% |
| **Large** | 8 | SJF | **14.25** | **19.88** | 14.25 | 45 | 100.0% |
| **Large** | 8 | Round Robin (q=2) | 21.62 | 27.25 | **5.62** | 45 | 100.0% |
| **Large** | 8 | Priority | 15.00 | 20.62 | 15.00 | 45 | 100.0% |
| **Edge-case** | 4 | FCFS | 6.00 | 10.00 | 6.00 | 16 | 100.0% |
| **Edge-case** | 4 | SJF | 6.00 | 10.00 | 6.00 | 16 | 100.0% |
| **Edge-case** | 4 | Round Robin (q=2) | 9.00 | 13.00 | **3.00** | 16 | 100.0% |
| **Edge-case** | 4 | Priority | 6.00 | 10.00 | 6.00 | 16 | 100.0% |

### 2.2 Which CPU Algorithm Achieved Lowest Average Waiting Time?
- In the **Normal Workload** (bursts 5, 3, 8, 2), **SJF** achieved the lowest average waiting time of **4.00 units** (turnaround 8.50 units), followed by Priority (4.25 units), FCFS (5.75 units), and Round Robin (7.25 units).
- In the **Large Workload** (8 processes), **SJF** also achieved the lowest average waiting time of **14.25 units** vs FCFS (17.00 units) and RR (21.62 units).
- **Critical Empirical Exception (Edge-case Workload)**: When all processes arrive simultaneously at $AT=0$ with identical burst times ($BT=4$), **SJF, FCFS, and Priority produce mathematically identical results** ($\overline{WT} = 6.00$, $\overline{TAT} = 10.00$). This proves that SJF is **not unconditionally superior**; its advantage strictly depends on burst time variance. When burst variance is zero, SJF degenerates into FCFS.

### 2.3 How Does Round Robin Quantum Affect Responsiveness & Overhead?
We executed an empirical parameter sensitivity experiment on the Normal workload with time quantums $q \in \{1, 2, 4, 8\}$:

| Time Quantum ($q$) | Avg Response Time ($\overline{RT}$) | Avg Waiting Time ($\overline{WT}$) | Avg Turnaround Time ($\overline{TAT}$) | Context Switches | Observed Scheduling Behavior |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **$q = 1$** | **0.75** | 6.50 | 11.00 | 17 | Hyper-responsive for interactive systems; severe context switch overhead |
| **$q = 2$** | 2.00 | 7.25 | 11.75 | 9 | Balanced interactive compromise; moderate switching |
| **$q = 4$** | 4.00 | 7.00 | 11.50 | 5 | Batch-leaning; reduced switching overhead; slower first response |
| **$q = 8$** | 5.75 | **5.75** | **10.25** | 3 | Degenerates exactly to FCFS (since maximum burst is 8) |

**Key Findings on Time Quantum**:
1. **Responsiveness**: Response time scales monotonically with quantum length ($\overline{RT} = 0.75 \to 2.00 \to 4.00 \to 5.75$). Small quantums deliver immediate user feedback.
2. **Context Switching Overhead**: A quantum of $q=1$ required 17 timeline segments (high dispatch penalty in real kernels), whereas $q=8$ required only 3 switches.
3. **FCFS Degeneration**: As $q \ge \max(BT_i)$, preemption ceases and Round Robin becomes FCFS in both schedule order and metrics.

### 2.4 CPU Scheduling Trade-offs
- **FCFS**: Simple $O(1)$ queue management, 0 preemption overhead, but suffers from the **Convoy Effect** when a long process (P3, $BT=8$) blocks short jobs.
- **SJF**: Provably minimizes average waiting time for known workloads, but is prone to **Starvation** for long-running processes if short processes continuously arrive. Furthermore, real-time operating systems cannot perfectly predict future CPU bursts without exponential smoothing heuristics ($\tau_{n+1} = \alpha t_n + (1-\alpha)\tau_n$).
- **Round Robin**: Completely eliminates starvation and minimizes response time, making it the ideal general-purpose desktop/interactive scheduler, but exhibits higher average waiting and turnaround times due to process interleaving.
- **Priority**: Enables differentiated Quality-of-Service (QoS), but requires priority aging mechanisms to prevent permanent starvation of low-priority tasks.

---

## 3. Memory Allocation Empirical Analysis

### 3.1 Comparative Empirical Results Across Workloads

| Workload Tier | Initial Blocks (KB) | Process Requests (KB) | Algorithm | Success Count | Fail Count | Success Rate | Allocated KB | Free KB | External Frag | Utilization |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Normal** | 100, 500, 200, 300, 600 | 212, 417, 112, 426 | First Fit | 3 | 1 | 75.0% | 741 | 959 | 959 KB | 43.6% |
| **Normal** | 100, 500, 200, 300, 600 | 212, 417, 112, 426 | **Best Fit** | **4** | **0** | **100.0%** | **1167** | **533** | **0 KB** | **68.7%** |
| **Normal** | 100, 500, 200, 300, 600 | 212, 417, 112, 426 | Worst Fit | 3 | 1 | 75.0% | 741 | 959 | 959 KB | 43.6% |
| **Small** | 200, 400 | 150, 350 | First Fit | **2** | 0 | **100.0%** | 500 | 100 | 0 KB | 83.3% |
| **Small** | 200, 400 | 150, 350 | Best Fit | **2** | 0 | **100.0%** | 500 | 100 | 0 KB | 83.3% |
| **Small** | 200, 400 | 150, 350 | Worst Fit | 1 | 1 | 50.0% | 150 | 450 | 450 KB | 25.0% |
| **Large** | 8 blocks (3574 KB) | 8 reqs (2750 KB) | First Fit | **8** | 0 | **100.0%** | 2750 | 824 | 0 KB | 76.9% |
| **Large** | 8 blocks (3574 KB) | 8 reqs (2750 KB) | Best Fit | **8** | 0 | **100.0%** | 2750 | 824 | 0 KB | 76.9% |
| **Large** | 8 blocks (3574 KB) | 8 reqs (2750 KB) | Worst Fit | 7 | 1 | 87.5% | 2000 | 1574 | 1574 KB | 56.0% |
| **Edge-case** | 100, 200, 300 | 100, 199, 305 | All Three | 2 | 1 | 66.7% | 299 | 301 | 0 KB | 49.8% |

### 3.2 Which Memory Strategy Allocated the Most Requests?
- **Best Fit was the top performer**: In the standard Normal workload, **Best Fit was the ONLY algorithm that achieved 100% allocation** (4/4 processes, 1167 KB allocated, 68.7% utilization).
- **First Fit and Worst Fit failed**: Both failed on process P4 (426 KB), achieving only 75% allocation success (741 KB allocated, 43.6% utilization).
- In the **Small workload**, Worst Fit failed severely (only 50% success vs 100% for First Fit and Best Fit).
- In the **Large workload**, First Fit and Best Fit tied at 100% (8/8 allocations, 2750 KB allocated), while Worst Fit failed on 1 process (allocating only 2000 KB).

### 3.3 Fragmentation & Memory Wastage Observations
1. **Dynamic Partition Splitting Eliminates Internal Fragmentation**: Because unallocated remainder blocks are immediately split into independent free partitions, internal fragmentation was preserved at exactly **0 KB** across all runs.
2. **The Pathology of Worst Fit**:
   - The theoretical justification for Worst Fit is that leaving the largest possible leftover remnant will maximize the chance of that remnant accommodating another process.
   - However, in our empirical tests, **Worst Fit consistently produced the highest memory wastage and failure rate**. By placing P1 (212 KB) into the 600 KB block, it left a 388 KB remnant. When P2 (417 KB) requested memory, it was forced into the 500 KB block, leaving an 83 KB remnant. When P4 (426 KB) arrived, no remaining block could fit it, even though 959 KB of free memory remained scattered in fragments (External Fragmentation = 959 KB).
   - In the Small workload, Worst Fit placed P1 (150 KB) in the 400 KB block, creating a 250 KB remnant that immediately starved P2 (350 KB).
3. **Best Fit Space Conservation**:
   - Best Fit paired P1 (212 KB) with the 300 KB block, P2 (417 KB) with the 500 KB block, P3 (112 KB) with the 200 KB block, and left the large 600 KB block intact for P4 (426 KB).
   - Trade-off: In static partition systems, Best Fit tends to create tiny unusable "slivers", but with dynamic splitting, it minimized external fragmentation to **0 KB**.

---

## 4. Deadlock Management Analysis (Banker's Algorithm)

### 4.1 System Safety & Safe Sequence Verification

The simulator evaluated multi-instance resource allocation under Dijkstra's Banker's Algorithm across all four workload tiers.

#### Normal Workload Baseline
- **Process Set**: $\{P_0, P_1, P_2, P_3, P_4\}$
- **Resource Types**: 3 instances of $[A, B, C]$
- **Available Vector**: $[3, 3, 2]$

**System Resource Matrices**:
```
+---------+-------------------+-------------------+-------------------+
| Process | Allocation (A B C)| Max Demand (A B C)| Calculated Need   |
+---------+-------------------+-------------------+-------------------+
|   P0    |      0   1   0    |      7   5   3    |      7   4   3    |
|   P1    |      2   0   0    |      3   2   2    |      1   2   2    |
|   P2    |      3   0   2    |      9   0   2    |      6   0   0    |
|   P3    |      2   1   1    |      2   2   2    |      0   1   1    |
|   P4    |      0   0   2    |      4   3   3    |      4   3   1    |
+---------+-------------------+-------------------+-------------------+
```

**Step-by-Step Safety Trace**:
1. Initial: $Work = [3, 3, 2]$. All $Finish[i] = False$.
2. Step 1: Process $P_1$ has $Need = [1, 2, 2] \le Work [3, 3, 2]$. $P_1$ finishes, releasing $[2, 0, 0] \to Work = [5, 3, 2]$.
3. Step 2: Process $P_3$ has $Need = [0, 1, 1] \le Work [5, 3, 2]$. $P_3$ finishes, releasing $[2, 1, 1] \to Work = [7, 4, 3]$.
4. Step 3: Process $P_0$ has $Need = [7, 4, 3] \le Work [7, 4, 3]$. $P_0$ finishes, releasing $[0, 1, 0] \to Work = [7, 5, 3]$.
5. Step 4: Process $P_2$ has $Need = [6, 0, 0] \le Work [7, 5, 3]$. $P_2$ finishes, releasing $[3, 0, 2] \to Work = [10, 5, 5]$.
6. Step 5: Process $P_4$ has $Need = [4, 3, 1] \le Work [10, 5, 5]$. $P_4$ finishes, releasing $[0, 0, 2] \to Work = [10, 5, 7]$.
- **Conclusion**: System is **SAFE**. Safe sequence: $\mathbf{P_1 \to P_3 \to P_0 \to P_2 \to P_4}$.

### 4.2 Dynamic Resource Request & Speculative Rollback Verification
We tested dynamic resource requests against the safety engine:

1. **Safe Request Evaluation ($P_1$ requests $[1, 0, 2]$)**:
   - Condition 1: $Request [1, 0, 2] \le Need [1, 2, 2]$ $\to$ True.
   - Condition 2: $Request [1, 0, 2] \le Available [3, 3, 2]$ $\to$ True.
   - Tentative state: $Available = [2, 3, 0]$, $Alloc(P_1) = [3, 0, 2]$, $Need(P_1) = [0, 2, 0]$.
   - Tentative safety check finds valid sequence: $P_1 \to P_3 \to P_0 \to P_2 \to P_4$.
   - **Decision: GRANTED**. System safely commits allocation.

2. **Unsafe Request Detection & Rollback (Edge-case Workload)**:
   - State: 3 processes ($P_0, P_1, P_2$), Available = $[1, 0, 0]$. Initial state is tightly safe ($P_0 \to P_1 \to P_2$).
   - Dynamic Request: $P_1$ requests $[1, 0, 0]$.
   - Condition 1: $Request [1, 0, 0] \le Need [1, 1, 0]$ $\to$ True.
   - Condition 2: $Request [1, 0, 0] \le Available [1, 0, 0]$ $\to$ True.
   - Tentative state: $Available = [0, 0, 0]$.
   - Safety check: All processes require at least 1 unit of some resource to complete ($Need(P_0)=[1, 0, 0]$, $Need(P_1)=[0, 1, 0]$, $Need(P_2)=[1, 1, 0]$). No process satisfies $Need \le Work$.
   - **Decision: DENIED**. Deadlock avoidance engine intercepts hazard and executes complete **speculative rollback**, ensuring zero state corruption.

---

## 5. Disk Scheduling Empirical Analysis

### 5.1 Comparative Empirical Results Across Workloads

| Workload Tier | Requests Stream | Initial Head | Total Cylinders | Algorithm | Total Head Movement | Avg Seek Distance | Requests Serviced |
| :--- | :--- | :---: | :---: | :--- | :---: | :---: | :---: |
| **Normal** | 98, 183, 37, 122, 14, 124, 65, 67 | 53 | 200 | FCFS | 640 cyl | 80.00 cyl/req | 8 |
| **Normal** | 98, 183, 37, 122, 14, 124, 65, 67 | 53 | 200 | **SSTF** | **236 cyl** | **29.50 cyl/req** | 8 |
| **Normal** | 98, 183, 37, 122, 14, 124, 65, 67 | 53 | 200 | SCAN (up) | 331 cyl | 41.38 cyl/req | 8 |
| **Normal** | 98, 183, 37, 122, 14, 124, 65, 67 | 53 | 200 | C-SCAN (up) | 382 cyl | 47.75 cyl/req | 8 |
| **Small** | 25, 75, 120 | 53 | 200 | **FCFS** | **123 cyl** | **41.00 cyl/req** | 3 |
| **Small** | 25, 75, 120 | 53 | 200 | SSTF | 162 cyl | 54.00 cyl/req | 3 |
| **Small** | 25, 75, 120 | 53 | 200 | SCAN (up) | 320 cyl | 106.67 cyl/req | 3 |
| **Small** | 25, 75, 120 | 53 | 200 | C-SCAN (up) | 370 cyl | 123.33 cyl/req | 3 |
| **Large** | 16 scattered requests | 53 | 200 | FCFS | 853 cyl | 53.31 cyl/req | 16 |
| **Large** | 16 scattered requests | 53 | 200 | **SSTF** | **232 cyl** | **14.50 cyl/req** | 16 |
| **Large** | 16 scattered requests | 53 | 200 | SCAN (up) | 335 cyl | 20.94 cyl/req | 16 |
| **Large** | 16 scattered requests | 53 | 200 | C-SCAN (up) | 390 cyl | 24.38 cyl/req | 16 |
| **Edge-case** | 0, 199, 50, 50, 1, 198 | 53 | 200 | FCFS | 647 cyl | 107.83 cyl/req | 6 |
| **Edge-case** | 0, 199, 50, 50, 1, 198 | 53 | 200 | **SSTF** | **252 cyl** | **42.00 cyl/req** | 6 |
| **Edge-case** | 0, 199, 50, 50, 1, 198 | 53 | 200 | SCAN (up) | 345 cyl | 57.50 cyl/req | 6 |
| **Edge-case** | 0, 199, 50, 50, 1, 198 | 53 | 200 | C-SCAN (up) | 395 cyl | 65.83 cyl/req | 6 |

### 5.2 Which Disk Algorithm Minimized Head Movement?
- In the **Normal Workload**, **SSTF achieved the lowest head movement of 236 cylinders** (29.50 cyl/req), representing a **63.1% reduction in mechanical seek travel** compared to FCFS (640 cylinders).
- In the **Large Workload** (16 requests), **SSTF was optimal**, achieving 232 cylinders (14.50 cyl/req), while FCFS traveled 853 cylinders.
- **Critical Empirical Counterexample (Small Workload)**: When requests arrived in sequential order ($25 \to 75 \to 120$), **FCFS outperformed SSTF, SCAN, and C-SCAN** (123 cyl vs 162 cyl for SSTF and 320 cyl for SCAN). SCAN and C-SCAN were severely penalized by compulsory boundary sweeps (moving all the way to cylinder 199 and jumping back to 0), proving that elevator algorithms introduce unnecessary mechanical overhead when request clusters do not span across the platter.

### 5.3 Disk Scheduling Trade-offs
1. **FCFS**:
   - *Advantages*: Zero algorithm overhead, strict fairness, absolutely zero risk of starvation.
   - *Disadvantages*: Wild mechanical oscillations ("ping-ponging") across platters on unsorted requests.
2. **SSTF (Greedy Nearest Neighbor)**:
   - *Advantages*: Minimizes total seek distance across dense workloads.
   - *Disadvantages*: **Starvation risk**. If requests arrive continuously in the vicinity of the disk arm, distant requests (e.g. tracks near cylinder 0 or 199) may wait indefinitely.
3. **SCAN (Elevator)**:
   - *Advantages*: Eliminates SSTF starvation by maintaining a monotonic direction until the boundary is reached.
   - *Disadvantages*: Biases waiting time against tracks immediately behind the sweep direction; incurs boundary sweep overhead.
4. **C-SCAN (Circular SCAN)**:
   - *Advantages*: Provides **uniform waiting time** across all cylinders by servicing only in one direction and returning via rapid seek jump to the starting boundary without servicing on the return pass.
   - *Disadvantages*: Total head movement is higher than SCAN due to the boundary jump ($199 \to 0 = 199$ cylinders).

---

## 6. Comprehensive Architectural Trade-offs Matrix

| Subsystem | Metric of Interest | Leading Algorithm | Key Trade-off / Penalty | Recommended Operational Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **CPU** | Minimum Average Waiting Time | **SJF** | Risk of starvation for long bursts; requires burst time estimation | Batch computing environments with known job durations |
| **CPU** | Interactive Responsiveness | **Round Robin ($q=1\text{ to }2$)** | Higher turnaround time; context-switch dispatch overhead | Desktop OS, interactive terminals, time-sharing shells |
| **CPU** | Quality-of-Service Guarantee | **Priority Scheduling** | Starvation of low-priority tasks unless aging is implemented | Real-time kernels, embedded devices, multimedia engines |
| **Memory** | Allocation Success & Space Preservation | **Best Fit** | Longer search latency traversing partition list | Systems with highly variable request sizes |
| **Memory** | Search Latency & Fast Allocation | **First Fit** | Higher external fragmentation on mixed workloads | High-throughput, low-latency dynamic memory managers |
| **Disk** | Minimum Seek Travel | **SSTF** | High starvation risk for edge cylinders | Local disk caches with bursty, clustered file reads |
| **Disk** | Starvation Prevention & Fairness | **SCAN (Elevator)** | Boundary travel penalty | General-purpose spinning magnetic drives |
| **Disk** | Uniform Wait Latency Distribution | **C-SCAN** | Increased total cylinders due to boundary jump | Heavy enterprise database servers with uniform random disk I/O |
| **Deadlock** | Strict Deadlock Avoidance | **Banker's Algorithm** | Conservative resource holding; $O(m \times n^2)$ runtime verification | Mission-critical avionics and nuclear control resource managers |

---

## 7. Verification & Reproducibility

All benchmarks and figures can be verified and reproduced deterministically:
1. **Interactive Execution**:
   ```bash
   python main.py
   # Select Menu Option 5: Performance Analysis
   ```
2. **Unit Test Suite Execution**:
   ```bash
   python -m unittest tests/test_reporting.py
   ```
3. **Full System Verification**:
   ```bash
   python -m unittest discover tests
   ```

All generated tabular data is persisted in `results/` and `Phase_3_Analysis/results/`.
All publication-grade visual charts are rendered at 300 DPI in `charts/` and `Phase_3_Analysis/charts/`.
