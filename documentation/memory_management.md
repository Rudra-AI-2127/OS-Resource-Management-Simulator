# Memory Management Subsystem Documentation

**Module**: `modules/memory_management.py`  
**Test Suite**: `tests/test_memory.py`  
**Associated Blueprint Component**: Phase 2 — Module B: Memory Management  
**Author**: Lead Software Architect & Systems Engineer  

---

## 1. Subsystem Overview

The Memory Management subsystem simulates primary storage (RAM) allocation under a **contiguous variable-partition allocation** model. In operating systems, the memory manager is responsible for tracking which parts of memory are currently in use, allocating partitions to arriving processes, splitting free blocks to satisfy requests, and auditing memory fragmentation.

---

## 2. Dynamic Partition Allocation Strategies

The simulator implements the three classic contiguous memory placement policies:

### 2.1 First Fit
- **Algorithm**: Scans the list of available free memory blocks from the beginning (lowest physical address/index order) and allocates the process to the **first block** whose size is greater than or equal to the requested size ($S_{block} \ge S_{req}$).
- **Performance**: Generally the fastest strategy because search terminates immediately upon discovering the first viable block ($\mathcal{O}(1)$ best case, $\mathcal{O}(m)$ worst case where $m$ is the number of free blocks).
- **Trade-off**: Tends to concentrate small leftover fragments near the beginning of memory, requiring subsequent searches to skip past many small unusable blocks.

### 2.2 Best Fit
- **Algorithm**: Scans the entire collection of free blocks and allocates the process to the **smallest suitable block** that can satisfy the request ($\min(S_{block} - S_{req})$ where $S_{block} \ge S_{req}$).
- **Performance**: Requires an exhaustive $\mathcal{O}(m)$ search across all available blocks.
- **Trade-off**: Optimizes immediate memory utilization and preserves large contiguous blocks for future large requests. However, it generates tiny leftover fragments that are often too small to satisfy subsequent processes.

### 2.3 Worst Fit
- **Algorithm**: Scans the entire collection of free blocks and allocates the process to the **largest available block** ($\max(S_{block} - S_{req})$ where $S_{block} \ge S_{req}$).
- **Performance**: Requires an exhaustive $\mathcal{O}(m)$ search across all available blocks.
- **Trade-off**: Designed to leave the largest possible remaining free block after allocation, increasing the likelihood that the remaining partition can accommodate another process. However, it rapidly fragments the largest available blocks in memory.

---

## 3. Dynamic Block Splitting Mechanics

In variable-partition multiprogramming:
1. When a process of size $S_{req}$ is allocated to a free block of size $S_{block}$ where $S_{block} > S_{req}$:
   - The block is partitioned into an allocated segment of exact size $S_{req}$.
   - The remaining portion $S_{rem} = S_{block} - S_{req}$ remains in the free memory pool as an independent free block.
2. When $S_{block} == S_{req}$, the entire block is allocated with zero remaining free space.
3. Memory Conservation Invariant:
   $$\sum \text{Allocated Memory} + \sum \text{Remaining Free Memory} = \text{Total Initial Memory}$$

---

## 4. Internal vs. External Fragmentation Analysis

### 4.1 Internal Fragmentation
- **Definition**: Internal fragmentation occurs when allocated storage exceeds the requested storage, leaving unusable memory *inside* an allocated partition.
- **Dynamic Partitioning Behavior**: In our dynamic partition model with block splitting, the allocated partition size matches the process request **exactly** ($S_{allocated} = S_{req}$). Leftover space is split off and returned to the free block pool. Therefore, **internal fragmentation is strictly 0 KB**.
- **Important Distinction**: Leftover space in a split free block is **not** internal fragmentation; it is active free memory available for subsequent allocations.

### 4.2 External Fragmentation
- **Definition**: External fragmentation occurs when total free memory across all available blocks is large enough to satisfy an incoming process request, but no single contiguous free block is large enough to hold it.
- **Mathematical Criterion**:
  $$\text{External Fragmentation Present} \iff \exists P_{failed} \text{ such that } \sum_{b \in Free} S_b \ge S_{req}(P_{failed}) \land \forall b \in Free: S_b < S_{req}(P_{failed})$$

### 4.3 Limitations of Scalar Free-Block Measurement
Measuring external fragmentation purely from a list of free block sizes (without a spatial physical address layout) has specific theoretical and practical limitations:
1. **Lack of Address Adjacency**: A simple list of block sizes does not track physical memory coordinates. Two free blocks might be physically adjacent in memory, meaning that in a real OS with coalescing (merging), they could combine into a single large block capable of servicing the request.
2. **Total Free Memory Fallacy**: Total free memory alone cannot determine whether an allocation will succeed. 1,000 KB of free memory divided into ten 100 KB non-contiguous fragments cannot satisfy a single 200 KB request without compaction.
3. **Absence of Relocation / Compaction**: Without hardware support (such as base and limit registers or MMU paging), external fragmentation can only be resolved by memory compaction, which incurs significant CPU copying overhead.

---

## 5. Empirical Comparison on Blueprint Baseline Workload

**Initial Blocks**: `[100, 500, 200, 300, 600] KB` (Total = 1700 KB)  
**Process Requests**: `P1(212 KB), P2(417 KB), P3(112 KB), P4(426 KB)` (Total Requested = 1167 KB)

### Comparison Summary:
| Algorithm | Allocations Succeeded | Succeeded / Total | Memory Allocated | Free Memory | Memory Utilization | External Fragmentation |
|---|---|---|---|---|---|---|
| **First Fit** | P1, P2, P3 (P4 Fails) | 3 / 4 (75.0%) | 741 KB | 959 KB | 43.59% | 959 KB |
| **Best Fit** | P1, P2, P3, P4 (All Fit!) | 4 / 4 (100.0%) | 1167 KB | 533 KB | 68.65% | 0 KB |
| **Worst Fit** | P1, P2, P3 (P4 Fails) | 3 / 4 (75.0%) | 741 KB | 959 KB | 43.59% | 959 KB |

### Analytical Insights:
- **Best Fit achieves 100% allocation success** because it preserves the 600 KB block for the large 426 KB request (P4) by routing P1 (212 KB) to Block 4 (300 KB) and P2 (417 KB) to Block 2 (500 KB).
- **First Fit and Worst Fit fail to allocate P4** because they consume the large 600 KB block early (Worst Fit allocates P1 to 600 KB, while First Fit allocates P2 to 600 KB), leaving only fragments $< 426$ KB.
- Both First Fit and Worst Fit suffer from 959 KB of external fragmentation because total free space (959 KB) is more than double P4's requirement (426 KB), yet P4 cannot be allocated.

---

## 6. Algorithmic Complexity

| Algorithm | Search Pattern | Time Complexity | Space Complexity |
|---|---|---|---|
| **First Fit** | First $S_{block} \ge S_{req}$ | Best $\mathcal{O}(1)$, Worst $\mathcal{O}(m)$ | $\mathcal{O}(m)$ |
| **Best Fit** | $\min(S_{block} - S_{req})$ | Exhaustive $\mathcal{O}(m)$ | $\mathcal{O}(m)$ |
| **Worst Fit** | $\max(S_{block} - S_{req})$ | Exhaustive $\mathcal{O}(m)$ | $\mathcal{O}(m)$ |

Where $m$ is the count of available free memory blocks.
