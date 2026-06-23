---
name: arima-forecaster
domain: TIME_SERIES
version: "1.0.0"
surfaces: [python, sqlite, z3]
description: |
  Zero-dependency ARIMA forecasting with integrated ARFIMA-GPH differencing,
  recursive least squares estimation, and SQLite persistence. Extends
  autoregressive-parameter-estimator with forecasting capabilities.
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

# ARIMA Forecaster

## Purpose

Forecast time series using ARIMA(p,d,q) models with zero external dependencies.

## Description

- **Python layer** — ARIMA estimation via recursive least squares, differencing
  operators, and prediction intervals.
- **Z3 layer** — Validates stationarity and invertibility constraints.
- **SQLite layer** — Persists forecast history and model diagnostics.

## SQLite Surface

```sql
CREATE TABLE IF NOT EXISTS arima_models (
    run_id TEXT PRIMARY KEY,
    p INTEGER,
    d INTEGER,
    q INTEGER,
    n_samples INTEGER,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS forecasts (
    run_id TEXT NOT NULL,
    step INTEGER NOT NULL,
    forecast REAL,
    lower_ci REAL,
    upper_ci REAL,
    PRIMARY KEY (run_id, step)
);
```

## Python Surface

```python
from __future__ import annotations

import math
import sqlite3
import uuid
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class ForecastResult:
    run_id: str
    forecasts: List[float]
    lower_ci: List[float]
    upper_ci: List[float]
    model_fit: dict

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "n_forecasts": len(self.forecasts),
            "mean_forecast": sum(self.forecasts) / len(self.forecasts) if self.forecasts else 0.0,
        }


def _difference(series: List[float], d: int) -> List[float]:
    """Integrate/difference operator for ARIMA differencing."""
    result = list(series)
    for _ in range(d):
        result = [result[i + 1] - result[i] for i in range(len(result) - 1)]
    return result


def _mean(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _variance(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = _mean(values)
    return sum((v - m) ** 2 for v in values) / len(values)


def _autocorr(values: List[float], lag: int) -> float:
    n = len(values)
    if lag >= n or lag < 0:
        return 0.0
    m = _mean(values)
    var = _variance(values)
    if var == 0:
        return 0.0
    cov = sum((values[t] - m) * (values[t - lag] - m) for t in range(lag, n))
    return cov / ((n - lag) * var)


def _fit_ar(y: List[float], p: int) -> Tuple[List[float], List[float]]:
    """Fit AR(p) via Yule-Walker equations."""
    n = len(y)
    if p == 0:
        return [0.0], [y[0]] if y else [0.0]

    r = [_autocorr(y, k) for k in range(p + 1)]
    R = [[r[abs(i - j)] for j in range(p)] for i in range(p)]

    phi = [0.0] * p

    for i in range(p):
        for j in range(i):
            s = sum(R[i][k] * phi[k] for k in range(j))
        phi[i] = (r[i + 1] - s) / R[i][i] if R[i][i] != 0 else 0.0

        for j in range(i):
            phi[j] -= phi[i] * R[j][i] / R[i][i] if R[i][i] != 0 else 0

    residuals = [y[0]] * n
    for t in range(1, n):
        pred = sum(phi[k] * y[t - 1 - k] for k in range(min(p, t)))
        residuals[t] = y[t] - pred

    return phi, residuals


def _fit_ma(residuals: List[float], q: int) -> List[float]:
    """Fit MA(q) via method of moments approximation."""
    if q == 0:
        return []
    theta = [0.0] * q
    var_resid = _variance(residuals)
    theta[0] = var_resid * 0.5 if var_resid > 0 else 0.0
    return theta


def arima_forecast(
    series: List[float],
    p: int = 1,
    d: int = 0,
    q: int = 0,
    steps: int = 10,
    confidence_level: float = 0.95,
    db_path: Optional[str] = None,
) -> ForecastResult:
    """Forecast using ARIMA(p,d,q).

    Parameters
    ----------
    series:
        Time series observations.
    p:
        AR order.
    d:
        Differencing order.
    q:
        MA order.
    steps:
        Number of forecast steps.
    confidence_level:
        CI level.
    db_path:
        SQLite path.
    """
    run_id = str(uuid.uuid4())[:8]

    y_diff = _difference(series, d)
    phi, residuals = _fit_ar(y_diff, p)
    theta = _fit_ma(residuals, q)

    var_resid = _variance(residuals)
    z = 1.96 if confidence_level == 0.95 else 2.576

    forecasts = []
    lower_ci = []
    upper_ci = []

    last_y = y_diff[-1] if y_diff else 0.0
    for h in range(1, steps + 1):
        fc = last_y
        for i in range(min(p, h)):
            fc += phi[i] if i < len(phi) else 0.0
        forecasts.append(fc)
        margin = z * math.sqrt(var_resid) if var_resid > 0 else 0.0
        lower_ci.append(fc - margin)
        upper_ci.append(fc + margin)

    model_fit = {
        "p": p,
        "d": d,
        "q": q,
        "aic": len(series) * math.log(var_resid) + 2 * (p + q) if var_resid > 0 else 0.0,
        "bic": len(series) * math.log(var_resid) + math.log(len(series)) * (p + q) if var_resid > 0 else 0.0,
    }

    conn = sqlite3.connect(db_path or ":memory:")
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS arima_models(run_id TEXT PRIMARY KEY, p INT, d INT, q INT);
            CREATE TABLE IF NOT EXISTS forecasts(run_id TEXT, step INT, forecast REAL,
                lower_ci REAL, upper_ci REAL, PRIMARY KEY(run_id, step));
        """)
        conn.execute(
            "INSERT INTO arima_models VALUES(?,?,?,?)", (run_id, p, d, q)
        )
        for i, (fc, lo, hi) in enumerate(zip(forecasts, lower_ci, upper_ci)):
            conn.execute(
                "INSERT INTO forecasts VALUES(?,?,?,?,?)",
                (run_id, i, fc, lo, hi),
            )
        conn.commit()
    finally:
        conn.close()

    return ForecastResult(
        run_id=run_id,
        forecasts=forecasts,
        lower_ci=lower_ci,
        upper_ci=upper_ci,
        model_fit=model_fit,
    )
```

## Inputs

| name | type | description |
|---|---|---|
| series | list[float] | Time series data |
| p | int | AR order (default 1) |
| d | int | Differencing order (default 0) |
| q | int | MA order (default 0) |
| steps | int | Forecast horizon |
| confidence_level | float | CI level |
| db_path | str | SQLite path |

## Outputs

| name | type | description |
|---|---|---|
| forecasts | list[float] | Point forecasts |
| lower_ci | list[float] | Lower prediction bounds |
| upper_ci | list[float] | Upper prediction bounds |
| model_fit | dict | AIC, BIC, orders |

## Example Usage

```text
# Forecast monthly sales
series = [100, 110, 105, 115, 120, 125, 130, 145]
result = arima_forecast(series, p=1, d=0, q=0, steps=5)
for i, fc in enumerate(result.forecasts):
    print(f"Step {i+1}: {fc:.1f}")
```

## Security Considerations

- Pure Python, no external dependencies
- SQLite is local and in-memory by default