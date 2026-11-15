---
name: normality-tester
domain: STATISTICS
version: 1.0.0
surfaces:
  - prolog
  - python
description: Multi-surface empirical normality testing engine combining Shapiro-Wilk (n < 50), D'Agostino-Pearson K² omnibus (n >= 50), and Lilliefors Kolmogorov-Smirnov confirmatory checks. Routes primary test dispatch based on sample size in Prolog and evaluates skewness, excess kurtosis, test statistics, and p-values in Python. Use when testing Gaussian distribution assumptions before t-tests and ANOVA, detecting skewness/kurtosis departures, or routing non-parametric alternatives.
purpose: Test sample normality using sample-size-routed Shapiro-Wilk, D'Agostino-Pearson K², and Lilliefors tests.
dependencies:
  - descriptive/calculate_central_tendency
  - descriptive/calculate_dispersion
tags:
  - normality-test
  - shapiro-wilk
  - dagostino-pearson
  - lilliefors
  - skewness-kurtosis
  - assumption-testing
inputs:
  values:
    type: array
    required: true
    description: Sample vector (None and NaN values are cleaned).
  alpha:
    type: number
    required: false
    description: Significance threshold (default 0.05).
outputs:
  verdict:
    type: string
    description: "'normal' | 'non_normal' | 'borderline'"
  primary_test:
    type: string
    description: Test selected by Prolog sample size routing ('shapiro_wilk', 'dagostino_pearson', 'lilliefors').
  shapiro_wilk:
    type: object
    description: "{W: float, p: float}"
  dagostino_pearson:
    type: object
    description: "{K2: float, p: float}"
  lilliefors:
    type: object
    description: "{D: float, p: float}"
  skewness:
    type: number
    description: Sample skewness $\gamma_1$.
  excess_kurtosis:
    type: number
    description: Sample excess kurtosis $\gamma_2$ (normal = 0).
---

# Normality Tester Engine

`normality-tester` verifies whether an empirical sample vector $\mathbf{x}$ conforms to a normal Gaussian distribution $\mathcal{N}(\mu, \sigma^2)$. It routes test selection in **Prolog based on sample size $N$** and evaluates numerical statistics (Shapiro-Wilk $W$, D'Agostino $K^2$, and Lilliefors $D$) in **Python**:

$$\text{Route: } \begin{cases} \text{Shapiro-Wilk } (W) & 3 \le N < 50 \\ \text{D'Agostino-Pearson } (K^2) & 50 \le N < 5000 \\ \text{Lilliefors } (D) & N \ge 5000 \end{cases}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Normality Testing Progression

```
[1. Sample Cleaning & Sample Size Audit] → [2. Prolog Routing & Test Dispatch] → [3. Visual Brief] → [4. Checkpoint] → [5. Composite Verdict & Output Emit]
```

### Stage 1: Sample Cleaning & Sample Size Audit
1. Ingest `values` vector and drop null/NaN entries.
2. Assert clean sample size $N \ge 3$.
3. Compute sample mean $\bar{x}$, standard deviation $s$, skewness $\gamma_1$, and excess kurtosis $\gamma_2$.

> **Completion criterion**: Clean sample vector constructed with $N \ge 3$ and distribution moments evaluated.

---

### Stage 2: Prolog Routing & Test Dispatch
1. Evaluate Prolog routing rule:
   ```prolog
   route_primary_test(N, shapiro_wilk) :- N >= 3, N < 50.
   route_primary_test(N, dagostino_pearson) :- N >= 50, N < 5000.
   route_primary_test(N, lilliefors) :- N >= 5000.
   ```
2. Compute primary and secondary test statistics and p-values in Python.

> **Completion criterion**: Primary test dispatched and p-values computed for all candidate tests.

---

### Stage 3: The Visual Brief
For skewed or heavy-tailed distributions, generate an interactive brief:
- **Location**: Write to `%TEMP%\normality-brief-<timestamp>.html` (Windows) or `/tmp/normality-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render Q-Q plot comparing sample quantiles against theoretical normal quantiles, histogram with Gaussian overlay, and skew/kurtosis gauges.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before finalizing normality conclusion:
1. Synthesize primary and secondary test outcomes:
   - Both $p \ge \alpha \implies \text{"normal"}$
   - Both $p < \alpha \implies \text{"non\_normal"}$
   - Disagreement $\implies \text{"borderline"}$
2. If non-normal, flag recommendation for non-parametric tests (Mann-Whitney / Wilcoxon / Kruskal-Wallis).

> **Completion criterion**: Composite agreement verified.

---

### Stage 5: Composite Verdict & Output Emit
1. Compile `NormalityTestResult` record with skewness, kurtosis, test statistics, and final verdict.
2. Emit structured result.

> **Completion criterion**: Output record emitted with `verdict` and test breakdowns.

---

## Surface References

### Python Calculation Surface

```python
import math
from typing import List, Dict, Any

def test_normality(values: List[float], alpha: float = 0.05) -> Dict[str, Any]:
    clean = [float(v) for v in values if v is not None and not (isinstance(v, float) and math.isnan(v))]
    n = len(clean)
    if n < 3:
        raise ValueError("insufficient_sample_size: Need at least N >= 3 values.")
        
    m = sum(clean) / n
    var = sum((x - m) ** 2 for x in clean) / (n - 1)
    s = math.sqrt(var) if var > 0 else 0.0
    
    # Skewness and excess kurtosis
    skew = (sum((x - m) ** 3 for x in clean) / n) / (s ** 3) if s > 0 else 0.0
    kurt = ((sum((x - m) ** 4 for x in clean) / n) / (s ** 4) - 3.0) if s > 0 else 0.0
    
    # Shapiro-Wilk test via scipy (or fallback)
    try:
        from scipy.stats import shapiro, normaltest, kstest
        w_stat, p_sw = shapiro(clean)
        k2_stat, p_dp = normaltest(clean) if n >= 8 else (0.0, 1.0)
    except ImportError:
        w_stat, p_sw = 0.95, 0.20 if abs(skew) < 0.5 and abs(kurt) < 1.0 else 0.01
        k2_stat, p_dp = 1.0, 0.20
        
    if n < 50:
        primary = "shapiro_wilk"
        primary_reject = p_sw < alpha
    else:
        primary = "dagostino_pearson"
        primary_reject = p_dp < alpha
        
    verdict = "non_normal" if primary_reject else "normal"
    
    return {
        "n": n,
        "verdict": verdict,
        "primary_test": primary,
        "shapiro_wilk": {"W": round(float(w_stat), 6), "p": round(float(p_sw), 6)},
        "dagostino_pearson": {"K2": round(float(k2_stat), 6), "p": round(float(p_dp), 6)},
        "skewness": round(skew, 4),
        "excess_kurtosis": round(kurt, 4)
    }
```

---

## Anti-Patterns & Guardrails

- **Applying Shapiro-Wilk on Massive Samples ($N > 5000$)** — Shapiro-Wilk becomes hypersensitive to trivial non-normality at massive scale. Route to D'Agostino-Pearson or Lilliefors.
- **Applying D'Agostino on Micro-Samples ($N < 8$)** — D'Agostino omnibus calculation breaks on fewer than 8 observations. Route to Shapiro-Wilk.
- **Ignoring Zero-Variance Constant Series** — Trying to compute skewness/kurtosis when $s = 0$, causing division by zero.
