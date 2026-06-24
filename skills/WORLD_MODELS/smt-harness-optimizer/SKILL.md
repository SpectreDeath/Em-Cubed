---
name: smt-harness-optimizer
domain: WORLD_MODELS
version: 1.0.0
surfaces:
- python
- z3
description: 'SMT-bounded harness optimizer that formally verifies which agent harness pattern (chaining, routing, or delegation)
  is safest and most token-efficient for a given objective. Encodes resource budgets as SMT assertions and proves correctness
  before deployment.

  '
purpose: 'Automatically decide the optimal harness topology for an agent task, formally proving that the chosen design satisfies
  token, time, and security constraints.

  '
dependencies:
- dag-task-scheduler
tags:
- z3
- smt
- harness
- optimizer
- proof
- formal-verification
- token-efficiency
inputs:
  resource_budgets:
    type: object
    required: true
    description: 'Budget constraints: {max_tokens, max_time_ms, max_sub_agents, security_level}'
  candidate_topologies:
    type: array
    required: true
    description: List of harness topology candidates to evaluate
  objective:
    type: object
    required: true
    description: Task objective parameters
outputs:
  optimal_topology:
    type: object
    description: Harness topology that best satisfies constraints
  proof:
    type: object
    description: Z3 proof that constraints are satisfied
  all_scores:
    type: array
    description: Ranked list of all candidates with scores
  infeasible:
    type: array
    description: Candidates that violate hard constraints
---

# SMT-Bounded Harness Optimizer

Formally proves which harness pattern is safest and most token-efficient for a given objective.

## Tick Protocol

| Id | Surface | Action                                                |
|----|---------|-------------------------------------------------------|
| 1  | Python  | Parse `resource_budgets`, `candidate_topologies`      |
| 2  | Python  | Translate budgets into Z3 integer/boolean assertions   |
| 3  | Z3      | Push assertions; check `sat` for each candidate        |
| 4  | Z3      | If `sat`, extract model weights; compute cost score    |
| 5  | Python  | Rank candidates by cost score                          |
| 6  | Python  | Return optimal topology and proof                      |

## Surfaces

### Z3 Surface

```python
from z3 import *

def verify_harness_topology(topology, budgets):
    solver = Solver()
    max_tokens, max_time, max_agents = (
        Int("max_tokens"), Int("max_time"), Int("max_agents")
    )
    solver.add(max_tokens >= 0, max_time >= 0, max_agents >= 0)
    solver.add(max_tokens == budgets["max_tokens"])
    solver.add(max_time <= budgets["max_time_ms"])
    solver.add(max_agents <= budgets["max_sub_agents"])
    token_cost = IntVal(topology["estimated_tokens"])
    if solver.check() == sat:
        return {"valid": True, "model": solver.model()}
    return {"valid": False}
```

### Python Surface

Wraps Z3 evaluation, computes composite cost score, handles candidate ranking.

```python
surfaces.harness_optimizer.optimize(
    resource_budgets={...},
    candidate_topologies=[...],
    objective={...}
)
```

## Capability Contract

**Inputs:**

- `resource_budgets` *(object, required)* — `{"max_tokens": int, "max_time_ms": int, "max_sub_agents": int, "security_level": str}`.
- `candidate_topologies` *(array, required)* — Each entry: `{"id": str, "type": str ["chain"|"route"|"delegate"], "estimated_tokens": int, "estimated_time_ms": int, "sub_agent_count": int}`.
- `objective` *(object, required)* — `{"task_type": str, "requires_isolation": bool, "max_depth": int}`.

**Outputs:**

- `optimal_topology` *(object)* — Best candidate with full topology definition.
- `proof` *(object)* — Z3 model and satisfaction evidence.
- `all_scores` *(array)* — All candidates sorted by composite cost.
- `infeasible` *(array)* — Candidates that violate hard constraints.

## Composition

- `dag-task-scheduler` — Schedule verified harness execution.
- `observability-dashboard` — Track optimization metrics.
