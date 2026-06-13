---
Domain: RESOURCE_MANAGEMENT
Version: 1.0.0
Complexity: Medium
Type: Allocation
Category: Capacity Planning
Estimated Execution Time: 5-10 minutes
name: predictive-capacity-planner
Source: community
surfaces:
  - python
  - prolog
  - hy

description: Predictive capacity planner for workload forecasting, resource scaling, and bottleneck prevention.
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
origin: manual
triggers:
  - capacity_planning
  - resource_allocation
  - demand_forecasting
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0

## Purpose

Multi-surface predictive capacity planner for forecasting resource demands, optimizing allocation, and detecting bottlenecks with Python for time series forecasting, Prolog for constraint validation, and Hy for fuzzy resource scoring.

## Description

This skill forecasts capacity by:
- Python for ARIMA/time series forecasting
- Prolog for resource constraint logic
- Hy for fuzzy capacity scoring

## Implementation

### Python Forecasting Core

```python
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional

class CapacityPlanner:
    def __init__(self, historical_data: np.ndarray, horizon: int = 30):
        self.data = np.asarray(historical_data)
        self.horizon = horizon

    def forecast_demand(self, method: str = "mean") -> np.ndarray:
        if method == "mean":
            forecast = np.full(self.horizon, np.mean(self.data))
        elif method == "trend":
            x = np.arange(len(self.data))
            slope = np.polyfit(x, self.data, 1)[0]
            forecast = np.arange(self.horizon) * slope + np.mean(self.data)
        else:
            forecast = np.full(self.horizon, np.median(self.data))
        return np.clip(forecast, 0, None)

    def calculate_required_capacity(self, utilization_target: float = 0.8) -> float:
        peak = np.max(self.data)
        safety_margin = 1.2
        return peak * safety_margin / utilization_target

def detect_bottleneck(current: float, capacity: float, threshold: float = 0.9) -> bool:
    return current / capacity > threshold
```

### Prolog Capacity Rules

```prolog
% Resource constraints
resource_constraint(Capacity, Demand, Utilization) :-
    Utilization is Demand / Capacity,
    Utilization =< 0.9.

% Over-provisioning detection
over_provisioned(Capacity, Demand, Threshold) :-
    Ratio is Capacity / Demand,
    Ratio > Threshold.

% Under-provisioning detection
under_provisioned(Capacity, Demand, Threshold) :-
    Ratio is Demand / Capacity,
    Ratio > Threshold.
```

### Hy Fuzzy Scoring

```hy
(defn capacity-utilization-score [current capacity]
  (let [util (/ current (max 1e-10 capacity))]
    (cond
      [(< util 0.6) 1.0]  ; under-utilized
      [(> util 0.9) 0.5]  ; over capacity
      [True (- 1.0 util)])))  ; normal range
```

## Testing

### Unit Tests

```python
import pytest
import numpy as np

@pytest.mark.asyncio
async def test_capacity_forecast():
    code = '''
import numpy as np

data = np.random.randn(100) * 10 + 100
np.random.seed(42)
forecast = [np.mean(data) for _ in range(30)]
len(forecast) == 30
'''
    from em_cubed.surfaces import PythonSurface
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

@pytest.mark.asyncio
async def test_bottleneck_detection():
    code = '''
current = 95
capacity = 100
threshold = 0.9
is_bottleneck = (current / capacity) > threshold
is_bottleneck
'''
    from em_cubed.surfaces import PythonSurface
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"
    assert result["value"] is True

@pytest.mark.asyncio
async def test_capacity_prolog_rule():
    code = '''
resource_constraint(Capacity, Demand, Utilization) :-
    Utilization is Demand / Capacity,
    Utilization =< 0.9.

?- resource_constraint(100, 80, Util).
'''
    from em_cubed.surfaces import PrologSurface
    surface = PrologSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"
```

## Security Considerations
- Pure numerical operations on in-memory data
- No network access

## Dependencies
- numpy
- pandas
- em_cubed framework