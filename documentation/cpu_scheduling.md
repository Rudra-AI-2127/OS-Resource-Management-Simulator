# CPU Scheduling Subsystem Documentation

**Module**: `modules/cpu_scheduling.py`  
**Test Suite**: `tests/test_cpu.py`  
**Associated Blueprint Component**: Phase 2 — Module A: CPU Scheduling  
**Author**: Lead Software Architect & Systems Engineer  

---

## 1. Subsystem Overview

The CPU Scheduling module models uniprocessor CPU scheduling policies. In an operating system, the short-term scheduler (or CPU scheduler) selects a process from the ready queue and allocates the CPU core to it.

The simulation accurately tracks:
- Dynamic process arrivals at arbitrary time instances ($AT \ge 0$).
- Deterministic queue ordering and tie-breaking.
- Preemptive time-slicing vs non-preemptive run-to-completion policies.
- Explicit representation of CPU idle periods when no processes have arrived.
- Structured timeline segment generation for ASCII and graphical Gantt charts.

---

## 2. Implemented Algorithms & Mechanics

### 2.1 First-Come, First-Served (FCFS)
- **Policy**: Strictly non-preemptive FIFO dispatching.
- **Queue Logic**: Ready processes are sorted primarily by `Arrival Time` ($AT$) and secondarily by `Process ID` (lexicographical order).
- **Execution**: The process at the head of the queue runs uninterrupted until its burst time is satisfied ($CT = \max(current\_time, AT) + BT$).
- **Characteristics**: Simple to implement, zero scheduling overhead, but vulnerable to the *convoy effect* where short processes wait behind a long, CPU-bound process.

### 2.2 Shortest Job First (SJF — Non-Preemptive)
- **Policy**: Non-preemptive shortest burst time selection.
- **Queue Logic**: At time instant $t$, the scheduler inspects the subset of processes that have arrived ($AT \le t$). From this ready pool, it dispatches the process with $\min(BT)$. Ties are resolved by earliest arrival time ($AT$), followed by lexicographical `PID`.
- **Execution**: Once scheduled, the selected process runs to full completion.
- **Characteristics**: Provably minimizes average waiting time for a static workload. However, long processes may experience *starvation* (indefinite postponement) if shorter tasks arrive continuously.

### 2.3 Round Robin (RR — Preemptive)
- **Policy**: Preemptive time-sliced circular dispatching.
- **Queue Logic**: Uses a FIFO `collections.deque` ready queue. A process executes for at most a configurable time quantum $q \ge 1$ (default $q = 2$).
- **Arrival vs Preemption Tie-Breaking Invariant**:
  When process $P_a$ finishes its time quantum slice at time $t$, and another process $P_b$ arrives fresh at time $t$, $P_b$ is enqueued into the ready queue **before** the preempted process $P_a$ is re-enqueued. This prevents job starvation and enforces fair queue arbitration.
- **Characteristics**: Provides balanced response times ($RT$), ideal for time-sharing interactive systems. If $q \to \infty$, Round Robin degenerates into FCFS; if $q \to 0$, context-switching overhead dominates.

### 2.4 Priority Scheduling (Non-Preemptive)
- **Policy**: Non-preemptive priority queue arbitration.
- **Priority Convention**: **Lower integer value indicates higher priority** (e.g., Priority `1` represents higher priority than Priority `2`), conforming to standard POSIX and Silberschatz conventions.
- **Queue Logic**: From all arrived processes ($AT \le t$), the scheduler selects the process with $\min(Priority)$. Ties are broken by earliest arrival time ($AT$), then lexicographical `PID`.
- **Characteristics**: Critical tasks receive prompt service, but lower-priority processes may suffer from starvation under heavy workloads.

---

## 3. Mathematical Metric Formulations

For every process $P_i$, the following lifecycle metrics are calculated:

$$\text{Turnaround Time } (TAT_i) = CT_i - AT_i$$

$$\text{Waiting Time } (WT_i) = TAT_i - BT_i$$

$$\text{Response Time } (RT_i) = \text{First Start Time}_i - AT_i$$

### Aggregate System Metrics:

$$\overline{WT} = \frac{1}{n} \sum_{i=1}^{n} WT_i, \quad \overline{TAT} = \frac{1}{n} \sum_{i=1}^{n} TAT_i, \quad \overline{RT} = \frac{1}{n} \sum_{i=1}^{n} RT_i$$

$$\text{CPU Utilization } (\%) = \left( \frac{\text{Total Busy Time}}{\text{Total Timeline Duration}} \right) \times 100\%$$

Where:
- $\text{Total Busy Time} = \sum_{seg \in Segments, seg.pid \ne \text{"IDLE"}} seg.duration = \sum_{i=1}^{n} BT_i$
- $\text{Total Timeline Duration} = \max(CT) - \min(AT, 0)$

---

## 4. Algorithmic Complexity Analysis

| Algorithm | Preemptive? | Time Complexity | Space Complexity | Starvation Vulnerability? |
|---|---|---|---|---|
| **FCFS** | No | $\mathcal{O}(n \log n)$ (sorting by arrival) | $\mathcal{O}(n)$ | No |
| **SJF (Non-preemptive)** | No | $\mathcal{O}(n^2)$ (ready queue scans) | $\mathcal{O}(n)$ | Yes (long burst jobs) |
| **Round Robin** | Yes | $\mathcal{O}\left(n \times \frac{\max(BT)}{q}\right)$ | $\mathcal{O}(n)$ | No (fair time-sharing) |
| **Priority (Non-preemptive)** | No | $\mathcal{O}(n^2)$ (ready queue scans) | $\mathcal{O}(n)$ | Yes (low priority jobs) |

---

## 5. Timeline Segment & Gantt Chart Specification

Every scheduling algorithm returns a tuple `(completed_processes: list[Process], segments: list[TimelineSegment])`.

Each `TimelineSegment` object encapsulates:
```python
@dataclass
class TimelineSegment:
    pid: str          # Process ID or "IDLE"
    start_time: int   # Starting time unit (inclusive)
    end_time: int     # Ending time unit (exclusive)

    @property
    def duration(self) -> int:
        return self.end_time - self.start_time
```

### Invariant Rules Enforced:
1. **Contiguity**: $\forall k \in [0, |Segments|-2]: segments[k].end\_time == segments[k+1].start\_time$.
2. **Non-negativity**: $\forall k: segments[k].start\_time \ge 0 \land segments[k].duration > 0$.
3. **Arrival Validity**: If $seg.pid \ne \text{"IDLE"}$, then $seg.start\_time \ge AT(seg.pid)$.
4. **Idle Preservation**: If the ready queue is empty and the next job arrives at $t_{next} > current\_time$, an explicit segment `TimelineSegment(pid="IDLE", start_time=current_time, end_time=t_next)` is generated.
