# Skill Summary Card: `skill-belief-state-updater`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        skill-belief-state-updater                │
│ Category:    DECISION_MAKING / Bayesian Belief State   │
│ Invocation:  /skill-belief-state-updater               │
│ Trigger:     "skill belief state updater",             │
│              "belief state updater", "mass redistribute│
│              "bayesian belief update", "prune mass"    │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Re-allocate eliminated probability mass   │
│              across surviving strategies using Hy Lisp │
│              lattice rules & Python Bayesian updates.  │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest active/eliminated sets & prior weights | Strategy Partition AST | $|S_{\text{active}}| \ge 1$ verified |
| **2. Mass Tally** | Sum eliminated mass $M_{\text{elim}}$ & active mass $M_{\text{active}}$| Mass Balance Record | $M_{\text{elim}} + M_{\text{active}} = 1.0$ |
| **3. Visual Brief** | Render before/after density charts & flow diagram | `%TEMP%\belief-state-brief-*.html`| Dark theme HTML brief |
| **4. Checkpoint** | Validate active mass $> 0$ (or uniform fallback) | Normalization Gate Record | Safe denominator verified |
| **5. Model Emission** | Compute posterior weights $\hat{p}_i$ & emit log | `BeliefStateResult` Payload | Full belief payload emitted |

---

## Invariants & Guardrails

- [ ] **Posterior Normalization**: $\sum_{i \in S_{\text{active}}} \hat{p}_i = 1.0 \pm 10^{-6}$.
- [ ] **Eliminated Mass Conservation**: $\hat{p}_k = 0.0$ for all $k \in S_{\text{elim}}$.
- [ ] **Zero-Active Fallback**: Uniform distribution assigned if active mass is 0.
