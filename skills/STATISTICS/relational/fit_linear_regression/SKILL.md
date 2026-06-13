---
name: fit_linear_regression
domain: STATISTICS
version: "1.0.0"
surfaces: [prolog, python]
description: |
  Hybrid skill fitting an ordinary least-squares (OLS) simple linear
  regression model y = b0 + b1*x.  Prolog enforces minimum sample
  size and independence preconditions; Python computes coefficients,
  r-squared, standard errors, t-statistic, and p-value.
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

# Fit Linear Regression

## Purpose
Fit an ordinary least-squares (OLS) simple linear regression model:
```
y = b0 + b1 * x
```
The skill computes coefficient estimates, goodness-of-fit (R-squared), and inferential statistics (standard error, t-statistic, p-value) for the slope.

## Description
Hybrid skill:
- **Prolog layer** — Enforces symbolic preconditions: minimum sample size (n >= 3), equal vector lengths, independence assertion.
- **Python layer** — Implements centered OLS formulas:
  - Coefficient estimation: beta_1 = cov(x,y) / var(x), beta_0 = y_bar - beta_1 * x_bar
  - Residuals and residual sum of squares
  - Standard error of beta_1
  - t-statistic and p-value via t-distribution
  - R-squared goodness-of-fit

## Prolog Surface (prelude.pl)

```prolog
:- module(ols_guard, [
    ols_min_samples/1,
    independent_groups/1,
    same_length/2,
    ols_preconditions/3,
    ols_permitted/4
]).

% ============================================================
% 1. Structural preconditions
% ============================================================
ols_min_samples(N) :- N >= 3.

same_length(Xs, Ys) :- length(Xs, N), length(Ys, N).

% ============================================================
% 2. Independence gate (symbolic trust flag)
%    Passed as an atom from Python; Prolog asserts or rejects.
% ============================================================
independent_groups(true).
independent_groups(false) :-
    fail.   % paired/repeated not supported by simple OLS

% ============================================================
% 3. Main precondition gate
% ============================================================
ols_preconditions(Xs, Ys, Independent) :-
    same_length(Xs, Ys),
    length(Xs, N),
    ols_min_samples(N),
    independent_groups(Independent).

% ============================================================
% 4. Permission predicate
% ============================================================
ols_permitted(Xs, Ys, Independent, allowed) :-
    ols_preconditions(Xs, Ys, Independent), !.

ols_permitted(_, _, _, blocked(insufficient_sample)) :-
    % numeric check delegated to Python via call_python
    call_python(check_length, [_, _], N),
    N < 3.

ols_permitted(_, _, _, blocked(dependent_groups)).
```

## Python Surface (executor.py)

```python
"""
fit_linear_regression
=======================
Hybrid skill: symbolic precondition checks + algorithmic OLS fitting.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union


@dataclass(frozen=True)
class LinearRegressionResult:
    """OLS simple linear regression result."""
    beta_0: float            # Intercept
    beta_1: float            # Slope
    r_squared: float         # Coefficient of determination
    std_err_beta1: float     # Standard error of slope
    t_stat: float            # t-statistic for beta_1
    p_value: float           # Two-tailed p-value for beta_1 = 0
    n: int                   # Original vector length
    df: int                  # Degrees of freedom = n - 2
    n_used: int              # Paired observations after cleaning
    n_dropped: int           # Pairs dropped due to missing data
    residuals: List[float]   # Observed - Predicted

    def to_dict(self) -> dict:
        return {
            "beta_0":         self.beta_0,
            "beta_1":         self.beta_1,
            "r_squared":      self.r_squared,
            "std_err_beta1":  self.std_err_beta1,
            "t_stat":         self.t_stat,
            "p_value":        self.p_value,
            "n":              self.n,
            "df":             self.df,
            "n_used":         self.n_used,
            "n_dropped":      self.n_dropped,
            "residuals":      self.residuals,
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


def fit_linear_regression(
    x: List[Union[float, int, None]],
    y: List[Union[float, int, None]],
    alpha: float = 0.05,
    independent: bool = True,
) -> LinearRegressionResult:
    """Fit OLS simple linear regression y = beta_0 + beta_1 * x.

    Parameters
    ----------
    x, y : list of numbers/None
        Paired vectors.  Pairs with any missing entry are dropped.
    alpha : float
        Significance level (default 0.05) for p-value reporting.
    independent : bool
        True if x-y pairs are independent (checked by Prolog preconditions).

    Returns
    -------
    LinearRegressionResult

    Raises
    ------
    ValueError
        Insufficient paired observations (need >= 3) or zero variance in x.
    """
    cx, cy, dropped = _clean_pairs(x, y)
    n = len(cx)
    n_orig = len(x)

    if n < 3:
        raise ValueError(
            f"insufficient_sample: need >= 3 paired observations, got {n}"
        )

    x_bar = sum(cx) / n
    y_bar = sum(cy) / n

    # Sums of squares and cross-products
    ss_xy = sum((xi - x_bar) * (yi - y_bar) for xi, yi in zip(cx, cy))
    ss_xx = sum((xi - x_bar) ** 2 for xi in cx)
    ss_yy = sum((yi - y_bar) ** 2 for yi in cy)

    if ss_xx == 0:
        raise ValueError(
            "zero_variance: all x values are identical; cannot estimate slope"
        )

    # Coefficients
    beta_1 = ss_xy / ss_xx
    beta_0 = y_bar - beta_1 * x_bar

    # R-squared
    r_squared = (ss_xy ** 2) / (ss_xx * ss_yy) if ss_yy != 0 else 0.0

    # Residuals
    residuals = [yi - (beta_0 + beta_1 * xi) for xi, yi in zip(cx, cy)]
    ss_res = sum(e * e for e in residuals)
    df = n - 2

    # Standard error of beta_1
    mse = ss_res / df if df > 0 else 0.0
    std_err_beta1 = math.sqrt(mse / ss_xx)

    # t-statistic and p-value
    t_stat = beta_1 / std_err_beta1 if std_err_beta1 > 0 else 0.0
    p_value = _t_pvalue(abs(t_stat), df)

    return LinearRegressionResult(
        beta_0        = beta_0,
        beta_1        = beta_1,
        r_squared     = r_squared,
        std_err_beta1 = std_err_beta1,
        t_stat        = t_stat,
        p_value       = p_value,
        n             = n_orig,
        df            = df,
        n_used        = n,
        n_dropped     = dropped,
        residuals     = residuals,
    )


def _t_pvalue(t_stat: float, df: int) -> float:
    """Two-tailed p-value from t-distribution with df degrees of freedom."""
    if df <= 0:
        return 1.0
    try:
        from scipy.stats import t as t_dist
        return float(2.0 * t_dist.sf(abs(t_stat), df))
    except ImportError:
        # Normal approximation
        p = 2.0 * (1.0 - _normal_cdf(abs(t_stat), 0.0, 1.0))
        if df < 30:
            p = min(1.0, p * (1.0 + (30 - df) / 60.0))
        return p


def _normal_cdf(x: float, mu: float, sigma: float) -> float:
    """Approximate normal CDF using error function."""
    z = (x - mu) / (sigma * math.sqrt(2.0))
    return 0.5 * (1.0 + math.erf(z))
```

## Inputs

| name | type | description |
|---|---|---|
| x | list[number\|None] | Independent variable vector |
| y | list[number\|None] | Dependent variable vector (same length as x) |
| alpha | float | Significance level (default 0.05) |
| independent | bool | Assertion that observations are independent (Prolog gate) |

## Outputs

| name | type | description |
|---|---|---|
| beta_0 | float | Intercept |
| beta_1 | float | Slope coefficient |
| r_squared | float | R-squared in [0, 1] |
| std_err_beta1 | float | Standard error of slope |
| t_stat | float | t-statistic: beta_1 / SE(beta_1) |
| p_value | float | Two-tailed p-value under H0: beta_1 = 0 |
| n | int | Original vector length |
| df | int | Degrees of freedom (n - 2) |
| n_used | int | Paired observations after cleaning |
| residuals | list[float] | yi - ŷi for all used pairs |

## Symbolic Preconditions (Prolog)
- `same_length(Xs, Ys)` — vectors must be same length
- `ols_min_samples(N)` — N >= 3
- `independent_groups(true)` — independence assertion must hold

## State Updates
```
state_add_observation("relational/regression/beta_0",    result.beta_0)
state_add_observation("relational/regression/beta_1",    result.beta_1)
state_add_observation("relational/regression/r_squared", result.r_squared)
state_add_observation("relational/regression/p_value",   result.p_value)
state_add_observation("relational/regression/t_stat",    result.t_stat)
```

## Error Handling
| Error | Condition |
|---|---|
| insufficient_sample | n < 3 after cleaning |
| zero_variance | All x values identical; slope undefined |

## Example Usage
```python
x = [1, 2, 3, 4, 5, 6, 7, 8]
y = [2.1, 3.9, 6.2, 7.8, 10.1, 11.9, 14.2, 15.8]
r = fit_linear_regression(x, y)
# r.beta_0      ≈ 0.14
# r.beta_1      ≈ 1.98
# r.r_squared   ≈ 0.999
# r.std_err_beta1 ≈ 0.03
# r.t_stat      ≈ 62.0
# r.p_value     << 0.001
# r.df          == 6

# With missing values
x2 = [1, None, 3, 4, 5, 6, 7, 8]
y2 = [2.1, 3.9, 6.2, 7.8, 10.1, 11.9, 14.2, 15.8]
r2 = fit_linear_regression(x2, y2)
# r2.n_used     == 7
# r2.n_dropped  == 1
```

## Security Considerations
- No I/O. All computation in-memory.
- scipy optional; normal approximation fallback provided with Satterthwaite heuristic for small df.
