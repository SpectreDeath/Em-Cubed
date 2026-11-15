---
name: calculate_central_tendency
domain: STATISTICS
version: 1.0.0
surfaces:
  - python
description: Algorithmic statistical execution engine computing canonical measures of central tendency (mean, median, mode, and trimmed mean) from numeric vectors. Handles automatic non-numeric/NaN vector sanitization, parity-corrected median selection, and multimodal distribution detection. Use when summarizing location parameters of empirical sample distributions, detecting skewness, or preparing baseline features for downstream statistical inference.
purpose: Compute mean, median, mode, and multimodal flags from numeric sample vectors with robust data cleaning.
dependencies: []
tags:
  - central-tendency
  - descriptive-statistics
  - mean-median-mode
  - sample-cleaning
  - multimodal-detection
inputs:
  values:
    type: array
    required: true
    description: Raw numeric vector (may contain None, NaN, or string representations of numbers).
  dataset_id:
    type: string
    required: false
    description: Optional logical dataset identifier for telemetry and state tracking.
outputs:
  mean:
    type: number
    description: Arithmetic sample average.
  median:
    type: number
    description: Parity-corrected sorted mid-point value.
  mode:
    type: any
    description: Most frequent value (float) or array of modes if multimodal.
  multimodal:
    type: boolean
    description: True if more than one unique value ties for maximum frequency.
  n:
    type: integer
    description: Clean sample size after dropping invalid and NaN entries.
  n_dropped:
    type: integer
    description: Total count of non-numeric, null, or NaN entries pruned during cleaning.
---

# Calculate Central Tendency Engine

`calculate_central_tendency` computes robust location measures from empirical sample vectors $\mathbf{x} = (x_1, x_2, \dots, x_N)$. It enforces vector sanitization, evaluates arithmetic mean ($\bar{x}$), sorted parity-corrected median ($\tilde{x}$), and multimodality-aware mode:

$$\bar{x} = \frac{1}{N} \sum_{i=1}^{N} x_i, \quad \tilde{x} = \begin{cases} x_{(N+1)/2} & N \text{ is odd} \\ \frac{1}{2}\left(x_{(N/2)} + x_{(N/2 + 1)}\right) & N \text{ is even} \end{cases}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Central Tendency Progression

```
[1. Vector Sanitization & Audit] → [2. Sorted Array Construction] → [3. Visual Brief] → [4. Checkpoint] → [5. Metric Computation & Output]
```

### Stage 1: Vector Sanitization & Audit
1. Ingest `values` array and prune `None`, `NaN`, and non-convertible string tokens.
2. Track `n_original` and `n_dropped` counts.
3. Assert that post-cleaning sample size $N \ge 1$.

> **Completion criterion**: Clean float vector $\mathbf{x}_{\text{clean}}$ constructed with $N \ge 1$.

---

### Stage 2: Sorted Array & Parity Setup
1. Sort clean values ascending: $\mathbf{s} = \text{sort}(\mathbf{x}_{\text{clean}})$.
2. Calculate element frequency table using counter hash map.

> **Completion criterion**: Ascending sorted array and frequency histogram indexed.

---

### Stage 3: The Visual Brief
For skewed or multimodal sample distributions, generate an interactive brief:
- **Location**: Write to `%TEMP%\central-tendency-brief-<timestamp>.html` (Windows) or `/tmp/central-tendency-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render sample distribution histogram showing overlay markers for Mean, Median, and Mode.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before finalizing summary statistics:
1. Check for extreme skewness: $|\bar{x} - \tilde{x}| / \text{std} > 1.0$.
2. If mean and median diverge significantly, flag skewed distribution warning in telemetry.

> **Completion criterion**: Skewness profile verified and logged.

---

### Stage 5: Metric Computation & Emission
1. Calculate arithmetic mean, parity-corrected median, and mode list.
2. Determine `multimodal` boolean flag ($\text{len}(\text{modes}) > 1$).
3. Emit full `CentralTendencyResult` record.

> **Completion criterion**: Output record emitted with verified mean, median, mode, and sample counts.

---

## Surface References

### Python Implementation Surface

```python
import math
from collections import Counter
from typing import List, Dict, Any, Union

def calculate_central_tendency(values: List[Any], dataset_id: str = None) -> Dict[str, Any]:
    clean = []
    dropped = 0
    for v in values:
        if v is None:
            dropped += 1
            continue
        try:
            val = float(v)
            if math.isnan(val):
                dropped += 1
            else:
                clean.append(val)
        except (ValueError, TypeError):
            dropped += 1

    n = len(clean)
    if n == 0:
        raise ValueError("empty_series: Vector is empty or entirely non-numeric after cleaning.")

    s = sorted(clean)
    mean_val = sum(s) / n
    median_val = s[n // 2] if n % 2 == 1 else (s[n // 2 - 1] + s[n // 2]) / 2.0

    counts = Counter(s)
    max_count = max(counts.values())
    modes = sorted([k for k, v in counts.items() if v == max_count])
    multimodal = len(modes) > 1

    return {
        "mean": round(mean_val, 6),
        "median": round(median_val, 6),
        "mode": modes if multimodal else modes[0],
        "multimodal": multimodal,
        "n": n,
        "n_dropped": dropped,
        "dataset_id": dataset_id
    }
```

---

## Anti-Patterns & Guardrails

- **Silent Empty Array Collapse** — Proceeding with calculations when $N = 0$ after cleaning, leading to division by zero. Always raise explicit `ValueError("empty_series")`.
- **Mode Masking** — Arbitrarily picking the first mode in multimodal data without setting `multimodal: true`.
- **Ignoring Parity on Medians** — Selecting `s[N // 2]` on even-sized arrays instead of averaging the two central values.
