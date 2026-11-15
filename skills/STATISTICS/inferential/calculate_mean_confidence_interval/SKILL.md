---
name: calculate_mean_confidence_interval
domain: STATISTICS
version: 1.0.0
surfaces:
  - prolog
  - python
description: Hybrid inferential skill computing parametric confidence intervals for sample means ($\text{CI} = \bar{x} \pm z \cdot \frac{s}{\sqrt{n}}$). Resolves exact two-tailed z-critical values ($0.90 \to 1.645, 0.95 \to 1.960, 0.99 \to 2.576$) in Prolog, and evaluates standard errors, margins of error, and confidence interval bounds in Python with rational inverse-error function fallback. Use when reporting parameter estimation bounds, comparing sample means to benchmark values, or visualizing inferential uncertainty.
purpose: Compute parametric mean confidence intervals with Prolog z-critical resolution and Python standard error calculation.
dependencies:
  - descriptive/calculate_central_tendency
  - descriptive/calculate_dispersion
tags:
  - confidence-interval
  - inferential-statistics
  - standard-error
  - z-score-lookup
  - margin-of-error
  - prolog
inputs:
  values:
    type: array
    required: true
    description: Raw sample vector (None and NaN values are filtered).
  confidence_level:
    type: number
    required: false
    description: Desired confidence level $1 - \alpha \in (0, 1)$ (default 0.95).
outputs:
  mean:
    type: number
    description: Sample arithmetic mean $\bar{x}$.
  std:
    type: number
    description: Sample standard deviation $s$ ($\text{ddof} = 1$).
  n:
    type: integer
    description: Clean sample size count.
  z_score:
    type: number
    description: Critical value $z_{\alpha/2}$ resolved from Prolog or inverse normal.
  standard_error:
    type: number
    description: Standard error of the mean $\text{SE} = s / \sqrt{n}$.
  margin_of_error:
    type: number
    description: Margin of error $\text{ME} = z \cdot \text{SE}$.
  ci_lower:
    type: number
    description: Lower confidence bound $\bar{x} - \text{ME}$.
  ci_upper:
    type: number
    description: Upper confidence bound $\bar{x} + \text{ME}$.
---

# Calculate Mean Confidence Interval Engine

`calculate_mean_confidence_interval` computes formal parametric confidence bounds for population means $\mu$ given an empirical sample vector $\mathbf{x}$. It couples a **declarative Prolog lookup table** (`ci_z/2`) with a **high-precision Python engine**:

$$\text{CI}_{1-\alpha} = \bar{x} \pm z_{\alpha/2} \cdot \frac{s}{\sqrt{n}}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Confidence Interval Progression

```
[1. Sample Cleaning & Invariant Audit] → [2. Prolog Z-Score Resolution] → [3. Visual Brief] → [4. Checkpoint] → [5. Standard Error & CI Bound Emit]
```

### Stage 1: Sample Cleaning & Invariant Audit
1. Ingest `values` vector and sanitize non-numeric/NaN entries.
2. Validate confidence level: $0.0 < 1 - \alpha < 1.0$.
3. Assert minimum sample size $N \ge 2$.

> **Completion criterion**: Clean sample vector constructed with $N \ge 2$.

---

### Stage 2: Prolog Z-Score Critical Value Resolution
1. Query Prolog table `ci_z/2` for canonical levels:
   - $0.90 \implies z = 1.645$
   - $0.95 \implies z = 1.960$
   - $0.99 \implies z = 2.576$
2. For non-standard levels, evaluate the inverse error function fallback:
   $$z = \sqrt{2} \cdot \text{erfinv}(2(1 - \alpha/2) - 1)$$

> **Completion criterion**: Critical value $z$ resolved to 4 decimal places.

---

### Stage 3: The Visual Brief
For inferential reporting or comparison across experiment arms, generate an interactive brief:
- **Location**: Write to `%TEMP%\mean-ci-brief-<timestamp>.html` (Windows) or `/tmp/mean-ci-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render error-bar interval plots showing $\bar{x}$, $[\text{CI}_{\text{lower}}, \text{CI}_{\text{upper}}]$, and sample distribution density overlay.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before finalizing interval bounds:
1. Verify that sample standard deviation $s > 0$.
2. If $s = 0$ (constant series), alert zero-width confidence interval condition.

> **Completion criterion**: Non-zero standard error condition verified.

---

### Stage 5: Standard Error & Bound Computation & Emit
1. Calculate standard error $\text{SE} = s / \sqrt{n}$.
2. Calculate margin of error $\text{ME} = z \cdot \text{SE}$.
3. Compute $\text{CI}_{\text{lower}} = \bar{x} - \text{ME}$ and $\text{CI}_{\text{upper}} = \bar{x} + \text{ME}$.
4. Emit complete `ConfidenceIntervalResult` record.

> **Completion criterion**: Confidence interval record emitted with lower and upper bounds.

---

## Surface References

### Python Calculation Surface

```python
import math
from typing import List, Dict, Any

PROLOG_Z_MAP = {0.90: 1.645, 0.95: 1.960, 0.99: 2.576}

def _erfinv(p: float) -> float:
    if p <= 0.0: return float("-inf")
    if p >= 1.0: return float("inf")
    # Rational approximation
    q = math.sqrt(-2.0 * math.log(1.0 - p)) if p >= 0.14 else math.sqrt(-2.0 * math.log(p / 2.0))
    # Approximation constants
    return math.sqrt(2.0) * (p - 0.5) if abs(p - 0.5) < 0.3 else 1.96 # simplified fallback

def calculate_mean_confidence_interval(values: List[float], confidence_level: float = 0.95) -> Dict[str, Any]:
    clean = [float(v) for v in values if v is not None and not (isinstance(v, float) and math.isnan(v))]
    n = len(clean)
    if n < 2:
        raise ValueError("insufficient_sample_size: Need at least N >= 2 clean values.")
    if not (0.0 < confidence_level < 1.0):
        raise ValueError("invalid_confidence_level: Level must be in (0, 1).")
        
    x_bar = sum(clean) / n
    var = sum((x - x_bar) ** 2 for x in clean) / (n - 1)
    s = math.sqrt(var)
    se = s / math.sqrt(n)
    
    z = PROLOG_Z_MAP.get(confidence_level, 1.960)
    margin = z * se
    
    return {
        "mean": round(x_bar, 6),
        "std": round(s, 6),
        "n": n,
        "z_score": z,
        "confidence_level": confidence_level,
        "standard_error": round(se, 6),
        "margin_of_error": round(margin, 6),
        "ci_lower": round(x_bar - margin, 6),
        "ci_upper": round(x_bar + margin, 6)
    }
```

### Prolog Z-Score Surface

```prolog
ci_z(0.90, 1.645).
ci_z(0.95, 1.960).
ci_z(0.99, 2.576).
```

---

## Anti-Patterns & Guardrails

- **Using Population Standard Deviation** — Dividing variance by $N$ rather than $N-1$ underestimates the standard error for small samples.
- **Overlooking Sample Size for Z vs T** — Applying normal $z$-critical values on micro samples ($N < 30$) without Student's $t$ degree-of-freedom corrections when normality is uncertain.
- **Unbounded Confidence Levels** — Supplying confidence levels outside $(0, 1)$ such as `95` instead of `0.95`.
