import urllib.request
import json
import sys

BASE = "http://127.0.0.1:8501"

def check_get(path):
    req = urllib.request.urlopen(f"{BASE}{path}")
    data = req.read()
    print(f"  [GET {path:26}] -> Status: {req.status}, Size: {len(data):6} bytes")
    return data

def check_post(path, payload):
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read().decode("utf-8"))
    print(f"  [POST {path:25}] -> Status: {resp.status}, Response Mode: {data.get('mode', 'N/A')}")
    return data

def main():
    print("==================================================")
    print("      LIVE WEB SERVER END-TO-END VERIFICATION     ")
    print("==================================================")

    print("\n1. Verifying Static Assets & Health Check:")
    check_get("/")
    check_get("/styles.css")
    check_get("/app.js")
    h_data = json.loads(check_get("/api/health").decode())
    assert h_data["status"] == "healthy", "Health check failed"

    print("\n2. Verifying Workload Presets API:")
    p_data = json.loads(check_get("/api/presets?tier=normal").decode())
    print(f"  ✓ Normal Preset Loaded: {len(p_data['cpu'])} CPU jobs, {len(p_data['memory']['blocks'])} RAM blocks, {len(p_data['disk']['requests'])} Disk requests")

    print("\n3. Verifying CPU Scheduling API (All Algorithms):")
    cpu_res = check_post("/api/cpu/run", {
        "algorithm": "all",
        "quantum": 2,
        "processes": p_data["cpu"]
    })
    for alg in ["fcfs", "sjf", "rr", "priority"]:
        assert alg in cpu_res["results"], f"Missing {alg} in CPU result"
        m = cpu_res["results"][alg]["metrics"]
        print(f"  ✓ {alg.upper():10} -> AvgWT: {m['avg_waiting_time']:.2f}, AvgTAT: {m['avg_turnaround_time']:.2f}, CPU Util: {m['cpu_utilization']:.1f}%")

    print("\n4. Verifying Memory Management API (All Algorithms):")
    mem_res = check_post("/api/memory/run", {
        "algorithm": "all",
        "blocks": p_data["memory"]["blocks"],
        "requests": p_data["memory"]["requests"]
    })
    for r in mem_res["results"]:
        print(f"  ✓ {r['algorithm'].upper():12} -> Success: {r['successful_allocations']}/{r['successful_allocations']+r['failed_allocations']}, ExtFrag: {r['external_fragmentation_kb']} KB, MemUtil: {r['memory_utilization']:.1f}%")

    print("\n5. Verifying Deadlock Management API (Banker's Algorithm & Requests):")
    dlk_res = check_post("/api/deadlock/run", {
        "process_ids": p_data["deadlock"]["process_ids"],
        "resource_ids": p_data["deadlock"]["resource_ids"],
        "available": p_data["deadlock"]["available"],
        "allocation": p_data["deadlock"]["allocation"],
        "max_demand": p_data["deadlock"]["max_demand"],
        "request": {"pid": "P1", "resources": [1, 0, 2]}
    })
    assert dlk_res["is_safe"] is True, "System should be safe"
    print(f"  ✓ System State   -> Safe: {dlk_res['is_safe']}, Safe Sequence: {' -> '.join(dlk_res['safe_sequence'])}")
    req_eval = dlk_res["request_evaluation"]
    print(f"  ✓ Dynamic Request-> Decision: {req_eval['decision']}, Post Safe: {req_eval['post_safe']}, Msg: {req_eval['detail']}")

    print("\n6. Verifying Disk Scheduling API (All Algorithms):")
    disk_res = check_post("/api/disk/run", {
        "algorithm": "all",
        "requests": p_data["disk"]["requests"],
        "initial_head": p_data["disk"]["initial_head"],
        "total_cylinders": 200,
        "direction": "up"
    })
    for r in disk_res["results"]:
        print(f"  ✓ {r['algorithm'].upper():12} -> Head Movement: {r['total_head_movement']} cyl, Avg Seek: {r['average_head_movement']:.2f} cyl/req")

    print("\n==================================================")
    print("  [SUCCESS] ALL SUBSYSTEMS & ENDPOINTS VERIFIED!  ")
    print("==================================================")

if __name__ == "__main__":
    main()
