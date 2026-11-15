# Skill Summary Card: `wilcoxon-signed-rank-test`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        wilcoxon-signed-rank-test                 │
│ Category:    STATISTICS / Non-Parametric Paired        │
│ Invocation:  /wilcoxon-signed-rank-test                │
│ Trigger:     "wilcoxon signed rank test",              │
│              "non-parametric paired test",             │
│              "matched pairs rank test", "median diff"  │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Non-parametric paired comparison with     │
│              zero-pruning, tie-corrected signed ranks, │
│              continuity z-scores & rank-biserial effect│
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Validate paired vectors & prune zero differences | Non-Zero Diff Vector | $n_{\text{effective}} \ge 1$ and $n_{\text{pairs}} \ge 6$ |
| **2. Signed Rank** | Rank absolute differences & compute $W^+, W^-$ | Signed Rank Sums | $W^+ + W^- = \frac{n(n+1)}{2}$ |
| **3. Visual Brief** | Render slope-graph & difference distribution | `%TEMP%\wilcoxon-signed-brief-*.html`| Dark theme HTML Wilcoxon brief |
| **4. Checkpoint** | Validate sample size regime ($n \le 25$ check) | Approximation Gate Record| Asymptotic vs exact mapped |
| **5. Test Emission** | Compute $z, p$, matched rank-biserial $r$ & emit | `WilcoxonResult` | Complete non-parametric record emitted |

---

## Invariants & Guardrails

- [ ] **Paired Integrity**: Vectors must have strictly identical lengths ($N_1 = N_2$).
- [ ] **Zero Difference Pruning**: Differences $d_i = 0$ must be dropped from effective sample count $n$.
- [ ] **Rank Sum Conservation**: $W^+ + W^- = \frac{n(n+1)}{2}$.
