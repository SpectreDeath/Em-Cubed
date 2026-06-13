---
name: execute_monte_carlo_walk
domain: STOCHASTIC_PROCESSES
version: "1.0.0"
surfaces: [python]
description: |
  Executes a weighted random walk over a transition matrix for a
  configurable number of steps.  Supports dynamic transition-probability
  injection from agent working memory at each step via a context-callback
  hook, enabling environmental state modulation during simulation.
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

# Execute Monte Carlo Walk

## Purpose
Simulate a path through a Markov chain by sampling state transitions from the transition matrix. Designed for agent-state traversal where the chain can be influenced by environmental variables (agent memory, context gate signals) at each simulation step.

## Connection to Veritasium Concepts
- **Monte Carlo neutron simulation** (Fermi, von Neumann, Ulam): random walk through state space approximating the solution to a problem.
- **Andrei Markov's vowel-consonant chains**: text as a state sequence sourced from probability, not deterministic rules.
- **Agent traversal**: each walk step corresponds to an M³ agent choosing its next action with probability dictated by the chain, modulating behavior based on memory state.

## Description
Pure algorithmic skill. At each step:
1. Read current state.
2. Consult the transition matrix (optionally perturbed by a `context_callback` that reads from agent memory).
3. Sample next state via cumulative-probability inversion (inverse transform sampling).
4. Record transition in the chain history.
5. Repeat until `n_steps` exhausted.

The `context_callback` signature is:
```python
context_callback(step_index, current_state, history) -> dict or None
```
If the callback returns `{"matrix_override": new_matrix}` or `{"state_boost": {state: delta}}`, those modifications are merged into the transition matrix before the step proceeds — modeling how environmental feedback shifts probabilities.

## Python Surface (executor.py)

```python
"""
execute_monte_carlo_walk
=========================
Stochastic random walk simulator with dynamic context injection.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple, Union


@dataclass(frozen=True)
class WalkResult:
    path: Tuple[str, ...]
    transition_log: Tuple[Tuple[int, str, str, float], ...]
    final_state: str
    steps_taken: int
    absorbing_step: Optional[int]
    state_visit_counts: Dict[str, int]
    seed: Optional[int]

    def to_dict(self) -> dict:
        return {
            "path":              list(self.path),
            "transition_log":    [list(t) for t in self.transition_log],
            "final_state":       self.final_state,
            "steps_taken":       self.steps_taken,
            "absorbing_step":    self.absorbing_step,
            "state_visit_counts": dict(self.state_visit_counts),
            "seed":              self.seed,
        }


def _sample_next(
    state: str,
    state_to_idx: Dict[str, int],
    matrix: List[List[float]],
    rng: random.Random,
) -> str:
    """Inverse-transform sampling: map uniform(0,1) to next state."""
    idx = state_to_idx[state]
    row = matrix[idx]
    u = rng.random()
    cumsum = 0.0
    for j, p in enumerate(row):
        cumsum += p
        if u <= cumsum:
            return list(state_to_idx.keys())[j]
    # Floating-point fallback: return last state
    return list(state_to_idx.keys())[-1]


def execute_monte_carlo_walk(
    matrix: List[List[float]],
    states: List[str],
    start_state: str,
    n_steps: int,
    seed: Optional[int] = None,
    context_callback: Optional[
        Callable[[int, str, List[str]], Optional[Dict]]
    ] = None,
    absorbing_threshold: float = 0.99,
) -> WalkResult:
    """Execute a Monte Carlo random walk through a Markov chain.

    Parameters
    ----------
    matrix : list[list[float]]
        R×R row-stochastic transition matrix.
    states : list of str
        State label vector (order matches matrix rows/cols).
    start_state : str
        Initial state label.
    n_steps : int
        Maximum number of transitions to simulate.
    seed : int or None
        RNG seed for reproducibility.  None → non-deterministic.
    context_callback : callable or None
        Called each step before transition: callback(step_index, current_state, history)
        Returns dict with optional keys:
          - "matrix_override": full R×R replacement matrix
          - "state_boost":  {state_label: additive_delta to row}
        If the callback mutates the matrix, the returned dict is applied
        before sampling.  Returning None leaves the matrix unchanged.
    absorbing_threshold : float
        P[i][i] ≥ this threshold for state i to be treated as absorbing.

    Returns
    -------
    WalkResult

    Raises
    ------
    ValueError
        start_state not in states, n_steps < 1, or matrix not row-stochastic.
    """
    if start_state not in states:
        raise ValueError(f"start_state '{start_state}' not in states: {states}")
    if n_steps < 1:
        raise ValueError(f"n_steps must be >= 1, got {n_steps}")
    n = len(states)
    if len(matrix) != n:
        raise ValueError(f"matrix rows ({len(matrix)}) != n_states ({n})")
    for i, row in enumerate(matrix):
        if len(row) != n:
            raise ValueError(f"matrix row {i} has {len(row)} cols, expected {n}")
        s = sum(row)
        if abs(s - 1.0) > 1e-6:
            raise ValueError(f"row {i} sum={s}, not row-stochastic")

    rng = random.Random(seed)
    state_to_idx = {s: i for i, s in enumerate(states)}

    path: List[str] = [start_state]
    history: List[str] = [start_state]
    transition_log: List[Tuple[int, str, str, float]] = []
    visit_counts: Dict[str, int] = {s: 0 for s in states}
    visit_counts[start_state] = 1

    absorbing_step: Optional[int] = None
    cur = start_state

    for step in range(n_steps):
        # Dynamic context injection from agent memory
        active_matrix = [row[:] for row in matrix]
        if context_callback is not None:
            override = context_callback(step, cur, history)
            if override:
                if "matrix_override" in override:
                    active_matrix = override["matrix_override"]
                if "state_boost" in override:
                    boost = override["state_boost"]
                    idx = state_to_idx[cur]
                    for s_label, delta in boost.items():
                        if s_label in state_to_idx:
                            j = state_to_idx[s_label]
                            active_matrix[idx][j] += delta
                    # Re-normalize row
                    row_sum = sum(active_matrix[idx])
                    if row_sum > 0:
                        active_matrix[idx] = [
                            p / row_sum for p in active_matrix[idx]
                        ]

        # Absorbing check
        cur_idx = state_to_idx[cur]
        if active_matrix[cur_idx][cur_idx] >= absorbing_threshold:
            absorbing_step = step
            break

        next_state = _sample_next(cur, state_to_idx, active_matrix, rng)

        # Probability of the transition actually taken (log for analysis)
        trans_prob = active_matrix[cur_idx][state_to_idx[next_state]]

        transition_log.append((step, cur, next_state, trans_prob))
        path.append(next_state)
        history.append(next_state)
        visit_counts[next_state] = visit_counts.get(next_state, 0) + 1
        cur = next_state

    return WalkResult(
        path             = tuple(path),
        transition_log   = tuple(transition_log),
        final_state      = cur,
        steps_taken      = len(transition_log),
        absorbing_step   = absorbing_step,
        state_visit_counts = visit_counts,
        seed             = seed,
    )
```

## Inputs

| name | type | description |
|---|---|---|
| matrix | list[list[float]] | R×R row-stochastic transition matrix |
| states | list[str] | State labels (row/col order) |
| start_state | str | Starting state (must be in `states`) |
| n_steps | int | Maximum simulation steps (≥ 1) |
| seed | int or None | RNG seed for reproducibility |
| context_callback | callable or None | Per-step environment hook; signature `(step, current_state, history) -> dict or None` |
| absorbing_threshold | float | P[i][i] ≥ this ⇒ absorbing halt (default 0.99) |

## Outputs

| name | type | description |
|---|---|---|
| path | tuple[str] | Full visited state sequence |
| transition_log | tuple[tuple] | (step, from, to, probability) for each transition |
| final_state | str | Last visited state |
| steps_taken | int | Number of transitions executed |
| absorbing_step | int or None | Step at which absorption detected; None if none |
| state_visit_counts | dict[str → int] | Visit count per state |
| seed | int or None | Echo of input seed |

## Dynamic Context Injection
The `context_callback` is the key feature linking this skill to the M³ agent architecture. At each step t:

```python
def my_context_callback(step, current_state, history):
    # Pull from agent working memory — e.g., "current_task_affinity"
    if step > 5:
        return {
            "state_boost": {"GoalState": 0.3},
            "matrix_override": None
        }
    return None
```

Return keys:
- `"matrix_override"` → full matrix replacement (rare, high-impact)
- `"state_boost"` → additive deltas to the current row (common, fine-grained)

## Error Handling
| Error | Condition |
|---|---|
| start_state not in states | Raise ValueError |
| n_steps < 1 | Raise ValueError |
| matrix dimension mismatch | Raise ValueError |
| row not stochastic | Raise ValueError (caught early from generate_transition_matrix) |

## State Updates
```
state_add_observation("stochastic/walk/path", result.path)
state_add_observation("stochastic/walk/final_state", result.final_state)
state_add_observation("stochastic/walk/visit_counts", result.state_visit_counts)
belief_add(walk_executed(MatrixId, StartState, Steps, Seed))
```

## Security
- In-memory only. No I/O.
- Seedable RNG prevents non-determinism in tests.
- `context_callback` receives only internal data; no external surface access.
