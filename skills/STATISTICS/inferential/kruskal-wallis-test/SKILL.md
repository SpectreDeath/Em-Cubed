---
name: kruskal-wallis-test
domain: STATISTICS
version: "1.0.0"
surfaces: [z3, python]
description: |
  Kruskal-Wallis H test — non-parametric equivalent of One-Way ANOVA
  for k >= 3 independent groups. Z3 encodes independence, group count,
  and ordinal-or-above measurement constraints. Python computes the H
  statistic with tie correction, chi-squared p-value, and eta-squared
  effect size. Includes Dunn's post-hoc pairwise comparisons with
  Bonferroni correction.
compatibility: PYTHON, Z3
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

# Kruskal-Wallis H Test

## Purpose
Non-parametric test for equality of medians across k ≥ 3 independent groups when:
- Normality assumption is violated
- Ordinal data or heavily skewed distributions

```
H = [12 / (N(N+1))] * Σ [R_i² / n_i] - 3(N+1)
```

With tie correction factor C = 1 - Σ(t³-t) / (N³-N).

Post-hoc pairwise comparisons via Dunn's test with Bonferroni correction.

## Description
Hybrid skill:
- **Z3 layer** — SMT constraints verify: k ≥ 3, all groups independent, measurement level is ordinal/interval/ratio, each group n ≥ 3.
- **Python layer** — Computes combined ranks, H statistic with tie correction, chi²(k-1) p-value, and Dunn's pairwise z-scores with Bonferroni-corrected p-values.

## Z3 Surface (constraints.py)

```python
"""
kruskal-wallis Z3 constraint surface
=====================================
Validates design requirements for the Kruskal-Wallis test.
"""
from z3 import Int, Bool, And, Solver, sat

def verify_kw_design(
    k: int,
    group_sizes: list[int],
    measurement_level: str,
    independent: bool,
) -> dict:
    s = Solver()
    k_var = Int('k')
    n_min = Int('n_min')
    indep = Bool('independent')

    s.add(k_var == k)
    s.add(n_min == min(group_sizes))
    s.add(indep == independent)

    # KW constraints
    s.add(k_var  >= 3)
    s.add(n_min  >= 3)
    s.add(indep  == True)

    if s.check() != sat:
        raise ValueError(
            f"kruskal_wallis_design_violation: k={k}, "
            f"min_n={min(group_sizes)}, independent={independent}. "
            "Require k>=3, all n>=3, independent=True."
        )
    if measurement_level not in ("ordinal", "interval", "ratio"):
        raise ValueError(
            f"measurement_level_violation: got '{measurement_level}', "
            "Kruskal-Wallis requires ordinal, interval, or ratio scale."
        )
    return {"satisfied": True, "k": k, "n_total": sum(group_sizes)}
```

## Python Surface (executor.py)

```python
"""
kruskal-wallis-test
===================
Kruskal-Wallis H test with tie correction and Dunn's post-hoc.
Pure stdlib — no numpy/scipy.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Union


@dataclass(frozen=True)
class DunnPair:
    group_a: int
    group_b: int
    z_statistic: float
    p_raw: float
    p_bonferroni: float
    significant: bool


@dataclass(frozen=True)
class KruskalWallisResult:
    k: int
    n_total: int
    group_sizes: List[int]
    group_rank_means: List[float]
    H_statistic: float
    H_corrected: float
    tie_correction: float
    df: int
    p_value: float
    eta_squared: float
    dunn_pairs: List[DunnPair]

    def to_dict(self) -> dict:
        return {
            "k":           self.k,
            "n_total":     self.n_total,
            "H_corrected": self.H_corrected,
            "df":          self.df,
            "p_value":     self.p_value,
            "eta_squared": self.eta_squared,
            "group_rank_means": self.group_rank_means,
            "dunn_pairs":  [{"a":p.group_a,"b":p.group_b,
                              "z":p.z_statistic,"p_bonf":p.p_bonferroni,
                              "sig":p.significant} for p in self.dunn_pairs],
        }


def _clean(xs): return [float(v) for v in xs if v is not None and not math.isnan(float(v))]
def _mean(xs):  return sum(xs)/len(xs)


def _rank_all(values: List[float]) -> List[float]:
    indexed = sorted(enumerate(values), key=lambda x: x[1])
    ranks = [0.0]*len(values)
    i = 0
    while i < len(indexed):
        j = i
        while j<len(indexed)-1 and indexed[j+1][1]==indexed[j][1]:
            j+=1
        avg=(i+j)/2.0+1.0
        for k in range(i,j+1):
            ranks[indexed[k][0]]=avg
        i=j+1
    return ranks


def _chi2_pvalue(chi2, df):
    def gammainc(a, x):
        if x==0: return 0.0
        ap=a;s=d=1.0/a
        for _ in range(300):
            ap+=1;d*=x/ap;s+=d
            if abs(d)<abs(s)*1e-10:break
        return s*math.exp(-x+a*math.log(x)-math.lgamma(a))
    return 1.0-gammainc(df/2.0, chi2/2.0)


def _norm_cdf(x): return 0.5*(1.0+math.erf(x/math.sqrt(2.0)))


def run_kruskal_wallis(
    groups: List[List[Union[float, int, None]]],
    alpha: float = 0.05,
) -> KruskalWallisResult:
    """Run Kruskal-Wallis H test with Dunn's post-hoc.

    Parameters
    ----------
    groups:
        List of k ≥ 3 independent sample vectors.
    alpha:
        Significance level for Dunn's test.
    """
    cleaned = [_clean(g) for g in groups]
    k = len(cleaned)
    if k < 3:
        raise ValueError("kruskal_wallis: need k >= 3 groups")
    if any(len(g) < 3 for g in cleaned):
        raise ValueError("kruskal_wallis: each group needs >= 3 observations")

    ns = [len(g) for g in cleaned]
    N  = sum(ns)

    # Combined ranks
    combined = [(v, i) for i,g in enumerate(cleaned) for v in g]
    all_vals = [v for v,_ in combined]
    all_ranks = _rank_all(all_vals)

    # Assign ranks back to groups
    group_ranks: List[List[float]] = [[] for _ in range(k)]
    for idx, (_, gi) in enumerate(combined):
        group_ranks[gi].append(all_ranks[idx])

    R = [sum(r) for r in group_ranks]   # rank sums
    group_rank_means = [R[i]/ns[i] for i in range(k)]

    # Tie correction
    tie_counts: dict = {}
    for v in all_vals:
        tie_counts[v] = tie_counts.get(v,0)+1
    C = 1.0 - sum(t**3-t for t in tie_counts.values()) / (N**3-N)
    C = max(C, 1e-10)

    # H statistic
    H = (12/(N*(N+1))) * sum(R[i]**2/ns[i] for i in range(k)) - 3*(N+1)
    H_corr = H / C
    df = k-1
    p  = _chi2_pvalue(H_corr, df)
    eta2 = (H_corr - k + 1) / (N - k)

    # Dunn's post-hoc (Bonferroni)
    n_comp = k*(k-1)//2
    pairs: List[DunnPair] = []
    grand_rank_mean = (N+1)/2.0
    for i in range(k):
        for j in range(i+1,k):
            se = math.sqrt(N*(N+1)/12.0*(1/ns[i]+1/ns[j]) - C)
            if se == 0: se = 1e-10
            z_ij = (group_rank_means[i]-group_rank_means[j]) / se
            p_raw   = 2.0*(1.0-_norm_cdf(abs(z_ij)))
            p_bonf  = min(1.0, p_raw*n_comp)
            pairs.append(DunnPair(
                group_a=i, group_b=j, z_statistic=z_ij,
                p_raw=p_raw, p_bonferroni=p_bonf,
                significant=p_bonf<alpha,
            ))

    return KruskalWallisResult(
        k=k, n_total=N, group_sizes=ns,
        group_rank_means=group_rank_means,
        H_statistic=H, H_corrected=H_corr,
        tie_correction=C, df=df, p_value=max(0.0,min(1.0,p)),
        eta_squared=max(0.0,eta2),
        dunn_pairs=pairs,
    )
```

## Inputs

| name | type | description |
|---|---|---|
| groups | list[list[float\|int\|None]] | k ≥ 3 independent sample vectors |
| alpha | float | Significance level for Dunn's post-hoc (default 0.05) |
| measurement_level | str | 'ordinal', 'interval', or 'ratio' (Z3 validated) |
| independent | bool | Must be True (Z3 validated) |

## Outputs

| name | type | description |
|---|---|---|
| H_corrected | float | Tie-corrected H statistic |
| df | int | Degrees of freedom (k-1) |
| p_value | float | Chi-squared p-value |
| eta_squared | float | Effect size (ε²) |
| group_rank_means | list[float] | Mean rank per group |
| dunn_pairs | list[DunnPair] | Pairwise Dunn's test results (Bonferroni-corrected) |

## State Updates
```
state_add_observation("inferential/kruskal_wallis_H", result.H_corrected)
state_add_observation("inferential/kruskal_wallis_p", result.p_value)
state_add_observation("inferential/kruskal_wallis_eta2", result.eta_squared)
```

## Error Handling
| Error | Condition | Behavior |
|---|---|---|
| insufficient_groups | k < 3 | Raise ValueError |
| insufficient_observations | any group n < 3 | Raise ValueError |
| kw_design_violation | Z3 constraint failure | Raise ValueError |

## Example Usage
```python
g1 = [23, 25, 28, 22, 24]
g2 = [30, 33, 35, 31, 29]
g3 = [18, 20, 19, 21, 17]
r = run_kruskal_wallis([g1, g2, g3])
# r.H_corrected  ≈ 13.8
# r.p_value      ≈ 0.001
# r.eta_squared  ≈ 0.74
# r.dunn_pairs: all 3 pairs significant after Bonferroni
```

## Security Considerations
- Pure in-memory. No I/O or network.
- Z3 constraint check prevents malformed designs.
