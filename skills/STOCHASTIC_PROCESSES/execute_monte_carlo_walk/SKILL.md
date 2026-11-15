---
name: execute_monte_carlo_walk
domain: STOCHASTIC_PROCESSES
version: 1.0.0
surfaces:
  - python
description: Stochastic random walk simulation engine executing discrete Markov chain traversals using inverse transform sampling. Supports dynamic environment modulation via per-step context-callback hooks (enabling transition matrix overrides and additive state boosts), tracks transition logs, state visit frequencies, absorbing state termination thresholds, and seedable RNG reproducibility in Python. Use when simulating random walks on graphs, modeling particle diffusion, or generating agent state trajectories.
purpose: Execute Monte Carlo random walk simulations on Markov transition matrices with dynamic context callbacks.
dependencies:
  - STOCHASTIC_PROCESSES/generate_transition_matrix
  - STOCHASTIC_PROCESSES/assert_context_gate
tags:
  - monte-carlo-walk
  - random-walk
  - inverse-transform-sampling
  - context-callback
  - absorbing-threshold
  - simulation
inputs:
  matrix:
    type: array
    required: true
    description: Row-stochastic probability matrix $R \times R$.
  states:
    type: array
    required: true
    description: List of state labels corresponding to matrix rows/columns.
  start_state:
    type: string
    required: true
    description: Initial starting state label.
  n_steps:
    type: integer
    required: true
    description: Maximum simulation step count $N \ge 1$.
  seed:
    type: integer
    required: false
    description: Optional RNG seed for deterministic reproduction.
  context_callback:
    type: object
    required: false
    description: Optional step callback for dynamic matrix mutation `(step, state, history) -> {matrix_override, state_boost}`.
  absorbing_threshold:
    type: number
    required: false
    description: Diagonal probability threshold to treat state as absorbing (default 0.99).
outputs:
  path:
    type: array
    description: Ordered state sequence trajectory visited during the walk.
  transition_log:
    type: array
    description: Chronological list of transition records `[(step, from, to, probability), ...]`.
  final_state:
    type: string
    description: Last visited state when simulation terminated.
  steps_taken:
    type: integer
    description: Total number of transitions executed.
  absorbing_step:
    type: integer
    description: Step index where absorbing state was encountered (or null).
  state_visit_counts:
    type: object
    description: Map of each state to total visit counts across the walk.
---

# Execute Monte Carlo Walk Engine

`execute_monte_carlo_walk` simulates stochastic paths through a discrete-time Markov chain using **inverse transform sampling** from uniform random draws $U \sim \text{Uniform}(0, 1)$. It incorporates **dynamic context callbacks** to model environmental state modulation at runtime:

$$s_{t+1} = F^{-1}(U \mid s_t), \quad F(k \mid s_t) = \sum_{j=1}^k P(s_t, j)$$

$$\mathbf{P}_{\text{active}}^{(t)} = \text{ContextCallback}(t, s_t, \text{History}) \oplus \mathbf{P}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Monte Carlo Walk Progression

```
[1. Matrix & Initial State Invariant Audit] → [2. Context Callback & Matrix Modulation] → [3. Visual Brief] → [4. Checkpoint] → [5. Inverse Transform Sample & Emit]
```

### Stage 1: Matrix & Initial State Invariant Audit
1. Ingest $R \times R$ matrix $\mathbf{P}$, state labels, and starting state $s_0$.
2. Assert row-stochasticity ($\sum P_{ij} = 1.0$) and $s_0 \in \text{states}$.
3. Initialize step counter $t = 0$, path array $[s_0]$, and visit count map.

> **Completion criterion**: Valid initial Markov chain state established.

---

### Stage 2: Context Callback & Matrix Modulation
1. At each step $t$, execute `context_callback(t, s_t, history)` if defined.
2. Apply `matrix_override` (full replacement) or `state_boost` (additive deltas with re-normalization).

> **Completion criterion**: Active transition probability row $\mathbf{p}(s_t)$ evaluated.

---

### Stage 3: The Visual Brief
For stochastic walk trajectories and diffusion simulations, generate an interactive brief:
- **Location**: Write to `%TEMP%\monte-carlo-walk-brief-<timestamp>.html` (Windows) or `/tmp/monte-carlo-walk-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render state trajectory timeline plot, cumulative state occupancy bar chart, and transition probability flow path.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before sampling next transition:
1. Inspect absorbing condition: if $P(s_t, s_t) \ge \text{absorbing\_threshold}$ (default 0.99), record `absorbing_step = t` and terminate early.

> **Completion criterion**: Absorbing boundary condition evaluated.

---

### Stage 5: Inverse Transform Sampling & Trajectory Emission
1. Draw $u \sim \text{Uniform}(0, 1)$ and select next state $s_{t+1}$ via cumulative sum inversion.
2. Record transition in `transition_log` and update visit counters.
3. Repeat until $n_{\text{steps}}$ or absorption.
4. Emit complete `WalkResult` record.

> **Completion criterion**: Full trajectory record emitted with visit counts and transition log.

---

## Surface References

### Python Calculation Surface

```python
import random
from typing import List, Dict, Any, Optional, Tuple, Callable

def _sample_next(state: str, state_to_idx: Dict[str, int], matrix: List[List[float]], rng: random.Random) -> str:
    idx = state_to_idx[state]
    row = matrix[idx]
    u = rng.random()
    cumsum = 0.0
    states_list = list(state_to_idx.keys())
    for j, p in enumerate(row):
        cumsum += p
        if u <= cumsum:
            return states_list[j]
    return states_list[-1]

def execute_monte_carlo_walk(
    matrix: List[List[float]],
    states: List[str],
    start_state: str,
    n_steps: int,
    seed: Optional[int] = None,
    context_callback: Optional[Callable[[int, str, List[str]], Optional[Dict[str, Any]]]] = None,
    absorbing_threshold: float = 0.99
) -> Dict[str, Any]:
    if start_state not in states:
        raise ValueError(f"invalid_start_state: '{start_state}' not in state list {states}.")
    if n_steps < 1:
        raise ValueError("insufficient_steps: n_steps must be >= 1.")
        
    n = len(states)
    if len(matrix) != n or any(len(row) != n for row in matrix):
        raise ValueError("matrix_dimension_mismatch: Matrix must be R x R where R = len(states).")
        
    rng = random.Random(seed)
    state_to_idx = {s: i for i, s in enumerate(states)}
    
    path = [start_state]
    history = [start_state]
    transition_log = []
    visit_counts = {s: 0 for s in states}
    visit_counts[start_state] = 1
    
    absorbing_step = None
    cur = start_state
    
    for step in range(n_steps):
        active_matrix = [row[:] for row in matrix]
        if context_callback is not None:
            override = context_callback(step, cur, history)
            if override:
                if "matrix_override" in override and override["matrix_override"]:
                    active_matrix = override["matrix_override"]
                if "state_boost" in override and override["state_boost"]:
                    idx = state_to_idx[cur]
                    for s_label, delta in override["state_boost"].items():
                        if s_label in state_to_idx:
                            active_matrix[idx][state_to_idx[s_label]] += delta
                    r_sum = sum(active_matrix[idx])
                    if r_sum > 0:
                        active_matrix[idx] = [p / r_sum for p in active_matrix[idx]]
                        
        cur_idx = state_to_idx[cur]
        if active_matrix[cur_idx][cur_idx] >= absorbing_threshold:
            absorbing_step = step
            break
            
        next_state = _sample_next(cur, state_to_idx, active_matrix, rng)
        trans_prob = active_matrix[cur_idx][state_to_idx[next_state]]
        
        transition_log.append({"step": step, "from": cur, "to": next_state, "probability": round(trans_prob, 6)})
        path.append(next_state)
        history.append(next_state)
        visit_counts[next_state] += 1
        cur = next_state
        
    return {
        "path": path,
        "transition_log": transition_log,
        "final_state": cur,
        "steps_taken": len(transition_log),
        "absorbing_step": absorbing_step,
        "state_visit_counts": visit_counts,
        "seed": seed
    }
```

---

## Anti-Patterns & Guardrails

- **Unseeded Non-Reproducible Simulations** — Running stochastic walks without seed parameters in regression test pipelines.
- **Missing State Bounds in Context Overrides** — Adding arbitrary unnormalized state boost weights without re-normalizing row probability sums to 1.0.
- **Infinite Walk Loops on Absorbing States** — Failing to halt simulation when reaching an absorbing terminal state ($P_{ii} \ge 0.99$).
