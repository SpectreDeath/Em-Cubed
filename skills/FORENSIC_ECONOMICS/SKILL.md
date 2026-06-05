---
name: linear-regression
domain: MACHINE_LEARNING
version: "1.0.0"
surfaces: [python, sqlite]
---

# Purpose
Fit a linear model to predict continuous target values by minimizing squared residuals.

# Description
Core inputs: data points with features (list of lists) and targets (list of floats). Mechanical steps: compute feature means, calculate covariance between features and target, derive slope coefficients via normal equation, determine intercept. Expected outputs: coefficients tuple (slope list, intercept float), predicted values (list), R-squared value (float).

## Python Surface

```python
def linear_regression(features, targets):
    """
    Ordinary least squares linear regression.
    
    Args:
        features: List of feature vectors [[x1, x2, ...], ...]
        targets: List of target values [y1, y2, ...]
    
    Returns:
        tuple of (coefficients, predictions, r_squared) where:
        - coefficients: (slopes list, intercept float)
        - predictions: List of predicted values
        - r_squared: Coefficient of determination
    """
    n = len(features)
    if n == 0:
        return ([], [], 0.0)
    
    p = len(features[0])
    if p == 0:
        return ([], [], 0.0)
    
    feature_means = [0.0] * p
    target_mean = 0.0
    for i in range(n):
        target_mean = target_mean + targets[i]
        for j in range(p):
            feature_means[j] = feature_means[j] + features[i][j]
    
    target_mean = target_mean / n
    for j in range(p):
        feature_means[j] = feature_means[j] / n
    
    covariances = [0.0] * p
    variances = [[0.0] * p for _ in range(p)]
    
    for i in range(n):
        for j in range(p):
            covariances[j] = covariances[j] + (features[i][j] - feature_means[j]) * (targets[i] - target_mean)
        for j in range(p):
            for k in range(p):
                variances[j][k] = variances[j][k] + (features[i][j] - feature_means[j]) * (features[i][k] - feature_means[k])
    
    identity = [[1.0 if i == j else 0.0 for j in range(p)] for i in range(p)]
    for reg in range(10):
        for j in range(p):
            variances[j][j] = variances[j][j] + reg * 0.001
    
    for col in range(p):
        pivot = variances[col][col]
        if pivot < 1e-10:
            for j in range(p):
                if j != col and variances[j][col] != 0:
                    pivot = variances[j][col]
                    for k in range(p):
                        variances[col][k] = variances[j][k]
                    covariances[col] = covariances[j]
                    identity[col] = identity[j][:]
                    break
        for j in range(p):
            variances[col][j] = variances[col][j] / pivot
        covariances[col] = covariances[col] / pivot
        for i in range(p):
            if i != col:
                factor = variances[i][col]
                for j in range(p):
                    variances[i][j] = variances[i][j] - factor * variances[col][j]
                covariances[i] = covariances[i] - factor * covariances[col]
    
    slope = list(covariances)
    intercept = target_mean
    for j in range(p):
        intercept = intercept - feature_means[j] * slope[j]
    
    predictions = []
    ss_res = 0.0
    ss_tot = 0.0
    for i in range(n):
        pred = intercept
        for j in range(p):
            pred = pred + slope[j] * features[i][j]
        predictions.append(pred)
        ss_res = ss_res + (targets[i] - pred) ** 2
        ss_tot = ss_tot + (targets[i] - target_mean) ** 2
    
    r_sqr = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
    
    return (slope, intercept, predictions, r_sqr)
```

## SQLite Surface

```sql
-- Create k-means state table for iterative clustering
CREATE TABLE IF NOT EXISTS k_means_state (
    iteration INTEGER PRIMARY KEY,
    point_index INTEGER,
    cluster_id INTEGER,
    coord_x REAL,
    coord_y REAL,
    centroid_x REAL,
    centroid_y REAL
);

-- Query to assign point to nearest centroid
-- Parameters: ? = iteration, ? = point_x, ? = point_y
-- Returns: nearest cluster id and distance
SELECT cluster_id, MIN(distance) as min_dist
FROM (
    SELECT cluster_id, 
           SQRT((coord_x - ?) * (coord_x - ?) + (coord_y - ?) * (coord_y - ?)) as distance
    FROM (SELECT DISTINCT cluster_id, centroid_x as coord_x, centroid_y as coord_y 
          FROM k_means_state)
) WHERE min_dist IS NOT NULL;
```