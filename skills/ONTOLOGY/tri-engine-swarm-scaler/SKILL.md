---
name: tri-engine-swarm-scaler
domain: ONTOLOGY
version: 1.0.0
surfaces:
  - python
  - sqlite
description: Dynamic capacity scaler and load balancing engine for tri-engine agent swarms. Allocates worker node pools across SME perception ingestion, Em-Cubed Topos Omega modal verification, and Strategify Mesa Geo ABM simulation based on live Coherence Index and Epistemic Trust metrics. Use when managing multi-agent cluster resource allocation, dynamic workload rebalancing under degraded coherence, or scaling swarm workers.
purpose: Dynamically calculate and dispatch optimal worker allocations across SME, Em-Cubed, and Strategify swarm nodes.
dependencies: []
tags:
  - swarm-scaler
  - load-balancer
  - tri-engine
  - worker-allocation
  - capacity-planning
inputs:
  total_workers:
    type: integer
    required: true
    description: Total available agent worker processes or container instances.
  coherence_index:
    type: number
    required: true
    description: Current live Em-Cubed ontology coherence index [0.0, 1.0].
  epistemic_trust:
    type: number
    required: true
    description: Current SME Harvester epistemic confidence score [0.0, 1.0].
outputs:
  scaling_mode:
    type: string
    description: "BALANCED | AXIOM_HEALING | PERCEPTION_BURST | SIMULATION_DOMINANT"
  allocations:
    type: object
    description: Distributed worker counts for SME, Em-Cubed, and Strategify.
  rebalance_dispatched:
    type: boolean
    description: True if worker pool reallocation was successfully applied.
---

# Tri-Engine Swarm Capacity Scaler Engine

`tri-engine-swarm-scaler` continuously balances agent worker allocations across SME perception ingestion, Em-Cubed Topos modal verification, and Strategify Mesa simulation engines. When ontology health drops, it surges workers to Em-Cubed self-healing; when new real-world data floods in, it reallocates workers to SME Harvester.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Swarm Scaling Progression

```
[1. Metric Invariant Audit] → [2. Scaling Mode Determination] → [3. Visual Brief] → [4. Checkpoint] → [5. Worker Pool Rebalance]
```

### Stage 1: Metric Invariant Audit
1. Ingest `total_workers` ($N \ge 1$), `coherence_index`, and `epistemic_trust`.
2. Validate that metric values are bounded in $[0.0, 1.0]$.

> **Completion criterion**: Cluster parameters and health metrics validated.

---

### Stage 2: Scaling Mode & Allocation Determination
1. Determine system scaling mode:
   - **AXIOM_HEALING**: If $\text{Coherence} < 0.85$, allocate $50\%$ workers to Em-Cubed.
   - **PERCEPTION_BURST**: If $\text{Trust} < 0.70$ and $\text{Coherence} \ge 0.90$, allocate $50\%$ to SME.
   - **SIMULATION_DOMINANT**: If $\text{Coherence} \ge 0.95$ and $\text{Trust} \ge 0.90$, allocate $60\%$ to Strategify.
   - **BALANCED**: Otherwise, partition evenly ($N/3$).
2. Guarantee conservation invariant: $N_{\text{SME}} + N_{\text{EmCubed}} + N_{\text{Strategify}} = N_{\text{total}}$.

> **Completion criterion**: Worker allocation calculated with strict pool conservation.

---

### Stage 3: The Visual Brief
For cluster rebalancing events, generate an interactive capacity allocation brief:
- **Location**: Write to `%TEMP%\swarm-scaler-brief-<timestamp>.html` (Windows) or `/tmp/swarm-scaler-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render worker partition pie/bar chart and allocation shift graph.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before applying radical rebalances ($> 50\%$ worker migration across engines):
1. Verify that active simulation runs or proof routines will not be terminated mid-computation.
2. Ensure graceful draining of deallocated worker threads.

> **Completion criterion**: Worker draining schedule verified safe against job termination.

---

### Stage 5: Worker Pool Rebalance Dispatch
1. Dispatch rebalance signals to worker container orchestration daemon.
2. Commit new allocation state to cluster SQLite registry.
3. Emit scaling report with new partition quotas.

> **Completion criterion**: Allocation dispatched and verified with zero worker leaks.

---

## Surface References

### Python Scaler Surface

```python
from typing import Dict, Any

def calculate_swarm_allocation(total_workers: int, coherence: float, trust: float) -> Dict[str, Any]:
    if coherence < 0.85:
        mode = "AXIOM_HEALING"
        em = int(total_workers * 0.50)
        sme = int(total_workers * 0.25)
        strat = total_workers - em - sme
    elif trust < 0.70:
        mode = "PERCEPTION_BURST"
        sme = int(total_workers * 0.50)
        em = int(total_workers * 0.25)
        strat = total_workers - em - sme
    elif coherence >= 0.95 and trust >= 0.90:
        mode = "SIMULATION_DOMINANT"
        strat = int(total_workers * 0.60)
        em = int(total_workers * 0.20)
        sme = total_workers - strat - em
    else:
        mode = "BALANCED"
        sme = total_workers // 3
        em = total_workers // 3
        strat = total_workers - sme - em

    return {
        "scaling_mode": mode,
        "allocations": {"sme_workers": sme, "em_cubed_workers": em, "strategify_workers": strat},
        "rebalance_dispatched": True
    }
```

---

## Anti-Patterns & Guardrails

- **Worker Starvation** — Allocating zero workers to any of the three core engines, which halts the feedback loop. Enforce $\min(N_i) \ge 1$.
- **Rebalancing Oscillation** — Rapidly switching scaling modes on minor metric fluctuations. Apply smoothing hysteresis before reallocating.
- **Worker Pool Leakage** — Sum of allocations not equaling `total_workers`.
