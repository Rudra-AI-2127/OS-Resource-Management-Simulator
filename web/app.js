/**
 * OS Resource Management Simulator — Vanilla JavaScript UI Client
 * High-performance, zero-framework, publication-grade interactive client.
 * Handles SVG vector rendering, dynamic tables, and API communication.
 */

class OSSimulatorApp {
  constructor() {
    this.currentTier = "normal";
    this.allTestCases = [];

    // State caches
    this.cpuProcesses = [
      { pid: "P1", arrival_time: 0, burst_time: 5, priority: 2 },
      { pid: "P2", arrival_time: 1, burst_time: 3, priority: 1 },
      { pid: "P3", arrival_time: 2, burst_time: 8, priority: 4 },
      { pid: "P4", arrival_time: 3, burst_time: 2, priority: 3 },
    ];

    this.memRequests = [
      { pid: "P1", size: 212 },
      { pid: "P2", size: 417 },
      { pid: "P3", size: 112 },
      { pid: "P4", size: 426 },
    ];

    this.dlState = {
      pids: ["P0", "P1", "P2", "P3", "P4"],
      rids: ["A", "B", "C"],
      available: [3, 3, 2],
      alloc: [
        [0, 1, 0],
        [2, 0, 0],
        [3, 0, 2],
        [2, 1, 1],
        [0, 0, 2],
      ],
      max: [
        [7, 5, 3],
        [3, 2, 2],
        [9, 0, 2],
        [2, 2, 2],
        [4, 3, 3],
      ],
    };
  }

  init() {
    this.setupNavigation();
    this.renderCpuTable();
    this.renderMemoryReqTable();
    this.renderDeadlockMatrix();
    this.loadBenchmarks();
    this.loadTestCases();
    this.loadLogs();

    // Auto-run baseline simulations for immediate publication visuals
    this.runCpu();
    this.runMemory();
    this.runDeadlock();
    this.runDisk();
  }

  // =========================================================================
  // NAVIGATION CONTROLLER
  // =========================================================================
  setupNavigation() {
    const tabBtns = document.querySelectorAll(".nav-tab-btn");
    tabBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        const tabId = btn.getAttribute("data-tab");
        this.switchTab(tabId);
      });
    });
  }

  switchTab(tabId) {
    document.querySelectorAll(".nav-tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".view-section").forEach((s) => s.classList.remove("active"));

    const targetBtn = document.querySelector(`.nav-tab-btn[data-tab="${tabId}"]`);
    const targetSection = document.getElementById(tabId);

    if (targetBtn) targetBtn.classList.add("active");
    if (targetSection) targetSection.classList.add("active");
  }

  // =========================================================================
  // PRESET MANAGEMENT
  // =========================================================================
  async loadPreset(moduleName, tier) {
    this.currentTier = tier;

    // Highlight active preset button in the active view
    const section = document.getElementById(`tab-${moduleName}`);
    if (section) {
      section.querySelectorAll(".preset-btn").forEach((btn) => {
        btn.classList.toggle("active", btn.textContent.toLowerCase().includes(tier));
      });
    }

    try {
      const res = await fetch(`/api/presets?tier=${tier}`);
      if (!res.ok) throw new Error("Failed to load preset");
      const data = await res.json();

      if (moduleName === "cpu" && data.cpu) {
        this.cpuProcesses = data.cpu;
        this.renderCpuTable();
        this.runCpu();
      } else if (moduleName === "memory" && data.memory) {
        document.getElementById("mem-blocks-input").value = data.memory.blocks.join(", ");
        this.memRequests = data.memory.requests.map((r) => ({ pid: r[0], size: r[1] }));
        this.renderMemoryReqTable();
        this.runMemory();
      } else if (moduleName === "deadlock" && data.deadlock) {
        this.dlState.pids = data.deadlock.process_ids;
        this.dlState.rids = data.deadlock.resource_ids;
        this.dlState.available = data.deadlock.available;
        this.dlState.alloc = data.deadlock.allocation;
        this.dlState.max = data.deadlock.max_demand;
        document.getElementById("dl-avail-input").value = this.dlState.available.join(", ");
        this.renderDeadlockMatrix();
        if (data.deadlock.sample_request) {
          const req = data.deadlock.sample_request;
          document.getElementById("dl-req-pid").value = req.pid;
          document.getElementById("dl-req-vector").value = req.resources.join(", ");
        }
        this.runDeadlock();
      } else if (moduleName === "disk" && data.disk) {
        document.getElementById("disk-requests-input").value = data.disk.requests.join(", ");
        document.getElementById("disk-head-slider").value = data.disk.initial_head;
        document.getElementById("disk-head-val").textContent = data.disk.initial_head;
        this.runDisk();
      }
    } catch (err) {
      console.error("Error loading preset:", err);
    }
  }

  // =========================================================================
  // MODULE 1: CPU SCHEDULING
  // =========================================================================
  onCpuAlgoChange() {
    const algo = document.getElementById("cpu-algo").value;
    const qGroup = document.getElementById("cpu-quantum-group");
    qGroup.style.display = algo === "rr" ? "block" : "none";
  }

  onQuantumChange(val) {
    document.getElementById("cpu-quantum-val").textContent = val;
  }

  renderCpuTable() {
    const tbody = document.getElementById("cpu-processes-body");
    tbody.innerHTML = "";
    this.cpuProcesses.forEach((p, idx) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><input type="text" class="table-input" value="${p.pid}" data-idx="${idx}" data-field="pid" style="width: 50px;"></td>
        <td><input type="number" class="table-input" value="${p.arrival_time}" min="0" data-idx="${idx}" data-field="arrival_time" style="width: 60px;"></td>
        <td><input type="number" class="table-input" value="${p.burst_time}" min="1" data-idx="${idx}" data-field="burst_time" style="width: 60px;"></td>
        <td><input type="number" class="table-input" value="${p.priority}" min="1" data-idx="${idx}" data-field="priority" style="width: 60px;"></td>
        <td><button class="btn btn-danger btn-sm" onclick="app.removeCpuProcessRow(${idx})">X</button></td>
      `;
      tbody.appendChild(tr);
    });

    tbody.querySelectorAll("input").forEach((inp) => {
      inp.addEventListener("change", (e) => {
        const idx = parseInt(e.target.dataset.idx);
        const field = e.target.dataset.field;
        const val = e.target.type === "number" ? parseInt(e.target.value) || 0 : e.target.value;
        this.cpuProcesses[idx][field] = val;
      });
    });
  }

  addCpuProcessRow() {
    const nextPid = `P${this.cpuProcesses.length + 1}`;
    this.cpuProcesses.push({ pid: nextPid, arrival_time: 0, burst_time: 4, priority: 1 });
    this.renderCpuTable();
  }

  removeCpuProcessRow(idx) {
    if (this.cpuProcesses.length <= 1) return;
    this.cpuProcesses.splice(idx, 1);
    this.renderCpuTable();
  }

  async runCpu() {
    const algo = document.getElementById("cpu-algo").value;
    const quantum = parseInt(document.getElementById("cpu-quantum-slider").value) || 2;

    const payload = {
      algorithm: algo,
      quantum: quantum,
      processes: this.cpuProcesses,
    };

    try {
      const res = await fetch("/api/cpu/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json();
        alert("CPU Simulation Error: " + (errData.error || res.statusText));
        return;
      }

      const data = await res.json();

      if (data.mode === "all") {
        this.renderCpuAllComparison(data.results);
      } else {
        document.getElementById("cpu-details-card").style.display = "block";
        document.getElementById("cpu-comparison-card").style.display = "none";
        this.renderCpuSingleResult(data);
      }
    } catch (err) {
      console.error("Failed to run CPU simulation:", err);
    }
  }

  renderCpuSingleResult(data) {
    // Render KPIs
    document.getElementById("kpi-cpu-wt").textContent = data.metrics.avg_waiting_time;
    document.getElementById("kpi-cpu-tat").textContent = data.metrics.avg_turnaround_time;
    document.getElementById("kpi-cpu-rt").textContent = data.metrics.avg_response_time;
    document.getElementById("kpi-cpu-util").textContent = `${data.metrics.cpu_utilization}%`;
    document.getElementById("cpu-gantt-total-time").textContent = `Total Execution Time: ${data.metrics.total_execution_time}`;
    document.getElementById("cpu-algo-badge").textContent = data.algorithm.toUpperCase();

    // Render Detailed Table
    const tbody = document.getElementById("cpu-results-body");
    tbody.innerHTML = "";
    data.processes.forEach((p) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td style="font-weight: 700; color: #ffffff;">${p.pid}</td>
        <td class="num">${p.arrival_time}</td>
        <td class="num">${p.burst_time}</td>
        <td class="num">${p.priority}</td>
        <td class="num">${p.start_time !== null ? p.start_time : "-"}</td>
        <td class="num" style="font-weight: 600;">${p.completion_time}</td>
        <td class="num">${p.turnaround_time}</td>
        <td class="num">${p.waiting_time}</td>
        <td class="num">${p.response_time}</td>
      `;
      tbody.appendChild(tr);
    });

    // Render Vector SVG Gantt Chart
    this.renderSvgGantt(data.timeline, data.metrics.total_execution_time);
  }

  renderCpuAllComparison(results) {
    document.getElementById("cpu-details-card").style.display = "none";
    document.getElementById("cpu-comparison-card").style.display = "block";

    const tbody = document.getElementById("cpu-comparison-body");
    tbody.innerHTML = "";

    const algorithms = [
      { key: "fcfs", name: "First-Come, First-Served (FCFS)" },
      { key: "sjf", name: "Shortest Job First (SJF)" },
      { key: "rr", name: "Round Robin" },
      { key: "priority", name: "Priority Scheduling" },
    ];

    algorithms.forEach((a) => {
      const r = results[a.key];
      if (!r) return;
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td style="font-weight: 700; color: #ffffff;">${r.algorithm}</td>
        <td class="num">${r.metrics.avg_waiting_time}</td>
        <td class="num">${r.metrics.avg_turnaround_time}</td>
        <td class="num">${r.metrics.avg_response_time}</td>
        <td class="num">${r.metrics.total_execution_time}</td>
        <td class="num">${r.metrics.cpu_utilization}%</td>
      `;
      tbody.appendChild(tr);
    });

    // Also render Gantt for first algorithm (FCFS) by default
    if (results.fcfs) {
      this.renderSvgGantt(results.fcfs.timeline, results.fcfs.metrics.total_execution_time);
      document.getElementById("kpi-cpu-wt").textContent = results.fcfs.metrics.avg_waiting_time;
      document.getElementById("kpi-cpu-tat").textContent = results.fcfs.metrics.avg_turnaround_time;
      document.getElementById("kpi-cpu-rt").textContent = results.fcfs.metrics.avg_response_time;
      document.getElementById("kpi-cpu-util").textContent = `${results.fcfs.metrics.cpu_utilization}%`;
    }
  }

  renderSvgGantt(timeline, totalTime) {
    const svg = document.getElementById("cpu-gantt-svg");
    svg.innerHTML = "";
    if (!timeline || timeline.length === 0 || totalTime <= 0) return;

    const width = 800;
    const height = 90;
    const barHeight = 44;
    const barY = 16;
    const leftPad = 10;
    const rightPad = 10;
    const chartWidth = width - leftPad - rightPad;

    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.setAttribute("preserveAspectRatio", "none");

    // Definitions for hatched pattern (IDLE)
    const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
    defs.innerHTML = `
      <pattern id="idleHatch" width="10" height="10" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
        <line x1="0" y1="0" x2="0" y2="10" stroke="#3f3f46" stroke-width="2" />
      </pattern>
    `;
    svg.appendChild(defs);

    // Baseline ruler line
    const ruler = document.createElementNS("http://www.w3.org/2000/svg", "line");
    ruler.setAttribute("x1", leftPad);
    ruler.setAttribute("y1", barY + barHeight);
    ruler.setAttribute("x2", width - rightPad);
    ruler.setAttribute("y2", barY + barHeight);
    ruler.setAttribute("stroke", "#27272a");
    ruler.setAttribute("stroke-width", "1");
    svg.appendChild(ruler);

    timeline.forEach((seg, i) => {
      const segStart = seg.start;
      const segEnd = seg.end;
      const segDuration = seg.duration;
      const x = leftPad + (segStart / totalTime) * chartWidth;
      const w = Math.max((segDuration / totalTime) * chartWidth, 2);

      const isIdle = seg.pid === "IDLE";

      // Rect
      const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
      rect.setAttribute("x", x);
      rect.setAttribute("y", barY);
      rect.setAttribute("width", w);
      rect.setAttribute("height", barHeight);
      rect.setAttribute("fill", isIdle ? "url(#idleHatch)" : "#18181b");
      rect.setAttribute("stroke", "#3f3f46");
      rect.setAttribute("stroke-width", "1");
      svg.appendChild(rect);

      // Label (PID)
      if (w > 20) {
        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", x + w / 2);
        text.setAttribute("y", barY + barHeight / 2 + 4);
        text.setAttribute("fill", isIdle ? "#71717a" : "#ffffff");
        text.setAttribute("font-family", "ui-monospace, monospace");
        text.setAttribute("font-size", "11");
        text.setAttribute("font-weight", "600");
        text.setAttribute("text-anchor", "middle");
        text.textContent = seg.pid;
        svg.appendChild(text);
      }

      // Start tick text
      const tickText = document.createElementNS("http://www.w3.org/2000/svg", "text");
      tickText.setAttribute("x", x);
      tickText.setAttribute("y", barY + barHeight + 16);
      tickText.setAttribute("fill", "#a1a1aa");
      tickText.setAttribute("font-family", "ui-monospace, monospace");
      tickText.setAttribute("font-size", "10");
      tickText.setAttribute("text-anchor", "middle");
      tickText.textContent = segStart;
      svg.appendChild(tickText);

      // If last segment, draw end tick
      if (i === timeline.length - 1) {
        const endText = document.createElementNS("http://www.w3.org/2000/svg", "text");
        endText.setAttribute("x", x + w);
        endText.setAttribute("y", barY + barHeight + 16);
        endText.setAttribute("fill", "#a1a1aa");
        endText.setAttribute("font-family", "ui-monospace, monospace");
        endText.setAttribute("font-size", "10");
        endText.setAttribute("text-anchor", "middle");
        endText.textContent = segEnd;
        svg.appendChild(endText);
      }
    });
  }

  // =========================================================================
  // MODULE 2: MEMORY MANAGEMENT
  // =========================================================================
  renderMemoryReqTable() {
    const tbody = document.getElementById("mem-requests-body");
    tbody.innerHTML = "";
    this.memRequests.forEach((req, idx) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><input type="text" class="table-input" value="${req.pid}" data-idx="${idx}" data-field="pid" style="width: 60px;"></td>
        <td><input type="number" class="table-input" value="${req.size}" min="1" data-idx="${idx}" data-field="size"></td>
        <td><button class="btn btn-danger btn-sm" onclick="app.removeMemoryReqRow(${idx})">X</button></td>
      `;
      tbody.appendChild(tr);
    });

    tbody.querySelectorAll("input").forEach((inp) => {
      inp.addEventListener("change", (e) => {
        const idx = parseInt(e.target.dataset.idx);
        const field = e.target.dataset.field;
        const val = field === "size" ? parseInt(e.target.value) || 0 : e.target.value;
        this.memRequests[idx][field] = val;
      });
    });
  }

  addMemoryReqRow() {
    const nextPid = `P${this.memRequests.length + 1}`;
    this.memRequests.push({ pid: nextPid, size: 150 });
    this.renderMemoryReqTable();
  }

  removeMemoryReqRow(idx) {
    if (this.memRequests.length <= 1) return;
    this.memRequests.splice(idx, 1);
    this.renderMemoryReqTable();
  }

  async runMemory() {
    const algo = document.getElementById("mem-algo").value;
    const blocksStr = document.getElementById("mem-blocks-input").value;
    const blocks = blocksStr.split(",").map((s) => parseInt(s.trim())).filter((n) => !isNaN(n) && n > 0);

    const requests = this.memRequests.map((r) => [r.pid, r.size]);

    const payload = {
      algorithm: algo,
      blocks: blocks,
      requests: requests,
    };

    try {
      const res = await fetch("/api/memory/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json();
        alert("Memory Error: " + (errData.error || res.statusText));
        return;
      }

      const data = await res.json();

      if (data.mode === "all") {
        document.getElementById("mem-allocations-card").style.display = "none";
        document.getElementById("mem-comparison-card").style.display = "block";
        this.renderMemoryComparison(data.results);
      } else {
        document.getElementById("mem-allocations-card").style.display = "block";
        document.getElementById("mem-comparison-card").style.display = "none";
        this.renderMemorySingleResult(data);
      }
    } catch (err) {
      console.error("Failed to run memory simulation:", err);
    }
  }

  renderMemorySingleResult(data) {
    const successRate = ((data.successful_allocations / (data.successful_allocations + data.failed_allocations)) * 100).toFixed(1);
    document.getElementById("kpi-mem-success").textContent = `${data.successful_allocations}/${data.successful_allocations + data.failed_allocations} (${successRate}%)`;
    document.getElementById("kpi-mem-util").textContent = `${data.memory_utilization}%`;
    document.getElementById("kpi-mem-extfrag").textContent = `${data.external_fragmentation_kb} KB`;
    document.getElementById("kpi-mem-intfrag").innerHTML = `0<span class="kpi-unit">KB (Split)</span>`;
    document.getElementById("mem-total-capacity").textContent = `Total: ${data.total_memory_kb} KB`;
    document.getElementById("mem-algo-badge").textContent = data.algorithm.toUpperCase();

    // Render Proportional Memory Map Bar
    this.renderMemoryMap(data.allocations, data.remaining_blocks, data.total_memory_kb);

    // Render Allocations Breakdown Table
    const tbody = document.getElementById("mem-allocations-body");
    tbody.innerHTML = "";

    data.allocations.forEach((item) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>Block #${item.block_id}</td>
        <td class="num">${item.original_block_size} KB</td>
        <td style="font-weight: 700; color: #ffffff;">${item.process_id}</td>
        <td class="num">${item.requested_size} KB</td>
        <td class="num" style="color: #ffffff; font-weight: 600;">${item.allocated_size} KB</td>
        <td class="num">0 KB</td>
        <td><span class="badge badge-white">ALLOCATED</span></td>
      `;
      tbody.appendChild(tr);
    });

    data.unallocated_processes.forEach((pid) => {
      const req = this.memRequests.find((r) => r.pid === pid);
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>-</td>
        <td class="num">-</td>
        <td style="font-weight: 700; color: #f87171;">${pid}</td>
        <td class="num">${req ? req.size : "-"} KB</td>
        <td class="num">-</td>
        <td class="num">-</td>
        <td><span class="badge badge-danger">FAILED (NO FIT)</span></td>
      `;
      tbody.appendChild(tr);
    });
  }

  renderMemoryMap(allocations, remainingBlocks, totalMem) {
    const bar = document.getElementById("memory-map-bar");
    bar.innerHTML = "";
    if (totalMem <= 0) return;

    allocations.forEach((alloc) => {
      const pct = (alloc.allocated_size / totalMem) * 100;
      const seg = document.createElement("div");
      seg.className = "memory-segment allocated";
      seg.style.width = `${pct}%`;
      seg.title = `Block #${alloc.block_id}: ${alloc.process_id} (${alloc.allocated_size} KB)`;
      seg.innerHTML = `<span>${alloc.process_id}</span><span style="font-size: 9px; opacity: 0.8;">${alloc.allocated_size}K</span>`;
      bar.appendChild(seg);
    });

    remainingBlocks.forEach((b) => {
      if (b.is_free && b.size > 0) {
        const pct = (b.size / totalMem) * 100;
        const seg = document.createElement("div");
        seg.className = "memory-segment free";
        seg.style.width = `${pct}%`;
        seg.title = `Free Block #${b.block_id}: ${b.size} KB Available`;
        seg.innerHTML = `<span>FREE</span><span style="font-size: 9px; opacity: 0.8;">${b.size}K</span>`;
        bar.appendChild(seg);
      }
    });
  }

  renderMemoryComparison(results) {
    const tbody = document.getElementById("mem-comparison-body");
    tbody.innerHTML = "";
    results.forEach((r) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td style="font-weight: 700; color: #ffffff;">${r.algorithm}</td>
        <td class="num">${r.successful_allocations}/${r.successful_allocations + r.failed_allocations}</td>
        <td class="num">${r.total_allocated_kb} KB</td>
        <td class="num">${r.total_free_memory_kb} KB</td>
        <td class="num">${r.external_fragmentation_kb} KB</td>
        <td class="num">${r.memory_utilization}%</td>
      `;
      tbody.appendChild(tr);
    });

    if (results.length > 0) {
      this.renderMemorySingleResult(results[0]);
    }
  }

  // =========================================================================
  // MODULE 3: DEADLOCK AVOIDANCE
  // =========================================================================
  renderDeadlockMatrix() {
    const tbody = document.getElementById("dl-matrix-body");
    tbody.innerHTML = "";

    this.dlState.pids.forEach((pid, i) => {
      const tr = document.createElement("tr");
      const allocRow = this.dlState.alloc[i] || [0, 0, 0];
      const maxRow = this.dlState.max[i] || [0, 0, 0];

      tr.innerHTML = `
        <td style="font-weight: 700; color: #ffffff;">${pid}</td>
        <td><input type="number" min="0" class="table-input" value="${allocRow[0]}" data-p="${i}" data-type="alloc" data-r="0"></td>
        <td><input type="number" min="0" class="table-input" value="${allocRow[1]}" data-p="${i}" data-type="alloc" data-r="1"></td>
        <td><input type="number" min="0" class="table-input" value="${allocRow[2]}" data-p="${i}" data-type="alloc" data-r="2"></td>
        <td><input type="number" min="0" class="table-input" value="${maxRow[0]}" data-p="${i}" data-type="max" data-r="0"></td>
        <td><input type="number" min="0" class="table-input" value="${maxRow[1]}" data-p="${i}" data-type="max" data-r="1"></td>
        <td><input type="number" min="0" class="table-input" value="${maxRow[2]}" data-p="${i}" data-type="max" data-r="2"></td>
      `;
      tbody.appendChild(tr);
    });

    tbody.querySelectorAll("input").forEach((inp) => {
      inp.addEventListener("change", (e) => {
        const p = parseInt(e.target.dataset.p);
        const type = e.target.dataset.type;
        const r = parseInt(e.target.dataset.r);
        const val = parseInt(e.target.value) || 0;
        if (type === "alloc") {
          this.dlState.alloc[p][r] = val;
        } else {
          this.dlState.max[p][r] = val;
        }
      });
    });
  }

  getDeadlockPayload(requestObj = null) {
    const availStr = document.getElementById("dl-avail-input").value;
    const avail = availStr.split(",").map((s) => parseInt(s.trim())).filter((n) => !isNaN(n));

    const payload = {
      process_ids: this.dlState.pids,
      resource_ids: this.dlState.rids,
      available: avail,
      allocation: this.dlState.alloc,
      max_demand: this.dlState.max,
    };

    if (requestObj) {
      payload.request = requestObj;
    }
    return payload;
  }

  async runDeadlock() {
    const payload = this.getDeadlockPayload();

    try {
      const res = await fetch("/api/deadlock/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json();
        alert("Deadlock Error: " + (errData.error || res.statusText));
        return;
      }

      const data = await res.json();
      this.renderDeadlockResult(data);
    } catch (err) {
      console.error("Failed to run deadlock check:", err);
    }
  }

  async runDeadlockRequest() {
    const reqPid = document.getElementById("dl-req-pid").value;
    const reqVectorStr = document.getElementById("dl-req-vector").value;
    const reqVector = reqVectorStr.split(",").map((s) => parseInt(s.trim())).filter((n) => !isNaN(n));

    const payload = this.getDeadlockPayload({
      pid: reqPid,
      resources: reqVector,
    });

    try {
      const res = await fetch("/api/deadlock/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json();
        alert("Deadlock Request Error: " + (errData.error || res.statusText));
        return;
      }

      const data = await res.json();
      this.renderDeadlockResult(data);
      this.renderDeadlockRequestOutcome(data.request_evaluation);
    } catch (err) {
      console.error("Failed to evaluate deadlock request:", err);
    }
  }

  renderDeadlockResult(data) {
    // Safety status KPI
    const badge = document.getElementById("dl-status-badge");
    const val = document.getElementById("dl-status-val");
    const desc = document.getElementById("dl-status-desc");

    if (data.is_safe) {
      badge.className = "badge badge-white";
      badge.textContent = "SAFE";
      val.textContent = "SAFE STATE";
      desc.textContent = "System is in a safe execution state. No deadlock can occur under optimal scheduling.";
    } else {
      badge.className = "badge badge-danger";
      badge.textContent = "UNSAFE";
      val.textContent = "DEADLOCK HAZARD";
      desc.textContent = "System cannot guarantee safety. Unsafe state detected — deadlock potential!";
    }

    // Sequence flow pills
    const flowContainer = document.getElementById("dl-sequence-flow");
    flowContainer.innerHTML = "";
    if (data.is_safe && data.safe_sequence && data.safe_sequence.length > 0) {
      data.safe_sequence.forEach((pid, i) => {
        const node = document.createElement("span");
        node.className = "sequence-node";
        node.textContent = pid;
        flowContainer.appendChild(node);

        if (i < data.safe_sequence.length - 1) {
          const arrow = document.createElement("span");
          arrow.className = "sequence-arrow";
          arrow.textContent = "→";
          flowContainer.appendChild(arrow);
        }
      });
    } else {
      flowContainer.innerHTML = `<span style="color: #f87171; font-family: var(--font-mono); font-size: 12px;">No safe execution sequence exists for current state.</span>`;
    }

    // Need Matrix table
    const needBody = document.getElementById("dl-need-body");
    needBody.innerHTML = "";
    this.dlState.pids.forEach((pid, i) => {
      const row = data.need[i] || [0, 0, 0];
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td style="font-weight: 700; color: #ffffff;">${pid}</td>
        <td class="num">${row[0]}</td>
        <td class="num">${row[1]}</td>
        <td class="num">${row[2]}</td>
      `;
      needBody.appendChild(tr);
    });

    // Steps container
    const stepsDiv = document.getElementById("dl-steps-container");
    stepsDiv.innerHTML = "";
    if (data.steps && data.steps.length > 0) {
      data.steps.forEach((st) => {
        const stepCard = document.createElement("div");
        stepCard.className = "step-card";
        stepCard.textContent = st;
        stepsDiv.appendChild(stepCard);
      });
    }
  }

  renderDeadlockRequestOutcome(outcome) {
    const card = document.getElementById("dl-request-outcome-card");
    if (!outcome) {
      card.style.display = "none";
      return;
    }
    card.style.display = "block";

    const badge = document.getElementById("dl-req-decision-badge");
    badge.className = outcome.decision === "GRANTED" ? "badge badge-white" : "badge badge-danger";
    badge.textContent = outcome.decision;

    document.getElementById("dl-req-detail-msg").textContent = outcome.detail;

    const postSeqDiv = document.getElementById("dl-req-post-seq");
    postSeqDiv.innerHTML = "";
    if (outcome.post_sequence && outcome.post_sequence.length > 0) {
      postSeqDiv.innerHTML = `<span style="font-size: 11px; color: var(--text-muted); margin-right: 8px;">POST-REQUEST SAFE SEQUENCE:</span>`;
      outcome.post_sequence.forEach((pid, i) => {
        const node = document.createElement("span");
        node.className = "sequence-node";
        node.textContent = pid;
        postSeqDiv.appendChild(node);
        if (i < outcome.post_sequence.length - 1) {
          const arrow = document.createElement("span");
          arrow.className = "sequence-arrow";
          arrow.textContent = "→";
          postSeqDiv.appendChild(arrow);
        }
      });
    }
  }

  // =========================================================================
  // MODULE 4: DISK SCHEDULING
  // =========================================================================
  onDiskHeadChange(val) {
    document.getElementById("disk-head-val").textContent = val;
  }

  async runDisk() {
    const algo = document.getElementById("disk-algo").value;
    const head = parseInt(document.getElementById("disk-head-slider").value) || 53;
    const dir = document.getElementById("disk-direction").value;
    const reqStr = document.getElementById("disk-requests-input").value;
    const reqs = reqStr.split(",").map((s) => parseInt(s.trim())).filter((n) => !isNaN(n));

    const payload = {
      algorithm: algo,
      initial_head: head,
      direction: dir,
      requests: reqs,
      total_cylinders: 200,
    };

    try {
      const res = await fetch("/api/disk/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json();
        alert("Disk Error: " + (errData.error || res.statusText));
        return;
      }

      const data = await res.json();

      if (data.mode === "all") {
        document.getElementById("disk-steps-card").style.display = "none";
        document.getElementById("disk-comparison-card").style.display = "block";
        this.renderDiskComparison(data.results);
      } else {
        document.getElementById("disk-steps-card").style.display = "block";
        document.getElementById("disk-comparison-card").style.display = "none";
        this.renderDiskSingleResult(data);
      }
    } catch (err) {
      console.error("Failed to run disk simulation:", err);
    }
  }

  renderDiskSingleResult(data) {
    document.getElementById("kpi-disk-thm").textContent = data.total_head_movement;
    document.getElementById("kpi-disk-avg").textContent = data.average_head_movement;
    document.getElementById("kpi-disk-serviced").textContent = data.requests_serviced;
    document.getElementById("disk-algo-badge").textContent = data.algorithm.toUpperCase();
    document.getElementById("disk-plot-algo-label").textContent = `Algorithm: ${data.algorithm.toUpperCase()}`;

    // Render Steps Table
    const tbody = document.getElementById("disk-steps-body");
    tbody.innerHTML = "";
    const seq = data.seek_sequence;
    for (let i = 1; i < seq.length; i++) {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>Step ${i}</td>
        <td class="num">${seq[i - 1]}</td>
        <td class="num" style="font-weight: 700; color: #ffffff;">${seq[i]}</td>
        <td class="num">${data.step_movements[i - 1]} cyl</td>
      `;
      tbody.appendChild(tr);
    }

    // Render Vector SVG Trajectory Plot
    this.renderSvgDiskTrajectory(data.seek_sequence, data.total_cylinders || 200);
  }

  renderDiskComparison(results) {
    const tbody = document.getElementById("disk-comparison-body");
    tbody.innerHTML = "";

    results.forEach((r) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td style="font-weight: 700; color: #ffffff;">${r.algorithm}</td>
        <td class="num">${r.total_head_movement} cyl</td>
        <td class="num">${r.average_head_movement}</td>
        <td class="num">${r.requests_serviced}</td>
      `;
      tbody.appendChild(tr);
    });

    if (results.length > 0) {
      this.renderDiskSingleResult(results[0]);
    }
  }

  renderSvgDiskTrajectory(sequence, totalCylinders) {
    const svg = document.getElementById("disk-trajectory-svg");
    svg.innerHTML = "";
    if (!sequence || sequence.length <= 1) return;

    const width = 800;
    const height = 240;
    const topPad = 25;
    const bottomPad = 30;
    const leftPad = 45;
    const rightPad = 30;

    const plotW = width - leftPad - rightPad;
    const plotH = height - topPad - bottomPad;

    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.setAttribute("preserveAspectRatio", "none");

    const maxCyl = totalCylinders - 1; // 199

    // Y Axis Guidelines (0, 50, 100, 150, 199)
    const yTicks = [0, 50, 100, 150, 199];
    yTicks.forEach((cyl) => {
      const y = topPad + plotH - (cyl / maxCyl) * plotH;

      const gridLine = document.createElementNS("http://www.w3.org/2000/svg", "line");
      gridLine.setAttribute("x1", leftPad);
      gridLine.setAttribute("y1", y);
      gridLine.setAttribute("x2", width - rightPad);
      gridLine.setAttribute("y2", y);
      gridLine.setAttribute("stroke", "#1c1c20");
      gridLine.setAttribute("stroke-width", "1");
      svg.appendChild(gridLine);

      const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
      label.setAttribute("x", leftPad - 8);
      label.setAttribute("y", y + 4);
      label.setAttribute("fill", "#71717a");
      label.setAttribute("font-family", "ui-monospace, monospace");
      label.setAttribute("font-size", "10");
      label.setAttribute("text-anchor", "end");
      label.textContent = cyl;
      svg.appendChild(label);
    });

    // Compute point coordinates
    const points = sequence.map((cyl, step) => {
      const x = leftPad + (step / (sequence.length - 1)) * plotW;
      const y = topPad + plotH - (cyl / maxCyl) * plotH;
      return { x, y, cyl, step };
    });

    // Draw polyline connecting points
    const pointsStr = points.map((p) => `${p.x},${p.y}`).join(" ");
    const polyline = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
    polyline.setAttribute("points", pointsStr);
    polyline.setAttribute("fill", "none");
    polyline.setAttribute("stroke", "#ffffff");
    polyline.setAttribute("stroke-width", "2");
    svg.appendChild(polyline);

    // Draw markers & labels
    points.forEach((p, idx) => {
      // Step tick on X axis
      const stepLabel = document.createElementNS("http://www.w3.org/2000/svg", "text");
      stepLabel.setAttribute("x", p.x);
      stepLabel.setAttribute("y", height - 10);
      stepLabel.setAttribute("fill", "#71717a");
      stepLabel.setAttribute("font-family", "ui-monospace, monospace");
      stepLabel.setAttribute("font-size", "10");
      stepLabel.setAttribute("text-anchor", "middle");
      stepLabel.textContent = `S${idx}`;
      svg.appendChild(stepLabel);

      // Circle node
      const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circle.setAttribute("cx", p.x);
      circle.setAttribute("cy", p.y);
      circle.setAttribute("r", idx === 0 ? "5" : "3.5");
      circle.setAttribute("fill", idx === 0 ? "#ffffff" : "#000000");
      circle.setAttribute("stroke", "#ffffff");
      circle.setAttribute("stroke-width", "2");
      svg.appendChild(circle);

      // Cylinder text label above node
      const valText = document.createElementNS("http://www.w3.org/2000/svg", "text");
      valText.setAttribute("x", p.x);
      valText.setAttribute("y", p.y - 8);
      valText.setAttribute("fill", "#ffffff");
      valText.setAttribute("font-family", "ui-monospace, monospace");
      valText.setAttribute("font-size", "10");
      valText.setAttribute("font-weight", "600");
      valText.setAttribute("text-anchor", "middle");
      valText.textContent = p.cyl;
      svg.appendChild(valText);
    });
  }

  // =========================================================================
  // MODULE 6: BENCHMARKS
  // =========================================================================
  async loadBenchmarks() {
    try {
      const res = await fetch("/api/benchmarks");
      if (!res.ok) return;
      const data = await res.json();

      // CPU Table
      const cpuTbody = document.querySelector("#bm-cpu-table tbody");
      cpuTbody.innerHTML = "";
      (data.cpu_results || []).forEach((row) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td style="font-weight: 700; color: #ffffff;">${row.Algorithm}</td>
          <td class="num">${row["Avg Waiting Time"]}</td>
          <td class="num">${row["Avg Turnaround Time"]}</td>
          <td class="num">${row["Avg Response Time"]}</td>
          <td class="num">${row["Total Execution Time"]}</td>
          <td class="num">${row["CPU Utilization (%)"]}%</td>
        `;
        cpuTbody.appendChild(tr);
      });

      // Memory Table
      const memTbody = document.querySelector("#bm-memory-table tbody");
      memTbody.innerHTML = "";
      (data.memory_results || []).forEach((row) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td style="font-weight: 700; color: #ffffff;">${row.Algorithm}</td>
          <td class="num">${row["Allocation Success Rate (%)"]}%</td>
          <td class="num">${row["Total Allocated (KB)"]}</td>
          <td class="num">${row["Remaining Free Memory (KB)"]}</td>
          <td class="num">${row["External Fragmentation (KB)"]}</td>
          <td class="num">${row["Memory Utilization (%)"]}%</td>
        `;
        memTbody.appendChild(tr);
      });

      // Disk Table
      const diskTbody = document.querySelector("#bm-disk-table tbody");
      diskTbody.innerHTML = "";
      (data.disk_results || []).forEach((row) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td style="font-weight: 700; color: #ffffff;">${row.Algorithm}</td>
          <td class="num">${row["Total Head Movement (cylinders)"]} cyl</td>
          <td class="num">${row["Average Seek Distance (cyl/req)"]}</td>
          <td class="num">${row["Requests Serviced"]}</td>
        `;
        diskTbody.appendChild(tr);
      });

      // RR Sensitivity Table
      const rrTbody = document.querySelector("#bm-rr-table tbody");
      rrTbody.innerHTML = "";
      (data.rr_sensitivity || []).forEach((row) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td class="num" style="font-weight: 700; color: #ffffff;">q=${row["Time Quantum"]}</td>
          <td class="num">${row["Avg Waiting Time"]}</td>
          <td class="num">${row["Avg Turnaround Time"]}</td>
          <td class="num">${row["Avg Response Time"]}</td>
        `;
        rrTbody.appendChild(tr);
      });
    } catch (err) {
      console.error("Failed to load benchmarks:", err);
    }
  }

  // =========================================================================
  // MODULE 7: TESTS & LOGS
  // =========================================================================
  async loadTestCases() {
    try {
      const res = await fetch("/api/test-cases");
      if (!res.ok) return;
      const data = await res.json();
      this.allTestCases = data.cases || [];
      document.getElementById("tests-count-badge").textContent = `${this.allTestCases.length} CASES`;
      this.filterTestCases();
    } catch (err) {
      console.error("Failed to load test cases:", err);
    }
  }

  filterTestCases() {
    const query = document.getElementById("test-search-input").value.toLowerCase();
    const cat = document.getElementById("test-cat-filter").value;

    const tbody = document.getElementById("test-cases-body");
    tbody.innerHTML = "";

    const filtered = this.allTestCases.filter((tc) => {
      const matchCat = cat === "ALL" || tc.Category === cat;
      const matchQuery =
        !query ||
        tc["Test ID"].toLowerCase().includes(query) ||
        tc.Description.toLowerCase().includes(query) ||
        (tc.Category && tc.Category.toLowerCase().includes(query));
      return matchCat && matchQuery;
    });

    filtered.forEach((tc) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td style="font-weight: 700; color: #ffffff;">${tc["Test ID"]}</td>
        <td><span class="badge badge-outline">${tc.Category}</span></td>
        <td style="color: var(--text-secondary);">${tc.Description}</td>
        <td><span class="badge badge-white">PASS</span></td>
      `;
      tbody.appendChild(tr);
    });
  }

  async loadLogs() {
    const level = document.getElementById("log-level-filter").value;
    const count = document.getElementById("log-count-select").value;

    try {
      const res = await fetch(`/api/logs?count=${count}&level=${level}`);
      if (!res.ok) return;
      const data = await res.json();

      const terminal = document.getElementById("log-terminal-output");
      terminal.innerHTML = "";

      if (!data.logs || data.logs.length === 0) {
        terminal.innerHTML = `<div class="log-line" style="color: #71717a;">No log entries found.</div>`;
        return;
      }

      data.logs.forEach((line) => {
        const div = document.createElement("div");
        div.className = "log-line";
        if (line.includes("[ERROR]")) div.classList.add("log-error");
        else if (line.includes("[WARNING]")) div.classList.add("log-warning");
        else div.classList.add("log-info");
        div.textContent = line;
        terminal.appendChild(div);
      });

      // Scroll to bottom
      terminal.scrollTop = terminal.scrollHeight;
    } catch (err) {
      console.error("Failed to load logs:", err);
    }
  }
}

// Initialize application on DOM ready
const app = new OSSimulatorApp();
document.addEventListener("DOMContentLoaded", () => {
  app.init();
});
