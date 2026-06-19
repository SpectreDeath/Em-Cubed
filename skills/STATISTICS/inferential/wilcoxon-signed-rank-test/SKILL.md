---
name: wilcoxon-signed-rank-test
domain: STATISTICS
version: "1.0.0"
surfaces: [prolog, python]
description: |
  Wilcoxon signed-rank test for two paired/matched samples or a single
  sample against a hypothesized median. Prolog enforces paired design,
  ordinal-or-above scale, and symmetry assumption. Python computes
  W+ and W- statistics, normal approximation z-score, p-value, and
  matched-pairs rank-biserial correlation effect size.
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

# Wilcoxon Signed-Rank Test

## Purpose
Non-parametric alternative to the paired t-test. Tests whether the median difference between paired observations is zero.

Two variants:
- **Paired samples**: Computes differences d_i = x_i - y_i, then tests if median(d) = 0.
- **One-sample**: Tests if the sample median equals a hypothesized value μ₀.

Returns W+ statistic, z-approximation p-value, and effect size r.

## Description
Hybrid skill:
- **Prolog layer** — Enforces: (1) paired design (equal group lengths), (2) ordinal-or-above measurement, (3) symmetry of the difference distribution is assumed. Routes exact vs. normal approximation by n.
- **Python layer** — Computes differences, ranks absolute differences (dropping zeros, handling ties), computes W+ and W-, z-score with continuity correction, and matched-pairs rank-biserial r = W+/(n(n+1)/2).

## Prolog Surface (prelude.pl)

```prolog
:- module(wilcoxon_signed_rank, [
    wsr_guard/2,
    route_method/2,
    wsr_effect_label/2
]).

% ============================================================
% 1. Design guards
% ============================================================
wsr_guard(Level, N) :-
    member(Level, [ordinal, interval, ratio]),
    N >= 6.    % minimum for meaningful signed-rank test

% ============================================================
% 2. Method routing by effective sample size
% ============================================================
route_method(N, exact)        :- N =< 25.
route_method(N, normal_approx):- N  > 25.

% ============================================================
% 3. Effect size labels (Cohen 1992, |r|)
% ============================================================
wsr_effect_label(R, small)  :- R <  0.3.
wsr_effect_label(R, medium) :- R >= 0.3, R < 0.5.
wsr_effect_label(R, large)  :- R >= 0.5.
```

## Python Surface (executor.py)

```python
"""
wilcoxon-signed-rank-test
=========================
Paired Wilcoxon signed-rank test.
Pure stdlib — no numpy/scipy.

Effect size: matched-pairs rank-biserial correlation
  r = W+ / (n*(n+1)/2)   where n = effective sample (zeros dropped)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Union


@dataclass(frozen=True)
class WilcoxonResult:
    n_pairs: int
    n_effective: int   # after dropping zero differences
    W_plus: float
    W_minus: float
    z_statistic: float
    p_value: float
    rank_biserial_r: float
    effect_label: str
    n_zeros: int
    n_ties: int

    def to_dict(self) -> dict:
        return {
            "n_pairs":         self.n_pairs,
            "n_effective":     self.n_effective,
            "W_plus":          self.W_plus,
            "W_minus":         self.W_minus,
            "z_statistic":     self.z_statistic,
            "p_value":         self.p_value,
            "rank_biserial_r": self.rank_biserial_r,
            "effect_label":    self.effect_label,
        }


def _clean(xs): return [float(v) for v in xs if v is not None and not math.isnan(float(v))]
def _norm_cdf(x): return 0.5*(1.0+math.erf(x/math.sqrt(2.0)))


def _rank_abs_with_ties(abs_diffs: List[float]) -> List[float]:
    """Rank absolute differences (already > 0) with tie averaging."""
    indexed = sorted(enumerate(abs_diffs), key=lambda x: x[1])
    ranks = [0.0]*len(abs_diffs)
    i = 0
    while i < len(indexed):
        j = i
        while j<len(indexed)-1 and indexed[j+1][1]==indexed[j][1]:
            j += 1
        avg = (i+j)/2.0+1.0
        for k in range(i,j+1):
            ranks[indexed[k][0]] = avg
        i = j+1
    return ranks


def run_wilcoxon_signed_rank(
    group1: List[Union[float, int, None]],
    group2: Optional[List[Union[float, int, None]]] = None,
    mu0: float = 0.0,
    alpha: float = 0.05,
) -> WilcoxonResult:
    """Run Wilcoxon signed-rank test.

    Parameters
    ----------
    group1:
        First sample (or single sample if group2=None).
    group2:
        Second paired sample. If None, tests group1 against mu0.
    mu0:
        Hypothesized median for one-sample variant (default 0.0).
    alpha:
        Significance level.
    """
    g1 = _clean(group1)
    if group2 is not None:
        g2 = _clean(group2)
        if len(g1) != len(g2):
            raise ValueError("wilcoxon_signed_rank: groups must have equal length")
        diffs = [a-b for a,b in zip(g1,g2)]
    else:
        diffs = [x-mu0 for x in g1]

    n_pairs = len(diffs)
    if n_pairs < 6:
        raise ValueError("wilcoxon_signed_rank: need >= 6 pairs")

    # Drop zero differences
    non_zero = [(d, i) for i, d in enumerate(diffs) if d != 0.0]
    n_zeros  = n_pairs - len(non_zero)
    n        = len(non_zero)

    if n == 0:
        raise ValueError("wilcoxon_signed_rank: all differences are zero")

    abs_diffs = [abs(d) for d,_ in non_zero]
    signs     = [1.0 if d>0 else -1.0 for d,_ in non_zero]
    ranks     = _rank_abs_with_ties(abs_diffs)

    W_plus  = sum(ranks[i] for i in range(n) if signs[i] > 0)
    W_minus = sum(ranks[i] for i in range(n) if signs[i] < 0)

    # Tie correction
    tie_counts: dict = {}
    for v in abs_diffs:
        tie_counts[v] = tie_counts.get(v,0)+1
    n_ties = sum(1 for c in tie_counts.values() if c > 1)
    tie_corr = sum(t**3-t for t in tie_counts.values() if t>1)

    # Normal approximation with continuity correction
    mu_W  = n*(n+1)/4.0
    var_W = n*(n+1)*(2*n+1)/24.0 - tie_corr/48.0
    T     = min(W_plus, W_minus)
    z     = (T - mu_W + 0.5) / math.sqrt(var_W)
    p     = 2.0*_norm_cdf(z)

    # Effect size (matched-pairs rank-biserial)
    r     = W_plus/(n*(n+1)/2.0)
    abs_r = abs(r-0.5)*2   # rescale to [0,1] centered on 0.5
    if abs_r < 0.3:   label = "small"
    elif abs_r < 0.5: label = "medium"
    else:             label = "large"

    return WilcoxonResult(
        n_pairs=n_pairs, n_effective=n,
        W_plus=W_plus, W_minus=W_minus,
        z_statistic=z, p_value=min(1.0,max(0.0,p)),
        rank_biserial_r=r, effect_label=label,
        n_zeros=n_zeros, n_ties=n_ties,
    )
```

## Inputs

| name | type | description |
|---|---|---|
| group1 | list[float\|int\|None] | First paired sample (or single sample) |
| group2 | list[float\|int\|None] \| None | Second paired sample; None for one-sample test |
| mu0 | float | Hypothesized median for one-sample test (default 0.0) |
| alpha | float | Significance level (default 0.05) |

## Outputs

| name | type | description |
|---|---|---|
| n_pairs | int | Total pairs |
| n_effective | int | Pairs after dropping zero differences |
| W_plus, W_minus | float | Signed rank sums |
| z_statistic | float | Normal approximation z-score |
| p_value | float | Two-tailed p-value |
| rank_biserial_r | float | Effect size |
| effect_label | str | 'small', 'medium', or 'large' |
| n_zeros | int | Count of zero differences (dropped) |
| n_ties | int | Count of tied rank groups |

## State Updates
```
state_add_observation("inferential/wilcoxon_p", result.p_value)
state_add_observation("inferential/wilcoxon_r", result.rank_biserial_r)
state_add_observation("inferential/wilcoxon_effect", result.effect_label)
```

## Error Handling
| Error | Condition | Behavior |
|---|---|---|
| insufficient_pairs | n < 6 | Raise ValueError |
| length_mismatch | len(group1) != len(group2) | Raise ValueError |
| all_zeros | all differences = 0 | Raise ValueError |

## Example Usage
```python
pre  = [85, 90, 78, 95, 88, 92, 80]
post = [90, 95, 85, 98, 92, 97, 88]
r = run_wilcoxon_signed_rank(pre, post)
# r.p_value      < 0.05 (post > pre)
# r.effect_label => 'large'

# One-sample: test if median != 0
scores = [2.1, -0.3, 1.5, 3.2, 0.8, 1.9, -0.5, 2.7]
r2 = run_wilcoxon_signed_rank(scores)
```

## Security Considerations
- Pure in-memory. No I/O or network.
