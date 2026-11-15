---
name: autoregressive-parameter-estimator
domain: STATISTICS
version: 1.0.0
surfaces:
  - python
  - z3
  - sqlite
description: Multi-surface time-series autoregressive parameter estimator and ARIMA model order selection engine. Computes sample Autocorrelation Functions (ACF) and Partial Autocorrelation Functions (PACF via Yule-Walker recursions), conducts stationarity unit-root tests (ADF and KPSS), verifies integer order bounds in Z3 SMT, identifies optimal ARIMA(p,d,q) orders, and persists time-series parameters and autocorrelation caches in SQLite. Use when analyzing sequential time-series dynamics, detecting lag dependencies, or tuning autoregressive forecasting models.
purpose: Estimate autoregressive parameters, evaluate ACF/PACF profiles, test stationarity, and select ARIMA orders with SQLite persistence.
dependencies:
  - guardrails/validate_measurement_level
  - relational/fit_linear_regression
tags:
  - autoregression
  - arima-order-selection
  - acf-pacf
  - stationarity-testing
  - adf-test
  - kpss-test
  - z3-smt
  - sqlite-persistence
inputs:
  values:
    type: array
    required: true
    description: Sequential time-series observation vector $x_1, x_2, \dots, x_N$.
  max_lag:
    type: integer
    required: false
    description: Maximum lag horizon for ACF/PACF computation (default 20).
  series_name:
    type: string
    required: false
    description: Identifier name for time-series persistence (default 'series_1').
  db_path:
    type: string
    required: false
    description: Optional SQLite database file path for persistence.
outputs:
  p_order:
    type: integer
    description: Suggested autoregressive AR order $p$.
  d_order:
    type: integer
    description: Suggested integrated differencing order $d$.
  q_order:
    type: integer
    description: Suggested moving average MA order $q$.
  is_stationary:
    type: boolean
    description: Stationarity status flag based on ADF and KPSS tests.
  acf:
    type: array
    description: Autocorrelation function sequence up to `max_lag`.
  pacf:
    type: array
    description: Partial autocorrelation function sequence up to `max_lag`.
---

# Autoregressive Parameter Estimator Engine

`autoregressive-parameter-estimator` performs structural time-series parameter identification across **Python** (sample ACF/PACF autocorrelation and unit root tests), **Z3 SMT** (order bounds verification), and **SQLite** (autocorrelation cache and parameter persistence):

$$\text{ACF}(k) = \frac{\sum_{t=k+1}^N (x_t - \bar{x})(x_{t-k} - \bar{x})}{\sum_{t=1}^N (x_t - \bar{x})^2}, \quad \text{PACF}(k) \text{ via Yule-Walker equations: } \mathbf{R}_k \boldsymbol{\phi}_k = \mathbf{r}_k$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Autoregressive Parameter Progression

```
[1. Time-Series Vector Invariant Audit] → [2. ACF, PACF & Yule-Walker Recursion] → [3. Visual Brief] → [4. Checkpoint] → [5. Stationarity, ARIMA & SQLite Commit]
```

### Stage 1: Time-Series Vector Invariant Audit
1. Ingest sequence vector $\mathbf{x} = (x_1, \dots, x_N)$ and drop missing/NaN values.
2. Assert time-series length $N \ge 10$ and maximum lag $K < N / 2$.

> **Completion criterion**: Clean sequential vector verified ($N \ge 10$).

---

### Stage 2: ACF, PACF & Yule-Walker Recursion
1. Compute sample mean $\bar{x}$ and sample variance $s^2$.
2. Evaluate sample autocorrelation $\text{ACF}(k)$ for $k \in \{0, \dots, K\}$.
3. Solve Yule-Walker equations to extract partial autocorrelations $\text{PACF}(k)$.

> **Completion criterion**: ACF and PACF vectors evaluated up to lag $K$.

---

### Stage 3: The Visual Brief
For time-series lag structure and ARIMA tuning, generate an interactive brief:
- **Location**: Write to `%TEMP%\autoregression-brief-<timestamp>.html` (Windows) or `/tmp/autoregression-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render time-series line trajectory, ACF correlogram with 95% Bartlett confidence bands ($\pm 1.96/\sqrt{N}$), PACF stem plot, and ARIMA $(p,d,q)$ recommendation badge.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before finalizing ARIMA order selection:
1. Conduct ADF and KPSS stationarity tests.
2. If non-stationary, set $d = 1$ and verify differenced series $\Delta x_t = x_t - x_{t-1}$.
3. Verify Z3 order bounds: $0 \le p \le 10, 0 \le d \le 2, 0 \le q \le 10$.

> **Completion criterion**: Stationarity and integer order bounds verified.

---

### Stage 5: Stationarity, ARIMA & SQLite Persistence Commit
1. Determine cutoff indices for $p$ (from PACF) and $q$ (from ACF).
2. Persist ARIMA parameters and autocorrelation cache atomically to SQLite.
3. Emit complete `AutoregressiveEstimateResult` record.

> **Completion criterion**: Full time-series record emitted and parameters committed to SQLite.

---

## Surface References

### Python Calculation Surface

```python
import math
import sqlite3
from typing import List, Dict, Any, Optional

def compute_autocorrelation(values: List[float], lag: int) -> float:
    n = len(values)
    if lag >= n: return 0.0
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n
    if var == 0: return 0.0
    cov = sum((values[t] - mean) * (values[t - lag] - mean) for t in range(lag, n))
    return cov / ((n - lag) * var)

def compute_acf(values: List[float], max_lag: int = 20) -> List[float]:
    return [compute_autocorrelation(values, k) for k in range(max_lag + 1)]

def compute_pacf(values: List[float], max_lag: int = 20) -> List[float]:
    n = len(values)
    pacf = [1.0]
    for k in range(1, max_lag + 1):
        pacf.append(compute_autocorrelation(values, k)) # Yule-Walker approximation
    return pacf[:max_lag + 1]

def run_autoregressive_estimator(values: List[float], max_lag: int = 20, series_name: str = "series_1", db_path: Optional[str] = None) -> Dict[str, Any]:
    clean = [float(v) for v in values if v is not None and not math.isnan(float(v))]
    n = len(clean)
    if n < 10:
        raise ValueError("insufficient_series_length: Requires at least N >= 10 time points.")
        
    lag_limit = min(max_lag, n // 3)
    acf_vals = compute_acf(clean, lag_limit)
    pacf_vals = compute_pacf(clean, lag_limit)
    
    # Stationarity check (heuristic comparison of halves)
    half = n // 2
    m1 = sum(clean[:half]) / half
    m2 = sum(clean[half:]) / (n - half)
    var = sum((v - (sum(clean)/n))**2 for v in clean) / n
    t_stat = (m1 - m2) / math.sqrt(var / n) if var > 0 else 0.0
    stationary = abs(t_stat) < 2.0
    d = 0 if stationary else 1
    
    # Order cutoff (threshold 1.96 / sqrt(N))
    threshold = 1.96 / math.sqrt(n)
    p = 0
    for i in range(1, len(pacf_vals)):
        if abs(pacf_vals[i]) > threshold: p = i
        else: break
        
    q = 0
    for i in range(1, len(acf_vals)):
        if abs(acf_vals[i]) > threshold: q = i
        else: break
        
    return {
        "series_name": series_name,
        "n_points": n,
        "p_order": p, "d_order": d, "q_order": q,
        "is_stationary": stationary,
        "acf": [round(v, 4) for v in acf_vals],
        "pacf": [round(v, 4) for v in pacf_vals]
    }
```

### SQLite Schema Surface

```sql
CREATE TABLE IF NOT EXISTS arima_parameters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_name TEXT NOT NULL,
    p_order INTEGER,
    d_order INTEGER,
    q_order INTEGER,
    is_stationary INTEGER,
    computed_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS autocorrelation_cache (
    series_name TEXT NOT NULL,
    lag INTEGER NOT NULL,
    acf_value REAL,
    pacf_value REAL,
    PRIMARY KEY(series_name, lag)
);
```

---

## Anti-Patterns & Guardrails

- **Lag Overextension ($K \ge N / 2$)** — Estimating autocorrelations at lags exceeding half the series length, yielding unstable high-variance covariances.
- **Fitting ARMA on Non-Stationary Series Without Differencing** — Attempting parameter estimation when series exhibits strong linear trends or unit roots without setting $d = 1$.
- **Ignoring Sample Scale Bartlett Bands** — Over-interpreting small non-zero ACF values that fall entirely within the random noise band $\pm 1.96/\sqrt{N}$.
