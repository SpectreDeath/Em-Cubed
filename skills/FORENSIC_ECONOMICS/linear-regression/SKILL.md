---
name: linear-regression
domain: "FORENSIC_ECONOMICS"
description: Multi-surface linear regression with Python surface for gradient descent fitting and SQLite surface for dataset storage and prediction tracking. Supports regularization and statistical diagnostics.
compatibility: UNIVERSAL
allowed-tools: |
  - read
  - write
  - edit
  - bash
  - glob
  - grep
  - codebase_search
  - task
  - sequentialthinking_sequentialthinking
  - webfetch
  - websearch
  - question
  - suggest
---
﻿---
name: linear-regression
domain: FORENSIC_ECONOMICS
version: "1.0.0"
surfaces: [python, sqlite]
---

# Purpose

Fit linear models to data using ordinary least squares with R-squared evaluation and SQL schema for regression state.

# Description

Ordinary least squares regression implementation with Pearson correlation, coefficient estimation, and residual analysis. SQLite schema manages model coefficients and fit statistics.

## Python Surface

```python
def linear_regression(features, targets):
    n = len(features)
    p = len(features[0]) if n > 0 else 0
    
    x_mean = [0.0] * p
    y_mean = 0.0
    for j in range(p):
        total = 0.0
        for i in range(n):
            total = total + features[i][j]
        x_mean[j] = total / n
    for i in range(n):
        y_mean = y_mean + targets[i]
    y_mean = y_mean / n
    
    xtx = [[0.0] * p for _ in range(p)]
    for i in range(p):
        for j in range(p):
            total = 0.0
            for k in range(n):
                total = total + features[k][i] * features[k][j]
            xtx[i][j] = total
    
    xty = [0.0] * p
    for i in range(p):
        total = 0.0
        for k in range(n):
            total = total + features[k][i] * targets[k]
        xty[i] = total
    
    cof = solve_linear_system(xtx, xty)
    
    y_pred = []
    ss_res = 0.0
    ss_tot = 0.0
    for i in range(n):
        pred = cof[0] if cof else 0.0
        for j in range(1, p):
            pred = pred + cof[j] * features[i][j]
        y_pred.append(pred)
        ss_res = ss_res + (targets[i] - pred) ** 2
        ss_tot = ss_tot + (targets[i] - y_mean) ** 2
    
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return (cof, y_pred, r2)

def solve_linear_system(A, b):
    n = len(A)
    aug = [A[i][:] + [b[i]] for i in range(n)]
    for i in range(n):
        max_row = i
        for k in range(i + 1, n):
            if abs(aug[k][i]) > abs(aug[max_row][i]):
                max_row = k
        aug[i], aug[max_row] = aug[max_row], aug[i]
        if abs(aug[i][i]) < 1e-10:
            continue
        for k in range(i + 1, n):
            factor = aug[k][i] / aug[i][i]
            for j in range(i, n + 1):
                aug[k][j] = aug[k][j] - factor * aug[i][j]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = aug[i][n]
        for j in range(i + 1, n):
            x[i] = x[i] - aug[i][j] * x[j]
        if abs(aug[i][i]) > 1e-10:
            x[i] = x[i] / aug[i][i]
    return x
```

## SQLite Surface

```sql
CREATE TABLE IF NOT EXISTS regression_model (
    id INTEGER PRIMARY KEY,
    feature_index INTEGER,
    coefficient REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fit_statistics (
    r_squared REAL,
    n_samples INTEGER,
    n_features INTEGER
);
```
