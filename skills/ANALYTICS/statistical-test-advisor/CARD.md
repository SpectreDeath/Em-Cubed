# Skill Summary Card: `statistical-test-advisor`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        statistical-test-advisor                  │
│ Category:    ANALYTICS / Statistical Hypothesis Tests  │
│ Invocation:  /statistical-test-advisor                 │
│ Trigger:     "advise statistical test", "route test",  │
│              "parametric test selection", "anova ttest"│
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Route experimental datasets to optimal    │
│              statistical tests via Prolog decision     │
│              trees and micro-sample safety fallbacks.  │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Invariant Audit** | Validate group counts and positive sample sizes | Experiment Design Spec | $\text{len}(\text{sizes}) = k$ & $n_i > 0$ |
| **2. Prolog Routing** | Evaluate decision tree rules in Prolog | Candidate Test Label | Test selected from relational tree |
| **3. Visual Brief** | Render decision tree path and category badge | `%TEMP%\stat-advisor-brief-*.html`| Dark theme HTML routing brief |
| **4. Checkpoint** | Validate sample size asymptotic sufficiency | Sample Gating Record | $N \ge 8$ or exact fallback triggered |
| **5. Test Dispatch** | Compile test spec & emit execution payload | Final Recommendation | Structured recommendation emitted |

---

## Invariants & Guardrails

- [ ] **Small Sample Guard**: Auto-fallback to Exact Permutation or Bootstrapping when $N < 8$.
- [ ] **Pairing Integrity**: Paired experiments strictly routed to paired tests (e.g. Paired t-Test, Wilcoxon).
- [ ] **Normality Assertion**: Non-normal distributions strictly routed to non-parametric tests.
