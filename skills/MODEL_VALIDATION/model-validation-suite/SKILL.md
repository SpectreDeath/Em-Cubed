---
name: model-validation-suite
domain: MODEL_VALIDATION
version: 1.0.0
surfaces:
  - python
  - prolog
  - hy
description: Multi-surface model validation suite combining Python for empirical error metrics (MSE, RMSE, MAE), bias-variance tradeoff decomposition, paired t-tests, and permutation significance tests; Prolog for declarative validation rules, data leakage detection, and CV score consistency checks; and Hy Lisp for fuzzy validation confidence scoring, distribution drift detection, and stability quotients. Use when conducting comprehensive model validation, auditing generalization integrity, or testing statistical superiority.
purpose: Validate statistical and ML models via error metrics, bias-variance decomposition, Prolog rules, and Hy fuzzy confidence.
dependencies: []
tags:
  - model-validation-suite
  - bias-variance
  - permutation-test
  - prolog-rules
  - hy-fuzzy-confidence
  - drift-detection
inputs:
  predictions:
    type: array
    required: true
    description: Model prediction vector of length $N$.
  actuals:
    type: array
    required: true
    description: Ground truth target vector of length $N$.
  cv_scores:
    type: array
    required: false
    description: Cross-validation scores across folds `[0.85, 0.87, 0.84, 0.86, 0.88]`.
  train_scores:
    type: array
    required: false
    description: Training fold performance scores for overfitting checks.
  alpha:
    type: number
    required: false
    description: Statistical significance threshold (default `0.05`).
outputs:
  metrics:
    type: object
    description: Empirical regression/classification error metrics (MSE, RMSE, MAE).
  bias_variance:
    type: object
    description: Bias-variance decomposition estimates (`bias_sq`, `variance`, `noise`).
  permutation_p_value:
    type: number
    description: Non-parametric permutation test significance p-value.
  overfitting_detected:
    type: boolean
    description: True if training performance significantly outpaces validation score.
  prolog_validation_status:
    type: string
    description: Declarative consistency verification status from Prolog.
  hy_fuzzy_confidence:
    type: number
    description: Fuzzy validation confidence quotient $[0, 1]$ synthesized in Hy.
---

# Model Validation Suite Engine

`model-validation-suite` performs multi-perspective model diagnostics. It combines **Python numerical metrics and bias-variance decomposition**, **Prolog declarative constraint validation**, and **Hy Lisp fuzzy confidence synthesis**:

$$\text{MSE} = \frac{1}{N}\sum (y_i - \hat{y}_i)^2, \quad \text{RMSE} = \sqrt{\text{MSE}}, \quad \text{MAE} = \frac{1}{N}\sum |y_i - \hat{y}_i|$$

$$\text{Expected Loss} = \text{Bias}^2 + \text{Variance} + \sigma_\epsilon^2$$

$$\text{Hy Fuzzy Confidence: } \mathcal{C} = \frac{\text{Score}_{\text{curr}} + \mu_{\text{hist}}}{2} \cdot \frac{1}{1 + \sigma_{\text{hist}}^2}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Model Validation Progression

```
[1. Prediction Ingest & Dimension Audit] → [2. Empirical Error & Bias-Variance Decomp] → [3. Visual Brief] → [4. Checkpoint] → [5. Prolog Rules, Hy Confidence & Emit]
```

### Stage 1: Prediction Ingest & Dimension Audit
1. Ingest `predictions` and `actuals` arrays.
2. Assert matching array lengths ($|\text{Pred}| = |\text{Actual}| = N \ge 2$).
3. Ingest optional `cv_scores` and `train_scores` arrays.

> **Completion criterion**: Equal-length evaluation arrays verified.

---

### Stage 2: Empirical Error & Bias-Variance Decomposition
1. Compute Mean Squared Error (MSE), Root Mean Squared Error (RMSE), and Mean Absolute Error (MAE).
2. Estimate bias-variance decomposition components: $\text{Bias}^2 = (\bar{\hat{y}} - \bar{y})^2$ and $\text{Var} = \text{Var}(\hat{y})$.
3. Run Monte Carlo permutation test to compute empirical $p$-value against chance predictions.

> **Completion criterion**: Empirical error and significance estimates computed.

---

### Stage 3: The Visual Brief
For model diagnostics and error residual distributions, generate an interactive brief:
- **Location**: Write to `%TEMP%\model-validation-brief-<timestamp>.html` (Windows) or `/tmp/model-validation-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render residual error distribution histogram, bias-variance tradeoff stacked bar chart, and Prolog validation badge.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before final confidence synthesis:
1. Verify CV score consistency in Prolog: $\sigma(\text{CV}) < 0.10 \cdot \mu(\text{CV})$.
2. Check overfitting gap: $(\mu(\text{Train}) - \mu(\text{Val})) > 0.10 \implies \text{overfitting: true}$.

> **Completion criterion**: Overfitting and CV consistency certified.

---

### Stage 5: Prolog Rules, Hy Confidence & Output Emission
1. Synthesize fuzzy validation confidence score in Hy Lisp.
2. Format complete `ModelValidationResult` dictionary.
3. Emit structured validation payload.

> **Completion criterion**: Full validation suite payload emitted.

---

## Surface References

### Prolog Consistency Surface

```prolog
:- module(model_validation, [
    valid_model/2,
    consistent_cv_scores/2,
    overfitting_check/3
]).

consistent_cv_scores(Scores, Tolerance) :-
    sum_list(Scores, Sum),
    length(Scores, N),
    Mean is Sum / N,
    std_dev(Scores, Mean, Std),
    Std < (Tolerance * Mean).

overfitting_check(TrainMean, ValMean, Threshold) :-
    Gap is TrainMean - ValMean,
    Gap > Threshold.
```

### Hy Fuzzy Confidence Surface

```hy
(defn validation-confidence [current-score historical-scores]
  "Synthesize fuzzy validation confidence quotient in Hy."
  (let [hist-mean (/ (sum historical-scores) (len historical-scores))
        variance (/ (sum (list-comp (** (- x hist-mean) 2) [x historical-scores])) (len historical-scores))
        consistency (/ (+ current-score hist-mean) 2)
        uncertainty (/ 1 (+ 1 variance))]
    (round (* consistency uncertainty) 4)))
```

### Python Validation Engine

```python
import math
import random
from typing import Dict, List, Any, Optional

def validate_model_performance(
    predictions: List[float],
    actuals: List[float],
    cv_scores: Optional[List[float]] = None,
    train_scores: Optional[List[float]] = None,
    alpha: float = 0.05
) -> Dict[str, Any]:
    n = len(predictions)
    if n != len(actuals) or n < 2:
        raise ValueError("dimension_mismatch: predictions and actuals must have equal length >= 2.")
        
    # 1. Error Metrics
    mse = sum((p - a) ** 2 for p, a in zip(predictions, actuals)) / n
    rmse = math.sqrt(mse)
    mae = sum(abs(p - a) for p, a in zip(predictions, actuals)) / n
    
    # 2. Bias-Variance Decomposition
    mean_p = sum(predictions) / n
    mean_a = sum(actuals) / n
    bias_sq = (mean_p - mean_a) ** 2
    var_p = sum((p - mean_p) ** 2 for p in predictions) / n
    noise = max(0.0, mse - bias_sq - var_p)
    
    # 3. Permutation Test
    observed = mse
    k_perm = 200
    count = 0
    shuffled = list(predictions)
    for _ in range(k_perm):
        random.shuffle(shuffled)
        perm_mse = sum((p - a) ** 2 for p, a in zip(shuffled, actuals)) / n
        if perm_mse <= observed:
            count += 1
    perm_p = count / k_perm
    
    # 4. Overfitting & CV Consistency
    overfitting = False
    if train_scores and cv_scores:
        t_mean = sum(train_scores) / len(train_scores)
        v_mean = sum(cv_scores) / len(cv_scores)
        overfitting = (t_mean - v_mean) > 0.10
        
    prolog_status = "consistent"
    if cv_scores and len(cv_scores) > 1:
        cv_mean = sum(cv_scores) / len(cv_scores)
        cv_std = math.sqrt(sum((s - cv_mean)**2 for s in cv_scores) / (len(cv_scores) - 1))
        if cv_std > 0.15 * cv_mean:
            prolog_status = "high_variance"
            
    # 5. Hy Fuzzy Confidence
    hist = cv_scores if cv_scores else [1.0 - min(1.0, rmse)]
    hist_mean = sum(hist) / len(hist)
    var_h = sum((x - hist_mean)**2 for x in hist) / len(hist) if len(hist) > 1 else 0.01
    curr_score = max(0.0, 1.0 - min(1.0, rmse))
    hy_conf = round(((curr_score + hist_mean) / 2.0) * (1.0 / (1.0 + var_h)), 4)
    
    return {
        "metrics": {"mse": round(mse, 4), "rmse": round(rmse, 4), "mae": round(mae, 4)},
        "bias_variance": {"bias_sq": round(bias_sq, 4), "variance": round(var_p, 4), "noise": round(noise, 4)},
        "permutation_p_value": round(perm_p, 4),
        "overfitting_detected": overfitting,
        "prolog_validation_status": prolog_status,
        "hy_fuzzy_confidence": hy_conf
    }
```

---

## Anti-Patterns & Guardrails

- **Conflating Total Error with Bias Squared** — Calculating sample-level squared residuals as pure bias without separating variance from sample predictions.
- **Ignoring Data Distribution Drift** — Validating models solely on in-sample metrics without monitoring temporal shifts between baseline reference sets and validation streams.
- **Overlooking Permutation Insignificance** — Accepting high accuracy models that fail non-parametric permutation tests against random label shuffling.
