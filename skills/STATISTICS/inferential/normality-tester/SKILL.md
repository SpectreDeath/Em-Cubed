---
name: normality-tester
domain: STATISTICS
version: "1.0.0"
surfaces: [prolog, python]
description: |
  Tests whether a sample is drawn from a normal distribution using
  Shapiro-Wilk (n < 50), D'Agostino-Pearson K² (n >= 50), and
  Kolmogorov-Smirnov (as a secondary check). Prolog routes to the
  appropriate primary test by sample size and emits a composite
  normality_verdict. Python executes all numerical tests.
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

# Normality Tester

## Purpose
Determine whether a data sample is plausibly drawn from a normal distribution — a prerequisite for parametric tests (t-test, ANOVA).

Three tests are run:
- **Shapiro-Wilk** — Primary for small samples (n < 50). Most powerful normality test.
- **D'Agostino-Pearson K²** — Primary for n ≥ 50. Combines skewness and kurtosis.
- **Lilliefors (KS-based)** — Secondary/confirmatory check for all n.

Prolog routes the primary test and combines verdicts into a final `normality_verdict`.

## Description
Hybrid skill:
- **Prolog layer** — Decision tree: routes primary test by sample size, declares `normal` or `non_normal` verdict by aggregating primary + secondary results.
- **Python layer** — Computes all three test statistics, p-values, skewness, and excess kurtosis without external libraries.

## Prolog Surface (prelude.pl)

```prolog
:- module(normality_tester, [
    route_primary_test/2,
    normality_verdict/3,
    interpret_verdict/2
]).

% ============================================================
% 1. Route primary normality test by sample size
% ============================================================
route_primary_test(N, shapiro_wilk)      :- N >= 3,  N <  50.
route_primary_test(N, dagostino_pearson) :- N >= 50, N < 5000.
route_primary_test(N, lilliefors)        :- N >= 5000.

% ============================================================
% 2. Composite verdict
%    normality_verdict(+PrimaryReject, +SecondaryReject, -Verdict)
%    Both tests must agree on rejection for non_normal verdict.
% ============================================================
normality_verdict(false, _,     normal).
normality_verdict(true,  true,  non_normal).
normality_verdict(true,  false, borderline).

% ============================================================
% 3. Interpretation for downstream test selection
% ============================================================
interpret_verdict(normal,     parametric_tests_permitted).
interpret_verdict(non_normal, use_nonparametric_tests).
interpret_verdict(borderline, review_sample_size_and_visualize).
```

## Python Surface (executor.py)

```python
"""
normality-tester
================
Tests normality via Shapiro-Wilk approximation, D'Agostino-Pearson K²,
and Lilliefors (KS) check — pure stdlib math.

References:
  Shapiro-Wilk: Shapiro & Wilk (1965); coefficients from Royston (1992).
  D'Agostino-Pearson: D'Agostino & Pearson (1973).
  Lilliefors: Lilliefors (1967).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Union


@dataclass(frozen=True)
class NormalityTestResult:
    n: int
    mean: float
    std: float
    skewness: float
    excess_kurtosis: float
    shapiro_wilk_W: float
    shapiro_wilk_p: float
    dagostino_K2: float
    dagostino_p: float
    lilliefors_D: float
    lilliefors_p: float
    primary_test: str
    primary_reject: bool
    secondary_reject: bool
    verdict: str        # 'normal' | 'non_normal' | 'borderline'
    alpha: float

    def to_dict(self) -> dict:
        return {
            "n": self.n,
            "verdict": self.verdict,
            "primary_test": self.primary_test,
            "shapiro_wilk": {"W": self.shapiro_wilk_W, "p": self.shapiro_wilk_p},
            "dagostino_pearson": {"K2": self.dagostino_K2, "p": self.dagostino_p},
            "lilliefors": {"D": self.lilliefors_D, "p": self.lilliefors_p},
            "skewness": self.skewness, "excess_kurtosis": self.excess_kurtosis,
        }


def _clean(xs): return [float(v) for v in xs if v is not None and not math.isnan(float(v))]
def _mean(xs):  return sum(xs) / len(xs)
def _std(xs, ddof=1):
    m = _mean(xs); n = len(xs)
    return math.sqrt(sum((x-m)**2 for x in xs) / (n-ddof))


def _skewness(xs):
    n = len(xs); m = _mean(xs); s = _std(xs)
    if s == 0: return 0.0
    return (sum((x-m)**3 for x in xs)/n) / s**3


def _kurtosis(xs):
    """Excess kurtosis (normal = 0)."""
    n = len(xs); m = _mean(xs); s = _std(xs)
    if s == 0: return 0.0
    return (sum((x-m)**4 for x in xs)/n) / s**4 - 3.0


# --- Shapiro-Wilk (Royston 1992 approximation) ---

def _shapiro_wilk(xs: List[float]) -> tuple:
    """Return (W, p-value). Valid for n in [3, 5000]."""
    n = len(xs)
    xs_sorted = sorted(xs)
    m = _mean(xs_sorted)
    # Compute W via Royston's polynomial coefficients (simplified)
    # For a pure-stdlib approximation, use the half-sample method
    half = n // 2
    c = [xs_sorted[n-1-i] - xs_sorted[i] for i in range(half)]
    # Simplified a-vector (Shapiro-Francia for large n, Shapiro-Wilk weight approx)
    # Exact a-weights require tabulated values; we use the Blom approximation
    a = []
    for i in range(1, half+1):
        phi_inv = _probit((i - 0.375) / (n + 0.25))
        a.append(phi_inv)
    norm_a = math.sqrt(sum(x**2 for x in a))
    a = [x/norm_a for x in a]
    numerator = sum(a[i]*c[i] for i in range(half)) ** 2
    denominator = sum((x-m)**2 for x in xs_sorted)
    W = numerator / denominator if denominator > 0 else 0.0
    W = min(1.0, max(0.0, W))
    # Royston p-value approximation via log(1-W) ~ normal
    if W >= 1.0: return W, 1.0
    mu_w  = -1.2725 + 1.0521*math.log(n)
    sig_w = math.exp(-0.6714 + 0.9220*math.log(n) - 0.0832*math.log(n)**2)
    z     = (math.log(1.0-W) - mu_w) / sig_w
    p     = 1.0 - _norm_cdf(z)
    return W, max(0.0, min(1.0, p))


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _probit(p: float) -> float:
    """Inverse normal CDF (rational approximation)."""
    if p <= 0: return float('-inf')
    if p >= 1: return float('inf')
    if p < 0.5:
        t = math.sqrt(-2*math.log(p))
    else:
        t = math.sqrt(-2*math.log(1-p))
    c = [2.515517, 0.802853, 0.010328]
    d = [1.432788, 0.189269, 0.001308]
    num = c[0] + c[1]*t + c[2]*t**2
    den = 1 + d[0]*t + d[1]*t**2 + d[2]*t**3
    x = t - num/den
    return -x if p < 0.5 else x


# --- D'Agostino-Pearson K² ---

def _dagostino_pearson(xs: List[float]) -> tuple:
    n = len(xs)
    sk = _skewness(xs)
    ku = _kurtosis(xs)

    # Z-score for skewness
    Y   = sk * math.sqrt((n+1)*(n+3) / (6*(n-2)))
    beta2_sk = 3*(n*n+27*n-70)*(n+1)*(n+3) / ((n-2)*(n+5)*(n+7)*(n+9))
    W2  = -1 + math.sqrt(2*(beta2_sk-1))
    d   = 1 / math.sqrt(math.log(math.sqrt(W2)))
    a   = math.sqrt(2/(W2-1))
    Z_sk = d * math.log(Y/a + math.sqrt((Y/a)**2 + 1))

    # Z-score for kurtosis
    E    = 3*(n-1)/(n+1)
    var_k= 24*n*(n-2)*(n-3)/((n+1)**2*(n+3)*(n+5))
    X    = (ku - E) / math.sqrt(var_k)
    beta1= 6*(n*n-5*n+2)/((n+7)*(n+9)) * math.sqrt(6*(n+3)*(n+5)/(n*(n-2)*(n-3)))
    A    = 6 + 8/beta1 * (2/beta1 + math.sqrt(1 + 4/beta1**2))
    Z_ku = ((1-2/(9*A)) - ((1-2/A)/(1+X*math.sqrt(2/(A-4))))**(1/3)) / math.sqrt(2/(9*A))

    K2 = Z_sk**2 + Z_ku**2
    # K2 ~ chi-squared(2)
    p  = 1.0 - _chi2_cdf(K2, 2)
    return K2, max(0.0, min(1.0, p))


def _chi2_cdf(x: float, df: int) -> float:
    """CDF of chi-squared(df) via regularised lower incomplete gamma."""
    if x <= 0: return 0.0
    return _gammainc(df/2.0, x/2.0)


def _gammainc(a: float, x: float) -> float:
    """Regularised lower incomplete gamma P(a, x) via series expansion."""
    if x == 0: return 0.0
    if x < 0:  raise ValueError("x must be >= 0")
    # Series representation
    ap = a; s = 1.0/a; d = 1.0/a
    for _ in range(300):
        ap += 1; d *= x/ap; s += d
        if abs(d) < abs(s)*1e-10: break
    return s * math.exp(-x + a*math.log(x) - math.lgamma(a))


# --- Lilliefors (KS-based) ---

def _lilliefors(xs: List[float]) -> tuple:
    n = len(xs)
    m = _mean(xs); s = _std(xs)
    zs = sorted((x-m)/s for x in xs)
    D = 0.0
    for i, z in enumerate(zs):
        cdf = _norm_cdf(z)
        D = max(D, abs((i+1)/n - cdf), abs(i/n - cdf))
    # Dallal-Wilkinson (1986) p-value approximation
    # p ≈ exp(-7.01256*D^2*(n+2.78019) + 2.99587*D*sqrt(n+2.78019) - 0.122119 + 0.974598/sqrt(n) + 1.67997/n)
    try:
        arg = (-7.01256*D**2*(n+2.78019)
               + 2.99587*D*math.sqrt(n+2.78019)
               - 0.122119
               + 0.974598/math.sqrt(n)
               + 1.67997/n)
        p = math.exp(arg)
    except Exception:
        p = 0.05
    return D, max(0.0, min(1.0, p))


# --- Main dispatcher ---

def test_normality(
    values: List[Union[float, int, None]],
    alpha: float = 0.05,
) -> NormalityTestResult:
    """Run all normality tests and return composite verdict.

    Parameters
    ----------
    values:
        Sample vector. None/NaN dropped.
    alpha:
        Significance level (default 0.05).
    """
    xs = _clean(values)
    n  = len(xs)
    if n < 3:
        raise ValueError("normality_tester: need >= 3 clean values")

    W, p_sw  = _shapiro_wilk(xs)
    K2, p_dp = _dagostino_pearson(xs) if n >= 8 else (float('nan'), 1.0)
    D, p_lf  = _lilliefors(xs)

    # Prolog-mirrored routing
    if n < 50:
        primary, primary_p = "shapiro_wilk", p_sw
        secondary_p = p_lf
    elif n < 5000:
        primary, primary_p = "dagostino_pearson", p_dp
        secondary_p = p_lf
    else:
        primary, primary_p = "lilliefors", p_lf
        secondary_p = p_dp

    primary_reject   = primary_p   < alpha
    secondary_reject = secondary_p < alpha

    if not primary_reject:
        verdict = "normal"
    elif primary_reject and secondary_reject:
        verdict = "non_normal"
    else:
        verdict = "borderline"

    return NormalityTestResult(
        n=n, mean=_mean(xs), std=_std(xs),
        skewness=_skewness(xs), excess_kurtosis=_kurtosis(xs),
        shapiro_wilk_W=W, shapiro_wilk_p=p_sw,
        dagostino_K2=K2, dagostino_p=p_dp,
        lilliefors_D=D, lilliefors_p=p_lf,
        primary_test=primary, primary_reject=primary_reject,
        secondary_reject=secondary_reject, verdict=verdict, alpha=alpha,
    )
```

## Inputs

| name | type | description |
|---|---|---|
| values | list[float\|int\|None] | Sample vector (min 3 clean values) |
| alpha | float | Significance level (default 0.05) |

## Outputs

| name | type | description |
|---|---|---|
| verdict | str | 'normal', 'non_normal', or 'borderline' |
| primary_test | str | Test selected by Prolog routing |
| shapiro_wilk_W | float | W statistic (small samples) |
| shapiro_wilk_p | float | Shapiro-Wilk p-value |
| dagostino_K2 | float | K² statistic (large samples) |
| dagostino_p | float | D'Agostino p-value |
| lilliefors_D | float | KS distance statistic |
| lilliefors_p | float | Lilliefors p-value |
| skewness | float | Sample skewness |
| excess_kurtosis | float | Sample excess kurtosis (normal=0) |

## State Updates
```
state_add_observation("inferential/normality_verdict", result.verdict)
state_add_observation("inferential/normality_primary_p", result.shapiro_wilk_p)
state_add_observation("inferential/normality_skewness", result.skewness)
```

## Error Handling
| Error | Condition | Behavior |
|---|---|---|
| insufficient_sample | n < 3 after cleaning | Raise ValueError |

## Example Usage
```python
import random
random.seed(42)
normal_data = [random.gauss(100, 15) for _ in range(30)]
r = test_normality(normal_data)
# r.verdict          => 'normal'
# r.primary_test     => 'shapiro_wilk' (n < 50)
# r.shapiro_wilk_p   => > 0.05

skewed_data = [random.expovariate(0.1) for _ in range(30)]
r2 = test_normality(skewed_data)
# r2.verdict         => 'non_normal'
```

## Security Considerations
- Pure in-memory computation. No I/O or network.
