# Skill Summary Card: `two-way-anova`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        two-way-anova                             │
│ Category:    STATISTICS / Factorial Multi-Factor       │
│ Invocation:  /two-way-anova                            │
│ Trigger:     "two way anova", "factorial anova",       │
│              "main effects interaction",               │
│              "partial eta squared"                     │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Factorial ANOVA evaluating main and       │
│              interaction effects with Prolog routing,  │
│              balanced design guards & partial $\eta_p^2$│
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Grid Ingestion** | Validate $a \ge 2, b \ge 2$ and balanced $n \ge 2$ | Factorial Grid AST | Equal cell replication verified |
| **2. Prolog Guards** | Prove design validity and balance in Prolog | Design Verification Atom | Factorial balance certified |
| **3. Visual Brief** | Render $A \times B$ interaction plot & partial $\eta_p^2$ | `%TEMP%\two-way-anova-brief-*.html`| Dark theme HTML factorial brief |
| **4. Checkpoint** | Validate interaction significance ($p_{AB} < \alpha$) | Interaction Gate Record | Simple effects vs main effects guided |
| **5. ANOVA Emission** | Compute $\text{SS}_A, \text{SS}_B, \text{SS}_{AB}$, $F, p$ & emit | `TwoWayAnovaResult` | Full factorial breakdown emitted |

---

## Invariants & Guardrails

- [ ] **Factorial Scale Gate**: Factor levels $a \ge 2$ and $b \ge 2$.
- [ ] **Replication Requirement**: Each cell must have $n \ge 2$ observations.
- [ ] **Sum of Squares Conservation**: $\text{SS}_{\text{total}} = \text{SS}_A + \text{SS}_B + \text{SS}_{AB} + \text{SS}_{\text{error}}$.
