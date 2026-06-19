---
name: variance-equality-tester
domain: STATISTICS
version: "1.0.0"
surfaces: [prolog, python]
description: |
  Tests equality of variances across two or more groups using Levene's
  test (primary, robust to non-normality) and Bartlett's test (secondary,
  optimal for normal data). Prolog routes the primary test based on the
  normality verdict of input groups and declares a homogeneity_verdict.
  Python computes both test statistics and p-values.
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

# Variance Equality Tester

## Purpose
Determine whether the variances of k ≥ 2 groups are equal — a key assumption for:
- Student's t-test (equal variance variant)
- One-Way ANOVA (homogeneity of variance assumption)

Two tests:
- **Levene's test** — Robust to non-normality; uses absolute deviations from group median.
- **Bartlett's test** — More powerful under normality; uses log of variance ratios.

## Description
Hybrid skill:
- **Prolog layer** — Routes primary test by the `normality_verdict` of the input groups. Declares `homogeneous` or `heterogeneous` and recommends Welch correction if variances are unequal.
- **Python layer** — Executes both tests, computes F (Levene) and χ² (Bartlett) statistics with p-values.

## Prolog Surface (prelude.pl)

```prolog
:- module(variance_equality_tester, [
    route_variance_test/2,
    homogeneity_verdict/2,
    recommend_correction/2
]).

% ============================================================
% 1. Route primary test by normality verdict
% ============================================================
route_variance_test(normal,     bartlett).    % optimal under normality
route_variance_test(non_normal, levene).      % robust to non-normality
route_variance_test(borderline, levene).      % conservative choice

% ============================================================
% 2. Homogeneity verdict
% ============================================================
homogeneity_verdict(Primary, homogeneous)   :- Primary = not_rejected.
homogeneity_verdict(Primary, heterogeneous) :- Primary = rejected.

% ============================================================
% 3. Downstream correction recommendation
% ============================================================
recommend_correction(homogeneous,   no_correction_needed).
recommend_correction(heterogeneous, apply_welch_correction).
```

## Python Surface (executor.py)

```python
"""
variance-equality-tester
========================
Levene's test (center=median) and Bartlett's test for equality of variances.
Pure stdlib math — no numpy/scipy.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Union


@dataclass(frozen=True)
class VarianceEqualityResult:
    k: int
    group_sizes: List[int]
    group_variances: List[float]
    levene_statistic: float
    levene_p: float
    bartlett_statistic: float
    bartlett_p: float
    primary_test: str      # 'levene' | 'bartlett'
    primary_reject: bool
    verdict: str           # 'homogeneous' | 'heterogeneous'
    alpha: float

    def to_dict(self) -> dict:
        return {
            "k":                  self.k,
            "verdict":            self.verdict,
            "primary_test":       self.primary_test,
            "levene":             {"F": self.levene_statistic, "p": self.levene_p},
            "bartlett":           {"chi2": self.bartlett_statistic, "p": self.bartlett_p},
            "group_variances":    self.group_variances,
        }


def _clean(xs): return [float(v) for v in xs if v is not None and not math.isnan(float(v))]
def _mean(xs):  return sum(xs)/len(xs)
def _median(xs):
    s = sorted(xs); n = len(s)
    return (s[n//2-1]+s[n//2])/2 if n%2==0 else s[n//2]
def _var(xs, ddof=1):
    m = _mean(xs); n = len(xs)
    return sum((x-m)**2 for x in xs)/(n-ddof)


def _f_pvalue(f, df1, df2):
    def betai(a, b, x):
        if x<=0: return 0.0
        if x>=1: return 1.0
        if x>(a+1)/(a+b+2): return 1.0-betai(b,a,1-x)
        lb=math.lgamma(a)+math.lgamma(b)-math.lgamma(a+b)
        front=math.exp(math.log(x)*a+math.log(1-x)*b-lb)/a
        cf=c=1.0;d=1.0-(a+b)*x/(a+1)
        if abs(d)<1e-30:d=1e-30
        d=1/d;cf=d
        for m in range(1,201):
            num=m*(b-m)*x/((a+2*m-1)*(a+2*m));d=1+num*d;c=1+num/c
            if abs(d)<1e-30:d=1e-30
            if abs(c)<1e-30:c=1e-30
            d=1/d;cf*=c*d
            num=-(a+m)*(a+b+m)*x/((a+2*m)*(a+2*m+1));d=1+num*d;c=1+num/c
            if abs(d)<1e-30:d=1e-30
            if abs(c)<1e-30:c=1e-30
            d=1/d;dlt=c*d;cf*=dlt
            if abs(dlt-1)<1e-10:break
        return front*cf
    return betai(df2/2, df1/2, df2/(df2+df1*f))


def _chi2_pvalue(chi2, df):
    """1 - CDF of chi-squared(df) at chi2."""
    def gammainc(a, x):
        if x==0: return 0.0
        ap=a;s=d=1.0/a
        for _ in range(300):
            ap+=1;d*=x/ap;s+=d
            if abs(d)<abs(s)*1e-10:break
        return s*math.exp(-x+a*math.log(x)-math.lgamma(a))
    return 1.0 - gammainc(df/2.0, chi2/2.0)


def _levene(groups: List[List[float]]) -> tuple:
    """Levene's test (center=median) → (F, p-value)."""
    k = len(groups); N = sum(len(g) for g in groups)
    # Z_ij = |X_ij - median(group_i)|
    Z = [[abs(x - _median(g)) for x in g] for g in groups]
    Z_means = [_mean(z) for z in Z]
    Z_grand  = _mean([v for row in Z for v in row])
    ns = [len(g) for g in groups]
    SS_between = sum(ns[i]*(Z_means[i]-Z_grand)**2 for i in range(k))
    SS_within  = sum(sum((Z[i][j]-Z_means[i])**2 for j in range(ns[i])) for i in range(k))
    df1 = k-1; df2 = N-k
    ms_b = SS_between/df1; ms_w = SS_within/df2
    F = ms_b/ms_w if ms_w > 0 else 0.0
    p = _f_pvalue(F, df1, df2)
    return F, p


def _bartlett(groups: List[List[float]]) -> tuple:
    """Bartlett's test → (chi2, p-value)."""
    k = len(groups); ns = [len(g) for g in groups]
    N = sum(ns)
    vars_ = [_var(g, ddof=1) for g in groups]
    sp2   = sum((ns[i]-1)*vars_[i] for i in range(k)) / (N-k)
    if sp2 <= 0: return 0.0, 1.0
    numerator   = (N-k)*math.log(sp2) - sum((ns[i]-1)*math.log(max(vars_[i],1e-100)) for i in range(k))
    c_factor    = 1 + (1/(3*(k-1))) * (sum(1/(ns[i]-1) for i in range(k)) - 1/(N-k))
    chi2 = numerator / c_factor
    p    = _chi2_pvalue(chi2, k-1)
    return chi2, p


def test_variance_equality(
    groups: List[List[Union[float, int, None]]],
    normality_verdict: str = "non_normal",
    alpha: float = 0.05,
) -> VarianceEqualityResult:
    """Test equality of variances across groups.

    Parameters
    ----------
    groups:
        List of k ≥ 2 sample vectors. None/NaN dropped.
    normality_verdict:
        Output of normality_tester ('normal'/'non_normal'/'borderline').
        Routes primary test selection (mirrors Prolog routing).
    alpha:
        Significance level.
    """
    cleaned = [_clean(g) for g in groups]
    k = len(cleaned)
    if k < 2:
        raise ValueError("variance_equality: need >= 2 groups")
    if any(len(g) < 2 for g in cleaned):
        raise ValueError("variance_equality: each group needs >= 2 observations")

    vars_   = [_var(g) for g in cleaned]
    F_lev, p_lev   = _levene(cleaned)
    chi2_bar, p_bar = _bartlett(cleaned)

    # Mirror Prolog routing
    if normality_verdict == "normal":
        primary, primary_p = "bartlett", p_bar
    else:
        primary, primary_p = "levene", p_lev

    reject  = primary_p < alpha
    verdict = "heterogeneous" if reject else "homogeneous"

    return VarianceEqualityResult(
        k=k, group_sizes=[len(g) for g in cleaned],
        group_variances=vars_,
        levene_statistic=F_lev, levene_p=p_lev,
        bartlett_statistic=chi2_bar, bartlett_p=p_bar,
        primary_test=primary, primary_reject=reject,
        verdict=verdict, alpha=alpha,
    )
```

## Inputs

| name | type | description |
|---|---|---|
| groups | list[list[float\|int\|None]] | k ≥ 2 sample vectors |
| normality_verdict | str | 'normal', 'non_normal', or 'borderline' from normality_tester |
| alpha | float | Significance level (default 0.05) |

## Outputs

| name | type | description |
|---|---|---|
| verdict | str | 'homogeneous' or 'heterogeneous' |
| primary_test | str | 'levene' or 'bartlett' (Prolog-routed) |
| levene_statistic | float | Levene's F statistic |
| levene_p | float | Levene p-value |
| bartlett_statistic | float | Bartlett's χ² statistic |
| bartlett_p | float | Bartlett p-value |
| group_variances | list[float] | Per-group sample variance |

## State Updates
```
state_add_observation("inferential/variance_verdict", result.verdict)
state_add_observation("inferential/levene_p", result.levene_p)
state_add_observation("inferential/bartlett_p", result.bartlett_p)
```

## Error Handling
| Error | Condition | Behavior |
|---|---|---|
| insufficient_groups | k < 2 | Raise ValueError |
| insufficient_observations | any group n < 2 | Raise ValueError |

## Example Usage
```python
g1 = [10, 11, 12, 10, 11]
g2 = [20, 25, 30, 18, 28]  # higher variance
r = test_variance_equality([g1, g2], normality_verdict="non_normal")
# r.verdict         => 'heterogeneous'
# r.levene_statistic > critical value
# r.levene_p        < 0.05
```

## Security Considerations
- Pure in-memory. No I/O or network.
