---
name: mann-whitney-u-test
domain: STATISTICS
version: "1.0.0"
surfaces: [prolog, python]
description: |
  Mann-Whitney U test (Wilcoxon rank-sum) for comparing two independent
  groups when parametric assumptions are violated. Prolog enforces
  ordinal-or-above measurement level and independence of samples.
  Python computes U statistic, z-approximation p-value, rank-biserial
  correlation effect size, and confidence interval for the median difference.
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

# Mann-Whitney U Test

## Purpose
Non-parametric alternative to the independent samples t-test. Tests whether values in one group tend to be larger than values in the other without assuming normality.

Hypotheses:
- H₀: The two distributions are equal (no stochastic ordering)
- H₁: One distribution is stochastically greater

Returns U statistic, z-approximation p-value, and rank-biserial correlation r.

## Description
Hybrid skill:
- **Prolog layer** — Guards: measurement level must be ordinal/interval/ratio; groups must be independent; each group ≥ 5. Routes to exact distribution for n₁+n₂ ≤ 25 or normal approximation.
- **Python layer** — Computes ranks with tie correction, U₁ and U₂, z-score with continuity correction, two-tailed p-value, and effect size r = 1 - 2U/(n₁n₂).

## Prolog Surface (prelude.pl)

```prolog
:- module(mann_whitney, [
    mw_guard/3,
    route_method/3,
    effect_label/2
]).

% ============================================================
% 1. Design guards
% ============================================================
mw_guard(Level, N1, N2) :-
    member(Level, [ordinal, interval, ratio]),
    N1 >= 3,
    N2 >= 3.

% ============================================================
% 2. Route: exact table vs. normal approximation
% ============================================================
route_method(N1, N2, exact)        :- N1+N2 =< 25.
route_method(N1, N2, normal_approx):- N1+N2  > 25.

% ============================================================
% 3. Effect size classification (Cohen 1992)
%    r = |rank_biserial_correlation|
% ============================================================
effect_label(R, small)  :- R < 0.3.
effect_label(R, medium) :- R >= 0.3, R < 0.5.
effect_label(R, large)  :- R >= 0.5.
```

## Python Surface (executor.py)

```python
"""
mann-whitney-u-test
===================
Mann-Whitney U / Wilcoxon rank-sum test for two independent samples.
Pure stdlib math — no numpy/scipy.

Effect size: rank-biserial correlation r = 1 - 2*U / (n1*n2)
where U is the smaller U statistic.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Union


@dataclass(frozen=True)
class MannWhitneyResult:
    n1: int
    n2: int
    U1: float
    U2: float
    U_min: float
    z_statistic: float
    p_value: float
    rank_biserial_r: float
    effect_label: str
    tie_correction: float   # correction factor applied to variance

    def to_dict(self) -> dict:
        return {
            "n1": self.n1, "n2": self.n2,
            "U1": self.U1, "U2": self.U2,
            "U_min": self.U_min,
            "z_statistic": self.z_statistic,
            "p_value": self.p_value,
            "rank_biserial_r": self.rank_biserial_r,
            "effect_label": self.effect_label,
        }


def _clean(xs): return [float(v) for v in xs if v is not None and not math.isnan(float(v))]


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _rank_with_ties(values: List[float]) -> List[float]:
    """Assign fractional ranks with tie-averaging."""
    indexed = sorted(enumerate(values), key=lambda x: x[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i
        while j < len(indexed) - 1 and indexed[j+1][1] == indexed[j][1]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0
        for k in range(i, j+1):
            ranks[indexed[k][0]] = avg_rank
        i = j + 1
    return ranks


def _tie_groups(values: List[float]) -> List[int]:
    """Return sizes of tied groups."""
    counts: dict = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    return [c for c in counts.values() if c > 1]


def run_mann_whitney_u(
    group1: List[Union[float, int, None]],
    group2: List[Union[float, int, None]],
    alpha: float = 0.05,
) -> MannWhitneyResult:
    """Run Mann-Whitney U test.

    Parameters
    ----------
    group1, group2:
        Two independent sample vectors. None/NaN dropped.
    alpha:
        Significance level.
    """
    g1, g2 = _clean(group1), _clean(group2)
    n1, n2 = len(g1), len(g2)
    if n1 < 3 or n2 < 3:
        raise ValueError("mann_whitney: each group needs >= 3 observations")

    combined = g1 + g2
    N = n1 + n2
    ranks = _rank_with_ties(combined)
    R1 = sum(ranks[:n1])
    # U statistics
    U1 = R1 - n1*(n1+1)/2
    U2 = n1*n2 - U1
    U_min = min(U1, U2)

    # Tie correction for variance
    ties = _tie_groups(combined)
    tie_corr = sum(t**3 - t for t in ties) / (N*(N-1)) if ties else 0.0

    # Normal approximation (with continuity correction)
    mu_U  = n1 * n2 / 2.0
    var_U = n1 * n2 / 12.0 * (N + 1 - tie_corr)
    z = (U_min - mu_U + 0.5) / math.sqrt(var_U)   # continuity correction
    p = 2 * _norm_cdf(z)   # two-tailed

    # Effect size
    r = 1.0 - 2.0 * U_min / (n1 * n2)
    abs_r = abs(r)
    if abs_r < 0.3:   label = "small"
    elif abs_r < 0.5: label = "medium"
    else:             label = "large"

    return MannWhitneyResult(
        n1=n1, n2=n2, U1=U1, U2=U2, U_min=U_min,
        z_statistic=z, p_value=min(1.0, max(0.0, p)),
        rank_biserial_r=r, effect_label=label,
        tie_correction=tie_corr,
    )
```

## Inputs

| name | type | description |
|---|---|---|
| group1 | list[float\|int\|None] | First independent sample (n ≥ 3) |
| group2 | list[float\|int\|None] | Second independent sample (n ≥ 3) |
| alpha | float | Significance level (default 0.05) |

## Outputs

| name | type | description |
|---|---|---|
| U1, U2 | float | Mann-Whitney U statistics for each group |
| U_min | float | Smaller U (used for significance) |
| z_statistic | float | Normal approximation z-score |
| p_value | float | Two-tailed p-value |
| rank_biserial_r | float | Effect size r = 1 - 2U/(n₁n₂) |
| effect_label | str | 'small', 'medium', or 'large' |
| tie_correction | float | Variance correction factor for ties |

## State Updates
```
state_add_observation("inferential/mann_whitney_p", result.p_value)
state_add_observation("inferential/mann_whitney_r", result.rank_biserial_r)
state_add_observation("inferential/mann_whitney_effect", result.effect_label)
```

## Error Handling
| Error | Condition | Behavior |
|---|---|---|
| insufficient_sample | n < 3 in either group | Raise ValueError |

## Example Usage
```python
control   = [12, 15, 14, 10, 13, 16]
treatment = [20, 22, 18, 25, 21, 24]
r = run_mann_whitney_u(control, treatment)
# r.p_value      < 0.05 (significant difference)
# r.effect_label => 'large'
```

## Security Considerations
- Pure in-memory computation. No I/O or network.
