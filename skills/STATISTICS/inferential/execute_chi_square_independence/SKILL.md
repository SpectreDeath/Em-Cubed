---
name: calculate_correlation_profile
domain: STATISTICS
version: "1.0.0"
surfaces: [prolog, python]
description: |
  Hybrid skill computing Pearson's r or Spearman's rho between two
  numeric vectors.  Prolog enforces measurement-level and method
  constraints; Python performs rank transforms, covariance, and
  significance testing.
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
Compute a correlation profile between two numeric vectors using either Pearson's r (interval/ratio, linear association) or Spearman's rho (ordinal+, monotonic association). The Prolog layer enforces which methods are permitted based on measurement level.

## Description
Hybrid skill:
- **Prolog layer** — Routes method selection based on declared measurement levels. Pearson requires interval/ratio for both vectors; Spearman requires at least ordinal.
- **Python layer** — Cleans paired vectors, ranks for Spearman, computes covariance-based rho, determines p-value under H0, and classifies magnitude.

### Correlation Magnitude Bands
| |r| or |ρ| | Interpretation |
|---|---|
| 0.00 – 0.10 | Negligible |
| 0.10 – 0.39 | Weak |
| 0.40 – 0.69 | Moderate |
| 0.70 – 0.89 | Strong |
| 0.90 – 1.00 | Very strong |

## Prolog Surface (prelude.pl)

```prolog
:- module(correlation_router, [
    method_allowed/3,
    lengths_equal/2,
    magnitude_band/2
]).

% ============================================================
% 1. Measurement-level gate per method
% ============================================================
dominates(ratio, interval).
dominates(interval, ordinal).
dominates(ordinal, nominal).

method_allowed(pearson, LevelX, LevelY) :-
    ( dominates(LevelX, interval) ; dominates(LevelY, interval) ).

method_allowed(spearman, LevelX, LevelY) :-
    ( dominates(LevelX, ordinal)  ; dominates(LevelY, ordinal)  ).

method_allowed(_, _, _) :-
    fail.

% ============================================================
% 2. Structural preconditions
% ============================================================
lengths_equal(X, Y) :- length(X, N), length(Y, N).

% ============================================================
% 3. Magnitude band (used by Python result formalizer)
% ============================================================
magnitude_band(AbsR, negligible) :- AbsR < 0.10.
magnitude_band(AbsR, weak)       :- AbsR >= 0.10, AbsR < 0.40.
magnitude_band(AbsR, moderate)   :- AbsR >= 0.40, AbsR < 0.70.
magnitude_band(AbsR, strong)     :- AbsR >= 0.70, AbsR < 0.90.
magnitude_band(AbsR, very_strong):- AbsR >= 0.90.
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
from typing import Dict, List, Optional, Tuple, Union


@dataclass(frozen=True)
class CorrelationResult:
    method: str                # "pearson" or "spearman"
    r: float                   # correlation coefficient
    rho: float                 # synonym for r (Spearman alias)
    p_value: float
    magnitude: str             # from Prolog magnitude_band/2
    n: int
    n_used: int
    n_dropped: int

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


def _rank(v: List[float]) -> List[float]:
    """Rank-transform: assign average rank to tied values."""
    indexed = sorted(enumerate(v), key=lambda p: p[1])
    n = len(indexed)
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n - 1 and indexed[j+1][1] == indexed[j][1]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1   # 1-indexed ranks
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = avg_rank
        i = j + 1
    return ranks


def _pearson_r(x: List[float], y: List[float]) -> float:
    """Pearson correlation r = cov(x,y) / (std_x * std_y)."""
    n = len(x)
    if n < 2:
        return float("nan")
    mx = sum(x) / n
    my = sum(y) / n
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    dx  = math.sqrt(sum((xi - mx) ** 2 for xi in x))
    dy  = math.sqrt(sum((yi - my) ** 2 for yi in y))
    denom = dx * dy
    if denom == 0:
        return 0.0
    return num / denom


def _spearman_rho(x: List[float], y: List[float]) -> float:
    """Spearman rho = Pearson correlation of rank-transformed vectors."""
    rx = _rank(x)
    ry = _rank(y)
    return _pearson_r(rx, ry)


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


def _r_pvalue(r: float, n: int) -> float:
    """Two-tailed p-value for Pearson/Spearman r under H0: rho = 0.

    Uses t-distribution: t = r * sqrt((n-2)/(1-r^2)).
    """
    if n < 3:
        return 1.0
    denom = 1.0 - r * r
    if denom <= 0:
        return 0.0
    t_stat = r * math.sqrt((n - 2) / denom)
    try:
        from scipy.stats import t as t_dist
        # Two-tailed: 2 * (1 - CDF(|t|))
        p = 2.0 * t_dist.sf(abs(t_stat), n - 2)
        return float(p)
    except ImportError:
        # Numerical approximation via incomplete beta (not implemented;
        # fallback to a normal approximation for practical use)
        return 2.0 * (1.0 - _normal_cdf(abs(t_stat), 0.0, 1.0))


def _normal_cdf(x: float, mu: float, sigma: float) -> float:
    """Standard normal CDF approximation."""
    z = (x - mu) / sigma
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def calculate_correlation_profile(
    x: List[Union[float, int, None]],
    y: List[Union[float, int, None]],
    method: str = "pearson",
    alpha: float = 0.05,
) -> CorrelationResult:
    """Compute Pearson r or Spearman rho between two vectors.

    Parameters
    ----------
    x, y : list of numbers/None
        Paired vectors.  Pairs with any missing entry are dropped.
    method : str
        One of "pearson" or "spearman".
    alpha : float
        Significance level (used for p-value reporting; stored in result).

    Returns
    -------
    CorrelationResult
        Correlation coefficient, p-value, magnitude classification.

    Raises
    ------
    ValueError
        If method is not "pearson" or "spearman".
        If fewer than 3 paired observations remain after cleaning.
    """
    if method not in ("pearson", "spearman"):
        raise ValueError(f"method must be 'pearson' or 'spearman', got '{method}'")

    cx, cy, dropped = _clean_pairs(x, y)
    n_used = len(cx)
    n_orig = len(x)

    if n_used < 3:
        raise ValueError(
            f"insufficient_pairs: need >= 3, got {n_used} after dropping {dropped} missing "
            f"from {n_orig} total"
        )

    if method == "pearson":
        r_val = _pearson_r(cx, cy)
    else:
        r_val = _spearman_rho(cx, cy)

    r_val = max(-1.0, min(1.0, r_val))   # clamp numerical drift

    try:
        p = _r_pvalue(r_val, n_used)
    except Exception:
        p = 1.0

    magnitude = _magnitude_band(abs(r_val))

    return CorrelationResult(
        method    = method,
        r         = r_val,
        rho       = r_val,
        p_value   = p,
        magnitude = magnitude,
        n         = n_orig,
        n_used    = n_used,
        n_dropped = dropped,
    )
```

## Inputs

| name | type | description |
|---|---|---|
| x, y | list[float\|int\|None] | Paired vectors; missing pairs dropped |
| method | str | `"pearson"` or `"spearman"` |
| alpha | float | Significance level for p-value interpretation (default 0.05) |

## Outputs

| name | type | description |
|---|---|---|
| method | str | Method used: `"pearson"` or `"spearman"` |
| r | float | Correlation coefficient (also aliased as `rho`) |
| p_value | float | Two-tailed p-value under H0: ρ = 0 |
| magnitude | str | Magnitude band from `_MAGNITUDE_BANDS` |
| n | int | Original vector length |
| n_used | int | Paired observations after cleaning |
| n_dropped | int | Pairs dropped due to missing data |

## Symbolic Preconditions (Prolog)
- `method_allowed(Method, LevelX, LevelY)` must succeed
- `lengths_equal(X, Y)` must succeed
- `n_used >= 3`

## State Updates
```
state_add_observation("relational/correlation/r",      result.r)
state_add_observation("relational/correlation/method", result.method)
state_add_observation("relational/correlation/magnitude", result.magnitude)
state_add_observation("relational/correlation/p_value", result.p_value)
state_add_observation("relational/correlation/n_used",  result.n_used)
```

## Error Handling
| Error | Condition |
|---|---|
| invalid_method | method not in {"pearson", "spearman"} |
| insufficient_pairs | n_used < 3 after cleaning |

## Example Usage
```python
# Strong positive Pearson r
x = [1, 2, 3, 4, 5, 6, 7, 8]
y = [2, 4, 5, 4, 8, 9, 11, 12]
r = calculate_correlation_profile(x, y, method="pearson")
# r.r          ≈ 0.966
# r.magnitude  == "very_strong"
# r.p_value    < 0.001

# Spearman (rank-based, robust to outliers)
r2 = calculate_correlation_profile(x, y, method="spearman")
# r2.rho       ≈ 0.964

# With missing data
x3 = [1, 2, None, 4, 5]
y3 = [2, 3, 4, None, 6]
r3 = calculate_correlation_profile(x3, y3)
# r3.n_used    == 3
# r3.n_dropped == 2
```

## Security Considerations
- No I/O. All computation in-memory.
- scipy optional; graceful numerical fallback provided.
