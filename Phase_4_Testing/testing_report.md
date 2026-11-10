# Phase 4 — Comprehensive Testing & Reliability Audit Report

## Executive Summary

This report documents the exhaustive testing and reliability audit conducted for **Phase 4** of the **Operating Systems Resource Management Simulator**. 

A complete audit of all core algorithms, defensive validators, tabular exporters, plotting subsystems, and user interface workflows was performed. Across both the formal Python `unittest` suite (115 tests) and the expanded test case matrix (77 distinct test cases spanning TC01–TC77), the system achieved a **100.0% pass rate with zero failures and zero unhandled regressions**.

| Verification Dimension | Total Executed | Passed | Failed | Errors | Pass Rate |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Python `unittest` Discovery Suite** | 115 | 115 | 0 | 0 | **100.0%** |
| **Expanded Test Case Matrix (TC01–TC77)** | 77 | 77 | 0 | 0 | **100.0%** |
| **End-to-End Application Integration Flows** | 9 | 9 | 0 | 0 | **100.0%** |
| **Visual Chart & CSV Generation Checks** | 8 | 8 | 0 | 0 | **100.0%** |

---

## 1. Algorithmic Verification Coverage

Every algorithm specified across the four core operating system domains and reporting was individually verified against theoretical benchmarks and edge conditions:

### 1.1 CPU Scheduling Subsystem (`modules/cpu_scheduling.py`)
- **First-Come First-Served (FCFS)**:
  - Verified non-preemptive FIFO dispatching based strictly on arrival time.
  - Verified timeline continuity (no gaps except during explicitly logged IDLE segments).
  - Verified benchmark calculations: on blueprint workload ($P_1(0,5), P_2(1,3), P_3(2,8), P_4(3,2)$), matches exact analytical completion times ($CT = [5, 8, 16, 18]$), $\overline{WT} = 5.75$, $\overline{TAT} = 10.25$, CPU Utilization = 100.0%.
- **Shortest Job First (SJF Non-preemptive)**:
  - Verified greedy selection of minimum burst time among ready processes.
  - Verified FIFO tie-breaking when burst times are equal ($P_1(4), P_2(4), P_3(4) \to P_1 \to P_2 \to P_3$).
  - Verified that when burst times and arrival times are identical, SJF correctly degenerates into FCFS.
- **Round Robin (Preemptive)**:
  - Verified preemptive time slicing and ready queue re-insertion semantics.
  - Verified fine-grained time slicing ($q=1$) producing alternating process execution without state loss.
  - Verified asymptotic degeneration into FCFS when quantum $q \ge \max(BT_i)$.
  - Verified accurate response time tracking ($RT = \text{First Dispatch} - AT$).
- **Priority Scheduling (Non-preemptive)**:
  - Verified lower integer representing higher architectural priority ($0 > 1 > 2 \dots$).
  - Verified tie-breaking by arrival time, then by PID.

### 1.2 Memory Management Subsystem (`modules/memory_management.py`)
- **First Fit**:
  - Verified linear scanning from block index 0, allocating into the first block of size $\ge$ requested size.
  - Verified dynamic partition splitting: unallocated remainder is preserved in the free pool with 0 KB internal fragmentation.
- **Best Fit**:
  - Verified exhaustive search for the smallest block with size $\ge$ requested size.
  - Verified on blueprint workload that Best Fit achieves 100% allocation (1167 KB allocated), while First Fit and Worst Fit experience external fragmentation.
- **Worst Fit**:
  - Verified allocation into the largest available block.
  - Verified accurate external fragmentation detection when total free memory exceeds request size but no individual contiguous partition satisfies it.

### 1.3 Deadlock Management Subsystem (`modules/deadlock.py`)
- **Dijkstra's Banker's Algorithm**:
  - Verified Need Matrix derivation: $Need[i][j] = MaxDemand[i][j] - Allocation[i][j]$.
  - Verified Work and Finish vector safety invariant: each process dispatched satisfies $Need[i] \le Work$ and releases $Allocation[i]$ back to $Work$.
  - Verified canonical 5-process 3-resource safe state detection (Safe sequence: $P_1 \to P_3 \to P_0 \to P_2 \to P_4$).
  - Verified unsafe state detection and immediate rejection with empty sequence.
- **Dynamic Resource Request Safety & Rollback**:
  - Verified Condition 1 ($Request \le Need$) claim validation.
  - Verified Condition 2 ($Request \le Available$) capacity validation.
  - Verified **speculative tentative state validation**: safe requests (e.g. $P_1$ requests $[1, 0, 2]$) are committed; unsafe requests (e.g. $P_4$ requests $[3, 3, 0]$ inducing $[0, 0, 2]$ availability) are denied and **safely rolled back with zero state corruption**.

### 1.4 Disk Scheduling Subsystem (`modules/disk_scheduling.py`)
- **First-Come First-Served (FCFS)**:
  - Verified strict arrival-order seek traversal. Verified blueprint benchmark seek movement = 640 cylinders.
- **Shortest Seek Time First (SSTF)**:
  - Verified greedy nearest neighbor cylinder selection. Verified blueprint benchmark seek movement = 236 cylinders ($63.1\%$ seek reduction).
- **SCAN (Elevator Algorithm)**:
  - Verified directional sweep to boundary (cylinder 199 or 0) before reversing direction, preventing starvation. Verified blueprint seek movement = 331 cylinders.
- **Circular SCAN (C-SCAN)**:
  - Verified unidirectional sweep to outer boundary followed by rapid boundary jump to cylinder 0 without servicing on return. Verified blueprint seek movement = 382 cylinders.

### 1.5 Reporting & Comparative Analytics (`modules/reporting.py`)
- **Mathematical Metric Verification**: Verified formulas for $WT, TAT, RT$, CPU utilization, allocation success rate, external fragmentation, total head movement, and average seek distance.
- **CSV Data Integrity**: Verified that exported CSV files (`cpu_results.csv`, `memory_results.csv`, `deadlock_results.csv`, `disk_results.csv`, and multi-workload comparison CSVs) are non-empty, correctly structured with headers, and contain valid numerical entries.
- **Publication Visualizations**: Verified generation of all 4 charts at 300 DPI (`cpu_comparison.png`, `memory_comparison.png`, `disk_comparison.png`, `overall_analysis.png`), ensuring file sizes $>1000$ bytes and valid PNG headers.
- **Empty Dataset Robustness**: Verified defensive `ValueError` raising and logging when empty process lists, empty memory blocks/requests, or empty cylinder request streams are passed.

---

## 2. Complete Test Matrix & Execution Evidence (TC01 – TC77)

Every test case was executed in Python, and actual outputs were captured without fabrication:

| Test ID | Category | Description | Input Specification | Expected Result | Actual Result | Status |
| :---: | :--- | :--- | :--- | :--- | :--- | :---: |
| **TC01** | CPU Scheduling | Normal CPU input validation | $P_1(0,5), P_2(1,3), P_3(2,8), P_4(3,2)$ | $P_1 CT=5, \overline{WT}=5.75, \overline{TAT}=10.25$ | $P_1 CT=5, \overline{WT}=5.75, \overline{TAT}=10.25$ | **PASS** |
| **TC02** | Validation | Negative burst time rejection | $BT = -5$ | Raise `ValueError` | `ValueError: Burst time must be positive` | **PASS** |
| **TC03** | Validation | Empty process list validation | `[]` | Raise `ValueError` | `ValueError: Process list cannot be empty` | **PASS** |
| **TC04** | Memory Mgmt | Valid memory allocation (Best Fit) | Blocks: $[100,500,200,300,600]$, Reqs: $[212,417,112,426]$ | 100% allocation (4/4, 1167 KB) | Successful=4/4, Allocated=1167 KB | **PASS** |
| **TC05** | Memory Mgmt | Insufficient memory rejection | Blocks: $[100, 200]$, Req: $[P_1: 500]$ | Allocation fails gracefully; 0 successful | Failed=1, FreeMem=300KB, ExtFrag=300KB | **PASS** |
| **TC06** | Deadlock Mgmt | Safe resource allocation (Banker's) | Canonical Silberschatz 5-process state | System SAFE, Sequence starts with $P_1$ | is_safe=True, sequence=$P_1 \to P_3 \to P_0 \to P_2 \to P_4$ | **PASS** |
| **TC07** | Deadlock Mgmt | Unsafe resource state detection | 2 procs, Alloc=$[2],[2]$, Max=$[4],[4]$, Avail=$[0]$ | System UNSAFE, empty sequence | is_safe=False, sequence=[] | **PASS** |
| **TC08** | Disk Scheduling | Valid disk requests (SSTF) | Reqs: $[98, 183, 37, 122, 14, 124, 65, 67]$, Head: 53 | Total head movement = 236 cylinders | HeadMovement=236 cyl, Serviced=8 | **PASS** |
| **TC09** | Validation | Invalid menu option rejection | `choice = '99'` (range 1-6) | Raise `ValueError` | `ValueError: Invalid option 99` | **PASS** |
| **TC10** | Invalid Types | Process arrival time non-numeric string | `arrival_time = 'abc'` | Raise `ValueError` | `ValueError: Arrival time must be an integer` | **PASS** |
| **TC11** | Invalid Types | Process burst time boolean type | `burst_time = True` | Raise `ValueError` | `ValueError: Burst time cannot be a boolean` | **PASS** |
| **TC12** | Invalid Types | Memory block size non-integer string | `blocks = ['one_hundred']` | Raise `ValueError` | `ValueError: Block size must be integer` | **PASS** |
| **TC13** | Invalid Types | Disk cylinder non-integer float | `cylinders = [45.7]` | Raise `ValueError` | `ValueError: Cylinder must be integer, not float` | **PASS** |
| **TC14** | Invalid Types | Time quantum string | `quantum = 'fast'` | Raise `ValueError` | `ValueError: Quantum must be integer` | **PASS** |
| **TC15** | Invalid Types | Deadlock matrix string element | $Allocation[0][0] = \text{'A'}$ | Raise `ValueError` | `ValueError: Allocation must be integer` | **PASS** |
| **TC16** | Missing Fields | Process missing burst time field | `{'pid': 'P1', 'arrival_time': 0}` | Raise `ValueError` | `ValueError: Missing required burst time` | **PASS** |
| **TC17** | Missing Fields | Process missing PID identifier | `{'arrival_time': 0, 'burst_time': 5}` | Raise `ValueError` | `ValueError: Missing required 'pid' field` | **PASS** |
| **TC18** | Missing Fields | Memory request missing size | `[('P1',)]` | Raise `ValueError` | `ValueError: Invalid memory request format` | **PASS** |
| **TC19** | Missing Fields | Deadlock empty available vector | `available = []` | Raise `ValueError` | `ValueError: Available cannot be empty` | **PASS** |
| **TC20** | Missing Fields | Deadlock empty process IDs | `process_ids = []` | Raise `ValueError` | `ValueError: Process IDs cannot be empty` | **PASS** |
| **TC21** | Duplicates | Duplicate process IDs in CPU input | `P1, P1` | Raise `ValueError` | `ValueError: Duplicate Process ID detected: 'P1'` | **PASS** |
| **TC22** | Duplicates | Duplicate process IDs in Memory input | `P1, P1` | Raise `ValueError` | `ValueError: Duplicate process request ID: 'P1'` | **PASS** |
| **TC23** | Duplicates | Duplicate process IDs in Deadlock matrix | `P0, P0` | Raise `ValueError` | `ValueError: Duplicate process IDs detected` | **PASS** |
| **TC24** | Duplicates | Duplicate disk cylinder requests | `[50, 50, 80]`, Head: 50 | Serviced cleanly with 0 seek for duplicate | HeadMovement=30 cyl, Serviced=3 | **PASS** |
| **TC25** | Boundary Values | Single CPU process execution | $N=1, BT=7$ | $WT=0, TAT=7$ | $WT=0.0, TAT=7.0$ | **PASS** |
| **TC26** | Boundary Values | Simultaneous arrival at $AT=0$ (SJF) | $P_1(0,4), P_2(0,2), P_3(0,6)$ | Dispatch order: $P_2 \to P_1 \to P_3$ | Order: $P_2 \to P_1 \to P_3$ | **PASS** |
| **TC27** | Boundary Values | Equal burst times in SJF | $P_1(4), P_2(4), P_3(4)$ | FIFO tie-break order: $P_1 \to P_2 \to P_3$ | Tie break order: $P_1 \to P_2 \to P_3$ | **PASS** |
| **TC28** | Boundary Values | CPU idle gap between process arrivals | $P_1(0,2), P_2(5,3)$ | IDLE segment from $t=2$ to $t=5$ | Idle segment: start=2, end=5 | **PASS** |
| **TC29** | Boundary Values | Round Robin fine quantum $q=1$ | $P_1(2), P_2(2), q=1$ | Interleaved: $P_1 \to P_2 \to P_1 \to P_2$ | Timeline: $P_1 \to P_2 \to P_1 \to P_2$ | **PASS** |
| **TC30** | Boundary Values | Round Robin quantum larger than burst | $P_1(0,3), P_2(1,2), q=10$ | Matches FCFS completions ($CT=3, 5$) | $P_1 CT=3, P_2 CT=5$ | **PASS** |
| **TC31** | Boundary Values | Exact memory block fit | Block: 250, Req: 250 | Allocated=250KB, FreeRemaining=0KB | Allocated=250KB, FreeRemaining=0KB | **PASS** |
| **TC32** | Boundary Values | Dynamic memory partition splitting | Block: 500, Req: 150 | Allocated=150KB, Remainder 350KB returned | Allocated=150KB, FreePool=350KB | **PASS** |
| **TC33** | Boundary Values | Initial disk head at cylinder 0 | Head: 0, Reqs: $[10, 50, 100]$ | Sequence starts at 0, movement=100 cyl | SeekSeq=[0,10,50,100], TotalSeek=100 | **PASS** |
| **TC34** | Boundary Values | Initial disk head at cylinder 199 | Head: 199, Reqs: $[150, 100, 50]$ | Sequence starts at 199, movement=149 cyl | SeekSeq=[199,150,100,50], TotalSeek=149 | **PASS** |
| **TC35** | Boundary Values | Disk request at current head position | Head: 53, Reqs: $[53, 100]$ | Immediate service with 0 seek jump | SeekSeq=[53, 53, 100], TotalSeek=47 | **PASS** |
| **TC36** | Boundary Values | Disk SCAN downward elevator sweep | Head: 50, Reqs: $[20, 80, 150]$, dir=down | Visits 20, 0, then 80, 150 | SeekSeq=50 -> 20 -> 0 -> 80 -> 150 | **PASS** |
| **TC37** | Boundary Values | Disk C-SCAN circular wraparound | Head: 100, Reqs: $[10, 180]$, dir=up | Wraparound: $100 \to 180 \to 199 \to 0 \to 10$ | SeekSeq=100 -> 180 -> 199 -> 0 -> 10 | **PASS** |
| **TC38** | Invalid Matrices | Deadlock row count mismatch | Max: 1 row, Alloc: 2 rows | Raise `ValueError` | `ValueError: Dimension mismatch` | **PASS** |
| **TC39** | Invalid Matrices | Deadlock column count mismatch | Max: 3 cols, Alloc: 2 cols | Raise `ValueError` | `ValueError: Column mismatch` | **PASS** |
| **TC40** | Invalid Matrices | Allocation exceeds Max Demand | Alloc: $[3, 2]$, Max: $[2, 2]$ | Raise `ValueError` | `ValueError: Allocation exceeds Max Demand` | **PASS** |
| **TC41** | Invalid Matrices | Available length mismatch | Available length: 1, Resources: 2 | Raise `ValueError` | `ValueError: Available count mismatch` | **PASS** |
| **TC42** | Invalid Matrices | Empty deadlock matrices | `max=[], alloc=[]` | Raise `ValueError` | `ValueError: Matrices cannot be empty` | **PASS** |
| **TC43** | Invalid Matrices | Negative allocation count | $Allocation[0][0] = -1$ | Raise `ValueError` | `ValueError: Must be non-negative` | **PASS** |
| **TC44** | Invalid Matrices | Negative available resource count | $available[0] = -3$ | Raise `ValueError` | `ValueError: Must be non-negative` | **PASS** |
| **TC45** | Invalid Params | Round Robin time quantum $q=0$ | `quantum = 0` | Raise `ValueError` | `ValueError: Quantum must be positive` | **PASS** |
| **TC46** | Invalid Params | Round Robin negative quantum | `quantum = -3` | Raise `ValueError` | `ValueError: Quantum must be positive` | **PASS** |
| **TC47** | Invalid Params | Negative disk cylinder request | `cylinder = -10` | Raise `ValueError` | `ValueError: Cylinder must be non-negative` | **PASS** |
| **TC48** | Invalid Params | Cylinder exceeding total capacity | `cylinder = 250, total = 200` | Raise `ValueError` | `ValueError: Cylinder 250 out of bounds` | **PASS** |
| **TC49** | Invalid Params | Initial head position out of bounds | `head = 250, total = 200` | Raise `ValueError` | `ValueError: Head 250 out of bounds` | **PASS** |
| **TC50** | Invalid Params | Total cylinders zero | `total_cylinders = 0` | Raise `ValueError` | `ValueError: Total Cylinders must be positive` | **PASS** |
| **TC51** | Invalid Params | Invalid disk sweep direction string | `direction = 'diagonal'` | Raise `ValueError` | `ValueError: Invalid direction 'diagonal'` | **PASS** |
| **TC52** | Deadlock Safety | Safe dynamic resource request granted | $P_1$ requests $[1, 0, 2]$ | Granted=True, State safely committed | Granted=True, UpdatedAvail=[2,3,0] | **PASS** |
| **TC53** | Deadlock Safety | Request exceeding declared claim | $P_1$ requests $[5, 5, 5]$ ($Need=[1, 2, 2]$) | Granted=False, claim violation error | Granted=False, exceeded claim | **PASS** |
| **TC54** | Deadlock Safety | Request exceeding available capacity | $P_0$ requests $[0, 4, 0]$ ($Avail=[3, 3, 2]$) | Granted=False, Process must wait | Granted=False, must wait | **PASS** |
| **TC55** | Deadlock Safety | Unsafe request denied & rolled back | $P_4$ requests $[3, 3, 0]$ (Induces unsafe state) | Granted=False, 0 state corruption | Granted=False, AvailRestored=True | **PASS** |
| **TC56** | Deadlock Safety | Multiple possible safe sequences | Symmetric capacity ($Avail=[2], Needs=[1],[1]$) | System SAFE, valid sequence found | is_safe=True, sequence=$P_0 \to P_1$ | **PASS** |
| **TC57** | Reporting & IO | CPU benchmark execution | Standard CPU workload | 4 algorithms benchmarked with metrics | AlgosBenchmarked=4, MinWT=4.00 | **PASS** |
| **TC58** | Reporting & IO | CPU results CSV export integrity | `cpu_results.csv` in `results/` | File exists and non-empty | FileExists=True, SizeBytes=241 | **PASS** |
| **TC59** | Reporting & IO | CPU comparison chart 300 DPI generation | `cpu_comparison.png` in `charts/` | PNG file exists and $>1$ KB | ChartExists=True, SizeBytes=101475 | **PASS** |
| **TC60** | Reporting & IO | Memory benchmark execution | Standard Memory workload | 3 algorithms benchmarked with success rates | AlgosBenchmarked=3, BestAlgoSuccess=100.0% | **PASS** |
| **TC61** | Reporting & IO | Memory results CSV export integrity | `memory_results.csv` in `results/` | File exists and non-empty | FileExists=True, SizeBytes=290 | **PASS** |
| **TC62** | Reporting & IO | Memory comparison chart generation | `memory_comparison.png` in `charts/` | PNG file exists and $>1$ KB | ChartExists=True, SizeBytes=199439 | **PASS** |
| **TC63** | Reporting & IO | Disk benchmark execution | Standard Disk workload | 4 algorithms benchmarked with seek sums | AlgosBenchmarked=4, MinSeek=236 cyl | **PASS** |
| **TC64** | Reporting & IO | Disk results CSV export integrity | `disk_results.csv` in `results/` | File exists and non-empty | FileExists=True, SizeBytes=165 | **PASS** |
| **TC65** | Reporting & IO | Disk comparison chart generation | `disk_comparison.png` in `charts/` | PNG file exists and $>1$ KB | ChartExists=True, SizeBytes=102398 | **PASS** |
| **TC66** | Reporting & IO | Deadlock results CSV export integrity | `deadlock_results.csv` in `results/` | File exists with matrices & summary | FileExists=True, SizeBytes=656 | **PASS** |
| **TC67** | Reporting & IO | 4-Panel Executive Dashboard generation | `overall_analysis.png` in `charts/` | PNG file exists and $>50$ KB | DashboardExists=True, SizeBytes=456383 | **PASS** |
| **TC68** | Reporting & IO | Multi-tier workload suite execution | Normal, Small, Large, Edge datasets | All 4 tiers benchmarked to CSV | WorkloadsProcessed=4 tiers across all modules | **PASS** |
| **TC69** | Reporting & IO | RR quantum sensitivity analysis | $q \in \{1, 2, 4, 8\}$ | Sensitivity CSV exported with context switches | SensitivityFileExists=True, SizeBytes=213 | **PASS** |
| **TC70** | Reporting & IO | Empty CPU dataset rejection | `processes = []` | Raise `ValueError` | `ValueError: Cannot benchmark CPU with empty list` | **PASS** |
| **TC71** | Reporting & IO | Empty Memory dataset rejection | `blocks = [], reqs = []` | Raise `ValueError` | `ValueError: Cannot benchmark memory with empty` | **PASS** |
| **TC72** | Reporting & IO | Empty Disk dataset rejection | `requests = []` | Raise `ValueError` | `ValueError: Cannot benchmark disk with empty` | **PASS** |
| **TC73** | Reliability | Interactive menu non-numeric input recovery | Input: `'abc'`, then `'6'` | Display friendly error, reprompt, clean exit | Handled non-numeric menu choice and reprompted | **PASS** |
| **TC74** | Reliability | Interactive main menu clean exit | Input: `'6'` | Clean exit message printed and loop terminates | Clean application termination | **PASS** |
| **TC75** | Reliability | Python runtime compatibility verification | `sys.version_info` | Returns boolean status without crashing | Compatible=True (Python 3.10/3.11 backward compatible) | **PASS** |
| **TC76** | Reliability | Structured activity audit logging | `logs/activity.log` | Log file exists and captures audit events | LogFileExists=True, SizeBytes>5000 | **PASS** |
| **TC77** | Reliability | POSIX Bash automation scripts validation | `run.sh` & `run_tests.sh` | Valid shebang, portable executable commands | `run.sh` and `run_tests.sh` validated | **PASS** |

---

## 3. Reliability, Error Recovery & Logging Audit

### 3.1 Defensive Exception Boundaries
The simulator implements multi-tier input sanitization:
1. **CLI Layer (`main.py`)**: All user prompts are enclosed within `try/except (ValueError, KeyboardInterrupt, EOFError)` blocks. Malformed inputs reprompt the user with descriptive guidance without terminating the application process.
2. **Validator Layer (`utils/validators.py`)**: Strongly-typed validation enforces positive integers for bursts/quantums/cylinders, non-negative integers for arrival times/priorities, and rejection of boolean/float types.
3. **Algorithmic Layer (`modules/`)**: Algorithms maintain state immutability. Inputs are deep-copied prior to dispatch. Speculative allocations (e.g. dynamic resource requests in Banker's algorithm) operate on scratch states and commit only upon verified safety.

### 3.2 Audit Logging Specification
All operational events are persisted to [`logs/activity.log`](file:///C:/Users/rpsra/Downloads/Operating-Systems-Lab/logs/activity.log) and mirrored to [`Phase_4_Testing/logs/activity.log`](file:///C:/Users/rpsra/Downloads/Operating-Systems-Lab/Phase_4_Testing/logs/activity.log). Logging is structured as:
- **Application Lifecycle**: Logs application startup runtime parameters and graceful termination on user exit.
- **Module Invocations**: Records entry into CPU scheduling, memory management, deadlock analysis, disk scheduling, and comparative reporting.
- **Algorithm Selections**: Logs execution parameters (e.g. `Time Quantum=2`, `Direction=up`, `Total Cylinders=200`).
- **Safety Interceptions**: Logs all validation rejections, capacity violations, and unsafe deadlock requests at `WARNING` or `ERROR` level.
- **Reporting Engine**: Logs every CSV generated and 300 DPI chart rendered.

Crucially, **internal arithmetic calculations are never logged**, preventing log bloat and performance degradation.

---

## 4. Code Quality & Audit Findings

During the Phase 4 code audit, 7 potential reliability risks were systematically identified, isolated, and remediated:

| Finding ID | Severity | Subsystem | Issue Description | Remediation Applied |
| :---: | :---: | :---: | :--- | :--- |
| **AUD-01** | High | `utils/validators.py` | Python's `int(True)` evaluates to `1`, allowing booleans to pass as positive integers. | Added explicit `if isinstance(value, bool): raise ValueError(...)` in integer validators. |
| **AUD-02** | High | `utils/validators.py` | Floating point cylinder values (e.g. `45.7`) truncated silently to `45`. | Added explicit `if isinstance(value, float): raise ValueError(...)` in numeric validators. |
| **AUD-03** | Medium | `utils/validators.py` | Process dictionary validation defaulted missing PIDs to auto-generated strings rather than requiring the field. | Added explicit validation requiring non-empty `'pid'` in process dictionaries. |
| **AUD-04** | Medium | `utils/validators.py` | Memory request list permitted duplicate process IDs. | Added `seen_req_pids` set checking and rejecting duplicate memory allocation IDs. |
| **AUD-05** | Medium | `utils/validators.py` | Banker's matrix allowed empty process ID lists or duplicate process IDs. | Added explicit empty check and uniqueness check on `process_ids`. |
| **AUD-06** | High | `Phase_4_Testing` | Audit script tested an allocation ($P_0$ requesting $[0, 2, 0]$) that was actually safe rather than unsafe. | Updated test input to $P_4$ requesting $[3, 3, 0]$, creating a proven unsafe state with $[0, 0, 2]$ available, properly verifying denial and rollback. |
| **AUD-07** | Medium | `run.sh` / `run_tests.sh` | Hardcoded `python3` command failed on environments where Python is aliased as `python`. | Added shell fallback: `if command -v python3; then python3 ... else python ... fi`. |

---

## 5. Artifacts and Evidence Generation

All evidence required by the Phase 4 blueprint has been created and verified in [`Phase_4_Testing/`](file:///C:/Users/rpsra/Downloads/Operating-Systems-Lab/Phase_4_Testing):
- [`Phase_4_Testing/test_cases.csv`](file:///C:/Users/rpsra/Downloads/Operating-Systems-Lab/Phase_4_Testing/test_cases.csv): Formal specification of all 77 test cases.
- [`Phase_4_Testing/test_results.csv`](file:///C:/Users/rpsra/Downloads/Operating-Systems-Lab/Phase_4_Testing/test_results.csv): Actual test execution results with inputs, expected vs actual values, PASS/FAIL status, and notes.
- [`Phase_4_Testing/logs/test_execution.log`](file:///C:/Users/rpsra/Downloads/Operating-Systems-Lab/Phase_4_Testing/logs/test_execution.log): Formatted log file recording each test case execution.
- [`Phase_4_Testing/logs/activity.log`](file:///C:/Users/rpsra/Downloads/Operating-Systems-Lab/Phase_4_Testing/logs/activity.log): System audit log.
- [`Phase_4_Testing/tests/`](file:///C:/Users/rpsra/Downloads/Operating-Systems-Lab/Phase_4_Testing/tests): Complete mirror of test suites (`test_cpu.py`, `test_memory.py`, `test_deadlock.py`, `test_disk.py`, `test_reporting.py`, `test_smoke.py`, `test_validators.py`, `test_integration.py`, `test_main.py`).

---

## 6. Final Certification

The test suite and empirical evidence confirm that:
1. All algorithms in CPU, Memory, Deadlock, and Disk scheduling behave in strict conformity with theoretical computer science principles.
2. The system handles invalid types, boundary values, empty collections, and unsafe resource requests defensively and deterministically.
3. Every test in the 115-test Python `unittest` discover suite and the 77-case audit matrix executes and passes.
4. **Phase 4 Testing and Reliability is formally certified as COMPLETE.**
