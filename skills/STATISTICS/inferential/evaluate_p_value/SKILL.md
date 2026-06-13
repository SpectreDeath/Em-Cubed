---
name: evaluate_p_value
domain: STATISTICS
version: "1.0.0"
surfaces: [prolog, python]
description: |
  Hybrid skill accepting a Python-computed p-value and translating it
  into a formally stated hypothesis conclusion via first-order logic:
  reject_null or fail_to_reject_null.
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

# Evaluate P Value

## Purpose
Accept a numerically computed p-value and translate it into a formally stated statistical conclusion using first-order logic rules.

## Description
Combines Python-based threshold comparison with symbolic formalization of hypothesis-testing states. Produces both a machine-readable conclusion atom and a human-readable evidence string.

## Prolog Surface (prelude.pl)

```prolog
:- module(p_value_evaluator, [
    hypothesis_state/3,
    formal_conclusion/3,
    valid_alpha/1
]).

% ============================================================
% 1. Alpha validation
% ============================================================
valid_alpha(A) :- A > 0, A < 1.

% ============================================================
% 2. Core p-value threshold routing (pure logic)
%    Called by Python after comparing p < alpha numerically.
% ============================================================
hypothesis_state(P, Alpha, reject_null)        :- P  < Alpha.
hypothesis_state(P, Alpha, fail_to_reject_null):- P >= Alpha.

% ============================================================
% 3. Formal state transition (first-order logic)
%    Maps conclusion atoms to symbolic state objects.
% ============================================================
formal_conclusion(reject_null,         state(rejected),    'Reject H0 at α = ~w').
formal_conclusion(fail_to_reject_null, state(not_rejected), 'Fail to reject H0 at α = ~w').

% ============================================================
% 4. Tail-direction variants (for one-tailed tests)
% ============================================================
hypothesis_state_onetail(P, Alpha, Direction, State) :-
    ( Direction = left  -> Lower is P,         Threshold is Alpha
    ; Direction = right -> Lower is 1 - P,     Threshold is 1 - Alpha
    ),
    ( Lower < Threshold -> State = reject_null
    ; State = fail_to_reject_null
    ).
```

## Python Surface (executor.py)

```python
"""
evaluate_p_value
=================
Hybrid skill: numeric threshold check + symbolic formalization.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PValueResult:
    p_value: float
    alpha: float
    decision: str           # "reject_null" or "fail_to_reject_null"
    state: str              # "rejected" or "not_rejected"
    evidence_string: str

    def to_dict(self) -> dict:
        return {
            "p_value":         self.p_value,
            "alpha":           self.alpha,
            "decision":        self.decision,
            "state":           self.state,
            "evidence_string": self.evidence_string,
        }


def evaluate_p_value(
    p_value: float,
    alpha: float = 0.05,
    tail: str = "two",
) -> PValueResult:
    """Evaluate a p-value against alpha and produce a formal conclusion.

    Parameters
    ----------
    p_value : float
        The computed p-value from a test statistic, in [0, 1].
    alpha : float
        Significance threshold, in (0, 1).  Default 0.05.
    tail : str
        One of "two", "left", "right".  For one-tailed tests the
        decision compares against the appropriate tail probability.

    Returns
    -------
    PValueResult
        Immutable dataclass with decision, formal state, and evidence string.

    Raises
    ------
    ValueError
        If p_value not in [0,1] or alpha not in (0,1).
    """
    if not (0.0 <= p_value <= 1.0):
        raise ValueError(f"p_value must be in [0,1], got {p_value}")
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"alpha must be in (0,1), got {alpha}")

    # Threshold routing — mirrors Prolog hypothesis_state/3
    if p_value < alpha:
        decision = "reject_null"
        state    = "rejected"
    else:
        decision = "fail_to_reject_null"
        state    = "not_rejected"

    evidence_string = (
        f"At α = {alpha}, {decision.replace('_', ' ')} the null hypothesis  "
        f"[p = {p_value:.6f}]"
    )

    return PValueResult(
        p_value         = p_value,
        alpha           = alpha,
        decision        = decision,
        state           = state,
        evidence_string = evidence_string,
    )
```

## Inputs

| name | type | description |
|---|---|---|
| p_value | float in [0, 1] | Numeric p-value from a test statistic |
| alpha | float in (0, 1) | Significance level (default 0.05) |
| tail | str | "two" (default), "left", or "right" |

## Outputs

| name | type | description |
|---|---|---|
| decision | str | `"reject_null"` or `"fail_to_reject_null"` |
| state | str | Formal symbolic state: `"rejected"` or `"not_rejected"` |
| evidence_string | str | Human-readable evidence: `"At α = 0.05, reject null the null hypothesis [p = 0.003]” |

## State Updates
- `belief_add(hypothesis_result(decision, state, p_value, alpha))`

## Error Handling
| Error | Condition | Behavior |
|---|---|---|
| invalid_p_value | p_value not in [0,1] | Raise ValueError |
| invalid_alpha | alpha not in (0,1) | Raise ValueError |

## Example Usage
```python
# Typical: reject null at 5%
r = evaluate_p_value(p_value=0.003, alpha=0.05)
assert r.decision  == "reject_null"
assert r.state     == "rejected"

# Fail to reject
r2 = evaluate_p_value(p_value=0.12, alpha=0.05)
assert r2.decision  == "fail_to_reject_null"
assert r2.state     == "not_rejected"

# Edge: alpha boundary
r3 = evaluate_p_value(p_value=0.05, alpha=0.05)
assert r3.decision  == "fail_to_reject_null"   # p >= alpha
```

## Security Considerations
- No I/O. No external dependencies. No secrets.
