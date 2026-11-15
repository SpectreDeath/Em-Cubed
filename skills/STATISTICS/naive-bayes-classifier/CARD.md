# Skill Summary Card: `naive-bayes-classifier`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        naive-bayes-classifier                    │
│ Category:    STATISTICS / Generative Classification    │
│ Invocation:  /naive-bayes-classifier                   │
│ Trigger:     "naive bayes classifier", "gaussian nb",  │
│              "log posterior probability",              │
│              "generative classification"               │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Gaussian Naive Bayes classifier with log- │
│              space posterior estimation, variance      │
│              smoothing & SQLite parameter persistence. │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Validate design matrix & $K \ge 2$ class labels | Feature Matrix AST | $N \ge 4, K \ge 2$ verified |
| **2. Training** | Compute class priors & smoothed Gauss parameters | Class Parameter Dictionary| $[\boldsymbol{\mu}, \boldsymbol{\sigma}^2]$ computed |
| **3. Visual Brief** | Render decision boundaries & Gaussian densities | `%TEMP%\naive-bayes-brief-*.html`| Dark theme HTML classifier brief|
| **4. Checkpoint** | Validate positive variance & feature dimension | Variance Check Record | $\sigma_{kj}^2 > 0$ confirmed |
| **5. Model & Commit** | Compute log-MAP posteriors & commit SQLite | `NaiveBayesClassificationResult`| Full predictions emitted & stored |

---

## Invariants & Guardrails

- [ ] **Class Scale Gate**: Training set requires at least $K \ge 2$ distinct classes.
- [ ] **Log-Space Rule**: Likelihood calculations strictly summed in log-space.
- [ ] **Variance Smoothing**: $\epsilon_{\text{smoothing}} \ge 10^{-9}$ added to all feature variances.
