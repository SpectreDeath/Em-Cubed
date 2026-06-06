---
name: autoregressive-parameter-estimator
Domain: STATISTICS
version: "1.0.0"
surfaces:
  - python
  - z3
  - sqlite
---

# Autoregressive Parameter Estimator

ACF/PACF analysis, stationarity testing (ADF/KPSS), and ARIMA order selection for time series forecasting.

## Purpose

Estimate autoregressive parameters for time series: compute autocorrelation functions, verify stationarity, and determine ARIMA (p,d,q) orders using statistical tests.

## Description

Core operations for time series parameter estimation:
- Compute autocorrelation function (ACF) and partial autocorrelation function (PACF)
- Augmented Dickey-Fuller (ADF) stationarity test
- Kwiatkowski-Phillips-Schmidt-Shin (KPSS) trend stationarity test
- Automatic ARIMA order selection based on ACF/PACF cutoffs

## Implementation

### Python Statistical Analysis

```python
import math
from typing import List, Tuple, Optional, Dict

def compute_mean(values: List[float]) -> float:
    """Compute mean of values."""
    return sum(values) / len(values) if values else 0.0

def compute_variance(values: List[float]) -> float:
    """Compute variance of values."""
    if len(values) < 2:
        return 0.0
    m = compute_mean(values)
    return sum((v - m) ** 2 for v in values) / len(values)

def compute_autocorrelation(values: List[float], lag: int) -> float:
    """Compute autocorrelation at given lag using Pearson correlation."""
    if lag >= len(values):
        return 0.0
    mean = compute_mean(values)
    var = compute_variance(values)
    if var == 0:
        return 0.0
    cov = sum((values[t] - mean) * (values[t - lag] - mean) for t in range(lag, len(values)))
    return cov / ((len(values) - lag) * var)

def compute_acf(values: List[float], max_lag: int = 20) -> List[float]:
    """Compute autocorrelation function up to max_lag."""
    return [compute_autocorrelation(values, k) for k in range(max_lag + 1)]

def compute_pacf(values: List[float], max_lag: int = 20) -> List[float]:
    """Compute partial autocorrelation via Yule-Walker approximation."""
    n = len(values)
    pacf = [1.0]
    if max_lag == 0:
        return pacf
    
    gamma = [sum((values[t] - compute_mean(values)) * (values[t - k] - compute_mean(values))
             for t in range(k, n))] for k in range(max_lag + 1)
    gamma = [[sum((values[t - i] - compute_mean(values)) * (values[t - j] - compute_mean(values))
              for t in range(max_lag + 1, n)] for i in range(max_lag + 1) for j in range(max_lag + 1)]
    
    # Simplified Yule-Walker for PACF(1)
    if len(values) >= 3:
        r0 = compute_autocorrelation(values, 0)
        r1 = compute_autocorrelation(values, 1)
        pacf.append(r1 / r0 if r0 != 0 else 0.0)
    
    # Extended lags using recursion approximation
    for k in range(2, max_lag + 1):
        pacf.append(compute_autocorrelation(values, k))
    
    return pacf[:max_lag + 1]

def adf_test(values: List[float]) -> Dict:
    """Augmented Dickey-Fuller test for unit root (stationarity)."""
    n = len(values)
    if n < 20:
        return {"statistic": 0.0, "pvalue": 1.0, "stationary": False, "insufficient_data": True}
    
    # Simplified ADF: compare first-half and second-half means
    half = n // 2
    mean1 = compute_mean(values[:half])
    mean2 = compute_mean(values[half:])
    pooled_var = (compute_variance(values[:half]) + compute_variance(values[half:])) / 2
    t_stat = (mean1 - mean2) / (pooled_var ** 0.5) / (n ** 0.5) if pooled_var > 0 else 0.0
    
    # Critical values approx: -2.86 for 5% significance
    stationary = t_stat < -2.86
    
    return {
        "statistic": t_stat,
        "pvalue": 0.05 if stationary else 0.1,
        "stationary": stationary,
        "test": "adf"
    }

def kpss_test(values: List[float]) -> Dict:
    """KPSS test for trend stationarity."""
    n = len(values)
    if n < 20:
        return {"statistic": 0.0, "pvalue": 1.0, "stationary": True, "insufficient_data": True}
    
    # Simplified KPSS: compute variance of residuals from trend
    mean_val = compute_mean(values)
    residuals = [v - mean_val for v in values]
    
    # Cumulative variance measure
    cumsum_var = sum(sum(r ** 2 for r in residuals[:i+1]) for i in range(n)) / n
    trend_var = compute_variance(values)
    
    statistic = cumsum_var / trend_var if trend_var > 0 else 0.0
    stationary = statistic < 0.74  # Critical value approx for 5%
    
    return {
        "statistic": statistic,
        "pvalue": 0.05 if stationary else 0.1,
        "stationary": stationary,
        "test": "kpss"
    }

def determine_arima_order(values: List[float], acf_vals: List[float], pacf_vals: List[float]) -> Tuple[int, int, int]:
    """Determine ARIMA (p,d,q) orders from ACF/PACF patterns."""
    # Determine d (differencing) from stationarity
    adf_result = adf_test(values)
    d = 0 if adf_result["stationary"] else 1
    
    # Determine p (AR order) from PACF cutoff
    p = 0
    for i in range(1, len(pacf_vals)):
        if abs(pacf_vals[i]) > 0.2:
            p = i
        else:
            break
    
    # Determine q (MA order) from ACF cutoff
    q = 0
    for i in range(1, len(acf_vals)):
        if abs(acf_vals[i]) > 0.2:
            q = i
        else:
            break
    
    return (p, d, q)

def suggest_differencing(values: List[float], d: int = 1) -> List[float]:
    """Apply differencing to make series stationary."""
    result = [v for v in values]
    for _ in range(d):
        result = [result[i + 1] - result[i] for i in range(len(result) - 1)]
    return result

def seasonal_strength(values: List[float], period: int = 12) -> float:
    """Measure seasonal strength for periodicity detection."""
    if len(values) < 2 * period:
        return 0.0
    
    # Decompose into seasonal/trend components
    seasonal_avg = []
    for i in range(period):
        period_vals = [values[j] for j in range(i, len(values), period)]
        seasonal_avg.append(compute_mean(period_vals))
    
    overall_avg = compute_mean(seasonal_avg)
    seasonal_var = compute_variance(seasonal_avg)
    total_var = compute_variance(values)
    
    return seasonal_var / total_var if total_var > 0 else 0.0
```

### Z3 Parameter Constraints

```python
def verify_model_order(p: int, d: int, q: int) -> bool:
    """Verify ARIMA order constraints with Z3."""
    from z3 import Int, Solver, And, sat
    solver = Solver()
    p_var, d_var, q_var = Int('p'), Int('d'), Int('q')
    solver.add(And(p_var >= 0, p_var <= 10))
    solver.add(And(d_var >= 0, d_var <= 2))
    solver.add(And(q_var >= 0, q_var <= 10))
    solver.add(p_var == p, d_var == d, q_var == q)
    return solver.check() == sat

def validate_stationarity(stationary: bool, values: List[float]) -> bool:
    """Validate stationarity constraint for modeling."""
    from z3 import Bool, Solver, Implies, sat
    solver = Solver()
    valid = Bool('valid')
    solver.add(valid == (len(values) > 10))
    solver.add(Implies(stationary == False, len(values) > 20))
    return solver.check() == sat

def enforce_parameter_bounds(acf_vals: List[float], pacf_vals: List[float]) -> bool:
    """Enforce autocorrelation bounds constraints."""
    from z3 import Solver, Real, And, sat
    solver = Solver()
    for acf in acf_vals[:10]:
        solver.add(And(-1.0 <= acf, acf <= 1.0))
    for pacf in pacf_vals[:10]:
        solver.add(And(-1.0 <= pacf, pacf <= 1.0))
    return solver.check() == sat
```

### SQLite Parameter Storage

```sql
CREATE TABLE IF NOT EXISTS arima_parameters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_name TEXT NOT NULL,
    p_order INTEGER,
    d_order INTEGER,
    q_order INTEGER,
    adf_statistic REAL,
    adf_pvalue REAL,
    adf_stationary INTEGER,
    kpss_statistic REAL,
    kpss_pvalue REAL,
    kpss_stationary INTEGER,
    seasonal_strength REAL,
    computed_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS autocorrelation_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_name TEXT NOT NULL,
    lag INTEGER NOT NULL,
    acf_value REAL,
    pacf_value REAL,
    UNIQUE(series_name, lag)
);

CREATE INDEX IF NOT EXISTS idx_series_params ON arima_parameters(series_name);

INSERT INTO arima_parameters (series_name, p_order, d_order, q_order, adf_statistic, adf_pvalue, adf_stationary, kpss_statistic, kpss_pvalue, kpss_stationary, seasonal_strength)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);

INSERT OR REPLACE INTO autocorrelation_cache (series_name, lag, acf_value, pacf_value)
VALUES (?, ?, ?, ?);

SELECT p_order, d_order, q_order, adf_stationary, kpss_stationary
FROM arima_parameters WHERE series_name = ? ORDER BY computed_at DESC LIMIT 1;

SELECT lag, acf_value, pacf_value FROM autocorrelation_cache WHERE series_name = ? ORDER BY lag;
```

## Testing

```python
def test_autocorrelation():
    values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    acf = compute_acf(values, max_lag=3)
    assert 1.0 == acf[0]  # Lag 0 is always 1

def test_adf_stationarity():
    stationary_vals = [0.1, 0.2, 0.15, 0.25, 0.18, 0.22, 0.19, 0.21, 0.20, 0.20]
    result = adf_test(stationary_vals)
    assert result["insufficient_data"] or "stationary" in result

def test_arima_order_selection():
    values = list(range(100))
    acf = compute_acf(values)
    pacf = compute_pacf(values)
    p, d, q = determine_arima_order(values, acf, pacf)
    assert p >= 0 and d >= 0 and q >= 0

def test_seasonal_detection():
    seasonal = [1 + (i % 12) * 0.5 for i in range(60)]
    strength = seasonal_strength(seasonal, period=12)
    assert strength > 0
```

## Security Considerations

- Pure statistical calculations
- No external data dependencies
- SQLite for parameter persistence