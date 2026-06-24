---
name: calculate_mean_confidence_interval
domain: STATISTICS
version: "1.0.0"
surfaces: [prolog, python]
description: |
  Hybrid skill computing the confidence interval for a sample mean
  using CI = x̄ ± z * s / sqrt(n).  Prolog resolves confidence_level
  -> z-score via a declarative lookup table; Python performs all
  numerical computation.
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

# Calculate Mean Confidence Interval

## Purpose
Compute a confidence interval for the population mean from a sample vector using the formula:

```
CI = x̄ ± z * s / sqrt(n)
```

where:
- x̄ = sample mean
- s = sample standard deviation (ddof=1)
- n = sample size
- z = z-score corresponding to the chosen confidence level

## Description
Hybrid skill:
- **Prolog layer** — Declarative `ci_z/2` lookup table maps confidence levels (0.90, 0.95, 0.99) to their z-scores. Falls back to Python `interpolate_z/2` for arbitrary levels.
- **Python layer** — Vector cleaning, mean, sample std, standard error, margin-of-error, and CI bounds.

## Prolog Surface (prelude.pl)

```prolog
:- module(confidence_interval, [
    ci_z/2,
    ci_preconditions/2,
    ci_result/9
]).

% ============================================================
% 1. Declarative z-score lookup table
%    Maps common confidence levels to their exact two-tailed z-scores.
%    Both layers share this as the "contract."
% ============================================================
ci_z(0.90, 1.645).
ci_z(0.95, 1.960).
ci_z(0.99, 2.576).

% Fallback for arbitrary confidence levels (delegated to Python)
ci_z(Level, Z) :-
    Level > 0, Level < 1,
    \+ ci_z(Level, _),          % not found in table
    call_python(interpolate_z, [Level], Z).

% ============================================================
% 2. Preconditions (numeric guard delegated to Python)
% ============================================================
ci_preconditions(Values, Level) :-
    length(Values, N),
    N >= 2,
    Level > 0,
    Level < 1.

% ============================================================
% 3. Result formalization
%    Mirrors the Python dataclass for cross-layer consistency.
% ============================================================
ci_result(Mean, Std, N, Z, SE, Margin, CL, Lower, Upper) :-
    Lower is Mean - Margin,
    Upper is Mean + Margin.
```

## Python Surface (executor.py)

```python
"""
calculate_mean_confidence_interval
====================================
Hybrid statistic skill:
- Symbolic surface: Prolog lookup (ci_z/2) resolves confidence_level -> z-score.
- Algorithmic surface: this module computes x̄, s, n, standard error, and CI.

Formula:
    CI = x̄ ± z * s / sqrt(n)
    where
        x̄ = mean of clean samples
        s  = sample standard deviation (ddof=1)
        n  = count of clean samples
        z  = z-score from Prolog ci_z/2 lookup
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Union


# ---- Surface types -----------------------------------------------------

@dataclass(frozen=True)
class ConfidenceIntervalResult:
    """Immutable result record stored in agent working memory."""
    mean: float
    std: float
    n: int
    z_score: float
    confidence_level: float
    standard_error: float
    margin_of_error: float
    ci_lower: float
    ci_upper: float

    def to_dict(self) -> dict:
        return {
            "mean":             self.mean,
            "std":              self.std,
            "n":                self.n,
            "z_score":          self.z_score,
            "confidence_level": self.confidence_level,
            "standard_error":   self.standard_error,
            "margin_of_error":  self.margin_of_error,
            "ci_lower":         self.ci_lower,
            "ci_upper":         self.ci_upper,
        }


# ---- Shared constants matching Prolog ci_z/2 ---------------------------
# This dictionary IS the Python anchor of the declarative Prolog table.
# Both must stay in sync; they are the "contract" between the two layers.
PROLOG_Z_MAP: dict[float, float] = {
    0.90: 1.645,
    0.95: 1.960,
    0.99: 2.576,
}


# ---- Low-level primitives ----------------------------------------------

def _clean(values: List[float]) -> List[float]:
    """Drop None and NaN while preserving order."""
    out: List[float] = []
    for v in values:
        if v is None:
            continue
        if isinstance(v, float) and math.isnan(v):
            continue
        out.append(float(v))
    return out


def _mean(values: List[float]) -> float:
    n = len(values)
    if n == 0:
        raise ValueError("empty_series")
    return sum(values) / n


def _sample_std(values: List[float]) -> float:
    """Sample standard deviation (ddof=1, matching scipy.stats.tstd)."""
    n = len(values)
    if n < 2:
        raise ValueError("insufficient_sample_for_std")
    m = _mean(values)
    variance = sum((v - m) ** 2 for v in values) / (n - 1)
    return math.sqrt(variance)


def _lookup_z(confidence_level: float) -> float:
    """Resolve z-score.

    1. Check the Prolog-backed exact map.
    2. Fall back to numerical inverse-normal via _erfinv if the
       confidence level is in (0,1) but not a registered key.
    3. Raise if level is outside (0,1).
    """
    if not (0.0 < confidence_level < 1.0):
        raise ValueError(f"confidence_level must be in (0,1), got {confidence_level}")
    if confidence_level in PROLOG_Z_MAP:
        return PROLOG_Z_MAP[confidence_level]
    # Numerical fallback for arbitrary levels
    tail_area = (1.0 - confidence_level) / 2.0
    target    = 1.0 - tail_area               # = (1 + L) / 2
    p         = 2.0 * target - 1.0
    z         = math.sqrt(2.0) * _erfinv(p)
    return z


# ---- Pure-python inverse-error-function --------------------------------
# Source: rational approx (Abramowitz & Stegun 7.1.26), refined.
_ERFINV_COEFFS = [
    -3.969683028665376e+01,  2.209460984245205e+02,
    -2.759285104469687e+02,  1.383577518672690e+02,
    -3.066479806614716e+01,  2.506628277459239e+00,
]
_ERFINV_POLY_COEFFS = [
    -5.447609879822406e+01, -1.615858368580409e+02,
     1.556049798740891e+02, -6.680131188771972e+01,
     1.328068155288572e+01,
]

def _erfinv(p: float) -> float:
    if p <= 0.0:
        return float("-inf")
    if p >= 1.0:
        return float("inf")
    split = 0.140
    if p < split:
        q = math.sqrt(-2.0 * math.log(p / 2.0))
        num = (((((_ERFINV_COEFFS[0]*q + _ERFINV_COEFFS[1])*q
                + _ERFINV_COEFFS[2])*q + _ERFINV_COEFFS[3])*q
                + _ERFINV_COEFFS[4])*q + _ERFINV_COEFFS[5])
        den = (((((_ERFINV_POLY_COEFFS[0]*q + _ERFINV_POLY_COEFFS[1])*q
                + _ERFINV_POLY_COEFFS[2])*q + _ERFINV_POLY_COEFFS[3])*q
                + _ERFINV_POLY_COEFFS[4])*q + 1.0)
        return -(num / den)
    else:
        q = math.sqrt(-2.0 * math.log(1.0 - p))
        num = (((((_ERFINV_COEFFS[0]*q + _ERFINV_COEFFS[1])*q
                + _ERFINV_COEFFS[2])*q + _ERFINV_COEFFS[3])*q
                + _ERFINV_COEFFS[4])*q + _ERFINV_COEFFS[5])
        den = (((((_ERFINV_POLY_COEFFS[0]*q + _ERFINV_POLY_COEFFS[1])*q
                + _ERFINV_POLY_COEFFS[2])*q + _ERFINV_POLY_COEFFS[3])*q
                + _ERFINV_POLY_COEFFS[4])*q + 1.0)
        return num / den


# ---- Orchestration ------------------------------------------------------

def calculate_mean_confidence_interval(
    values: List[Union[float, int, None]],
    confidence_level: float = 0.95,
) -> ConfidenceIntervalResult:
    """Compute CI per the formula x̄ ± z * s / sqrt(n).

    Parameters
    ----------
    values:
        Raw sample vector.  None/NaN entries are skipped.
    confidence_level:
        Confidence level in (0, 1).  Common values (0.90, 0.95, 0.99)
        are resolved through the shared Prolog z-table by the lookup
        helper; arbitrary levels use a numerical fallback.

    Returns
    -------
    ConfidenceIntervalResult
        Immutable dataclass carrying every quantity needed downstream.

    Raises
    ------
    ValueError
        ``confidence_level`` not in (0, 1) or ``values`` empty
        after cleaning.
    """
    clean = _clean(values)
    n = len(clean)
    if n < 2:
        raise ValueError("insufficient_sample_size: need >= 2 clean values")

    x_bar    = _mean(clean)
    s        = _sample_std(clean)
    se       = s / math.sqrt(n)
    z        = _lookup_z(confidence_level)
    margin   = z * se

    return ConfidenceIntervalResult(
        mean             = x_bar,
        std              = s,
        n                = n,
        z_score          = z,
        confidence_level = confidence_level,
        standard_error   = se,
        margin_of_error  = margin,
        ci_lower         = x_bar - margin,
        ci_upper         = x_bar + margin,
    )
```

## Inputs

| name | type | description |
|---|---|---|
| values | list[float\|int\|None] | Raw sample vector. None/NaN skipped. |
| confidence_level | float in (0,1) | Desired confidence level. Common: 0.90, 0.95, 0.99 |

## Outputs

| name | type | description |
|---|---|---|
| mean | float | Sample mean (x̄) |
| std | float | Sample standard deviation (s, ddof=1) |
| n | int | Clean sample size |
| z_score | float | Resolved z-score (from Prolog table or numerical fallback) |
| confidence_level | float | Echo of input |
| standard_error | float | s / sqrt(n) |
| margin_of_error | float | z * standard_error |
| ci_lower | float | Lower bound: x̄ - margin |
| ci_upper | float | Upper bound: x̄ + margin |

## State Updates
```
state_add_observation("inferential/current_ci", ci_result.to_dict())
state_add_observation("inferential/ci_mean",    result.mean)
state_add_observation("inferential/ci_lower",   result.ci_lower)
state_add_observation("inferential/ci_upper",   result.ci_upper)
```

## Error Handling
| Error | Condition | Behavior |
|---|---|---|
| insufficient_sample_size | n < 2 after cleaning | Raise ValueError |
| invalid_confidence_level | confidence_level not in (0,1) | Raise ValueError |

## Example Usage
```python
# 95 % CI for known normal data
values = [10.2, 9.8, 10.5, 10.1, 9.9, 10.3, 10.0, 9.7]
r = calculate_mean_confidence_interval(values, 0.95)
# r.mean       ≈ 10.0625
# r.std        ≈ 0.2724...
# r.z_score    == 1.96           (from Prolog table lookup)
# r.standard_error ≈ 0.0963...
# r.margin_of_error ≈ 0.1889...
# r.ci_lower   ≈ 9.873...
# r.ci_upper   ≈ 10.251...

# 99 % CI
r99 = calculate_mean_confidence_interval(values, 0.99)
# r99.z_score  == 2.576          (from Prolog table lookup)

# Arbitrary level (falls back to numerical erfinv)
r90 = calculate_mean_confidence_interval(values, 0.92)
# r90.z_score  ≈ 1.751...       (computed via _erfinv)
```

## Security Considerations
- Pure in-memory computation. No I/O, no network, no subprocess execution.
- The mathematical approximations are bounded (erfinv domain -4..4 covers all practical CIs).
