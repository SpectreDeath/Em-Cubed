# Skill Summary Card: `bootstrap-resampling`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        bootstrap-resampling                      │
│ Category:    STATISTICS / Resampling & Uncertainty     │
│ Invocation:  /bootstrap-resampling                     │
│ Trigger:     "bootstrap resampling", "bca interval",   │
│              "bootstrap confidence interval",          │
│              "empirical sampling distribution"         │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Non-parametric bootstrap estimation of    │
│              sampling distributions, bias, SE & BCa /  │
│              percentile confidence intervals in SQLite.│
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Filter NaN/Null & validate $N \ge 4$ observations| Sample Vector AST | Clean sample verified |
| **2. Replicate Draw** | Generate $B$ Monte Carlo draws with replacement | Bootstrap Replicate Vector| $B$ replicate statistics evaluated |
| **3. Visual Brief** | Render bootstrap histogram & empirical density | `%TEMP%\bootstrap-resampling-brief-*.html`| Dark theme HTML bootstrap brief |
| **4. Checkpoint** | Validate replicate count ($B \ge 1000$ tail rule) | Convergence Gate Record | Monte Carlo convergence guided |
| **5. CI & Commit** | Extract percentiles, evaluate bias & commit SQLite| `BootstrapResult` Payload | Complete results emitted & stored |

---

## Invariants & Guardrails

- [ ] **Sample Count Gate**: Requires $N \ge 4$ observations.
- [ ] **Replicate Scale**: Default $B = 1000$ draws for stable 95% tail bounds.
- [ ] **Coverage Invariant**: Confidence bounds $[\text{CI}_{\text{lower}}, \text{CI}_{\text{upper}}]$ strictly bounded within support range.
