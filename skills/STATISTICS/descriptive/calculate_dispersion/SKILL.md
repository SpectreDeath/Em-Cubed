---
name: calculate_dispersion
domain: STATISTICS
version: "1.0.0"
surfaces: [python]
description: |
  Algorithmic skill computing range, variance, standard deviation,
  and interquartile range from a numeric vector.  Used for
  distributional diagnostics and downstream standard-error
  derivation (e.g., confidence intervals).
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

# Calculate Dispersion

## Purpose
Quantify the spread of a numeric distribution using range, variance, standard deviation, and interquartile range. Supports both sample and population variance formulations.

## Description
Pure algorithmic skill. Results are appended to agent state. Complements `calculate_central_tendency` and provides inputs for `calculate_mean_confidence_interval` (which requires `s`, the sample standard deviation).

### Measures Computed
- **Range**: max - min
- **Variance**: mean((x - mean(x))^2) with explicit `ddof` flag
  - `ddof=0` → population variance (divides by n)
  - `ddof=1` → sample variance (divides by n-1)
- **Standard Deviation**: sqrt(variance), matching the `ddof` selection
- **IQR**: 75th percentile - 25th percentile (linear interpolation)

## Python Surface (executor.py)

```python
"""
calculate_dispersion
======================
Algorithmic skill: compute range, variance, std, and IQR.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union


@dataclass(frozen=True)
class DispersionResult:
    measure: str
    range: float
    variance: float      # population variance by default (ddof=0)
    variance_sample: float  # sample variance (ddof=1)
    std: float           # population std (ddof=0)
    std_sample: float    # sample std (ddof=1)
    iqr: float
    n: int
    n_original: int
    n_dropped: int

    def to_dict(self) -> dict:
        return {
            "measure":       self.measure,
            "range":         self.range,
            "variance":      self.variance,
            "variance_sample": self.variance_sample,
            "std":           self.std,
            "std_sample":    self.std_sample,
            "iqr":           self.iqr,
            "n":             self.n,
            "n_original":    self.n_original,
            "n_dropped":     self.n_dropped,
        }


def _clean(values: List[Union[float, int, None, str]]) -> Tuple[List[float], int]:
    out: List[float] = []
    dropped = 0
    for v in values:
        if v is None:
            dropped += 1
            continue
        if isinstance(v, str):
            try:
                v = float(v)
            except (ValueError, TypeError):
                dropped += 1
                continue
        if isinstance(v, float) and math.isnan(v):
            dropped += 1
            continue
        out.append(float(v))
    return out, dropped


def _percentile(sorted_values: List[float], pct: float) -> float:
    """Linear interpolation percentile (matching numpy default)."""
    n = len(sorted_values)
    if n == 0:
        raise ValueError("empty_series")
    if n == 1:
        return sorted_values[0]
    # rank = pct/100 * (n-1)  (0-indexed)
    rank = (pct / 100.0) * (n - 1)
    lower = int(math.floor(rank))
    upper = int(math.ceil(rank))
    if lower == upper:
        return sorted_values[lower]
    frac = rank - lower
    return sorted_values[lower] * (1 - frac) + sorted_values[upper] * frac


def calculate_dispersion(
    values: List[Union[float, int, None, str]],
    dataset_id: Optional[str] = None,
) -> DispersionResult:
    """Compute range, variance (population and sample), std, and IQR.

    Parameters
    ----------
    values : list
        Raw input vector.  Non-numeric and NaN entries are silently dropped.
    dataset_id : str, optional
        Logical identifier used when writing to agent state.

    Returns
    -------
    DispersionResult
        Dataclass carrying all dispersion measures.

    Raises
    ------
    ValueError
        If the vector is empty or entirely non-numeric after cleaning.
    """
    clean, dropped = _clean(values)
    n = len(clean)
    n_original = len(values)

    if n == 0:
        raise ValueError(
            "empty_series: vector is empty or entirely non-numeric after cleaning"
        )

    s = sorted(clean)

    # Range
    range_val: float = s[-1] - s[0]

    # Variance (population and sample)
    mean_val = sum(s) / n
    sum_sq_diff = sum((v - mean_val) ** 2 for v in s)
    variance_pop = sum_sq_diff / n          # ddof=0
    variance_samp = sum_sq_diff / (n - 1)   # ddof=1

    # Standard deviation
    std_pop = math.sqrt(variance_pop)
    std_samp = math.sqrt(variance_samp)

    # IQR
    q75 = _percentile(s, 75.0)
    q25 = _percentile(s, 25.0)
    iqr = q75 - q25

    return DispersionResult(
        measure        = "dispersion",
        range          = range_val,
        variance       = variance_pop,
        variance_sample= variance_samp,
        std            = std_pop,
        std_sample     = std_samp,
        iqr            = iqr,
        n              = n,
        n_original     = n_original,
        n_dropped      = dropped,
    )
```

## Inputs

| name | type | description |
|---|---|---|
| values | list[float\|int\|None\|str] | Raw sample vector; non-numeric entries are silently dropped |
| dataset_id | str, optional | Logical identifier for state tagging |

## Outputs

| name | type | description |
|---|---|---|
| range | float | max - min |
| variance | float | Population variance (ddof=0) |
| variance_sample | float | Sample variance (ddof=1) |
| std | float | Population standard deviation |
| std_sample | float | Sample standard deviation (used for CI formula) |
| iqr | float | 75th - 25th percentile |
| n | int | Valid count after cleaning |

## State Updates
```
state_add_observation("descriptive/range",          result.range)
state_add_observation("descriptive/variance",       result.variance)
state_add_observation("descriptive/variance_sample",result.variance_sample)
state_add_observation("descriptive/std",            result.std)
state_add_observation("descriptive/std_sample",     result.std_sample)
state_add_observation("descriptive/iqr",            result.iqr)
```

## Error Handling
| Error | Condition | Behavior |
|---|---|---|
| empty_series | n == 0 after cleaning | Raise ValueError |

## Example Usage
```python
values = [10, 12, 23, 23, 16, 23, 21, 16]
result = calculate_dispersion(values)
# result.range         == 13.0
# result.variance      == 18.0625
# result.variance_sample == 20.64285714285714
# result.std           == 4.2504...
# result.std_sample    == 4.5424...
# result.iqr           == 6.5  (Q3=23, Q1=16.5)
```

## Security Considerations
- Pure in-memory computation. No I/O, no network, no subprocess execution.
