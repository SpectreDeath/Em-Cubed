---
name: mixed-model-anova
domain: STATISTICS
version: "1.0.0"
surfaces: [sqlite, python]
description: |
  Mixed ANOVA (split-plot design) combining one between-subjects factor
  and one within-subjects factor. SQLite stores the split-plot design
  metadata and per-subject group assignments. Python computes
  between-subjects SS (groups, subjects-within-groups), within-subjects
  SS (trials/conditions, interaction, error), F-statistics, and p-values.
compatibility: PYTHON, SQLITE
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

# Mixed-Model ANOVA

## Purpose
Analyze a mixed design with:
- **Between-subjects factor** (e.g., treatment vs. control group)
- **Within-subjects factor** (e.g., time-point: pre/post/follow-up)

Returns separate F-tests for:
1. Between-subjects main effect (group)
2. Within-subjects main effect (time/condition)
3. Group × Time interaction

## Description
Hybrid skill:
- **SQLite layer** — Stores the split-plot design: subject IDs, group assignments, condition values. Enables design queries (group sizes, condition counts) and result audit.
- **Python layer** — Computes partitioned sums of squares using the Winer-Brown-Michels (1991) split-plot ANOVA formulas. Uses two separate error terms: MS_subjects_within_groups for the between-subjects test and MS_interaction_error for within-subjects tests.

## SQLite Surface (schema.sql)

```sql
-- mixed_anova.db schema

CREATE TABLE IF NOT EXISTS mixed_design (
    run_id       TEXT NOT NULL,
    subject_id   INTEGER NOT NULL,
    group_id     INTEGER NOT NULL,       -- between-subjects factor
    condition_id INTEGER NOT NULL,       -- within-subjects factor
    value        REAL NOT NULL,
    PRIMARY KEY (run_id, subject_id, condition_id)
);

CREATE TABLE IF NOT EXISTS mixed_results (
    run_id              TEXT PRIMARY KEY,
    n_groups            INTEGER,
    n_subjects_per_group INTEGER,
    k_conditions        INTEGER,
    -- Between-subjects
    f_between           REAL,
    p_between           REAL,
    eta2_between        REAL,
    -- Within-subjects
    f_within            REAL,
    p_within            REAL,
    eta2_within         REAL,
    -- Interaction
    f_interaction       REAL,
    p_interaction       REAL,
    eta2_interaction    REAL,
    created_at          TEXT DEFAULT (datetime('now'))
);
```

## Python Surface (executor.py)

```python
"""
mixed-model-anova
=================
Split-plot ANOVA: one between-subjects factor (groups) × one within-subjects
factor (conditions/time-points). Balanced design required.

Data format:
  data[group_idx][subject_within_group_idx][condition_idx] = float
  Shape: (g groups) × (n subjects per group) × (k conditions)
"""

from __future__ import annotations

import math
import sqlite3
import uuid
from dataclasses import dataclass
from typing import List, Optional, Union


@dataclass(frozen=True)
class MixedEffect:
    name: str
    ss: float
    df: float
    ms: float
    f_statistic: float
    p_value: float
    partial_eta_sq: float


@dataclass(frozen=True)
class MixedAnovaResult:
    run_id: str
    n_groups: int
    n_per_group: int
    k_conditions: int
    between_effect: MixedEffect   # between-subjects main effect
    within_effect:  MixedEffect   # within-subjects main effect
    interaction:    MixedEffect   # group × condition
    grand_mean: float

    def to_dict(self) -> dict:
        def eff(e: MixedEffect):
            return {"F": e.f_statistic, "p": e.p_value, "eta2": e.partial_eta_sq}
        return {
            "run_id":      self.run_id,
            "between":     eff(self.between_effect),
            "within":      eff(self.within_effect),
            "interaction": eff(self.interaction),
        }


def _mean(xs): return sum(xs) / len(xs)


def _betai(a, b, x):
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    if x > (a+1)/(a+b+2): return 1.0 - _betai(b, a, 1.0-x)
    lb = math.lgamma(a)+math.lgamma(b)-math.lgamma(a+b)
    front = math.exp(math.log(x)*a+math.log(1-x)*b-lb)/a
    cf=c=d=1.0;d=1.0-(a+b)*x/(a+1)
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


def _f_p(f, df1, df2):
    if f <= 0: return 1.0
    return _betai(df2/2, df1/2, df2/(df2+df1*f))


def run_mixed_anova(
    data: List[List[List[Union[float, int, None]]]],
    alpha: float = 0.05,
    db_path: Optional[str] = None,
) -> MixedAnovaResult:
    """Run Mixed ANOVA (split-plot design).

    Parameters
    ----------
    data:
        3-D list [group][subject_in_group][condition].
        Must be balanced: equal subjects per group, equal conditions.
    alpha:
        Significance level.
    db_path:
        SQLite path for persistence. None uses in-memory.
    """
    g = len(data)
    n = len(data[0])      # subjects per group
    k = len(data[0][0])   # conditions
    run_id = str(uuid.uuid4())[:8]

    if g < 2: raise ValueError("mixed_anova: need >= 2 groups")
    if n < 2: raise ValueError("mixed_anova: need >= 2 subjects per group")
    if k < 2: raise ValueError("mixed_anova: need >= 2 conditions")

    d = [[[float(data[gi][si][ci]) for ci in range(k)]
           for si in range(n)] for gi in range(g)]
    N  = g * n          # total subjects
    Nk = N * k          # total observations

    grand = sum(d[gi][si][ci] for gi in range(g) for si in range(n) for ci in range(k)) / Nk

    # Cell means, group means, condition means, subject means
    group_means = [_mean([d[gi][si][ci] for si in range(n) for ci in range(k)]) for gi in range(g)]
    cond_means  = [_mean([d[gi][si][ci] for gi in range(g) for si in range(n)]) for ci in range(k)]
    subj_means  = [[_mean(d[gi][si]) for si in range(n)] for gi in range(g)]

    # SS computation (Winer et al. notation)
    ss_between_groups = n*k * sum((m - grand)**2 for m in group_means)
    ss_subjects_wg    = k   * sum((subj_means[gi][si] - group_means[gi])**2
                                   for gi in range(g) for si in range(n))
    ss_conditions     = N   * sum((m - grand)**2 for m in cond_means)
    ss_interaction    = n   * sum((
        _mean([d[gi][si][ci] for si in range(n)]) - group_means[gi] - cond_means[ci] + grand
    )**2 for gi in range(g) for ci in range(k))
    ss_cond_error     = sum((d[gi][si][ci] - subj_means[gi][si] -
                              _mean([d[gi][si2][ci] for si2 in range(n)]) +  # approx cell mean
                              group_means[gi])**2
                             for gi in range(g) for si in range(n) for ci in range(k))
    # Simplified error: total_within - conditions - interaction
    ss_total_within = sum((d[gi][si][ci] - subj_means[gi][si])**2
                           for gi in range(g) for si in range(n) for ci in range(k))
    ss_cond_error = ss_total_within - ss_conditions - ss_interaction

    df_between = g - 1
    df_swg     = N - g          # subjects within groups
    df_cond    = k - 1
    df_inter   = (g-1)*(k-1)
    df_ce      = (N-g)*(k-1)

    ms_between = ss_between_groups / df_between
    ms_swg     = ss_subjects_wg   / df_swg
    ms_cond    = ss_conditions    / df_cond
    ms_inter   = ss_interaction   / df_inter
    ms_ce      = ss_cond_error    / df_ce if df_ce > 0 else 1e-10

    f_bet  = ms_between / ms_swg
    f_con  = ms_cond    / ms_ce
    f_int  = ms_inter   / ms_ce

    ss_total = (ss_between_groups + ss_subjects_wg + ss_conditions +
                ss_interaction + ss_cond_error)

    def make_effect(name, ss, df, ms, f, dfe, mse):
        p    = _f_p(f, df, dfe)
        eta2 = ss / (ss + (dfe * mse))
        return MixedEffect(name=name, ss=ss, df=df, ms=ms,
                           f_statistic=f, p_value=p, partial_eta_sq=eta2)

    result = MixedAnovaResult(
        run_id=run_id, n_groups=g, n_per_group=n, k_conditions=k,
        grand_mean=grand,
        between_effect = make_effect("between_groups",   ss_between_groups, df_between, ms_between, f_bet, df_swg, ms_swg),
        within_effect  = make_effect("within_conditions",ss_conditions,     df_cond,    ms_cond,    f_con, df_ce,  ms_ce),
        interaction    = make_effect("group_x_condition",ss_interaction,    df_inter,   ms_inter,   f_int, df_ce,  ms_ce),
    )

    # SQLite persistence
    conn = sqlite3.connect(db_path or ":memory:")
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS mixed_design(
                run_id TEXT, subject_id INTEGER, group_id INTEGER,
                condition_id INTEGER, value REAL,
                PRIMARY KEY(run_id, subject_id, condition_id));
            CREATE TABLE IF NOT EXISTS mixed_results(
                run_id TEXT PRIMARY KEY, n_groups INTEGER,
                n_subjects_per_group INTEGER, k_conditions INTEGER,
                f_between REAL, p_between REAL, eta2_between REAL,
                f_within REAL, p_within REAL, eta2_within REAL,
                f_interaction REAL, p_interaction REAL, eta2_interaction REAL,
                created_at TEXT DEFAULT(datetime('now')));
        """)
        sid = 0
        for gi in range(g):
            for si in range(n):
                for ci in range(k):
                    conn.execute("INSERT OR REPLACE INTO mixed_design VALUES(?,?,?,?,?)",
                                 (run_id, sid, gi, ci, d[gi][si][ci]))
                sid += 1
        r = result
        conn.execute("INSERT OR REPLACE INTO mixed_results VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            run_id, g, n, k,
            r.between_effect.f_statistic, r.between_effect.p_value, r.between_effect.partial_eta_sq,
            r.within_effect.f_statistic,  r.within_effect.p_value,  r.within_effect.partial_eta_sq,
            r.interaction.f_statistic,    r.interaction.p_value,    r.interaction.partial_eta_sq,
        ))
        conn.commit()
    finally:
        conn.close()

    return result
```

## Inputs

| name | type | description |
|---|---|---|
| data | list[list[list[float\|int\|None]]] | 3-D array [group][subject][condition] |
| alpha | float | Significance level (default 0.05) |
| db_path | str \| None | SQLite path for design + result persistence |

## Outputs

| name | type | description |
|---|---|---|
| between_effect | MixedEffect | Between-subjects (group) F, p, η² |
| within_effect | MixedEffect | Within-subjects (condition) F, p, η² |
| interaction | MixedEffect | Group × Condition F, p, η² |
| grand_mean | float | Overall grand mean |

## State Updates
```
state_add_observation("inferential/mixed_anova_result", result.to_dict())
state_add_observation("inferential/interaction_significant", result.interaction.p_value < alpha)
```

## Error Handling
| Error | Condition | Behavior |
|---|---|---|
| insufficient_groups | g < 2 | Raise ValueError |
| insufficient_subjects | n < 2 per group | Raise ValueError |
| insufficient_conditions | k < 2 | Raise ValueError |

## Example Usage
```python
# 2 groups × 2 subjects each × 3 conditions
data = [
    [[10,12,14], [11,13,15]],   # Group 0 (control)
    [[20,22,25], [19,21,24]],   # Group 1 (treatment)
]
r = run_mixed_anova(data, db_path="mixed.db")
# r.between_effect.significant => True  (treatment vs control)
# r.within_effect.significant  => True  (change over time)
# r.interaction.significant    => check for differential time-course
```

## Security Considerations
- SQLite is sandboxed to a single local file.
- No network I/O; pure-math computation.
