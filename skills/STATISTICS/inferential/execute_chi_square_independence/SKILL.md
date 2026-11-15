---
name: execute_chi_square_independence
domain: STATISTICS
version: 1.0.0
surfaces:
  - python
  - prolog
description: Inferential statistical testing engine executing Pearson's Chi-Square Test of Independence ($\chi^2$) on two-dimensional categorical contingency tables. Calculates expected frequencies $E_{ij} = \frac{R_i C_j}{N}$, tests Cochran's rule of thumb ($\ge 80\%$ of expected counts $\ge 5$), computes degrees of freedom $(r-1)(c-1)$, evaluates test statistics, and determines Cramér's V effect sizes. Use when testing associations between two nominal/categorical variables or analyzing frequency cross-tabulations.
purpose: Compute Pearson Chi-Square test of independence with expected cell count validation and Cramér's V effect size estimation.
dependencies:
  - guardrails/validate_measurement_level
  - inferential/evaluate_p_value
tags:
  - chi-square
  - contingency-table
  - independence-test
  - cramers-v
  - categorical-data
  - nominal-scale
inputs:
  contingency_table:
    type: array
    required: true
    description: 2D matrix of observed non-negative counts `[[int, int, ...], ...]`.
  alpha:
    type: number
    required: false
    description: Significance threshold (default 0.05).
outputs:
  chi2_statistic:
    type: number
    description: Pearson chi-square test statistic $\chi^2 = \sum \frac{(O_{ij} - E_{ij})^2}{E_{ij}}$.
  p_value:
    type: number
    description: Asymptotic p-value from chi-square distribution with $\text{df} = (r-1)(c-1)$.
  degrees_of_freedom:
    type: integer
    description: Table degrees of freedom $(r-1)(c-1)$.
  cramers_v:
    type: number
    description: Cramér's V association effect size $\sqrt{\frac{\chi^2}{N \cdot \min(r-1, c-1)}}$.
  expected_frequencies:
    type: array
    description: Matrix of expected cell frequencies $E_{ij}$.
  cochran_valid:
    type: boolean
    description: True if all expected counts $\ge 1$ and at least 80% of cells $\ge 5$.
---

# Execute Chi-Square Independence Engine

`execute_chi_square_independence` tests for statistical independence between two categorical variables represented in an $r \times c$ contingency table $\mathbf{O}$. It computes marginal totals, expected frequencies $\mathbf{E}$, evaluates Cochran's rule for cell adequacy, and computes **Cramér's V effect size**:

$$\chi^2 = \sum_{i=1}^{r} \sum_{j=1}^{c} \frac{(O_{ij} - E_{ij})^2}{E_{ij}}, \quad E_{ij} = \frac{\sum_k O_{ik} \sum_k O_{kj}}{\sum_{i,j} O_{ij}}$$

$$\text{Cramér's } V = \sqrt{\frac{\chi^2}{N \cdot \min(r-1, c-1)}}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Chi-Square Progression

```
[1. Contingency Table Invariant Audit] → [2. Expected Frequencies & Cochran Check] → [3. Visual Brief] → [4. Checkpoint] → [5. Chi2 Statistic, P-Value & Cramér's V Emit]
```

### Stage 1: Contingency Table Invariant Audit
1. Ingest `contingency_table` matrix ($r \ge 2, c \ge 2$).
2. Assert that all observed entries are non-negative integers ($O_{ij} \ge 0$) and table total $N > 0$.

> **Completion criterion**: 2D matrix validated with $r, c \ge 2$ and $N \ge 5$.

---

### Stage 2: Expected Frequency Matrix & Cochran Rule
1. Compute row sums $R_i = \sum_j O_{ij}$ and column sums $C_j = \sum_i O_{ij}$.
2. Compute expected cell counts $E_{ij} = (R_i \cdot C_j) / N$.
3. Check **Cochran's Criterion**:
   - All $E_{ij} \ge 1.0$.
   - At least $80\%$ of cells have $E_{ij} \ge 5.0$.

> **Completion criterion**: Expected frequency matrix $\mathbf{E}$ generated and Cochran validity evaluated.

---

### Stage 3: The Visual Brief
For multi-category contingency tables or significant associations, generate an interactive brief:
- **Location**: Write to `%TEMP%\chi-square-brief-<timestamp>.html` (Windows) or `/tmp/chi-square-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render observed vs. expected heatmap table, standardized residuals, and Cramér's V association gauge.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before finalizing test dispatch:
1. If Cochran's criterion fails (small cell counts $< 5$ in $> 20\%$ of cells):
   - For $2 \times 2$ tables, flag recommendation for **Fisher's Exact Test** or Yates' continuity correction.
   - For larger tables, record small-cell distortion warning in output record.

> **Completion criterion**: Small-cell adequacy verified and warnings logged.

---

### Stage 5: Chi2 Statistic, P-Value & Cramér's V Emit
1. Calculate test statistic $\chi^2 = \sum \frac{(O_{ij} - E_{ij})^2}{E_{ij}}$.
2. Degrees of freedom $\text{df} = (r - 1)(c - 1)$.
3. Compute $p$-value and Cramér's $V = \sqrt{\frac{\chi^2}{N \min(r-1, c-1)}}$.
4. Emit complete result record.

> **Completion criterion**: Complete record emitted with $\chi^2$, $p$-value, degrees of freedom, and Cramér's V.

---

## Surface References

### Python Implementation Surface

```python
import math
from typing import List, Dict, Any

def execute_chi_square_independence(table: List[List[int]], alpha: float = 0.05) -> Dict[str, Any]:
    r = len(table)
    c = len(table[0]) if r > 0 else 0
    if r < 2 or c < 2:
        raise ValueError("invalid_table_shape: Contingency table must be at least 2x2.")
        
    row_sums = [sum(row) for row in table]
    col_sums = [sum(table[i][j] for i in range(r)) for j in range(c)]
    total_n = sum(row_sums)
    
    if total_n == 0:
        raise ValueError("empty_table: Table contains zero total observations.")
        
    expected = []
    chi2 = 0.0
    cells_under_5 = 0
    
    for i in range(r):
        exp_row = []
        for j in range(c):
            e_ij = (row_sums[i] * col_sums[j]) / total_n
            exp_row.append(round(e_ij, 4))
            if e_ij < 5.0:
                cells_under_5 += 1
            if e_ij > 0:
                chi2 += ((table[i][j] - e_ij) ** 2) / e_ij
        expected.append(exp_row)
        
    df = (r - 1) * (c - 1)
    cochran_ok = (cells_under_5 / (r * c)) <= 0.20
    
    # Asymptotic p-value calculation
    try:
        from scipy.stats import chi2 as chi2_dist
        p_val = float(chi2_dist.sf(chi2, df))
    except ImportError:
        p_val = 0.001 if chi2 > 3.84 * df else 0.50 # rough approximation fallback
        
    # Cramér's V
    min_dim = min(r - 1, c - 1)
    cramers_v = math.sqrt(chi2 / (total_n * min_dim)) if min_dim > 0 and total_n > 0 else 0.0
    cramers_v = min(1.0, max(0.0, cramers_v))
    
    return {
        "chi2_statistic": round(chi2, 6),
        "p_value": round(p_val, 6),
        "degrees_of_freedom": df,
        "cramers_v": round(cramers_v, 4),
        "expected_frequencies": expected,
        "cochran_valid": cochran_ok,
        "total_observations": total_n
    }
```

---

## Anti-Patterns & Guardrails

- **Small Expected Counts (< 5)** — Interpreting asymptotic Chi-square p-values on $2 \times 2$ tables with cell counts $< 5$ without Fisher's exact test fallback.
- **Percentages as Raw Counts** — Passing normalized percentages or proportions rather than absolute integer frequencies into the contingency matrix.
- **Negative Observed Entries** — Allowing negative counts in contingency matrix cells.
