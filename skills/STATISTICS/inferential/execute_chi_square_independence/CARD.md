# Skill Summary Card: `execute_chi_square_independence`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        execute_chi_square_independence           │
│ Category:    STATISTICS / Categorical Association      │
│ Invocation:  /execute_chi_square_independence          │
│ Trigger:     "chi square test of independence",        │
│              "contingency table test", "cramers v",    │
│              "categorical association test"            │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Execute Pearson Chi-Square independence   │
│              test on contingency tables with Cochran   │
│              cell adequacy check & Cramér's V.         │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Table Audit** | Validate $r \ge 2, c \ge 2$ and non-negative counts | Contingency Matrix AST | Non-negative integers verified |
| **2. Expected Counts**| Calculate $E_{ij}$ matrix and evaluate Cochran rule| Expected Counts Table | Expected matrix computed |
| **3. Visual Brief** | Render observed vs expected residual heatmap | `%TEMP%\chi-square-brief-*.html`| Dark theme HTML contingency brief |
| **4. Checkpoint** | Validate Cochran rule ($< 20\%$ cells $< 5$) | Cell Adequacy Record | Fisher fallback flagged if needed |
| **5. Test Emission** | Compute $\chi^2$, $p$-value, Cramér's V & emit | `ChiSquareResult` Payload | Full statistical result emitted |

---

## Invariants & Guardrails

- [ ] **Table Dimensions**: Matrix must be at least $2 \times 2$.
- [ ] **Raw Integer Counts**: Strictly requires absolute observed frequencies, never percentages.
- [ ] **Degrees of Freedom**: $\text{df} = (r - 1)(c - 1)$.
