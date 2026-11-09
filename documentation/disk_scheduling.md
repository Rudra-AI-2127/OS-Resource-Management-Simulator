# Module 4 — Disk Scheduling

**Subsystem**: Secondary Storage I/O Optimization  
**Implementation**: [`modules/disk_scheduling.py`](file:///C:/Users/rpsra/Downloads/Operating-Systems-Lab/modules/disk_scheduling.py)  
**Test Suite**: [`tests/test_disk.py`](file:///C:/Users/rpsra/Downloads/Operating-Systems-Lab/tests/test_disk.py) (17 unit tests)  
**Interactive Entry Point**: Option 4 in [`main.py`](file:///C:/Users/rpsra/Downloads/Operating-Systems-Lab/main.py)  

---

## 1. Executive Summary & Physical Disk Modeling

In an operating system storage subsystem, magnetic hard disk drives (HDDs) and non-uniform storage media represent mechanical or localized physical bottlenecks. When multiple concurrent processes issue block read/write system calls, the operating system kernel maintains a queue of pending cylinder I/O requests.

Disk access latency is governed by three physical components:
$$\text{Total Access Time} = T_{seek} + T_{rotational} + T_{transfer}$$

1. **Seek Time ($T_{seek}$)**: The mechanical duration required for the actuator arm to accelerate, translate the read/write head radially across platters, and settle onto the target cylinder. This is mechanically the slowest phase ($\sim 3\text{ ms} - 15\text{ ms}$).
2. **Rotational Latency ($T_{rotational}$)**: The time required for the target sector on the spinning platter to rotate under the head ($\sim 2\text{ ms} - 4\text{ ms}$ at 7,200–15,000 RPM).
3. **Transfer Time ($T_{transfer}$)**: The electronic rate at which data bits flow from the magnetic surface into the disk controller buffer ($\sim \text{microseconds}$).

Because **seek time dominates total disk access time by an order of magnitude**, disk scheduling algorithms aim to minimize total head travel (measured in cylinders traversed) and ensure fair, predictable response times for competing I/O streams.

---

## 2. Supported Disk Scheduling Algorithms

### 2.1 First-Come, First-Served (FCFS)
- **Principle**: Dispatches requests in the strict chronological order of their arrival in the I/O queue.
- **Advantages**:
  - Completely fair; every request is serviced in deterministic $\mathcal{O}(1)$ FIFO queue order.
  - Zero possibility of starvation.
- **Disadvantages**:
  - Suffers from extreme seek oscillations (the "wild swing" effect). The disk head repeatedly crosses the entire platter surface back and forth, resulting in maximal total head travel and poor I/O throughput.

---

### 2.2 Shortest Seek Time First (SSTF)
- **Principle**: Greedily selects the pending cylinder request that is closest to the current position of the disk head:
  $$\min_{r \in \text{Pending}} |r - \text{CurrentHead}|$$
- **Tie-Breaking Convention**: If two pending requests are equidistant from the current head ($|r_a - \text{Head}| = |r_b - \text{Head}|$), ties are broken deterministically by selecting the **lower cylinder number** ($\min(r_a, r_b)$).
- **Advantages**:
  - Dramatically reduces total head movement compared to FCFS, typically achieving near-optimal seek distances on stationary workloads.
- **Disadvantages**:
  - **Starvation Risk**: If incoming I/O requests consistently cluster around the current head position, distant requests located near the inner or outer platter edges may be indefinitely starved.
  - High variance in response time.

---

### 2.3 SCAN (The Elevator Algorithm)
- **Principle**: The disk arm behaves like a building elevator. Starting from the initial head position, it sweeps continuously in the configured direction (e.g., upward towards the maximum cylinder boundary $\text{MaxCylinder} - 1$). It services all requests encountered along its path until it touches the disk boundary, then reverses direction and sweeps toward the opposite boundary, servicing remaining requests.
- **Boundary Behavior**:
  - If moving **UP** / **RIGHT** and requests remain on the left, the head traverses all the way to cylinder $\text{MaxCylinder} - 1$ before reversing downward.
  - If moving **DOWN** / **LEFT** and requests remain on the right, the head traverses down to cylinder $0$ before reversing upward.
  - If all requests lie strictly ahead in the current direction of motion, the head terminates upon servicing the final request without unnecessary boundary travel.
- **Advantages**:
  - Eliminates starvation entirely.
  - Significantly lower variance in waiting time compared to SSTF.
- **Distinction from LOOK**: In SCAN, the head visits the physical boundary cylinder ($0$ or $199$) upon reversing, whereas the LOOK algorithm reverses immediately after servicing the final request in that direction.

---

### 2.4 Circular SCAN (C-SCAN)
- **Principle**: Designed to provide uniform waiting times across all cylinders. In standard SCAN, cylinders near the center of the disk are swept twice as frequently as cylinders near the outer boundaries. C-SCAN eliminates this bias by treating the cylinders as a circular list.
- **Sweep and Return Mechanism**:
  - The head sweeps in the initial direction, servicing requests until reaching the boundary cylinder.
  - Upon reaching the boundary, the head performs a rapid, non-servicing return seek directly to the opposite disk boundary (e.g., from $199$ jumping directly to $0$).
  - Servicing resumes in the original sweep direction.
- **Accounting Convention**:
  - In this simulator, the rapid circular return jump ($|\text{Boundary}_{max} - \text{Boundary}_{min}|$, e.g. $|199 - 0| = 199$) is **explicitly included in the total head movement calculation**. This reflects the true mechanical actuator workload and energy expenditure incurred by the drive arm.
- **Advantages**:
  - Provides the most uniform waiting time distribution of all elevator-based algorithms.
  - Outer cylinder requests experience the same average delay as inner cylinder requests.

---

## 3. Mathematical Accounting Conventions & Formulae

Let $\mathbf{S} = \langle c_0, c_1, c_2, \dots, c_k \rangle$ denote the complete ordered trajectory of head positions, where $c_0 = \text{InitialHead}$, and subsequent elements represent serviced requests and physical boundary turnarounds.

### 3.1 Step-by-Step Seek Delta
For each transition from position $c_{i-1}$ to $c_i$:
$$\Delta_i = |c_i - c_{i-1}|, \quad \forall i \in \{1, 2, \dots, k\}$$

### 3.2 Total Head Movement (THM)
The cumulative distance traversed by the disk head across all seeks:
$$\text{THM} = \sum_{i=1}^{k} \Delta_i = \sum_{i=1}^{k} |c_i - c_{i-1}|$$

### 3.3 Average Head Movement per Request (AHM)
Let $N_{requests}$ denote the number of unique I/O requests fulfilled (excluding boundary turnarounds and starting positions):
$$\text{AHM} = \frac{\text{THM}}{N_{requests}}$$

### 3.4 Trajectory vs. Service Sequence Separation
To ensure clean visualization and unambiguous reporting, the engine cleanly separates:
1. `seek_sequence`: Complete physical path of the head, including initial position and boundary turnarounds (used for Matplotlib plotting and step delta calculations).
2. `service_sequence`: Ordered sequence of actual user process requests serviced.

---

## 4. Canonical Blueprint Numerical Walkthrough

### Workload Parameters
- **Pending Cylinder Requests**: $[98, 183, 37, 122, 14, 124, 65, 67]$ ($N = 8$)
- **Initial Head Position**: $53$
- **Total Cylinders**: $200$ (Cylinders $0$ to $199$)
- **Initial Direction**: `up` (towards cylinder $199$)

---

### 4.1 FCFS Execution
- **Seek Path**: $53 \to 98 \to 183 \to 37 \to 122 \to 14 \to 124 \to 65 \to 67$
- **Step Movements**:
  - $|98 - 53| = 45$
  - $|183 - 98| = 85$
  - $|37 - 183| = 146$
  - $|122 - 37| = 85$
  - $|14 - 122| = 108$
  - $|124 - 14| = 110$
  - $|65 - 124| = 59$
  - $|67 - 65| = 2$
- **Total Head Movement**: $45 + 85 + 146 + 85 + 108 + 110 + 59 + 2 = \mathbf{640\text{ cylinders}}$
- **Average Seek**: $640 / 8 = \mathbf{80.00\text{ cyl/req}}$

---

### 4.2 SSTF Execution
- **Seek Path**: $53 \to 65 \to 67 \to 37 \to 14 \to 98 \to 122 \to 124 \to 183$
- **Step Movements**:
  - $|65 - 53| = 12$
  - $|67 - 65| = 2$
  - $|37 - 67| = 30$
  - $|14 - 37| = 23$
  - $|98 - 14| = 84$
  - $|122 - 98| = 24$
  - $|124 - 122| = 2$
  - $|183 - 124| = 59$
- **Total Head Movement**: $12 + 2 + 30 + 23 + 84 + 24 + 2 + 59 = \mathbf{236\text{ cylinders}}$
- **Average Seek**: $236 / 8 = \mathbf{29.50\text{ cyl/req}}$

---

### 4.3 SCAN Execution (Direction: `up`)
- **Seek Path**: $53 \to 65 \to 67 \to 98 \to 122 \to 124 \to 183 \to \mathbf{199} \to 37 \to 14$
- **Step Movements**:
  - Sweeping Upward: $|65-53| + |67-65| + |98-67| + |122-98| + |124-122| + |183-124| + |199-183| = 199 - 53 = 146$
  - Reversing Downward: $|37 - 199| + |14 - 37| = 199 - 14 = 185$
- **Total Head Movement**: $146 + 185 = \mathbf{331\text{ cylinders}}$
- **Average Seek**: $331 / 8 = \mathbf{41.38\text{ cyl/req}}$

---

### 4.4 C-SCAN Execution (Direction: `up`)
- **Seek Path**: $53 \to 65 \to 67 \to 98 \to 122 \to 124 \to 183 \to \mathbf{199} \to \mathbf{0} \to 14 \to 37$
- **Step Movements**:
  - Upward Sweep to Boundary: $199 - 53 = 146$
  - Rapid Return Jump: $|0 - 199| = 199$
  - Upward Sweep from 0: $37 - 0 = 37$
- **Total Head Movement**: $146 + 199 + 37 = \mathbf{382\text{ cylinders}}$
- **Average Seek**: $382 / 8 = \mathbf{47.75\text{ cyl/req}}$

---

### 4.5 Comparative Summary

```text
=== DISK SCHEDULING COMPARISON SUMMARY ===
+-----------+----------------------+-----------------------+-------------------+
| Algorithm | Total Head Movement  | Average Seek Distance | Requests Serviced |
+-----------+----------------------+-----------------------+-------------------+
| FCFS      | 640 cylinders        | 80.00 cyl/req         | 8                 |
| SSTF      | 236 cylinders        | 29.50 cyl/req         | 8                 |
| SCAN      | 331 cylinders        | 41.38 cyl/req         | 8                 |
| C-SCAN    | 382 cylinders        | 47.75 cyl/req         | 8                 |
+-----------+----------------------+-----------------------+-------------------+

Optimal Algorithm for Minimum Head Movement: SSTF (236 cylinders)
```

---

## 5. Edge Cases & Boundary Handling

| Edge Case | Description | Expected Behavior |
|:---|:---|:---|
| **Empty Request Queue** | `requests = []` | Raises `ValueError("Disk cylinder request queue cannot be empty.")` |
| **Out-of-Bounds Cylinder** | $r < 0$ or $r \ge \text{TotalCylinders}$ | Raises `ValueError` with coordinate details |
| **Initial Head at Request** | Head is at cylinder $53$, request includes $53$ | First seek step is $\Delta = 0$; request is marked serviced immediately |
| **Requests on One Side Only** | All requests are $> \text{Head}$ and direction is `up` | SCAN sweeps through requests and terminates without touching boundary |
| **Boundary Turnarounds** | Cylinder $0$ or $199$ is among the requests | Visited as a normal request; boundary cylinder is not duplicated in seek path |
| **SSTF Distance Ties** | Head at $50$, requests at $40$ and $60$ (both distance $10$) | Breaks tie by selecting lower cylinder ($40$) |
| **Duplicate Requests** | Multiple requests for cylinder $40$ | Both requests are serviced in succession ($\Delta = 0$) and counted in total requests |

---

## 6. Faculty Viva Defense Guide

> **Q1: Why is SSTF not used as the standard scheduling algorithm in enterprise operating systems despite producing the lowest head movement on many workloads?**  
> **A**: SSTF is prone to **starvation**. If new requests continually arrive close to the current head position, requests far from the head will never be serviced. In a heavily loaded system, outer-track requests can experience infinite delay. SCAN and C-SCAN eliminate this risk by enforcing monotonic sweeps across the platter.

> **Q2: What is the primary operational advantage of C-SCAN over standard SCAN?**  
> **A**: In standard SCAN, cylinders near the middle of the disk are serviced twice per full cycle (once on the forward pass and once on the return pass), whereas cylinders near the outer boundaries are serviced only once per cycle. C-SCAN eliminates this non-uniformity by always sweeping in one direction and jumping back to the start, providing a uniform waiting time distribution for all cylinders.

> **Q3: Why is the return jump from cylinder 199 to 0 in C-SCAN counted toward total head movement?**  
> **A**: The return seek is a real mechanical movement executed by the voice-coil actuator arm. Even though no user data is read or written during the return jump, the arm physically traverses 199 cylinders, consuming mechanical time and power. Accurately modeling physical actuator work requires including this seek distance.

> **Q4: How does LOOK differ from SCAN, and how does C-LOOK differ from C-SCAN?**  
> **A**: In SCAN, the head travels all the way to the end of the disk (cylinder $0$ or $199$) before reversing, even if no pending requests exist at the boundary. In LOOK, the head "looks" ahead and reverses immediately upon servicing the final request in the current direction, avoiding unnecessary seeks to the physical boundary. C-LOOK applies the same optimization to C-SCAN.

> **Q5: In modern Solid State Drives (SSDs), does disk scheduling (like SCAN or SSTF) still provide a performance benefit?**  
> **A**: No. SSDs have no moving mechanical parts, actuator arms, or spinning platters. Flash memory access is electronic and nearly uniform across all block addresses ($T_{seek} \approx 0$). In SSDs, I/O scheduling algorithms focus instead on wear leveling, write amplification reduction, and parallelism across flash memory channels (e.g., NVMe multi-queue dispatching).

> **Q6: How does SSTF break ties when two requests are equidistant from the head?**  
> **A**: In this simulator, SSTF breaks ties deterministically by selecting the request with the lower cylinder number ($\min(r_a, r_b)$). This ensures reproducible, testable behavior across all execution environments.
