---
name: generate_transition_matrix
domain: STOCHASTIC_PROCESSES
version: 1.0.0
surfaces:
  - prolog
  - python
description: Stochastic transition matrix generation engine constructing row-stochastic probability matrices $P$ from observed state sequence paths or raw transition count matrices. Evaluates frequency tallies, applies Laplace smoothing $\alpha$, enforces row-stochastic normalization ($\sum_j P_{ij} = 1.0$) with non-negative entries ($P_{ij} \ge 0$), detects absorbing states ($P_{ii} = 1.0$), and verifies stochastic properties in Prolog. Use when building discrete-time Markov chains, estimating transition probabilities, or preparing graphs for stochastic random walks.
purpose: Construct and validate row-stochastic transition matrices with Laplace smoothing and absorbing state classification.
dependencies:
  - STOCHASTIC_PROCESSES/assert_context_gate
tags:
  - transition-matrix
  - markov-chain
  - row-stochastic
  - laplace-smoothing
  - absorbing-state
  - stochastic-processes
inputs:
  sequence:
    type: array
    required: false
    description: Ordered state path sequence `['state_a', 'state_b', ...]` for sequence mode.
  counts:
    type: array
    required: false
    description: Raw $R \times R$ integer frequency count matrix for count mode.
  states:
    type: array
    required: false
    description: Explicit ordered state label universe (required if using count mode).
  laplace_alpha:
    type: number
    required: false
    description: Additive Laplace smoothing constant (default 0.0).
outputs:
  states:
    type: array
    description: Ordered state label universe.
  matrix:
    type: array
    description: Validated $R \times R$ row-stochastic probability transition matrix.
  raw_counts:
    type: array
    description: Original empirical transition count matrix before smoothing.
  absorbing_states:
    type: array
    description: List of absorbing state labels where $P_{ii} = 1.0$ and $P_{ij} = 0.0$ for $j \neq i$.
  row_sums:
    type: array
    description: Vector of row sums prior to normalization.
---

# Generate Transition Matrix Engine

`generate_transition_matrix` transforms empirical discrete state sequences or raw frequency counts into a validated row-stochastic Markov transition matrix $\mathbf{P} \in \mathbb{R}^{R \times R}$. It enforces **stochastic normalization in Prolog** and computes smoothed probabilities and **absorbing state classifications** in **Python**:

$$P_{ij} = \frac{C_{ij} + \alpha}{\sum_{k=1}^R C_{ik} + R \cdot \alpha}, \quad \sum_{j=1}^R P_{ij} = 1.0, \quad P_{ij} \ge 0$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Transition Matrix Progression

```
[1. Sequence / Count Invariant Audit] → [2. Laplace Smoothing & Frequency Tally] → [3. Visual Brief] → [4. Checkpoint] → [5. Normalization, Absorbing Flag & Emit]
```

### Stage 1: Sequence / Count Invariant Audit
1. Ingest either state `sequence` (length $L \ge 2$) or square matrix `counts` ($R \times R$).
2. Determine or validate explicit `states` label array.
3. Ensure no negative counts exist.

> **Completion criterion**: Clean state space universe of size $R \ge 2$ established.

---

### Stage 2: Laplace Smoothing & Frequency Tally
1. If sequence mode: count consecutive transitions $(s_t \to s_{t+1})$ into raw matrix $\mathbf{C}$.
2. Apply additive Laplace smoothing $\alpha \ge 0.0$:
   $$\tilde{C}_{ij} = C_{ij} + \alpha$$

> **Completion criterion**: Smoothed transition count matrix evaluated.

---

### Stage 3: The Visual Brief
For stochastic transition topologies and Markov chains, generate an interactive brief:
- **Location**: Write to `%TEMP%\transition-matrix-brief-<timestamp>.html` (Windows) or `/tmp/transition-matrix-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render directed Markov state transition graph with edge probability weights, transition probability heatmap, and absorbing state flags.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before finalizing output matrix:
1. Check for unobserved states (rows with total count 0): distribute probability uniformly across all $R$ states ($P_{ij} = 1/R$).
2. Verify row sums: $\left|\sum_{j} P_{ij} - 1.0\right| \le 10^{-6}$.

> **Completion criterion**: Row-stochastic normalization invariant verified.

---

### Stage 5: Normalization, Absorbing Flag & Output Emission
1. Identify absorbing states: $P_{ii} = 1.0$ and $\forall j \neq i, P_{ij} = 0.0$.
2. Verify matrix properties in Prolog module.
3. Emit complete `TransitionMatrixResult` record.

> **Completion criterion**: Complete transition matrix payload emitted.

---

## Surface References

### Prolog Validation Surface

```prolog
:- module(transition_matrix, [
    row_stochastic/2,
    absorbing_state/2,
    valid_matrix/1
]).

row_stochastic(Row, _Tolerance) :-
    sum_list(Row, Sum),
    abs(Sum - 1.0) < 1e-6.

absorbing_state(StateIndex, Matrix) :-
    nth0(StateIndex, Matrix, Row),
    nth0(StateIndex, Row, 1.0),
    sum_list(Row, 1.0).

valid_matrix(Matrix) :-
    forall(
        member(Row, Matrix),
        ( forall(member(E, Row), E >= 0.0), row_stochastic(Row, 1e-6) )
    ).
```

### Python Calculation Surface

```python
from typing import List, Dict, Any, Optional, Tuple

def generate_transition_matrix(
    sequence: Optional[List[str]] = None,
    counts: Optional[List[List[int]]] = None,
    states: Optional[List[str]] = None,
    laplace_alpha: float = 0.0
) -> Dict[str, Any]:
    alpha = max(0.0, float(laplace_alpha))
    
    if sequence is not None:
        if len(sequence) < 2:
            raise ValueError("insufficient_sequence: Requires sequence length >= 2.")
        state_list = states or sorted(set(sequence))
        n = len(state_list)
        state_to_idx = {s: i for i, s in enumerate(state_list)}
        raw = [[0] * n for _ in range(n)]
        for i in range(len(sequence) - 1):
            src, dst = sequence[i], sequence[i + 1]
            if src in state_to_idx and dst in state_to_idx:
                raw[state_to_idx[src]][state_to_idx[dst]] += 1
    elif counts is not None:
        if states is None:
            raise ValueError("missing_states: Explicit state labels required for count matrix mode.")
        state_list = states
        n = len(state_list)
        if len(counts) != n or any(len(row) != n for row in counts):
            raise ValueError("matrix_dimension_mismatch: Counts matrix must be R x R where R = len(states).")
        raw = [[int(v) for v in row] for row in counts]
    else:
        raise ValueError("missing_input: Either sequence or counts matrix must be provided.")
        
    matrix = []
    row_sums = []
    for i in range(n):
        r_sum = sum(raw[i])
        row_sums.append(float(r_sum))
        denom = r_sum + n * alpha
        if denom == 0:
            probs = [1.0 / n] * n
        else:
            probs = [(raw[i][j] + alpha) / denom for j in range(n)]
        matrix.append(probs)
        
    absorbing = [state_list[i] for i, row in enumerate(matrix) if row[i] >= 0.9999 and sum(row) - row[i] < 1e-6]
    
    return {
        "states": state_list,
        "matrix": [[round(p, 6) for p in row] for row in matrix],
        "raw_counts": raw,
        "absorbing_states": absorbing,
        "laplace_alpha": alpha,
        "row_sums": row_sums
    }
```

---

## Anti-Patterns & Guardrails

- **Zero-Count Deadlock Rows** — Allowing unobserved states to generate rows with all zeros; must uniformly distribute probability mass ($1/R$).
- **Negative Smoothing Parameters** — Passing $\alpha < 0$, which can lead to negative transition probabilities.
- **Asymmetrical State Dimensions** — Passing count matrices whose row or column counts do not strictly match the state label set size.
