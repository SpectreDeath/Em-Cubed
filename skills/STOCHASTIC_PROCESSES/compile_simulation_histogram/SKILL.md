---
name: compile_simulation_histogram
domain: STOCHASTIC_PROCESSES
version: 1.0.0
surfaces:
  - python
  - prolog
description: Monte Carlo simulation aggregation engine compiling multiple random walk path trajectories into empirical state visit frequency histograms, empirical stationary distributions, first-passage times, and L1 convergence metrics. Enforces non-negative integer count invariants and total visit sum constraints in Prolog, and computes path length statistics and empirical distribution vectors in Python. Use when estimating empirical stationary distributions from simulated trajectories, evaluating first-passage hitting times, or comparing empirical Monte Carlo distributions against theoretical priors.
purpose: Aggregate Monte Carlo walk paths into empirical frequency distributions and first-passage time statistics.
dependencies:
  - STOCHASTIC_PROCESSES/generate_transition_matrix
  - STOCHASTIC_PROCESSES/execute_monte_carlo_walk
tags:
  - simulation-histogram
  - empirical-distribution
  - first-passage-time
  - monte-carlo-aggregation
  - stationary-distribution
  - prolog-validation
inputs:
  paths:
    type: array
    required: true
    description: List of state sequence trajectory paths `[['s1', 's2', ...], ...]`.
  states:
    type: array
    required: false
    description: Optional state universe labels (auto-inferred from union of paths if omitted).
  target_state:
    type: string
    required: false
    description: Optional target state label for first-passage hitting time estimation.
outputs:
  states:
    type: array
    description: Ordered state label universe.
  visit_counts:
    type: array
    description: Total visit counts per state across all simulation paths.
  total_visits:
    type: integer
    description: Total state visits across all paths ($\sum \text{counts}$).
  empirical_distribution:
    type: array
    description: Empirical probability distribution vector $f_i = \text{counts}_i / \text{total\_visits}$.
  path_count:
    type: integer
    description: Number of simulation paths aggregated.
  total_steps:
    type: integer
    description: Total transition steps across all paths.
  mean_path_length:
    type: number
    description: Average length of simulation paths.
  std_path_length:
    type: number
    description: Standard deviation of simulation path lengths.
  first_passage_times:
    type: object
    description: Earliest step index when target state was first reached.
  chi_square_convergence:
    type: number
    description: $L_1$ total variation distance from uniform distribution.
---

# Compile Simulation Histogram Engine

`compile_simulation_histogram` aggregates independent Monte Carlo walk trajectories into empirical state occupancy frequencies and estimates the **empirical stationary distribution** $\mathbf{f} \to \boldsymbol{\pi}$. It validates **count non-negativity in Prolog** and evaluates path statistics, **first-passage times**, and convergence metrics in **Python**:

$$f_i = \frac{\sum_{m=1}^M \sum_{t=0}^{T_m} \mathbb{I}(s_t^{(m)} = i)}{\sum_{i=1}^R \text{Visits}_i} \xrightarrow{M \cdot T \to \infty} \pi_i$$

$$\tau_{\text{target}} = \min \{ t \ge 0 \mid s_t = \text{target} \}, \quad L_1 = \sum_{i=1}^R \left| f_i - \frac{1}{R} \right|$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Histogram Compilation Progression

```
[1. Path Trajectory Invariant Audit] → [2. State Frequency Tally & Passage Analysis] → [3. Visual Brief] → [4. Checkpoint] → [5. Distribution Normalization & Emit]
```

### Stage 1: Path Trajectory Invariant Audit
1. Ingest `paths` array containing $M \ge 1$ state trajectories.
2. Ingest or infer state universe $\mathcal{S} = \bigcup_{m,t} s_t^{(m)}$.
3. Verify that paths contain non-empty state sequences.

> **Completion criterion**: Clean path collection verified with $M \ge 1$ trajectories.

---

### Stage 2: State Frequency Tally & First-Passage Analysis
1. Count state visits across all path steps into frequency vector $\mathbf{c} \in \mathbb{N}^R$.
2. For each path, record first-passage hitting step $\tau = \min \{t \mid s_t = s_{\text{target}}\}$.
3. Compute trajectory length mean $\mu_L$ and sample standard deviation $\sigma_L$.

> **Completion criterion**: State visit counts and first-passage times evaluated.

---

### Stage 3: The Visual Brief
For empirical distribution and hitting time analysis, generate an interactive brief:
- **Location**: Write to `%TEMP%\simulation-histogram-brief-<timestamp>.html` (Windows) or `/tmp/simulation-histogram-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render empirical state frequency bar histogram, first-passage time survival curve, and path length distribution box plot.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before finalizing output distribution:
1. Verify Prolog non-negative integer count invariant:
   ```prolog
   histogram_valid(States, Counts) :- same_length(States, Counts), forall(member(C, Counts), (C >= 0, integer(C))).
   ```
2. Verify total sum: $\sum c_i = \text{total\_visits}$.

> **Completion criterion**: Non-negativity and integer count invariants certified in Prolog.

---

### Stage 5: Distribution Normalization & Output Emission
1. Calculate normalized empirical distribution $f_i = c_i / \text{total\_visits}$.
2. Compute $L_1$ total variation distance against uniform benchmark.
3. Emit complete `HistogramResult` record.

> **Completion criterion**: Complete histogram compilation payload emitted.

---

## Surface References

### Prolog Validation Surface

```prolog
:- module(simulation_histogram, [
    non_negative_count/1,
    histogram_valid/2,
    distribution_sums_to/2
]).

non_negative_count(Count) :- Count >= 0, integer(Count).

histogram_valid(States, Counts) :-
    length(States, N),
    length(Counts, N),
    forall(member(C, Counts), non_negative_count(C)).

distribution_sums_to(Counts, Total) :-
    sum_list(Counts, Total).
```

### Python Calculation Surface

```python
import math
from typing import List, Dict, Any, Optional

def compile_simulation_histogram(
    paths: List[List[str]],
    states: Optional[List[str]] = None,
    target_state: Optional[str] = None
) -> Dict[str, Any]:
    if not paths:
        raise ValueError("empty_paths: Requires at least 1 path trajectory.")
        
    if states is None:
        seen = set()
        for p in paths: seen.update(p)
        state_list = sorted(seen)
    else:
        state_list = states
        
    n = len(state_list)
    state_to_idx = {s: i for i, s in enumerate(state_list)}
    
    counts = [0] * n
    path_lengths = []
    first_passage = {s: None for s in state_list}
    
    for path in paths:
        if not path: continue
        path_lengths.append(len(path))
        for t, s in enumerate(path):
            if s in state_to_idx:
                counts[state_to_idx[s]] += 1
                
        if target_state is not None:
            for t, s in enumerate(path):
                if s == target_state:
                    if first_passage[target_state] is None or t < first_passage[target_state]:
                        first_passage[target_state] = t
                    break
                    
    total = sum(counts)
    dist = [round(c / total, 6) if total > 0 else 0.0 for c in counts]
    
    mean_len = sum(path_lengths) / len(path_lengths) if path_lengths else 0.0
    if len(path_lengths) > 1:
        var_len = sum((l - mean_len) ** 2 for l in path_lengths) / (len(path_lengths) - 1)
        std_len = math.sqrt(var_len)
    else:
        std_len = 0.0
        
    uniform = [1.0 / n] * n if n > 0 else []
    l1 = sum(abs(d - u) for d, u in zip(dist, uniform))
    
    return {
        "states": state_list,
        "visit_counts": counts,
        "total_visits": total,
        "empirical_distribution": dist,
        "path_count": len(paths),
        "total_steps": sum(path_lengths),
        "mean_path_length": round(mean_len, 4),
        "std_path_length": round(std_len, 4),
        "first_passage_times": first_passage,
        "chi_square_convergence": round(l1, 6)
    }
```

---

## Anti-Patterns & Guardrails

- **Empty Path List** — Calling histogram compilation with empty path arrays, resulting in zero total visits.
- **Ignoring Unvisited States** — Omitting unvisited states from the state universe, yielding incomplete distribution dimensionality.
- **Conflating Transition Steps with Visit Counts** — Failing to count the initial state ($t=0$), causing total visit counts to equal $N_{\text{steps}}$ instead of $N_{\text{steps}} + 1$.
