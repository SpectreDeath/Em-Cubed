---
name: mann-whitney-u-test
domain: STATISTICS
version: 1.0.0
surfaces:
  - prolog
  - python
description: Non-parametric two-sample hypothesis testing engine (Mann-Whitney U / Wilcoxon rank-sum test) for comparing two independent groups without assuming normality. Enforces measurement-level (ordinal/interval/ratio) and sample-size constraints in Prolog, and evaluates fractional tie-adjusted ranks, U1/U2 statistics, continuity-corrected normal z-approximations, and rank-biserial correlation effect sizes in Python. Use when comparing two independent groups under non-normal distributions or ordinal ranking scales.
purpose: Execute Mann-Whitney U test with tie correction, continuity-adjusted z-approximation, and rank-biserial correlation effect size.
dependencies:
  - guardrails/validate_measurement_level
  - inferential/evaluate_p_value
tags:
  - mann-whitney-u
  - wilcoxon-rank-sum
  - non-parametric
  - rank-biserial-correlation
  - ordinal-data
  - two-sample-test
inputs:
  group1:
    type: array
    required: true
    description: First independent sample vector (None and NaN values are cleaned).
  group2:
    type: array
    required: true
    description: Second independent sample vector (None and NaN values are cleaned).
  alpha:
    type: number
    required: false
    description: Significance threshold (default 0.05).
outputs:
  U_statistic:
    type: number
    description: Minimal test statistic $U = \min(U_1, U_2)$.
  z_statistic:
    type: number
    description: Asymptotic normal z-statistic with continuity correction.
  p_value:
    type: number
    description: Two-tailed significance p-value.
  rank_biserial_r:
    type: number
    description: Rank-biserial correlation effect size $r = 1 - \frac{2U}{n_1 n_2} \in [-1, 1]$.
  effect_label:
    type: string
    description: Qualitative effect label ('small', 'medium', 'large').
  tie_correction:
    type: number
    description: Variance adjustment factor applied for tied observations.
---

# Mann-Whitney U Test Engine

`mann-whitney-u-test` (Wilcoxon rank-sum test) evaluates stochastic dominance between two independent sample groups without assuming normality. It enforces **ordinal-or-above measurement gates in Prolog** and computes fractional ranks, tie corrections, and **rank-biserial correlation** in **Python**:

$$U_1 = R_1 - \frac{n_1(n_1 + 1)}{2}, \quad U_2 = n_1 n_2 - U_1, \quad U = \min(U_1, U_2)$$

$$r = 1 - \frac{2U}{n_1 n_2}, \quad z = \frac{U - \frac{n_1 n_2}{2} + 0.5}{\sqrt{\frac{n_1 n_2}{12}\left(N + 1 - \sum \frac{t_i^3 - t_i}{N(N-1)}\right)}}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Mann-Whitney Progression

```
[1. Vector Sanitization & Sample Audit] → [2. Combined Ranking & Tie Adjustment] → [3. Visual Brief] → [4. Checkpoint] → [5. U-Stat, Z-Score & Effect Size Emit]
```

### Stage 1: Vector Sanitization & Sample Size Audit
1. Ingest `group1` and `group2` vectors and drop invalid/NaN entries.
2. Assert that $n_1 \ge 3$ and $n_2 \ge 3$.

> **Completion criterion**: Clean independent sample vectors verified ($n_1, n_2 \ge 3$).

---

### Stage 2: Combined Ranking & Tie Adjustment
1. Concatenate $g_1$ and $g_2$ into combined vector $\mathbf{v}$ ($N = n_1 + n_2$).
2. Assign fractional average ranks for tied values.
3. Compute tie variance correction term: $T = \sum (t_i^3 - t_i) / (N(N - 1))$.

> **Completion criterion**: Tie-adjusted rank sums $R_1$ and $R_2$ computed.

---

### Stage 3: The Visual Brief
For non-parametric group comparisons, generate an interactive brief:
- **Location**: Write to `%TEMP%\mann-whitney-brief-<timestamp>.html` (Windows) or `/tmp/mann-whitney-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render jittered rank strip-plots, cumulative empirical CDF curves for both groups, and rank-biserial $r$ effect dial.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before computing asymptotic approximations:
1. Verify whether $N = n_1 + n_2 \le 25$.
2. For small samples ($N \le 25$), flag recommendation for exact permutation distribution where available.

> **Completion criterion**: Sample size regime confirmed for asymptotic vs. exact calculation.

---

### Stage 5: U-Statistic, P-Value & Rank-Biserial Emission
1. Calculate $U_1, U_2$, and $U = \min(U_1, U_2)$.
2. Calculate continuity-corrected $z$-statistic and two-tailed $p$-value.
3. Evaluate rank-biserial correlation $r = 1 - 2U / (n_1 n_2)$ and qualitative magnitude.
4. Emit complete `MannWhitneyResult` record.

> **Completion criterion**: Complete result record emitted with test statistics and effect size.

---

## Surface References

### Python Calculation Surface

```python
import math
from typing import List, Dict, Any

def _clean(xs): return [float(v) for v in xs if v is not None and not math.isnan(float(v))]

def run_mann_whitney_u(group1: List[float], group2: List[float], alpha: float = 0.05) -> Dict[str, Any]:
    g1, g2 = _clean(group1), _clean(group2)
    n1, n2 = len(g1), len(g2)
    if n1 < 3 or n2 < 3:
        raise ValueError("insufficient_sample: Each group requires N >= 3.")
        
    combined = g1 + g2
    N = n1 + n2
    
    # Fractional ranking
    indexed = sorted(enumerate(combined), key=lambda x: x[1])
    ranks = [0.0] * N
    i = 0
    while i < N:
        j = i
        while j < N - 1 and indexed[j+1][1] == indexed[j][1]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = avg_rank
        i = j + 1
        
    R1 = sum(ranks[:n1])
    U1 = R1 - (n1 * (n1 + 1)) / 2.0
    U2 = (n1 * n2) - U1
    U_min = min(U1, U2)
    
    # Ties correction
    counts = {}
    for v in combined: counts[v] = counts.get(v, 0) + 1
    ties = [c for c in counts.values() if c > 1]
    tie_corr = sum(t**3 - t for t in ties) / (N * (N - 1)) if ties else 0.0
    
    # Asymptotic Z with continuity correction
    mu_u = (n1 * n2) / 2.0
    var_u = (n1 * n2 / 12.0) * (N + 1 - tie_corr)
    z = (U_min - mu_u + 0.5) / math.sqrt(var_u) if var_u > 0 else 0.0
    
    # Two-tailed p-value
    p_val = 2.0 * 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
    p_val = min(1.0, max(0.0, p_val))
    
    # Effect size
    r_biserial = 1.0 - (2.0 * U_min) / (n1 * n2)
    abs_r = abs(r_biserial)
    label = "small" if abs_r < 0.3 else ("medium" if abs_r < 0.5 else "large")
    
    return {
        "n1": n1, "n2": n2,
        "U1": round(U1, 4), "U2": round(U2, 4), "U_statistic": round(U_min, 4),
        "z_statistic": round(z, 6),
        "p_value": round(p_val, 6),
        "rank_biserial_r": round(r_biserial, 4),
        "effect_label": label,
        "tie_correction": round(tie_corr, 6)
    }
```

---

## Anti-Patterns & Guardrails

- **Paired Sample Misuse** — Running Mann-Whitney on paired pre/post measurements rather than the Wilcoxon Signed-Rank test.
- **Ignoring Extreme Ties** — Computing variance without tie correction factors when a high proportion of sample values are identical.
- **Micro-Sample Distortion** — Running Mann-Whitney on groups with $N < 3$, where the minimum possible p-value cannot reach significance.
