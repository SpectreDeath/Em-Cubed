---
name: time-series-preprocessor
domain: DATA_PROCESSING
version: 1.0.0
surfaces:
- python
- sqlite
description: Multi-surface time series preprocessor with Python surface for datetime parsing and SQLite surface for resampled
  data storage. Supports configurable interpolation and deduplication.
compatibility: PYTHON
allowed-tools: '- read

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

  '
---

# Time Series Preprocessor

Time series cleaning and preparation with datetime alignment, outlier detection, and imputation.

## Purpose

Clean and prepare time series data: handle missing timestamps, detect outliers via rolling statistics, align frequency grids, and perform forward-fill imputation.

## Description

Core operations for time series preprocessing:
- Convert to canonical datetime format, resample to uniform frequency
- Detect outliers using rolling Z-scores and IQR bounds
- Reindex missing timestamps to frequency grid
- Forward-fill and interpolate missing values

## Implementation

### Python Preprocessing Core

```python
import time
from typing import Dict, List, Tuple, Optional

def parse_datetime(ts_str: str) -> Tuple[int, int, int, int, int, int]:
    """Parse datetime string to (year, month, day, hour, minute, second) tuple."""
    parts = ts_str.replace('-', ' ').replace(':', ' ').replace('T', ' ').split()
    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    hour, minute = int(parts[3]) if len(parts) > 3 else 0, int(parts[4]) if len(parts) > 4 else 0
    second = int(parts[5]) if len(parts) > 5 else 0
    return (year, month, day, hour, minute, second)

def datetime_to_seconds(dt_tuple: Tuple[int, ...]) -> float:
    """Convert datetime tuple to Unix timestamp (simplified)."""
    year, month, day, hour, minute, second = dt_tuple
    days = year * 365 + month * 31 + day
    return days * 86400 + hour * 3600 + minute * 60 + second

def align_to_frequency(timestamps: List[str], freq: str = "hourly") -> List[str]:
    """Align timestamps to uniform frequency grid."""
    seconds_per_period = {"hourly": 3600, "daily": 86400, "weekly": 604800}
    period_sec = seconds_per_period.get(freq, 3600)
    secs = [datetime_to_seconds(parse_datetime(ts)) for ts in timestamps]
    aligned = set(int(s // period_sec) * period_sec for s in secs)
    return [str(s) for s in sorted(aligned)]

def compute_rolling_zscores(values: List[float], window: int = 5) -> List[float]:
    """Compute rolling Z-scores for outlier detection."""
    n = len(values)
    zscores = [0.0] * n
    for i in range(n):
        start = max(0, i - window)
        window_vals = values[start:i+1]
        if len(window_vals) < 2:
            zscores[i] = 0.0
            continue
        mean = sum(window_vals) / len(window_vals)
        variance = sum((v - mean) ** 2 for v in window_vals) / len(window_vals)
        std = variance ** 0.5
        zscores[i] = (values[i] - mean) / std if std > 0 else 0.0
    return zscores

def detect_outliers_zscore(values: List[float], threshold: float = 2.0) -> List[int]:
    """Detect outlier indices using rolling Z-score method."""
    zscores = compute_rolling_zscores(values)
    return [i for i, z in enumerate(zscores) if abs(z) > threshold]

def detect_outliers_iqr(values: List[float], multiplier: float = 1.5) -> List[int]:
    """Detect outlier indices using IQR method."""
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    q1_idx = n // 4
    q3_idx = (3 * n) // 4
    q1 = sorted_vals[q1_idx]
    q3 = sorted_vals[q3_idx]
    iqr = q3 - q1
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr
    return [i for i, v in enumerate(values) if v < lower or v > upper]

def forward_fill(values: List[Optional[float]]) -> List[float]:
    """Forward-fill missing values (None/NaN becomes last valid value)."""
    result = []
    last_valid = 0.0
    for v in values:
        if v is None:
            result.append(last_valid)
        else:
            last_valid = v
            result.append(v)
    return result

def interpolate_missing(values: List[Optional[float]], freq_hours: int = 1) -> List[float]:
    """Linear interpolation for missing values."""
    n = len(values)
    result = list(values)
    last_valid = None
    for i in range(n):
        if values[i] is not None:
            last_valid = (i, values[i])
    for i in range(n):
        if values[i] is None and last_valid is not None:
            if i == 0:
                result[i] = last_valid[1]
            else:
                next_valid = None
                for j in range(i+1, n):
                    if values[j] is not None:
                        next_valid = (j, values[j])
                        break
                if next_valid is None:
                    result[i] = last_valid[1]
                else:
                    t = (i - last_valid[0]) / (next_valid[0] - last_valid[0])
                    result[i] = last_valid[1] + t * (next_valid[1] - last_valid[1])
        elif values[i] is not None:
            last_valid = (i, values[i])
    return [v for v in result]

def resample_series(timestamps: List[str], values: List[float], agg: str = "mean") -> List[float]:
    """Aggregate values to aligned timestamps."""
    agg_funcs = {
        "mean": lambda vals: sum(vals) / len(vals) if vals else 0.0,
        "sum": lambda vals: sum(vals),
        "max": lambda vals: max(vals) if vals else 0.0,
        "min": lambda vals: min(vals) if vals else 0.0
    }
    func = agg_funcs.get(agg, agg_funcs["mean"])
    aligned_ts = align_to_frequency(timestamps)
    result = []
    ts_idx = {ts: i for i, ts in enumerate(timestamps)}
    for at in aligned_ts:
        period_vals = []
        for ts, v in zip(timestamps, values):
            if ts.startswith(str(at)[:8]):
                period_vals.append(v)
        result.append(func(period_vals))
    return result

def preprocess_time_series(
    timestamps: List[str],
    values: List[float],
    freq: str = "hourly",
    outlier_method: str = "zscore",
    fill_method: str = "forward"
) -> Dict:
    """Complete preprocessing pipeline."""
    aligned = align_to_frequency(timestamps, freq)
    filled = interpolate_missing(values) if fill_method == "interpolate" else forward_fill(
        [v if v is not None else None for v in values]
    )
    if outlier_method == "zscore":
        outliers = detect_outliers_zscore(filled)
    else:
        outliers = detect_outliers_iqr(filled)
    return {
        "original_timestamps": timestamps,
        "aligned_timestamps": aligned,
        "original_values": values,
        "cleaned_values": filled,
        "outlier_indices": outliers
    }
```

### SQLite Time Series Storage

```sql
CREATE TABLE IF NOT EXISTS time_series_raw (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_name TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    value REAL,
    cleaned_value REAL,
    is_outlier INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS frequency_grids (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_name TEXT NOT NULL,
    frequency TEXT NOT NULL,
    aligned_timestamp TEXT UNIQUE,
    interpolated_value REAL
);

CREATE INDEX IF NOT EXISTS idx_series_time ON time_series_raw(series_name, timestamp);
CREATE INDEX IF NOT EXISTS idx_outliers ON time_series_raw(is_outlier) WHERE is_outlier = 1;

INSERT INTO time_series_raw (series_name, timestamp, value, cleaned_value, is_outlier)
VALUES (?, ?, ?, ?, ?);

INSERT OR REPLACE INTO frequency_grids (series_name, frequency, aligned_timestamp, interpolated_value)
VALUES (?, ?, ?, ?);

UPDATE time_series_raw SET cleaned_value = ? WHERE is_outlier = 1 AND series_name = ?;

SELECT ts.timestamp, ts.value, fg.interpolated_value 
FROM time_series_raw ts
LEFT JOIN frequency_grids fg 
    ON ts.series_name = fg.series_name AND ts.timestamp = fg.aligned_timestamp
WHERE ts.series_name = ?
ORDER BY ts.timestamp;
```

## Testing

```python
def test_align_to_frequency():
    ts = ["2024-01-01 00:00:00", "2024-01-01 01:30:00", "2024-01-01 02:15:00"]
    aligned = align_to_frequency(ts, "hourly")
    assert len(aligned) == 3

def test_outlier_detection():
    values = [0.1, 0.1, 0.12, 0.11, 1.5]
    outliers = detect_outliers_zscore(values, threshold=2.0)
    assert len(outliers) > 0

def test_forward_fill():
    values = [1.0, None, None, 4.0, 5.0]
    filled = forward_fill(values)
    assert filled[1] == 1.0
    assert filled[2] == 1.0
```

## Security Considerations

- No external data sources
- Pure numerical operations on in-memory data
- SQLite for isolated storage