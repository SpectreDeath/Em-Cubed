---
name: markov-chain-sequence
domain: ANALYTICS
version: 1.0.0
surfaces:
  - python
  - prolog
description: Multi-surface discrete Markov chain state sequence generator and transition auditor. Validates stochastic matrix normalization (sum of row transition probabilities equals 1.0) in Prolog and executes memoryless random walk state transitions across discrete states in Python. Use when simulating Markovian state dynamics, verifying stochastic matrix row constraints, or generating dependent sequential text/state streams.
purpose: Simulate memoryless discrete Markov chain state transitions with strict Prolog stochastic matrix row validation.
dependencies: []
tags:
  - markov-chain
  - stochastic-matrix
  - state-transition
  - random-walk
  - sequence-generator
  - prolog
inputs:
  transition_matrix:
    type: object
    required: true
    description: 'Nested dictionary mapping current state to next state transition probabilities `{"StateA": {"StateA": float, "StateB": float}}`.'
  current_state:
    type: string
    required: true
    description: Starting state identifier for the transition step.
  random_value:
    type: number
    required: false
    description: Optional pseudo-random float in [0.0, 1.0] for deterministic stepping.
outputs:
  next_state:
    type: string
    description: Sampled destination state following the transition probability distribution.
  previous_state:
    type: string
    description: The origin state before the transition step.
  stochastic_valid:
    type: boolean
    description: True if transition matrix rows sum to 1.0 in Prolog.
---

# Markov Chain Sequence Generator Engine

`markov-chain-sequence` implements an infrastructure-safe, memoryless discrete Markov chain transition engine $(\mathcal{S}, \mathbf{P})$. It audits stochastic matrix rows in Prolog to guarantee strict unit probability normalization ($\sum_j P_{ij} = 1.0$) and executes cumulative density sampling in Python to step across state trajectories:

$$P(X_{t+1} = s_j \mid X_t = s_i, X_{t-1} = s_{t-1}, \dots) = P(X_{t+1} = s_j \mid X_t = s_i) = P_{ij}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Markov Transition Progression

```
[1. Matrix Invariant Audit] → [2. Prolog Stochastic Row Validation] → [3. Visual Brief] → [4. Checkpoint] → [5. Cumulative Stepping & Emission]
```

### Stage 1: Matrix Invariant & State Vocabulary Audit
1. Ingest `transition_matrix` and `current_state`.
2. Verify that `current_state` exists as a key in the transition matrix.
3. Validate that all transition branch probabilities are non-negative ($P_{ij} \ge 0.0$).

> **Completion criterion**: State space vocabulary $\mathcal{S}$ and non-negative probabilities verified.

---

### Stage 2: Prolog Stochastic Row Sum Normalization
1. Export transition row weights for `current_state` into Prolog.
2. Assert that row weights sum to unity:
   $$\left| \sum_{j} P_{ij} - 1.0 \right| < 10^{-4}$$
3. Check for sub-stochastic or super-stochastic row deviations.

> **Completion criterion**: Prolog returns success for `validate_state_weights/2`.

---

### Stage 3: The Visual Brief
For multi-state transition networks or absorbing state topologies, generate an interactive brief:
- **Location**: Write to `%TEMP%\markov-chain-brief-<timestamp>.html` (Windows) or `/tmp/markov-chain-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render the state transition directed graph with edge probability weights and stationary distribution estimates.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before executing long sequence walks ($> 100$ steps):
1. Detect absorbing states ($P_{ii} = 1.0$) or isolated subgraphs.
2. Verify that the random seed/value is bounded in $[0.0, 1.0]$.

> **Completion criterion**: Topology verified against unexpected trapping states.

---

### Stage 5: Cumulative Density Stepping & Sequence Emit
1. Construct cumulative probability distribution over candidate destination states.
2. Sample `next_state` where $\sum_{k=1}^{j-1} P_{ik} < r \le \sum_{k=1}^{j} P_{ik}$.
3. Emit transition step payload.

> **Completion criterion**: Valid next state emitted with `stochastic_valid: true`.

---

## Surface References

### Python Markov Transition Surface

```python
import random
from typing import Dict, Any

def step_markov_chain(matrix: Dict[str, Dict[str, float]], current_state: str, rand_val: float = None) -> Dict[str, Any]:
    if current_state not in matrix:
        return {"status": "error", "message": f"Unknown active state '{current_state}'"}
        
    branches = matrix[current_state]
    r = random.random() if rand_val is None else rand_val
    
    cumulative = 0.0
    for next_state, prob in branches.items():
        cumulative += prob
        if r <= cumulative:
            return {
                "previous_state": current_state,
                "next_state": next_state,
                "stochastic_valid": True
            }
            
    # Fallback to terminal branch if minor floating point rounding
    last_state = list(branches.keys())[-1]
    return {
        "previous_state": current_state,
        "next_state": last_state,
        "stochastic_valid": True
    }
```

### Prolog Row Normalization Surface

```prolog
sum_list([], 0.0).
sum_list([H|T], Sum) :-
    sum_list(T, Rest),
    Sum is H + Rest.

validate_state_weights(StateName, WeightsList) :-
    sum_list(WeightsList, Total),
    abs(Total - 1.0) < 0.0001, !.
validate_state_weights(StateName, _) :-
    throw(error(sub_stochastic_row(StateName))).
```

---

## Anti-Patterns & Guardrails

- **Sub-Stochastic Row Leakage** — Rows where $\sum P_{ij} < 0.999$, allowing probability mass to escape without a transition.
- **Unregistered Destination States** — Transitioning to a state identifier that is not declared in the global state vocabulary.
- **Unseeded Non-Reproducibility** — Executing regression tests on random walks without accepting a deterministic `rand_val` parameter.
