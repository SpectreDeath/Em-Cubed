---
Domain: DECISION_MAKING
surfaces:
  - python
  - prolog
  - hy
  - cangjie
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

Multi-surface multi-criteria decision analysis (MCDA) tool that uses Python for weight calculation algorithms, Prolog for consistency checking in pairwise comparisons, and Hy for fuzzy AHP and dynamic weight adjustment.

## Description

This skill provides comprehensive MCDA capabilities:
- Python for Analytic Hierarchy Process (AHP), TOPSIS, and other weighting methods
- Prolog for consistency ratio calculation and logical preference validation
- Hy for fuzzy pairwise comparisons and uncertainty propagation

## Examples

### Vendor Selection

```
Input: 3 vendors evaluated on 4 criteria with pairwise comparisons
Output: Criteria weights and vendor rankings with consistency scores
```

## Implementation

### Python Weight Calculation

```python
from typing import Dict, List, Tuple, Optional
import numpy as np
from dataclasses import dataclass

@dataclass
class Criterion:
    name: str
    weight: float = 0.0
    description: str = ""

class AHPCalculator:
    """Analytic Hierarchy Process for multi-criteria weighting."""
    
    def __init__(self, criteria: List[str]):
        self.criteria = criteria
        self.n = len(criteria)
        self.comparison_matrix = np.ones((self.n, self.n))
    
    def set_comparison(self, i: int, j: int, value: float) -> None:
        """Set pairwise comparison value (i,j) where value = ai/aj."""
        self.comparison_matrix[i][j] = value
        self.comparison_matrix[j][i] = 1.0 / value
    
    def calculate_weights(self) -> np.ndarray:
        """Calculate criteria weights using eigenvalue method."""
        # Normalize columns
        normalized = self.comparison_matrix / self.comparison_matrix.sum(axis=0)
        
        # Calculate weights as row averages
        weights = normalized.mean(axis=1)
        
        # Normalize weights
        weights = weights / weights.sum()
        
        return weights
    
    def calculate_consistency_ratio(self) -> Tuple[float, float]:
        """Calculate consistency ratio (CR) for the comparison matrix."""
        weights = self.calculate_weights()
        
        # Calculate weighted sum vector
        weighted_sum = self.comparison_matrix @ weights
        
        # Calculate lambda_max (maximum eigenvalue approximation)
        ratios = weighted_sum / weights
        lambda_max = np.mean(ratios)
        
        # Consistency Index (CI)
        ci = (lambda_max - self.n) / (self.n - 1) if self.n > 1 else 0
        
        # Random Index (RI) lookup table
        ri_values = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 
                     6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
        ri = ri_values.get(self.n, 1.49)
        
        # Consistency Ratio (CR)
        cr = ci / ri if ri > 0 else 0
        
        return ci, cr
    
    def rank_alternatives(self, evaluations: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Rank alternatives based on criteria weights."""
        weights = self.calculate_weights()
        scores = {}
        
        for alt_name, criterion_scores in evaluations.items():
            score = sum(weights[i] * criterion_scores.get(crit, 0) 
                       for i, crit in enumerate(self.criteria))
            scores[alt_name] = score
        
        # Sort by score descending
        return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))


class TOPSISCalculator:
    """TOPSIS method for multi-criteria decision making."""
    
    def __init__(self, alternatives: List[str], criteria: List[str], 
                 weights: List[float], impacts: List[int]):  # impacts: +1 for benefit, -1 for cost
        self.alternatives = alternatives
        self.criteria = criteria
        self.weights = np.array(weights)
        self.impacts = np.array(impacts)
    
    def calculate(self, decision_matrix: np.ndarray) -> Dict[str, float]:
        """Calculate TOPSIS scores for alternatives."""
        # Normalize decision matrix
        normalized = decision_matrix / np.sqrt((decision_matrix ** 2).sum(axis=0))
        
        # Weighted normalized matrix
        weighted = normalized * self.weights
        
        # Determine ideal solutions
        ideal_best = np.max(weighted, axis=0) * self.impacts
        ideal_worst = np.min(weighted, axis=0) * self.impacts
        
        # Calculate separation measures
        dist_best = np.sqrt(((weighted - ideal_best) ** 2).sum(axis=1))
        dist_worst = np.sqrt(((weighted - ideal_worst) ** 2).sum(axis=1))
        
        # Calculate similarity to ideal solution
        topsis_scores = dist_worst / (dist_best + dist_worst)
        
        return {alt: score for alt, score in zip(self.alternatives, topsis_scores)}


def entropy_weights(decision_matrix: np.ndarray) -> np.ndarray:
    """Calculate weights using entropy method."""
    # Normalize each column
    normalized = decision_matrix / decision_matrix.sum(axis=0)
    
    # Calculate entropy
    epsilon = 1e-10
    entropy = -np.sum(normalized * np.log(normalized + epsilon), axis=0) / np.log(decision_matrix.shape[0])
    
    # Calculate weights
    weights = (1 - entropy) / (1 - entropy).sum()
    
    return weights


def hybrid_weighting(ahp_weights: np.ndarray, entropy_weights: np.ndarray, 
                     ahp_importance: float = 0.6) -> np.ndarray:
    """Combine AHP and entropy weights."""
    return ahp_importance * ahp_weights + (1 - ahp_importance) * entropy_weights
```

### Prolog Consistency Logic

```prolog
% AHP consistency rules
consistent_comparison(Value) :-
    number(Value),
    Value > 0,
    Value =< 9.

reciprocal(Value, Reciprocal) :-
    Reciprocal is 1 / Value.

% Check matrix consistency
matrix_consistent(Matrix, CR) :-
    consistency_ratio(Matrix, CI, CR),
    CR =< 0.1.  % Standard threshold

consistency_ratio(Matrix, CI, CR) :-
    eigenvalue_max(Matrix, Lambda_max),
    size(Matrix, N),
    CI is (Lambda_max - N) / (N - 1),
    random_index(N, RI),
    CR is CI / RI.

% Random index values for different matrix sizes
random_index(1, 0.0).
random_index(2, 0.0).
random_index(3, 0.58).
random_index(4, 0.90).
random_index(5, 1.12).
random_index(6, 1.24).
random_index(7, 1.32).
random_index(8, 1.41).
random_index(9, 1.45).

% Preference transitivity
transitive_preference(A, B, C) :-
    preference(A, B, Val1),
    preference(B, C, Val2),
    preference(A, C, Val3),
    Expected is Val1 * Val2,
    abs(Val3 - Expected) =< 0.1.  % Allow 10% deviation

% Dominance relationships
dominates(Option1, Option2, Criteria) :-
    forall(member(Criterion, Criteria),
           (score(Option1, Criterion, Score1),
            score(Option2, Criterion, Score2),
            Score1 >= Score2)).

% Pareto optimal check
pareto_optimal(Option, AllOptions) :-
    \+ (member(Other, AllOptions),
        dominates(Other, Option, _)).
```

### Hy Fuzzy AHP

```hy
(defn fuzzy-pairwise [crit1 crit2]
  "Create fuzzy comparison using triangular fuzzy numbers"
  (let [triangular-numbers {1 [1 1 1] 3 [2 3 4] 5 [4 5 6] 7 [6 7 8] 9 [8 9 9]}
        inverse {[1 9] [8 9 9] [2 3 4] [4 5 6] [4 6 8] [2 3 4] [6 8 9] [1 2 3]}
        get-fuzzy (fn [val] (get triangular-numbers val [val val val]))]
    {:criterion1 crit1 :criterion2 crit2 :fuzzy-value (get-fuzzy 1)}))

(defn defuzzify [fuzzy-triplet]
  "Convert triangular fuzzy to crisp using centroid method"
  (let [[a b c] fuzzy-triplet]
    (/ (+ a b c) 3)))

(defn fuzzy-geometric-mean [fuzzy-matrix]
  "Calculate fuzzy geometric mean for fuzzy AHP"
  (for [row fuzzy-matrix]
    (let [product (reduce * (map first row))
          root (pow product (/ 1 (len row)))]
      root)))

(defn fuzzy-consistency [fuzzy-matrix]
  "Calculate fuzzy consistency ratio"
  (let [weights (fuzzy-geometric-mean fuzzy-matrix)
        crisp-weights (map defuzzify weights)
        cr (calculate-consistency-ratio crisp-weights)]
    {:weights weights :cr cr :consistent (<= cr 0.1)}))

(defn dynamic-weight-update [current-weights performance feedback-factor]
  "Update weights based on performance feedback"
  (let [performance-adjustment (map (fn [perf] (* feedback-factor (- 1 perf))) performance)
        adjusted-weights (map + current-weights performance-adjustment)
        normalized (let [total (sum adjusted-weights)]
                     (map (fn [w] (/ w total)) adjusted-weights))]
    normalized))

(defn sensitivity-analysis [base-weights variation-range]
  "Analyze weight sensitivity to variations"
  (let [perturbations (for [i (range 100)]
                        (map (fn [w] (+ w (* variation-range (- (random) 0.5)))) base-weights))
        normalized-perts (map (fn [p] (let [t (sum p)] (map (fn [x] (/ x t)) p))) perturbations)
        std-dev (map (fn [i]
                      (let [values (map (fn [p] (get p i)) normalized-perts)]
                        (sqrt (/ (sum (map (fn [v] ** (- v (mean values)) 2)) values) (len values)))))
                    (range (len base-weights)))]
    {:std-deviations std-dev :most-sensitive (apply max std-dev :key (fn [i] (get std-dev i)))}))
```

## Testing

```python
# Test AHP calculator
import numpy as np
from skills.multi_criteria_weight_calculator import AHPCalculator

ahp = AHPCalculator(["Cost", "Quality", "Delivery"])

# Set pairwise comparisons (Cost vs Quality = 3, meaning Cost is 3x more important)
ahp.set_comparison(0, 1, 3)  # Cost vs Quality
ahp.set_comparison(0, 2, 2)  # Cost vs Delivery
ahp.set_comparison(1, 2, 1.5)  # Quality vs Delivery

weights = ahp.calculate_weights()
assert abs(weights.sum() - 1.0) < 0.01
assert all(w >= 0 for w in weights)

ci, cr = ahp.calculate_consistency_ratio()
assert cr < 0.1  # Should be consistent
```
### Cangjie Orchestrator

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
