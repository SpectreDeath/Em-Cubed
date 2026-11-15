# Skill Summary Card: `builtin-occams-razor-evaluator`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        builtin-occams-razor-evaluator            │
│ Category:    STATISTICS / Bayesian Model Selection     │
│ Invocation:  /builtin-occams-razor-evaluator           │
│ Trigger:     "occams razor evaluator", "bayes factor", │
│              "model comparison", "bic penalty",        │
│              "prior density dilution"                  │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Bayesian model selection via Bayes Factor │
│              $B_{12}$, prior volume dilution penalties │
│              and Kass-Raftery evidence classification. │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Validate model parameters $k_i \ge 1$ and sample $N$ | Model Comparison AST | $N \ge 3, k_i \ge 1$ verified |
| **2. Z3 Verification**| Verify prior volume dilution and complexity axioms| Z3 Sat Certificate | Complexity axioms certified |
| **3. Visual Brief** | Render BIC trade-off & Bayes factor evidence meter | `%TEMP%\occams-razor-brief-*.html`| Dark theme HTML Occam brief |
| **4. Checkpoint** | Validate $\Delta \text{BIC}$ threshold ($|\Delta| \ge 2.0$) | Evidence Resolution Record| Negligible vs decisive guided |
| **5. Model Emission** | Compute $B_{AB}, \log_{10}(B_{AB})$, favored model | `OccamComparisonResult` | Complete model selection payload |

---

## Invariants & Guardrails

- [ ] **Sample Scale Gate**: Requires $N \ge 3$ observations.
- [ ] **Prior Volume Scaling**: Occam factor ratio $\Omega_A / \Omega_B \approx N^{(k_B - k_A)/2}$.
- [ ] **Evidence Classification**: Kass-Raftery 4-tier scale strictly enforced.
