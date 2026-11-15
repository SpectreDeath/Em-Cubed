# Skill Summary Card: `calculate_mean_confidence_interval`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        calculate_mean_confidence_interval        │
│ Category:    STATISTICS / Inferential Estimation       │
│ Invocation:  /calculate_mean_confidence_interval       │
│ Trigger:     "calculate confidence interval",          │
│              "mean CI", "margin of error",             │
│              "standard error of mean"                  │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Compute parametric mean confidence        │
│              intervals with Prolog z-critical lookup   │
│              and Python standard error calculation.    │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Filter NaN/Null & validate sample count | Clean Numeric Vector | $N \ge 2$ and $CL \in (0, 1)$ |
| **2. Z-Resolution** | Lookup or interpolate $z$-critical value | Resolved Z-Score | Exact z-score mapped from Prolog |
| **3. Visual Brief** | Render CI error-bar plot & density chart | `%TEMP%\mean-ci-brief-*.html`| Dark theme HTML interval brief |
| **4. Checkpoint** | Validate non-zero sample variance | Variance Invariant Record| $s > 0$ confirmed |
| **5. CI Emission** | Calculate $\text{SE}, \text{ME}, \text{CI}$ bounds | `ConfidenceIntervalResult` | Lower & upper bounds emitted |

---

## Invariants & Guardrails

- [ ] **Sample Count Requirement**: Requires $N \ge 2$.
- [ ] **Unbiased SE Formula**: $\text{SE} = s / \sqrt{n}$ where $s = \sqrt{\frac{1}{n-1} \sum (x_i - \bar{x})^2}$.
- [ ] **Exact Z Mapping**: $0.90 \to 1.645, 0.95 \to 1.960, 0.99 \to 2.576$.
