# Skill Summary Card: `execute_monte_carlo_walk`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        execute_monte_carlo_walk                  │
│ Category:    STOCHASTIC_PROCESSES / Random Walks       │
│ Invocation:  /execute_monte_carlo_walk                 │
│ Trigger:     "execute monte carlo walk", "random walk",│
│              "simulate markov chain", "inverse sample" │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Simulate discrete Markov chain random     │
│              walks with inverse transform sampling,    │
│              dynamic context callbacks & visit counts. │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest transition matrix, state list & start state| Markov Walk State AST | Valid $s_0 \in \text{states}$ verified |
| **2. Callback** | Query context callback for dynamic matrix override| Active Transition Matrix | Row stochasticity maintained |
| **3. Visual Brief** | Render state trajectory timeline & visit counts | `%TEMP%\monte-carlo-walk-brief-*.html`| Dark theme HTML walk brief |
| **4. Checkpoint** | Validate absorbing condition ($P_{ii} \ge 0.99$) | Absorbing Decision Record| Early stop evaluated |
| **5. Model Emission** | Sample transitions & emit full path trajectory | `WalkResult` Payload | Full trajectory emitted |

---

## Invariants & Guardrails

- [ ] **State Universe Gate**: $s_0 \in \text{states}$ and matrix dimension $R \times R$.
- [ ] **Inverse Transform Sampling**: Next state selected via uniform cumulative sum inversion.
- [ ] **Deterministic Reproducibility**: Seed parameter guarantees identical trajectory output.
