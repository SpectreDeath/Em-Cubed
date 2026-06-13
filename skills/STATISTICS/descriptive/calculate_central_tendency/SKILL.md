---
name: calculate_central_tendency
domain: STATISTICS
version: "1.0.0"
surfaces: [python]
description: |
  Algorithmic execution skill computing mean, median, and mode
  from a numeric vector.  Results are appended to agent working
  memory or state for downstream consumption.
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

# Calculate Central Tendency

## Purpose
Compute the three canonical measures of central tendency — mean, median, and mode — from a cleaned numeric vector, then record results to agent state.

## Description
Pure algorithmic skill. No symbolic preconditions are enforced beyond a measurement-level check passed in from the guardrail layer. The skill handles:
- Vector cleaning (drops `None`, `NaN`, and non-numeric entries)
- Mean: arithmetic average
- Median: mid-value after sorting (parity-corrected)
- Mode: most frequent value(s); flags multimodal distributions
- Empty-after-cleaning guard

## Python Surface (executor.py)

```python
"""
calculate_central_tendency
=============================
Algorithmic skill: compute mean, median, and mode.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union


@dataclass(frozen=True)
class CentralTendencyResult:
    measure: str
    mean: float
    median: float
    mode: Union[float, List[float]]
    multimodal: bool
    n: int
    n_original: int
    n_dropped: int

    def to_dict(self) -> dict:
        return {
            "measure":      self.measure,
            "mean":         self.mean,
            "median":       self.median,
            "mode":         self.mode,
            "multimodal":   self.multimodal,
            "n":            self.n,
            "n_original":   self.n_original,
            "n_dropped":    self.n_dropped,
        }


def _clean(values: List[Union[float, int, None, str]]) -> List[float]:
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


def calculate_central_tendency(
    values: List[Union[float, int, None, str]],
    dataset_id: Optional[str] = None,
) -> CentralTendencyResult:
    """Compute mean, median, and mode from a numeric vector.

    Parameters
    ----------
    values : list
        Raw input vector.  Non-numeric and NaN entries are silently dropped.
    dataset_id : str, optional
        Logical identifier used when writing to agent state.

    Returns
    -------
    CentralTendencyResult
        Dataclass carrying all computed quantities.

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

    # Mean
    mean: float = sum(s) / n

    # Median (parity-corrected)
    if n % 2 == 1:
        median: float = s[n // 2]
    else:
        median = (s[n // 2 - 1] + s[n // 2]) / 2.0

    # Mode
    counts = Counter(s)
    max_count = max(counts.values())
    modes = sorted([k for k, v in counts.items() if v == max_count])
    multimodal: bool = len(modes) > 1

    return CentralTendencyResult(
        measure     = "central_tendency",
        mean        = mean,
        median      = median,
        mode        = modes if multimodal else modes[0],
        multimodal  = multimodal,
        n           = n,
        n_original  = n_original,
        n_dropped   = dropped,
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
| mean | float | Arithmetic average |
| median | float | Mid-value after sorting |
| mode | float or list[float] | Most frequent value(s); list if multimodal |
| multimodal | bool | True if more than one value ties for highest frequency |
| n | int | Count of valid (non-missing) values used |
| n_original | int | Original vector length before cleaning |
| n_dropped | int | Count of dropped entries |

## State Updates
On success, the orchestration layer should store:
```
state_add_observation("descriptive/mean",     result.mean)
state_add_observation("descriptive/median",   result.median)
state_add_observation("descriptive/mode",     result.mode)
state_add_observation("descriptive/n",        result.n)
state_add_observation("descriptive/multimodal", result.multimodal)
```

## Error Handling
| Error | Condition | Behavior |
|---|---|---|
| empty_series | n == 0 after cleaning | Raise ValueError; do not record partial results |

## Example Usage
```python
values = [1, 2, 2, 3, 4, None, float('nan'), 5]
result = calculate_central_tendency(values)
# result.mean    == 2.7142857142857144
# result.median  == 2.5
# result.mode    == 2.0        (single mode)
# result.multimodal == False
# result.n       == 6
# result.n_dropped == 2

bimodal = [1, 1, 2, 2, 3]
r2 = calculate_central_tendency(bimodal)
# r2.mode        == [1.0, 2.0]
# r2.multimodal  == True
```

## Security Considerations
- No I/O, no network, no subprocess execution.
- All computation is in-memory on the user-supplied vector.
- No secrets or credentials involved.
