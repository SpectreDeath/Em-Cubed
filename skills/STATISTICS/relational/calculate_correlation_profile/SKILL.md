---
name: calculate_correlation_profile
domain: STATISTICS
version: "1.0.0"
surfaces: [prolog, python]
description: |
  Hybrid skill computing Pearson's r or Spearman's rho between two
  numeric vectors.  Prolog enforces measurement-level and method
  constraints; Python performs rank transforms, covariance computation,
  and significance testing.
compatibility: PYTHON, PROLOG
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

# Calculate Correlation Profile

## Purpose
Compute a correlation profile between two numeric vectors using either Pearson's r (interval/ratio, linear association) or Spearman's rho (ordinal+, monotonic association). The Prolog layer enforces which methods are permitted based on declared measurement level.

## Description
Hybrid skill:
- **Prolog layer** — Routes method selection based on declared measurement levels. Pearson requires both vectors at interval/ratio. Spearman requires at least ordinal for both vectors. Vector length equality is also enforced.
- **Python layer** — Cleans paired vectors (dropping rows with NA), computes rank transforms for Spearman, calculates covariance-based coefficient, and computes p-value for H0: rho = 0.

### Correlation Magnitude Bands
| |r| or |ρ| | Magnitude |
|---|---|
| 0.00 – 0.10 | negligible |
| 0.10 – 0.39 | weak |
| 0.40 – 0.69 | moderate |
| 0.70 – 0.89 | strong |
| 0.90 – 1.00 | very_strong |

## Prolog Surface (prelude.pl)

```prolog
:- module(correlation_router, [
    dominates/2,
    method_allowed/3,
    lengths_equal/2,
    magnitude_band/2
]).

% ============================================================
% 1. Measurement hierarchy (mirrors guardrails/validate_measurement_level)
% ============================================================
dominates(ratio,    interval).
dominates(interval, ordinal).
dominates(ordinal,  nominal).

% ============================================================
% 2. Method routing by measurement level
% ============================================================
method_allowed(pearson, LevelX, LevelY) :-
    dominates(LevelX, interval),
    dominates(LevelY, interval).

method_allowed(spearman, LevelX, LevelY) :-
    dominates(LevelX, ordinal),
    dominates(LevelY, ordinal).

% ============================================================
% 3. Structural preconditions
% ============================================================
lengths_equal(X, Y) :- length(X, N), length(Y, N).

% ============================================================
ed subroutine]
)
% 4. Magnitude band (used by Python result interpreter)
% ============================================================
magnitude_band(AbsR, negligible) :- AbsR < 0.10, !.
magnitude_band(AbsR, weak)       :- AbsR < 0.40, !.
magnitude_band(AbsR, moderate)   :- AbsR < 0.70, !.
magnitude_band(AbsR, strong)     :- AbsR < 0.90, !.
magnitude_band(_, very_strong).
```

## Python Surface (executor.py)

```python
"""
calculate_correlation_profile
===============================
Hybrid skill: symbolic method routing + algorithmic correlation computation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union


@dataclass(frozen=True)
class CorrelationResult:
    """Correlation analysis result."""
    method: str                # "pearson" or "spearman"
    r: float                   # Pearson correlation coefficient
    rho: float                 # Spearman rho (same shape, different method)
    p_value: float
    magnitude: str             # from magnitude_band classification
    n: int                     # Original vector length
    n_used: int                # Pairs used after cleaning
    n_dropped: int             # Pairs dropped due to missing data

    def to_dict(self) -> dict:
        return {
            "method":     self.method,
            "r":          self.r,
            "rho":        self.rho,
            "p_value":    self.p_value,
            "magnitude":  self.magnitude,
            "n":          self.n,
            "n_used":     self.n_used,
            "n_dropped":  self.n_dropped,
        }


def _clean_pairs(
    x: List[Union[float, int, None]],
    y: List[Union[float, int, None]],
) -> Tuple[List[float], List[float], int]:
    """Drop rows where either x or y is missing."""
    dropped = 0
    cx: List[float] = []
    cy: List[float] = []
    for a, b in zip(x, y):
        a_ok = a is not None and not (isinstance(a, float) and math.isnan(a))
        b_ok = b is not None and not (isinstance(b, float) and math.isnan(b))
        if a_ok and b_ok:
            cx.append(float(a))
            cy.append(float(b))
        else:
            dropped += 1
    return cx, cy, dropped


def _rank(values: List[float]) -> List[float]:
    """Rank-transform with average-rank tie handling."""
    indexed = sorted(enumerate(values), key=lambda p: p[1])
    n = len(indexed)
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n - 1 and indexed[j + 1][1] == indexed[j][1]:
            j += 1
        avg_rank = sum(range(i + 1, j + 2)) / (j - i + 1)
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = float(avg_rank)
        i = j + 1
    return ranks


def _pearson_r(x: List[float], y: List[float]) -> float:
    """Pearson correlation: cov(x, y) / (std(x) * std(y))."""
    n = len(x)
    if n < 2:
        raise ValueError("insufficient_pairs")
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    dx  = math.sqrt(sum((xi - mean_x) ** 2 for xi in x))
    dy  = math.sqrt(sum((yi - mean_y) ** 2 for yi in y))
    denom = dx * dy
    if denom == 0:
        return 0.0
    return num / denom


def _spearman_rho(x: List[float], y: List[float]) -> float:
    """Spearman rho: Pearson correlation of rank-transformed vectors."""
    rx = _rank(x)
    ry = _rank(y)
    return _pearson_r(rx, ry)


def _pearson_pvalue(r: float, n: int) -> float:
    """Two-tailed p-value for Pearson r under H0: population rho = 0.

    Uses t-statistic: t = r * sqrt((n - 2) / (1 - r^2)), df = n - 2.
    """
    if n < 3:
        return 1.0
    denom = 1.0 - r * r
    if denom <= 0:
        return 0.0
    t_stat = abs(r * math.sqrt((n - 2) / denom))
    try:
        from scipy.stats import t as t_dist
        return float(2.0 * t_dist.sf(t_stat, n - 2))
    except ImportError:
        return _normal_approximation(t_stat)


def _normal_approximation(t: float) -> float:
    """Two-tailed p via standard normal survival (fallback when no scipy)."""
    p = 2.0 * (1.0 - _normal_cdf(t, 0.0, 1.0))
    return min(1.0, max(0.0, p))


def _normal_cdf(x: float, mu: float, sigma: float) -> float:
    z = (x - mu) / (sigma * math.sqrt(2.0))
    return 0.5 * (1.0 + math.erf(z))


# magnitude band thresholds (mirrors Prolog magnitude_band/2)
_MAGNITUDE_BANDS = [
    (0.90, "very_strong"),
    (0.70, "strong"),
    (0.40, "moderate"),
    (0.10, "weak"),
    (0.00, "negligible"),
]


def _magnitude_band(abs_r: float) -> str:
    for threshold, label in _MAGNITUDE_BANDS:
        if abs_r >= threshold:
            return label
    return "negligible"


def calculate_correlation_profile(
    x: List[Union[float, int, None]],
    y: List[Union[float, int, None]],
    method: str = "pearson",
    alpha: float = 0.05,
) -> CorrelationResult:
    """Compute Pearson r or Spearman rho between two paired vectors.

    Parameters
    ----------
    x, y : list of numbers/None
        Paired vectors.  Rows where either entry is None/NaN are dropped.
    method : str
        "pearson" (linear, interval/ratio) or "spearman" (monotonic, ordinal+).
    alpha : float
        Significance threshold (stored in result; used for hypothesis decision).

    Returns
    -------
    CorrelationResult

    Raises
    ------
    ValueError
        Method not in {"pearson", "spearman"} or fewer than 3 valid pairs.
    """
    if method not in ("pearson", "spearman"):
        raise ValueError(
            f"method must be 'pearson' or 'spearman', got '{method}'"
        )

    cx, cy, dropped = _clean_pairs(x, y)
    n_used   = len(cx)
    n_orig   = len(x)

    if n_used < 3:
        raise ValueError(
            f"insufficient_pairs: need >= 3, got {n_used} after dropping "
            f"{dropped} from {n_orig} total"
        )

    if method == "pearson":
        r_val = _pearson_r(cx, cy)
    else:
        r_val = _spearman_rho(cx, cy)

    r_val = max(-1.0, min(1.0, r_val))
    p_val = _pearson_pvalue(r_val, n_used)
    mag   = _magnitude_band(abs(r_val))

    return CorrelationResult(
        method    = method,
        r         = r_val,
        rho       = r_val,
        p_value   = p_val,
        magnitude = mag,
        n         = n_orig,
        n_used    = n_used,
        n_dropped = dropped,
    )
```

## Inputs

| name | type | description |
|---|---|---|
| x, y | list[number\|None] | Paired vectors; rows with any NA dropped |
| method | str | `"pearson"` or `"spearman"` |
| alpha | float | Significance threshold (default 0.05) |

## Outputs

| name | type | description |
|---|---|---|
| method | str | Method used |
| r | float | Pearson correlation (or Spearman rho equivalently) |
| rho | float | Alias of r for Spearman compatibility |
| p_value | float | Two-tailed p-value under H0: rho = 0 |
| magnitude | str | Magnitude band classification |
| n | int | Original vector length |
| n_used | int | Valid pairs after cleaning |
| n_dropped | int | Dropped pairs count |

## Symbolic Preconditions (Prolog)
- `lengths_equal(X, Y)` — vectors must be same length
- `method_allowed(Method, LevelX, LevelY)` — measurement level gate
- `n_used >= 3`

## State Updates
```
state_add_observation("relational/correlation/method",    result.method)
state_add_observation("relational/correlation/r",         result.r)
state_add_observation("relational/correlation/magnitude", result.magnitude)
state_add_observation("relational/correlation/p_value",   result.p_value)
belief_add(correlation_computed(DatasetId, X, Y, Method, Result))
```

## Error Handling
| Error | Condition | Behavior |
|---|---|---|
| invalid_method | method not in {"pearson", "spearman"} | Raise ValueError |
| insufficient_pairs | n_used < 3 after cleaning | Raise ValueError |

## Example Usage
```python
x = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
y = [2.1, 3.9, 6.2, 7.8, 10.1, 11.9, 14.2, 15.8]

r = calculate_correlation_profile(x, y, method="pearson")
# r.r         ≈ 0.999
# r.magnitude == "very_strong"
# r.p_value   << 0.001

r2 = calculate_correlation_profile(x, y, method="spearman")
# r2.rho      == 1.0   (perfect monotonic relationship)

# With missing data
x3 = [1.0, 2.0, None, 4.0, 5.0, 6.0, 7.0]
y3 = [2.1, 3.9, 6.2, None, 10.1, 11.9, 14.2]
r3 = calculate_correlation_profile(x3, y3)
# r3.n_used   == 5
# r3.n_dropped == 2
```

## Security Considerations
- No I/O. All computation in-memory.
- scipy optional; normal approximation fallback provided.
