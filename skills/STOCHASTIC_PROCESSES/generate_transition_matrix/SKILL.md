---
name: generate_transition_matrix
domain: STOCHASTIC_PROCESSES
version: "1.0.0"
surfaces: [prolog, python]
description: |
  Constructs a validated stochastic transition matrix from observed
  state sequences or raw count data.  The Prolog layer verifies
  row-stochastic normalization and detects absorbing states;
  Python performs frequency counting and smoothing.
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

# Generate Transition Matrix

## Purpose
Convert observed state sequences or raw transition counts into a validated row-stochastic transition matrix P where each row i sums to exactly 1.0 and every entry P[i][j] ≥ 0.

## Description
Hybrid skill bridging Markov's original vowel-consonant derivation with modern agent-state traversal. Two input modes:
1. **Sequence mode**: list of state tokens `[A, B, A, C, ...]` — Python counts (i→j) transitions.
2. **Count mode**: raw integer matrix of (i, j) occurrence counts.

After counting, a Laplace smoothing parameter α is applied. The Prolog layer then validates:
- Every row is a valid probability distribution
- Row sums equal 1.0 within optional tolerance
- No row contains negative probabilities
- Absorbing states (row where P[i][i] = 1, all other entries = 0) are flagged

## Prolog Surface (prelude.pl)

```prolog
:- module(transition_matrix, [
    row_stochastic/2,
    absorbing_state/2,
    valid_matrix/1
]).

% ============================================================
% 1. Row-stochastic validation
%    Sum of each row must be 1.0 within tolerance.
% ============================================================
row_stochastic(Row, _Tolerance) :-
    sum_list(Row, Sum),
    abs(Sum - 1.0) < 1e-9.

% ============================================================
% 2. Absorbing state detection
%    An absorbing state i has P[i][i] = 1 and P[i][j≠i] = 0.
% ============================================================
absorbing_state(StateIndex, _Matrix) :-
    nth0(StateIndex, _Matrix, Row),
    Row = [First|Rest],
    First = 1.0,
    forall(member(Elem, Rest), Elem = 0.0).

% ============================================================
% 3. Non-absorbing classification
% ============================================================
transient_state(StateIndex, Matrix) :-
    nth0(StateIndex, _Matrix, _),
    \+ absorbing_state(StateIndex, Matrix).

% ============================================================
% 4. Full matrix validator (called after Python normalization)
% ============================================================
valid_matrix(Matrix) :-
    forall(
        nth0(_, Matrix, Row),
        ( valid_row(Row), row_stochastic(Row, 1e-9) )
    ).

valid_row(Row) :-
    forall(member(E, Row), E >= 0.0).
```

## Python Surface (executor.py)

```python
"""
generate_transition_matrix
============================
Constructs a normalized, Laplace-smoothed row-stochastic transition
matrix from state sequences or raw count data.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Union


@dataclass(frozen=True)
class TransitionMatrixResult:
    states: Tuple[str, ...]
    matrix: Tuple[Tuple[float, ...], ...]
    raw_counts: Tuple[Tuple[int, ...], ...]
    absorbing_states: Tuple[str, ...]
    laplace_alpha: float
    row_sums: Tuple[float, ...]

    def to_dict(self) -> dict:
        return {
            "states":          list(self.states),
            "matrix":          [list(r) for r in self.matrix],
            "raw_counts":      [list(r) for r in self.raw_counts],
            "absorbing_states": list(self.absorbing_states),
            "laplace_alpha":   self.laplace_alpha,
            "row_sums":        list(self.row_sums),
        }


def from_sequence(
    sequence: List[str],
    states: Optional[List[str]] = None,
    laplace_alpha: float = 0.0,
) -> TransitionMatrixResult:
    """Build transition matrix from an ordered state sequence.

    Parameters
    ----------
    sequence : list of str
        Observed state path e.g. ['Vowel', 'Consonant', 'Vowel', ...].
    states : list of str or None
        Explicit state universe.  If None, inferred from unique values.
    laplace_alpha : float
        Laplace smoothing additive (default 0.0 = no smoothing).

    Returns
    -------
    TransitionMatrixResult
    """
    if len(sequence) < 2:
        raise ValueError(
            f"insufficient_sequence: need >= 2 states, got {len(sequence)}"
        )

    if states is None:
        states = sorted(set(sequence))
    state_to_idx = {s: i for i, s in enumerate(states)}
    n = len(states)

    counts = [[0] * n for _ in range(n)]
    for i in range(len(sequence) - 1):
        src = sequence[i]
        dst = sequence[i + 1]
        if src in state_to_idx and dst in state_to_idx:
            counts[state_to_idx[src]][state_to_idx[dst]] += 1

    return _normalize(counts, states, laplace_alpha)


def from_count_matrix(
    counts: List[List[Union[int, float]]],
    states: List[str],
    laplace_alpha: float = 0.0,
) -> TransitionMatrixResult:
    """Build transition matrix from a raw count matrix.

    Parameters
    ----------
    counts : list of list of int
        R×R matrix where counts[i][j] is number of times state i
        transitioned to state j.
    states : list of str
        Ordered state labels (row and column order).
    laplace_alpha : float
        Laplace smoothing additive.

    Returns
    -------
    TransitionMatrixResult
    """
    n = len(states)
    if len(counts) != n:
        raise ValueError(f"count matrix rows ({len(counts)}) != n_states ({n})")
    for i, row in enumerate(counts):
        if len(row) != n:
            raise ValueError(
                f"count matrix row {i} has {len(row)} cols, expected {n}"
            )

    return _normalize(counts, states, laplace_alpha)


def _normalize(
    counts: List[List[int]],
    states: List[str],
    laplace_alpha: float,
) -> TransitionMatrixResult:
    """Private: normalize count matrix into row-stochastic probabilities."""
    n = len(states)
    alpha = max(laplace_alpha, 0.0)
    raw = [row[:] for row in counts]

    matrix = []
    row_sums = []
    for i in range(n):
        row_total = sum(raw[i]) + n * alpha
        row_sums.append(float(row_total))
        if row_total == 0:
            # Completely unobserved state — distribute uniformly
            probs = [1.0 / n] * n
        else:
            probs = [(c + alpha) / row_total for c in raw[i]]
        matrix.append(probs)

    # Absorbing states
    absorbing: List[str] = []
    for i, row in enumerate(matrix):
        if all(
            (row[j] == 1.0 and j == i) or (row[j] == 0.0 and j != i)
            for j in range(n)
        ):
            absorbing.append(states[i])

    return TransitionMatrixResult(
        states           = tuple(states),
        matrix           = tuple(tuple(r) for r in matrix),
        raw_counts       = tuple(tuple(r) for r in raw),
        absorbing_states = tuple(absorbing),
        laplace_alpha    = alpha,
        row_sums         = tuple(row_sums),
    )
```

## Inputs

| name | type | description |
|---|---|---|
| sequence | list[str] or None | Ordered state sequence for count-mode input |
| counts | list[list[int]] or None | Raw R×R count matrix |
| states | list[str] | Explicit state universe (required for count mode) |
| laplace_alpha | float | Additive smoothing (default 0.0) |

## Outputs

| name | type | description |
|---|---|---|
| states | tuple[str] | Ordered state universe |
| matrix | tuple[tuple[float]] | R×R row-stochastic matrix |
| raw_counts | tuple[tuple[int]] | Original count matrix |
| absorbing_states | tuple[str] | Row indices where P[i][i]=1, all else 0 |
| row_sums | tuple[float] | Row sums before normalization (debug) |

## Validation Rules
- `len(sequence) >= 2` or `counts` non-empty
- Row sums equal 1.0 within floating epsilon
- All entries `>= 0.0`
- No NaN or Inf in output matrix
- `laplace_alpha >= 0.0`

## State Updates
```
belief_add(transition_matrix(States, Matrix))
belief_add(absorbing_states(States, AbsorbingList))
```

## Error Handling
| Error | Condition |
|---|---|
| insufficient_sequence | len(sequence) < 2 |
| ragged_matrix | Count rows have inconsistent lengths |
| states_mismatch | Count matrix size ≠ len(states) |

## Security
- No I/O. Pure in-memory computation.
- No external dependencies.
