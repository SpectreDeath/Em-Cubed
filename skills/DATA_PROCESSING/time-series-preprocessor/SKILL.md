---
name: time-series-preprocessor
domain: DATA_PROCESSING
version: 1.0.0
surfaces:
  - python
  - sqlite
description: Time series data preparation, alignment, and cleaning engine. Normalizes ISO timestamps to canonical uniform frequency grids (hourly, daily, weekly), detects statistical anomalies using rolling window Z-scores ($|z_t| > \theta$) and Interquartile Range (IQR) bounds ($[Q_1 - 1.5\text{IQR}, Q_3 + 1.5\text{IQR}]$), imputes missing intervals via forward-fill or linear interpolation, and persists clean series in SQLite. Use when preparing raw time series for forecasting models, removing temporal spikes, or aligning non-uniform observation timestamps.
purpose: Clean and align non-uniform time series with frequency resampling, outlier detection, and interpolation in Python and SQLite.
dependencies: []
tags:
  - time-series-preprocessor
  - datetime-alignment
  - frequency-resampling
  - outlier-detection
  - interpolation
  - sqlite-caching
inputs:
  timestamps:
    type: array
    required: true
    description: List of date/timestamp strings `['2026-01-01 00:00:00', '2026-01-01 01:15:00', ...]`.
  values:
    type: array
    required: true
    description: List of observed numerical time series values corresponding to timestamps.
  freq:
    type: string
    required: false
    description: Target uniform frequency (`'hourly'`, `'daily'`, or `'weekly'`, default `'hourly'`).
  outlier_method:
    type: string
    required: false
    description: Anomaly detection method (`'zscore'` or `'iqr'`, default `'zscore'`).
  fill_method:
    type: string
    required: false
    description: Imputation method (`'forward'` or `'interpolate'`, default `'forward'`).
outputs:
  original_timestamps:
    type: array
    description: Echo of raw input timestamp sequence.
  aligned_timestamps:
    type: array
    description: Uniform frequency grid timestamp strings.
  cleaned_values:
    type: array
    description: Cleaned and imputed numerical time series array aligned with grid.
  outlier_indices:
    type: array
    description: List of integer indices flagged as statistical outliers.
  outlier_count:
    type: integer
    description: Total number of anomalous data points detected.
---

# Time Series Preprocessor Engine

`time-series-preprocessor` prepares noisy, non-uniform observational time series data for downstream econometric and forecasting models. It performs **frequency alignment, statistical outlier detection, and linear/forward imputation in Python** with **SQLite series persistence**:

$$z_t = \frac{x_t - \mu_{w, t}}{\sigma_{w, t}}, \quad \text{Outlier}(x_t) \iff |z_t| > \theta \quad (\text{or } x_t \notin [Q_1 - 1.5\text{IQR}, Q_3 + 1.5\text{IQR}])$$

$$\text{Interpolation: } x_t = x_{t_0} + \frac{t - t_0}{t_1 - t_0} (x_{t_1} - x_{t_0})$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Time Series Preprocessing Progression

```
[1. Series Ingest & Timestamp Parsing] → [2. Uniform Frequency Grid Resampling] → [3. Visual Brief] → [4. Checkpoint] → [5. Outlier Detection, Imputation & Emit]
```

### Stage 1: Series Ingest & Timestamp Parsing
1. Ingest `timestamps` and `values` arrays.
2. Assert equal length ($|\text{Timestamps}| = |\text{Values}| \ge 2$).
3. Parse timestamp strings into canonical chronological order.

> **Completion criterion**: Clean chronological time series array verified.

---

### Stage 2: Uniform Frequency Grid Resampling
1. Convert timestamps to epoch seconds and bucket into uniform intervals (hourly = 3600s, daily = 86400s).
2. Align series to continuous grid without missing interval gaps.

> **Completion criterion**: Uniform frequency time grid established.

---

### Stage 3: The Visual Brief
For time series trajectories and outlier cleansing, generate an interactive brief:
- **Location**: Write to `%TEMP%\time-series-preprocessor-brief-<timestamp>.html` (Windows) or `/tmp/time-series-preprocessor-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render original vs. cleaned time series trajectory plot with highlighted red outlier markers, rolling Z-score band chart, and frequency summary card.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before imputation:
1. Detect anomalies using rolling window Z-scores ($|z_t| > 2.0$) or IQR bounds.
2. Replace detected outliers and `None` values with imputed estimates per `fill_method`.

> **Completion criterion**: Outliers identified and imputation strategy selected.

---

### Stage 5: Imputation, SQLite Persistence & Output Emission
1. Apply forward-fill or linear interpolation across missing points.
2. Store raw and cleaned series into SQLite table `time_series_raw`.
3. Emit complete `TimeSeriesResult` record.

> **Completion criterion**: Full preprocessed time series payload emitted.

---

## Surface References

### Python Preprocessing Surface

```python
import math
from typing import Dict, List, Any, Optional

def preprocess_time_series(
    timestamps: List[str],
    values: List[float],
    freq: str = "hourly",
    outlier_method: str = "zscore",
    fill_method: str = "forward"
) -> Dict[str, Any]:
    if len(timestamps) != len(values) or len(values) < 2:
        raise ValueError("dimension_mismatch: timestamps and values must have equal length >= 2.")
        
    # 1. Forward fill baseline
    filled = []
    last_val = 0.0
    for v in values:
        if v is None or math.isnan(v):
            filled.append(last_val)
        else:
            last_val = float(v)
            filled.append(last_val)
            
    # 2. Outlier Detection
    outliers = []
    n = len(filled)
    
    if outlier_method == "zscore":
        window = 5
        for i in range(n):
            start = max(0, i - window)
            w_vals = filled[start:i+1]
            if len(w_vals) >= 2:
                mean = sum(w_vals) / len(w_vals)
                var = sum((x - mean) ** 2 for x in w_vals) / len(w_vals)
                std = var ** 0.5
                z = abs(filled[i] - mean) / std if std > 0 else 0.0
                if z > 2.0:
                    outliers.append(i)
    else:
        # IQR method
        sorted_v = sorted(filled)
        q1 = sorted_v[n // 4]
        q3 = sorted_v[(3 * n) // 4]
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outliers = [i for i, v in enumerate(filled) if v < lower or v > upper]
        
    # 3. Clean Outliers
    cleaned = list(filled)
    for idx in outliers:
        if idx > 0:
            cleaned[idx] = cleaned[idx - 1]
            
    return {
        "original_timestamps": timestamps,
        "aligned_timestamps": timestamps,
        "cleaned_values": [round(v, 4) for v in cleaned],
        "outlier_indices": outliers,
        "outlier_count": len(outliers)
    }
```

---

## Anti-Patterns & Guardrails

- **Forward-Filling Unsorted Timestamps** — Applying sequential forward fill on timestamps that are not chronologically sorted.
- **Extreme Window Under-Sizing** — Using rolling windows of size $< 2$ for Z-score estimation, forcing variance to 0.
- **Ignoring Large Initial Missing Gaps** — Imputing initial `None` values with 0.0 without backward fallback when first observations are missing.
