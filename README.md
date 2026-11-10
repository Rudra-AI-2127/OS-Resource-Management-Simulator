# OS Resource Management Simulator
**Integrated Operating System Resource Management Simulator**

An integrated, modular Python application engineered to simulate, benchmark, and analyze core operating system resource management algorithms. Developed for the Operating Systems Lab Capstone (Submission Deadline: 14 November 2026).

> 📘 **Looking for the master feature & presentation guide?**  
> Read the complete handbook: [**`PROJECT_COMPLETE_GUIDE.md`**](file:///c:/Users/rpsra/Downloads/Operating-Systems-Lab/PROJECT_COMPLETE_GUIDE.md) — includes in-depth explanations of all 15 algorithms, quick-start commands, a 10-minute live demonstration script, and answers to the top 10 faculty viva questions.

---

## 1. Overview & Modules

The simulator integrates five specialized subsystems into a single interactive terminal application:

1. **CPU Scheduling**:
   - First-Come, First-Served (**FCFS** - Non-preemptive)
   - Shortest Job First (**SJF** - Non-preemptive)
   - Round Robin (**RR** - Preemptive, configurable quantum $q$)
   - Priority Scheduling (**Priority** - Non-preemptive, lower numeric value = higher priority)
   - Metrics: Completion Time ($CT$), Turnaround Time ($TAT$), Waiting Time ($WT$), Response Time ($RT$), and ASCII Gantt chart timelines.
2. **Memory Management**:
   - Contiguous dynamic partition allocation: **First Fit**, **Best Fit**, and **Worst Fit**.
   - Dynamic block splitting: partitions free blocks to exact requested sizes and returns remainders to the free pool.
   - Fragmentation accounting: strictly distinguishes external fragmentation from internal fragmentation.
3. **Deadlock Management**:
   - Dijkstra's **Banker's Algorithm** for multi-instance resource systems.
   - Dynamic $Need$ matrix derivation ($Need = Max - Allocation$).
   - System safety audits, safe sequence identification, and dynamic resource-request safety checks with speculative rollback.
4. **Disk Scheduling**:
   - Cylindrical seek optimization: **FCFS**, Shortest Seek Time First (**SSTF**), **SCAN** (Elevator), and Circular SCAN (**C-SCAN**).
   - Accurate cylinder seek steps, boundary sweeps, wraparound jump accounting, and average seek distance.
5. **Reporting & Performance Analysis**:
   - Cross-algorithm comparisons under identical baseline workloads.
   - Structured CSV result persistence (`results/*.csv`).
   - Publication-quality analytical charts rendered with Matplotlib (`charts/*.png`).

---

## 2. Technology Stack & Requirements

- **Runtime**: Python 3.11+ (tested on Python 3.12.3 in Linux/WSL and Python 3.10+ on Windows).
- **Core Dependencies**:
  - `matplotlib` (>= 3.8.0)
  - `pandas` (>= 2.1.0)
- **Standard Library**: `dataclasses`, `unittest`, `logging`, `csv`, `pathlib`, `collections`.
- **Operating Systems**: Linux / Ubuntu (WSL2), macOS, Windows 10/11.

---

## 3. Directory Layout

```
Operating-Systems-Lab/
├── main.py                     # Central application interactive controller
├── app.py                      # Optional Streamlit dashboard (Phase 5)
├── requirements.txt            # Minimal dependency definitions
├── README.md                   # Project documentation & setup instructions
├── run.sh                      # Automated Bash application launcher
├── run_tests.sh                # Automated Bash test runner
├── modules/                    # Core resource-management engines
│   ├── __init__.py
│   ├── cpu_scheduling.py
│   ├── memory_management.py
│   ├── deadlock.py
│   ├── disk_scheduling.py
│   └── reporting.py
├── utils/                      # Shared cross-cutting utilities
│   ├── __init__.py
│   ├── validators.py           # Defensive validation gateway
│   ├── logger.py               # Structured audit logger
│   └── helpers.py              # ASCII tables and Gantt renderers
├── tests/                      # Automated unittest test suite
│   ├── __init__.py
│   ├── test_smoke.py           # Bootstrap and environment verification
│   ├── test_validators.py      # Validator tests
│   ├── test_cpu.py             # CPU scheduling tests
│   ├── test_memory.py          # Memory management tests
│   ├── test_deadlock.py        # Banker's algorithm tests
│   ├── test_disk.py            # Disk scheduling tests
│   └── test_main.py            # Main controller navigation tests
├── data/                       # Standardized baseline benchmark datasets
├── results/                    # Exported simulation CSV results
├── charts/                     # Matplotlib analytical figures
├── logs/                       # Activity audit trail (logs/activity.log)
├── screenshots/                # Real terminal and chart execution captures
├── Phase_1_Design/             # Phase 1 submission folder (20 marks)
├── Phase_3_Analysis/           # Phase 3 submission folder (20 marks)
├── Phase_4_Testing/            # Phase 4 submission folder (20 marks)
└── documentation/              # Project report & viva defense materials
```

---

## 4. Setup & Installation

### Option A: Linux / WSL (Ubuntu)

```bash
# 1. Clone or navigate to the project directory
cd ~/Operating-Systems-Lab

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Option B: Windows (PowerShell)

```powershell
# 1. Navigate to the project directory
cd C:\Users\rpsra\Downloads\Operating-Systems-Lab

# 2. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 5. Execution Instructions

### Running the Interactive Simulator

Using Python directly:
```bash
python3 main.py     # Linux / macOS / WSL
python main.py      # Windows
```

Using the automated Bash script:
```bash
chmod +x run.sh
./run.sh
```

### Interactive Menu Navigation
```
==================================================
        OS RESOURCE MANAGEMENT SIMULATOR
==================================================
OS RESOURCE MANAGEMENT
1. CPU Scheduling
2. Memory Management
3. Deadlock Management
4. Disk Scheduling
5. Performance Analysis
6. Exit
Enter choice (1-6): 
```

---

## 6. Testing & Quality Assurance

Run the automated test suite discovering all test modules:

```bash
# Direct Python discovery
python3 -m unittest discover -s tests

# Or via automated Bash script
chmod +x run_tests.sh
./run_tests.sh
```

All test outcomes, warnings, and errors are recorded in `logs/activity.log`.
