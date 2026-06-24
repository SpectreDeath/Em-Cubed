---
name: skill-world-designer
domain: WORLD_MODELS
version: 1.0.0
surfaces:
- clingo
- z3
description: 'Multi-surface world simulator that evaluates proposed skill changes in a logical sandbox before execution. Clingo
  surface performs predictive simulation and logical invariant checks. Z3 surface verifies formal budget constraints.

  '
purpose: 'Run a skill definition through a logical sandbox to verify correctness, detect resource budget violations, and confirm
  invariant safety before the harness builder compiles it into an executable artifact.

  '
dependencies:
- skill-harness-builder
tags:
- world-model
- simulation
- clingo
- asp
- z3
- smt
- invariant-check
- budget-verification
- sandbox
inputs:
  skill_definition:
    type: object
    required: true
    description: Parsed SKILL.md frontmatter and body
  world_rules:
    type: string
    required: false
    description: Datalog/Clingo rules defining the simulated environment
  resource_budgets:
    type: object
    required: false
    description: Budget constraints for formal verification
  simulation_steps:
    type: integer
    required: false
    description: 'Max simulation depth (default: 1)'
outputs:
  simulation_result:
    type: object
    description: Result of predictive simulation
  invariant_check:
    type: object
    description: Logical invariant verification result
  budget_proof:
    type: object
    description: Z3 proof of budget feasibility
  readiness_verdict:
    type: string
    description: verified | contradiction | budget_exceeded | inconclusive
---

# Skill World Designer

Simulates skill execution in a logical sandbox before compilation.
Clingo handles predictive simulation. Z3 handles formal budget verification.

## Tick Protocol

| Id | Surface       | Action                                                |
|----|---------------|-------------------------------------------------------|
| 1  | Python        | Parse `skill_definition` and optional `world_rules`  |
| 2  | Python        | Validate required fields from skill_definition        |
| 3  | Clingo (ASP)  | Encode skill execution as answer-set program          |
| 4  | Clingo (ASP)  | Run simulation for `simulation_steps`                 |
| 5  | Clingo (ASP)  | Evaluate invariants; detect `UNSAT` or conflicts      |
| 6  | Z3            | Encode `resource_budgets` as SMT assertions           |
| 7  | Z3            | Check `sat`; extract model if feasible                |
| 8  | Python        | Aggregate results into `simulation_result`            |
| 9  | Return        | Readiness verdict from combined surface outputs       |

If tick 5 detects a contradiction, abort and emit readiness_verdict = contradiction.
If tick 7 returns unsat, emit readiness_verdict = budget_exceeded.

## Surfaces

### Clingo (ASP) Surface

Predictive simulation of skill execution. Encodes skill execution as an answer-set program and evaluates invariants.

```prolog
% Program injected per simulation step:
%   skill_loaded(world_simulator).
%   action(proposed_action).
%   invariant(safe_state) :- not conflict(X).
%   #show next_state/1.
%   #show invariant/1.
```

### Z3 Surface

Formal verification of resource budgets. Encodes `resource_budgets` as SMT assertions and proves feasibility before deployment.

```python
from z3 import *

def verify_budgets(skill_definition, resource_budgets):
    solver = Solver()
    token_budget = Int("token_budget")
    time_budget = Int("time_budget")
    tool_budget = Int("tool_budget")
    solver.add(token_budget >= 0, time_budget >= 0, tool_budget >= 0)
    if resource_budgets:
        solver.add(token_budget == resource_budgets.get("max_tokens", token_budget))
        solver.add(time_budget <= resource_budgets.get("max_time_ms", time_budget))
        solver.add(tool_budget == resource_budgets.get("max_tool_calls", tool_budget))
    if solver.check() == sat:
        return {"verified": True, "model": solver.model()}
    return {"verified": False}
```

## Capability Contract

**Inputs:**

- `skill_definition` *(object, required)* — Parsed SKILL.md frontmatter and body.
- `world_rules` *(string, optional)* — Datalog/Clingo rules defining the simulated environment.
- `resource_budgets` *(object, optional)* — Resource constraints for formal verification.
- `simulation_steps` *(integer, optional)* — Max simulation depth. Default `1`.

**Outputs:**

- `simulation_result` *(object)* — Result of predictive simulation with trace.
- `invariant_check` *(object)* — Logical invariant verification result.
- `budget_proof` *(object)* — Z3 model and satisfaction evidence.
- `readiness_verdict` *(string)* — `verified`, `contradiction`, `budget_exceeded`, or `inconclusive`.

## Composition

- `skill-harness-builder` — Receives verified skill definition for compilation.
- `durable-execution-engine` — Checkpoint simulation state across sessions.
- `observability-dashboard` — Track simulation metrics and invariant check results.
- `dag-task-scheduler` — Schedule simulation steps with dependencies.
