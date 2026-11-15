# Skill Summary Card: `variance-equality-tester`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        variance-equality-tester                  │
│ Category:    STATISTICS / Homoscedasticity Assumptions │
│ Invocation:  /variance-equality-tester                 │
│ Trigger:     "test variance equality", "levene test",  │
│              "bartlett test", "homoscedasticity check" │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Evaluate equality of variances across $k$ │
│              groups via Prolog normality routing and   │
│              Python Levene/Bartlett engines.           │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Invariant Audit** | Validate $k \ge 2$ and group sample sizes $n_i \ge 2$ | Group Variance AST | All groups have $n_i \ge 2$ |
| **2. Prolog Routing** | Route between Bartlett and Levene based on shape | Routed Primary Test | Bartlett (Normal) or Levene (Non-Normal) |
| **3. Visual Brief** | Render group variance box plots & spread ratios | `%TEMP%\variance-equality-brief-*.html`| Dark theme HTML variance brief |
| **4. Checkpoint** | Validate homogeneity ($p \ge \alpha$) & Welch need | Homogeneity Decision Record| `homogeneous` / `heterogeneous` set |
| **5. Result Emit** | Compile Levene & Bartlett statistics & emit | `VarianceEqualityResult` | Full test breakdown emitted |

---

## Invariants & Guardrails

- [ ] **Minimum Group Sample**: Each group must have at least $n_i \ge 2$.
- [ ] **Robustness Routing**: Non-normal data strictly evaluated via Levene's median-centered test.
- [ ] **Welch Correction Flag**: Automatically flag `welch_correction_recommended: true` when heterogeneous.
