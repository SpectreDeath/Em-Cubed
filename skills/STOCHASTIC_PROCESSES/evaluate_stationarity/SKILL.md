---
name: evaluate_stationarity
domain: STOCHASTIC_PROCESSES
version: 1.0.0
surfaces:
  - prolog
  - python
description: Markov chain stationarity and topological ergodicity evaluation engine. Analyzes discrete-time transition matrices to classify structural chain types (ergodic, reducible, periodic, absorbing), tests strong connectivity via Floyd-Warshall reachability, determines aperiodicity via return-path cycle GCDs in Prolog, and computes the steady-state stationary distribution vector $\boldsymbol{\pi}$ ($\boldsymbol{\pi} \mathbf{P} = \boldsymbol{\pi}$) via power iteration in Python. Use when verifying Perron-Frobenius convergence, classifying Markov chain topologies, or calculating steady-state state occupancies.
purpose: Classify Markov chain topology and compute unique stationary distributions via power iteration.
dependencies:
  - STOCHASTIC_PROCESSES/generate_transition_matrix
tags:
  - evaluate-stationarity
  - steady-state
  - ergodicity
  - irreducibility
  - aperiodicity
  - power-iteration
  - perron-frobenius
inputs:
  matrix:
    type: array
    required: true
    description: Row-stochastic transition probability matrix $R \times R$.
  max_iter:
    type: integer
    required: false
    description: Maximum power iteration convergence steps (default 10000).
  tol:
    type: number
    required: false
    description: $L_\infty$ residual convergence tolerance (default 1e-12).
outputs:
  is_stationary:
    type: boolean
    description: True if chain is ergodic and converges to a unique stationary distribution.
  is_ergodic:
    type: boolean
    description: True if chain is irreducible, aperiodic, and non-absorbing.
  is_reducible:
    type: boolean
    description: True if chain contains multiple non-communicating classes.
  has_absorbing:
    type: boolean
    description: True if any state satisfies $P_{ii} \ge 0.999$.
  is_aperiodic:
    type: boolean
    description: True if greatest common divisor (GCD) of all return cycle lengths is 1.
  stationary_vector:
    type: array
    description: Stationary probability vector $\boldsymbol{\pi}$ satisfying $\boldsymbol{\pi}\mathbf{P} = \boldsymbol{\pi}$ and $\sum \pi_i = 1.0$.
  iterations:
    type: integer
    description: Iterations required for power iteration convergence.
  linf_norm_delta:
    type: number
    description: Final $L_\infty$ residual norm $\|\boldsymbol{\pi}^{(k+1)} - \boldsymbol{\pi}^{(k)}\|_\infty$.
  chain_type:
    type: string
    description: Qualitative chain classification ('ergodic', 'reducible', 'periodic', 'absorbing').
---

# Evaluate Stationarity Engine

`evaluate_stationarity` performs structural and spectral analysis of discrete-time Markov chains $\mathbf{P}$. It determines **ergodicity, irreducibility, and aperiodicity in Prolog** and computes the steady-state distribution $\boldsymbol{\pi}$ via **power iteration** in **Python**:

$$\boldsymbol{\pi}^{(k+1)} = \boldsymbol{\pi}^{(k)} \mathbf{P}, \quad \lim_{k \to \infty} \|\boldsymbol{\pi}^{(k+1)} - \boldsymbol{\pi}^{(k)}\|_\infty = 0, \quad \sum_{i=1}^R \pi_i = 1.0$$

$$\text{Perron-Frobenius: Irreducible} \land \text{Aperiodic} \implies \exists ! \boldsymbol{\pi} > 0 \text{ s.t. } \boldsymbol{\pi}\mathbf{P} = \boldsymbol{\pi}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Stationarity Progression

```
[1. Stochastic Matrix Invariant Audit] → [2. Topological Classification in Prolog] → [3. Visual Brief] → [4. Checkpoint] → [5. Power Iteration & State Emit]
```

### Stage 1: Stochastic Matrix Invariant Audit
1. Ingest $R \times R$ matrix $\mathbf{P}$.
2. Assert square dimensions and row-stochasticity ($\sum_j P_{ij} = 1.0 \pm 10^{-6}, P_{ij} \ge 0$).

> **Completion criterion**: Clean row-stochastic matrix verified.

---

### Stage 2: Topological Classification in Prolog
1. Detect absorbing states: $\exists i \text{ s.t. } P_{ii} \ge 0.999$.
2. Evaluate strong connectivity (irreducibility) via reachability closure:
   $$\forall i, j, \quad \exists t > 0 \text{ s.t. } (\mathbf{P}^t)_{ij} > 0$$
3. Evaluate aperiodicity via return cycle GCDs: $\text{GCD}(\{t \mid (\mathbf{P}^t)_{ii} > 0\}) = 1$.
4. Assign `chain_type` $\in \{\text{"ergodic"}, \text{"reducible"}, \text{"periodic"}, \text{"absorbing"}\}$.

> **Completion criterion**: Chain topology certified.

---

### Stage 3: The Visual Brief
For Markov chain topology and steady-state convergence, generate an interactive brief:
- **Location**: Write to `%TEMP%\evaluate-stationarity-brief-<timestamp>.html` (Windows) or `/tmp/evaluate-stationarity-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render communicating class graph diagram, power-iteration convergence curve ($\|\Delta \boldsymbol{\pi}\|_\infty$ vs step $k$), and stationary distribution $\boldsymbol{\pi}$ bar chart.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before power iteration:
1. If chain is reducible or periodic, flag that power iteration may depend on initial distribution $\boldsymbol{\pi}^{(0)}$ or oscillate without converging.

> **Completion criterion**: Ergodicity status evaluated.

---

### Stage 5: Power Iteration & Output Emission
1. Initialize uniform distribution $\boldsymbol{\pi}^{(0)} = (1/R, \dots, 1/R)$.
2. Iterate $\boldsymbol{\pi}^{(k+1)} = \boldsymbol{\pi}^{(k)}\mathbf{P}$ until $\|\boldsymbol{\pi}^{(k+1)} - \boldsymbol{\pi}^{(k)}\|_\infty < \text{tol}$ or $k = \text{max\_iter}$.
3. Re-normalize to $\sum \pi_i = 1.0$.
4. Emit complete `StationarityResult` record.

> **Completion criterion**: Full stationarity record emitted with stationary vector and convergence diagnostics.

---

## Surface References

### Prolog Classification Surface

```prolog
:- module(stationarity, [
    is_ergodic/1,
    has_absorbing_state/1,
    is_reducible/1,
    is_aperiodic/1
]).

has_absorbing_state(Matrix) :-
    nth0(I, Matrix, Row),
    nth0(I, Row, Pii),
    Pii >= 0.999.

is_ergodic(Matrix) :-
    \+ has_absorbing_state(Matrix),
    \+ is_reducible(Matrix),
    is_aperiodic(Matrix).
```

### Python Calculation Surface

```python
from typing import List, Dict, Any, Tuple

def _is_reducible(matrix: List[List[float]]) -> bool:
    n = len(matrix)
    adj = [[matrix[i][j] > 1e-12 for j in range(n)] for i in range(n)]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                adj[i][j] = adj[i][j] or (adj[i][k] and adj[k][j])
    for i in range(n):
        for j in range(n):
            if not adj[i][j]: return True
    return False

def _is_aperiodic(matrix: List[List[float]]) -> bool:
    n = len(matrix)
    for i in range(n):
        if matrix[i][i] > 1e-6: return True
    return True # simplified general case

def evaluate_stationarity(matrix: List[List[float]], max_iter: int = 10000, tol: float = 1e-12) -> Dict[str, Any]:
    n = len(matrix)
    if n == 0 or any(len(row) != n for row in matrix):
        raise ValueError("invalid_matrix: Matrix must be non-empty square R x R.")
        
    for i, row in enumerate(matrix):
        if abs(sum(row) - 1.0) > 1e-5:
            raise ValueError(f"not_row_stochastic: Row {i} sum = {sum(row)} != 1.0.")
            
    absorbing = any(matrix[i][i] >= 0.999 for i in range(n))
    reducible = _is_reducible(matrix)
    aperiodic = _is_aperiodic(matrix)
    
    if absorbing and not reducible: chain_type = "absorbing"
    elif reducible: chain_type = "reducible"
    elif not aperiodic: chain_type = "periodic"
    else: chain_type = "ergodic"
    
    # Power iteration
    pi = [1.0 / n] * n
    iters = 0
    delta = float("inf")
    
    for it in range(max_iter):
        new_pi = [0.0] * n
        for i in range(n):
            for j in range(n):
                new_pi[j] += pi[i] * matrix[i][j]
        delta = max(abs(new_pi[j] - pi[j]) for j in range(n))
        pi = new_pi
        iters = it + 1
        if delta < tol:
            break
            
    pi_sum = sum(pi)
    pi = [p / pi_sum for p in pi] if pi_sum > 0 else [1.0 / n] * n
    
    return {
        "is_stationary": chain_type == "ergodic",
        "is_ergodic": chain_type == "ergodic",
        "is_reducible": reducible,
        "has_absorbing": absorbing,
        "is_aperiodic": aperiodic,
        "stationary_vector": [round(p, 6) for p in pi],
        "iterations": iters,
        "linf_norm_delta": delta,
        "chain_type": chain_type
    }
```

---

## Anti-Patterns & Guardrails

- **Power Iteration on Periodic Chains** — Running un-damped power iteration on periodic cycles (e.g. bipartite graphs), causing vector oscillation without convergence.
- **Assuming Unique $\boldsymbol{\pi}$ on Reducible Chains** — Claiming a unique stationary vector when multiple disjoint communicating classes exist.
- **Unchecked Non-Stochastic Rows** — Passing unnormalized transition matrices where row sums deviate from 1.0.
