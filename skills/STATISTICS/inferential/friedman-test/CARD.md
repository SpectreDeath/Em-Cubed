# Skill Summary Card: `friedman-test`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        friedman-test                             │
│ Category:    STATISTICS / Non-Parametric Within-Subject│
│ Invocation:  /friedman-test                            │
│ Trigger:     "friedman test", "non-parametric rm anova"│
│              "kendalls w", "conover post-hoc"          │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Non-parametric within-subjects comparison │
│              with within-block ranking, Kendall's W &  │
│              Bonferroni-adjusted Conover post-hoc.     │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Validate complete matrix ($n \ge 2, k \ge 2$) | Block Design AST | Balanced block design verified |
| **2. Row Ranking** | Rank values within each subject row | Within-Block Rank Array | Condition rank sums calculated |
| **3. Visual Brief** | Render subject slope-plots & Kendall's W dial | `%TEMP%\friedman-test-brief-*.html`| Dark theme HTML Friedman brief |
| **4. Checkpoint** | Validate omnibus $\chi_F^2$ significance ($p < \alpha$)| Omnibus Decision Record| Omnibus significance guided |
| **5. Test & Commit** | Compute $\chi_F^2, W$, Conover pairs & commit SQLite| `FriedmanResult` Payload | Results emitted & SQLite updated |

---

## Invariants & Guardrails

- [ ] **Row-Independent Ranking**: Ranks must be assigned strictly within each subject row $1 \dots k$.
- [ ] **Kendall's Concordance**: $W \in [0.0, 1.0]$.
- [ ] **Conover Adjustment**: Pairwise contrasts adjusted via Bonferroni ($p \cdot \binom{k}{2}$).
