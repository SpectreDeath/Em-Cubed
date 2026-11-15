# Skill Summary Card: `skill-expected-utility-maximizer`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        skill-expected-utility-maximizer          │
│ Category:    DECISION_MAKING / Expected Utility        │
│ Invocation:  /skill-expected-utility-maximizer         │
│ Trigger:     "skill expected utility maximizer",       │
│              "expected utility maximizer", "maximize eu│
│              "optimal action selection", "z3 indep"    │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Select optimal pure action by maximizing  │
│              expected utility over opponent belief     │
│              states with Z3 SMT independence checks.   │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest actions, opponent beliefs & payoff matrix| Strategic Decision AST | Payoff matrix dimensions match |
| **2. Z3 SMT** | Encode independence constraints & solve in Z3 | SMT Independence Atom | Independence status proved |
| **3. Visual Brief** | Render expected utility ranking chart & belief pie| `%TEMP%\expected-utility-brief-*.html`| Dark theme HTML brief |
| **4. Checkpoint** | Validate utility finiteness & tie-breaking | Ranking Invariant Record| All utilities finite |
| **5. Model Emission** | Compute $EU(a)$, rank actions & emit $a^*$ | `ExpectedUtilityResult` Payload| Full EU optimization payload emitted |

---

## Invariants & Guardrails

- [ ] **Belief State Normalization**: $\sum_{o} P(o) = 1.0 \pm 10^{-5}$.
- [ ] **Dimension Matching**: $\text{rows}(\mathbf{U}) = |\mathcal{A}|$ and $\text{cols}(\mathbf{U}) = |\mathcal{O}|$.
- [ ] **Action Optimality**: $a^* = \arg\max_{a} EU(a)$.
