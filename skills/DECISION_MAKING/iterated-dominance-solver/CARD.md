# Skill Summary Card: `iterated-dominance-solver`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        iterated-dominance-solver                 │
│ Category:    DECISION_MAKING / Game Theory IESDS       │
│ Invocation:  /iterated-dominance-solver                │
│ Trigger:     "iterated dominance solver", "iesds",     │
│              "rationalizable strategies", "solve game",│
│              "strictly dominated strategies"           │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Compute rationalizable strategy profiles  │
│              via IESDS using Z3 mixed strategy SMT     │
│              dominance checks & Prolog belief stores.  │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest players, strategy spaces & payoff matrices | Normal-Form Game AST | Non-empty game verified |
| **2. Z3 SMT** | Encode mixed strategy dominance constraints in Z3| SMT Dominance Solver | Strict dominance proved |
| **3. Visual Brief** | Render payoff matrices with strikethrough styling | `%TEMP%\iterated-dominance-brief-*.html`| Dark theme HTML brief |
| **4. Checkpoint** | Validate fixpoint condition ($S_i^{K+1} = S_i^K$)| Fixpoint Gate Record | Convergence certified |
| **5. Model Emission** | Extract $S_i^\infty$ & check dominance solvability | `IESDSResult` Payload | Full rationalizable payload emitted |

---

## Invariants & Guardrails

- [ ] **Strict Dominance Invariant**: Elimination requires strict inequality $u(\sigma) > u(s)$.
- [ ] **Fixpoint Termination**: Loop halts when no strategies are pruned or $K \ge K_{\text{max}}$.
- [ ] **Mixed Strategy Soundness**: Z3 solver validates convex combinations $\sum \sigma_j = 1$.
