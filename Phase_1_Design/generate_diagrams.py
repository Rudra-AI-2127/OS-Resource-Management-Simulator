"""
Render system_architecture.png and workflow_diagram.png using Matplotlib.
Produces high-resolution diagrams adhering to Phase 1 blueprint deliverables.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent

def generate_system_architecture():
    fig, ax = plt.subplots(figsize=(14, 10), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Title
    ax.text(50, 96, "OS RESOURCE MANAGEMENT SIMULATOR", 
            ha='center', va='center', fontsize=18, fontweight='bold', color='#1a237e')
    ax.text(50, 93, "System Architectural Topology & Subsystem Boundaries", 
            ha='center', va='center', fontsize=12, style='italic', color='#455a64')

    # Layer 1: Presentation Layer
    layer1 = patches.FancyBboxPatch((5, 78), 90, 12, boxstyle="round,pad=1,rounding_size=2",
                                    facecolor='#e1f5fe', edgecolor='#0288d1', linewidth=2)
    ax.add_patch(layer1)
    ax.text(8, 87, "PRESENTATION & USER INTERFACES", fontsize=11, fontweight='bold', color='#01579b')
    
    # Subcomponents in Layer 1
    c1 = patches.FancyBboxPatch((10, 80), 24, 6, boxstyle="round,pad=0.5", facecolor='#ffffff', edgecolor='#0288d1')
    ax.add_patch(c1)
    ax.text(22, 83, "CLI Controller\n(main.py)", ha='center', va='center', fontsize=9, fontweight='semibold', color='#0277bd')

    c2 = patches.FancyBboxPatch((38, 80), 24, 6, boxstyle="round,pad=0.5", facecolor='#ffffff', edgecolor='#0288d1')
    ax.add_patch(c2)
    ax.text(50, 83, "Streamlit Dashboard\n(app.py - Optional)", ha='center', va='center', fontsize=9, color='#0277bd')

    c3 = patches.FancyBboxPatch((66, 80), 24, 6, boxstyle="round,pad=0.5", facecolor='#ffffff', edgecolor='#0288d1')
    ax.add_patch(c3)
    ax.text(78, 83, "Automated Bash Scripts\n(run.sh / run_tests.sh)", ha='center', va='center', fontsize=9, color='#0277bd')

    # Layer 2: Orchestration & Utilities
    layer2 = patches.FancyBboxPatch((5, 59), 90, 15, boxstyle="round,pad=1,rounding_size=2",
                                    facecolor='#e8f5e9', edgecolor='#388e3c', linewidth=2)
    ax.add_patch(layer2)
    ax.text(8, 71, "CONTROLLER & SHARED INFRASTRUCTURE", fontsize=11, fontweight='bold', color='#1b5e20')

    ctrl = patches.FancyBboxPatch((10, 61), 38, 8, boxstyle="round,pad=0.5", facecolor='#ffffff', edgecolor='#388e3c')
    ax.add_patch(ctrl)
    ax.text(29, 65, "Application Controller & Dispatcher\n(main.py: Navigation & Flow Control)", 
            ha='center', va='center', fontsize=9, fontweight='semibold', color='#2e7d32')

    val = patches.FancyBboxPatch((52, 61), 19, 8, boxstyle="round,pad=0.5", facecolor='#ffffff', edgecolor='#388e3c')
    ax.add_patch(val)
    ax.text(61.5, 65, "Input Validators\n(utils/validators.py)", ha='center', va='center', fontsize=8.5, color='#2e7d32')

    log = patches.FancyBboxPatch((74, 61), 18, 8, boxstyle="round,pad=0.5", facecolor='#ffffff', edgecolor='#388e3c')
    ax.add_patch(log)
    ax.text(83, 65, "Activity Logger\n(utils/logger.py)", ha='center', va='center', fontsize=8.5, color='#2e7d32')

    # Layer 3: Core Algorithmic Engines
    layer3 = patches.FancyBboxPatch((5, 34), 90, 21, boxstyle="round,pad=1,rounding_size=2",
                                    facecolor='#fff3e0', edgecolor='#f57c00', linewidth=2)
    ax.add_patch(layer3)
    ax.text(8, 52, "CORE OS RESOURCE-MANAGEMENT MODULES", fontsize=11, fontweight='bold', color='#e65100')

    m1 = patches.FancyBboxPatch((8, 36), 19.5, 14, boxstyle="round,pad=0.5", facecolor='#ffffff', edgecolor='#f57c00')
    ax.add_patch(m1)
    ax.text(17.75, 47, "CPU Scheduling\n(cpu_scheduling.py)", ha='center', va='center', fontsize=9, fontweight='bold', color='#d84315')
    ax.text(17.75, 40, "• FCFS\n• SJF (Non-preempt)\n• Round Robin (q)\n• Priority (Non-preempt)", ha='center', va='center', fontsize=7.5, color='#bf360c')

    m2 = patches.FancyBboxPatch((30.5, 36), 19.5, 14, boxstyle="round,pad=0.5", facecolor='#ffffff', edgecolor='#f57c00')
    ax.add_patch(m2)
    ax.text(40.25, 47, "Memory Mgmt\n(memory_management.py)", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#d84315')
    ax.text(40.25, 40, "• First Fit\n• Best Fit\n• Worst Fit\n• Dynamic Splitting", ha='center', va='center', fontsize=7.5, color='#bf360c')

    m3 = patches.FancyBboxPatch((53, 36), 19.5, 14, boxstyle="round,pad=0.5", facecolor='#ffffff', edgecolor='#f57c00')
    ax.add_patch(m3)
    ax.text(62.75, 47, "Deadlock Mgmt\n(deadlock.py)", ha='center', va='center', fontsize=9, fontweight='bold', color='#d84315')
    ax.text(62.75, 40, "• Need Matrix\n• Banker's Safety\n• Safe Sequence\n• Request Grant Check", ha='center', va='center', fontsize=7.5, color='#bf360c')

    m4 = patches.FancyBboxPatch((75.5, 36), 17.5, 14, boxstyle="round,pad=0.5", facecolor='#ffffff', edgecolor='#f57c00')
    ax.add_patch(m4)
    ax.text(84.25, 47, "Disk Scheduling\n(disk_scheduling.py)", ha='center', va='center', fontsize=9, fontweight='bold', color='#d84315')
    ax.text(84.25, 40, "• FCFS\n• SSTF\n• SCAN (Elevator)\n• C-SCAN (Circular)", ha='center', va='center', fontsize=7.5, color='#bf360c')

    # Layer 4: Reporting & Output Persistence
    layer4 = patches.FancyBboxPatch((5, 8), 90, 22, boxstyle="round,pad=1,rounding_size=2",
                                    facecolor='#fce4ec', edgecolor='#c2185b', linewidth=2)
    ax.add_patch(layer4)
    ax.text(8, 27, "REPORTING, BENCHMARKING & PERSISTENCE", fontsize=11, fontweight='bold', color='#880e4f')

    rep = patches.FancyBboxPatch((8, 11), 38, 14, boxstyle="round,pad=0.5", facecolor='#ffffff', edgecolor='#c2185b')
    ax.add_patch(rep)
    ax.text(27, 21.5, "Reporting & Analytics Engine (reporting.py)", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#ad1457')
    ax.text(27, 15.5, "• Automated Cross-Algorithm Benchmark\n• Comparative Performance Tables\n• Matplotlib Graph Generator (4+ plots)", ha='center', va='center', fontsize=7.5, color='#880e4f')

    per1 = patches.FancyBboxPatch((49, 11), 22, 14, boxstyle="round,pad=0.5", facecolor='#ffffff', edgecolor='#c2185b')
    ax.add_patch(per1)
    ax.text(60, 21.5, "Datasets & CSV Storage", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#ad1457')
    ax.text(60, 15.5, "• data/*.csv (Inputs)\n• results/*.csv (Outputs)\n• reproducible traces", ha='center', va='center', fontsize=7.5, color='#880e4f')

    per2 = patches.FancyBboxPatch((74, 11), 19, 14, boxstyle="round,pad=0.5", facecolor='#ffffff', edgecolor='#c2185b')
    ax.add_patch(per2)
    ax.text(83.5, 21.5, "Visual Artifacts & Logs", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#ad1457')
    ax.text(83.5, 15.5, "• charts/*.png\n• logs/activity.log\n• screenshots/", ha='center', va='center', fontsize=7.5, color='#880e4f')

    # Connecting arrows
    arrow_props = dict(facecolor='#37474f', edgecolor='#37474f', width=1.2, headwidth=6, headlength=6, shrink=0.05)
    ax.annotate('', xy=(29, 69), xytext=(22, 80), arrowprops=arrow_props)
    ax.annotate('', xy=(17.75, 50), xytext=(22, 61), arrowprops=arrow_props)
    ax.annotate('', xy=(40.25, 50), xytext=(29, 61), arrowprops=arrow_props)
    ax.annotate('', xy=(62.75, 50), xytext=(36, 61), arrowprops=arrow_props)
    ax.annotate('', xy=(84.25, 50), xytext=(40, 61), arrowprops=arrow_props)
    ax.annotate('', xy=(27, 25), xytext=(50, 36), arrowprops=arrow_props)

    plt.tight_layout()
    out_path = OUT_DIR / "system_architecture.png"
    plt.savefig(out_path, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Generated: {out_path}")

def generate_workflow_diagram():
    fig, ax = plt.subplots(figsize=(12, 14), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Title
    ax.text(50, 97, "OS RESOURCE MANAGEMENT SIMULATOR", 
            ha='center', va='center', fontsize=17, fontweight='bold', color='#1a237e')
    ax.text(50, 94.5, "End-to-End Application Workflow & Simulation Lifecycle", 
            ha='center', va='center', fontsize=11.5, style='italic', color='#455a64')

    def draw_box(x, y, w, h, text, title=None, bg='#ffffff', edge='#0288d1', shape='rect'):
        boxstyle = "circle,pad=0.3" if shape == 'circle' else "round,pad=0.5,rounding_size=1.5"
        p = patches.FancyBboxPatch((x, y), w, h, boxstyle=boxstyle, facecolor=bg, edgecolor=edge, linewidth=1.5)
        ax.add_patch(p)
        if title:
            ax.text(x + w/2, y + h - 2.5, title, ha='center', va='center', fontsize=8.5, fontweight='bold', color=edge)
            ax.text(x + w/2, y + (h - 2.5)/2, text, ha='center', va='center', fontsize=8, color='#263238')
        else:
            ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=8.5, fontweight='semibold', color='#263238')

    # Start
    draw_box(38, 89, 24, 4, "Application Start (main.py)", bg='#e8eaf6', edge='#303f9f')
    
    # Init Logging
    draw_box(32, 81.5, 36, 5, "Initialize Logger & Audit Subsystem\n(logs/activity.log)", bg='#ede7f6', edge='#512da8')
    
    # Main Menu
    draw_box(25, 71, 50, 7.5, "Options: 1. CPU | 2. Memory | 3. Deadlock\n4. Disk | 5. Reporting | 6. Exit", 
             title="INTERACTIVE MENU LOOP (main.py)", bg='#e1f5fe', edge='#0288d1')
    
    # Input Selection
    draw_box(20, 58, 28, 9, "Interactive Manual Entry\n(Console Prompts)", title="INPUT SOURCE: MANUAL", bg='#fffde7', edge='#fbc02d')
    draw_box(52, 58, 28, 9, "Batch Execution from CSV\n(Load from data/*.csv)", title="INPUT SOURCE: BATCH CSV", bg='#fffde7', edge='#fbc02d')

    # Validation Engine
    draw_box(25, 46, 50, 8.5, "Range Checks, Data Types, Boundary Protection\n(utils/validators.py - raises ValueError)", 
             title="STRICT INPUT VALIDATION GATEWAY", bg='#ffebee', edge='#d32f2f')

    # Module Execution Branch
    draw_box(4, 30, 21, 12, "FCFS, SJF, RR (q),\nPriority Scheduling;\nMetrics: CT, TAT, WT, RT;\nGantt Chart Generator", 
             title="CPU SCHEDULER", bg='#fff3e0', edge='#f57c00')

    draw_box(27.5, 30, 21, 12, "First, Best, Worst Fit;\nDynamic Partition Split;\nInternal / External\nFragmentation Audits", 
             title="MEMORY ALLOCATOR", bg='#fff3e0', edge='#f57c00')

    draw_box(51, 30, 21, 12, "Need Matrix = Max - Alloc;\nBanker's Safety Algorithm;\nSafe Execution Sequence;\nDynamic Request Grant", 
             title="DEADLOCK (BANKER)", bg='#fff3e0', edge='#f57c00')

    draw_box(74.5, 30, 21, 12, "FCFS, SSTF, SCAN, C-SCAN;\nTotal Cylinder Movement;\nAverage Head Seek;\nRequest Path Sequence", 
             title="DISK SCHEDULER", bg='#fff3e0', edge='#f57c00')

    # Results & Visualization Layer
    draw_box(15, 14, 32, 11, "Console Output Formatting\nASCII Tables & Gantt Charts\n(utils/helpers.py)", 
             title="PRESENTATION OUTPUT", bg='#f3e5f5', edge='#7b1fa2')

    draw_box(53, 14, 32, 11, "Export results/*.csv\nGenerate 4+ Matplotlib Charts\n(Phase_3_Analysis/)", 
             title="REPORTING & EXPORT", bg='#fce4ec', edge='#c2185b')

    # Exit
    draw_box(38, 3, 24, 6, "Log Shutdown & Clean Exit\n(Option 6)", bg='#eceff1', edge='#455a64')

    # Arrows
    arrow = dict(facecolor='#455a64', edgecolor='#455a64', width=1.0, headwidth=5, headlength=5, shrink=0.05)
    ax.annotate('', xy=(50, 86.5), xytext=(50, 89), arrowprops=arrow)
    ax.annotate('', xy=(50, 78.5), xytext=(50, 81.5), arrowprops=arrow)
    ax.annotate('', xy=(34, 67), xytext=(45, 71), arrowprops=arrow)
    ax.annotate('', xy=(66, 67), xytext=(55, 71), arrowprops=arrow)
    ax.annotate('', xy=(40, 54.5), xytext=(34, 58), arrowprops=arrow)
    ax.annotate('', xy=(60, 54.5), xytext=(66, 58), arrowprops=arrow)
    ax.annotate('', xy=(14.5, 42), xytext=(35, 46), arrowprops=arrow)
    ax.annotate('', xy=(38, 42), xytext=(45, 46), arrowprops=arrow)
    ax.annotate('', xy=(61.5, 42), xytext=(55, 46), arrowprops=arrow)
    ax.annotate('', xy=(85, 42), xytext=(65, 46), arrowprops=arrow)
    ax.annotate('', xy=(31, 25), xytext=(38, 30), arrowprops=arrow)
    ax.annotate('', xy=(69, 25), xytext=(61.5, 30), arrowprops=arrow)
    ax.annotate('', xy=(50, 9), xytext=(50, 14), arrowprops=arrow)

    plt.tight_layout()
    out_path = OUT_DIR / "workflow_diagram.png"
    plt.savefig(out_path, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Generated: {out_path}")

if __name__ == "__main__":
    generate_system_architecture()
    generate_workflow_diagram()
