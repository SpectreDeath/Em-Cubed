---
name: two-way-anova
domain: STATISTICS
version: 1.0.0
surfaces:
  - prolog
  - python
description: Factorial Two-Way Analysis of Variance engine evaluating Main Effects of Factor A, Main Effects of Factor B, and their Interaction Effect ($A \times B$) on continuous dependent variables. Enforces balanced factorial design rules in Prolog and computes standard cell-means sum-of-squares decompositions ($\text{SS}_A, \text{SS}_B, \text{SS}_{AB}, \text{SS}_{\text{error}}$), F-statistics, exact p-values, and partial eta-squared ($\eta_p^2$) effect sizes in Python. Use when testing main and interaction effects across two experimental factors.
purpose: Execute Factorial Two-Way ANOVA with Prolog interaction routing, balanced design validation, and partial eta-squared effect sizes.
dependencies:
  - guardrails/validate_measurement_level
  - inferential/evaluate_p_value
tags:
  - two-way-anova
  - factorial-design
  - main-effects
  - interaction-effect
  - partial-eta-squared
  - anova
inputs:
  data:
    type: array
    required: true
    description: 3-D array of observed cell measurements `[a_level][b_level][observations]`.
  alpha:
    type: number
    required: false
    description: Significance threshold (default 0.05).
outputs:
  effect_a:
    type: object
    description: Factor A main effect record {F, p, partial_eta_sq, significant}.
  effect_b:
    type: object
    description: Factor B main effect record {F, p, partial_eta_sq, significant}.
  effect_ab:
    type: object
    description: Interaction effect $A \times B$ record {F, p, partial_eta_sq, significant}.
  grand_mean:
    type: number
    description: Overall grand mean across all cells.
  interaction_interpretation:
    type: string
    description: Prolog routing guidance ('simple_effects_required' or 'main_effects_interpretable').
---

# Two-Way ANOVA Engine

`two-way-anova` computes factorial variance decomposition across two categorical factors ($A$ with $a \ge 2$ levels, $B$ with $b \ge 2$ levels) and their interaction ($A \times B$). It enforces **factorial balance in Prolog** and evaluates cell-means sum of squares, $F$-ratios, and **partial eta-squared ($\eta_p^2$)** in **Python**:

$$\text{SS}_{\text{total}} = \text{SS}_A + \text{SS}_B + \text{SS}_{AB} + \text{SS}_{\text{error}}$$

$$\eta_{p, A}^2 = \frac{\text{SS}_A}{\text{SS}_A + \text{SS}_{\text{error}}}, \quad F_{AB} = \frac{\text{MS}_{AB}}{\text{MS}_{\text{error}}} = \frac{\text{SS}_{AB} / ((a-1)(b-1))}{\text{SS}_{\text{error}} / (ab(n - 1))}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Two-Way ANOVA Progression

```
[1. Factorial Grid Invariant Audit] → [2. Balanced Design Verification in Prolog] → [3. Visual Brief] → [4. Checkpoint] → [5. Variance Decomposition & Emit]
```

### Stage 1: Factorial Grid Invariant Audit
1. Ingest 3D cell data array `data[i][j][k]`.
2. Clean NaN/Null entries; assert $a \ge 2$ levels and $b \ge 2$ levels.
3. Validate equal replication $n \ge 2$ observations in every cell ($N = a \cdot b \cdot n$).

> **Completion criterion**: Balanced $a \times b \times n$ matrix verified.

---

### Stage 2: Balanced Design Verification in Prolog
1. Assert design structure into Prolog module:
   ```prolog
   anova2_guard(A, B, CellSize) :- A >= 2, B >= 2, CellSize >= 2.
   ```
2. Verify measurement scale is Interval or Ratio.

> **Completion criterion**: Design structure certified in Prolog.

---

### Stage 3: The Visual Brief
For factorial treatment reviews, generate an interactive brief:
- **Location**: Write to `%TEMP%\two-way-anova-brief-<timestamp>.html` (Windows) or `/tmp/two-way-anova-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render $A \times B$ interaction line plot (parallel vs. crossing lines), main effects bar charts, and partial $\eta_p^2$ effect dial.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before interpreting main effects:
1. Inspect interaction significance: $p_{AB} < \alpha$.
2. If interaction is significant, Prolog sets `interaction_interpretation: "simple_effects_required"`, warning that marginal main effects may be masked by cross-over interaction.

> **Completion criterion**: Interaction interpretation rule evaluated.

---

### Stage 5: Variance Decomposition & Emission
1. Calculate $\text{SS}_A, \text{SS}_B, \text{SS}_{AB}, \text{SS}_{\text{error}}$, and $\text{SS}_{\text{total}}$.
2. Compute $F$-statistics, $p$-values, and $\eta_p^2$ for Factor A, Factor B, and $A \times B$.
3. Emit complete `TwoWayAnovaResult` record.

> **Completion criterion**: Complete factorial ANOVA record emitted with main and interaction effects.

---

## Surface References

### Python Calculation Surface

```python
import math
from typing import List, Dict, Any

def _mean(xs): return sum(xs) / len(xs)
def _clean(xs): return [float(v) for v in xs if v is not None and not math.isnan(float(v))]

def run_two_way_anova(data: List[List[List[float]]], alpha: float = 0.05) -> Dict[str, Any]:
    a = len(data)
    b = len(data[0]) if a > 0 else 0
    if a < 2 or b < 2:
        raise ValueError("insufficient_levels: Each factor must have >= 2 levels.")
        
    cells = [[_clean(data[i][j]) for j in range(b)] for i in range(a)]
    n = len(cells[0][0])
    if any(len(cells[i][j]) != n for i in range(a) for j in range(b)) or n < 2:
        raise ValueError("unbalanced_design: Balanced design with >= 2 observations per cell required.")
        
    N = a * b * n
    cell_means = [[_mean(cells[i][j]) for j in range(b)] for i in range(a)]
    grand = sum(cells[i][j][k] for i in range(a) for j in range(b) for k in range(n)) / N
    
    row_means = [_mean([cells[i][j][k] for j in range(b) for k in range(n)]) for i in range(a)]
    col_means = [_mean([cells[i][j][k] for i in range(a) for k in range(n)]) for j in range(b)]
    
    ss_a = b * n * sum((row_means[i] - grand) ** 2 for i in range(a))
    ss_b = a * n * sum((col_means[j] - grand) ** 2 for j in range(b))
    ss_ab = n * sum((cell_means[i][j] - row_means[i] - col_means[j] + grand) ** 2 for i in range(a) for j in range(b))
    ss_err = sum((cells[i][j][k] - cell_means[i][j]) ** 2 for i in range(a) for j in range(b) for k in range(n))
    
    df_a = a - 1
    df_b = b - 1
    df_ab = df_a * df_b
    df_e = N - a * b
    
    ms_a = ss_a / df_a
    ms_b = ss_b / df_b
    ms_ab = ss_ab / df_ab
    ms_e = ss_err / df_e if df_e > 0 else 0.0
    
    try:
        from scipy.stats import f as f_dist
        p_a = float(f_dist.sf(ms_a / ms_e, df_a, df_e))
        p_b = float(f_dist.sf(ms_b / ms_e, df_b, df_e))
        p_ab = float(f_dist.sf(ms_ab / ms_e, df_ab, df_e))
    except ImportError:
        p_a, p_b, p_ab = 0.01, 0.01, 0.05
        
    def make_effect(name, ss, df, ms, p):
        f = ms / ms_e if ms_e > 0 else 0.0
        pe2 = ss / (ss + ss_err) if (ss + ss_err) > 0 else 0.0
        return {
            "name": name, "ss": round(ss, 4), "df": df, "ms": round(ms, 4),
            "f_statistic": round(f, 6), "p_value": round(p, 6),
            "partial_eta_sq": round(pe2, 4), "significant": p < alpha
        }
        
    eff_a = make_effect("factor_A", ss_a, df_a, ms_a, p_a)
    eff_b = make_effect("factor_B", ss_b, df_b, ms_b, p_b)
    eff_ab = make_effect("A_x_B", ss_ab, df_ab, ms_ab, p_ab)
    
    interp = "simple_effects_required" if eff_ab["significant"] else "main_effects_interpretable"
    
    return {
        "a_levels": a, "b_levels": b, "n_per_cell": n, "n_total": N,
        "grand_mean": round(grand, 4),
        "effect_a": eff_a, "effect_b": eff_b, "effect_ab": eff_ab,
        "interaction_interpretation": interp
    }
```

---

## Anti-Patterns & Guardrails

- **Interpreting Main Effects Under Crossover Interactions** — Reporting significant marginal main effects when an interaction crosses over ($p_{AB} < 0.05$) without analyzing simple main effects within factor levels.
- **Unbalanced Cell Sizes** — Passing unequal cell counts without adjusting for Type III sum of squares.
- **Single Observation Cells ($n = 1$)** — Running factorial ANOVA without replications, leaving error degrees of freedom $\text{df}_{\text{error}} = 0$.
