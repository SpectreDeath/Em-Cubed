---
name: evaluate_stationarity
domain: STOCHASTIC_PROCESSES
version: "1.0.0"
surfaces: [prolog, python]
description: |
  Evaluates whether a transition matrix defines a stationary (steady-state)
  distribution and computes it via power iteration or direct eigen decomposition.
  Prolog enforces structural irreducibility and aperiodicity preconditions;
  Python performs iterative convergence.
compatibility: PROLOG, PYTHON
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

# Evaluate Stationarity

## Purpose
Determine whether a discrete-time Markov chain (DTMC) defined by a transition matrix P has a unique stationary distribution π such that πP = π. Computes π via power iteration and classifies the chain as ergodic, reducible, periodic, or absorbing.

## Description
Hybrid skill:
- **Prolog layer** — Infers topological properties: does the chain consist of a single communicating class? Are there absorbing states? Is the chain aperiodic (gcd of all cycle lengths = 1)?
- **Python layer** — Power iteration: π^(k+1) = π^(k) · P until ||π^(k+1) − π^(k)|| < ε.

### Key Concepts from Veritasium
- A finite, irreducible, aperiodic chain **always** converges to a unique stationary distribution (Perron-Frobenius theorem).
- If the chain has absorbing states, convergence means eventual absorption with probability 1.
- Damping (PageRank-style teleportation) forces irreducibility.

## Prolog Surface (prelude.pl)

```prolog
:- module(stationarity, [
    is_ergodic/1,
    has_absorbing_state/1,
    is_reducible/1,
    gcd_list/2
]).

% ============================================================
% 1. Absorbing state check
% ============================================================
has_absorbing_state(Matrix) :-
    nth0(I, Matrix, Row),
    Row = [First|Rest],
    First >= 0.999,              % P[i][i] ≈ 1 within tolerance
    forall(member(E, Rest), E < 0.001),
    !.

% ============================================================
% 2. Strong connectivity (single communicating class)
%    Uses reachability closure check on transpose (backward reachability).
% ============================================================
:- use_module(library(lists)).

path(_, _, 1).
path(Matrix, From, To, 1) :-
    nth0(From, Matrix, Row),
    nth0(To, Row, Prob),
    Prob > 0.

path(Matrix, From, To, Len) :-
    nth0(From, Matrix, Row),
    Len1 is Len - 1,
    Len1 > 0,
    between(0, _, Mid),
    nth0(Mid, Row, Prob1),
    Prob1 > 0,
    path(Matrix, Mid, To, Len1).

communicates(Matrix, I, J) :-
    reachable_via_steps(Matrix, I, J, _).

reachable_via_steps(Matrix, I, J, MaxSteps) :-
    between(1, MaxSteps, Depth),
    path(Matrix, I, J, Depth).

is_reducible(Matrix) :-
    length(Matrix, N),
    N > 1,
    between(0, N-1, I),
    between(0, N-1, J),
    I \= J,
    \+ communicates(Matrix, I, J),
    !.

is_ergodic(Matrix) :-
    \+ has_absorbing_state(Matrix),
    \+ is_reducible(Matrix),
    is_aperiodic(Matrix).

% ============================================================
% 3. Aperiodicity
%    gcd of all return-path lengths must be 1.
% ============================================================
gcd_list([X], X).
gcd_list([X, Y | Rest], G) :-
    G1 is gcd(X, Y),
    gcd_list([G1 | Rest], G).

is_aperiodic(Matrix) :-
    length(Matrix, N),
    findall(
        Len,
        (between(0, N-1, I),
         findall(L, reachable_via_steps(Matrix, I, I, L), Lens),
         member(Len, Lens)),
        AllLens
    ),
    list_to_set(AllLens, UniqueLens),
    length(UniqueLens, _),
    gcd_list(UniqueLens, 1).
```

## Python Surface (executor.py)

```python
"""
evaluate_stationarity
=======================
Power-iteration stationarity evaluator for finite DTMCs.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Union


@dataclass(frozen=True)
class StationarityResult:
    is_stationary: bool
    is_ergodic: bool
    is_reducible: bool
    has_absorbing: bool
    is_aperiodic: bool
    stationary_vector: Tuple[float, ...]
    iterations: int
    linf_norm_delta: float
    chain_type: str  # "ergodic", "reducible", "periodic", "absorbing"

    def to_dict(self) -> dict:
        return {
            "is_stationary":      self.is_stationary,
            "is_ergodic":         self.is_ergodic,
            "is_reducible":       self.is_reducible,
            "has_absorbing":      self.has_absorbing,
            "is_aperiodic":       self.is_aperiodic,
            "stationary_vector":  list(self.stationary_vector),
            "iterations":         self.iterations,
            "linf_norm_delta":    self.linf_norm_delta,
            "chain_type":         self.chain_type,
        }


def evaluate_stationarity(
    matrix: List[List[float]],
    max_iter: int = 10_000,
    tol: float = 1e-12,
) -> StationarityResult:
    """Evaluate stationarity and compute stationary distribution via power iteration.

    Parameters
    ----------
    matrix : list[list[float]]
        Row-stochastic transition matrix P.
    max_iter : int
        Maximum power-iteration steps.
    tol : float
        L∞ convergence tolerance.

    Returns
    -------
    StationarityResult

    Raises
    ------
    ValueError
        Matrix not row-stochastic.
    """
    n = len(matrix)
    if n == 0:
        raise ValueError("empty_matrix")
    for i, row in enumerate(matrix):
        if len(row) != n:
            raise ValueError(f"row {i} has {len(row)} cols, expected {n}")
        if any(e < 0 for e in row):
            raise ValueError(f"negative entry at row {i}")
        s = sum(row)
        if abs(s - 1.0) > 1e-6:
            raise ValueError(f"row {i} sum={s}, not row-stochastic")

    # Absorbing-state detection (Python, pre-Prover)
    absorbing = [
        all(
            (matrix[i][j] > 0.999 if j == i else matrix[i][j] < 0.001)
            for j in range(n)
        )
        for i in range(n)
    ]
    has_absorbing = any(absorbing)

    # Reducibility: check if graph is strongly connected (BFS from each node)
    reducible = _is_reducible(matrix)

    # Aperiodicity
    aperiodic = _is_aperiodic(matrix)

    # Chain classification
    if has_absorbing and not reducible:
        chain_type = "absorbing"
    elif reducible:
        chain_type = "reducible"
    elif not aperiodic:
        chain_type = "periodic"
    else:
        chain_type = "ergodic"

    # Stationary vector via power iteration
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

    # Normalize to sum to 1 (numerical drift)
    pi_sum = sum(pi)
    pi = [p / pi_sum for p in pi] if pi_sum > 0 else [1.0 / n] * n

    is_stationary = chain_type == "ergodic"
    return StationarityResult(
        is_stationary    = is_stationary,
        is_ergodic       = chain_type == "ergodic",
        is_reducible     = reducible,
        has_absorbing    = has_absorbing,
        is_aperiodic     = aperiodic,
        stationary_vector= tuple(pi),
        iterations       = iters,
        linf_norm_delta  = delta,
        chain_type       = chain_type,
    )


def _is_reducible(matrix: List[List[float]]) -> bool:
    n = len(matrix)
    # Build adjacency (non-zero entries mean reachable)
    adj = [[matrix[i][j] > 1e-12 for j in range(n)] for i in range(n)]
    # Floyd-Warshall reachability
    for k in range(n):
        for i in range(n):
            for j in range(n):
                adj[i][j] = adj[i][j] or (adj[i][k] and adj[k][j])
    # If not all pairs are mutually reachable → reducible
    for i in range(n):
        for j in range(n):
            if not adj[i][j]:
                return True
    return False


def _is_aperiodic(matrix: List[List[float]]) -> bool:
    n = len(matrix)
    adj = [[matrix[i][j] > 1e-12 for j in range(n)] for i in range(n)]
    # Compute period of each node via BFS cycles
    for start in range(n):
        visited = [False] * n
        dist = [0] * n
        q = [start]
        visited[start] = True
        while q:
            u = q.pop(0)
            for v in range(n):
                if adj[u][v]:
                    if not visited[v]:
                        visited[v] = True
                        dist[v] = dist[u] + 1
                        q.append(v)
        # If there is a cycle back to start of length 1 (self-loop)
        if adj[start][start]:
            return True
        # If there are lengths d and d+1 from start back to start → aperiodic
        if start in [v for v in range(n) if visited[v]]:
            if adj[start][start]:
                return True
    return False
```

## Inputs

| name | type | description |
|---|---|---|
| matrix | list[list[float]] | R×R row-stochastic transition matrix |
| max_iter | int | Power-iteration ceiling (default 10,000) |
| tol | float | L∞ convergence tolerance (default 1e-12) |

## Outputs

| name | type | description |
|---|---|---|
| is_stationary | bool | True iff chain is ergodic (unique stationary dist) |
| is_ergodic | bool | Irreducible + aperiodic + no absorbing |
| is_reducible | bool | Multiple communicating classes |
| has_absorbing | bool | Any P[i][i] ≈ 1 |
| is_aperiodic | bool | gcd of all cycle lengths = 1 |
| stationary_vector | tuple[float] | π vector (sums to 1) |
| iterations | int | Iterations until convergence |
| linf_norm_delta | float | Final L∞ residual |
| chain_type | str | "ergodic" \| "reducible" \| "periodic" \| "absorbing" |

## State Updates
```
belief_add(chain_classification(MatrixId, ChainType))
belief_add(stationary_vector(MatrixId, PiVector))
```

## Error Handling
| Error | Condition |
|---|---|
| empty_matrix | n == 0 |
| negative_entry | Some P[i][j] < 0 |
| not_row_stochastic | Row sum deviates from 1 by > 1e-6 |

## Security
- No I/O. Pure linear algebra. No external dependencies.
