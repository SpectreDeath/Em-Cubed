# Skill Summary Card: `finite-limit-sequence-boundary`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        finite-limit-sequence-boundary            │
│ Category:    MODEL_VALIDATION / SMT Limit Safety       │
│ Invocation:  /finite-limit-sequence-boundary           │
│ Trigger:     "finite limit sequence boundary", "limit   │
│              "cauchy convergence", "z3 limit solver",  │
│              "bertrand paradox", "borel kolmogorov"    │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Enforce infinite sets be evaluated as     │
│              limits of finite sequences with Z3 SMT    │
│              convergence & measure paradox checks.     │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest sequence approximations & epsilon tolerance | Sequence Tolerance AST | Sequence length $\ge 3$ |
| **2. Z3 Axioms** | Formulate Cauchy real bounds in Z3 SMT solver | Z3 SMT Solver Model | Satisfiability checked |
| **3. Visual Brief** | Render convergence corridor plot & paradox table | `%TEMP%\finite-limit-brief-*.html`| Dark theme HTML brief |
| **4. Checkpoint** | Validate tail spread $\le 2\epsilon$ & audit paradoxes | Convergence Gate Record | Epsilon bounds certified |
| **5. Model Emission**| Extract empirical limit value $L$ & emit payload| `FiniteLimitResult` Payload | Full limit payload emitted |

---

## Invariants & Guardrails

- [ ] **Cauchy Invariant**: $|x_n - L| < \epsilon$ for all $n \ge N$.
- [ ] **Finite Counterexample**: Exact divergent indices emitted on failure.
- [ ] **Paradox Protection**: Blocks ill-conditioned zero-measure limits.
