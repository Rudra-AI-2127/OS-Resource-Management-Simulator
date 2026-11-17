/**
 * Client-Side Simulation Engine for GitHub Pages & Offline Execution
 * Implements 100% compliant OS algorithms mirroring Python backend.
 */

const CLIENT_PRESETS = {
  normal: {
    cpu: [
      { pid: "P1", arrival_time: 0, burst_time: 5, priority: 2 },
      { pid: "P2", arrival_time: 1, burst_time: 3, priority: 1 },
      { pid: "P3", arrival_time: 2, burst_time: 8, priority: 4 },
      { pid: "P4", arrival_time: 3, burst_time: 2, priority: 3 }
    ],
    memory: {
      blocks: [100, 500, 200, 300, 600],
      requests: [["P1", 212], ["P2", 417], ["P3", 112], ["P4", 426]]
    },
    deadlock: {
      process_ids: ["P0", "P1", "P2", "P3", "P4"],
      resource_ids: ["A", "B", "C"],
      available: [3, 3, 2],
      allocation: [
        [0, 1, 0],
        [2, 0, 0],
        [3, 0, 2],
        [2, 1, 1],
        [0, 0, 2]
      ],
      max_demand: [
        [7, 5, 3],
        [3, 2, 2],
        [9, 0, 2],
        [2, 2, 2],
        [4, 3, 3]
      ],
      sample_request: { pid: "P1", resources: [1, 0, 2] }
    },
    disk: {
      requests: [98, 183, 37, 122, 14, 124, 65, 67],
      initial_head: 53
    }
  },
  small: {
    cpu: [
      { pid: "P1", arrival_time: 0, burst_time: 3, priority: 1 },
      { pid: "P2", arrival_time: 1, burst_time: 2, priority: 2 }
    ],
    memory: {
      blocks: [200, 400],
      requests: [["P1", 150], ["P2", 350]]
    },
    deadlock: {
      process_ids: ["P0", "P1"],
      resource_ids: ["R1", "R2"],
      available: [1, 2],
      allocation: [[1, 0], [0, 1]],
      max_demand: [[2, 2], [1, 3]],
      sample_request: { pid: "P1", resources: [1, 0] }
    },
    disk: {
      requests: [25, 75, 120],
      initial_head: 53
    }
  },
  large: {
    cpu: [
      { pid: "P1", arrival_time: 0, burst_time: 10, priority: 3 },
      { pid: "P2", arrival_time: 1, burst_time: 4, priority: 1 },
      { pid: "P3", arrival_time: 2, burst_time: 6, priority: 4 },
      { pid: "P4", arrival_time: 3, burst_time: 3, priority: 2 },
      { pid: "P5", arrival_time: 4, burst_time: 8, priority: 5 },
      { pid: "P6", arrival_time: 6, burst_time: 2, priority: 1 },
      { pid: "P7", arrival_time: 8, burst_time: 5, priority: 3 },
      { pid: "P8", arrival_time: 9, burst_time: 7, priority: 2 }
    ],
    memory: {
      blocks: [50, 150, 300, 400, 600, 800, 250, 1024],
      requests: [
        ["P1", 120], ["P2", 280], ["P3", 450], ["P4", 90],
        ["P5", 600], ["P6", 310], ["P7", 750], ["P8", 150]
      ]
    },
    deadlock: {
      process_ids: ["P0", "P1", "P2", "P3", "P4", "P5"],
      resource_ids: ["A", "B", "C", "D"],
      available: [2, 1, 0, 0],
      allocation: [
        [0, 0, 1, 2],
        [2, 0, 0, 0],
        [0, 0, 3, 4],
        [2, 3, 5, 4],
        [0, 3, 3, 2],
        [0, 0, 1, 4]
      ],
      max_demand: [
        [0, 0, 1, 2],
        [2, 7, 5, 0],
        [6, 6, 5, 6],
        [4, 3, 5, 6],
        [0, 6, 5, 2],
        [0, 6, 5, 6]
      ],
      sample_request: { pid: "P0", resources: [0, 0, 0, 0] }
    },
    disk: {
      requests: [15, 45, 85, 110, 135, 170, 195, 10, 55, 95, 140, 180, 30, 70, 125, 160],
      initial_head: 53
    }
  },
  edge: {
    cpu: [
      { pid: "P1", arrival_time: 0, burst_time: 4, priority: 4 },
      { pid: "P2", arrival_time: 0, burst_time: 4, priority: 3 },
      { pid: "P3", arrival_time: 0, burst_time: 4, priority: 2 },
      { pid: "P4", arrival_time: 0, burst_time: 4, priority: 1 }
    ],
    memory: {
      blocks: [100, 200, 300],
      requests: [["P1", 100], ["P2", 199], ["P3", 305]]
    },
    deadlock: {
      process_ids: ["P0", "P1", "P2"],
      resource_ids: ["A", "B", "C"],
      available: [1, 0, 0],
      allocation: [
        [1, 1, 0],
        [1, 0, 1],
        [0, 1, 1]
      ],
      max_demand: [
        [2, 1, 0],
        [2, 1, 1],
        [1, 2, 1]
      ],
      sample_request: { pid: "P1", resources: [1, 0, 0] }
    },
    disk: {
      requests: [0, 199, 50, 50, 1, 198],
      initial_head: 53
    }
  }
};

const SimEngine = {
  getPresets(tier) {
    const t = (tier || "normal").toLowerCase();
    return CLIENT_PRESETS[t] || CLIENT_PRESETS.normal;
  },

  // =========================================================================
  // CPU SCHEDULING
  // =========================================================================
  runCpu(data) {
    const rawProcs = data.processes || [];
    if (!rawProcs.length) throw new Error("Process list cannot be empty.");

    const algo = (data.algorithm || "fcfs").toLowerCase().trim();
    const quantum = parseInt(data.quantum) || 2;

    const runSingle = (name) => {
      let procs = rawProcs.map(p => ({
        pid: String(p.pid).trim(),
        arrival_time: parseInt(p.arrival_time) || 0,
        burst_time: parseInt(p.burst_time) || 1,
        priority: parseInt(p.priority) || 1,
        remaining_time: parseInt(p.burst_time) || 1,
        start_time: null,
        completion_time: null,
        waiting_time: null,
        turnaround_time: null,
        response_time: null
      }));

      let segments = [];
      let algoLabel = "";

      if (name === "fcfs") {
        algoLabel = "First-Come, First-Served (FCFS)";
        procs.sort((a, b) => a.arrival_time - b.arrival_time || a.pid.localeCompare(b.pid));
        let currentTime = 0;
        for (const p of procs) {
          if (currentTime < p.arrival_time) {
            segments.push({ pid: "IDLE", start: currentTime, end: p.arrival_time, duration: p.arrival_time - currentTime });
            currentTime = p.arrival_time;
          }
          const start = currentTime;
          p.start_time = start;
          p.response_time = start - p.arrival_time;
          currentTime += p.burst_time;
          p.completion_time = currentTime;
          p.turnaround_time = p.completion_time - p.arrival_time;
          p.waiting_time = p.turnaround_time - p.burst_time;
          p.remaining_time = 0;
          segments.push({ pid: p.pid, start, end: currentTime, duration: currentTime - start });
        }
      } else if (name === "sjf") {
        algoLabel = "Shortest Job First (SJF)";
        let remainingPool = [...procs];
        let completed = [];
        let currentTime = 0;

        while (remainingPool.length > 0) {
          const ready = remainingPool.filter(p => p.arrival_time <= currentTime);
          if (!ready.length) {
            const nextArrival = Math.min(...remainingPool.map(p => p.arrival_time));
            segments.push({ pid: "IDLE", start: currentTime, end: nextArrival, duration: nextArrival - currentTime });
            currentTime = nextArrival;
            continue;
          }
          ready.sort((a, b) => a.burst_time - b.burst_time || a.arrival_time - b.arrival_time || a.pid.localeCompare(b.pid));
          const selected = ready[0];
          remainingPool = remainingPool.filter(p => p !== selected);

          const start = currentTime;
          selected.start_time = start;
          selected.response_time = start - selected.arrival_time;
          currentTime += selected.burst_time;
          selected.completion_time = currentTime;
          selected.turnaround_time = selected.completion_time - selected.arrival_time;
          selected.waiting_time = selected.turnaround_time - selected.burst_time;
          selected.remaining_time = 0;

          segments.push({ pid: selected.pid, start, end: currentTime, duration: currentTime - start });
          completed.push(selected);
        }
        procs = completed;
      } else if (name === "priority") {
        algoLabel = "Priority Scheduling (Non-preemptive)";
        let remainingPool = [...procs];
        let completed = [];
        let currentTime = 0;

        while (remainingPool.length > 0) {
          const ready = remainingPool.filter(p => p.arrival_time <= currentTime);
          if (!ready.length) {
            const nextArrival = Math.min(...remainingPool.map(p => p.arrival_time));
            segments.push({ pid: "IDLE", start: currentTime, end: nextArrival, duration: nextArrival - currentTime });
            currentTime = nextArrival;
            continue;
          }
          // Lower priority number = higher priority
          ready.sort((a, b) => a.priority - b.priority || a.arrival_time - b.arrival_time || a.pid.localeCompare(b.pid));
          const selected = ready[0];
          remainingPool = remainingPool.filter(p => p !== selected);

          const start = currentTime;
          selected.start_time = start;
          selected.response_time = start - selected.arrival_time;
          currentTime += selected.burst_time;
          selected.completion_time = currentTime;
          selected.turnaround_time = selected.completion_time - selected.arrival_time;
          selected.waiting_time = selected.turnaround_time - selected.burst_time;
          selected.remaining_time = 0;

          segments.push({ pid: selected.pid, start, end: currentTime, duration: currentTime - start });
          completed.push(selected);
        }
        procs = completed;
      } else if (name === "rr" || name === "round_robin") {
        algoLabel = `Round Robin (q=${quantum})`;
        procs.sort((a, b) => a.arrival_time - b.arrival_time || a.pid.localeCompare(b.pid));
        let unvisited = [...procs];
        let readyQueue = [];
        let completed = [];
        let currentTime = 0;

        while (unvisited.length > 0 || readyQueue.length > 0) {
          while (unvisited.length > 0 && unvisited[0].arrival_time <= currentTime) {
            readyQueue.push(unvisited.shift());
          }

          if (!readyQueue.length) {
            const nextArrival = unvisited[0].arrival_time;
            segments.push({ pid: "IDLE", start: currentTime, end: nextArrival, duration: nextArrival - currentTime });
            currentTime = nextArrival;
            while (unvisited.length > 0 && unvisited[0].arrival_time <= currentTime) {
              readyQueue.push(unvisited.shift());
            }
          }

          const active = readyQueue.shift();
          if (active.start_time === null) {
            active.start_time = currentTime;
            active.response_time = currentTime - active.arrival_time;
          }

          const execDuration = Math.min(active.remaining_time, quantum);
          const start = currentTime;
          currentTime += execDuration;
          active.remaining_time -= execDuration;

          segments.push({ pid: active.pid, start, end: currentTime, duration: execDuration });

          while (unvisited.length > 0 && unvisited[0].arrival_time <= currentTime) {
            readyQueue.push(unvisited.shift());
          }

          if (active.remaining_time > 0) {
            readyQueue.push(active);
          } else {
            active.completion_time = currentTime;
            active.turnaround_time = active.completion_time - active.arrival_time;
            active.waiting_time = active.turnaround_time - active.burst_time;
            completed.push(active);
          }
        }
        completed.sort((a, b) => a.pid.localeCompare(b.pid));
        procs = completed;
      } else {
        throw new Error(`Unknown CPU algorithm: ${name}`);
      }

      const n = procs.length;
      const totalWt = procs.reduce((acc, p) => acc + p.waiting_time, 0);
      const totalTat = procs.reduce((acc, p) => acc + p.turnaround_time, 0);
      const totalRt = procs.reduce((acc, p) => acc + p.response_time, 0);
      const totalTime = segments.length ? segments[segments.length - 1].end : 0;
      const busyTime = segments.filter(s => s.pid !== "IDLE").reduce((acc, s) => acc + s.duration, 0);
      const cpuUtil = totalTime > 0 ? parseFloat(((busyTime / totalTime) * 100).toFixed(2)) : 0.0;

      const metrics = {
        avg_waiting_time: parseFloat((totalWt / n).toFixed(2)),
        avg_turnaround_time: parseFloat((totalTat / n).toFixed(2)),
        avg_response_time: parseFloat((totalRt / n).toFixed(2)),
        total_execution_time: totalTime,
        cpu_utilization: cpuUtil,
        total_processes: n
      };

      return {
        algorithm: algoLabel,
        processes: procs,
        timeline: segments,
        metrics: metrics
      };
    };

    if (algo === "all") {
      return {
        mode: "all",
        results: {
          fcfs: runSingle("fcfs"),
          sjf: runSingle("sjf"),
          rr: runSingle("rr"),
          priority: runSingle("priority")
        }
      };
    } else {
      const res = runSingle(algo);
      return { mode: "single", ...res };
    }
  },

  // =========================================================================
  // MEMORY MANAGEMENT
  // =========================================================================
  runMemory(data) {
    const rawBlocks = data.blocks || [];
    const rawReqs = data.requests || [];
    if (!rawBlocks.length) throw new Error("Memory blocks list cannot be empty.");
    if (!rawReqs.length) throw new Error("Memory requests list cannot be empty.");

    const algo = (data.algorithm || "all").toLowerCase().trim();

    const runSingleStrategy = (strategyName) => {
      let blocks = rawBlocks.map((sz, idx) => ({ block_id: idx + 1, size: parseInt(sz), is_free: true }));
      const totalMem = rawBlocks.reduce((a, b) => a + parseInt(b), 0);
      let allocations = [];
      let unallocated = [];

      for (const req of rawReqs) {
        const pid = String(req[0]);
        const reqSize = parseInt(req[1]);
        let candidateIdx = null;

        if (strategyName === "First Fit") {
          for (let i = 0; i < blocks.length; i++) {
            if (blocks[i].is_free && blocks[i].size >= reqSize) {
              candidateIdx = i;
              break;
            }
          }
        } else if (strategyName === "Best Fit") {
          let bestDiff = Infinity;
          for (let i = 0; i < blocks.length; i++) {
            if (blocks[i].is_free && blocks[i].size >= reqSize) {
              const diff = blocks[i].size - reqSize;
              if (diff < bestDiff) {
                bestDiff = diff;
                candidateIdx = i;
              }
            }
          }
        } else if (strategyName === "Worst Fit") {
          let worstDiff = -1;
          for (let i = 0; i < blocks.length; i++) {
            if (blocks[i].is_free && blocks[i].size >= reqSize) {
              const diff = blocks[i].size - reqSize;
              if (diff > worstDiff) {
                worstDiff = diff;
                candidateIdx = i;
              }
            }
          }
        }

        if (candidateIdx !== null) {
          const chosen = blocks[candidateIdx];
          const initialSz = chosen.size;
          const remainingSz = initialSz - reqSize;

          allocations.push({
            pid: pid,
            allocated_kb: reqSize,
            block_id: chosen.block_id,
            initial_block_kb: initialSz,
            remaining_block_kb: remainingSz,
            status: "Allocated"
          });

          if (remainingSz > 0) {
            chosen.size = remainingSz;
            chosen.is_free = true;
          } else {
            chosen.size = 0;
            chosen.is_free = false;
          }
        } else {
          unallocated.push(pid);
        }
      }

      const usedMem = allocations.reduce((acc, a) => acc + a.allocated_kb, 0);
      const freeMem = blocks.filter(b => b.is_free).reduce((acc, b) => acc + b.size, 0);
      const utilization = totalMem > 0 ? parseFloat(((usedMem / totalMem) * 100).toFixed(2)) : 0.0;

      let externalFrag = 0;
      if (unallocated.length > 0) {
        const reqMap = Object.fromEntries(rawReqs.map(r => [String(r[0]), parseInt(r[1])]));
        for (const uPid of unallocated) {
          if (freeMem >= reqMap[uPid]) {
            externalFrag = freeMem;
            break;
          }
        }
      }

      const remainingBlocks = blocks.filter(b => b.size > 0).map(b => ({
        block_id: b.block_id,
        remaining_kb: b.size,
        is_free: b.is_free
      }));

      return {
        algorithm: strategyName,
        allocations: allocations,
        unallocated_processes: unallocated,
        total_memory_kb: totalMem,
        total_allocated_kb: usedMem,
        total_free_memory_kb: freeMem,
        successful_allocations: allocations.length,
        failed_allocations: unallocated.length,
        memory_utilization: utilization,
        external_fragmentation_kb: externalFrag,
        internal_fragmentation_kb: 0,
        remaining_blocks: remainingBlocks
      };
    };

    if (algo === "all") {
      const ff = runSingleStrategy("First Fit");
      const bf = runSingleStrategy("Best Fit");
      const wf = runSingleStrategy("Worst Fit");
      const results = [ff, bf, wf];

      // Sort to find best algorithm (highest successful allocations, then lowest external fragmentation, then utilization)
      const sorted = [...results].sort((a, b) =>
        b.successful_allocations - a.successful_allocations ||
        a.external_fragmentation_kb - b.external_fragmentation_kb ||
        b.memory_utilization - a.memory_utilization
      );

      const comparisonTable = results.map(r => ({
        algorithm: r.algorithm,
        successful: r.successful_allocations,
        failed: r.failed_allocations,
        allocated_kb: r.total_allocated_kb,
        utilization_pct: r.memory_utilization,
        external_frag_kb: r.external_fragmentation_kb
      }));

      return {
        mode: "all",
        results: results,
        comparison_table: comparisonTable,
        best_algorithm: sorted[0].algorithm
      };
    } else {
      let strat = "First Fit";
      if (algo.includes("best")) strat = "Best Fit";
      else if (algo.includes("worst")) strat = "Worst Fit";
      const res = runSingleStrategy(strat);
      return { mode: "single", ...res };
    }
  },

  // =========================================================================
  // DEADLOCK AVOIDANCE (BANKER'S ALGORITHM)
  // =========================================================================
  runDeadlock(data) {
    const pids = data.process_ids || [];
    const rids = data.resource_ids || [];
    let avail = [...(data.available || [])].map(x => parseInt(x));
    let alloc = (data.allocation || []).map(row => row.map(x => parseInt(x)));
    let maxD = (data.max_demand || []).map(row => row.map(x => parseInt(x)));

    const n = pids.length;
    const m = rids.length;
    if (!n || !m) throw new Error("Deadlock matrices cannot be empty.");

    // Compute Need matrix = Max - Allocation
    let need = [];
    for (let i = 0; i < n; i++) {
      let row = [];
      for (let j = 0; j < m; j++) {
        row.push(maxD[i][j] - alloc[i][j]);
      }
      need.push(row);
    }

    // Safety algorithm runner
    const checkSafety = (workAvail, curAlloc, curNeed) => {
      let work = [...workAvail];
      let finish = new Array(n).fill(false);
      let seq = [];
      let steps = [];

      while (seq.length < n) {
        let found = false;
        for (let i = 0; i < n; i++) {
          if (!finish[i]) {
            let canAlloc = true;
            for (let j = 0; j < m; j++) {
              if (curNeed[i][j] > work[j]) {
                canAlloc = false;
                break;
              }
            }
            if (canAlloc) {
              const workBefore = [...work];
              for (let j = 0; j < m; j++) {
                work[j] += curAlloc[i][j];
              }
              finish[i] = true;
              seq.push(pids[i]);
              steps.push({
                step: seq.length,
                pid: pids[i],
                work_before: workBefore,
                need: curNeed[i],
                allocation: curAlloc[i],
                work_after: [...work]
              });
              found = true;
              break;
            }
          }
        }
        if (!found) return { is_safe: false, sequence: [], steps: steps };
      }
      return { is_safe: true, sequence: seq, steps: steps };
    };

    const safetyResult = checkSafety(avail, alloc, need);

    let response = {
      is_safe: safetyResult.is_safe,
      safe_sequence: safetyResult.sequence,
      need: need,
      available: avail,
      steps: safetyResult.steps
    };

    // Evaluate dynamic resource request if present
    const req = data.request;
    if (req && req.pid && req.resources) {
      const reqPid = String(req.pid).trim();
      const reqVec = req.resources.map(x => parseInt(x));
      const pIdx = pids.indexOf(reqPid);

      if (pIdx === -1) {
        response.request_evaluation = {
          pid: reqPid,
          request_vector: reqVec,
          decision: "DENIED",
          detail: `Process ${reqPid} not found in system state.`,
          post_safe: false,
          post_sequence: []
        };
      } else {
        // Condition 1: Request <= Need
        let exceedsNeed = false;
        for (let j = 0; j < m; j++) {
          if (reqVec[j] > need[pIdx][j]) {
            exceedsNeed = true;
            break;
          }
        }

        // Condition 2: Request <= Available
        let exceedsAvail = false;
        for (let j = 0; j < m; j++) {
          if (reqVec[j] > avail[j]) {
            exceedsAvail = true;
            break;
          }
        }

        if (exceedsNeed) {
          response.request_evaluation = {
            pid: reqPid,
            request_vector: reqVec,
            decision: "DENIED",
            detail: `Error: Process ${reqPid} has exceeded its maximum claim!`,
            post_safe: false,
            post_sequence: []
          };
        } else if (exceedsAvail) {
          response.request_evaluation = {
            pid: reqPid,
            request_vector: reqVec,
            decision: "DENIED",
            detail: `Process ${reqPid} must wait: Resources currently unavailable.`,
            post_safe: false,
            post_sequence: []
          };
        } else {
          // Speculative Allocation
          let tempAvail = [...avail];
          let tempAlloc = alloc.map(r => [...r]);
          let tempNeed = need.map(r => [...r]);

          for (let j = 0; j < m; j++) {
            tempAvail[j] -= reqVec[j];
            tempAlloc[pIdx][j] += reqVec[j];
            tempNeed[pIdx][j] -= reqVec[j];
          }

          const specSafety = checkSafety(tempAvail, tempAlloc, tempNeed);
          if (specSafety.is_safe) {
            response.request_evaluation = {
              pid: reqPid,
              request_vector: reqVec,
              decision: "GRANTED",
              detail: `Resource request granted for ${reqPid}. System remains in a SAFE state.`,
              post_safe: true,
              post_sequence: specSafety.sequence,
              post_available: tempAvail,
              post_allocation: tempAlloc,
              post_need: tempNeed
            };
          } else {
            response.request_evaluation = {
              pid: reqPid,
              request_vector: reqVec,
              decision: "DENIED",
              detail: `Request denied: Granting leads to an UNSAFE state (Deadlock hazard).`,
              post_safe: false,
              post_sequence: []
            };
          }
        }
      }
    }

    return response;
  },

  // =========================================================================
  // DISK SCHEDULING
  // =========================================================================
  runDisk(data) {
    const rawReqs = data.requests || [];
    if (!rawReqs.length) throw new Error("Disk cylinder requests list cannot be empty.");

    const requests = rawReqs.map(r => parseInt(r));
    const initialHead = parseInt(data.initial_head !== undefined ? data.initial_head : 53);
    const direction = String(data.direction || "up").toLowerCase().trim();
    const totalCylinders = parseInt(data.total_cylinders || 200);
    const algo = (data.algorithm || "all").toLowerCase().trim();

    const calcHeadMovement = (sequence, numReqs) => {
      if (sequence.length <= 1) return { total: 0, steps: [], avg: 0.0 };
      let steps = [];
      let total = 0;
      for (let i = 1; i < sequence.length; i++) {
        const diff = Math.abs(sequence[i] - sequence[i - 1]);
        steps.push(diff);
        total += diff;
      }
      const avg = numReqs > 0 ? parseFloat((total / numReqs).toFixed(2)) : 0.0;
      return { total, steps, avg };
    };

    const runSingleDisk = (name) => {
      let seq = [initialHead];
      let serviced = [];
      const numReqs = requests.length;

      if (name === "fcfs") {
        for (const r of requests) {
          seq.push(r);
          serviced.push(r);
        }
      } else if (name === "sstf") {
        let pending = [...requests];
        let cur = initialHead;
        while (pending.length > 0) {
          pending.sort((a, b) => Math.abs(a - cur) - Math.abs(b - cur) || a - b);
          const closest = pending.shift();
          seq.push(closest);
          serviced.push(closest);
          cur = closest;
        }
      } else if (name === "scan") {
        const upper = totalCylinders - 1;
        const lower = 0;
        const left = requests.filter(r => r < initialHead).sort((a, b) => a - b);
        const right = requests.filter(r => r >= initialHead).sort((a, b) => a - b);

        if (direction === "up") {
          for (const r of right) { seq.push(r); serviced.push(r); }
          if (left.length > 0) {
            if (seq[seq.length - 1] !== upper) seq.push(upper);
            for (let i = left.length - 1; i >= 0; i--) {
              seq.push(left[i]);
              serviced.push(left[i]);
            }
          }
        } else {
          for (let i = left.length - 1; i >= 0; i--) { seq.push(left[i]); serviced.push(left[i]); }
          if (right.length > 0) {
            if (seq[seq.length - 1] !== lower) seq.push(lower);
            for (const r of right) {
              seq.push(r);
              serviced.push(r);
            }
          }
        }
      } else if (name === "cscan" || name === "c-scan") {
        const upper = totalCylinders - 1;
        const lower = 0;
        const left = requests.filter(r => r < initialHead).sort((a, b) => a - b);
        const right = requests.filter(r => r >= initialHead).sort((a, b) => a - b);

        if (direction === "up") {
          for (const r of right) { seq.push(r); serviced.push(r); }
          if (left.length > 0) {
            if (seq[seq.length - 1] !== upper) seq.push(upper);
            seq.push(lower);
            for (const r of left) {
              if (seq[seq.length - 1] === lower && r === lower) {
                serviced.push(r);
                continue;
              }
              seq.push(r);
              serviced.push(r);
            }
          }
        } else {
          for (let i = left.length - 1; i >= 0; i--) { seq.push(left[i]); serviced.push(left[i]); }
          if (right.length > 0) {
            if (seq[seq.length - 1] !== lower) seq.push(lower);
            seq.push(upper);
            for (let i = right.length - 1; i >= 0; i--) {
              const r = right[i];
              if (seq[seq.length - 1] === upper && r === upper) {
                serviced.push(r);
                continue;
              }
              seq.push(r);
              serviced.push(r);
            }
          }
        }
      } else {
        throw new Error(`Unknown disk algorithm: ${name}`);
      }

      const { total, steps, avg } = calcHeadMovement(seq, numReqs);

      return {
        algorithm: name.toUpperCase(),
        initial_head: initialHead,
        seek_sequence: seq,
        service_sequence: serviced,
        step_movements: steps,
        total_head_movement: total,
        average_head_movement: avg,
        requests_serviced: numReqs,
        direction: direction,
        total_cylinders: totalCylinders
      };
    };

    if (algo === "all") {
      const fcfsRes = runSingleDisk("fcfs");
      const sstfRes = runSingleDisk("sstf");
      const scanRes = runSingleDisk("scan");
      const cscanRes = runSingleDisk("cscan");
      const results = [fcfsRes, sstfRes, scanRes, cscanRes];

      const sorted = [...results].sort((a, b) => a.total_head_movement - b.total_head_movement);

      const comparisonTable = results.map(r => ({
        algorithm: r.algorithm,
        total_head_movement: r.total_head_movement,
        average_head_movement: r.average_head_movement,
        requests_serviced: r.requests_serviced
      }));

      return {
        mode: "all",
        results: results,
        comparison_table: comparisonTable,
        best_algorithm: sorted[0].algorithm
      };
    } else {
      const res = runSingleDisk(algo);
      return { mode: "single", ...res };
    }
  }
};

if (typeof module !== "undefined" && module.exports) {
  module.exports = { SimEngine, CLIENT_PRESETS };
}
