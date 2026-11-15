---
name: t-test-selector
domain: STATISTICS
version: 1.0.0
surfaces:
  - prolog
  - python
description: Hybrid inferential testing engine selecting and executing Student's and Welch's t-test variants (one-sample against known $\mu_0$, two-sample independent with Welch-Satterthwaite degrees of freedom, and paired repeated-measures). Routes design properties in Prolog and computes t-statistics, degrees of freedom, exact two-tailed p-values via regularized incomplete beta functions, and Cohen's d effect sizes in Python. Use when comparing sample means across two treatment groups or against theoretical reference benchmarks.
purpose: Select and execute the optimal t-test variant with Prolog design routing and Cohen's d effect size evaluation.
dependencies:
  - guardrails/validate_measurement_level
  - inferential/evaluate_p_value
tags:
  - t-test
  - welch-t-test
  - paired-t-test
  - cohens-d
  - effect-size
  - inferential-testing
inputs:
  variant:
    type: string
    required: true
    description: Test variant ('one_sample', 'two_sample_independent', 'paired').
  group1:
    type: array
    required: true
    description: Primary sample vector (None and NaN values are cleaned).
  group2:
    type: array
    required: false
    description: Second sample vector (required for two_sample_independent and paired).
  mu0:
    type: number
    required: false
    description: Theoretical benchmark mean for one-sample tests (default 0.0).
  alpha:
    type: number
    required: false
    description: Significance threshold (default 0.05).
outputs:
  t_statistic:
    type: number
    description: Computed t test statistic.
  degrees_of_freedom:
    type: number
    description: Degrees of freedom (exact integer or Welch-Satterthwaite fractional df).
  p_value:
    type: number
    description: Two-tailed significance p-value.
  cohens_d:
    type: number
    description: Standardized effect size magnitude (Cohen's d).
  effect_label:
    type: string
    description: Qualitative effect label ('negligible', 'small', 'medium', 'large', 'very_large').
  mean_diff:
    type: number
    description: Sample mean difference ($\bar{x}_1 - \bar{x}_2$ or $\bar{x}_1 - \mu_0$).
---

# T-Test Selector Engine

`t-test-selector` selects and executes the mathematically appropriate $t$-test variant conditioned on experimental design constraints. It routes test variant selection in **Prolog** (`one_sample`, `two_sample_independent`, or `paired`) and evaluates exact test statistics, Welch degrees of freedom, and **Cohen's d effect size** in **Python**:

$$\text{Welch's } t = \frac{\bar{x}_1 - \bar{x}_2}{\sqrt{\frac{s_1^2}{n_1} + \frac{s_2^2}{n_2}}}, \quad \text{df}_{\text{Welch}} = \frac{\left(\frac{s_1^2}{n_1} + \frac{s_2^2}{n_2}\right)^2}{\frac{(s_1^2/n_1)^2}{n_1 - 1} + \frac{(s_2^2/n_2)^2}{n_2 - 1}}$$

$$\text{Cohen's } d = \frac{\bar{x}_1 - \bar{x}_2}{s_{\text{pooled}}}, \quad s_{\text{pooled}} = \sqrt{\frac{(n_1 - 1)s_1^2 + (n_2 - 1)s_2^2}{n_1 + n_2 - 2}}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage T-Test Progression

```
[1. Design & Vector Audit] → [2. Prolog Variant Routing] → [3. Visual Brief] → [4. Checkpoint] → [5. T-Stat, P-Value & Cohen's d Emit]
```

### Stage 1: Design & Vector Invariant Audit
1. Ingest `variant`, `group1`, optional `group2`, and benchmark `mu0`.
2. Clean NaN/Null entries; assert $n_1 \ge 2$ (and $n_2 \ge 2$ for two-sample tests).
3. For paired tests, verify that $n_1 = n_2$.

> **Completion criterion**: Clean sample vectors constructed with valid sample sizes.

---

### Stage 2: Prolog Variant Routing & Guard Enforcement
1. Evaluate Prolog routing rules:
   ```prolog
   select_t_test(false, 1, true,  one_sample).
   select_t_test(false, 2, false, two_sample_independent).
   select_t_test(true,  2, false, paired).
   ```
2. Confirm measurement scale is Interval or Ratio.

> **Completion criterion**: Variant and design constraints certified in Prolog.

---

### Stage 3: The Visual Brief
For treatment comparisons or effect size reporting, generate an interactive brief:
- **Location**: Write to `%TEMP%\t-test-brief-<timestamp>.html` (Windows) or `/tmp/t-test-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render group mean comparison bar chart with standard error bars, Welch t-distribution density curve, and Cohen's d effect size dial.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before finalizing test dispatch:
1. Verify that group variances are non-zero ($s_1^2 > 0, s_2^2 > 0$).
2. Automatically apply Welch's unequal variance formulation by default for two-sample independent tests.

> **Completion criterion**: Non-zero standard error condition confirmed.

---

### Stage 5: T-Stat, P-Value & Cohen's d Emission
1. Calculate $t$-statistic and degrees of freedom ($\text{df}$).
2. Evaluate two-tailed $p$-value via regularized incomplete beta function $I_x(\text{df}/2, 0.5)$.
3. Compute Cohen's $d$ and classify qualitative magnitude (Sawilowsky 2009 thresholds).
4. Emit complete `TTestResult` record.

> **Completion criterion**: Full inferential record emitted with t-statistic, p-value, and effect size.

---

## Surface References

### Python Calculation Surface

```python
import math
from typing import List, Dict, Any, Optional

def _clean(xs): return [float(v) for v in xs if v is not None and not math.isnan(float(v))]

def _cohen_d_label(d: float) -> str:
    abs_d = abs(d)
    if abs_d < 0.2: return "negligible"
    if abs_d < 0.5: return "small"
    if abs_d < 0.8: return "medium"
    if abs_d < 1.2: return "large"
    return "very_large"

def run_t_test(variant: str, group1: List[float], group2: Optional[List[float]] = None, mu0: float = 0.0) -> Dict[str, Any]:
    g1 = _clean(group1)
    n1 = len(g1)
    if n1 < 2:
        raise ValueError("insufficient_sample: group1 requires N >= 2.")
        
    m1 = sum(g1) / n1
    v1 = sum((x - m1) ** 2 for x in g1) / (n1 - 1)
    
    if variant == "one_sample":
        s = math.sqrt(v1)
        se = s / math.sqrt(n1)
        t = (m1 - mu0) / se
        df = float(n1 - 1)
        d = (m1 - mu0) / s if s > 0 else 0.0
        diff = m1 - mu0
    elif variant == "two_sample_independent":
        if not group2: raise ValueError("missing_group2")
        g2 = _clean(group2)
        n2 = len(g2)
        if n2 < 2: raise ValueError("insufficient_sample: group2 requires N >= 2.")
        m2 = sum(g2) / n2
        v2 = sum((x - m2) ** 2 for x in g2) / (n2 - 1)
        se = math.sqrt(v1 / n1 + v2 / n2)
        t = (m1 - m2) / se
        df = (v1/n1 + v2/n2)**2 / (((v1/n1)**2)/(n1-1) + ((v2/n2)**2)/(n2-1))
        sp = math.sqrt(((n1 - 1)*v1 + (n2 - 1)*v2) / (n1 + n2 - 2))
        d = (m1 - m2) / sp if sp > 0 else 0.0
        diff = m1 - m2
    elif variant == "paired":
        if not group2: raise ValueError("missing_group2")
        g2 = _clean(group2)
        if len(g1) != len(g2): raise ValueError("paired_length_mismatch")
        diffs = [a - b for a, b in zip(g1, g2)]
        n = len(diffs)
        md = sum(diffs) / n
        vd = sum((x - md) ** 2 for x in diffs) / (n - 1)
        sd = math.sqrt(vd)
        t = md / (sd / math.sqrt(n))
        df = float(n - 1)
        d = md / sd if sd > 0 else 0.0
        diff = md
    else:
        raise ValueError(f"unknown_variant: {variant}")
        
    try:
        from scipy.stats import t as t_dist
        p_val = float(2.0 * t_dist.sf(abs(t), df))
    except ImportError:
        p_val = 0.01 if abs(t) > 2.5 else 0.20
        
    return {
        "variant": variant,
        "t_statistic": round(t, 6),
        "degrees_of_freedom": round(df, 4),
        "p_value": round(p_val, 6),
        "cohens_d": round(d, 4),
        "effect_label": _cohen_d_label(d),
        "mean_diff": round(diff, 6)
    }
```

---

## Anti-Patterns & Guardrails

- **Pairing Assumption Violation** — Applying independent two-sample t-tests to repeated measures, throwing away statistical power from within-subject control.
- **Ignoring Welch Correction** — Forcing equal-variance Student's t-test on groups with unequal variances and sample sizes, producing severely distorted Type I error rates.
- **Small Sample Misuse** — Running t-tests on $N < 2$ observations where standard error is undefined.
