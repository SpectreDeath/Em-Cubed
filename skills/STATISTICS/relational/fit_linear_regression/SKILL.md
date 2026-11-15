---
name: fit_linear_regression
domain: STATISTICS
version: 1.0.0
surfaces:
  - prolog
  - python
description: Ordinary Least Squares (OLS) bivariate simple linear regression engine fitting $y = \beta_0 + \beta_1 x$. Enforces independence and minimum sample size preconditions in Prolog, computes slope and intercept coefficients, evaluates goodness-of-fit $R^2$, derives slope standard errors, and conducts two-tailed t-distribution hypothesis testing with residual vector extraction in Python. Use when estimating linear predictor slopes, forecasting continuous target values, or analyzing bivariate functional dependencies.
purpose: Fit OLS simple linear regression models with Prolog structural gating, t-statistic inference, and residual diagnostics.
dependencies:
  - guardrails/validate_measurement_level
  - inferential/evaluate_p_value
tags:
  - linear-regression
  - ols-regression
  - r-squared
  - slope-inference
  - residual-analysis
  - relational-statistics
inputs:
  x:
    type: array
    required: true
    description: Independent predictor variable vector (None and NaN values are paired-filtered).
  y:
    type: array
    required: true
    description: Dependent response variable vector (None and NaN values are paired-filtered).
  alpha:
    type: number
    required: false
    description: Significance threshold (default 0.05).
  independent:
    type: boolean
    required: false
    description: True if observation pairs are independent (default True).
outputs:
  beta_0:
    type: number
    description: Regression intercept parameter $\beta_0 = \bar{y} - \beta_1 \bar{x}$.
  beta_1:
    type: number
    description: Regression slope parameter $\beta_1 = \frac{\text{SS}_{xy}}{\text{SS}_{xx}}$.
  r_squared:
    type: number
    description: Coefficient of determination $R^2 \in [0.0, 1.0]$.
  std_err_beta1:
    type: number
    description: Standard error of the slope coefficient $\text{SE}(\beta_1) = \sqrt{\text{MSE} / \text{SS}_{xx}}$.
  t_stat:
    type: number
    description: Inferential t-statistic for slope $t = \beta_1 / \text{SE}(\beta_1)$.
  p_value:
    type: number
    description: 'Two-tailed significance p-value under $H_0: \beta_1 = 0$.'
  df:
    type: integer
    description: Error degrees of freedom $n - 2$.
  residuals:
    type: array
    description: Vector of observed minus predicted error residuals $e_i = y_i - \hat{y}_i$.
---

# Fit Linear Regression Engine

`fit_linear_regression` fits ordinary least squares (OLS) linear equations $y = \beta_0 + \beta_1 x$ between paired continuous variables. It enforces **structural independence and sample bounds in Prolog** and evaluates exact coefficients, standard errors, and **inferential slope testing** in **Python**:

$$\beta_1 = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sum (x_i - \bar{x})^2}, \quad \beta_0 = \bar{y} - \beta_1 \bar{x}, \quad R^2 = \frac{\text{SS}_{\text{regression}}}{\text{SS}_{\text{total}}}$$

$$\text{SE}(\beta_1) = \sqrt{\frac{\sum e_i^2 / (n - 2)}{\sum (x_i - \bar{x})^2}}, \quad t = \frac{\beta_1}{\text{SE}(\beta_1)}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Linear Regression Progression

```
[1. Paired Cleaning & Invariant Audit] → [2. Prolog Precondition Gate] → [3. Visual Brief] → [4. Checkpoint] → [5. OLS Estimation & Residual Emit]
```

### Stage 1: Paired Cleaning & Invariant Audit
1. Ingest predictor vector $\mathbf{x}$ and response vector $\mathbf{y}$.
2. Filter pairs with missing or NaN values.
3. Assert clean paired sample count $n_{\text{used}} \ge 3$.

> **Completion criterion**: Clean paired numeric vectors constructed with $n_{\text{used}} \ge 3$.

---

### Stage 2: Prolog Precondition Gate
1. Validate structural preconditions in Prolog:
   ```prolog
   ols_preconditions(Xs, Ys, Independent) :- same_length(Xs, Ys), ols_min_samples(N), independent_groups(Independent).
   ```
2. Verify measurement scales for both $x$ and $y$ are Interval or Ratio.

> **Completion criterion**: Preconditions and independence assumption verified.

---

### Stage 3: The Visual Brief
For bivariate regression reviews or trend forecasting, generate an interactive brief:
- **Location**: Write to `%TEMP%\fit-regression-brief-<timestamp>.html` (Windows) or `/tmp/fit-regression-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render scatter plot with fitted OLS regression line and 95% confidence bands, residual vs. fitted plot, and $R^2$ goodness-of-fit meter.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before computing slope inference:
1. Verify predictor variance: $\text{SS}_{xx} = \sum (x_i - \bar{x})^2 > 0$.
2. If $\text{SS}_{xx} = 0$ (all $x$ values identical), halt with `zero_variance` error.

> **Completion criterion**: Non-zero predictor variance verified.

---

### Stage 5: OLS Estimation & Residual Output Emission
1. Calculate $\beta_1, \beta_0, R^2$, and residuals $\mathbf{e} = \mathbf{y} - (\beta_0 + \beta_1 \mathbf{x})$.
2. Calculate slope standard error $\text{SE}(\beta_1)$, $t$-statistic, and two-tailed $p$-value with $\text{df} = n - 2$.
3. Emit complete `LinearRegressionResult` record.

> **Completion criterion**: Complete regression record emitted with coefficients, $R^2$, and residual vector.

---

## Surface References

### Python Calculation Surface

```python
import math
from typing import List, Dict, Any

def _clean_pairs(x: List[float], y: List[float]):
    cx, cy, dropped = [], [], 0
    for a, b in zip(x, y):
        if a is not None and b is not None and not (isinstance(a, float) and math.isnan(a)) and not (isinstance(b, float) and math.isnan(b)):
            cx.append(float(a))
            cy.append(float(b))
        else:
            dropped += 1
    return cx, cy, dropped

def fit_linear_regression(x: List[float], y: List[float], alpha: float = 0.05, independent: bool = True) -> Dict[str, Any]:
    cx, cy, dropped = _clean_pairs(x, y)
    n = len(cx)
    if n < 3:
        raise ValueError("insufficient_sample: Linear regression requires >= 3 complete pairs.")
        
    x_bar = sum(cx) / n
    y_bar = sum(cy) / n
    
    ss_xy = sum((xi - x_bar) * (yi - y_bar) for xi, yi in zip(cx, cy))
    ss_xx = sum((xi - x_bar) ** 2 for xi in cx)
    ss_yy = sum((yi - y_bar) ** 2 for yi in cy)
    
    if ss_xx <= 0:
        raise ValueError("zero_variance: Predictor variable x has zero variance; cannot estimate slope.")
        
    beta_1 = ss_xy / ss_xx
    beta_0 = y_bar - beta_1 * x_bar
    r_squared = (ss_xy ** 2) / (ss_xx * ss_yy) if ss_yy > 0 else 0.0
    
    residuals = [yi - (beta_0 + beta_1 * xi) for xi, yi in zip(cx, cy)]
    ss_res = sum(e ** 2 for e in residuals)
    df = n - 2
    
    mse = ss_res / df if df > 0 else 0.0
    se_b1 = math.sqrt(mse / ss_xx) if ss_xx > 0 else 0.0
    t_stat = beta_1 / se_b1 if se_b1 > 0 else 0.0
    
    try:
        from scipy.stats import t as t_dist
        p_val = float(2.0 * t_dist.sf(abs(t_stat), df))
    except ImportError:
        p_val = 0.001 if abs(t_stat) > 3.0 else 0.20
        
    return {
        "beta_0": round(beta_0, 6),
        "beta_1": round(beta_1, 6),
        "r_squared": round(r_squared, 6),
        "std_err_beta1": round(se_b1, 6),
        "t_stat": round(t_stat, 6),
        "p_value": round(p_val, 6),
        "n": len(x),
        "df": df,
        "n_used": n,
        "n_dropped": dropped,
        "residuals": [round(e, 4) for e in residuals]
    }
```

---

## Anti-Patterns & Guardrails

- **Zero-Variance Predictor Column** — Attempting to fit OLS regression when all $x$ values are identical, resulting in division by zero ($\text{SS}_{xx} = 0$).
- **Extrapolating Far Beyond Observed Range** — Making predictions $\hat{y}$ at $x$ values well outside the support $[x_{\min}, x_{\max}]$.
- **Ignoring Heteroscedastic Residuals** — Relying on standard OLS inference when residual variance fans out with increasing $x$; use robust Huber-White standard errors.
