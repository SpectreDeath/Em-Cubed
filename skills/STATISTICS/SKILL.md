---
name: naive-bayes-classifier
domain: MACHINE_LEARNING
version: "1.0.0"
surfaces: [python, sqlite]
---

# Purpose
Classify instances using probabilistic generative modeling with feature independence assumptions.

# Description
Core inputs: feature matrix (list of vectors), class labels (list), feature types (categorical/continuous). Mechanical steps: compute class priors, estimate feature likelihoods per class using Gaussian or discrete distributions, apply Bayes rule with independence assumption, predict most probable class. Expected outputs: class probabilities (list of dicts), predicted labels (list), class prior dictionary.

## Python Surface

```python
def gaussian_pdf(x, mu, sigma):
    if sigma == 0:
        sigma = 1e-6
    coeff = 1.0 / (sigma * (2.0 * 3.14159265358979) ** 0.5)
    exp_val = -((x - mu) ** 2) / (2.0 * sigma * sigma)
    return coeff * my_exp(exp_val)

def my_exp(x):
    if x > 50:
        return 1e21
    if x < -30:
        result = 1.0
        term = 1.0
        for i in range(1, 100):
            term = term * (-x) / i
            result = result + term
            if term > 1e15:
                return 1e-20
            if term < 1e-15 * result:
                break
        return 1.0 / result
    if x < 0:
        result = 1.0
        term = 1.0
        for i in range(1, 50):
            term = term * (-x) / i
            result = result + term
        return 1.0 / result
    result = 1.0
    term = 1.0
    for i in range(1, 50):
        term = term * x / i
        result = result + term
        if term < 1e-15 * result and i > 10:
            break
    return result

def naive_bayes_train(features, labels):
    n = len(features)
    p = len(features[0])
    classes = list(set(labels))
    
    priors = {}
    for c in classes:
        priors[c] = labels.count(c) / n
    
    likelihoods = {}
    for c in classes:
        class_features = [features[i] for i in range(n) if labels[i] == c]
        if len(class_features) == 0:
            continue
        means = [0.0] * p
        variances = [0.0] * p
        for j in range(p):
            total = 0.0
            for i in range(len(class_features)):
                total = total + class_features[i][j]
            means[j] = total / len(class_features)
            var_total = 0.0
            for i in range(len(class_features)):
                var_total = var_total + (class_features[i][j] - means[j]) ** 2
            variances[j] = var_total / len(class_features) + 1e-6
        likelihoods[c] = (means, variances)
    
    return priors, likelihoods

def naive_bayes_predict(features, priors, likelihoods):
    predictions = []
    probs_list = []
    
    for feat in features:
        probs = {}
        best_class = None
        best_prob = -1.0
        
        for c in priors:
            log_prob = priors[c]
            means, variances = likelihoods[c]
            for j in range(len(feat)):
                log_prob = log_prob * gaussian_pdf(feat[j], means[j], variances[j] ** 0.5)
            probs[c] = log_prob
            if log_prob > best_prob:
                best_prob = log_prob
                best_class = c
        predictions.append(best_class)
        probs_list.append(probs)
    
    return predictions, probs_list

def naive_bayes(features, labels, test_features):
    priors, likelihoods = naive_bayes_train(features, labels)
    predictions, probs = naive_bayes_predict(test_features, priors, likelihoods)
    return (priors, likelihoods, predictions, probs)
```

## SQLite Surface

```sql
-- Naive Bayes model state table
CREATE TABLE IF NOT EXISTS naive_bayes_model (
    class_label TEXT PRIMARY KEY,
    prior_probability REAL,
    feature_index INTEGER,
    feature_mean REAL,
    feature_variance REAL
);

-- Insert class priors
-- Parameters: ? = class_label, ? = prior
INSERT INTO naive_bayes_model (class_label, prior_probability, feature_index)
VALUES (?, ?, -1);

-- Insert feature likelihoods
-- Parameters: ? = class_label, ? = feature_idx, ? = mean, ? = variance
INSERT INTO naive_bayes_model (class_label, prior_probability, feature_index, feature_mean, feature_variance)
VALUES (?, ?, ?, ?, ?);

-- Query predictions for classification
-- Returns class with highest posterior probability
SELECT class_label, prior_probability
FROM naive_bayes_model
WHERE class_label IS NOT NULL
ORDER BY prior_probability DESC
LIMIT 1;
```