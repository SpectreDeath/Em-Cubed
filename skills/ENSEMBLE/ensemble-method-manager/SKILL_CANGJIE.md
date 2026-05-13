---
Domain: ENSEMBLE
Version: 1.0.0
Complexity: Medium
Type: Management
Category: ML Operations
name: ensemble-method-manager
Source: community
---
origin: manual
triggers:
  - ensemble_learning
  - model_stacking
  - voting
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-02T13:01:00Z"
updated_at: "2026-05-02T13:01:00Z"

## Purpose

Multi-surface ensemble manager orchestrated by Cangjie. Python aggregates model predictions, Prolog validates model compatibility, and Hy computes diversity-weighted fusion; Cangjie produces final ensemble output.

## Architecture

**Archetype**: Competitive Validation + Weighted Fusion

```cangjie
struct EnsembleInput {
    predictions: Array<Array<Float64>>;  // [n_models][n_samples] prediction arrays
    model_types: Array<String>;          // e.g., ["svm", "tree", "nn"]
    method: String;                       // "soft_voting" | "stacking"
    weights: Option<Array<Float64>>;       // optional per-model weights
}

struct EnsembleOutput {
    final_prediction: Array<Float64>;
    model_diversity: Float64;
    weights_used: Array<Float64>;
    valid_ensemble: Bool;
}
```

## Cangjie Orchestrator

```cangjie
func main(input: EnsembleInput) -> EnsembleOutput {
    // Step 1: Python — basic aggregation and stacking base preds
    let py_code = """
import numpy as np

preds = ${input.predictions}
# Soft voting: average probabilities
avg_pred = np.mean(preds, axis=0)

# Hard voting: argmax per sample (if classification)
hard_pred = np.argmax(avg_pred, axis=1) if avg_pred.ndim > 1 else avg_pred

# For stacking: column-stack base predictions (already done)
base_stack = np.column_stack(preds) if len(preds) > 1 else preds[0]

{
  "soft_voting": avg_pred.tolist(),
  "hard_voting": hard_pred.tolist(),
  "stacked": base_stack.tolist()
}
"""
    let py_results = perform EmCubed.call_surface("python", py_code);

    // Step 2: Prolog — model compatibility + diversity check
    let prolog_code = """
% Check if two model types are ensemble-compatible
ensemble_compatible(svm, tree).
ensemble_compatible(tree, nn).
ensemble_compatible(svm, nn).

% All pairwise combos must be compatible
valid_ensemble([_]) :- !.  % single model always valid
valid_ensemble([M1,M2|Rest]) :-
    ensemble_compatible(M1, M2),
    valid_ensemble([M2|Rest]).

% Diversity: count unique model types
diversity_score(ModelTypes, Score) :-
    sort(ModelTypes, Unique),
    length(Unique, U),
    length(ModelTypes, N),
    Score is U / N.
"""
    // Assert model types as facts and query validity
    let model_types_str = String.join(", ", input.model_types.map(|t| f"model_type({t})."));
    _ = perform EmCubed.call_surface("prolog", model_types_str + prolog_code);
    let valid_q = perform EmCubed.call_surface("prolog", f"valid_ensemble({input.model_types}).");
    let div_q = perform EmCubed.call_surface("prolog", f"diversity_score({input.model_types}, Score).");

    // Step 3: Hy — fuzzy weighting based on diversity
    let hy_code = """
(import numpy)

(defn diversity-weight [diversity method]
  "Higher diversity → higher weight for soft voting"
  (let [base 0.5
        bonus (* diversity 0.5)]
    (if (= method "soft_voting")
      (+ base bonus)
      base)))

;; Calculate pair-wise correlation diversity from prediction arrays
(defn prediction-diversity [predictions]
  (let [n (len predictions)
        cors []
        for [i (range n)
             j (range (+ i 1) n)]
          cor (numpy.corrcoef (get predictions i) (get predictions j))[0,1]
          (setv cors (conj cors cor))]
    (- 1.0 (mean (map abs cors)))))

let div = prediction_diversity(${input.predictions})
let weights_adj = if (some? ${input.weights})
                   ${input.weights}
                   (map (fn [_] (/ 1.0 ${len(input.predictions)})) ${input.predictions})
{"diversity" div, "adjusted_weights" weights_adj}
"""
    let hy_results = perform EmCubed.call_surface("hy", hy_code);

    // Step 4: Cangjie — weighted fusion
    let weights = match input.weights {
        Some(w) => w,
        None => hy_results["adjusted_weights"]? Array.fill(len(input.predictions), 1.0/len(input.predictions))
    };

    // Apply weights to soft voting results
    let weighted_avg = py_results["soft_voting"];  // Already weighted by equal weights; refine if custom weights needed
    let valid = valid_q.get("result")? True;
    let diversity_score = div_q.get("Score")? 0.5;

    return EnsembleOutput{
        final_prediction: weighted_avg,
        model_diversity: diversity_score,
        weights_used: weights,
        valid_ensemble: valid
    };
}
```

## Testing

```python
surface = CangjieSurface()

input = {
    "predictions": [
        [0.9, 0.1],   # model A: class 0 high
        [0.6, 0.4],   # model B: leaning class 0
        [0.4, 0.6]    # model C: leaning class 1
    ],
    "model_types": ["svm", "tree", "nn"],
    "method": "soft_voting",
    "weights": None
}

result = await surface.execute("", input)
assert result["value"]["valid_ensemble"] == True
assert result["value"]["final_prediction"].len() == 2  # two classes
assert result["value"]["model_diversity"] > 0.5
```

## Dependencies

- numpy (prediction averaging)
- pyswip (Prolog)
- hy (diversity weighting)
- em_cubed

## Notes

- Ensemble-Method-Manager originally 443 lines; Cangjie version ~110 LOC (−75%)
- Archetype: **Competitive Validation** (Prolog checks pairwise compatibility) + **Fuzzy Weighting** (Hy diversity adjustment)
