# Skill Summary Card: `evaluate_stationarity`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        evaluate_stationarity                     │
│ Category:    STOCHASTIC_PROCESSES / Markov Stationarity│
│ Invocation:  /evaluate_stationarity                    │
│ Trigger:     "evaluate stationarity", "steady state",  │
│              "ergodicity test", "power iteration",     │
│              "perron frobenius convergence"            │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Classify Markov chain ergodicity,         │
│              irreducibility & aperiodicity in Prolog   │
│              and solve steady-state $\pi$ via iteration│
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Validate row-stochasticity & dimensions ($R \times R$)| Stochastic Matrix AST | $\sum P_j = 1.0$ verified |
| **2. Prolog Class** | Prove reachability & aperiodicity in Prolog | Topology Classification Atom| Chain type certified |
| **3. Visual Brief** | Render communicating class graph & $\pi$ bar chart | `%TEMP%\evaluate-stationarity-brief-*.html`| Dark theme HTML stationarity brief|
| **4. Checkpoint** | Validate ergodicity for unique $\boldsymbol{\pi}$ | Convergence Gate Record | Ergodicity verified |
| **5. Model Emission** | Solve $\boldsymbol{\pi}\mathbf{P} = \boldsymbol{\pi}$ via power iteration & emit | `StationarityResult` Payload | Full steady-state payload emitted |

---

## Invariants & Guardrails

- [ ] **Row-Stochastic Gate**: All row sums strictly $1.0 \pm 10^{-6}$.
- [ ] **Perron-Frobenius Invariant**: Unique positive $\boldsymbol{\pi}$ iff chain is ergodic.
- [ ] **Normalization**: $\sum \pi_i = 1.0 \pm 10^{-6}$.
