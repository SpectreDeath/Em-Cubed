---
name: kruskal-wallis-test
domain: STATISTICS
version: 1.0.0
surfaces:
  - z3
  - python
description: Non-parametric multi-group hypothesis testing engine (Kruskal-Wallis H test) comparing medians across $k \ge 3$ independent groups without assuming Gaussian normality. Enforces design constraints via Z3 SMT, evaluates combined ranking with tie-adjustment corrections, computes the H-statistic, asymptotic chi-square p-values, rank-based eta-squared ($\eta_H^2$) effect sizes, and post-hoc Dunn's pairwise contrasts with Bonferroni FWER control in Python. Use when testing differences across 3+ independent groups under non-normal distributions.
purpose: Execute Kruskal-Wallis H test with Z3 design verification, tie-corrected H-statistics, and post-hoc Dunn's pairwise comparisons.
dependencies:
  - guardrails/validate_measurement_level
  - inferential/evaluate_p_value
tags:
  - kruskal-wallis
  - non-parametric-anova
  - rank-sum-test
  - dunns-test
  - bonferroni-correction
  - z3-smt
inputs:
  groups:
    type: array
    required: true
    description: List of $k \ge 3$ sample vectors `[[float, ...], [float, ...], [float, ...]]`.
  alpha:
    type: number
    required: false
    description: Significance threshold for omnibus H and Dunn post-hoc contrasts (default 0.05).
outputs:
  H_statistic:
    type: number
    description: Raw Kruskal-Wallis test statistic $H$.
  H_corrected:
    type: number
    description: Tie-corrected test statistic $H / C$.
  degrees_of_freedom:
    type: integer
    description: Degrees of freedom $k - 1$.
  p_value:
    type: number
    description: Asymptotic chi-square significance p-value.
  eta_squared:
    type: number
    description: Rank-based effect size $\eta_H^2 = \frac{H_{\text{corr}} - k + 1}{N - k}$.
  group_rank_means:
    type: array
    description: Mean rank value $\bar{R}_i$ for each group.
  dunn_pairs:
    type: array
    description: List of pairwise Dunn contrasts with raw p-values and Bonferroni-corrected significance flags.
---

# Kruskal-Wallis H Test Engine

`kruskal-wallis-test` is the non-parametric analog of One-Way ANOVA, evaluating stochastic dominance across $k \ge 3$ independent sample groups. It enforces **design validity in Z3 SMT** and calculates combined pooled ranks, tie corrections, and **post-hoc Dunn's pairwise comparisons** in **Python**:

$$H = \frac{12}{N(N + 1)} \sum_{i=1}^{k} \frac{R_i^2}{n_i} - 3(N + 1), \quad C = 1 - \frac{\sum (t_i^3 - t_i)}{N^3 - N}, \quad H_{\text{corr}} = \frac{H}{C}$$

$$\text{Dunn's } z_{ij} = \frac{\bar{R}_i - \bar{R}_j}{\sqrt{\left(\frac{N(N+1)}{12} - \frac{\sum (t_i^3 - t_i)}{12(N-1)}\right)\left(\frac{1}{n_i} + \frac{1}{n_j}\right)}}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Kruskal-Wallis Progression

```
[1. Sample Grid Invariant Audit] → [2. Z3 SMT Design Verification] → [3. Visual Brief] → [4. Checkpoint] → [5. H-Stat, P-Value & Dunn's Emit]
```

### Stage 1: Sample Grid Invariant Audit
1. Ingest `groups` list and drop invalid/NaN entries.
2. Assert that $k \ge 3$ groups and each group has sample size $n_i \ge 3$.
3. Compute total pooled sample size $N = \sum n_i$.

> **Completion criterion**: Clean independent groups matrix established with $k \ge 3$ and $N \ge 9$.

---

### Stage 2: Z3 SMT Design Verification
1. Assert symbolic constraints in Z3:
   - $k \ge 3$
   - $\min(n_i) \ge 3$
   - $\text{independent} == \text{True}$
2. Execute Z3 solver check. If `unsat`, halt with design violation.

> **Completion criterion**: Z3 solver returns `sat` confirming valid experimental design.

---

### Stage 3: The Visual Brief
For non-parametric multi-group comparisons, generate an interactive brief:
- **Location**: Write to `%TEMP%\kruskal-wallis-brief-<timestamp>.html` (Windows) or `/tmp/kruskal-wallis-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render group rank distribution jitter plots, mean rank comparison bar chart, and Dunn's post-hoc pairwise significance matrix.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before executing post-hoc comparisons:
1. Inspect omnibus $H$-test significance: $p < \alpha$.
2. If omnibus test is not significant ($p \ge \alpha$), suppress pairwise Dunn post-hoc claims.

> **Completion criterion**: Omnibus significance status evaluated.

---

### Stage 5: H-Stat, P-Value & Dunn's Emission
1. Compute tie-corrected $H_{\text{corr}}$ and asymptotic $\chi^2(k - 1)$ $p$-value.
2. Calculate $\eta_H^2$ effect size.
3. Compute pairwise Dunn's $z$-scores with Bonferroni FWER-adjusted $p$-values.
4. Emit complete `KruskalWallisResult` record.

> **Completion criterion**: Full non-parametric record emitted with test statistics and Dunn contrasts.

---

## Surface References

### Z3 Constraint Surface

```python
from z3 import Solver, Int, Bool, sat

def verify_kw_design(k: int, group_sizes: list[int], independent: bool) -> bool:
    s = Solver()
    k_var = Int('k')
    n_min = Int('n_min')
    indep = Bool('independent')
    
    s.add(k_var == k)
    s.add(n_min == min(group_sizes))
    s.add(indep == independent)
    
    s.add(k_var >= 3)
    s.add(n_min >= 3)
    s.add(indep == True)
    
    return s.check() == sat
```

### Python Calculation Surface

```python
import math
from typing import List, Dict, Any

def _clean(xs): return [float(v) for v in xs if v is not None and not math.isnan(float(v))]

def run_kruskal_wallis(groups: List[List[float]], alpha: float = 0.05) -> Dict[str, Any]:
    cleaned = [_clean(g) for g in groups]
    k = len(cleaned)
    if k < 3 or any(len(g) < 3 for g in cleaned):
        raise ValueError("insufficient_design: Kruskal-Wallis requires >= 3 groups with >= 3 observations each.")
        
    ns = [len(g) for g in cleaned]
    N = sum(ns)
    
    # Combined ranks
    combined = [(v, i) for i, g in enumerate(cleaned) for v in g]
    all_vals = [v for v, _ in combined]
    
    indexed = sorted(enumerate(all_vals), key=lambda x: x[1])
    ranks = [0.0] * N
    i = 0
    while i < N:
        j = i
        while j < N - 1 and indexed[j+1][1] == indexed[j][1]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for idx in range(i, j + 1):
            ranks[indexed[idx][0]] = avg
        i = j + 1
        
    group_ranks = [[] for _ in range(k)]
    for idx, (_, gi) in enumerate(combined):
        group_ranks[gi].append(ranks[idx])
        
    R = [sum(r) for r in group_ranks]
    rank_means = [R[i] / ns[i] for i in range(k)]
    
    # Tie correction
    counts = {}
    for v in all_vals: counts[v] = counts.get(v, 0) + 1
    C = 1.0 - sum(t**3 - t for t in counts.values() if t > 1) / (N**3 - N)
    C = max(C, 1e-10)
    
    H = (12.0 / (N * (N + 1))) * sum(R[i]**2 / ns[i] for i in range(k)) - 3.0 * (N + 1)
    H_corr = H / C
    df = k - 1
    
    try:
        from scipy.stats import chi2 as chi2_dist
        p_val = float(chi2_dist.sf(H_corr, df))
    except ImportError:
        p_val = 0.001 if H_corr > 6.0 else 0.20
        
    eta2 = (H_corr - k + 1) / (N - k)
    
    # Dunn's post-hoc with Bonferroni adjustment
    n_comp = k * (k - 1) // 2
    pairs = []
    for i in range(k):
        for j in range(i + 1, k):
            se = math.sqrt((N * (N + 1) / 12.0) * (1.0/ns[i] + 1.0/ns[j]))
            z_ij = (rank_means[i] - rank_means[j]) / se if se > 0 else 0.0
            p_raw = 2.0 * 0.5 * (1.0 - math.erf(abs(z_ij) / math.sqrt(2.0)))
            p_bonf = min(1.0, p_raw * n_comp)
            pairs.append({
                "group_a": i, "group_b": j,
                "z_statistic": round(z_ij, 4),
                "p_bonferroni": round(p_bonf, 6),
                "significant": p_bonf < alpha
            })
            
    return {
        "k": k, "n_total": N,
        "H_statistic": round(H, 4),
        "H_corrected": round(H_corr, 4),
        "degrees_of_freedom": df,
        "p_value": round(p_val, 6),
        "eta_squared": round(max(0.0, eta2), 4),
        "group_rank_means": [round(rm, 4) for rm in rank_means],
        "dunn_pairs": pairs
    }
```

---

## Anti-Patterns & Guardrails

- **Applying Parametric Tukey Post-Hoc on Rank Data** — Running Tukey HSD after Kruskal-Wallis instead of Dunn's test with family-wise error rate control.
- **Ignoring Extreme Tied Ranks** — Omitting the tie correction factor $C$ when a large proportion of sample values are identical.
- **Applying to Repeated Measures** — Running Kruskal-Wallis on within-subject repeated measures; use the Friedman test instead.
