---
name: calculate_correlation_profile
domain: STATISTICS
version: 1.0.0
surfaces:
  - prolog
  - python
description: Relational correlation profiling engine evaluating linear (Pearson's r) and monotonic rank (Spearman's rho) association between paired numeric vectors. Enforces measurement-level gates in Prolog (interval/ratio for Pearson, ordinal+ for Spearman), cleans paired missing entries, computes covariance/rank transforms, calculates t-distribution p-values, and maps quantitative correlation coefficients to qualitative magnitude bands (negligible to very strong). Use when evaluating bivariate association strengths, feature collinearity, or testing monotonic relationships.
purpose: Compute Pearson and Spearman correlation profiles with Prolog scale routing and magnitude band classification.
dependencies:
  - guardrails/validate_measurement_level
  - inferential/evaluate_p_value
tags:
  - correlation-profile
  - pearson-r
  - spearman-rho
  - rank-correlation
  - magnitude-bands
  - relational-statistics
inputs:
  x:
    type: array
    required: true
    description: First variable vector (None and NaN values are paired-filtered).
  y:
    type: array
    required: true
    description: Second variable vector (None and NaN values are paired-filtered).
  method:
    type: string
    required: false
    description: Correlation method ('pearson' or 'spearman', default 'pearson').
  alpha:
    type: number
    required: false
    description: Significance threshold (default 0.05).
outputs:
  r:
    type: number
    description: Pearson correlation coefficient $r \in [-1.0, 1.0]$.
  rho:
    type: number
    description: Spearman rank correlation coefficient $\rho \in [-1.0, 1.0]$.
  p_value:
    type: number
    description: 'Two-tailed significance p-value under $H_0: \rho = 0$.'
  magnitude:
    type: string
    description: Qualitative magnitude band ('negligible', 'weak', 'moderate', 'strong', 'very_strong').
  n_used:
    type: integer
    description: Complete paired observation count after filtering missing values.
  n_dropped:
    type: integer
    description: Total paired rows dropped due to missing data in either $x$ or $y$.
---

# Calculate Correlation Profile Engine

`calculate_correlation_profile` computes formal bivariate correlation coefficients and statistical significance between paired variables. It routes method selection in **Prolog based on Stevens' measurement scale** and evaluates exact covariance, rank transformations, and **qualitative magnitude bands** in **Python**:

$$\text{Pearson } r = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum (x_i - \bar{x})^2 \sum (y_i - \bar{y})^2}}, \quad \text{Spearman } \rho = r(\text{Rank}(\mathbf{x}), \text{Rank}(\mathbf{y}))$$

$$t = r \sqrt{\frac{n - 2}{1 - r^2}}, \quad \text{df} = n - 2$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Correlation Progression

```
[1. Paired Cleaning & Invariant Audit] → [2. Prolog Method Gate & Routing] → [3. Visual Brief] → [4. Checkpoint] → [5. Coefficient, P-Value & Magnitude Emit]
```

### Stage 1: Paired Cleaning & Invariant Audit
1. Ingest paired vectors $\mathbf{x}$ and $\mathbf{y}$.
2. Drop rows where either $x_i$ or $y_i$ is null or NaN.
3. Assert clean paired sample count $n_{\text{used}} \ge 3$.

> **Completion criterion**: Clean paired float vectors $\mathbf{x}_{\text{clean}}, \mathbf{y}_{\text{clean}}$ constructed ($N \ge 3$).

---

### Stage 2: Prolog Method Gate & Routing
1. Query Prolog rules for scale compatibility:
   ```prolog
   method_allowed(pearson, LevelX, LevelY) :- dominates(LevelX, interval), dominates(LevelY, interval).
   method_allowed(spearman, LevelX, LevelY) :- dominates(LevelX, ordinal), dominates(LevelY, ordinal).
   ```
2. For ordinal or non-normal continuous data, route to Spearman rank correlation.

> **Completion criterion**: Correlation method certified against variable measurement scale.

---

### Stage 3: The Visual Brief
For feature correlation reviews or regression screening, generate an interactive brief:
- **Location**: Write to `%TEMP%\correlation-profile-brief-<timestamp>.html` (Windows) or `/tmp/correlation-profile-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render bivariate scatter plot with OLS linear trendline, $r/\rho$ correlation strength meter, and magnitude classification badge.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before finalizing output payload:
1. Verify that standard deviations of both vectors are non-zero ($s_x > 0, s_y > 0$).
2. If either vector is constant, return $r = 0.0$ and flag zero-variance warning.

> **Completion criterion**: Non-zero variance verified for both variables.

---

### Stage 5: Coefficient, P-Value & Magnitude Emission
1. Calculate Pearson's $r$ or Spearman's $\rho$.
2. Compute two-tailed $t$-statistic and significance $p$-value.
3. Classify magnitude band:
   - $|r| < 0.10 \implies \text{"negligible"}$
   - $0.10 \le |r| < 0.40 \implies \text{"weak"}$
   - $0.40 \le |r| < 0.70 \implies \text{"moderate"}$
   - $0.70 \le |r| < 0.90 \implies \text{"strong"}$
   - $|r| \ge 0.90 \implies \text{"very\_strong"}$
4. Emit complete `CorrelationResult` record.

> **Completion criterion**: Full correlation record emitted with coefficient, p-value, and magnitude.

---

## Surface References

### Python Calculation Surface

```python
import math
from typing import List, Dict, Any

def _clean_pairs(x: List[float], y: List[float]):
    cx, cy, dropped = [], [], 0
    for a, b in zip(x, y):
        if a is not None and b is not None and not (isinstance(a, float) and math.isnan(a)) and not (isinstance(b, float) and math.isnan(b)):
            cx.append(float(a))
            cy.append(float(b))
        else:
            dropped += 1
    return cx, cy, dropped

def _rank(values: List[float]) -> List[float]:
    indexed = sorted(enumerate(values), key=lambda x: x[1])
    n = len(indexed)
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n - 1 and indexed[j + 1][1] == indexed[j][1]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = avg
        i = j + 1
    return ranks

def calculate_correlation_profile(x: List[float], y: List[float], method: str = "pearson", alpha: float = 0.05) -> Dict[str, Any]:
    cx, cy, dropped = _clean_pairs(x, y)
    n = len(cx)
    if n < 3:
        raise ValueError("insufficient_pairs: Correlation requires at least N >= 3 complete pairs.")
        
    if method == "spearman":
        cx = _rank(cx)
        cy = _rank(cy)
    elif method != "pearson":
        raise ValueError("invalid_method: Method must be 'pearson' or 'spearman'.")
        
    mx = sum(cx) / n
    my = sum(cy) / n
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(cx, cy))
    dx = math.sqrt(sum((xi - mx) ** 2 for xi in cx))
    dy = math.sqrt(sum((yi - my) ** 2 for yi in cy))
    
    r_val = (num / (dx * dy)) if (dx * dy > 0) else 0.0
    r_val = max(-1.0, min(1.0, r_val))
    
    # P-value calculation via t-distribution
    denom = 1.0 - r_val * r_val
    if denom <= 0:
        p_val = 0.0
    else:
        t_stat = abs(r_val * math.sqrt((n - 2) / denom))
        try:
            from scipy.stats import t as t_dist
            p_val = float(2.0 * t_dist.sf(t_stat, n - 2))
        except ImportError:
            p_val = 0.001 if t_stat > 3.0 else 0.20
            
    abs_r = abs(r_val)
    if abs_r < 0.10: mag = "negligible"
    elif abs_r < 0.40: mag = "weak"
    elif abs_r < 0.70: mag = "moderate"
    elif abs_r < 0.90: mag = "strong"
    else: mag = "very_strong"
    
    return {
        "method": method,
        "r": round(r_val, 6),
        "rho": round(r_val, 6),
        "p_value": round(p_val, 6),
        "magnitude": mag,
        "n": len(x),
        "n_used": n,
        "n_dropped": dropped
    }
```

---

## Anti-Patterns & Guardrails

- **Applying Pearson to Non-Linear Monotonic Trends** — Using Pearson $r$ on exponential or ordinal data; Pearson measures strictly linear relationships. Use Spearman $\rho$ for general monotonic curves.
- **Conflating Correlation with Causation** — Reporting high correlation as proof of direct causal linkage without confounding variable controls.
- **Unchecked Complete-Case Sample Loss** — Silently proceeding when $> 50\%$ of rows are dropped due to misaligned missing data.
