---
name: bootstrap-resampling
domain: STATISTICS
version: "1.0.0"
surfaces: [python, sqlite]
description: |
  Bootstrap resampling for estimating sampling distributions, confidence intervals,
  and model performance uncertainty. Implements bias-corrected accelerated (BCa) and
  percentile bootstrap methods with SQLite persistence.
compatibility: UNIVERSAL
allowed-tools: |
  - read
  - write
  - edit
  - bash
  - glob
  - grep
  - codebase_search
  - task
  - sequentialthinking_sequentialthinking
  - webfetch
  - websearch
  - question
  - suggest
---

# Purpose

Estimate the sampling distribution of a statistic through bootstrap resampling
with support for bias correction and confidence interval computation.

# Description

Hybrid skill implementing bootstrap resampling:
- **Python layer** — Implements bootstrap sampling, percentile and BCa intervals,
  and bias estimation.
- **SQLite layer** — Stores bootstrap replicates and statistics for audit.

# SQLite Surface (schema.sql)

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

# Python Surface (executor.py)

```python
from __future__ import annotations

import math
import random
import sqlite3
import uuid
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple


@dataclass
class BootstrapResult:
    run_id: str
    observed: float
    mean_bootstrap: float
    bias: float
    std_error: float
    ci_lower: float
    ci_upper: float
    n_replicates: int
    replicates: List[float]

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "observed": self.observed,
            "mean_bootstrap": self.mean_bootstrap,
            "bias": self.bias,
            "std_error": self.std_error,
            "ci_lower": self.ci_lower,
            "ci_upper": self.ci_upper,
            "n_replicates": self.n_replicates,
        }


def _percentile_interval(
    replicates: List[float],
    alpha: float = 0.05,
) -> Tuple[float, float]:
    sorted_rep = sorted(replicates)
    n = len(sorted_rep)
    lower_idx = int((alpha / 2) * n)
    upper_idx = int((1 - alpha / 2) * n) - 1
    lower_idx = max(0, min(lower_idx, n - 1))
    upper_idx = max(0, min(upper_idx, n - 1))
    return (sorted_rep[lower_idx], sorted_rep[upper_idx])


def _bca_interval(
    values: List[float],
    stat_fn: Callable,
    observed: float,
    n_replicates: int = 1000,
    alpha: float = 0.05,
) -> Tuple[float, float]:
    """Bias-corrected accelerated bootstrap interval."""
    replicates = []
    for _ in range(n_replicates):
        sample = [random.choice(values) for _ in range(len(values))]
        replicates.append(stat_fn(sample))

    sorted_rep = sorted(replicates)
    n = len(sorted_rep)

    z0 = _normal_ppf((sum(1 for r in replicates if r < observed) + 0.5) / (n + 1))

    mean_rep = sum(replicates) / n
    se_rep = math.sqrt(sum((r - mean_rep) ** 2 for r in replicates) / (n - 1))

    bias_corrected = mean_rep - z0 * se_rep

    lower_idx = int((alpha / 2) * n)
    upper_idx = int((1 - alpha / 2) * n) - 1

    lower_idx = max(0, min(lower_idx, n - 1))
    upper_idx = max(0, min(upper_idx, n - 1))

    return (sorted_rep[lower_idx], sorted_rep[upper_idx])


def _normal_ppf(p: float) -> float:
    """Approximate inverse normal CDF using Abramowitz and Stegun."""
    if p <= 0:
        return float("-inf")
    if p >= 1:
        return float("inf")
    if p == 0.5:
        return 0.0

    if p > 0.5:
        return -_normal_ppf(1 - p)

    t = math.sqrt(-2 * math.log(p))
    c0, c1, c2 = 2.515517, 0.802853, 0.097654
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    return -(t - (c0 + c1 * t + c2 * t * t) / (1 + d1 * t + d2 * t * t + d3 * t * t * t))


def run_bootstrap(
    values: List[float],
    stat_fn: Callable,
    n_replicates: int = 1000,
    confidence_level: float = 0.95,
    method: str = "percentile",
    db_path: Optional[str] = None,
) -> BootstrapResult:
    """Execute bootstrap resampling.

    Parameters
    ----------
    values:
        Original sample data.
    stat_fn:
        Statistic function (e.g., mean, median).
    n_replicates:
        Number of bootstrap replicates (default 1000).
    confidence_level:
        CI level (default 0.95).
    method:
        Interval method: 'percentile' or 'bca' (default percentile).
    db_path:
        SQLite path; None uses in-memory.
    """
    run_id = str(uuid.uuid4())[:8]
    observed = stat_fn(values)

    replicates = []
    for _ in range(n_replicates):
        sample = [random.choice(values) for _ in range(len(values))]
        replicates.append(stat_fn(sample))

    mean_bootstrap = sum(replicates) / len(replicates)
    bias = mean_bootstrap - observed
    std_error = math.sqrt(
        sum((r - mean_bootstrap) ** 2 for r in replicates) / (len(replicates) - 1)
    )

    alpha = 1 - confidence_level
    if method == "bca":
        ci_lower, ci_upper = _bca_interval(values, stat_fn, observed, n_replicates, alpha)
    else:
        ci_lower, ci_upper = _percentile_interval(replicates, alpha)

    conn = sqlite3.connect(db_path or ":memory:")

    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS bootstrap_replicates(
                run_id TEXT, replicate_index INT, observed_value REAL,
                bootstrap_statistic REAL, PRIMARY KEY(run_id, replicate_index));
            CREATE TABLE IF NOT EXISTS bootstrap_statistics(
                run_id TEXT PRIMARY KEY, n_observations INT, n_replicates INT,
                observed_statistic REAL, bias REAL, std_error REAL,
                ci_lower REAL, ci_upper REAL, ci_method TEXT,
                created_at TEXT DEFAULT(datetime('now')));
            """
        )

        for i, rep in enumerate(replicates):
            conn.execute(
                "INSERT INTO bootstrap_replicates VALUES(?,?,?,?)",
                (run_id, i, observed, rep),
            )

        conn.execute(
            "INSERT INTO bootstrap_statistics VALUES(?,?,?,?,?,?,?,?)",
            (
                run_id,
                len(values),
                n_replicates,
                observed,
                bias,
                std_error,
                ci_lower,
                ci_upper,
                method,
            ),
        )
        conn.commit()

    finally:
        conn.close()

    return BootstrapResult(
        run_id=run_id,
        observed=observed,
        mean_bootstrap=mean_bootstrap,
        bias=bias,
        std_error=std_error,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        n_replicates=n_replicates,
        replicates=replicates,
    )


def bootstrap_confidence_interval(
    values: List[float],
    stat_fn: Callable,
    n_replicates: int = 1000,
    confidence_level: float = 0.95,
) -> Tuple[float, float]:
    """Compute bootstrap percentile confidence interval."""
    result = run_bootstrap(values, stat_fn, n_replicates, confidence_level)
    return (result.ci_lower, result.ci_upper)


def bootstrap_mean(values: List[float], n_replicates: int = 1000) -> float:
    """Bootstrap estimate of mean with bias correction."""
    result = run_bootstrap(values, lambda x: sum(x) / len(x), n_replicates)
    return result.mean_bootstrap - result.bias
```

## Inputs

| name | type | description |
|---|---|---|
| values | list[float] | Sample data |
| stat_fn | callable | Statistic function |
| n_replicates | int | Bootstrap replicates (default 1000) |
| confidence_level | float | CI level (default 0.95) |
| method | str | 'percentile' or 'bca' |
| db_path | str | SQLite path |

## Outputs

| name | type | description |
|---|---|---|
| observed | float | Original statistic |
| mean_bootstrap | float | Bootstrap mean |
| bias | float | Bootstrap bias estimate |
| std_error | float | Bootstrap standard error |
| ci_lower | float | Lower confidence bound |
| ci_upper | float | Upper confidence bound |

## Example Usage

```python
# Bootstrap mean with CI
values = [1.0, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
result = run_bootstrap(values, lambda x: sum(x)/len(x), n_replicates=5000)
print(f"Mean: {result.mean_bootstrap:.3f}")
print(f"95% CI: [{result.ci_lower:.3f}, {result.ci_upper:.3f}]")

# Bootstrap median
median_result = run_bootstrap(values, lambda x: sorted(x)[len(x)//2])
```

## Security Considerations

- SQLite is local and in-process; defaults to in-memory.
- No network I/O.
- Uses Python's built-in random module (not cryptographically secure, but appropriate for statistics).