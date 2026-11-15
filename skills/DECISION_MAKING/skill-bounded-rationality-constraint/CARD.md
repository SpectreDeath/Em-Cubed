# Skill Summary Card: `skill-bounded-rationality-constraint`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        skill-bounded-rationality-constraint      │
│ Category:    DECISION_MAKING / Bounded Rationality     │
│ Invocation:  /skill-bounded-rationality-constraint    │
│ Trigger:     "skill bounded rationality constraint",   │
│              "bounded rationality circuit breaker",    │
│              "iesds termination guard", "fixpoint delta│
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Active circuit breaker middleware for     │
│              recursive IESDS loops enforcing depth     │
│              ceilings & weight delta convergence.      │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest iteration counter, max depth & convergence $\delta$| Boundedness State AST | Valid thresholds verified |
| **2. Residual** | Compute maximum weight change $\Delta_{\text{max}} = \max |\Delta w|$| Weight Delta Record | Delta residual evaluated |
| **3. Visual Brief** | Render iteration progress gauge & convergence curve | `%TEMP%\bounded-rationality-brief-*.html`| Dark theme HTML brief |
| **4. Checkpoint** | Validate depth limit ($K \ge K_{\text{max}}$) & fixpoint ($\Delta < \delta$)| Circuit Verdict Atom | Termination reason assigned |
| **5. Model Emission** | Emit circuit breaker verdict & iteration counter | `BoundedRationalityResult` Payload| Full verdict payload emitted |

---

## Invariants & Guardrails

- [ ] **Depth Ceiling Invariant**: Forced termination if $K \ge K_{\text{max}}$.
- [ ] **Fixpoint Detection**: Convergence triggered if $\max |\Delta w_i| < \delta$.
- [ ] **Positive Delta**: Threshold parameter $\delta > 0$ strictly enforced.
