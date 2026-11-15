# Skill Summary Card: `model-validation-suite`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        model-validation-suite                    │
│ Category:    MODEL_VALIDATION / Multi-Surface Testing  │
│ Invocation:  /model-validation-suite                   │
│ Trigger:     "model validation suite", "validate model"│
│              "bias variance decomposition", "perm test │
│              "prolog validation rules", "hy confidence"│
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Comprehensive validation suite: empirical │
│              residuals, bias-variance, permutation,    │
│              Prolog logic rules & Hy fuzzy confidence. │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest predictions, actuals & fold scores | Evaluation Dataset AST | $|\text{Pred}| = |\text{Actual}| \ge 2$ |
| **2. Error Decomp**| Compute MSE, RMSE, MAE & bias-variance parts| Error Decomposition Record| Variance & bias calculated |
| **3. Visual Brief** | Render residual error histogram & bias-var chart| `%TEMP%\model-validation-brief-*.html`| Dark theme HTML brief |
| **4. Checkpoint** | Validate Prolog consistency & overfitting gap | Verification Gate Record | Overfitting status checked |
| **5. Model Emission**| Synthesize Hy confidence quotient & emit payload| `ModelValidationResult` Payload| Full validation payload emitted|

---

## Invariants & Guardrails

- [ ] **Error Decomposition Soundness**: $\text{MSE} \approx \text{Bias}^2 + \text{Var} + \text{Noise}$.
- [ ] **Significance Bounds**: Permutation $p$-value bounded strictly to $[0.0, 1.0]$.
- [ ] **Fuzzy Confidence Stability**: Quotient clamped to $[0.0, 1.0]$.
