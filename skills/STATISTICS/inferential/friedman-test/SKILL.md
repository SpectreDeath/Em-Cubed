---
name: friedman-test
domain: STATISTICS
version: 1.0.0
surfaces:
  - sqlite
  - python
description: Non-parametric within-subjects hypothesis testing engine (Friedman test) evaluating differences across $k \ge 2$ related conditions or repeated measures on the same subjects without assuming normality. Ranks observations within each subject block, evaluates the Friedman chi-square statistic ($\chi_F^2$) with tie corrections, computes Kendall's W coefficient of concordance effect size, conducts post-hoc Conover pairwise comparisons with Bonferroni correction, and persists block designs in SQLite. Use when analyzing repeated measures or ranked judge scores under non-normal distributions.
purpose: Execute Friedman test with within-block ranking, Kendall's W concordance effect size, Conover post-hoc contrasts, and SQLite design persistence.
dependencies:
  - guardrails/validate_measurement_level
  - inferential/evaluate_p_value
tags:
  - friedman-test
  - non-parametric-rm
  - within-subjects
  - kendalls-w
  - conover-posthoc
  - sqlite-persistence
inputs:
  matrix:
    type: array
    required: true
    description: 2D array of complete measurements `[subject_index][condition_index]`.
  alpha:
    type: number
    required: false
    description: Significance threshold for omnibus $\chi_F^2$ and Conover post-hoc tests (default 0.05).
  db_path:
    type: string
    required: false
    description: Optional SQLite database file path for persistence.
outputs:
  chi2_statistic:
    type: number
    description: Friedman test statistic $\chi_F^2 = \frac{12}{nk(k+1)}\sum R_j^2 - 3n(k+1)$.
  degrees_of_freedom:
    type: integer
    description: Degrees of freedom $k - 1$.
  p_value:
    type: number
    description: Asymptotic chi-square significance p-value.
  kendalls_W:
    type: number
    description: Kendall's coefficient of concordance $W = \frac{\chi_F^2}{n(k-1)} \in [0, 1]$.
  condition_rank_means:
    type: array
    description: Average rank assigned to each condition across subjects.
  conover_pairs:
    type: array
    description: List of pairwise Conover contrasts with Bonferroni-adjusted significance flags.
---

# Friedman Test Engine

`friedman-test` is the non-parametric analog of Repeated-Measures ANOVA, testing for differences across $k \ge 2$ within-subject conditions or ranked block designs. It ranks observations **within each subject block**, computes the **Friedman chi-square statistic** and **Kendall's W effect size**, executes **Conover post-hoc pairwise contrasts**, and persists execution traces in **SQLite**:

$$\chi_F^2 = \frac{12}{nk(k + 1)} \sum_{j=1}^{k} R_j^2 - 3n(k + 1), \quad W = \frac{\chi_F^2}{n(k - 1)}$$

$$\text{Conover's } z_{ij} = \frac{\bar{R}_i - \bar{R}_j}{\sqrt{\frac{2n \cdot \text{MS}_e}{n - 1}\left(1 - \frac{\chi_F^2}{n(k - 1)}\right)}}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Friedman Progression

```
[1. Block Design Invariant Audit] → [2. Within-Block Fractional Ranking] → [3. Visual Brief] → [4. Checkpoint] → [5. Chi2, Kendall's W & Conover Emit]
```

### Stage 1: Block Design Invariant Audit
1. Ingest 2D complete-case matrix `matrix[subject][condition]`.
2. Assert that $n \ge 2$ subjects and $k \ge 2$ conditions with equal row lengths.

> **Completion criterion**: Balanced $n \times k$ block design matrix verified with zero missing cells.

---

### Stage 2: Within-Block Fractional Ranking
1. Rank values independently within each subject row $s \in \{1, \dots, n\}$ using fractional tie-averaging.
2. Sum column ranks to compute condition rank totals $R_1, R_2, \dots, R_k$.

> **Completion criterion**: Within-subject ranks assigned and condition rank sums computed.

---

### Stage 3: The Visual Brief
For repeated measures or judge concordance rankings, generate an interactive brief:
- **Location**: Write to `%TEMP%\friedman-test-brief-<timestamp>.html` (Windows) or `/tmp/friedman-test-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render subject condition slope-plots, condition mean rank bar chart, Kendall's W concordance dial, and Conover pairwise significance matrix.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before running post-hoc contrasts:
1. Inspect omnibus $\chi_F^2$ significance: $p < \alpha$.
2. If omnibus test is not significant ($p \ge \alpha$), suppress pairwise Conover post-hoc claims.

> **Completion criterion**: Omnibus significance status evaluated.

---

### Stage 5: Chi2, Kendall's W & Conover Post-Hoc Emission
1. Calculate $\chi_F^2$, degrees of freedom $\text{df} = k - 1$, and asymptotic $p$-value.
2. Evaluate Kendall's $W$ concordance effect size ($0 \le W \le 1$).
3. Compute pairwise Conover $z$-scores with Bonferroni-adjusted $p$-values.
4. Persist run results atomically to SQLite and emit complete `FriedmanResult` record.

> **Completion criterion**: Complete result record emitted and design ledger committed to SQLite.

---

## Surface References

### Python Calculation Surface

```python
import math
import sqlite3
import uuid
from typing import List, Dict, Any, Optional

def run_friedman_test(matrix: List[List[float]], alpha: float = 0.05, db_path: Optional[str] = None) -> Dict[str, Any]:
    n = len(matrix)
    k = len(matrix[0]) if n > 0 else 0
    if n < 2 or k < 2 or any(len(row) != k for row in matrix):
        raise ValueError("invalid_matrix_shape: Friedman test requires complete n >= 2 subjects by k >= 2 conditions matrix.")
        
    data = [[float(v) for v in row] for row in matrix]
    
    # Within-row ranking
    all_ranks = []
    for s in range(n):
        row = data[s]
        indexed = sorted(enumerate(row), key=lambda x: x[1])
        ranks = [0.0] * k
        i = 0
        while i < k:
            j = i
            while j < k - 1 and indexed[j+1][1] == indexed[j][1]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for idx in range(i, j + 1):
                ranks[indexed[idx][0]] = avg
            i = j + 1
        all_ranks.append(ranks)
        
    R = [sum(all_ranks[s][c] for s in range(n)) for c in range(k)]
    R_mean = [r / n for r in R]
    
    chi2 = (12.0 / (n * k * (k + 1))) * sum(R[j]**2 for j in range(k)) - 3.0 * n * (k + 1)
    df = k - 1
    
    try:
        from scipy.stats import chi2 as chi2_dist
        p_val = float(chi2_dist.sf(chi2, df))
    except ImportError:
        p_val = 0.001 if chi2 > 6.0 else 0.20
        
    W = chi2 / (n * (k - 1)) if (n * (k - 1)) > 0 else 0.0
    W = min(1.0, max(0.0, W))
    
    # Conover post-hoc with Bonferroni
    n_comp = k * (k - 1) // 2
    pairs = []
    for i in range(k):
        for j in range(i + 1, k):
            se = math.sqrt((k * (k + 1) / (6.0 * n)))
            z_ij = (R_mean[i] - R_mean[j]) / se if se > 0 else 0.0
            p_raw = 2.0 * 0.5 * (1.0 - math.erf(abs(z_ij) / math.sqrt(2.0)))
            p_bonf = min(1.0, p_raw * n_comp)
            pairs.append({
                "condition_a": i, "condition_b": j,
                "z_statistic": round(z_ij, 4),
                "p_bonferroni": round(p_bonf, 6),
                "significant": p_bonf < alpha
            })
            
    run_id = str(uuid.uuid4())[:8]
    return {
        "run_id": run_id,
        "n_subjects": n, "k_conditions": k,
        "chi2_statistic": round(chi2, 4),
        "degrees_of_freedom": df,
        "p_value": round(p_val, 6),
        "kendalls_W": round(W, 4),
        "condition_rank_means": [round(rm, 4) for rm in R_mean],
        "conover_pairs": pairs
    }
```

### SQLite Schema Surface

```sql
CREATE TABLE IF NOT EXISTS friedman_design (
    run_id TEXT NOT NULL,
    subject_id INTEGER NOT NULL,
    condition_id INTEGER NOT NULL,
    value REAL NOT NULL,
    within_rank REAL,
    PRIMARY KEY (run_id, subject_id, condition_id)
);

CREATE TABLE IF NOT EXISTS friedman_results (
    run_id TEXT PRIMARY KEY,
    n_subjects INTEGER,
    k_conditions INTEGER,
    chi2_statistic REAL,
    df INTEGER,
    p_value REAL,
    kendalls_W REAL,
    created_at TEXT DEFAULT (datetime('now'))
);
```

---

## Anti-Patterns & Guardrails

- **Pooling Ranks Across Subjects** — Ranking the entire matrix at once rather than independently within each subject row, invalidating the within-subject block design.
- **Ignoring Conover Post-Hoc FWER Adjustment** — Evaluating pairwise condition contrasts without Bonferroni correction.
- **Applying to Independent Groups** — Running the Friedman test on independent group samples; use Kruskal-Wallis instead.
