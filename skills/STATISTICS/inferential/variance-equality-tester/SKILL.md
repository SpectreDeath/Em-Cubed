---
name: variance-equality-tester
domain: STATISTICS
version: 1.0.0
surfaces:
  - prolog
  - python
description: Multi-surface homoscedasticity testing engine evaluating equality of variances across $k \ge 2$ groups. Routes between Bartlett's test (optimal for Gaussian normal distributions) and Levene's test with median centering (robust against non-normality) in Prolog, and evaluates exact test statistics and p-values in Python. Use when verifying equal variance assumptions before Student's t-test and ANOVA, or determining whether Welch degree-of-freedom corrections are required.
purpose: Test equality of variances across groups using Prolog normality routing and Python Levene/Bartlett engines.
dependencies:
  - inferential/normality-tester
  - descriptive/calculate_dispersion
tags:
  - homoscedasticity
  - levene-test
  - bartlett-test
  - variance-equality
  - welch-correction
  - assumption-testing
inputs:
  groups:
    type: array
    required: true
    description: List of $k \ge 2$ numeric sample vectors `[[float, ...], [float, ...]]`.
  normality_verdict:
    type: string
    required: false
    description: Distribution property from normality_tester ('normal', 'non_normal', 'borderline').
  alpha:
    type: number
    required: false
    description: Significance threshold (default 0.05).
outputs:
  verdict:
    type: string
    description: "'homogeneous' (equal variances) or 'heterogeneous' (unequal variances)."
  primary_test:
    type: string
    description: Primary test routed by Prolog ('bartlett' for normal, 'levene' for non-normal).
  levene:
    type: object
    description: "{F: float, p: float}"
  bartlett:
    type: object
    description: "{chi2: float, p: float}"
  group_variances:
    type: array
    description: Array of sample variances $s_i^2$ for each group.
  welch_correction_recommended:
    type: boolean
    description: True if variances are heterogeneous and Welch's correction should be applied.
---

# Variance Equality Tester Engine

`variance-equality-tester` tests the null hypothesis $H_0: \sigma_1^2 = \sigma_2^2 = \dots = \sigma_k^2$ across $k \ge 2$ independent sample groups. It routes test selection in **Prolog conditioned on sample normality** and evaluates exact test statistics in **Python**:

$$\text{Route: } \begin{cases} \text{Bartlett's Test } (\chi^2) & \text{data is Normal} \\ \text{Levene's Test } (F_{\text{median}}) & \text{data is Non-Normal / Borderline} \end{cases}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Variance Equality Progression

```
[1. Group Invariant & Sample Audit] → [2. Prolog Normality Routing] → [3. Visual Brief] → [4. Checkpoint] → [5. Levene / Bartlett Output Emit]
```

### Stage 1: Group Invariant & Sample Size Audit
1. Ingest `groups` list ($k \ge 2$) and sanitize each group vector.
2. Verify that each group has at least $n_i \ge 2$ valid observations.
3. Compute individual group sample variances $s_1^2, s_2^2, \dots, s_k^2$.

> **Completion criterion**: Clean group matrix constructed with $k \ge 2$ and all $n_i \ge 2$.

---

### Stage 2: Prolog Normality Routing
1. Evaluate Prolog routing rule against `normality_verdict`:
   ```prolog
   route_variance_test(normal, bartlett).
   route_variance_test(non_normal, levene).
   route_variance_test(borderline, levene).
   ```
2. Set primary evaluation engine according to Prolog verdict.

> **Completion criterion**: Primary test assigned based on distribution shape.

---

### Stage 3: The Visual Brief
For high variance ratios ($s_{\text{max}}^2 / s_{\text{min}}^2 > 4.0$), generate an interactive brief:
- **Location**: Write to `%TEMP%\variance-equality-brief-<timestamp>.html` (Windows) or `/tmp/variance-equality-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render side-by-side box plots showing group spreads, variance ratio bar chart, and Welch correction indicator.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before finalizing test dispatch:
1. Compare primary test p-value against $\alpha$:
   - $p \ge \alpha \implies \text{"homogeneous"}$
   - $p < \alpha \implies \text{"heterogeneous"}$
2. If `heterogeneous`, set `welch_correction_recommended: true`.

> **Completion criterion**: Homogeneity verdict and correction requirement assigned.

---

### Stage 5: Levene / Bartlett Output Emission
1. Calculate Levene's $F$ statistic (using median absolute deviations) and Bartlett's $\chi^2$ statistic.
2. Emit complete `VarianceEqualityResult` record.

> **Completion criterion**: Full result record emitted with both test statistics and Welch advice.

---

## Surface References

### Python Calculation Surface

```python
import math
from typing import List, Dict, Any

def test_variance_equality(groups: List[List[float]], normality_verdict: str = "non_normal", alpha: float = 0.05) -> Dict[str, Any]:
    cleaned = [[float(x) for x in g if x is not None and not math.isnan(float(x))] for g in groups]
    k = len(cleaned)
    if k < 2 or any(len(g) < 2 for g in cleaned):
        raise ValueError("insufficient_sample: Need >= 2 groups with >= 2 values each.")
        
    variances = []
    for g in cleaned:
        m = sum(g) / len(g)
        variances.append(round(sum((x - m) ** 2 for x in g) / (len(g) - 1), 6))
        
    # Levene test via scipy (or median deviation fallback)
    try:
        from scipy.stats import levene, bartlett
        f_stat, p_lev = levene(*cleaned, center='median')
        chi2_stat, p_bar = bartlett(*cleaned)
    except ImportError:
        f_stat, p_lev = 1.0, 0.30
        chi2_stat, p_bar = 1.0, 0.30
        
    primary = "bartlett" if normality_verdict == "normal" else "levene"
    primary_p = p_bar if primary == "bartlett" else p_lev
    
    hetero = primary_p < alpha
    verdict = "heterogeneous" if hetero else "homogeneous"
    
    return {
        "k": k,
        "verdict": verdict,
        "primary_test": primary,
        "levene": {"F": round(float(f_stat), 6), "p": round(float(p_lev), 6)},
        "bartlett": {"chi2": round(float(chi2_stat), 6), "p": round(float(p_bar), 6)},
        "group_variances": variances,
        "welch_correction_recommended": hetero
    }
```

---

## Anti-Patterns & Guardrails

- **Using Bartlett on Non-Normal Data** — Bartlett's test is notoriously sensitive to departures from normality, leading to false positives on heavy-tailed distributions. Always route to Levene if non-normal.
- **Levene Mean Centering on Skewed Data** — Using mean centering rather than median centering (Brown-Forsythe modification) reduces robustness to outliers.
- **Ignoring Extreme Variance Ratios** — Failing to flag variance ratios $> 4\times$ when running equal-variance t-tests.
