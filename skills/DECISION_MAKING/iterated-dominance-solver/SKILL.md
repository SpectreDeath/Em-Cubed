---
name: iterated-dominance-solver
domain: DECISION_MAKING
version: 1.0.0
surfaces:
- python
- z3
- prolog
description: 'Computes rationalizable strategy sets for finite strategic-form games using the Iterated Elimination of Strictly
  Dominated Strategies (IESDS) algorithm. Implements pure and mixed strategy dominance checks with higher-order knowledge
  recursion.

  '
purpose: 'Determine which strategies survive iterated elimination of strictly conditionally dominated strategies, producing
  the set of rationalizable strategies for each player.

  '
dependencies:
- skill-constraint-resolver
- skill-unconscious-inference
tags:
- game-theory
- iesds
- rationalizability
- dominance
- z3
- prolog
- python
- decision-making
inputs:
  game_definition:
    type: object
    required: true
    description: Strategic form game with players, strategy sets, and payoff matrices
  elimination_order:
    type: string
    required: false
    description: 'sequential | simultaneous (default: sequential)'
  max_iterations:
    type: integer
    required: false
    description: 'Maximum elimination rounds before forced stop (default: 100)'
outputs:
  rationalizable_strategies:
    type: object
    description: Surviving strategy sets for each player
  elimination_history:
    type: array
    description: Step-by-step record of eliminated strategies
  dominance_solvable:
    type: boolean
    description: True if unique strategy profile remains
  final_profile:
    type: object
    required: false
    description: Unique equilibrium profile if dominance solvable
---

# Iterated Dominance Solver

Computes rationalizable strategies using IESDS. Python runs the elimination
loop. Z3 verifies strict conditional dominance. Prolog stores game facts.

## Tick Protocol

| Id | Surface       | Action                                                |
|----|---------------|-------------------------------------------------------|
| 1  | Python        | Parse `game_definition` and initialize strategy sets  |
| 2  | Python        | Compute initial best-response sets                    |
| 3  | Z3            | Encode payoff constraints for dominance checks        |
| 4  | Z3            | Identify strictly conditionally dominated strategies  |
| 5  | Python        | Eliminate dominated strategies, update sets           |
| 6  | Python        | Check fixpoint: no change in strategy sets?           |
| 7  | Prolog        | Assert surviving strategies as game facts             |
| 8  | Python        | BR-validate final sets; compute `dominance_solvable`  |

If $S_i^{K+1} == S_i^K$ for all players, halt and output rationalizable sets.

## Surfaces

### Python Surface

```python
from em_cubed.skills.decision_making.iterated_dominance_solver import RationalizabilitySolver

solver = RationalizabilitySolver()
result = solver.solve(
    game_definition={
        "players": ["Player1", "Player2"],
        "strategy_sets": {
            "Player1": ["T", "M", "B"],
            "Player2": ["L", "R"]
        },
        "payoff_matrices": {
            "Player1": [[3, 1], [0, 2], [1, 3]],
            "Player2": [[3, 0], [1, 2]]
        }
    },
    max_iterations=100
)
```

### Z3 Surface

```python
from z3 import *

def check_strict_dominance(payoffs_a, payoffs_b, candidate_idx, opponent_set):
    s = Solver()
    mixed_a = Real("mixed_a")
    mixed_b = Real("mixed_b")
    s.add(mixed_a >= 0, mixed_b >= 0, mixed_a + mixed_b == 1)
    for opp_idx in opponent_set:
        util_candidate = payoffs_a[candidate_idx][opp_idx]
        util_mixed = mixed_a * payoffs_a[0][opp_idx] + mixed_b * payoffs_a[1][opp_idx]
        s.add(util_mixed > util_candidate)
    return s.check() == sat
```

### Prolog Surface

```prolog
% Game facts
player(player1).
player(player2).
strategy(player1, t).
strategy(player1, m).
strategy(player1, b).
strategy(player2, l).
strategy(player2, r).

payoff(player1, [t,l], 3).
payoff(player1, [t,r], 1).
payoff(player1, [m,l], 0).
payoff(player1, [m,r], 2).
payoff(player1, [b,l], 1).
payoff(player1, [b,r], 3).

payoff(player2, [t,l], 3).
payoff(player2, [t,r], 0).
payoff(player2, [m,l], 1).
payoff(player2, [m,r], 2).
payoff(player2, [b,l], 2).
payoff(player2, [b,r], 1).

% Strict dominance: s_i is dominated by mixed sigma_i if
% u_i(sigma_i, s_-i) > u_i(s_i, s_-i) for ALL s_-i in surviving set
strictly_dominated(Player, Strategy, OpponentStrategies) :-
    findall(Opp, (member(Opp, OpponentStrategies), profile(Player, Strategy, Opp, U1), profile(Player, Strategy, Opp, U2)), _),
    mixed_strategy_beats(Player, Strategy, OpponentStrategies).

% Rationalizable: not eliminated in any round K
rationalizable(Player, Strategy) :-
    strategy(Player, Strategy),
    \+ eliminated(Player, Strategy, _).
```

## Capability Contract

**Inputs:**

- `game_definition` *(object, required)* — Strategic form game with players, strategy sets (`S_i`), and payoff matrices (`u_i`).
- `elimination_order` *(string, optional)* — `sequential` or `simultaneous`. Default `sequential`.
- `max_iterations` *(integer, optional)* — Maximum elimination rounds before forced stop. Default `100`.

**Outputs:**

- `rationalizable_strategies` *(object)* — Surviving strategy sets $S_i^\infty$ for each player.
- `elimination_history` *(array)* — Step-by-step record of eliminated strategies per round.
- `dominance_solvable` *(boolean)* — `true` if unique strategy profile remains.
- `final_profile` *(object, optional)* — Unique equilibrium profile $(s_1^*, ..., s_n^*)$ if dominance solvable.

## Mathematical Foundation

Implements the IESDS algorithm from MIT OpenCourseWare Game Theory:

$$S_i^{K+1} = S_i \setminus SCD_i(S_{-i}^K)$$

$$SCD_i(S_{-i}') = \{ s_i \in S_i \mid \exists \sigma_i \in \Delta(S_i) : u_i(\sigma_i, s_{-i}) > u_i(s_i, s_{-i}) \ \forall s_{-i} \in S_{-i}' \}$$

Termination: $S_i^K = S_i^{K+1}$ for all $i$ (fixpoint reached).

## Examples

### Prisoner's Dilemma (1-step elimination)

```python
solver.solve({
    "players": ["P1", "P2"],
    "strategy_sets": {"P1": ["C", "D"], "P2": ["C", "D"]},
    "payoff_matrices": {
        "P1": [[-1, -3], [0, -1]],   # (C,C), (C,D) / (D,C), (D,D)
        "P2": [[-1, 0], [-3, -1]]
    }
})
# Output: rationalizable = {"P1": ["D"], "P2": ["D"]}, dominance_solvable = True
```

### Coordination Game (no elimination)

```python
solver.solve({
    "players": ["P1", "P2"],
    "strategy_sets": {"P1": ["T", "B"], "P2": ["L", "R"]},
    "payoff_matrices": {
        "P1": [[2, 0], [0, 1]],
        "P2": [[2, 0], [0, 1]]
    }
})
# Output: rationalizable = {"P1": ["T", "B"], "P2": ["L", "R"]}, dominance_solvable = False
```

## Composition

- `skill-constraint-resolver` — Provides dominance-checking as `solution_space`.
- `skill-unconscious-inference` — Uses `elimination_history` for probabilistic scoring.
- `skill-sensor-transducer` — Ingests raw game matrices as `normalized_data`.
