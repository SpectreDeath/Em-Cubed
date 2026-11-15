# Skill Summary Card: `kruskal-wallis-test`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        kruskal-wallis-test                       │
│ Category:    STATISTICS / Non-Parametric Multi-Group   │
│ Invocation:  /kruskal-wallis-test                      │
│ Trigger:     "kruskal wallis test", "non-parametric    │
│              anova", "dunns test", "rank sum anova"    │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Non-parametric multi-group comparison     │
│              with Z3 design guards, tie-corrected H    │
│              statistic & Bonferroni-corrected Dunn's.  │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Filter NaN/Null & validate $k \ge 3, n_i \ge 3$ | Sample Grid AST | $k \ge 3$ independent groups verified |
| **2. Z3 Verification**| Prove design constraints (scale, independence) | Z3 Sat Certificate | Z3 returns `sat` |
| **3. Visual Brief** | Render mean rank bar chart & Dunn's matrix | `%TEMP%\kruskal-wallis-brief-*.html`| Dark theme HTML Kruskal-Wallis brief |
| **4. Checkpoint** | Validate omnibus H significance ($p < \alpha$) | Omnibus Decision Record| Omnibus significance guided |
| **5. Test Emission** | Compute $H_{\text{corr}}, p$, Dunn's pairs & emit | `KruskalWallisResult` | Complete non-parametric record emitted |

---

## Invariants & Guardrails

- [ ] **Multi-Group Scale Gate**: Strictly requires $k \ge 3$ independent groups.
- [ ] **Sample Count Gate**: Each group requires at least $n_i \ge 3$.
- [ ] **Post-Hoc Family Control**: Dunn's test strictly adjusted via Bonferroni correction ($p \cdot \binom{k}{2}$).
