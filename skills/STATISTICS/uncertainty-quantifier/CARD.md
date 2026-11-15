# Skill Summary Card: `uncertainty-quantifier`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        uncertainty-quantifier                    │
│ Category:    STATISTICS / Probabilistic Risk & Sampling│
│ Invocation:  /uncertainty-quantifier                   │
│ Trigger:     "uncertainty quantifier", "monte carlo",  │
│              "sensitivity analysis", "risk assessment",│
│              "probabilistic uncertainty"               │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Multi-surface uncertainty quantification  │
│              with Monte Carlo sampling, Cholesky       │
│              correlations & OAT sensitivity analysis.  │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Validate distribution specifications & sample count| Distribution Schema AST | $N_{\text{samples}} \ge 1000$ verified |
| **2. Correlation** | Apply Cholesky transformation to correlated inputs| Correlated Sample Draws | Positive-definite matrix certified |
| **3. Visual Brief** | Render outcome distribution histogram & tornado | `%TEMP%\uncertainty-quantifier-brief-*.html`| Dark theme HTML uncertainty brief |
| **4. Checkpoint** | Validate percentile convergence & dominant risk | Risk Gate Record | Sensitivity bounds certified |
| **5. Model Emission** | Compute mean, std, percentiles, sensitivities | `UncertaintyAnalysisResult`| Full probabilistic record emitted |

---

## Invariants & Guardrails

- [ ] **Sample Minimum Gate**: $N_{\text{samples}} \ge 1000$ simulation draws.
- [ ] **Correlation Validity**: Pairwise correlation matrix must be positive semi-definite.
- [ ] **Monotonic Percentiles**: $P_5 \le P_{25} \le P_{50} \le P_{75} \le P_{95}$.
