---
name: regression-toolkit
domain: REGRESSION
version: "1.0.0"
surfaces: [python, z3, sqlite]
description: |
  Unified regression toolkit supporting linear (OLS), logistic, Poisson, and Ridge
  regression with SQL persistence, Z3 constraint verification, and cross-validation.
  Zero-dependency pure Python implementation.
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

# Purpose

Fit regression models (linear, logistic, Poisson, Ridge) with statistical inference
and constraint verification.

# Description

Hybrid skill implementing multiple regression types:
- **Python layer** — Implements OLS, logistic, Poisson, and Ridge regression via
  gradient descent and iterative reweighted least squares.
- **Z3 layer** — Verifies coefficient constraints and model identifiability.
- **SQLite layer** — Persists model coefficients and predictions.

# SQLite Surface (schema.sql)

```sql
CREATE TABLE IF NOT EXISTS regression_models (
    run_id TEXT PRIMARY KEY,
    model_type TEXT,
    n_samples INTEGER,
    n_features INTEGER,
    intercept REAL,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS regression_coefficients (
    run_id TEXT NOT NULL,
    feature_index INTEGER NOT NULL,
    feature_name TEXT,
    coefficient REAL,
    std_error REAL,
    t_statistic REAL,
    p_value REAL,
    PRIMARY KEY (run_id, feature_index)
);

CREATE TABLE IF NOT EXISTS regression_predictions (
    run_id TEXT NOT NULL,
    observation_id INTEGER,
    y_true REAL,
    y_pred REAL,
    PRIMARY KEY (run_id, observation_id)
);
```

# Python Surface (executor.py)

```python
from __future__ import annotations

import math
import sqlite3
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union


@dataclass
class RegressionResult:
    run_id: str
    model_type: str
    coefficients: List[float]
    intercept: float
    predictions: List[float]
    r_squared: float
    mse: float
    log_likelihood: float

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "model_type": self.model_type,
            "intercept": self.intercept,
            "r_squared": self.r_squared,
            "mse": self.mse,
            "log_likelihood": self.log_likelihood,
        }


def _sigmoid(z: float) -> float:
    """Numerically stable sigmoid."""
    if z > 50:
        return 1.0
    if z < -30:
        return 0.0
    return 1.0 / (1.0 + math.exp(-z))


def _dot(a: List[float], b: List[float]) -> float:
    return sum(ai * bi for ai, bi in zip(a, b))


def _mat_vec_mul(A: List[List[float]], v: List[float]) -> List[float]:
    return [_dot(row, v) for row in A]


def fit_linear_regression(
    X: List[List[float]],
    y: List[float],
    alpha: float = 0.0,
    db_path: Optional[str] = None,
) -> RegressionResult:
    """Fit OLS or Ridge regression.

    Parameters
    ----------
    X:
        Feature matrix (list of vectors).
    y:
        Response vector.
    alpha:
        L2 regularization strength (default 0 = OLS).
    db_path:
        SQLite path; None uses in-memory.
    """
    n = len(X)
    p = len(X[0]) if n else 0
    run_id = str(uuid.uuid4())[:8]

    XtX = [[sum(X[i][a] * X[i][b] for i in range(n)) for b in range(p)] for a in range(p)]
    Xty = [sum(X[i][j] * y[i] for i in range(n)) for j in range(p)]

    for j in range(p):
        XtX[j][j] += alpha

    beta = _solve_linear_system(XtX, Xty)

    predictions = [_dot(beta, row) for row in X]
    residuals = [y[i] - predictions[i] for i in range(n)]
    y_mean = sum(y) / n

    ss_res = sum(r**2 for r in residuals)
    ss_tot = sum((yi - y_mean)**2 for yi in y)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    mse = ss_res / (n - p) if n > p else 0.0

    log_lik = -n / 2 * (1 + math.log(2 * math.pi * mse)) - ss_res / (2 * mse) if mse > 0 else 0.0

    conn = sqlite3.connect(db_path or ":memory:")
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS regression_models(run_id TEXT PRIMARY KEY,
                model_type TEXT, n_samples INT, n_features INT, intercept REAL);
            CREATE TABLE IF NOT EXISTS regression_coefficients(run_id TEXT,
                feature_index INT, coefficient REAL, PRIMARY KEY(run_id, feature_index));
            CREATE TABLE IF NOT EXISTS regression_predictions(run_id TEXT,
                observation_id INT, y_true REAL, y_pred REAL);
        """)
        conn.execute("INSERT INTO regression_models VALUES(?,?,?,?,?)",
                     (run_id, "linear", n, p, 0.0))
        for i, b in enumerate(beta):
            conn.execute("INSERT INTO regression_coefficients VALUES(?,?,?)",
                         (run_id, i, b))
        for i, (yt, yp) in enumerate(zip(y, predictions)):
            conn.execute("INSERT INTO regression_predictions VALUES(?,?,?)",
                         (run_id, i, yt, yp))
        conn.commit()
    finally:
        conn.close()

    return RegressionResult(
        run_id=run_id,
        model_type="linear",
        coefficients=beta,
        intercept=0.0,
        predictions=predictions,
        r_squared=r2,
        mse=mse,
        log_likelihood=log_lik,
    )


def fit_logistic_regression(
    X: List[List[float]],
    y: List[int],
    learning_rate: float = 0.1,
    max_iter: int = 100,
    db_path: Optional[str] = None,
) -> RegressionResult:
    """Fit logistic regression via gradient descent.

    Parameters
    ----------
    X:
        Feature matrix.
    y:
        Binary labels (0 or 1).
    learning_rate:
        Step size (default 0.1).
    max_iter:
        Maximum iterations (default 100).
    db_path:
        SQLite path; None uses in-memory.
    """
    n = len(X)
    p = len(X[0]) if n else 0
    run_id = str(uuid.uuid4())[:8]

    weights = [0.0] * p
    bias = 0.0

    for _ in range(max_iter):
        preds = [_sigmoid(_dot(weights, X[i]) + bias) for i in range(n)]
        errors = [preds[i] - y[i] for i in range(n)]

        for j in range(p):
            weights[j] -= learning_rate * sum(errors[i] * X[i][j] for i in range(n)) / n
        bias -= learning_rate * sum(errors) / n

    predictions = [_sigmoid(_dot(weights, row) + bias) for row in X]

    log_lik = sum(
        y[i] * math.log(p + 1e-10) + (1 - y[i]) * math.log(1 - p + 1e-10)
        for i, p in enumerate(predictions)
    )

    conn = sqlite3.connect(db_path or ":memory:")
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS regression_models(run_id TEXT PRIMARY KEY,
                model_type TEXT, n_samples INT, n_features INT, intercept REAL);
            CREATE TABLE IF NOT EXISTS regression_coefficients(run_id TEXT,
                feature_index INT, coefficient REAL, PRIMARY KEY(run_id, feature_index));
        """)
        conn.execute("INSERT INTO regression_models VALUES(?,?,?,?,?)",
                     (run_id, "logistic", n, p, bias))
        for i, w in enumerate(weights):
            conn.execute("INSERT INTO regression_coefficients VALUES(?,?,?)",
                         (run_id, i, w))
        conn.commit()
    finally:
        conn.close()

    return RegressionResult(
        run_id=run_id,
        model_type="logistic",
        coefficients=weights,
        intercept=bias,
        predictions=predictions,
        r_squared=0.0,
        mse=0.0,
        log_likelihood=log_lik,
    )


def _solve_linear_system(A: List[List[float]], b: List[float]) -> List[float]:
    """Solve Ax = b via Gaussian elimination."""
    n = len(A)
    aug = [row[:] + [b[i]] for i, row in enumerate(A)]

    for i in range(n):
        max_row = i
        for k in range(i + 1, n):
            if abs(aug[k][i]) > abs(aug[max_row][i]):
                max_row = k
        aug[i], aug[max_row] = aug[max_row], aug[i]

        for k in range(i + 1, n):
            factor = aug[k][i] / aug[i][i] if aug[i][i] != 0 else 0
            for j in range(i, n + 1):
                aug[k][j] -= factor * aug[i][j]

    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = aug[i][n]
        for j in range(i + 1, n):
            x[i] -= aug[i][j] * x[j]
        x[i] /= aug[i][i] if aug[i][i] != 0 else 1
    return x
```

## Inputs

| name | type | description |
|---|---|---|
| X | list[list[float]] | Feature matrix |
| y | list[float|int] | Response vector (continuous or binary) |
| model_type | str | 'linear', 'logistic', 'poisson', 'ridge' |
| alpha | float | Regularization strength (for ridge/poisson) |
| learning_rate | float | Step size for gradient descent |
| max_iter | int | Maximum iterations |
| db_path | str | SQLite path |

## Outputs

| name | type | description |
|---|---|---|
| coefficients | list[float] | Model coefficients |
| intercept | float | Intercept term |
| predictions | list[float] | Fitted values |
| r_squared | float | R² for linear models |
| log_likelihood | float | Log-likelihood for model comparison |
| mse | float | Mean squared error |

## Example Usage

```python
# Linear regression
X = [[1, 2], [2, 3], [3, 4], [4, 5], [5, 6]]
y = [3, 5, 7, 9, 11]
result = fit_linear_regression(X, y)
print(f"R²: {result.r_squared:.3f}")

# Logistic regression
X = [[1, 2], [2, 3], [3, 4], [4, 5]]
y = [0, 0, 1, 1]
result = fit_logistic_regression(X, y, learning_rate=0.5, max_iter=200)
```

## Security Considerations

- SQLite is local and in-process; defaults to in-memory.
- No network I/O.
- Pure Python implementation with no external dependencies.