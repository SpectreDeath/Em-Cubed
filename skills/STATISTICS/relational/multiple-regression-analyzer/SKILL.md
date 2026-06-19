---
name: multiple-regression-analyzer
domain: STATISTICS
version: "1.0.0"
surfaces: [sqlite, python]
description: |
  Multiple OLS linear regression for p >= 1 predictors. SQLite stores
  the design matrix, coefficient estimates, residuals, and model fit
  metrics for audit and downstream reporting. Python computes beta
  coefficients via normal equations, standard errors, t-statistics,
  p-values, R², adjusted R², F-test of overall fit, and VIF
  (Variance Inflation Factor) for multicollinearity detection.
  Extends the existing simple linear regression skill to the
  multivariate case.
compatibility: PYTHON, SQLITE
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

# Multiple Regression Analyzer

## Purpose
Fit multiple Ordinary Least Squares regression:

```
y = β₀ + β₁x₁ + β₂x₂ + ... + βₚxₚ + ε
```

Provides:
- Coefficient estimates (β), standard errors, t-statistics, p-values
- R² (coefficient of determination) and adjusted R²
- Overall model F-test
- VIF for each predictor (multicollinearity detection; VIF > 10 = high collinearity)
- Residuals and fitted values stored in SQLite

## Description
Hybrid skill:
- **SQLite layer** — Stores: design matrix (X, y), fitted coefficients, residuals, VIF table, and overall model metrics. Enables downstream residual analysis, prediction, and audit.
- **Python layer** — Implements normal equations (X'X)⁻¹X'y with Cholesky decomposition (no numpy). Computes full inference: MSE, coefficient SE, t-stats, p-values, R², adjusted R², F-stat.

## SQLite Surface (schema.sql)

```sql
-- multiple_regression.db schema

CREATE TABLE IF NOT EXISTS regression_observations (
    run_id  TEXT NOT NULL,
    obs_id  INTEGER NOT NULL,
    y_actual REAL,
    y_fitted REAL,
    residual REAL,
    PRIMARY KEY (run_id, obs_id)
);

CREATE TABLE IF NOT EXISTS regression_coefficients (
    run_id      TEXT NOT NULL,
    predictor   TEXT NOT NULL,
    beta        REAL,
    std_error   REAL,
    t_statistic REAL,
    p_value     REAL,
    vif         REAL,
    PRIMARY KEY (run_id, predictor)
);

CREATE TABLE IF NOT EXISTS regression_model_fit (
    run_id       TEXT PRIMARY KEY,
    n            INTEGER,
    p            INTEGER,
    r_squared    REAL,
    adj_r_squared REAL,
    f_statistic  REAL,
    f_p_value    REAL,
    mse          REAL,
    rmse         REAL,
    created_at   TEXT DEFAULT (datetime('now'))
);
```

## Python Surface (executor.py)

```python
"""
multiple-regression-analyzer
=============================
Multiple OLS regression via normal equations solved with
Cholesky decomposition. No numpy/scipy required.

Computes:
  beta    = (X'X)^-1 X'y
  residuals = y - X*beta
  MSE     = SS_res / (n - p - 1)
  SE_j    = sqrt(MSE * [(X'X)^-1]_jj)
  t_j     = beta_j / SE_j
  R²      = 1 - SS_res/SS_tot
  adj_R²  = 1 - (1-R²)*(n-1)/(n-p-1)
  F       = (R²/p) / ((1-R²)/(n-p-1))
  VIF_j   = 1 / (1 - R²_j)   where R²_j is from regressing x_j on all others
"""

from __future__ import annotations

import math
import sqlite3
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional, Union


@dataclass(frozen=True)
class CoefficientInfo:
    name: str
    beta: float
    std_error: float
    t_statistic: float
    p_value: float
    vif: float


@dataclass(frozen=True)
class MultipleRegressionResult:
    run_id: str
    n: int
    p: int
    intercept: float
    coefficients: List[CoefficientInfo]
    y_fitted: List[float]
    residuals: List[float]
    r_squared: float
    adj_r_squared: float
    f_statistic: float
    f_p_value: float
    mse: float
    rmse: float

    def to_dict(self) -> dict:
        return {
            "run_id":        self.run_id,
            "n":             self.n,
            "p":             self.p,
            "intercept":     self.intercept,
            "r_squared":     self.r_squared,
            "adj_r_squared": self.adj_r_squared,
            "f_statistic":   self.f_statistic,
            "f_p_value":     self.f_p_value,
            "mse":           self.mse,
            "rmse":          self.rmse,
            "coefficients":  [{
                "name":        c.name,
                "beta":        c.beta,
                "std_error":   c.std_error,
                "t_statistic": c.t_statistic,
                "p_value":     c.p_value,
                "vif":         c.vif,
            } for c in self.coefficients],
        }


# ---- Matrix utilities (pure Python, no numpy) -------------------------

def _mat_mul(A, B):
    """Matrix multiply A (m×n) by B (n×p) → m×p list-of-lists."""
    m, n = len(A), len(A[0])
    p = len(B[0])
    C = [[0.0]*p for _ in range(m)]
    for i in range(m):
        for k in range(n):
            if A[i][k] == 0.0: continue
            for j in range(p):
                C[i][j] += A[i][k] * B[k][j]
    return C


def _mat_T(A):
    return [[A[j][i] for j in range(len(A))] for i in range(len(A[0]))]


def _cholesky(A):
    """Cholesky decomposition of positive-definite symmetric matrix A → L."""
    n = len(A)
    L = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1):
            s = sum(L[i][k]*L[j][k] for k in range(j))
            if i == j:
                val = A[i][i] - s
                if val < 0: val = 1e-14
                L[i][j] = math.sqrt(val)
            else:
                L[i][j] = (A[i][j] - s) / L[j][j] if L[j][j] != 0 else 0.0
    return L


def _fwd_sub(L, b):
    """Forward substitution Lx = b."""
    n = len(b)
    x = [0.0]*n
    for i in range(n):
        x[i] = (b[i] - sum(L[i][j]*x[j] for j in range(i))) / L[i][i]
    return x


def _bwd_sub(L, b):
    """Backward substitution L'x = b."""
    n = len(b)
    x = [0.0]*n
    for i in range(n-1, -1, -1):
        x[i] = (b[i] - sum(L[j][i]*x[j] for j in range(i+1, n))) / L[i][i]
    return x


def _solve_normal(XtX, Xty):
    """Solve normal equations XtX * beta = Xty via Cholesky."""
    L = _cholesky(XtX)
    y1 = _fwd_sub(L, Xty)
    return _bwd_sub(L, y1)


def _invert_via_cholesky(A):
    """Compute A^-1 via Cholesky (A symmetric positive-definite)."""
    n = len(A)
    L = _cholesky(A)
    Ainv = []
    for j in range(n):
        e = [1.0 if i==j else 0.0 for i in range(n)]
        y = _fwd_sub(L, e)
        Ainv.append(_bwd_sub(L, y))
    return [[Ainv[j][i] for j in range(n)] for i in range(n)]


# ---- Statistical helpers -----------------------------------------------

def _mean(xs): return sum(xs)/len(xs)
def _clean(xs): return [float(v) for v in xs if v is not None and not math.isnan(float(v))]


def _t_pvalue(t, df):
    def betai(a,b,x):
        if x<=0:return 0.0
        if x>=1:return 1.0
        if x>(a+1)/(a+b+2):return 1-betai(b,a,1-x)
        lb=math.lgamma(a)+math.lgamma(b)-math.lgamma(a+b)
        front=math.exp(math.log(x)*a+math.log(1-x)*b-lb)/a
        cf=c=1.0;d=1-(a+b)*x/(a+1)
        if abs(d)<1e-30:d=1e-30
        d=1/d;cf=d
        for m in range(1,201):
            num=m*(b-m)*x/((a+2*m-1)*(a+2*m));d=1+num*d;c=1+num/c
            if abs(d)<1e-30:d=1e-30
            if abs(c)<1e-30:c=1e-30
            d=1/d;cf*=c*d
            num=-(a+m)*(a+b+m)*x/((a+2*m)*(a+2*m+1));d=1+num*d;c=1+num/c
            if abs(d)<1e-30:d=1e-30
            if abs(c)<1e-30:c=1e-30
            d=1/d;dlt=c*d;cf*=dlt
            if abs(dlt-1)<1e-10:break
        return front*cf
    return betai(df/2.0, 0.5, df/(df+t*t))


def _f_pvalue(f, df1, df2):
    def betai(a,b,x):
        if x<=0:return 0.0
        if x>=1:return 1.0
        if x>(a+1)/(a+b+2):return 1-betai(b,a,1-x)
        lb=math.lgamma(a)+math.lgamma(b)-math.lgamma(a+b)
        front=math.exp(math.log(x)*a+math.log(1-x)*b-lb)/a
        cf=c=1.0;d=1-(a+b)*x/(a+1)
        if abs(d)<1e-30:d=1e-30
        d=1/d;cf=d
        for m in range(1,201):
            num=m*(b-m)*x/((a+2*m-1)*(a+2*m));d=1+num*d;c=1+num/c
            if abs(d)<1e-30:d=1e-30
            if abs(c)<1e-30:c=1e-30
            d=1/d;cf*=c*d
            num=-(a+m)*(a+b+m)*x/((a+2*m)*(a+2*m+1));d=1+num*d;c=1+num/c
            if abs(d)<1e-30:d=1e-30
            if abs(c)<1e-30:c=1e-30
            d=1/d;dlt=c*d;cf*=dlt
            if abs(dlt-1)<1e-10:break
        return front*cf
    return betai(df2/2, df1/2, df2/(df2+df1*f))


# ---- Main function -------------------------------------------------------

def run_multiple_regression(
    X: List[List[Union[float, int, None]]],
    y: List[Union[float, int, None]],
    predictor_names: Optional[List[str]] = None,
    alpha: float = 0.05,
    db_path: Optional[str] = None,
) -> MultipleRegressionResult:
    """Fit multiple OLS regression y = beta_0 + X*beta + epsilon.

    Parameters
    ----------
    X:
        Design matrix [observations × predictors]. None/NaN rows dropped.
    y:
        Response vector. Matched by row index with X.
    predictor_names:
        Names for each column of X. Defaults to x1, x2, ...
    alpha:
        Significance level.
    db_path:
        SQLite path; None uses in-memory.
    """
    # Clean and align X and y
    n_raw = len(y)
    p_cols = len(X[0]) if X else 0
    rows = []
    for i in range(n_raw):
        yi = y[i]
        xi = X[i]
        if yi is None or math.isnan(float(yi)): continue
        if any(v is None or math.isnan(float(v)) for v in xi): continue
        rows.append(([float(v) for v in xi], float(yi)))

    n = len(rows)
    p = p_cols
    run_id = str(uuid.uuid4())[:8]

    if n < p + 2:
        raise ValueError(f"multiple_regression: need n >= p+2 ({p+2}), got {n}")

    names = predictor_names or [f"x{i+1}" for i in range(p)]

    X_raw = [row[0] for row in rows]
    y_raw = [row[1] for row in rows]

    # Build design matrix with intercept [1 | x1 | x2 | ...]
    Xm = [[1.0]+row for row in X_raw]      # n × (p+1)
    XtX = _mat_mul(_mat_T(Xm), Xm)        # (p+1)×(p+1)
    Xty = [sum(Xm[i][j]*y_raw[i] for i in range(n)) for j in range(p+1)]

    beta = _solve_normal(XtX, Xty)
    XtX_inv = _invert_via_cholesky(XtX)

    # Fitted values and residuals
    y_hat = [sum(beta[j]*Xm[i][j] for j in range(p+1)) for i in range(n)]
    resid = [y_raw[i]-y_hat[i] for i in range(n)]

    # SS
    y_mean  = _mean(y_raw)
    SS_res  = sum(r**2 for r in resid)
    SS_tot  = sum((yi-y_mean)**2 for yi in y_raw)
    SS_reg  = SS_tot - SS_res
    MSE     = SS_res/(n-p-1)
    R2      = 1-SS_res/SS_tot if SS_tot>0 else 0.0
    adjR2   = 1-(1-R2)*(n-1)/(n-p-1)
    F_stat  = (SS_reg/p)/MSE if p>0 and MSE>0 else 0.0
    F_p     = _f_pvalue(F_stat, p, n-p-1)

    # Coefficient inference
    coefs: List[CoefficientInfo] = []
    for j in range(p):
        se_j  = math.sqrt(MSE*XtX_inv[j+1][j+1]) if XtX_inv[j+1][j+1]>0 else 0.0
        t_j   = beta[j+1]/se_j if se_j>0 else 0.0
        p_j   = _t_pvalue(t_j, n-p-1)

        # VIF via auxiliary regression of x_j on all other x's
        if p > 1:
            others_idx = [k for k in range(p) if k != j]
            X_aux = [[X_raw[i][k] for k in others_idx] for i in range(n)]
            y_aux = [X_raw[i][j] for i in range(n)]
            Xm_aux = [[1.0]+row for row in X_aux]
            try:
                XtX_a = _mat_mul(_mat_T(Xm_aux), Xm_aux)
                Xty_a = [sum(Xm_aux[i][k]*y_aux[i] for i in range(n)) for k in range(len(Xm_aux[0]))]
                beta_a = _solve_normal(XtX_a, Xty_a)
                yhat_a = [sum(beta_a[k]*Xm_aux[i][k] for k in range(len(beta_a))) for i in range(n)]
                ya_mean = _mean(y_aux)
                ss_res_a = sum((y_aux[i]-yhat_a[i])**2 for i in range(n))
                ss_tot_a = sum((y_aux[i]-ya_mean)**2 for i in range(n))
                R2_j = 1-ss_res_a/ss_tot_a if ss_tot_a>0 else 0.0
                vif = 1/(1-R2_j) if R2_j<1 else float('inf')
            except Exception:
                vif = float('nan')
        else:
            vif = 1.0

        coefs.append(CoefficientInfo(
            name=names[j], beta=beta[j+1], std_error=se_j,
            t_statistic=t_j, p_value=min(1.0,max(0.0,p_j)), vif=vif,
        ))

    result = MultipleRegressionResult(
        run_id=run_id, n=n, p=p,
        intercept=beta[0],
        coefficients=coefs,
        y_fitted=y_hat, residuals=resid,
        r_squared=max(0.0,min(1.0,R2)),
        adj_r_squared=max(-1.0,min(1.0,adjR2)),
        f_statistic=F_stat, f_p_value=min(1.0,max(0.0,F_p)),
        mse=MSE, rmse=math.sqrt(max(0.0,MSE)),
    )

    # SQLite persistence
    conn = sqlite3.connect(db_path or ":memory:")
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS regression_observations(
                run_id TEXT, obs_id INT, y_actual REAL, y_fitted REAL, residual REAL,
                PRIMARY KEY(run_id,obs_id));
            CREATE TABLE IF NOT EXISTS regression_coefficients(
                run_id TEXT, predictor TEXT, beta REAL, std_error REAL,
                t_statistic REAL, p_value REAL, vif REAL,
                PRIMARY KEY(run_id,predictor));
            CREATE TABLE IF NOT EXISTS regression_model_fit(
                run_id TEXT PRIMARY KEY, n INT, p INT,
                r_squared REAL, adj_r_squared REAL,
                f_statistic REAL, f_p_value REAL, mse REAL, rmse REAL,
                created_at TEXT DEFAULT(datetime('now')));
        """)
        for i,(a,f,r) in enumerate(zip(y_raw,y_hat,resid)):
            conn.execute("INSERT OR REPLACE INTO regression_observations VALUES(?,?,?,?,?)",
                         (run_id,i,a,f,r))
        for c in coefs:
            conn.execute("INSERT OR REPLACE INTO regression_coefficients VALUES(?,?,?,?,?,?,?)",
                         (run_id,c.name,c.beta,c.std_error,c.t_statistic,c.p_value,c.vif))
        conn.execute("INSERT OR REPLACE INTO regression_model_fit VALUES(?,?,?,?,?,?,?,?,?)", (
            run_id,n,p,result.r_squared,result.adj_r_squared,
            result.f_statistic,result.f_p_value,result.mse,result.rmse,
        ))
        conn.commit()
    finally:
        conn.close()

    return result
```

## Inputs

| name | type | description |
|---|---|---|
| X | list[list[float\|int\|None]] | Design matrix [n_obs × p_predictors]. Rows with None dropped. |
| y | list[float\|int\|None] | Response vector (length n_obs) |
| predictor_names | list[str] \| None | Labels for each predictor column (default x1, x2, ...) |
| alpha | float | Significance level (default 0.05) |
| db_path | str \| None | SQLite path; None = in-memory |

## Outputs

| name | type | description |
|---|---|---|
| intercept | float | Intercept β₀ |
| coefficients | list[CoefficientInfo] | Per-predictor: β, SE, t, p-value, VIF |
| r_squared | float | Coefficient of determination R² |
| adj_r_squared | float | Adjusted R² |
| f_statistic | float | Overall model F-test |
| f_p_value | float | F-test p-value |
| mse | float | Mean Squared Error |
| rmse | float | Root Mean Squared Error |
| y_fitted | list[float] | Predicted values |
| residuals | list[float] | Residuals |

## VIF Interpretation
| VIF | Collinearity |
|---|---|
| 1.0 | None |
| 1–5 | Low |
| 5–10 | Moderate |
| > 10 | High — consider removing predictor |

## State Updates
```
state_add_observation("relational/regression_r2", result.r_squared)
state_add_observation("relational/regression_f_p", result.f_p_value)
state_add_observation("relational/regression_mse", result.mse)
state_add_observation("relational/regression_coefficients", [c.to_dict() for c in result.coefficients])
```

## Error Handling
| Error | Condition | Behavior |
|---|---|---|
| insufficient_observations | n < p+2 after cleaning | Raise ValueError |

## Example Usage
```python
# Predict house price from area and bedrooms
X = [[1200, 3], [1500, 4], [900, 2], [1800, 4], [1100, 3], [2000, 5]]
y = [250000, 320000, 190000, 380000, 230000, 420000]
r = run_multiple_regression(X, y, predictor_names=["area", "bedrooms"])
# r.r_squared        ≈ 0.99
# r.coefficients[0]: area beta ≈ 180, p < 0.05
# r.coefficients[1]: bedrooms beta ≈ 12000, p < 0.05
# VIF values         ≈ 1.x (low collinearity)
```

## Security Considerations
- SQLite is local and in-process; defaults to in-memory when db_path is None.
- No network I/O.
- Cholesky decomposition handles near-singular matrices by clamping to 1e-14.
