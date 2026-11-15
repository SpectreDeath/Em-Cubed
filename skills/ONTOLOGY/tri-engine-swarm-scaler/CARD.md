# Skill Summary Card: `tri-engine-swarm-scaler`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        tri-engine-swarm-scaler                   │
│ Category:    ONTOLOGY / Swarm Capacity Balancing       │
│ Invocation:  /tri-engine-swarm-scaler                  │
│ Trigger:     "scale tri-engine swarm",                 │
│              "balance worker allocation",              │
│              "rebalance cluster", "swarm capacity"     │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Dynamically balance worker allocations    │
│              across SME, Em-Cubed, and Strategify      │
│              based on Coherence and Epistemic Trust.   │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Metric Audit** | Ingest worker pool size and health scores | Validated Metrics | All metrics bounded in $[0.0, 1.0]$ |
| **2. Mode Determination**| Classify scaling mode & calculate partition | Allocation Quotas | $\sum N_i = N_{\text{total}}$ with $\min(N_i) \ge 1$ |
| **3. Visual Brief** | Render capacity chart and shift diagram | `%TEMP%\swarm-scaler-brief-*.html` | Dark theme HTML allocation report |
| **4. Checkpoint** | Validate worker draining and migration safety | Safety Gate Record | Graceful worker drain confirmed |
| **5. Pool Dispatch** | Dispatch allocation signals to orchestrator | Scaling Report | New quotas applied with zero leaks |

---

## Invariants & Guardrails

- [ ] **Worker Conservation**: $N_{\text{SME}} + N_{\text{EmCubed}} + N_{\text{Strategify}} = N_{\text{total}}$.
- [ ] **No Engine Starvation**: Every engine receives at least 1 worker node.
- [ ] **Hysteresis Smoothing**: Rebalancing throttled to prevent thrashing.
