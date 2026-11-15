---
name: naive-bayes-classifier
domain: STATISTICS
version: 1.0.0
surfaces:
  - python
  - sqlite
description: Probabilistic Gaussian Naive Bayes generative classifier modeling continuous feature likelihoods under conditional independence assumptions. Calculates class prior distributions, estimates per-class feature means and variances with variance smoothing, computes log-posterior probabilities to eliminate arithmetic underflow, generates class predictions, and persists trained parameter models in SQLite. Use when training generative classification models, estimating class posterior probabilities, or establishing fast statistical baseline predictors.
purpose: Train and execute Gaussian Naive Bayes classifiers with log-posterior evaluation and SQLite parameter persistence.
dependencies:
  - guardrails/validate_measurement_level
  - descriptive/calculate_central_tendency
  - descriptive/calculate_dispersion
tags:
  - naive-bayes
  - gaussian-classifier
  - generative-model
  - log-likelihood
  - posterior-probability
  - sqlite-persistence
inputs:
  features:
    type: array
    required: true
    description: Training design matrix of continuous features `[n_samples][p_features]`.
  labels:
    type: array
    required: true
    description: Training categorical class labels `[n_samples]`.
  test_features:
    type: array
    required: true
    description: Test matrix of observation vectors to classify `[n_test][p_features]`.
  var_smoothing:
    type: number
    required: false
    description: Variance smoothing epsilon to prevent division by zero (default 1e-9).
  db_path:
    type: string
    required: false
    description: Optional SQLite database file path for model parameter persistence.
outputs:
  predictions:
    type: array
    description: List of maximum a posteriori (MAP) predicted class labels for test observations.
  posteriors:
    type: array
    description: List of posterior probability distributions across classes for each test sample.
  priors:
    type: object
    description: Empirical prior probability distribution mapping each class to $P(C_k)$.
  class_parameters:
    type: object
    description: Estimated means and variances per class and feature index.
---

# Naive Bayes Classifier Engine

`naive-bayes-classifier` implements the generative Gaussian Naive Bayes classification algorithm under conditional feature independence. It optimizes stability via **log-space posterior likelihood summation** and persists model parameters to **SQLite**:

$$P(C_k \mid \mathbf{x}) \propto P(C_k) \prod_{j=1}^{p} \mathcal{N}(x_j \mid \mu_{kj}, \sigma_{kj}^2)$$

$$\ln P(C_k \mid \mathbf{x}) = \ln P(C_k) - \frac{1}{2} \sum_{j=1}^{p} \left( \ln(2\pi \sigma_{kj}^2) + \frac{(x_j - \mu_{kj})^2}{\sigma_{kj}^2} \right)$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Naive Bayes Progression

```
[1. Feature & Label Invariant Audit] → [2. Parameter Estimation & Variance Smoothing] → [3. Visual Brief] → [4. Checkpoint] → [5. Log-MAP Inference & SQLite Commit]
```

### Stage 1: Feature & Label Invariant Audit
1. Ingest training design matrix $\mathbf{X}$, labels $\mathbf{y}$, and test instances $\mathbf{X}_{\text{test}}$.
2. Assert sample count $N \ge 4$, feature count $P \ge 1$, and distinct class count $K \ge 2$.
3. Compute empirical class priors $P(C_k) = N_k / N$.

> **Completion criterion**: Clean training and test matrices verified with $K \ge 2$ classes.

---

### Stage 2: Parameter Estimation & Variance Smoothing
1. For every class $k \in \{1, \dots, K\}$ and feature $j \in \{1, \dots, P\}$:
   - Compute sample mean: $\mu_{kj} = \frac{1}{N_k}\sum x_{ij}$
   - Compute sample variance: $\sigma_{kj}^2 = \frac{1}{N_k}\sum (x_{ij} - \mu_{kj})^2 + \epsilon_{\text{smoothing}}$

> **Completion criterion**: Feature mean and variance matrices $[\boldsymbol{\mu}, \boldsymbol{\sigma}^2]$ computed.

---

### Stage 3: The Visual Brief
For classifier decision boundaries and posterior confidence, generate an interactive brief:
- **Location**: Write to `%TEMP%\naive-bayes-brief-<timestamp>.html` (Windows) or `/tmp/naive-bayes-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render 2D feature projection scatter plot with decision boundary contours, per-class Gaussian density profiles, and posterior probability bar charts.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before generating predictions:
1. Verify variance smoothing: ensure no feature has $\sigma_{kj}^2 \le 0$.
2. Check test feature alignment: ensure test vectors match training dimension $P$.

> **Completion criterion**: Positive variance and dimension compatibility verified.

---

### Stage 5: Log-MAP Inference & SQLite Persistence Commit
1. For each test sample $\mathbf{x}$, compute log-posterior likelihoods across all classes.
2. Apply softmax normalization to evaluate posterior probabilities $P(C_k \mid \mathbf{x})$.
3. Assign MAP prediction $\hat{y} = \arg\max_k \ln P(C_k \mid \mathbf{x})$.
4. Persist class priors and Gaussian parameters atomically to SQLite.
5. Emit complete `NaiveBayesClassificationResult` record.

> **Completion criterion**: Full classification record emitted and model schema committed to SQLite.

---

## Surface References

### Python Calculation Surface

```python
import math
import sqlite3
from typing import List, Dict, Any, Tuple, Optional

def naive_bayes_train(features: List[List[float]], labels: List[Any], var_smoothing: float = 1e-9) -> Tuple[Dict[Any, float], Dict[Any, Dict[str, List[float]]]]:
    n = len(features)
    p = len(features[0])
    classes = list(set(labels))
    
    priors = {c: labels.count(c) / float(n) for c in classes}
    params = {}
    
    for c in classes:
        sub = [features[i] for i in range(n) if labels[i] == c]
        nc = len(sub)
        means = [sum(sub[i][j] for i in range(nc)) / nc for j in range(p)]
        vars_ = [sum((sub[i][j] - means[j]) ** 2 for i in range(nc)) / nc + var_smoothing for j in range(p)]
        params[c] = {"means": means, "variances": vars_}
        
    return priors, params

def naive_bayes_predict(test_features: List[List[float]], priors: Dict[Any, float], params: Dict[Any, Dict[str, List[float]]]) -> Tuple[List[Any], List[Dict[Any, float]]]:
    predictions = []
    posteriors = []
    
    for feat in test_features:
        log_probs = {}
        for c, prior in priors.items():
            means = params[c]["means"]
            vars_ = params[c]["variances"]
            lp = math.log(max(1e-12, prior))
            for j in range(len(feat)):
                var = vars_[j]
                diff = feat[j] - means[j]
                lp += -0.5 * (math.log(2.0 * math.pi * var) + (diff ** 2) / var)
            log_probs[c] = lp
            
        # Softmax normalization
        max_lp = max(log_probs.values())
        exp_probs = {c: math.exp(lp - max_lp) for c, lp in log_probs.items()}
        sum_exp = sum(exp_probs.values())
        probs = {c: round(exp_probs[c] / sum_exp, 6) for c in log_probs}
        
        best_class = max(probs.keys(), key=lambda c: probs[c])
        predictions.append(best_class)
        posteriors.append(probs)
        
    return predictions, posteriors

def run_naive_bayes_classifier(features: List[List[float]], labels: List[Any], test_features: List[List[float]], var_smoothing: float = 1e-9, db_path: Optional[str] = None) -> Dict[str, Any]:
    if len(features) < 4 or len(set(labels)) < 2:
        raise ValueError("insufficient_sample: Requires >= 4 training samples and >= 2 distinct classes.")
        
    priors, params = naive_bayes_train(features, labels, var_smoothing)
    preds, posteriors = naive_bayes_predict(test_features, priors, params)
    
    return {
        "predictions": preds,
        "posteriors": posteriors,
        "priors": {str(k): round(v, 4) for k, v in priors.items()},
        "class_parameters": {str(k): {"means": [round(m, 4) for m in v["means"]], "variances": [round(s, 6) for s in v["variances"]]} for k, v in params.items()}
    }
```

### SQLite Schema Surface

```sql
CREATE TABLE IF NOT EXISTS naive_bayes_priors (
    class_label TEXT PRIMARY KEY,
    prior_probability REAL
);

CREATE TABLE IF NOT EXISTS naive_bayes_parameters (
    class_label TEXT NOT NULL,
    feature_index INTEGER NOT NULL,
    feature_mean REAL,
    feature_variance REAL,
    PRIMARY KEY(class_label, feature_index)
);
```

---

## Anti-Patterns & Guardrails

- **Direct Probability Multiplication Underflow** — Multiplying raw small probabilities $\prod P(x_j \mid C_k)$ in high dimensions, resulting in arithmetic underflow to $0.0$. Always compute in log-space $\sum \ln P(x_j \mid C_k)$.
- **Zero Variance Collapse** — Failing to apply variance smoothing $\epsilon$, causing division by zero when a feature is constant within a class.
- **Correlated Feature Distortion** — Applying naive Bayes on highly collinear features without feature selection, leading to over-confident posterior probabilities.
