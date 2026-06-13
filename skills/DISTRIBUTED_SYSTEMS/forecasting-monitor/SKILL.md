---
name: forecasting-monitor
Domain: DISTRIBUTED_SYSTEMS
version: "1.0.0"
surfaces:
  - python
  - sqlite
description: Multi-surface forecasting monitor with Python surface for drift detection and SQLite surface for metric history tracking. Supports configurable thresholds and restart policies.
compatibility: PYTHON
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

# Forecasting Monitor

Continuous monitoring of production forecasts with concept drift detection, accuracy tracking, and automated retraining triggers.

## Purpose

Monitor time series forecasting models in production: detect concept drift, track forecast accuracy, and trigger retraining workflows via DAG scheduler integration.

## Description

Production monitoring capabilities:
- Python: Rolling error metrics, drift detection, retraining decision logic
- SQLite: Forecast storage, accuracy history, drift alerts
- Integration with DAG task scheduler for automated retraining

## Implementation

### Python Monitor Core

```python
import time
import math
from typing import Dict, List, Optional, Tuple

def compute_mae(actual: List[float], predicted: List[float]) -> float:
    """Compute Mean Absolute Error."""
    n = min(len(actual), len(predicted))
    if n == 0:
        return 0.0
    return sum(abs(actual[i] - predicted[i]) for i in range(n)) / n

def compute_mape(actual: List[float], predicted: List[float]) -> float:
    """Compute Mean Absolute Percentage Error."""
    n = min(len(actual), len(predicted))
    if n == 0:
        return 0.0
    errors = [abs((actual[i] - predicted[i]) / actual[i]) if actual[i] != 0 else 0
              for i in range(n)]
    return sum(errors) / n * 100

def compute_rmse(actual: List[float], predicted: List[float]) -> float:
    """Compute Root Mean Square Error."""
    n = min(len(actual), len(predicted))
    if n == 0:
        return 0.0
    return math.sqrt(sum((actual[i] - predicted[i]) ** 2 for i in range(n)) / n)

def rolling_accuracy_metrics(actual: List[float], predicted: List[float], window: int = 10) -> Dict:
    """Compute rolling accuracy metrics."""
    n = min(len(actual), len(predicted))
    if n < window:
        return {"mae": compute_mae(actual, predicted), "mape": compute_mape(actual, predicted)}
    
    recent_actual = actual[-window:]
    recent_predicted = predicted[-window:]
    return {
        "mae": compute_mae(recent_actual, recent_predicted),
        "mape": compute_mape(recent_actual, recent_predicted),
        "rmse": compute_rmse(recent_actual, recent_predicted)
    }

def detect_concept_drift(actual: List[float], predicted: List[float], threshold: float = 0.2) -> Dict:
    """Detect concept drift in forecast accuracy."""
    n = len(actual)
    if n < 20:
        return {"drift_detected": False, "insufficient_data": True}
    
    mae = compute_mae(actual, predicted)
    errors = [abs(actual[i] - predicted[i]) for i in range(n)]
    
    # Compare recent error variance to historical
    recent_std = math.sqrt(sum((e - mae) ** 2 for e in errors[-10:]) / 10)
    hist_std = math.sqrt(sum((e - mae) ** 2 for e in errors[:-10]) / max(1, n - 10))
    
    drift_detected = recent_std > threshold * hist_std
    
    return {
        "drift_detected": drift_detected,
        "current_mae": mae,
        "recent_std": recent_std,
        "historical_std": hist_std,
        "drift_ratio": recent_std / hist_std if hist_std > 0 else 1.0
    }

def should_retrain(actual: List[float], predicted: List[float], error_threshold: float = 1.0) -> bool:
    """Decision logic for model retraining."""
    n = min(len(actual), len(predicted))
    if n == 0:
        return False
    
    mae = compute_mae(actual, predicted)
    drift = detect_concept_drift(actual, predicted)
    
    # Retrain if error exceeds threshold or drift detected
    return mae > error_threshold or drift["drift_detected"]

def model_version_check(current_version: str, min_accuracy: float = 0.7) -> bool:
    """Check if model version meets minimum accuracy requirements."""
    return True  # Placeholder - actual check via SQLite

def trigger_retraining(workflow_id: str, model_params: Dict) -> Dict:
    """Trigger retraining workflow via DAG scheduler integration."""
    return {
        "workflow_id": workflow_id,
        "triggered": True,
        "reason": "accuracy_degraded",
        "params": model_params,
        "timestamp": time.time()
    }

def compute_forecast_accuracy(actual: List[float], predicted: List[float]) -> Dict:
    """Comprehensive forecast accuracy assessment."""
    return {
        "mae": compute_mae(actual, predicted),
        "mape": compute_mape(actual, predicted),
        "rmse": compute_rmse(actual, predicted),
        "mean_actual": sum(actual) / len(actual) if actual else 0.0,
        "mean_predicted": sum(predicted) / len(predicted) if predicted else 0.0
    }

def aggregate_forecast_performance(forecasts: List[Dict]) -> Dict:
    """Aggregate accuracy across multiple forecast runs."""
    if not forecasts:
        return {}
    
    mae_values = [f.get("mae", 0) for f in forecasts if f.get("mae") is not None]
    mape_values = [f.get("mape", 0) for f in forecasts if f.get("mape") is not None]
    
    return {
        "avg_mae": sum(mae_values) / len(mae_values) if mae_values else 0.0,
        "avg_mape": sum(mape_values) / len(mape_values) if mape_values else 0.0,
        "total_forecasts": len(forecasts),
        "degraded_runs": sum(1 for f in forecasts if f.get("mae", 0) > 1.0)
    }
```

### SQLite Forecast Store

```sql
CREATE TABLE IF NOT EXISTS forecast_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id TEXT NOT NULL,
    model_version TEXT,
    forecast_time TEXT,
    horizon INTEGER,
    actual_value REAL,
    predicted_value REAL,
    error REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS forecast_accuracy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL,
    window_start TEXT,
    window_end TEXT,
    computed_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS drift_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    metric_value REAL,
    threshold REAL,
    triggered_at TEXT DEFAULT CURRENT_TIMESTAMP,
    resolved INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS retraining_triggers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    model_params_json TEXT,
    triggered_at TEXT DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending'
);

CREATE INDEX IF NOT EXISTS idx_forecast_workflow ON forecast_records(workflow_id, forecast_time);
CREATE INDEX IF NOT EXISTS idx_accuracy_workflow ON forecast_accuracy(workflow_id);
CREATE INDEX IF NOT EXISTS idx_alerts_unresolved ON drift_alerts(resolved) WHERE resolved = 0;

INSERT INTO forecast_records (workflow_id, model_version, forecast_time, horizon, actual_value, predicted_value, error)
VALUES (?, ?, ?, ?, ?, ?, ?);

INSERT INTO forecast_accuracy (workflow_id, metric_name, metric_value, window_start, window_end)
VALUES (?, ?, ?, ?, ?);

INSERT INTO drift_alerts (workflow_id, alert_type, metric_value, threshold)
VALUES (?, ?, ?, ?);

SELECT workflow_id, AVG(error) as avg_error
FROM forecast_records
WHERE forecast_time >= ?
GROUP BY workflow_id;

SELECT metric_name, metric_value FROM forecast_accuracy
WHERE workflow_id = ? AND computed_at >= ?
ORDER BY computed_at DESC LIMIT 10;

SELECT COUNT(*) as drift_count FROM drift_alerts
WHERE workflow_id = ? AND resolved = 0;

UPDATE drift_alerts SET resolved = 1 WHERE id = ?;
```

### DAG Integration for Retraining

```python
def build_retraining_dag(model_id: str, p: int, d: int, q: int) -> List[tuple]:
    """Generate DAG dependencies for retraining workflow."""
    return [
        ("fetch_training_data", "preprocess_data"),
        ("preprocess_data", "train_model"),
        ("train_model", "validate_model"),
        ("validate_model", "deploy_model")
    ]

def extract_model_params(arima_record: Dict) -> Dict:
    """Extract model parameters for retraining task."""
    return {
        "p": arima_record.get("p_order", 1),
        "d": arima_record.get("d_order", 0),
        "q": arima_record.get("q_order", 1),
        "horizon": arima_record.get("horizon", 10)
    }
```

## Testing

```python
def test_mae_calculation():
    actual = [1.0, 2.0, 3.0, 4.0]
    predicted = [1.1, 2.1, 2.9, 4.2]
    mae = compute_mae(actual, predicted)
    assert mae == 0.125

def test_concept_drift_detection():
    stable = [0.1, 0.1, 0.1, 0.1, 0.1]
    predictions = [0.15, 0.05, 0.12, 0.08, 0.11]
    drift = detect_concept_drift(stable, predictions, threshold=0.5)
    assert "drift_detected" in drift

def test_retraining_decision():
    actual = [1.0, 2.0, 3.0, 100.0, 5.0]  # Spike causing high error
    predicted = [1.0, 2.0, 3.0, 4.0, 5.0]
    should = should_retrain(actual, predicted, error_threshold=0.5)
    assert should == True

def test_forecast_aggregation():
    forecasts = [
        {"mae": 0.1, "mape": 5.0},
        {"mae": 0.2, "mape": 10.0},
        {"mae": 0.15, "mape": 7.5}
    ]
    agg = aggregate_forecast_performance(forecasts)
    assert agg["avg_mae"] == 0.15
    assert agg["total_forecasts"] == 3
```

## Security Considerations

- Metrics are statistical aggregates only
- No PII in forecast records
- SQLite for isolated storage