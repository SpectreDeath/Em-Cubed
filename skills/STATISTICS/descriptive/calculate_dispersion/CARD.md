# Skill Summary Card: `calculate_dispersion`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        calculate_dispersion                      │
│ Category:    STATISTICS / Descriptive Spread           │
│ Invocation:  /calculate_dispersion                     │
│ Trigger:     "calculate dispersion", "sample variance",│
│              "standard deviation", "compute iqr"       │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Compute range, population/sample variance,│
│              std, and linear-interpolated IQR from     │
│              sanitized numeric vectors ($N \ge 2$).    │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Sanitization** | Filter NaN/Null & validate sample count | Clean Numeric Vector | $N \ge 2$ after cleaning |
| **2. Quartile Setup** | Sort array & determine linear percentile ranks | Sorted Vector & Ranks | $Q_1$ and $Q_3$ positions mapped |
| **3. Visual Brief** | Render box plot, $\sigma$-bands, and spread | `%TEMP%\dispersion-brief-*.html`| Dark theme HTML dispersion brief |
| **4. Checkpoint** | Validate against zero variance (constant series) | Variance Diagnostic Record| Degenerate spread flagged |
| **5. Metric Emit** | Calculate range, $\sigma^2, s^2, \text{IQR}$ & emit | `DispersionResult` | Complete metrics record emitted |

---

## Invariants & Guardrails

- [ ] **Sample Count Gate**: Requires $N \ge 2$ to compute unbiased sample variance ($N-1$).
- [ ] **Linear Percentile Interpolation**: Fractional percentile ranks interpolated linearly.
- [ ] **Bessel Correction Isolation**: Clearly distinguish between `std` ($\text{ddof}=0$) and `std_sample` ($\text{ddof}=1$).
