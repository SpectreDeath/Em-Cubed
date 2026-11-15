# Skill Summary Card: `t-test-selector`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        t-test-selector                           │
│ Category:    STATISTICS / Parametric Hypothesis Tests  │
│ Invocation:  /t-test-selector                          │
│ Trigger:     "run t-test", "welch t-test",             │
│              "paired t-test", "one-sample t-test",     │
│              "cohens d effect size"                    │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Design-routed t-test execution with       │
│              Welch degrees of freedom and Cohen's d    │
│              standardized effect size estimation.      │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Validate vectors, $N \ge 2$, and paired lengths | Sample Vector AST | Clean inputs verified |
| **2. Prolog Routing** | Route variant (one-sample, independent, paired) | Routed Variant Atom | Variant & scale certified |
| **3. Visual Brief** | Render mean comparison bar plot & Cohen's d | `%TEMP%\t-test-brief-*.html`| Dark theme HTML t-test brief |
| **4. Checkpoint** | Validate non-zero variance & Welch application | Variance Gate Record | Non-zero variance verified |
| **5. Test Emission** | Compute $t, \text{df}, p$, Cohen's d & emit | `TTestResult` | Full test breakdown emitted |

---

## Invariants & Guardrails

- [ ] **Sample Count Gate**: $N \ge 2$ per group.
- [ ] **Paired Integrity**: Paired vectors must have strictly identical lengths ($N_1 = N_2$).
- [ ] **Default Welch Correction**: Fractional Welch-Satterthwaite df used for independent groups.
