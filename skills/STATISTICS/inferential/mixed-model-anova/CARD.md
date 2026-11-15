# Skill Summary Card: `mixed-model-anova`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        mixed-model-anova                         │
│ Category:    STATISTICS / Split-Plot Mixed Designs     │
│ Invocation:  /mixed-model-anova                        │
│ Trigger:     "mixed model anova", "split plot anova",  │
│              "between within anova", "treatment time"  │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Split-plot ANOVA combining between-group  │
│              and within-subject factors with dual error│
│              terms, partial $\eta_p^2$ & SQLite schema.│
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Split-Plot Ingestion**| Validate $g \ge 2, n \ge 2, k \ge 2$ balanced design| Split-Plot Grid AST | Balanced design verified |
| **2. Dual Error Setup**| Formulate $\text{MS}_{\text{subj(groups)}}$ and $\text{MS}_{\text{error}}$ terms | Variance Error Baselines| Dual error denominators mapped |
| **3. Visual Brief** | Render longitudinal profile & interaction chart| `%TEMP%\mixed-anova-brief-*.html`| Dark theme HTML split-plot brief |
| **4. Checkpoint** | Validate Group $\times$ Time interaction ($p_{\text{int}}$)| Interaction Decision Record| Interaction significance guided |
| **5. ANOVA & Commit**| Compute separate F-tests, $\eta_p^2$ & commit SQLite| `MixedAnovaResult` Payload | Results emitted & SQLite updated |

---

## Invariants & Guardrails

- [ ] **Dual Error Term Rule**: Between-effect uses $\text{MS}_{\text{subj(groups)}}$; within & interaction use $\text{MS}_{\text{error}}$.
- [ ] **Split-Plot Balance**: Balanced subject allocation across all $g$ groups.
- [ ] **Partial Effect Sizes**: $\eta_p^2$ reported separately for between, within, and interaction.
