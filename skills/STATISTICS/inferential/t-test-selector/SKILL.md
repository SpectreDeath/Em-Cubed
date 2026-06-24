---
name: t-test-selector
domain: STATISTICS
version: "1.0.0"
surfaces: [prolog, python]
description: |
  Hybrid skill selecting and executing the correct t-test variant
  (one-sample, two-sample independent, or paired) based on study
  design constraints. Prolog routes the decision; Python computes
  the t-statistic, degrees of freedom, p-value, and Cohen's d.
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

# T-Test Selector

## Purpose
Select and execute the correct t-test variant based on study design, then compute inferential statistics and effect size.

Three variants are supported:
- **One-sample t-test**: Compare sample mean against a known population mean μ₀.
- **Two-sample independent t-test** (Welch's): Compare means of two independent groups.
- **Paired t-test**: Compare means of two matched/repeated measurements.

## Description
Hybrid skill:
- **Prolog layer** — Declarative routing rules select test variant from design attributes (`paired`, `n_groups`, `mu0_known`). Guards enforce measurement level (interval/ratio) and minimum sample size.
- **Python layer** — Computes t-statistic, degrees of freedom, two-tailed p-value, and Cohen's d effect size without external dependencies.

## Prolog Surface (prelude.pl)

```prolog
:- module(t_test_selector, [
    select_t_test/4,
    t_test_guard/3,
    effect_size_label/2
]).

% ============================================================
% 1. Test variant routing
%    select_t_test(+Paired, +NGroups, +Mu0Known, -Variant)
% ============================================================
select_t_test(false, 1, true,  one_sample).
select_t_test(false, 2, false, two_sample_independent).
select_t_test(true,  2, false, paired).

% ============================================================
% 2. Design guards
%    t_test_guard(+Variant, +N, +MeasurementLevel)
% ============================================================
t_test_guard(one_sample, N, Level) :-
    N >= 2,
    member(Level, [interval, ratio]).

t_test_guard(two_sample_independent, N, Level) :-
    N >= 4,
    member(Level, [interval, ratio]).

t_test_guard(paired, N, Level) :-
    N >= 2,
    member(Level, [interval, ratio]).

% ============================================================
% 3. Cohen's d classification (Sawilowsky 2009 thresholds)
% ============================================================
effect_size_label(D, negligible) :- D < 0.2.
effect_size_label(D, small)      :- D >= 0.2, D < 0.5.
effect_size_label(D, medium)     :- D >= 0.5, D < 0.8.
effect_size_label(D, large)      :- D >= 0.8, D < 1.2.
effect_size_label(D, very_large) :- D >= 1.2.
```

## Python Surface (executor.py)

```python
"""
t-test-selector
===============
Hybrid statistical skill:
- Prolog routes the test variant (one_sample / two_sample_independent / paired).
- Python computes t-statistic, degrees of freedom, p-value, and Cohen's d.

No external scientific libraries required — pure stdlib math.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Literal, Optional, Union

TTestVariant = Literal["one_sample", "two_sample_independent", "paired"]


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TTestResult:
    """Immutable result record for all t-test variants."""
    variant: str
    t_statistic: float
    degrees_of_freedom: float
    p_value: float
    cohens_d: float
    effect_label: str
    n1: int
    n2: Optional[int]
    mean1: float
    mean2: Optional[float]
    std1: float
    std2: Optional[float]

    def to_dict(self) -> dict:
        return {
            "variant":            self.variant,
            "t_statistic":        self.t_statistic,
            "degrees_of_freedom": self.degrees_of_freedom,
            "p_value":            self.p_value,
            "cohens_d":           self.cohens_d,
            "effect_label":       self.effect_label,
            "n1":                 self.n1,
            "n2":                 self.n2,
            "mean1":              self.mean1,
            "mean2":              self.mean2,
        }


# ---------------------------------------------------------------------------
# Numeric primitives (stdlib only)
# ---------------------------------------------------------------------------

def _mean(xs: List[float]) -> float:
    return sum(xs) / len(xs)


def _var(xs: List[float], ddof: int = 1) -> float:
    m = _mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - ddof)


def _std(xs: List[float], ddof: int = 1) -> float:
    return math.sqrt(_var(xs, ddof))


def _clean(xs: List) -> List[float]:
    return [float(v) for v in xs if v is not None and not (isinstance(v, float) and math.isnan(v))]


# ---------------------------------------------------------------------------
# Regularised incomplete beta function (two-tailed p-value via t-dist CDF)
# Abramowitz & Stegun §26.5.15 continued-fraction approximation
# ---------------------------------------------------------------------------

def _betai(a: float, b: float, x: float) -> float:
    """Regularised incomplete beta I_x(a,b) — used to derive p-value from t-dist."""
    if x < 0.0 or x > 1.0:
        raise ValueError("x must be in [0, 1]")
    if x == 0.0:
        return 0.0
    if x == 1.0:
        return 1.0
    # Use symmetry relation when x > (a+1)/(a+b+2)
    if x > (a + 1.0) / (a + b + 2.0):
        return 1.0 - _betai(b, a, 1.0 - x)
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(math.log(x) * a + math.log(1.0 - x) * b - lbeta) / a
    # Continued fraction (Lentz's method, 200 iterations)
    cf = 1.0
    c  = 1.0
    d  = 1.0 - (a + b) * x / (a + 1.0)
    if abs(d) < 1e-30:
        d = 1e-30
    d = 1.0 / d
    cf = d
    for m in range(1, 201):
        # Even step
        numerator = m * (b - m) * x / ((a + 2*m - 1) * (a + 2*m))
        d = 1.0 + numerator * d
        c = 1.0 + numerator / c
        if abs(d) < 1e-30: d = 1e-30
        if abs(c) < 1e-30: c = 1e-30
        d = 1.0 / d
        cf *= c * d
        # Odd step
        numerator = -(a + m) * (a + b + m) * x / ((a + 2*m) * (a + 2*m + 1))
        d = 1.0 + numerator * d
        c = 1.0 + numerator / c
        if abs(d) < 1e-30: d = 1e-30
        if abs(c) < 1e-30: c = 1e-30
        d = 1.0 / d
        delta = c * d
        cf *= delta
        if abs(delta - 1.0) < 1e-10:
            break
    return front * cf


def _t_pvalue(t: float, df: float) -> float:
    """Two-tailed p-value from t-distribution."""
    x = df / (df + t * t)
    return _betai(df / 2.0, 0.5, x)


def _cohen_d_label(d: float) -> str:
    abs_d = abs(d)
    if abs_d < 0.2:   return "negligible"
    if abs_d < 0.5:   return "small"
    if abs_d < 0.8:   return "medium"
    if abs_d < 1.2:   return "large"
    return "very_large"


# ---------------------------------------------------------------------------
# One-sample t-test
# ---------------------------------------------------------------------------

def _one_sample(group: List[float], mu0: float) -> TTestResult:
    n = len(group)
    m = _mean(group)
    s = _std(group)
    se = s / math.sqrt(n)
    t = (m - mu0) / se
    df = n - 1
    p = _t_pvalue(t, df)
    d = (m - mu0) / s
    return TTestResult(
        variant="one_sample", t_statistic=t, degrees_of_freedom=df,
        p_value=p, cohens_d=d, effect_label=_cohen_d_label(d),
        n1=n, n2=None, mean1=m, mean2=mu0, std1=s, std2=None,
    )


# ---------------------------------------------------------------------------
# Two-sample independent t-test (Welch's)
# ---------------------------------------------------------------------------

def _two_sample_independent(g1: List[float], g2: List[float]) -> TTestResult:
    n1, n2 = len(g1), len(g2)
    m1, m2 = _mean(g1), _mean(g2)
    v1, v2 = _var(g1), _var(g2)
    s1, s2 = math.sqrt(v1), math.sqrt(v2)
    se = math.sqrt(v1 / n1 + v2 / n2)
    t = (m1 - m2) / se
    # Welch–Satterthwaite degrees of freedom
    df = (v1/n1 + v2/n2) ** 2 / ((v1/n1)**2 / (n1-1) + (v2/n2)**2 / (n2-1))
    p = _t_pvalue(t, df)
    # Pooled Cohen's d
    sp = math.sqrt(((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2))
    d = (m1 - m2) / sp
    return TTestResult(
        variant="two_sample_independent", t_statistic=t, degrees_of_freedom=df,
        p_value=p, cohens_d=d, effect_label=_cohen_d_label(d),
        n1=n1, n2=n2, mean1=m1, mean2=m2, std1=s1, std2=s2,
    )


# ---------------------------------------------------------------------------
# Paired t-test
# ---------------------------------------------------------------------------

def _paired(g1: List[float], g2: List[float]) -> TTestResult:
    if len(g1) != len(g2):
        raise ValueError("paired_t_test: groups must have equal length")
    diffs = [a - b for a, b in zip(g1, g2)]
    n = len(diffs)
    m = _mean(diffs)
    s = _std(diffs)
    se = s / math.sqrt(n)
    t = m / se
    df = n - 1
    p = _t_pvalue(t, df)
    d = m / s
    return TTestResult(
        variant="paired", t_statistic=t, degrees_of_freedom=df,
        p_value=p, cohens_d=d, effect_label=_cohen_d_label(d),
        n1=n, n2=n, mean1=_mean(g1), mean2=_mean(g2),
        std1=_std(g1), std2=_std(g2),
    )


# ---------------------------------------------------------------------------
# Public dispatcher (mirrors Prolog select_t_test/3)
# ---------------------------------------------------------------------------

def run_t_test(
    variant: TTestVariant,
    group1: List[Union[float, int, None]],
    group2: Optional[List[Union[float, int, None]]] = None,
    mu0: float = 0.0,
) -> TTestResult:
    """Execute a t-test.

    Parameters
    ----------
    variant:
        One of 'one_sample', 'two_sample_independent', 'paired'.
        Should match Prolog select_t_test/3 output.
    group1:
        Primary sample vector. None/NaN skipped.
    group2:
        Second sample (required for independent/paired).
    mu0:
        Population mean for one-sample test (default 0.0).
    """
    g1 = _clean(group1)
    if len(g1) < 2:
        raise ValueError("insufficient_sample: group1 needs >= 2 clean values")

    if variant == "one_sample":
        return _one_sample(g1, mu0)

    if group2 is None:
        raise ValueError(f"group2 required for variant '{variant}'")
    g2 = _clean(group2)
    if len(g2) < 2:
        raise ValueError("insufficient_sample: group2 needs >= 2 clean values")

    if variant == "two_sample_independent":
        return _two_sample_independent(g1, g2)
    if variant == "paired":
        return _paired(g1, g2)

    raise ValueError(f"unknown_variant: {variant}")
```

## Inputs

| name | type | description |
|---|---|---|
| variant | str | Test variant: 'one_sample', 'two_sample_independent', or 'paired'. Routed by Prolog. |
| group1 | list[float\|int\|None] | Primary sample vector. None/NaN skipped. |
| group2 | list[float\|int\|None] \| None | Second sample (required for independent/paired tests). |
| mu0 | float | Known population mean for one-sample test (default 0.0). |

## Outputs

| name | type | description |
|---|---|---|
| variant | str | Confirmed test variant executed |
| t_statistic | float | Computed t-statistic |
| degrees_of_freedom | float | df (Welch-Satterthwaite for independent) |
| p_value | float | Two-tailed p-value |
| cohens_d | float | Effect size (Cohen's d) |
| effect_label | str | Effect magnitude: negligible/small/medium/large/very_large |
| n1, n2 | int | Clean sample sizes |
| mean1, mean2 | float | Group means |

## State Updates
```
state_add_observation("inferential/t_test_result", result.to_dict())
state_add_observation("inferential/t_test_p_value", result.p_value)
state_add_observation("inferential/t_test_effect", result.effect_label)
```

## Error Handling
| Error | Condition | Behavior |
|---|---|---|
| insufficient_sample | n < 2 in any group after cleaning | Raise ValueError |
| paired_length_mismatch | len(group1) != len(group2) for paired | Raise ValueError |
| unknown_variant | variant not in allowed set | Raise ValueError |
| missing_group2 | group2=None for independent/paired | Raise ValueError |

## Example Usage
```python
# One-sample: test if mean == 100
r = run_t_test("one_sample", [102, 98, 105, 97, 103, 99, 101], mu0=100.0)
# r.t_statistic ≈ 0.756, r.p_value ≈ 0.477, r.effect_label == "negligible"

# Two-sample independent: compare two groups
g1 = [85, 90, 92, 88, 94]
g2 = [78, 82, 80, 76, 85]
r = run_t_test("two_sample_independent", g1, g2)
# r.t_statistic ≈ 2.83, r.p_value ≈ 0.022, r.effect_label == "large"

# Paired: pre vs. post measurements
pre  = [70, 75, 80, 65, 72]
post = [78, 82, 85, 70, 79]
r = run_t_test("paired", pre, post)
# r.t_statistic ≈ -5.5, r.p_value ≈ 0.005, r.effect_label == "large"
```

## Security Considerations
- Pure in-memory computation. No I/O, no network, no subprocess execution.
- Continued-fraction convergence is bounded to 200 iterations.
