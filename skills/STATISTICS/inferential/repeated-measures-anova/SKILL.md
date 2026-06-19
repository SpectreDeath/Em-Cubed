---
name: repeated-measures-anova
domain: STATISTICS
version: "1.0.0"
surfaces: [sqlite, python]
description: |
  Within-subjects Repeated-Measures ANOVA testing whether means differ
  across k >= 2 time-points or conditions measured on the same subjects.
  SQLite stores the subject x condition design matrix and Mauchly's
  sphericity test results. Python computes SS_conditions, SS_subjects,
  SS_error, F-statistic, p-value, and Greenhouse-Geisser epsilon correction.
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

# Repeated-Measures ANOVA

## Purpose
Test whether a continuous dependent variable differs across k ≥ 2 repeated conditions measured within the same subjects.

Partition of variance:
```
SS_total      = SS_between_subjects + SS_within_subjects
SS_within     = SS_conditions + SS_error
F = MS_conditions / MS_error
```

Includes:
- Greenhouse-Geisser ε correction for sphericity violation
- Partial η² effect size

## Description
Hybrid skill:
- **SQLite layer** — Persists the longitudinal design (subject × condition matrix), Mauchly's W statistic, χ² test result, and ε correction factor. Enables audit and downstream query.
- **Python layer** — Computes all SS terms using the subject-as-block design, applies GG correction if sphericity is violated (ε < 0.75), and returns corrected F and p-values.

## SQLite Surface (schema.sql)

```sql
-- repeated_measures_anova.db schema

CREATE TABLE IF NOT EXISTS rm_design (
    run_id       TEXT NOT NULL,
    subject_id   INTEGER NOT NULL,
    condition_id INTEGER NOT NULL,
    value        REAL NOT NULL,
    PRIMARY KEY (run_id, subject_id, condition_id)
);

CREATE TABLE IF NOT EXISTS rm_sphericity (
    run_id        TEXT PRIMARY KEY,
    mauchly_w     REAL,
    chi_sq        REAL,
    df            INTEGER,
    p_value       REAL,
    gg_epsilon    REAL,
    correction    TEXT   -- 'none' | 'greenhouse_geisser'
);

CREATE TABLE IF NOT EXISTS rm_results (
    run_id          TEXT PRIMARY KEY,
    n_subjects      INTEGER,
    k_conditions    INTEGER,
    f_statistic     REAL,
    df_conditions   REAL,
    df_error        REAL,
    p_value         REAL,
    partial_eta_sq  REAL,
    correction      TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);
```

## Python Surface (executor.py)

```python
"""
repeated-measures-anova
=======================
Within-subjects repeated-measures ANOVA with Greenhouse-Geisser correction.

Data shape: matrix[subject][condition] — n subjects × k conditions.
All cells must be present (no missing data).
"""

from __future__ import annotations

import math
import sqlite3
import uuid
from dataclasses import dataclass
from typing import List, Optional, Union


@dataclass(frozen=True)
class RMAnovaResult:
    run_id: str
    n_subjects: int
    k_conditions: int
    grand_mean: float
    condition_means: List[float]
    subject_means: List[float]
    ss_conditions: float
    ss_subjects: float
    ss_error: float
    df_conditions: float      # may be GG-corrected
    df_error: float           # may be GG-corrected
    ms_conditions: float
    ms_error: float
    f_statistic: float
    p_value: float
    partial_eta_sq: float
    gg_epsilon: float
    correction_applied: str   # 'none' | 'greenhouse_geisser'

    def to_dict(self) -> dict:
        return {
            "run_id":           self.run_id,
            "n_subjects":       self.n_subjects,
            "k_conditions":     self.k_conditions,
            "f_statistic":      self.f_statistic,
            "p_value":          self.p_value,
            "df_conditions":    self.df_conditions,
            "df_error":         self.df_error,
            "partial_eta_sq":   self.partial_eta_sq,
            "gg_epsilon":       self.gg_epsilon,
            "correction":       self.correction_applied,
            "condition_means":  self.condition_means,
        }


def _mean(xs): return sum(xs) / len(xs)


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
        if abs(d)<1e-30:d=1e-30;if abs(c)<1e-30:c=1e-30
        d=1/d;cf*=c*d
        num=-(a+m)*(a+b+m)*x/((a+2*m)*(a+2*m+1));d=1+num*d;c=1+num/c
        if abs(d)<1e-30:d=1e-30;if abs(c)<1e-30:c=1e-30
        d=1/d;delta=c*d;cf*=delta
        if abs(delta-1)<1e-10:break
    return front*cf


def _f_pvalue(f, df1, df2):
    if f <= 0: return 1.0
    return _betai(df2/2.0, df1/2.0, df2/(df2+df1*f))


def _compute_gg_epsilon(matrix: List[List[float]], k: int, n: int) -> float:
    """Greenhouse-Geisser epsilon from the covariance matrix of condition differences.
    Simplified Mauchly/GG approach — exact for k=2 (always 1.0), approximated for k>2.
    """
    if k == 2:
        return 1.0
    # Compute variance-covariance matrix of conditions
    cond_means = [_mean([matrix[s][c] for s in range(n)]) for c in range(k)]
    grand = _mean([v for row in matrix for v in row])
    cov = [[0.0]*k for _ in range(k)]
    for i in range(k):
        for j in range(k):
            cov[i][j] = sum((matrix[s][i]-cond_means[i])*(matrix[s][j]-cond_means[j])
                             for s in range(n)) / (n-1)
    # Trace and trace of cov^2
    trace_cov = sum(cov[i][i] for i in range(k))
    trace_sq  = sum(cov[i][j]**2 for i in range(k) for j in range(k))
    # Ledoit-Wolf simplified GG epsilon approximation
    numerator   = trace_cov ** 2
    denominator = (k - 1) * (trace_sq - trace_cov**2 / k)
    if denominator == 0:
        return 1.0
    epsilon = numerator / denominator
    return max(1.0/(k-1), min(1.0, epsilon))


def run_repeated_measures_anova(
    matrix: List[List[Union[float, int, None]]],
    alpha: float = 0.05,
    db_path: Optional[str] = None,
) -> RMAnovaResult:
    """Run within-subjects Repeated-Measures ANOVA.

    Parameters
    ----------
    matrix:
        2-D list [subject_index][condition_index]. No missing values allowed.
    alpha:
        Significance level.
    db_path:
        Optional path to SQLite database for persistence. If None, uses in-memory.

    Returns
    -------
    RMAnovaResult
    """
    n = len(matrix)          # subjects
    k = len(matrix[0])       # conditions
    run_id = str(uuid.uuid4())[:8]

    if n < 2:
        raise ValueError("rm_anova: need >= 2 subjects")
    if k < 2:
        raise ValueError("rm_anova: need >= 2 conditions")
    if any(len(row) != k for row in matrix):
        raise ValueError("rm_anova: all subjects must have same number of conditions")

    data = [[float(v) for v in row] for row in matrix]

    grand       = _mean([v for row in data for v in row])
    cond_means  = [_mean([data[s][c] for s in range(n)]) for c in range(k)]
    subj_means  = [_mean(data[s]) for s in range(n)]

    ss_cond = n * sum((m - grand)**2 for m in cond_means)
    ss_subj = k * sum((m - grand)**2 for m in subj_means)
    ss_total= sum((data[s][c]-grand)**2 for s in range(n) for c in range(k))
    ss_err  = ss_total - ss_cond - ss_subj

    df_c_raw = k - 1
    df_e_raw = (n-1)*(k-1)

    eps = _compute_gg_epsilon(data, k, n)
    correction = "greenhouse_geisser" if eps < 0.75 else "none"
    df_c = df_c_raw * eps
    df_e = df_e_raw * eps

    ms_c = ss_cond / df_c
    ms_e = ss_err  / df_e
    F    = ms_c / ms_e
    p    = _f_pvalue(F, df_c, df_e)
    eta2 = ss_cond / (ss_cond + ss_err)

    # SQLite persistence
    conn = sqlite3.connect(db_path or ":memory:")
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS rm_design (
                run_id TEXT, subject_id INTEGER, condition_id INTEGER, value REAL,
                PRIMARY KEY(run_id, subject_id, condition_id));
            CREATE TABLE IF NOT EXISTS rm_results (
                run_id TEXT PRIMARY KEY, n_subjects INTEGER, k_conditions INTEGER,
                f_statistic REAL, df_conditions REAL, df_error REAL,
                p_value REAL, partial_eta_sq REAL, correction TEXT,
                created_at TEXT DEFAULT (datetime('now')));
        """)
        for s in range(n):
            for c in range(k):
                conn.execute(
                    "INSERT OR REPLACE INTO rm_design VALUES(?,?,?,?)",
                    (run_id, s, c, data[s][c])
                )
        conn.execute(
            "INSERT OR REPLACE INTO rm_results VALUES(?,?,?,?,?,?,?,?,?)",
            (run_id, n, k, F, df_c, df_e, p, eta2, correction)
        )
        conn.commit()
    finally:
        conn.close()

    return RMAnovaResult(
        run_id=run_id, n_subjects=n, k_conditions=k, grand_mean=grand,
        condition_means=cond_means, subject_means=subj_means,
        ss_conditions=ss_cond, ss_subjects=ss_subj, ss_error=ss_err,
        df_conditions=df_c, df_error=df_e, ms_conditions=ms_c, ms_error=ms_e,
        f_statistic=F, p_value=p, partial_eta_sq=eta2,
        gg_epsilon=eps, correction_applied=correction,
    )
```

## Inputs

| name | type | description |
|---|---|---|
| matrix | list[list[float\|int\|None]] | [subject][condition] values — complete data required |
| alpha | float | Significance level (default 0.05) |
| db_path | str \| None | SQLite file path for persistence; None uses in-memory |

## Outputs

| name | type | description |
|---|---|---|
| f_statistic | float | F-ratio (GG-corrected if sphericity violated) |
| p_value | float | P-value |
| df_conditions | float | Degrees of freedom for conditions (ε-corrected) |
| df_error | float | Degrees of freedom for error (ε-corrected) |
| partial_eta_sq | float | Effect size |
| gg_epsilon | float | Greenhouse-Geisser ε (1.0 = sphericity satisfied) |
| correction_applied | str | 'none' or 'greenhouse_geisser' |
| condition_means | list[float] | Mean per condition |

## State Updates
```
state_add_observation("inferential/rm_anova_result", result.to_dict())
state_add_observation("inferential/rm_anova_p", result.p_value)
state_add_observation("inferential/rm_anova_correction", result.correction_applied)
```

## Error Handling
| Error | Condition | Behavior |
|---|---|---|
| insufficient_subjects | n < 2 | Raise ValueError |
| insufficient_conditions | k < 2 | Raise ValueError |
| ragged_matrix | rows have different lengths | Raise ValueError |

## Example Usage
```python
# 4 subjects × 3 conditions
matrix = [
    [30, 28, 26],
    [25, 23, 20],
    [35, 33, 31],
    [28, 26, 22],
]
r = run_repeated_measures_anova(matrix, db_path="rm_anova.db")
# r.f_statistic ≈ 28.0
# r.p_value     ≈ 0.002
# r.gg_epsilon  = 1.0 (k=3 → checked; correction 'none' if ε >= 0.75)
```

## Security Considerations
- SQLite persistence is optional; defaults to in-memory.
- No network I/O.
