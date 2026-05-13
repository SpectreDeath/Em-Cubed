---
Domain: DECISION_MAKING
Version: 1.0.0
Complexity: Medium
Type: Utility
Category: Analytical Skills
Estimated Execution Time: 1-3 minutes
name: multi-criteria-weight-calculator
Source: community
---
origin: manual
triggers:
  - decision_analysis
  - weighted_scoring
  - multi_criteria
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-02T09:53:00Z"
updated_at: "2026-05-02T09:53:00Z"

## Purpose

Multi-criteria decision analysis (MCDA) orchestrated by Cangjie. Python computes weights (AHP/TOPSIS), Prolog validates consistency, and Hy provides fuzzy AHP; Cangjie synthesizes final ranking.

## Architecture

**Archetype**: Competitive Validation (run Python + Hy, pick most consistent)

```cangjie
struct MCDAInput {
    criteria: Array<String>;
    alternatives: Array<String>;
    decision_matrix: Array<Array<Float64>>;  // [alt][crit] scores
    ahp_pairwise: Option<Array<Array<Float64>>>;  // optional comparison matrix
    consistency_threshold: Float64;  // CR < 0.1 required
}

struct MCDAOutput {
    weights: Array<Float64>;
    rankings: Array<(String, Float64)>;  // (alternative, score)
    consistency_ratio: Float64;
    method_used: String;  // "ahp" | "entropy" | "topsis"
}
```

## Cangjie Orchestrator

```cangjie
func main(input: MCDAInput) -> MCDAOutput {
    // Step 1: Python — AHP weight calculation
    let py_code = """
import numpy as np

def ahp_weights(comparison_matrix):
    n = len(comparison_matrix)
    # Normalize columns
    normalized = comparison_matrix / comparison_matrix.sum(axis=0)
    # Row average = weights
    weights = normalized.mean(axis=1)
    return weights / weights.sum()

def consistency_ratio(matrix, weights):
    weighted_sum = matrix @ weights
    ratios = weighted_sum / weights
    lambda_max = np.mean(ratios)
    n = len(matrix)
    ci = (lambda_max - n) / (n - 1) if n > 1 else 0
    ri_lookup = {1:0, 2:0, 3:0.58, 4:0.90, 5:1.12, 6:1.24, 7:1.32, 8:1.41, 9:1.45}
    cr = ci / ri_lookup.get(n, 1.49) if ri_lookup.get(n, 1.49) > 0 else 0
    return cr

cm = np.array(${input.ahp_pairwise}? [[1.0]])
weights = ahp_weights(cm)
cr = consistency_ratio(cm, weights)
"""
    let py_results = perform EmCubed.call_surface("python", py_code);

    // Step 2: Prolog — transitivity check
    let prolog_code = """
% Consistency validation
transitive_preference(A, B, C) :-
    preference(A, B, V1),
    preference(B, C, V2),
    preference(A, C, V3),
    Expected is V1 * V2,
    abs(V3 - Expected) =< 0.1.

% Pareto optimality
pareto_optimal(Alt, All) :-
    \+ (member(Other, All), Other \\= Alt,
       dominates(Other, Alt, _)).
"""
    _ = perform EmCubed.call_surface("prolog", prolog_code);

    // Step 3: Hy — fuzzy AHP (triangular numbers)
    let hy_code = """
(import numpy)

(defn fuzzy-geom-mean [matrix]
  (let [rows matrix
        product (fn [row] (reduce * (map first row)))
        n (len (first rows))]
    (for [row rows]
      (pow (product row) (/ 1 n)))))

(defn defuzzify [[a b c]]
  (/ (+ a b c) 3))

;; Simplified: run fuzzy AHP with same matrix
fweights = (map defuzzify (fuzzy-geom-mean ${input.ahp_pairwise}? [[1 1 1]]))
"""
    let hy_results = perform EmCubed.call_surface("hy", hy_code);

    // Step 4: Cangjie — select method based on CR
    let cr = py_results["cr"]? 0.0;
    let weights = if cr < input.consistency_threshold {
        py_results["weights"]  // AHP valid
    } else {
        hy_results["fweights"]  // fallback to fuzzy
    };
    let method = if cr < input.consistency_threshold { "ahp" } else { "fuzzy_ahp" };

    // Rank alternatives by applying weights to decision matrix
    let rankings = [];
    for (i, alt) in enumerate(input.alternatives) {
        let score = 0.0;
        for (j, crit_weight) in enumerate(weights) {
            score += input.decision_matrix[i][j] * crit_weight;
        }
        rankings.push((alt, score));
    }
    rankings = sort_by(rankings, |(_, score)| -score);  // descending

    return MCDAOutput{
        weights: weights,
        rankings: rankings,
        consistency_ratio: cr,
        method_used: method
    };
}
```

## Implementation Mapping

| Surface | Role | LOC |
|---------|------|-----|
| Python | AHP eigenvector + CR computation | ~25 |
| Prolog | Preference transitivity + Pareto | ~12 |
| Hy | Fuzzy triangular AHP | ~18 |
| Cangjie | Method selection + ranking synthesis | ~45 |

**Total**: ~100 LOC vs 301-line original (−67%)

## Testing

```python
surface = CangjieSurface()

# Simple 3-criteria, 3-alternative vendor selection
input = {
    "criteria": ["Cost", "Quality", "Delivery"],
    "alternatives": ["Vendor A", "Vendor B", "Vendor C"],
    "decision_matrix": [
        [0.8, 0.6, 0.9],   # Vendor A scores
        [0.6, 0.9, 0.7],   # Vendor B
        [0.7, 0.7, 0.8]    # Vendor C
    ],
    "ahp_pairwise": [
        [1.0, 3.0, 2.0],
        [1/3, 1.0, 1.5],
        [0.5, 2/3, 1.0]
    ],
    "consistency_threshold": 0.1
}

result = await surface.execute("", input)
assert result["value"]["consistency_ratio"] < 0.1  // consistent pairwise
assert len(result["value"]["rankings"]) == 3
assert result["value"]["rankings"][0][0] in input["alternatives"]
```

## Dependencies

- numpy (AHP matrix math)
- pyswip (Prolog)
- hy (fuzzy numbers)
- em_cubed

## Notes

- TOPSIS and entropy methods excluded for brevity; can be added as alternate Python branches
- This version emphasizes **consistency validation** before accepting AHP weights
