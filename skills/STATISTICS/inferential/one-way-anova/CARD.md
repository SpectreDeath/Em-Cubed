# Skill Summary Card: `one-way-anova`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        one-way-anova                             │
│ Category:    STATISTICS / Parametric Multi-Group       │
│ Invocation:  /one-way-anova                            │
│ Trigger:     "one way anova", "f test",                │
│              "compare 3 groups", "tukey hsd",          │
│              "eta squared effect size"                 │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Multi-group mean equality testing with    │
│              Z3 design verification, $\eta^2/\omega^2$ │
│              effect sizes & post-hoc Tukey HSD.        │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Filter NaN/Null & validate $k \ge 3, n_i \ge 2$ | Group Matrix AST | $k \ge 3$ groups established |
| **2. Z3 Verification**| Prove design validity (independence, scale, $k$) | Z3 Sat Certificate | Z3 returns `sat` |
| **3. Visual Brief** | Render ANOVA summary table & Tukey HSD forest | `%TEMP%\one-way-anova-brief-*.html`| Dark theme HTML ANOVA brief |
| **4. Checkpoint** | Validate omnibus F significance ($p < \alpha$) | Omnibus Gate Record | Omnibus significance evaluated |
| **5. ANOVA Emission** | Compute $F, p, \eta^2, \omega^2$, Tukey pairs & emit| `AnovaResult` Payload | Complete ANOVA breakdown emitted |

---

## Invariants & Guardrails

- [ ] **Design Bounds**: Strictly requires $k \ge 3$ independent groups.
- [ ] **Sum of Squares Conservation**: $\text{SS}_{\text{total}} = \text{SS}_{\text{between}} + \text{SS}_{\text{within}}$.
- [ ] **Post-Hoc Family Control**: Tukey HSD used for all pairwise contrasts to bound FWER at $\alpha$.
