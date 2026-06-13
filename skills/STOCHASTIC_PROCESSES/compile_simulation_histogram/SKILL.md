---
name: compile_simulation_histogram
domain: STOCHASTIC_PROCESSES
version: "1.0.0"
surfaces: [python, prolog]
description: |
  Aggregates multiple Monte Carlo walk paths into frequency histograms
  and computes empirical stationary distributions.  Prolog validates
  histogram bin constraints; Python performs the aggregation.
compatibility: PYTHON, PROLOG
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

# Compile Simulation Histogram

## Purpose
Collect multiple independent Monte Carlo walk trajectories and aggregate them into state visit-frequency counts, empirical stationary distributions, and first-passage time statistics. This is the direct statistical bridge between the Veritasium Monte Carlo method and the M³ agent's working-memory beliefs.

## Description
Hybrid skill:
- **Python layer** — Accepts a list of `WalkResult` objects (or raw path lists), computes per-state visit counts, total path lengths, normalized visit frequencies (empirical stationary distribution), and first-passage time statistics.
- **Prolog layer** — Enforces that each state's frequency is a non-negative integer, totals match expected sample count, and distribution sums to the total number of steps (or visits).

### Verification Theorem (empirical)
If the MC is ergodic and we run N independent walks of T steps each:
- The empirical frequency `f_i = visits_i / (N·T)` converges to `π_i` (stationary distribution) as `N·T → ∞`.
- The histogram approximates `π`.

## Prolog Surface (prelude.pl)

```prolog
:- module(simulation_histogram, [
    non_negative_count/1,
    histogram_valid/2,
    distribution_sums_to/2
]).

% ============================================================
% 1. Non-negative frequency counts
% ============================================================
non_negative_count(Count) :- Count >= 0, integer(Count).

% ============================================================
% 2. Full histogram validation
% ============================================================
histogram_valid(States, Counts) :-
    same_length(States, Counts),
    forall(member(C, Counts), non_negative_count(C)).

% ============================================================
% 3. Total visit count
% ============================================================
distribution_sums_to(Counts, Total) :-
    sum_list(Counts, Total).
```

## Python Surface (executor.py)

```python
"""
compile_simulation_histogram
===============================
Aggregate Monte Carlo walk histories into empirical probability distributions.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union


@dataclass(frozen=True)
class HistogramResult:
    states: Tuple[str, ...]
    visit_counts: Tuple[int, ...]
    total_visits: int
    empirical_distribution: Tuple[float, ...]
    path_count: int
    total_steps: int
    mean_path_length: float
    std_path_length: float
    first_passage_times: Dict[str, Optional[int]]
    chi_square_convergence: float  # ||freq - uniform||_1 for uniform baseline

    def to_dict(self) -> dict:
        return {
            "states":                   list(self.states),
            "visit_counts":             list(self.visit_counts),
            "total_visits":             self.total_visits,
            "empirical_distribution":   list(self.empirical_distribution),
            "path_count":               self.path_count,
            "total_steps":              self.total_steps,
            "mean_path_length":         self.mean_path_length,
            "std_path_length":          self.std_path_length,
            "first_passage_times":      dict(self.first_passage_times),
            "chi_square_convergence":   self.chi_square_convergence,
        }


def compile_simulation_histogram(
    paths: List[List[str]],
    states: Optional[List[str]] = None,
    target_state: Optional[str] = None,
) -> HistogramResult:
    """Aggregate multiple walk paths into visit frequency and distribution statistics.

    Parameters
    ----------
    paths : list[list[str]]
        List of state-sequence paths from Monte Carlo walks.
    states : list[str] or None
        Full state universe.  If None, inferred from union of all paths.
    target_state : str or None
        If provided, compute first-passage time to this state from each path.

    Returns
    -------
    HistogramResult

    Raises
    ------
    ValueError
        paths is empty.
    """
    if not paths:
        raise ValueError("paths must be non-empty")

    if states is None:
        seen: set = set()
        for p in paths:
            seen.update(p)
        states = sorted(seen)

    state_set = list(states)
    idx = {s: i for i, s in enumerate(state_set)}
    n = len(state_set)

    counts = [0] * n
    path_lengths = []
    first_passage: Dict[str, Optional[int]] = {s: None for s in state_set}

    for path in paths:
        if not path:
            continue
        path_lengths.append(len(path))
        for t, s in enumerate(path):
            if s in idx:
                counts[idx[s]] += 1
        if target_state is not None:
            for t, s in enumerate(path):
                if s == target_state:
                    if first_passage[target_state] is None:
                        first_passage[target_state] = t
                    break

    total = sum(counts)
    dist = [c / total if total > 0 else 0.0 for c in counts]

    mean_len = sum(path_lengths) / len(path_lengths) if path_lengths else 0.0
    if len(path_lengths) > 1:
        var_len = sum((l - mean_len) ** 2 for l in path_lengths) / (len(path_lengths) - 1)
        std_len = math.sqrt(var_len)
    else:
        std_len = 0.0

    # Convergence proxy: L1 distance from uniform distribution
    uniform = [1.0 / n] * n if n > 0 else []
    l1 = sum(abs(d - u) for d, u in zip(dist, uniform))

    return HistogramResult(
        states                 = tuple(state_set),
        visit_counts           = tuple(counts),
        total_visits           = total,
        empirical_distribution = tuple(dist),
        path_count             = len(paths),
        total_steps            = sum(path_lengths),
        mean_path_length       = mean_len,
        std_path_length        = std_len,
        first_passage_times    = first_passage,
        chi_square_convergence = l1,
    )
```

## Inputs

| name | type | description |
|---|---|---|
| paths | list[list[str]] | Walk result paths (each is a state sequence) |
| states | list[str] or None | State universe; auto-inferred if None |
| target_state | str or None | Compute first-passage time for this specific state |

## Outputs

| name | type | description |
|---|---|---|
| states | tuple[str] | Sorted state universe |
| visit_counts | tuple[int] | Total visits per state (sum = total_visits) |
| total_visits | int | Total state visits across all paths |
| empirical_distribution | tuple[float] | Normalized visit frequencies |
| mean_path_length | float | Average path length |
| std_path_length | float | Std dev of path lengths |
| path_count | int | Number of paths aggregated |
| first_passage_times | dict[str → int or None] | First appearance step per target |
| chi_square_convergence | float | L1 distance from uniform (lower = closer to uniform) |

## Error Handling
| Error | Condition |
|---|---|
| empty_paths | No paths provided |

## Security
- No I/O. In-memory aggregation only.
