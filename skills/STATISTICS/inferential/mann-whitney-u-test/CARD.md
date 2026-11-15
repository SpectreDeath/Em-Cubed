# Skill Summary Card: `mann-whitney-u-test`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        mann-whitney-u-test                       │
│ Category:    STATISTICS / Non-Parametric Two-Sample    │
│ Invocation:  /mann-whitney-u-test                      │
│ Trigger:     "mann-whitney u test", "rank-sum test",   │
│              "non-parametric independent test",        │
│              "rank biserial correlation"               │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Non-parametric two-sample comparison with │
│              tie-corrected fractional ranks, continuity│
│              adjusted z-scores & rank-biserial effect. │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Filter NaN/Null & validate independent samples | Sample Vector AST | $n_1 \ge 3, n_2 \ge 3$ verified |
| **2. Fractional Rank**| Sort pooled array & compute fractional tie ranks| Tie-Adjusted Rank Array | Rank sums $R_1, R_2$ calculated |
| **3. Visual Brief** | Render rank strip-plot & cumulative ECDF curves | `%TEMP%\mann-whitney-brief-*.html`| Dark theme HTML Mann-Whitney brief |
| **4. Checkpoint** | Validate sample size regime ($N \le 25$ check) | Approximation Gate Record| Asymptotic vs exact mapped |
| **5. Test Emission** | Compute $U, z, p$, rank-biserial $r$ & emit | `MannWhitneyResult` | Complete non-parametric record emitted |

---

## Invariants & Guardrails

- [ ] **Independent Group Gate**: Each group requires at least $n_i \ge 3$.
- [ ] **Rank Sum Conservation**: $R_1 + R_2 = \frac{N(N+1)}{2}$.
- [ ] **Rank-Biserial Scale**: $r \in [-1.0, 1.0]$.
