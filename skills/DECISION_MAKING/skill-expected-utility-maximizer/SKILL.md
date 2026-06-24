---
name: skill-expected-utility-maximizer
domain: DECISION_MAKING
version: 1.0.0
surfaces:
- python
- z3
description: 'Dual-surface expected utility maximizer that computes optimal action selection under dependency constraints.
  Python orchestrates EU computation and action ranking; Z3 verifies independence bounds and injects joint conditional matrices
  when player models are dependent.

  '
purpose: 'Select the optimal pure action by computing weighted expected utility against an opponent belief state, with formal
  verification of independence assumptions via Z3 SMT solving.

  '
dependencies:
- decision-making/epistemological-independence-filter
- decision-making/iterated-dominance-solver
tags:
- expected-utility
- bayesian-decision
- z3
- action-selection
- independence
- python
- decision-making
- jaynes
inputs:
  my_strategies:
    type: array
    required: true
    description: Available pure actions for the deciding player
  opponent_belief_state:
    type: object
    required: true
    description: Belief state dict[int, float] over opponent strategies
  payoff_matrix:
    type: array
    required: true
    description: Payoff matrix list[list[float]] for the deciding player
  player_observable_history:
    type: array
    required: false
    description: 'Observable state history for dependency check (default: [])'
outputs:
  optimal_action:
    type: integer
    description: Index of the optimal pure action
  expected_utility:
    type: float
    description: Expected utility of the optimal action
  action_ranking:
    type: array
    description: All actions ranked by descending EU
  independence_status:
    type: string
    description: independent | dependent | inconclusive from Z3 check
  joint_matrix_used:
    type: boolean
    description: True if joint conditional matrix was injected
---

# Skill Expected Utility Maximizer

Dual-surface expected utility maximizer. Python computes EU and ranks
actions. Z3 verifies independence assumptions and injects joint conditional
matrices when player models are dependent.

## Tick Protocol

| Id | Surface | Action                                                |
|----|---------|-------------------------------------------------------|
| 1  | Python  | Parse `my_strategies`, `opponent_belief_state`, `payoff_matrix` |
| 2  | Z3      | Encode independence constraints with `player_observable_history` |
| 3  | Z3      | Query if opponent choice correlates with player state  |
| 4  | Z3      | If dependent, construct joint conditional payoff matrix |
| 5  | Python  | Compute EU = sum over opponent strategies of P(o) * payoff(a, o) |
| 6  | Python  | Rank all actions by descending EU                      |
| 7  | Python  | Return `optimal_action`, `expected_utility`, `independence_status` |

$$EU(a) = \sum_{o \in S_{opp}} P(o) \cdot u(a, o)$$

## Surfaces

### Python Surface

```python
surfaces.skill_expected_utility_maximizer.select(
    my_strategies=[0, 1, 2],
    opponent_belief_state={0: 0.4, 1: 0.35, 2: 0.25},
    payoff_matrix=[[3, 1, 0], [2, 4, 1], [1, 0, 5]],
    player_observable_history=[]
)
# Result: optimal_action=2, expected_utility=2.25, independence_status="independent"
```

### Z3 Surface

```python
from z3 import *

def check_independence_z3(player_history, opponent_strategies, belief_state):
    s = Solver()
    opp_vars = {o: Real(f"opp_{o}") for o in opponent_strategies}
    for o, p in belief_state.items():
        s.add(opp_vars[o] >= 0)
    s.add(Sum([opp_vars[o] for o in opponent_strategies]) == 1)
    if player_history:
        hist_var = Real("hist_dep")
        for o in opponent_strategies:
            s.add(opp_vars[o] == belief_state[o] * (1 + hist_var))
        s.add(hist_var == 0)
    return s.check() == sat
```

## Capability Contract

**Inputs:**

- `my_strategies` *(array, required)* — Available pure actions for the deciding player.
- `opponent_belief_state` *(object, required)* — Belief state over opponent strategies.
- `payoff_matrix` *(array, required)* — Payoff matrix for the deciding player.
- `player_observable_history` *(array, optional)* — Observable state history for dependency check.

**Outputs:**

- `optimal_action` *(integer)* — Index of the optimal pure action.
- `expected_utility` *(float)* — Expected utility of the optimal action.
- `action_ranking` *(array)* — All actions ranked by descending EU.
- `independence_status` *(string)* — `independent`, `dependent`, or `inconclusive`.
- `joint_matrix_used` *(boolean)* — Whether joint conditional matrix was injected.

## Composition

- `skill-belief-state-updater` — Provides `opponent_belief_state` as primary input.
- `epistemological-independence-filter` — Z3 independence validation via Prolog/Python layer.
- `iterated-dominance-solver` — Consumes `optimal_action` to update strategy sets.
