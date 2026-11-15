---
name: calculate_dispersion
domain: STATISTICS
version: 1.0.0
surfaces:
  - python
description: Algorithmic statistical execution engine computing canonical measures of spread and dispersion (range, population/sample variance, standard deviation, and interquartile range / IQR) from numeric vectors. Handles linear percentile interpolation, degree of freedom (ddof) adjustments, and sanitization of NaN/None entries. Use when quantifying distributional spread, computing standard errors for confidence intervals, or screening for outlier variance.
purpose: Compute range, variance (ddof=0,1), standard deviation, and IQR from sanitized numeric vectors.
dependencies: []
tags:
  - dispersion
  - variance
  - standard-deviation
  - interquartile-range
  - descriptive-statistics
inputs:
  values:
    type: array
    required: true
    description: Raw numeric vector (may contain None, NaN, or string representations of numbers).
  dataset_id:
    type: string
    required: false
    description: Optional logical dataset identifier for state tagging.
outputs:
  range:
    type: number
    description: Difference between maximum and minimum value ($\text{max} - \text{min}$).
  variance:
    type: number
    description: Population variance with degrees of freedom $\text{ddof} = 0$.
  variance_sample:
    type: number
    description: Unbiased sample variance with Bessel's correction $\text{ddof} = 1$.
  std:
    type: number
    description: Population standard deviation $\sigma$.
  std_sample:
    type: number
    description: Sample standard deviation $s$ (used for standard errors and t-tests).
  iqr:
    type: number
    description: Interquartile range ($Q_3 - Q_1$) via linear interpolation.
  n:
    type: integer
    description: Clean sample size count after pruning invalid entries.
---

# Calculate Dispersion Engine

`calculate_dispersion` quantifies the spread of empirical sample distributions $\mathbf{x} = (x_1, x_2, \dots, x_N)$. It computes range, population variance ($\sigma^2$), sample variance with Bessel's correction ($s^2$), standard deviations, and linear-interpolated Interquartile Range ($\text{IQR} = Q_{75} - Q_{25}$):

$$s^2 = \frac{1}{N - 1} \sum_{i=1}^{N} (x_i - \bar{x})^2, \quad \sigma^2 = \frac{1}{N} \sum_{i=1}^{N} (x_i - \bar{x})^2$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Dispersion Progression

```
[1. Vector Sanitization & Audit] → [2. Sorted Array & Quartile Setup] → [3. Visual Brief] → [4. Checkpoint] → [5. Variance & IQR Computation]
```

### Stage 1: Vector Sanitization & Audit
1. Ingest `values` array and filter non-numeric, `None`, and `NaN` entries.
2. Assert clean sample size $N \ge 2$ for valid sample variance ($N - 1 \ge 1$).

> **Completion criterion**: Clean float vector verified with $N \ge 2$.

---

### Stage 2: Sorted Array & Quartile Setup
1. Sort sanitized vector ascending: $\mathbf{s} = \text{sort}(\mathbf{x}_{\text{clean}})$.
2. Calculate linear interpolation ranks for 25th ($Q_1$) and 75th ($Q_3$) percentiles.

> **Completion criterion**: Array sorted and quartile bounds positioned.

---

### Stage 3: The Visual Brief
For high-variance distributions or outlier detection, generate an interactive brief:
- **Location**: Write to `%TEMP%\dispersion-brief-<timestamp>.html` (Windows) or `/tmp/dispersion-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render box-and-whisker plot, $\pm 1\sigma / \pm 2\sigma$ standard deviation bands, and IQR range.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before exporting dispersion metrics:
1. Check for zero variance: $\text{var} = 0.0$ (all values identical / degenerate distribution).
2. If variance is zero, flag constant-value series in diagnostics to alert downstream inference solvers.

> **Completion criterion**: Constant distribution check evaluated and recorded.

---

### Stage 5: Variance & IQR Computation & Emission
1. Compute sum of squared differences from mean: $\text{SSD} = \sum (x_i - \bar{x})^2$.
2. Compute $\sigma^2 = \text{SSD} / N$ and $s^2 = \text{SSD} / (N - 1)$.
3. Compute $\text{IQR} = Q_3 - Q_1$ and $\text{range} = s[-1] - s[0]$.
4. Emit full `DispersionResult` record.

> **Completion criterion**: Complete dispersion record emitted with sample and population metrics.

---

## Surface References

### Python Implementation Surface

```python
import math
from typing import List, Dict, Any

def _percentile(sorted_vals: List[float], pct: float) -> float:
    n = len(sorted_vals)
    if n == 1:
        return sorted_vals[0]
    rank = (pct / 100.0) * (n - 1)
    lower = int(math.floor(rank))
    upper = int(math.ceil(rank))
    if lower == upper:
        return sorted_vals[lower]
    frac = rank - lower
    return sorted_vals[lower] * (1.0 - frac) + sorted_vals[upper] * frac

def calculate_dispersion(values: List[Any], dataset_id: str = None) -> Dict[str, Any]:
    clean = []
    dropped = 0
    for v in values:
        if v is None:
            dropped += 1
            continue
        try:
            val = float(v)
            if math.isnan(val):
                dropped += 1
            else:
                clean.append(val)
        except (ValueError, TypeError):
            dropped += 1

    n = len(clean)
    if n < 2:
        raise ValueError("insufficient_sample: Dispersion requires at least N >= 2 valid numeric entries.")

    s = sorted(clean)
    mean_val = sum(s) / n
    sum_sq_diff = sum((x - mean_val) ** 2 for x in s)

    var_pop = sum_sq_diff / n
    var_samp = sum_sq_diff / (n - 1)
    std_pop = math.sqrt(var_pop)
    std_samp = math.sqrt(var_samp)

    q75 = _percentile(s, 75.0)
    q25 = _percentile(s, 25.0)
    iqr_val = q75 - q25

    return {
        "range": round(s[-1] - s[0], 6),
        "variance": round(var_pop, 6),
        "variance_sample": round(var_samp, 6),
        "std": round(std_pop, 6),
        "std_sample": round(std_samp, 6),
        "iqr": round(iqr_val, 6),
        "n": n,
        "n_dropped": dropped,
        "dataset_id": dataset_id
    }
```

---

## Anti-Patterns & Guardrails

- **Bessel's Correction Confusion** — Using population standard deviation ($\sigma$, dividing by $N$) instead of sample standard deviation ($s$, dividing by $N-1$) when calculating standard errors for t-tests and confidence intervals.
- **Single-Element Dispersion** — Attempting to compute sample variance on $N = 1$, leading to division by zero ($N - 1 = 0$). Enforce $N \ge 2$.
- **Negative Variance Floats** — Allowing tiny negative floating-point epsilon values from subtraction rounding before taking square roots.
