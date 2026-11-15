# Skill Summary Card: `multiple-regression-analyzer`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        multiple-regression-analyzer              │
│ Category:    STATISTICS / Multivariate OLS Regression  │
│ Invocation:  /multiple-regression-analyzer             │
│ Trigger:     "multiple regression", "multivariate ols",│
│              "vif collinearity", "adjusted r squared", │
│              "cholesky normal equations"               │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Multivariate OLS regression via Cholesky  │
│              normal equations with VIF multicollinearity│
│              screening, $R_{\text{adj}}^2$ & SQLite.   │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Matrix Cleaning** | Align $\mathbf{X}$ and $\mathbf{y}$, drop NA rows | Aligned Design Matrix AST | $n \ge p + 2$ verified |
| **2. Normal Solve** | Solve $(\mathbf{X}^T\mathbf{X})\boldsymbol{\beta} = \mathbf{X}^T\mathbf{y}$ via Cholesky| Parameter Vector $\boldsymbol{\beta}$ | Parameters & covariance mapped |
| **3. Visual Brief** | Render coefficient forest plot & VIF gauge bar | `%TEMP%\multiple-regression-brief-*.html`| Dark theme HTML multivariate brief |
| **4. Checkpoint** | Validate VIF collinearity ($\text{VIF}_j \le 10$) | Collinearity Gate Record | Multicollinearity status guided |
| **5. Model & Commit** | Compute $R_{\text{adj}}^2, F$, $p$-values & commit SQLite| `MultipleRegressionResult` Payload | Results emitted & SQLite updated |

---

## Invariants & Guardrails

- [ ] **Degrees of Freedom Gate**: Strictly requires $n \ge p + 2$ observations.
- [ ] **VIF Guard**: Flag warning when $\text{VIF}_j > 10.0$ (severe collinearity).
- [ ] **Adjusted $R^2$ Metric**: Always report $R_{\text{adj}}^2 \le R^2$ to penalize parameter expansion.
