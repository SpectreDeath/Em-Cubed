# Skill Summary Card: `compile_simulation_histogram`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        compile_simulation_histogram              │
│ Category:    STOCHASTIC_PROCESSES / Trajectory Analysis│
│ Invocation:  /compile_simulation_histogram             │
│ Trigger:     "compile simulation histogram",           │
│              "empirical stationary distribution",      │
│              "first passage time", "visit frequency"   │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Aggregate Monte Carlo walk paths into     │
│              empirical state visit distributions, first│
│              passage times & Prolog count validation.  │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest path trajectories & resolve state universe | Simulation Trajectory AST | Non-empty paths verified |
| **2. Tally** | Count visits & calculate first-passage hitting times| Raw State Visit Array | Visit frequencies computed |
| **3. Visual Brief** | Render state visit histogram & survival curve | `%TEMP%\simulation-histogram-brief-*.html`| Dark theme HTML histogram brief|
| **4. Checkpoint** | Validate non-negative count invariants in Prolog| Prolog Invariant Certificate| Integer counts $\ge 0$ certified |
| **5. Model Emission** | Normalize empirical $\mathbf{f}$ & emit metrics | `HistogramResult` Payload | Full aggregation payload emitted |

---

## Invariants & Guardrails

- [ ] **Non-Negative Count Invariant**: Counts $c_i \ge 0 \in \mathbb{N}$.
- [ ] **Sum Conservation**: $\sum c_i = \text{total\_visits}$.
- [ ] **Empirical Distribution Normalization**: $\sum f_i = 1.0 \pm 10^{-6}$.
