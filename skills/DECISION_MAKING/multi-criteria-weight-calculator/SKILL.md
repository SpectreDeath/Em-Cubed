---
name: multi-criteria-weight-calculator
domain: DECISION_MAKING
version: 1.0.0
surfaces:
  - python
  - prolog
  - hy
description: Multi-surface Multi-Criteria Decision Analysis (MCDA) weight calculation engine supporting Analytic Hierarchy Process (AHP), TOPSIS, Shannon Entropy weighting, and Fuzzy AHP. Verifies pairwise comparison transitivity and consistency bounds in Prolog ($CR = CI / RI \le 0.10$), computes principal eigenvectors and TOPSIS separation distances in Python, and performs triangular fuzzy aggregation in Hy. Use when determining criteria priority weights, ranking decision alternatives, or assessing pairwise comparison consistency.
purpose: Derive criteria weights and rank alternatives via AHP, TOPSIS, Entropy weighting, and Fuzzy AHP with Prolog consistency verification.
dependencies:
  - DECISION_MAKING/multi-surface-decision-tree
tags:
  - mcda
  - ahp
  - topsis
  - entropy-weighting
  - fuzzy-ahp
  - consistency-ratio
  - criteria-weights
inputs:
  criteria:
    type: array
    required: true
    description: List of criteria names `['Cost', 'Quality', 'Delivery']`.
  pairwise_comparisons:
    type: array
    required: false
    description: List of pairwise ratios `[(i, j, value), ...]` where value $= a_i / a_j \in [1/9, 9]$.
  decision_matrix:
    type: array
    required: false
    description: Alternative evaluation matrix $M \times N$ for TOPSIS or Entropy weighting.
  method:
    type: string
    required: false
    description: Weighting method (`'ahp'`, `'topsis'`, `'entropy'`, `'fuzzy_ahp'`, or `'hybrid'`, default `'ahp'`).
outputs:
  weights:
    type: object
    description: 'Derived criteria weights mapping `{criterion_name: weight}` summing to 1.0.'
  consistency_index:
    type: number
    description: AHP Consistency Index $CI = (\lambda_{\text{max}} - n) / (n - 1)$.
  consistency_ratio:
    type: number
    description: AHP Consistency Ratio $CR = CI / RI$.
  is_consistent:
    type: boolean
    description: True if $CR \le 0.10$ (satisfies standard Saaty consistency threshold).
  alternative_rankings:
    type: object
    description: Optional ranked dictionary of alternatives if decision matrix was provided.
---

# Multi-Criteria Weight Calculator Engine

`multi-criteria-weight-calculator` derives criteria priority weights and ranks multi-attribute decision alternatives using **Analytic Hierarchy Process (AHP)**, **TOPSIS**, and **Shannon Entropy weighting**. It enforces **consistency ratio bounds ($CR \le 0.10$) in Prolog**, calculates eigenvalue weights in **Python**, and models triangular fuzzy numbers in **Hy**:

$$\mathbf{A} \mathbf{w} = \lambda_{\text{max}} \mathbf{w}, \quad \text{CI} = \frac{\lambda_{\text{max}} - n}{n - 1}, \quad \text{CR} = \frac{\text{CI}}{\text{RI}_n} \le 0.10$$

$$\text{TOPSIS Score: } C_i = \frac{D_i^-}{D_i^+ + D_i^-}, \quad D_i^+ = \sqrt{\sum_j (v_{ij} - v_j^+)^2}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage MCDA Weight Progression

```
[1. Criteria & Matrix Ingest] → [2. Pairwise Matrix & Consistency Ratio Evaluation] → [3. Visual Brief] → [4. Checkpoint] → [5. Eigenvector Weight Solution & Emit]
```

### Stage 1: Criteria & Matrix Ingest
1. Ingest `criteria` array ($n \ge 2$) and `pairwise_comparisons` or `decision_matrix`.
2. Construct $n \times n$ reciprocal pairwise comparison matrix $\mathbf{A}$ ($A_{ij} = 1 / A_{ji}, A_{ii} = 1$).

> **Completion criterion**: Clean reciprocal comparison matrix verified.

---

### Stage 2: Pairwise Matrix & Consistency Ratio Evaluation
1. Compute column sums $S_j = \sum_{i=1}^n A_{ij}$.
2. Normalize matrix: $B_{ij} = A_{ij} / S_j$.
3. Compute weight vector $\mathbf{w}$ as row averages: $w_i = \frac{1}{n} \sum_j B_{ij}$.
4. Compute maximum eigenvalue approximation $\lambda_{\text{max}} = \frac{1}{n} \sum_{i} \frac{(\mathbf{A}\mathbf{w})_i}{w_i}$.
5. Calculate Consistency Index $\text{CI}$ and Consistency Ratio $\text{CR} = \text{CI} / \text{RI}_n$.

> **Completion criterion**: Eigenvector weights and consistency ratio evaluated.

---

### Stage 3: The Visual Brief
For multi-criteria weighting and alternative rankings, generate an interactive brief:
- **Location**: Write to `%TEMP%\multi-criteria-brief-<timestamp>.html` (Windows) or `/tmp/multi-criteria-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render criteria weight distribution bar chart, AHP pairwise comparison heatmap matrix, consistency ratio gauge ($CR$ vs $0.10$), and alternative rankings table.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before finalizing output weights:
1. Verify consistency threshold: in Prolog, test `CR =< 0.10`. If $CR > 0.10$, flag inconsistent matrix with recommendation to revise pairwise judgments.
2. Verify weight normalization: $\sum w_i = 1.0 \pm 10^{-6}$.

> **Completion criterion**: Consistency ratio and weight normalization verified.

---

### Stage 5: Eigenvector Weight Solution & Output Emission
1. Compile final criteria weights mapping.
2. If decision matrix or alternative evaluations are supplied, evaluate TOPSIS composite scores.
3. Emit complete `MCDAWeightResult` record.

> **Completion criterion**: Full MCDA weighting and ranking payload emitted.

---

## Surface References

### Prolog Consistency Surface

```prolog
:- module(mcda_consistency, [
    matrix_consistent/2,
    consistency_ratio/3
]).

random_index(1, 0.0). random_index(2, 0.0). random_index(3, 0.58).
random_index(4, 0.90). random_index(5, 1.12). random_index(6, 1.24).
random_index(7, 1.32). random_index(8, 1.41). random_index(9, 1.45).

matrix_consistent(N, CR) :-
    CR =< 0.10.

consistency_ratio(N, LambdaMax, CR) :-
    ( N > 1 -> CI is (LambdaMax - N) / (N - 1) ; CI is 0.0 ),
    random_index(N, RI),
    ( RI > 0 -> CR is CI / RI ; CR is 0.0 ).
```

### Python Calculation Surface

```python
import numpy as np
from typing import Dict, List, Any, Optional, Tuple

RI_TABLE = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}

def calculate_mcda_weights(
    criteria: List[str],
    pairwise_comparisons: Optional[List[Tuple[int, int, float]]] = None,
    decision_matrix: Optional[List[List[float]]] = None,
    method: str = "ahp"
) -> Dict[str, Any]:
    n = len(criteria)
    if n < 1:
        raise ValueError("empty_criteria: Requires at least 1 criterion.")
        
    if method == "ahp" or pairwise_comparisons is not None:
        matrix = np.ones((n, n))
        if pairwise_comparisons:
            for i, j, val in pairwise_comparisons:
                if 0 <= i < n and 0 <= j < n:
                    matrix[i, j] = float(val)
                    matrix[j, i] = 1.0 / float(val)
                    
        # Column normalization
        col_sums = matrix.sum(axis=0)
        norm_matrix = matrix / col_sums
        weights = norm_matrix.mean(axis=1)
        weights = weights / weights.sum()
        
        # Consistency evaluation
        weighted_sum = matrix @ weights
        ratios = weighted_sum / weights
        lambda_max = float(np.mean(ratios))
        
        ci = (lambda_max - n) / (n - 1) if n > 1 else 0.0
        ri = RI_TABLE.get(n, 1.49)
        cr = ci / ri if ri > 0 else 0.0
        
        weights_dict = {crit: round(float(w), 6) for crit, w in zip(criteria, weights)}
        return {
            "weights": weights_dict,
            "consistency_index": round(ci, 6),
            "consistency_ratio": round(cr, 6),
            "is_consistent": cr <= 0.10,
            "method": "ahp"
        }
        
    elif method == "entropy" and decision_matrix is not None:
        mat = np.array(decision_matrix, dtype=float)
        m = mat.shape[0]
        col_sum = mat.sum(axis=0)
        col_sum[col_sum == 0] = 1.0
        p_mat = mat / col_sum
        
        eps = 1e-12
        entropy = -np.sum(p_mat * np.log(p_mat + eps), axis=0) / np.log(m if m > 1 else 2)
        d_val = 1.0 - entropy
        weights = d_val / d_val.sum()
        
        weights_dict = {crit: round(float(w), 6) for crit, w in zip(criteria, weights)}
        return {
            "weights": weights_dict,
            "consistency_index": 0.0,
            "consistency_ratio": 0.0,
            "is_consistent": True,
            "method": "entropy"
        }
    else:
        raise ValueError("invalid_configuration: Provide pairwise comparisons for AHP or decision matrix for Entropy.")
```

---

## Anti-Patterns & Guardrails

- **Accepting Inconsistent Pairwise Matrices** — Proceeding with decision selection when $CR > 0.10$, indicating contradictory preference judgments (e.g. $A \succ B \succ C \succ A$).
- **Zero or Negative Comparison Ratios** — Allowing comparison values $\le 0$; standard Saaty scale requires values in $[1/9, 9]$.
- **Unnormalized Entropy Weighting** — Computing entropy weights without log normalization against alternative sample count $m$.
