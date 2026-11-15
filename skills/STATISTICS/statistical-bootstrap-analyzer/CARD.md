# Skill Summary Card: `statistical-bootstrap-analyzer`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        statistical-bootstrap-analyzer            │
│ Category:    STATISTICS / Multi-Surface Resampling     │
│ Invocation:  /statistical-bootstrap-analyzer           │
│ Trigger:     "statistical bootstrap analyzer",         │
│              "multi-surface bootstrap",                │
│              "hy uncertainty scoring"                  │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Multi-surface bootstrap engine with       │
│              Prolog replicate ratio gating, Python     │
│              percentile sampling & Hy quality scoring. │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Vector Ingestion**| Filter NaN/Null & validate $N_{\text{obs}} \ge 5$ | Clean Sample Vector AST | Clean sample verified |
| **2. Prolog Bounds** | Check $N_{\text{boot}} \ge N_{\text{obs}}$ ratio | Prolog Bounds Predicate | Design ratio certified |
| **3. Visual Brief** | Render bootstrap density & Hy quality meter | `%TEMP%\stat-bootstrap-brief-*.html`| Dark theme HTML bootstrap brief |
| **4. Checkpoint** | Validate replicate variance ($\hat{\text{SE}} > 0$) | Variance Decision Record | Positive bootstrap variance verified |
| **5. Model Emission** | Compute empirical CI, Hy score & emit payload | `BootstrapAnalysisResult` | Full multi-surface record emitted |

---

## Invariants & Guardrails

- [ ] **Sample Count Gate**: Requires $N_{\text{obs}} \ge 5$ observations.
- [ ] **Replicate Ratio**: $N_{\text{boot}} \ge N_{\text{obs}}$ enforced via Prolog.
- [ ] **Quality Score Bound**: $Q \in [0.0, 1.0]$.
