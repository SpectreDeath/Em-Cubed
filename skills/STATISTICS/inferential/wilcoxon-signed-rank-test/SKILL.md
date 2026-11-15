---
name: wilcoxon-signed-rank-test
domain: STATISTICS
version: 1.0.0
surfaces:
  - prolog
  - python
description: Non-parametric paired hypothesis testing engine (Wilcoxon Signed-Rank test) for comparing two matched/repeated sample measures or testing a single sample against a hypothesized median without assuming normality. Enforces paired design constraints in Prolog, drops zero-differences, ranks absolute differences with tie averaging, and computes W+/W- signed rank sums, continuity-corrected normal z-scores, and matched-pairs rank-biserial correlation effect sizes in Python. Use when analyzing repeated-measures experiments under non-normal distributions.
purpose: Execute Wilcoxon Signed-Rank test with zero-difference pruning, tie corrections, and matched-pairs rank-biserial effect size.
dependencies:
  - guardrails/validate_measurement_level
  - inferential/evaluate_p_value
tags:
  - wilcoxon-signed-rank
  - paired-test
  - non-parametric
  - matched-pairs
  - rank-biserial-correlation
inputs:
  group1:
    type: array
    required: true
    description: First paired sample vector (or single vector for one-sample median test).
  group2:
    type: array
    required: false
    description: Second paired sample vector (optional; if omitted, tests group1 against mu0).
  mu0:
    type: number
    required: false
    description: Hypothesized median benchmark for one-sample tests (default 0.0).
  alpha:
    type: number
    required: false
    description: Significance threshold (default 0.05).
outputs:
  W_plus:
    type: number
    description: Sum of positive signed ranks $W^+$.
  W_minus:
    type: number
    description: Sum of negative signed ranks $W^-$.
  z_statistic:
    type: number
    description: Continuity-corrected normal z-score approximation.
  p_value:
    type: number
    description: Two-tailed significance p-value.
  rank_biserial_r:
    type: number
    description: Matched-pairs rank-biserial correlation effect size.
  effect_label:
    type: string
    description: Qualitative effect label ('small', 'medium', 'large').
  n_effective:
    type: integer
    description: Effective sample pairs after dropping zero differences ($d_i = 0$).
---

# Wilcoxon Signed-Rank Test Engine

`wilcoxon-signed-rank-test` evaluates median differences in paired/repeated measurements or single-sample deviations from a hypothesized median $\mu_0$ without assuming Gaussian normality. It enforces **paired design gates in Prolog** and computes absolute difference ranks, tie corrections, and **matched-pairs rank-biserial correlation** in **Python**:

$$d_i = x_i - y_i \quad (\text{pruning } d_i = 0), \quad W^+ = \sum_{d_i > 0} \text{Rank}(|d_i|), \quad W^- = \sum_{d_i < 0} \text{Rank}(|d_i|)$$

$$z = \frac{\min(W^+, W^-) - \frac{n(n+1)}{4} + 0.5}{\sqrt{\frac{n(n+1)(2n+1)}{24} - \frac{\sum (t_i^3 - t_i)}{48}}}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Wilcoxon Signed-Rank Progression

```
[1. Paired Vector Audit & Zero Pruning] → [2. Absolute Difference Ranking] → [3. Visual Brief] → [4. Checkpoint] → [5. W-Stat, Z-Score & Effect Size Emit]
```

### Stage 1: Paired Vector Audit & Zero Pruning
1. Ingest paired vectors $g_1, g_2$ and verify equal length $n_{\text{pairs}} \ge 6$.
2. Compute paired differences $d_i = x_i - y_i$.
3. Prune zero differences ($d_i = 0$) and establish effective sample size $n_{\text{effective}}$.

> **Completion criterion**: Non-zero difference vector constructed with $n_{\text{effective}} \ge 1$.

---

### Stage 2: Absolute Difference Ranking & Tie Adjustment
1. Rank absolute differences $|d_i|$ with fractional tie-averaging.
2. Sum positive ranks ($W^+$) and negative ranks ($W^-$).
3. Compute tie variance correction term: $\sum (t_i^3 - t_i) / 48$.

> **Completion criterion**: Signed rank sums $W^+$ and $W^-$ computed with $W^+ + W^- = \frac{n(n+1)}{2}$.

---

### Stage 3: The Visual Brief
For repeated-measures treatment comparisons, generate an interactive brief:
- **Location**: Write to `%TEMP%\wilcoxon-signed-brief-<timestamp>.html` (Windows) or `/tmp/wilcoxon-signed-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render pre-vs-post slope-graphs, paired difference histogram, and rank-biserial effect gauge.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before calculating asymptotic z-scores:
1. Verify whether $n_{\text{effective}} \le 25$.
2. For small samples ($n \le 25$), flag recommendation for exact signed-rank distribution where available.

> **Completion criterion**: Sample size regime confirmed for asymptotic vs. exact calculation.

---

### Stage 5: W-Stat, Z-Score & Effect Size Emission
1. Compute continuity-corrected $z$-statistic and two-tailed $p$-value.
2. Evaluate matched-pairs rank-biserial correlation $r = \frac{W^+ - W^-}{W^+ + W^-}$.
3. Emit complete `WilcoxonResult` record.

> **Completion criterion**: Full statistical record emitted with test statistics and effect size.

---

## Surface References

### Python Calculation Surface

```python
import math
from typing import List, Dict, Any, Optional

def _clean(xs): return [float(v) for v in xs if v is not None and not math.isnan(float(v))]

def run_wilcoxon_signed_rank(group1: List[float], group2: Optional[List[float]] = None, mu0: float = 0.0, alpha: float = 0.05) -> Dict[str, Any]:
    g1 = _clean(group1)
    if group2 is not None:
        g2 = _clean(group2)
        if len(g1) != len(g2):
            raise ValueError("length_mismatch: Paired groups must have identical lengths.")
        diffs = [a - b for a, b in zip(g1, g2)]
    else:
        diffs = [x - mu0 for x in g1]
        
    n_pairs = len(diffs)
    if n_pairs < 6:
        raise ValueError("insufficient_sample: Wilcoxon requires at least 6 paired observations.")
        
    non_zero = [(d, i) for i, d in enumerate(diffs) if d != 0.0]
    n = len(non_zero)
    if n == 0:
        raise ValueError("all_zeros: All paired differences are exactly zero.")
        
    abs_diffs = [abs(d) for d, _ in non_zero]
    signs = [1.0 if d > 0 else -1.0 for d, _ in non_zero]
    
    # Fractional ranking
    indexed = sorted(enumerate(abs_diffs), key=lambda x: x[1])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n - 1 and indexed[j+1][1] == indexed[j][1]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = avg
        i = j + 1
        
    W_plus = sum(ranks[i] for i in range(n) if signs[i] > 0)
    W_minus = sum(ranks[i] for i in range(n) if signs[i] < 0)
    
    # Tie correction
    counts = {}
    for v in abs_diffs: counts[v] = counts.get(v, 0) + 1
    tie_corr = sum(t**3 - t for t in counts.values() if t > 1)
    
    # Asymptotic Z with continuity correction
    mu_w = n * (n + 1) / 4.0
    var_w = (n * (n + 1) * (2 * n + 1)) / 24.0 - tie_corr / 48.0
    T = min(W_plus, W_minus)
    z = (T - mu_w + 0.5) / math.sqrt(var_w) if var_w > 0 else 0.0
    
    p_val = 2.0 * 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
    p_val = min(1.0, max(0.0, p_val))
    
    total_ranks = n * (n + 1) / 2.0
    r_biserial = (W_plus - W_minus) / total_ranks if total_ranks > 0 else 0.0
    abs_r = abs(r_biserial)
    label = "small" if abs_r < 0.3 else ("medium" if abs_r < 0.5 else "large")
    
    return {
        "n_pairs": n_pairs,
        "n_effective": n,
        "W_plus": round(W_plus, 4),
        "W_minus": round(W_minus, 4),
        "z_statistic": round(z, 6),
        "p_value": round(p_val, 6),
        "rank_biserial_r": round(r_biserial, 4),
        "effect_label": label,
        "n_zeros": n_pairs - n
    }
```

---

## Anti-Patterns & Guardrails

- **Failing to Drop Zero Differences** — Retaining $d_i = 0$ in the rank calculations distorts both $W^+$ and $W^-$ sums.
- **Unmatched Vector Lengths** — Running paired signed-rank analysis on vectors of unequal length.
- **Micro-Sample Distortion** — Running test on fewer than 6 pairs where the minimum achievable p-value cannot reach significance.
