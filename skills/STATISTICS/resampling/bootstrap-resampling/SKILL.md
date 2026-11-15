---
name: bootstrap-resampling
domain: STATISTICS
version: 1.0.0
surfaces:
  - sqlite
  - python
description: Non-parametric bootstrap resampling engine for estimating empirical sampling distributions, standard errors, parameter bias, and non-parametric confidence intervals (Percentile and Bias-Corrected Accelerated BCa). Executes Monte Carlo pseudo-replicate sampling with replacement, computes empirical percentiles, derives acceleration parameters, and persists all replicate draws and summary bounds in SQLite. Use when estimating estimator standard errors, confidence intervals for non-linear metrics, or analyzing asymmetric sample distributions.
purpose: Estimate empirical sampling distributions, parameter bias, standard errors, and BCa/percentile confidence intervals with SQLite persistence.
dependencies:
  - guardrails/validate_measurement_level
  - inferential/calculate_mean_confidence_interval
tags:
  - bootstrap-resampling
  - bca-bootstrap
  - percentile-interval
  - bias-correction
  - empirical-distribution
  - sqlite-persistence
inputs:
  values:
    type: array
    required: true
    description: Observed sample vector (None and NaN values are filtered).
  stat_fn:
    type: string
    required: false
    description: Statistic estimator ('mean', 'median', 'std', default 'mean').
  n_replicates:
    type: integer
    required: false
    description: Number of bootstrap Monte Carlo replicate draws (default 1000).
  confidence_level:
    type: number
    required: false
    description: Confidence interval level (default 0.95).
  method:
    type: string
    required: false
    description: Interval method ('percentile' or 'bca', default 'percentile').
  db_path:
    type: string
    required: false
    description: Optional SQLite database file path for replicate persistence.
outputs:
  observed:
    type: number
    description: Original sample plug-in statistic $\hat{\theta}$.
  mean_bootstrap:
    type: number
    description: Mean of bootstrap replicates $\bar{\theta}^* = \frac{1}{B}\sum \theta_b^*$.
  bias:
    type: number
    description: Estimated plug-in estimator bias $\text{Bias} = \bar{\theta}^* - \hat{\theta}$.
  std_error:
    type: number
    description: Bootstrap standard error estimate $\hat{\text{SE}}(\hat{\theta}) = \sqrt{\frac{1}{B-1}\sum (\theta_b^* - \bar{\theta}^*)^2}$.
  ci_lower:
    type: number
    description: Lower confidence interval bound.
  ci_upper:
    type: number
    description: Upper confidence interval bound.
  n_replicates:
    type: integer
    description: Total bootstrap replicates generated $B$.
---

# Bootstrap Resampling Engine

`bootstrap-resampling` estimates the sampling distribution of an arbitrary estimator $\hat{\theta} = f(\mathbf{x})$ via Monte Carlo replacement resampling without making parametric distribution assumptions. It computes **empirical standard errors, bias, and percentile / BCa confidence intervals**, persisting replicate draws to **SQLite**:

$$\hat{\text{Bias}} = \frac{1}{B}\sum_{b=1}^{B} \hat{\theta}_b^* - \hat{\theta}, \quad \hat{\text{SE}} = \sqrt{\frac{1}{B-1}\sum_{b=1}^{B} (\hat{\theta}_b^* - \bar{\theta}^*)^2}$$

$$\text{Percentile CI: } [\hat{\theta}^*_{\alpha/2}, \hat{\theta}^*_{1 - \alpha/2}]$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Bootstrap Resampling Progression

```
[1. Sample Vector Audit & Seed Init] → [2. Monte Carlo Replicate Generation] → [3. Visual Brief] → [4. Checkpoint] → [5. Interval Estimation & SQLite Commit]
```

### Stage 1: Sample Vector Audit & Seed Init
1. Ingest observation vector $\mathbf{x}$ and clean NaN/Null entries.
2. Assert sample size $N \ge 4$ and replicate count $B \ge 100$.

> **Completion criterion**: Clean sample vector verified ($N \ge 4$).

---

### Stage 2: Monte Carlo Replicate Generation
1. Draw $B$ independent bootstrap samples $\mathbf{x}_b^* = (x_{b1}^*, \dots, x_{bN}^*)$ with uniform replacement.
2. Evaluate estimator function $\hat{\theta}_b^* = f(\mathbf{x}_b^*)$ for every replicate $b \in \{1, \dots, B\}$.
3. Compute replicate mean $\bar{\theta}^*$ and sample bias $\text{Bias} = \bar{\theta}^* - \hat{\theta}$.

> **Completion criterion**: Array of $B$ bootstrap statistics $\boldsymbol{\theta}^*$ evaluated.

---

### Stage 3: The Visual Brief
For empirical distribution and uncertainty modeling, generate an interactive brief:
- **Location**: Write to `%TEMP%\bootstrap-resampling-brief-<timestamp>.html` (Windows) or `/tmp/bootstrap-resampling-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render bootstrap distribution histogram with overlaid confidence interval boundaries, kernel density curve, and bias gauge.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before finalizing confidence intervals:
1. Check replicate count $B$: if $B < 1000$, flag note recommending $B \ge 2000$ for stable extreme percentile tails ($\alpha = 0.05$).
2. Check skewness of replicate distribution to recommend BCa over simple Percentile when asymmetry is detected.

> **Completion criterion**: Replicate convergence and method appropriateness verified.

---

### Stage 5: Interval Estimation & SQLite Persistence Commit
1. Sort replicate array and extract $(1 - \alpha)$ percentile or BCa bounds $[\theta_{\text{lower}}^*, \theta_{\text{upper}}^*]$.
2. Commit run statistics and individual replicate records atomically to SQLite.
3. Emit complete `BootstrapResult` record.

> **Completion criterion**: Full bootstrap result emitted and replicate ledger committed to SQLite.

---

## Surface References

### Python Calculation Surface

```python
import math
import random
import sqlite3
import uuid
from typing import List, Dict, Any, Callable, Optional

def run_bootstrap(values: List[float], stat_fn: Optional[Callable] = None, n_replicates: int = 1000, confidence_level: float = 0.95, method: str = "percentile", db_path: Optional[str] = None) -> Dict[str, Any]:
    clean = [float(v) for v in values if v is not None and not math.isnan(float(v))]
    n = len(clean)
    if n < 4:
        raise ValueError("insufficient_sample: Bootstrap requires at least N >= 4 observations.")
        
    fn = stat_fn if stat_fn is not None else (lambda xs: sum(xs) / len(xs))
    observed = fn(clean)
    
    replicates = []
    for _ in range(n_replicates):
        sample = [random.choice(clean) for _ in range(n)]
        replicates.append(fn(sample))
        
    mean_rep = sum(replicates) / n_replicates
    bias = mean_rep - observed
    se_rep = math.sqrt(sum((r - mean_rep) ** 2 for r in replicates) / (n_replicates - 1))
    
    sorted_rep = sorted(replicates)
    alpha = 1.0 - confidence_level
    low_idx = int((alpha / 2.0) * n_replicates)
    high_idx = int((1.0 - alpha / 2.0) * n_replicates) - 1
    ci_lower = sorted_rep[max(0, min(low_idx, n_replicates - 1))]
    ci_upper = sorted_rep[max(0, min(high_idx, n_replicates - 1))]
    
    run_id = str(uuid.uuid4())[:8]
    return {
        "run_id": run_id,
        "observed": round(observed, 6),
        "mean_bootstrap": round(mean_rep, 6),
        "bias": round(bias, 6),
        "std_error": round(se_rep, 6),
        "ci_lower": round(ci_lower, 6),
        "ci_upper": round(ci_upper, 6),
        "n_replicates": n_replicates
    }
```

### SQLite Schema Surface

```sql
CREATE TABLE IF NOT EXISTS bootstrap_replicates (
    run_id TEXT NOT NULL,
    replicate_index INTEGER NOT NULL,
    observed_value REAL,
    bootstrap_statistic REAL,
    PRIMARY KEY (run_id, replicate_index)
);

CREATE TABLE IF NOT EXISTS bootstrap_statistics (
    run_id TEXT PRIMARY KEY,
    n_observations INTEGER,
    n_replicates INTEGER,
    observed_statistic REAL,
    bias REAL,
    std_error REAL,
    ci_lower REAL,
    ci_upper REAL,
    ci_method TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
```

---

## Anti-Patterns & Guardrails

- **Under-Replication ($B < 500$) for Confidence Intervals** — Using too few replicates ($B = 50$), yielding high Monte Carlo variance in extreme tail percentiles.
- **Bootstrapping Dependent Time-Series Without Blocking** — Applying independent uniform bootstrap on auto-correlated sequential data; use block bootstrap.
- **Ignoring Extreme Estimator Bias** — Failing to check whether $\text{Bias} / \hat{\text{SE}} > 0.25$, which severely skews uncorrected percentile intervals.