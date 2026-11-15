# Skill Summary Card: `normality-tester`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        normality-tester                          │
│ Category:    STATISTICS / Distributional Assumptions   │
│ Invocation:  /normality-tester                         │
│ Trigger:     "test normality", "shapiro-wilk test",    │
│              "dagostino pearson test", "check normal"  │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Sample-size-routed normality testing via  │
│              Shapiro-Wilk, D'Agostino-Pearson K², and  │
│              Lilliefors with skewness/kurtosis moments.│
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Cleaning** | Filter NaN/Null & compute moments ($\bar{x}, s, \gamma_1, \gamma_2$)| Sample Moments AST | $N \ge 3$ verified |
| **2. Prolog Route** | Select primary test by sample size ($N$) | Routed Test Atom | Shapiro ($N < 50$) or D'Agostino ($N \ge 50$) |
| **3. Visual Brief** | Render Q-Q plot & histogram Gaussian overlay | `%TEMP%\normality-brief-*.html`| Dark theme HTML normality brief |
| **4. Checkpoint** | Validate primary/secondary test agreement | Composite Verdict Record| `normal` / `non_normal` / `borderline` |
| **5. Verdict Emit** | Compile test statistics & emit payload | `NormalityTestResult` | Full test breakdown emitted |

---

## Invariants & Guardrails

- [ ] **Sample Size Minimum**: $N \ge 3$ for Shapiro-Wilk; $N \ge 8$ for D'Agostino.
- [ ] **Sample-Size Routing**: $N < 50 \to \text{Shapiro-Wilk}; N \ge 50 \to \text{D'Agostino-Pearson}$.
- [ ] **Excess Kurtosis**: Normalized so that Gaussian kurtosis is $0.0$.
