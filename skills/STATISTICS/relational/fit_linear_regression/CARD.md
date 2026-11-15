# Skill Summary Card: `fit_linear_regression`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        fit_linear_regression                     │
│ Category:    STATISTICS / OLS Bivariate Regression     │
│ Invocation:  /fit_linear_regression                    │
│ Trigger:     "fit linear regression", "ols regression",│
│              "slope intercept model", "r squared"      │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Ordinary Least Squares simple linear      │
│              regression with Prolog precondition guards│
│              $R^2$ goodness-of-fit & slope t-inference.│
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Paired Cleaning** | Filter NaN/Null pairs & validate sample count | Clean Paired Vectors | $n_{\text{used}} \ge 3$ verified |
| **2. Prolog Guards** | Prove independence and sample size rules | Prolog Precondition Atom | Preconditions certified |
| **3. Visual Brief** | Render scatter plot with OLS trend & residuals | `%TEMP%\fit-regression-brief-*.html`| Dark theme HTML regression brief |
| **4. Checkpoint** | Validate non-zero variance on predictor $x$ | Predictor Variance Record| $\text{SS}_{xx} > 0$ confirmed |
| **5. Model Emission** | Compute $\beta_0, \beta_1, R^2, \text{SE}, t, p$ & emit | `LinearRegressionResult` | Complete OLS record emitted |

---

## Invariants & Guardrails

- [ ] **Sample Minimum Gate**: $n_{\text{used}} \ge 3$ complete observation pairs.
- [ ] **Predictor Variance Invariant**: $\text{Var}(x) > 0$ strictly required.
- [ ] **Degrees of Freedom**: $\text{df} = n - 2$.
