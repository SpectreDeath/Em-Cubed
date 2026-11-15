# Skill Summary Card: `assert_test_constraints`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        assert_test_constraints                  │
│ Category:    STATISTICS / Pre-condition Guardrails     │
│ Invocation:  /assert_test_constraints                 │
│ Trigger:     "assert test constraints",                │
│              "check normality homoscedasticity",       │
│              "statistical guardrail", "gate test"      │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Enforce sample size, normality, and       │
│              variance equality pre-conditions before   │
│              dispatching statistical hypothesis tests. │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Extract complete-case sample size $N$ | Sample Vector AST | $N \ge \text{min\_n}(\text{test})$ |
| **2. Assumption Eval** | Evaluate Shapiro-Wilk & Levene in Python | Diagnostic Flags Record | `normal` & `equal_variance` flags set |
| **3. Visual Brief** | Render Q-Q plots, variance box plots & checklist| `%TEMP%\test-constraints-brief-*.html`| Dark theme HTML constraints brief |
| **4. Checkpoint** | Validate parametric assumptions & map fallbacks| Fallback Decision Record | Non-parametric fallback assigned if needed |
| **5. Prolog Gating** | Evaluate `permitted_test/4` & emit authorization| Constraint Bundle Payload | `allowed` or `blocked(reason)` emitted |

---

## Invariants & Guardrails

- [ ] **Sample Minimum Gate**: $N \ge \text{min\_n}(\text{Test})$.
- [ ] **Normality Invariant**: Parametric tests strictly require $p_{\text{shapiro}} \ge 0.05$.
- [ ] **Homoscedasticity Invariant**: Equal variance assumption verified or Welch correction triggered.
