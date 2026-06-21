---
Domain: DECISION_MAKING
Version: 1.0.0
Complexity: High
Type: Pipeline
Category: Decision Making
Estimated Execution Time: 5-15 minutes
name: jaynesian-layered-decision-engine
Source: manual
description: >
  Automated layered decision-making pipeline integrating belief-state
  updating, expected utility maximization, and bounded rationality
  constraints with iterated dominance elimination.
purpose: >
  Transition the framework from hard binary strategy pruning to continuous
  belief-state weighting and optimal action selection under incomplete
  information.
---

origin: manual
triggers:
  - game_theory
  - bayesian_decision
  - iterated_elimination
  - belief_state
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
  min_structural_score: 0.90
created_at: "2026-06-21T12:14:00Z"
updated_at: "2026-06-21T12:14:00Z"

## Pipeline Architecture

Sequential three-stage decision engine:

$$\text{Hard Elimination (Z3/Clingo)} \longrightarrow \text{Belief State Update (Hy)} \longrightarrow \text{EU Maximization (Python)}$$

With bounded-rationality constraint as active circuit-breaker.

### Stage 1: Hard Elimination (iterated-dominance-solver)

```python
from em_cubed.skills.decision_making.iterated_dominance_solver import RationalizabilitySolver

solver = RationalizabilitySolver()
elimination_result = solver.solve(
    game_definition={
        "players": ["Player1", "Player2"],
        "strategy_sets": {"Player1": [0, 1, 2], "Player2": [0, 1]},
        "payoff_matrices": {
            "Player1": [[3, 1], [0, 2], [1, 3]],
            "Player2": [[3, 0], [1, 2]]
        }
    },
    max_iterations=10
)

active = elimination_result["rationalizable_strategies"]["Player1"]
eliminated = elimination_result["elimination_history"][-1]["eliminated"] if elimination_result["elimination_history"] else []
```

### Stage 2: Belief State Update (skill-belief-state-updater)

```python
from em_cubed.skills.decision_making.skill_belief_state_updater import BeliefStateUpdater

belief_updater = BeliefStateUpdater()
belief_result = belief_updater.update(
    active_strategies=active,
    eliminated_strategies=eliminated,
    prior_weights={0: 0.33, 1: 0.33, 2: 0.34}
)

opponent_belief = belief_result["updated_belief_state"]
```

### Stage 3: Expected Utility Maximization (skill-expected-utility-maximizer)

```python
from em_cubed.skills.decision_making.skill_expected_utility_maximizer import ExpectedUtilityMaximizer

eu_maximizer = ExpectedUtilityMaximizer()
eu_result = eu_maximizer.select(
    my_strategies=active,
    opponent_belief_state=opponent_belief,
    payoff_matrix=[[3, 1], [0, 2], [1, 3]],
    player_observable_history=[]
)
```

### Circuit Breaker: Bounded Rationality (skill-bounded-rationality-constraint)

```python
from em_cubed.skills.decision_making.skill_bounded_rationality_constraint import BoundedRationalityConstraint

constraint = BoundedRationalityConstraint()
control_result = constraint.check(
    current_iteration_k=elimination_result.get("iterations", 0),
    max_depth_threshold=10,
    delta_convergence=0.001,
    previous_weights={0: 0.33, 1: 0.33, 2: 0.34},
    current_weights=opponent_belief
)

if control_result["should_terminate"]:
    print(f"Terminating: {control_result['termination_reason']}")
```

## Full Pipeline Execution

```python
def run_jaynesian_pipeline(game_definition, max_iterations=10, delta_threshold=0.001):
    constraint = BoundedRationalityConstraint()
    solver = RationalizabilitySolver()
    belief_updater = BeliefStateUpdater()
    eu_maximizer = ExpectedUtilityMaximizer()

    for k in range(max_iterations):
        elimination = solver.solve(game_definition, max_iterations=1)
        active = elimination["rationalizable_strategies"]["Player1"]
        eliminated = elimination["elimination_history"][-1]["eliminated"] if elimination["elimination_history"] else []

        belief = belief_updater.update(
            active_strategies=active,
            eliminated_strategies=eliminated,
            prior_weights={i: 1.0/len(active) for i in range(3)}
        )

        eu = eu_maximizer.select(
            my_strategies=active,
            opponent_belief_state=belief["updated_belief_state"],
            payoff_matrix=game_definition["payoff_matrices"]["Player1"]
        )

        ctrl = constraint.check(
            current_iteration_k=k,
            max_depth_threshold=max_iterations,
            delta_convergence=delta_threshold,
            previous_weights={} if k == 0 else belief["updated_belief_state"],
            current_weights=belief["updated_belief_state"]
        )

        game_definition["strategy_sets"]["Player1"] = active

        if ctrl["should_terminate"]:
            return {
                "pipeline": "jaynesian-layered-decision-engine",
                "optimal_action": eu["optimal_action"],
                "expected_utility": eu["expected_utility"],
                "final_belief_state": belief["updated_belief_state"],
                "termination_reason": ctrl["termination_reason"],
                "iterations": k + 1
            }
```

## Validation

### Structural Quality Test

Run `em3 validate` on all three skills:

```bash
em3 validate skills/DECISION_MAKING/skill-belief-state-updater
em3 validate skills/DECISION_MAKING/skill-expected-utility-maximizer
em3 validate skills/DECISION_MAKING/skill-bounded-rationality-constraint
```

Minimum structural quality score: **0.90**

### Integration Test

```python
result = run_jaynesian_pipeline({
    "players": ["Player1", "Player2"],
    "strategy_sets": {"Player1": [0, 1, 2], "Player2": [0, 1]},
    "payoff_matrices": {
        "Player1": [[3, 1], [0, 2], [1, 3]],
        "Player2": [[3, 0], [1, 2]]
    }
})
assert result["termination_reason"] in ["fixpoint_reached", "depth_exceeded"]
assert result["iterations"] <= 10
assert result["optimal_action"] in [0, 1, 2]
```

## Composition

- `iterated-dominance-solver` — Primary entry point for hard elimination.
- `skill-belief-state-updater` — Re-allocates probability mass after elimination.
- `skill-expected-utility-maximizer` — Selects optimal action from belief state.
- `skill-bounded-rationality-constraint` — Circuit breaker for recursive loop.
- `epistemological-independence-filter` — Validates independence for joint matrix injection.
- `lattice-inclusion-exclusion-sum` — Provides probability distribution foundation.
