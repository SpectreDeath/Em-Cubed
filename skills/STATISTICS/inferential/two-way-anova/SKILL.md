---
name: two-way-anova
domain: STATISTICS
version: "1.0.0"
surfaces: [prolog, python]
description: |
  Factorial Two-Way ANOVA testing main effects of two independent
  factors (A and B) and their interaction (A×B) on a continuous
  dependent variable. Prolog routes main-effect vs. interaction
  queries and enforces design validity. Python computes all sums
  of squares, F-statistics, p-values, and partial eta-squared.
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

# Two-Way ANOVA

## Purpose
Perform factorial Two-Way ANOVA to test:
1. **Main effect of Factor A** (row factor)
2. **Main effect of Factor B** (column factor)
3. **Interaction effect A×B** — whether the effect of A depends on B

Assumes a balanced design (equal cell sizes) with at least 2 observations per cell.

## Description
Hybrid skill:
- **Prolog layer** — Routes query type (main_effect_A, main_effect_B, interaction), validates factor levels (≥ 2), checks balanced design. Declares which effects to interpret when interaction is significant.
- **Python layer** — Computes all SS terms via the standard cell-means approach, derives F-statistics and p-values for each effect, reports partial η².

## Prolog Surface (prelude.pl)

```prolog
:- module(two_way_anova, [
    route_query/2,
    interpret_interaction/2,
    anova2_guard/3
]).

% ============================================================
% 1. Query routing — which effects to extract
% ============================================================
route_query(main_a,     [main_effect_a]).
route_query(main_b,     [main_effect_b]).
route_query(both_main,  [main_effect_a, main_effect_b]).
route_query(all,        [main_effect_a, main_effect_b, interaction_ab]).

% ============================================================
% 2. Interaction interpretation rule
%    If interaction is significant, marginal main effects are
%    misleading; inspect simple effects instead.
% ============================================================
interpret_interaction(significant, simple_effects_required).
interpret_interaction(not_significant, main_effects_interpretable).

% ============================================================
% 3. Design guards
%    anova2_guard(+LevelsA, +LevelsB, +CellSize)
% ============================================================
anova2_guard(A, B, CellSize) :-
    A >= 2,
    B >= 2,
    CellSize >= 2.
```

## Python Surface (executor.py)

```python
"""
two-way-anova
=============
Balanced factorial Two-Way ANOVA.
Requires equal cell sizes (n_per_cell same for all a*b cells).

Data format:
  data[i][j] = list of observations for cell (factor_a=i, factor_b=j)
  shape: (a_levels, b_levels, n_per_cell)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Union


@dataclass(frozen=True)
class TwoWayAnovaEffect:
    name: str
    ss: float
    df: int
    ms: float
    f_statistic: float
    p_value: float
    partial_eta_sq: float
    significant: bool


@dataclass(frozen=True)
class TwoWayAnovaResult:
    a_levels: int
    b_levels: int
    n_per_cell: int
    n_total: int
    grand_mean: float
    effect_a: TwoWayAnovaEffect
    effect_b: TwoWayAnovaEffect
    effect_ab: TwoWayAnovaEffect
    ss_error: float
    df_error: int
    ms_error: float

    def to_dict(self) -> dict:
        return {
            "a_levels":  self.a_levels,
            "b_levels":  self.b_levels,
            "n_per_cell": self.n_per_cell,
            "effect_a":  {"F": self.effect_a.f_statistic, "p": self.effect_a.p_value,
                          "eta2": self.effect_a.partial_eta_sq},
            "effect_b":  {"F": self.effect_b.f_statistic, "p": self.effect_b.p_value,
                          "eta2": self.effect_b.partial_eta_sq},
            "effect_ab": {"F": self.effect_ab.f_statistic, "p": self.effect_ab.p_value,
                          "eta2": self.effect_ab.partial_eta_sq},
        }


def _mean(xs): return sum(xs) / len(xs)
def _clean(xs): return [float(v) for v in xs if v is not None]


def _betai(a, b, x):
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    if x > (a+1)/(a+b+2): return 1.0 - _betai(b, a, 1.0-x)
    lb = math.lgamma(a)+math.lgamma(b)-math.lgamma(a+b)
    front = math.exp(math.log(x)*a+math.log(1-x)*b-lb)/a
    cf=1.0;c=1.0;d=1.0-(a+b)*x/(a+1)
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
        d=1/d;delta=c*d;cf*=delta
        if abs(delta-1)<1e-10:break
    return front*cf


def _f_pvalue(f, df1, df2):
    return _betai(df2/2.0, df1/2.0, df2/(df2+df1*f))


def _make_effect(name, ss, df, ms_err, ss_total, alpha=0.05):
    df_err_placeholder = 1  # will be filled by caller
    ms = ss / df if df > 0 else 0.0
    f  = ms / ms_err if ms_err > 0 else 0.0
    return ss, df, ms, f


def run_two_way_anova(
    data: List[List[List[Union[float, int, None]]]],
    alpha: float = 0.05,
) -> TwoWayAnovaResult:
    """Run balanced Two-Way ANOVA.

    Parameters
    ----------
    data:
        3-D list [a][b][observations]. All cells must have equal size.
    alpha:
        Significance level (default 0.05).
    """
    a = len(data)
    b = len(data[0])
    cells = [[_clean(data[i][j]) for j in range(b)] for i in range(a)]
    n = len(cells[0][0])

    if any(len(cells[i][j]) != n for i in range(a) for j in range(b)):
        raise ValueError("two_way_anova: balanced design required (equal cell sizes)")
    if n < 2:
        raise ValueError("two_way_anova: need >= 2 observations per cell")
    if a < 2 or b < 2:
        raise ValueError("two_way_anova: each factor needs >= 2 levels")

    N = a * b * n
    cell_means = [[_mean(cells[i][j]) for j in range(b)] for i in range(a)]
    grand = sum(cells[i][j][k] for i in range(a) for j in range(b) for k in range(n)) / N

    row_means = [_mean([cells[i][j][k] for j in range(b) for k in range(n)]) for i in range(a)]
    col_means = [_mean([cells[i][j][k] for i in range(a) for k in range(n)]) for j in range(b)]

    ss_a  = b*n * sum((row_means[i]-grand)**2 for i in range(a))
    ss_b  = a*n * sum((col_means[j]-grand)**2 for j in range(b))
    ss_ab = n   * sum((cell_means[i][j]-row_means[i]-col_means[j]+grand)**2
                      for i in range(a) for j in range(b))
    ss_err= sum((cells[i][j][k]-cell_means[i][j])**2
                for i in range(a) for j in range(b) for k in range(n))
    ss_tot= ss_a + ss_b + ss_ab + ss_err

    df_a  = a - 1
    df_b  = b - 1
    df_ab = df_a * df_b
    df_e  = N - a*b

    ms_a  = ss_a  / df_a
    ms_b  = ss_b  / df_b
    ms_ab = ss_ab / df_ab
    ms_e  = ss_err/ df_e

    def make(name, ss_, df_, ms_):
        F = ms_ / ms_e
        p = _f_pvalue(F, df_, df_e)
        pe2 = ss_ / (ss_ + ss_err)
        return TwoWayAnovaEffect(name=name, ss=ss_, df=df_, ms=ms_,
                                 f_statistic=F, p_value=p,
                                 partial_eta_sq=pe2, significant=p < alpha)

    return TwoWayAnovaResult(
        a_levels=a, b_levels=b, n_per_cell=n, n_total=N, grand_mean=grand,
        effect_a  = make("factor_A", ss_a,  df_a,  ms_a),
        effect_b  = make("factor_B", ss_b,  df_b,  ms_b),
        effect_ab = make("A_x_B",    ss_ab, df_ab, ms_ab),
        ss_error=ss_err, df_error=df_e, ms_error=ms_e,
    )
```

## Inputs

| name | type | description |
|---|---|---|
| data | list[list[list[float\|int\|None]]] | 3-D cell data [a_level][b_level][observations] |
| alpha | float | Significance level (default 0.05) |

## Outputs

| name | type | description |
|---|---|---|
| effect_a | TwoWayAnovaEffect | Main effect F, p, partial η² for Factor A |
| effect_b | TwoWayAnovaEffect | Main effect F, p, partial η² for Factor B |
| effect_ab | TwoWayAnovaEffect | Interaction A×B F, p, partial η² |
| ss_error | float | Within-cell error SS |
| grand_mean | float | Overall grand mean |

## State Updates
```
state_add_observation("inferential/two_way_anova", result.to_dict())
state_add_observation("inferential/interaction_significant", result.effect_ab.significant)
```

## Error Handling
| Error | Condition | Behavior |
|---|---|---|
| unbalanced_design | Cell sizes differ | Raise ValueError |
| insufficient_observations | n < 2 per cell | Raise ValueError |
| insufficient_levels | a < 2 or b < 2 | Raise ValueError |

## Example Usage
```python
# 2x2 factorial, n=3 per cell
data = [
    [[10,12,11], [20,22,21]],  # Factor A = level 1
    [[15,14,16], [25,27,26]],  # Factor A = level 2
]
r = run_two_way_anova(data)
# r.effect_a.significant  => True (main effect A)
# r.effect_b.significant  => True (main effect B)
# r.effect_ab.significant => depends on data
```

## Security Considerations
- Pure in-memory. No I/O or network.
- Balanced design enforced before computation.
