import subprocess
import sys
import os

commits = [
    # 1. Validators
    (["utils/validators.py"], "refactor(validators): implement defensive type verification and boundary checks"),
    
    # 2. Reporting Module
    (["modules/reporting.py"], "feat(reporting): integrate cross-module benchmarking and metrics engine"),
    
    # 3-10. Datasets (data/)
    (["data/cpu_normal.csv", "data/cpu_processes.csv", "data/cpu_input.csv"], "feat(data): add canonical baseline CPU scheduling workload datasets"),
    (["data/cpu_small.csv", "data/cpu_large.csv"], "feat(data): add multi-tier small and large CPU workload datasets"),
    (["data/cpu_edge.csv"], "feat(data): add simultaneous arrival edge CPU workload dataset"),
    (["data/memory_normal.csv", "data/memory_workload.csv", "data/memory_input.csv"], "feat(data): add canonical baseline memory allocation workload datasets"),
    (["data/memory_small.csv", "data/memory_large.csv", "data/memory_edge.csv"], "feat(data): add multi-tier and high-demand memory workload datasets"),
    (["data/deadlock_normal.csv", "data/deadlock_small.csv"], "feat(data): add canonical multi-resource allocation state and small matrices"),
    (["data/deadlock_large.csv", "data/deadlock_edge.csv"], "feat(data): add complex 5-resource and deadlock-prone edge case matrices"),
    (["data/disk_normal.csv", "data/disk_requests.csv", "data/disk_input.csv"], "feat(data): add canonical 8-request baseline disk cylinder queue"),
    (["data/disk_small.csv", "data/disk_large.csv", "data/disk_edge.csv"], "feat(data): add multi-tier and boundary cylinder disk request queues"),

    # 11-15. Baseline Results Persistence (results/)
    (["results/cpu_results.csv", "results/cpu_workloads_comparison.csv"], "feat(results): persist baseline CPU scheduling benchmark metrics"),
    (["results/rr_quantum_sensitivity.csv"], "feat(results): persist Round Robin quantum sensitivity analysis across q in [1, 10]"),
    (["results/memory_results.csv", "results/memory_workloads_comparison.csv"], "feat(results): persist memory allocation and external fragmentation records"),
    (["results/deadlock_results.csv", "results/deadlock_workloads_comparison.csv"], "feat(results): persist Banker's algorithm safe sequences and request audits"),
    (["results/disk_results.csv", "results/disk_workloads_comparison.csv"], "feat(results): persist cylinder seek movement and trajectory benchmark data"),

    # 16-19. Phase 3 Analysis Subsystem
    (["Phase_3_Analysis/datasets/"], "feat(analysis): populate Phase 3 standardized benchmark datasets"),
    (["Phase_3_Analysis/results/"], "feat(analysis): record Phase 3 multi-workload simulation outputs"),
    (["Phase_3_Analysis/charts/"], "feat(analysis): generate Phase 3 publication-grade comparison charts"),
    (["Phase_3_Analysis/observations.md"], "docs(analysis): author Phase 3 comprehensive observations on algorithmic trade-offs"),

    # 20-23. Charts (charts/)
    (["charts/cpu_chart.png", "charts/cpu_comparison.png"], "feat(charts): render 300 DPI CPU scheduling comparison bar chart"),
    (["charts/memory_chart.png", "charts/memory_comparison.png"], "feat(charts): render 300 DPI memory allocation and fragmentation breakdown"),
    (["charts/disk_chart.png", "charts/disk_comparison.png"], "feat(charts): render 300 DPI disk seek movement comparison chart"),
    (["charts/overall_analysis.png"], "feat(charts): render 300 DPI 4-panel master executive performance dashboard"),

    # 24-27. Test Suites (tests/)
    (["tests/test_smoke.py"], "test(smoke): add environment compatibility and logging verification tests"),
    (["tests/test_reporting.py"], "test(reporting): add unit test suite for reporting engine and metrics"),
    (["tests/test_integration.py"], "test(integration): add cross-subsystem end-to-end integration tests"),
    (["tests/test_streamlit_app.py"], "test(ui): add test harness for Streamlit dashboard navigation and pages"),

    # 28-32. Phase 4 Testing Package (Phase_4_Testing/)
    (["Phase_4_Testing/tests/"], "feat(testing): populate Phase 4 unit test discovery suite"),
    (["Phase_4_Testing/test_cases.csv"], "feat(testing): author formal test cases matrix spanning TC01 through TC77"),
    (["Phase_4_Testing/test_cases.xlsx"], "feat(testing): generate binary Excel workbook test_cases.xlsx for submission"),
    (["Phase_4_Testing/test_results.csv"], "feat(testing): record runtime test execution results verifying 100% pass rate"),
    (["Phase_4_Testing/run_phase4_audit.py", "Phase_4_Testing/logs/", "Phase_4_Testing/testing_report.md"], "docs(testing): author comprehensive Phase 4 testing and reliability audit report"),

    # 33-35. Build & CI Scripts
    (["requirements.txt"], "chore(deps): specify minimal dependencies for pandas, matplotlib, and streamlit"),
    (["run.sh"], "ci(scripts): enhance automated bash runner script for terminal application"),
    (["run_tests.sh"], "ci(scripts): enhance automated bash test runner for unittest discovery"),

    # 36-37. Automation Tools (tools/)
    (["tools/generate_screenshots.py"], "tools(screenshots): implement automated headless terminal screenshot generator"),
    (["tools/build_html_reports.py"], "tools(reports): implement automated print-ready HTML academic report builder"),

    # 38-42. Screenshots (screenshots/)
    (["screenshots/01_main_application_menu.png", "screenshots/02_cpu_scheduling_execution.png"], "docs(screenshots): add CLI main menu and CPU scheduling Gantt execution captures"),
    (["screenshots/03_memory_allocation_results.png", "screenshots/04_deadlock_detection_banker.png"], "docs(screenshots): add dynamic memory allocation and Banker's safe sequence captures"),
    (["screenshots/05_disk_scheduling_trajectories.png", "screenshots/06_performance_comparison_dashboard.png"], "docs(screenshots): add disk seek trajectories and 4-panel performance dashboard captures"),
    (["screenshots/07_test_suite_execution.png", "screenshots/08_activity_logging_audit.png"], "docs(screenshots): add unit test execution trace and activity audit log captures"),
    (["screenshots/09_streamlit_executive_dashboard.png", "screenshots/10_streamlit_algorithm_simulators.png"], "docs(screenshots): add Streamlit overview dashboard and interactive simulator captures"),

    # 43. Presentation Dashboard
    (["app.py"], "feat(ui): implement Streamlit Pro-Max dark-mode interactive dashboard with 4-tab section layouts"),

    # 44-45. Phase 1 Master Design
    (["Phase_1_Design/phase1_design.md"], "docs(design): compile Phase 1 consolidated architecture specification report"),
    (["Phase_1_Design/phase1_design.html"], "docs(design): compile print-ready styled HTML report for Phase 1 submission"),

    # 46-47. Phase 5 Academic Project Report
    (["documentation/project_report.md"], "docs(report): author 25-page comprehensive academic project report across 11 sections"),
    (["documentation/project_report.html"], "docs(report): compile print-ready styled HTML academic project report"),

    # 48. Viva Voce Preparation
    (["documentation/viva_preparation.md"], "docs(viva): author complete oral examination viva voce preparation handbook"),

    # 49. Master Guide
    (["PROJECT_COMPLETE_GUIDE.md"], "docs(guide): compile complete master feature walkthrough and presentation guide"),

    # 50. README
    (["README.md"], "docs(readme): update project documentation index with master guide and quickstart links"),
]

def main():
    print(f"Total commits planned: {len(commits)}")
    for idx, (files, msg) in enumerate(commits, 1):
        add_cmd = ["git", "add"] + files
        res = subprocess.run(add_cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Error adding files for commit {idx}: {res.stderr}")
            sys.exit(1)
        
        commit_cmd = ["git", "commit", "-m", msg]
        res = subprocess.run(commit_cmd, capture_output=True, text=True)
        if res.returncode != 0:
            # Check if there was anything to commit
            if "nothing to commit" in res.stdout or "nothing to commit" in res.stderr:
                print(f"[{idx}/50] Nothing to commit for: {msg}")
            else:
                print(f"Error committing [{idx}/50]: {res.stderr}")
                sys.exit(1)
        else:
            print(f"[{idx}/50] Successfully committed: {msg}")

    print("\nAll commits executed successfully!")

if __name__ == "__main__":
    main()
