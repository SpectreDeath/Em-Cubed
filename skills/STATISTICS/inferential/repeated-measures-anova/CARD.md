# Skill Summary Card: `repeated-measures-anova`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        repeated-measures-anova                   │
│ Category:    STATISTICS / Within-Subject Longitudinal  │
│ Invocation:  /repeated-measures-anova                  │
│ Trigger:     "repeated measures anova", "within subject│
│              anova", "sphericity correction",          │
│              "greenhouse geisser epsilon"              │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Within-subjects ANOVA with Greenhouse-    │
│              Geisser sphericity epsilon corrections and│
│              atomic SQLite design matrix persistence.  │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Matrix Ingestion**| Validate complete-case matrix ($n \ge 2, k \ge 2$) | Longitudinal Matrix AST | Complete balanced data verified |
| **2. Epsilon Estimation**| Compute Greenhouse-Geisser sphericity $\hat{\epsilon}$ | Sphericity Record | $\hat{\epsilon} \in [1/(k-1), 1.0]$ |
| **3. Visual Brief** | Render subject spaghetti plot & condition profile | `%TEMP%\rm-anova-brief-*.html`| Dark theme HTML RM-ANOVA brief |
| **4. Checkpoint** | Validate df shrinkage ($\text{df}_c, \text{df}_e$) | Sphericity Gate Record | GG correction assigned if $\epsilon < 0.75$ |
| **5. ANOVA & Commit**| Compute corrected $F, p, \eta_p^2$ & commit SQLite | `RMAnovaResult` Payload | Results emitted & SQLite updated |

---

## Invariants & Guardrails

- [ ] **Complete Case Requirement**: All subjects must have values for all $k$ conditions.
- [ ] **Sphericity Gating**: Apply Greenhouse-Geisser correction whenever $\hat{\epsilon} < 0.75$.
- [ ] **Sum of Squares Partition**: $\text{SS}_{\text{total}} = \text{SS}_{\text{subjects}} + \text{SS}_{\text{conditions}} + \text{SS}_{\text{error}}$.
