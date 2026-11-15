---
name: statistical-bootstrap-analyzer
domain: STATISTICS
version: 1.0.0
surfaces:
  - python
  - prolog
  - hy
description: Multi-surface statistical bootstrap analyzer for high-precision empirical confidence interval estimation, plug-in statistic uncertainty scoring, and two-sample bootstrap hypothesis testing. Enforces bootstrap validity ratios in Prolog, computes pure stdlib/NumPy accelerated resampling in Python, and evaluates Lisp-based bootstrap quality and stability scores in Hy. Use when conducting advanced multi-surface resampling simulations or estimating non-standard metric distributions.
purpose: Execute multi-surface bootstrap resampling simulations with Prolog design bounds and Hy uncertainty scoring.
dependencies:
  - guardrails/validate_measurement_level
  - resampling/bootstrap-resampling
tags:
  - statistical-bootstrap
  - multi-surface
  - hy-uncertainty
  - prolog-bounds
  - empirical-ci
  - non-parametric
inputs:
  data:
    type: array
    required: true
    description: Sample observation array (single vector or paired groups).
  n_bootstrap:
    type: integer
    required: false
    description: Number of bootstrap Monte Carlo replicate draws (default 10000).
  alpha:
    type: number
    required: false
    description: Significance threshold for confidence interval (default 0.05).
outputs:
  observed_statistic:
    type: number
    description: Plug-in sample statistic.
  ci_lower:
    type: number
    description: Lower bootstrap percentile confidence bound.
  ci_upper:
    type: number
    description: Upper bootstrap percentile confidence bound.
  bootstrap_quality_score:
    type: number
    description: Hy evaluation of Monte Carlo resampling coverage quality $\in [0.0, 1.0]$.
  standard_error:
    type: number
    description: Empirical standard error of bootstrap distribution.
---

# Statistical Bootstrap Analyzer Engine

`statistical-bootstrap-analyzer` coordinates multi-surface bootstrap estimation across **Prolog** (replicate bounds gating), **Python** (high-throughput Monte Carlo sampling), and **Hy** (uncertainty and stability quality scoring):

$$\text{Replicate Ratio: } R = \frac{N_{\text{boot}}}{N_{\text{obs}}}, \quad \text{Quality Score: } Q = \min\left(1.0, \frac{R}{100}\right)$$

$$[\text{CI}_{\text{lower}}, \text{CI}_{\text{upper}}] = [P_{100 \cdot \alpha / 2}(\boldsymbol{\theta}^*), P_{100 \cdot (1 - \alpha / 2)}(\boldsymbol{\theta}^*)]$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Multi-Surface Bootstrap Progression

```
[1. Sample Vector Audit] → [2. Prolog Ratio Precondition Check] → [3. Visual Brief] → [4. Checkpoint] → [5. Multi-Surface Resample & Hy Score Emit]
```

### Stage 1: Sample Vector Audit
1. Ingest observation vector $\mathbf{x}$; drop NaN and null entries.
2. Assert sample size $N_{\text{obs}} \ge 5$.

> **Completion criterion**: Clean observation vector verified ($N \ge 5$).

---

### Stage 2: Prolog Ratio Precondition Check
1. Assert design bounds into Prolog engine:
   ```prolog
   valid_bootstrap(NObs, NBoot) :- NBoot >= NObs, NBoot =< 100000.
   ```
2. Verify that $N_{\text{boot}} \ge N_{\text{obs}}$.

> **Completion criterion**: Bootstrap sample-to-replicate ratio certified in Prolog.

---

### Stage 3: The Visual Brief
For empirical distribution and resampling stability review, generate an interactive brief:
- **Location**: Write to `%TEMP%\stat-bootstrap-brief-<timestamp>.html` (Windows) or `/tmp/stat-bootstrap-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render bootstrap empirical distribution density curve, confidence interval bounds marker, and Hy quality score gauge.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before finalizing output payload:
1. Verify empirical standard error: $\hat{\text{SE}} > 0$.
2. Evaluate replicate coverage: $N_{\text{boot}} \ge 5000$ for narrow confidence interval estimation.

> **Completion criterion**: Bootstrap distribution variance verified.

---

### Stage 5: Multi-Surface Resample & Hy Quality Scoring
1. Compute $N_{\text{boot}}$ replicate draws and extract empirical $(1 - \alpha)$ percentile interval.
2. Compute Hy quality stability score: $Q = \min(1.0, (N_{\text{boot}} / N_{\text{obs}}) / 100)$.
3. Emit complete `BootstrapAnalysisResult` record.

> **Completion criterion**: Complete multi-surface statistical record emitted.

---

## Surface References

### Python Calculation Surface

```python
import math
import random
from typing import List, Dict, Any, Callable, Optional

def run_statistical_bootstrap(data: List[float], n_bootstrap: int = 10000, alpha: float = 0.05, stat_fn: Optional[Callable] = None) -> Dict[str, Any]:
    clean = [float(v) for v in data if v is not None and not math.isnan(float(v))]
    n_obs = len(clean)
    if n_obs < 5:
        raise ValueError("insufficient_sample: Bootstrap analyzer requires N >= 5 observations.")
        
    fn = stat_fn if stat_fn is not None else (lambda xs: sum(xs) / len(xs))
    observed = fn(clean)
    
    replicates = []
    for _ in range(n_bootstrap):
        sample = [random.choice(clean) for _ in range(n_obs)]
        replicates.append(fn(sample))
        
    sorted_rep = sorted(replicates)
    low_idx = max(0, min(int((alpha / 2.0) * n_bootstrap), n_bootstrap - 1))
    high_idx = max(0, min(int((1.0 - alpha / 2.0) * n_bootstrap) - 1, n_bootstrap - 1))
    
    mean_boot = sum(replicates) / n_bootstrap
    se_boot = math.sqrt(sum((r - mean_boot) ** 2 for r in replicates) / (n_bootstrap - 1))
    
    # Hy quality score mirror
    ratio = n_bootstrap / n_obs
    quality_score = min(1.0, ratio / 100.0)
    
    return {
        "n_obs": n_obs,
        "n_bootstrap": n_bootstrap,
        "observed_statistic": round(observed, 6),
        "ci_lower": round(sorted_rep[low_idx], 6),
        "ci_upper": round(sorted_rep[high_idx], 6),
        "standard_error": round(se_boot, 6),
        "bootstrap_quality_score": round(quality_score, 4)
    }
```

### Prolog Bounds Surface

```prolog
valid_bootstrap(NObs, NBoot) :-
    NBoot >= NObs,
    NBoot =< 100000.

confidence_interval_contains(Lower, Upper, TrueValue) :-
    Lower =< TrueValue,
    TrueValue =< Upper.
```

---

## Anti-Patterns & Guardrails

- **Insufficient Replicate Ratio** — Using $N_{\text{boot}} < N_{\text{obs}}$, which fails to adequately populate the empirical discrete probability simplex.
- **Excessive Replicates on Micro-Data** — Running $N_{\text{boot}} > 100,000$ on $N_{\text{obs}} = 5$ without gaining true distribution resolution ($\binom{2N-1}{N}$ unique combinations).
- **Ignoring Degenerate Sample Variance** — Bootstrapping constant vectors ($x_i = c$), producing zero variance confidence bounds.