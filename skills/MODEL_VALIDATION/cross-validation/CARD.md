# Skill Summary Card: `cross-validation`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        cross-validation                          │
│ Category:    MODEL_VALIDATION / Generalization Testing │
│ Invocation:  /cross-validation                         │
│ Trigger:     "cross validation", "k-fold split",       │
│              "stratified cross validation", "cv rmse", │
│              "generalization error", "sqlite cv audit" │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      K-fold cross-validation with stratified   │
│              sampling, confidence bounds, and SQLite   │
│              fold assignment & metric audit logs.      │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest feature matrix $X$ & target $y$; verify dimensions| Dataset Dimension AST | $N \ge K \ge 2$ verified |
| **2. Partitioning**| Construct disjoint stratified/uniform fold partitions | Fold Partition Map | Disjoint sets verified |
| **3. Visual Brief** | Render fold score bar chart & confidence error bands | `%TEMP%\cross-validation-brief-*.html`| Dark theme HTML brief |
| **4. Checkpoint** | Validate finite float scores & compute margin $M$ | Metric Gate Record | Finite scores certified |
| **5. Model Emission**| Persist SQLite audit tables & emit complete payload | `CrossValidationResult` Payload | Full CV payload emitted |

---

## Invariants & Guardrails

- [ ] **Disjoint Folds**: $\bigcup V_k = \{0, \dots, N-1\}$ and $V_i \cap V_j = \emptyset$.
- [ ] **Finite Metric Scores**: No `NaN` or `Inf` values permitted in fold scores.
- [ ] **Audit Completeness**: All fold assignments persisted to SQLite.
