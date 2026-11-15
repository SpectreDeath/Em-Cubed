# Skill Summary Card: `calculate_correlation_profile`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        calculate_correlation_profile             │
│ Category:    STATISTICS / Relational Association       │
│ Invocation:  /calculate_correlation_profile            │
│ Trigger:     "calculate correlation profile",          │
│              "pearson r", "spearman rho",              │
│              "bivariate correlation", "rank correlation│
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Compute Pearson r and Spearman rho        │
│              coefficients with Prolog scale routing,   │
│              p-values & qualitative magnitude bands.   │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Paired Cleaning** | Filter NaN/Null pairs & validate sample count | Clean Paired Vectors | $n_{\text{used}} \ge 3$ verified |
| **2. Prolog Routing** | Validate measurement scale (interval vs ordinal)| Routed Method Atom | Method certified against scale |
| **3. Visual Brief** | Render scatter plot with OLS trend & magnitude | `%TEMP%\correlation-profile-brief-*.html`| Dark theme HTML correlation brief |
| **4. Checkpoint** | Validate non-zero variance on both vectors | Variance Gate Record | $s_x > 0, s_y > 0$ confirmed |
| **5. Result Emit** | Compute $r/\rho, t, p$, magnitude band & emit | `CorrelationResult` | Complete correlation record emitted |

---

## Invariants & Guardrails

- [ ] **Sample Minimum Gate**: $n_{\text{used}} \ge 3$ complete pairs.
- [ ] **Scale Protection**: Pearson requires Interval/Ratio; Spearman requires Ordinal+.
- [ ] **Bounded Coefficients**: $r, \rho \in [-1.0, 1.0]$.
