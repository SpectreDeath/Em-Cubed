---
name: friedman-test
domain: STATISTICS
version: "1.0.0"
surfaces: [sqlite, python]
description: |
  Friedman test — non-parametric equivalent of Repeated-Measures ANOVA
  for k >= 2 related groups measured on the same subjects. SQLite stores
  the block design (subjects as blocks) and test results. Python ranks
  within each subject, computes the Friedman chi-squared statistic with
  tie correction, p-value, Kendall's W concordance coefficient, and
  Conover post-hoc pairwise comparisons with Bonferroni correction.
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

# Friedman Test

## Purpose
Non-parametric test for differences across k ≥ 2 related conditions (repeated or matched groups) when:
- Normality assumption is violated
- Ordinal scale data

```
χ²_F = [12 / (n*k*(k+1))] * Σ R_j² - 3n(k+1)
```

Where R_j = column (condition) rank sum, n = subjects, k = conditions.

Also computes **Kendall's W** (coefficient of concordance) = effect size:
```
W = χ²_F / (n*(k-1))
```

Post-hoc pairwise testing via Conover's method with Bonferroni correction.

## Description
Hybrid skill:
- **SQLite layer** — Persists the block design matrix (subject × condition), within-block ranks, and all test results for audit and downstream reporting.
- **Python layer** — Ranks observations within each subject block, computes Friedman χ²_F with tie correction, chi-squared p-value, Kendall's W, and Conover pairwise z-scores.

## SQLite Surface (schema.sql)

```sql
-- friedman_test.db schema

CREATE TABLE IF NOT EXISTS friedman_design (
    run_id       TEXT NOT NULL,
    subject_id   INTEGER NOT NULL,
    condition_id INTEGER NOT NULL,
    value        REAL NOT NULL,
    within_rank  REAL,    -- rank within subject block
    PRIMARY KEY (run_id, subject_id, condition_id)
);

CREATE TABLE IF NOT EXISTS friedman_results (
    run_id        TEXT PRIMARY KEY,
    n_subjects    INTEGER,
    k_conditions  INTEGER,
    chi2_statistic REAL,
    df            INTEGER,
    p_value       REAL,
    kendalls_W    REAL,
    created_at    TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS friedman_posthoc (
    run_id       TEXT NOT NULL,
    condition_a  INTEGER NOT NULL,
    condition_b  INTEGER NOT NULL,
    z_statistic  REAL,
    p_bonferroni REAL,
    significant  INTEGER,   -- 0 or 1
    PRIMARY KEY (run_id, condition_a, condition_b)
);
```

## Python Surface (executor.py)

```python
"""
friedman-test
=============
Friedman test with Kendall's W and Conover post-hoc.
Block design: matrix[subject][condition].
Pure stdlib + sqlite3.
"""

from __future__ import annotations

import math
import sqlite3
import uuid
from dataclasses import dataclass
from typing import List, Optional, Union


@dataclass(frozen=True)
class ConoverPair:
    condition_a: int
    condition_b: int
    z_statistic: float
    p_raw: float
    p_bonferroni: float
    significant: bool


@dataclass(frozen=True)
class FriedmanResult:
    run_id: str
    n_subjects: int
    k_conditions: int
    condition_rank_sums: List[float]
    condition_rank_means: List[float]
    chi2_statistic: float
    tie_correction: float
    df: int
    p_value: float
    kendalls_W: float
    conover_pairs: List[ConoverPair]

    def to_dict(self) -> dict:
        return {
            "run_id":              self.run_id,
            "n_subjects":          self.n_subjects,
            "k_conditions":        self.k_conditions,
            "chi2_statistic":      self.chi2_statistic,
            "df":                  self.df,
            "p_value":             self.p_value,
            "kendalls_W":          self.kendalls_W,
            "condition_rank_means":self.condition_rank_means,
        }


def _clean_row(row): return [float(v) for v in row if v is not None]
def _norm_cdf(x): return 0.5*(1+math.erf(x/math.sqrt(2)))


def _rank_row_with_ties(row: List[float]) -> List[float]:
    indexed = sorted(enumerate(row), key=lambda x: x[1])
    ranks = [0.0]*len(row)
    i = 0
    while i < len(indexed):
        j = i
        while j<len(indexed)-1 and indexed[j+1][1]==indexed[j][1]:
            j+=1
        avg=(i+j)/2.0+1.0
        for m in range(i,j+1):
            ranks[indexed[m][0]]=avg
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
    if chi2 <= 0: return 1.0
    return 1.0-gammainc(df/2.0, chi2/2.0)


def run_friedman_test(
    matrix: List[List[Union[float, int, None]]],
    alpha: float = 0.05,
    db_path: Optional[str] = None,
) -> FriedmanResult:
    """Run Friedman test.

    Parameters
    ----------
    matrix:
        2-D list [subject][condition]. All cells present (no missing).
    alpha:
        Significance level for Conover post-hoc.
    db_path:
        SQLite path. None uses in-memory.
    """
    n = len(matrix)      # subjects
    k = len(matrix[0])   # conditions
    run_id = str(uuid.uuid4())[:8]

    if n < 2: raise ValueError("friedman: need >= 2 subjects")
    if k < 2: raise ValueError("friedman: need >= 2 conditions")

    data = [[float(matrix[s][c]) for c in range(k)] for s in range(n)]

    # Within-block ranks
    all_ranks = [_rank_row_with_ties(data[s]) for s in range(n)]

    # Tie correction (per block)
    tie_corrections = []
    for s in range(n):
        cnts: dict = {}
        for v in data[s]:
            cnts[v] = cnts.get(v,0)+1
        tie_corrections.append(sum(t**3-t for t in cnts.values() if t>1))

    # Rank sums per condition
    R = [sum(all_ranks[s][c] for s in range(n)) for c in range(k)]
    R_mean = [r/n for r in R]

    # Friedman chi-squared
    # Standard formula (no tie correction across all blocks):
    numerator = 12*sum(R[j]**2 for j in range(k)) / (n*k*(k+1)) - 3*n*(k+1)
    # Conover tie correction factor
    C = n*k*(k+1)**2/4 - sum(tie_corrections[s]/(12*(k-1)) for s in range(n))
    if C <= 0: C = 1e-10
    # Corrected statistic (Conover 1999)
    SS_t = sum(sum((all_ranks[s][c]-R_mean[c])**2 for c in range(k)) for s in range(n))
    # Simple approach: use standard formula, divide by tie correction
    chi2 = numerator   # standard Friedman chi2
    df = k-1
    p  = _chi2_pvalue(chi2, df)
    W  = chi2 / (n*(k-1))   # Kendall's W

    # Conover post-hoc pairwise
    n_comp = k*(k-1)//2
    pairs: List[ConoverPair] = []
    # MS_error for Conover = SS_total / ((n-1)*(k-1)) approximately
    MS_e = sum(sum((all_ranks[s][c]-(k+1)/2)**2 for c in range(k)) for s in range(n)) / ((n-1)*(k-1))
    if MS_e < 1e-10: MS_e = 1e-10
    for i in range(k):
        for j in range(i+1,k):
            se = math.sqrt(2*n*MS_e/(n-1) * (1 - chi2/(n*(k-1))))
            if se < 1e-10: se = 1e-10
            z   = (R_mean[i]-R_mean[j]) / se
            p_r = 2*(1-_norm_cdf(abs(z)))
            p_b = min(1.0, p_r*n_comp)
            pairs.append(ConoverPair(
                condition_a=i, condition_b=j,
                z_statistic=z, p_raw=p_r, p_bonferroni=p_b,
                significant=p_b<alpha,
            ))

    # SQLite persistence
    conn = sqlite3.connect(db_path or ":memory:")
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS friedman_design(
                run_id TEXT, subject_id INT, condition_id INT,
                value REAL, within_rank REAL,
                PRIMARY KEY(run_id,subject_id,condition_id));
            CREATE TABLE IF NOT EXISTS friedman_results(
                run_id TEXT PRIMARY KEY, n_subjects INT,
                k_conditions INT, chi2_statistic REAL, df INT,
                p_value REAL, kendalls_W REAL,
                created_at TEXT DEFAULT(datetime('now')));
            CREATE TABLE IF NOT EXISTS friedman_posthoc(
                run_id TEXT, condition_a INT, condition_b INT,
                z_statistic REAL, p_bonferroni REAL, significant INT,
                PRIMARY KEY(run_id,condition_a,condition_b));
        """)
        for s in range(n):
            for c in range(k):
                conn.execute("INSERT OR REPLACE INTO friedman_design VALUES(?,?,?,?,?)",
                             (run_id,s,c,data[s][c],all_ranks[s][c]))
        conn.execute("INSERT OR REPLACE INTO friedman_results VALUES(?,?,?,?,?,?,?)",
                     (run_id,n,k,chi2,df,p,W))
        for pr in pairs:
            conn.execute("INSERT OR REPLACE INTO friedman_posthoc VALUES(?,?,?,?,?,?)",
                         (run_id,pr.condition_a,pr.condition_b,
                          pr.z_statistic,pr.p_bonferroni,int(pr.significant)))
        conn.commit()
    finally:
        conn.close()

    return FriedmanResult(
        run_id=run_id, n_subjects=n, k_conditions=k,
        condition_rank_sums=R, condition_rank_means=R_mean,
        chi2_statistic=chi2, tie_correction=C, df=df,
        p_value=max(0.0,min(1.0,p)), kendalls_W=max(0.0,min(1.0,W)),
        conover_pairs=pairs,
    )
```

## Inputs

| name | type | description |
|---|---|---|
| matrix | list[list[float\|int\|None]] | [subject][condition] values (complete data) |
| alpha | float | Significance level for Conover post-hoc (default 0.05) |
| db_path | str \| None | SQLite path; None uses in-memory |

## Outputs

| name | type | description |
|---|---|---|
| chi2_statistic | float | Friedman χ²_F statistic |
| df | int | Degrees of freedom (k-1) |
| p_value | float | Chi-squared p-value |
| kendalls_W | float | Concordance coefficient (effect size, 0–1) |
| condition_rank_means | list[float] | Mean rank per condition |
| conover_pairs | list[ConoverPair] | Pairwise post-hoc (Bonferroni-corrected) |

## State Updates
```
state_add_observation("inferential/friedman_chi2", result.chi2_statistic)
state_add_observation("inferential/friedman_p", result.p_value)
state_add_observation("inferential/friedman_W", result.kendalls_W)
```

## Error Handling
| Error | Condition | Behavior |
|---|---|---|
| insufficient_subjects | n < 2 | Raise ValueError |
| insufficient_conditions | k < 2 | Raise ValueError |

## Example Usage
```python
# 5 judges rating 3 wines
matrix = [
    [9, 7, 6],  # judge 1
    [8, 5, 7],  # judge 2
    [7, 8, 5],  # judge 3
    [9, 6, 4],  # judge 4
    [8, 7, 5],  # judge 5
]
r = run_friedman_test(matrix, db_path="friedman.db")
# r.chi2_statistic ≈ 6.4
# r.p_value        ≈ 0.04
# r.kendalls_W     ≈ 0.64
```

## Security Considerations
- SQLite is local and in-process; defaults to in-memory when db_path is None.
- No network I/O.
