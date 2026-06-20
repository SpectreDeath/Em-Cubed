---
name: world-simulator
version: 1.0.0
domain: WORLD_MODELS
surfaces:
  - python
  - datalog
  - clingo
description: >
  Multi-surface world simulator with Datalog surface for state transition logic
  and Clingo (ASP) surface for constraint-based forecasting. Agents simulate
  proposed actions in a logical sandbox before real-world execution.
purpose: >
  Lets an agent test proposed actions in a logical sandbox before executing them.
  Datalog defines environment state transition rules; Clingo performs
  constraint-based forecasting and conflict detection.
dependencies:
  - durable-execution-engine
  - dag-task-scheduler
inputs:
  world_rules:
    type: string
    required: true
    description: "Datalog/Clingo rules defining the environment"
  proposed_action:
    type: object
    required: true
    description: "Action to simulate"
  initial_state:
    type: object
    required: false
    description: "Initial fact set (empty by default)"
  simulation_steps:
    type: integer
    required: false
    description: "Max simulation depth (1 by default)"
outputs:
  next_state:
    type: object
    description: "World state after action"
  conflict:
    type: boolean
    description: "True if logical contradiction detected"
  conflict_reason:
    type: string
    description: "ASP explanation of the conflict"
  trace:
    type: array
    description: "Step-by-step simulation trace"
  surface_log:
    type: object
    description: "Per-surface execution results and timing"
tags:
  - world-model
  - simulation
  - datalog
  - clingo
  - asp
  - sandbox
  - state-transition
  - constraint-verification
---

# World Model Simulator

Multi-surface world simulator that lets an agent test proposed actions in a logical sandbox
before executing them in the real world. Datalog defines environment physics. Clingo solves
constraints. Python orchestrates.

## Tick Protocol

| Id | Surface       | Action                                             |
|----|---------------|----------------------------------------------------|
| 1  | Python        | Parse `world_rules` and `proposed_action`          |
| 2  | Python        | Load `initial_state` into Datalog fact store       |
| 3  | Python        | Generate Clingo `#program` block from action       |
| 4  | Clingo (ASP)  | Compute answer set; detect `UNSAT` or conflicts    |
| 5  | Datalog       | Apply validated state transitions                  |
| 6  | Python        | Update `current_state`, append to `trace`          |
| 7  | Python        | Repeat from tick 3 for remaining `simulation_steps` |

If tick 4 returns no valid answer set -> abort immediately with `conflict: true`.

## Surfaces

### Python Surface

Entry point and orchestration layer.

```python
surfaces.world_simulator.wms_simulate(
    world_rules="<datalog-rules>",
    proposed_action={"action": str, "params": dict},
    initial_state={},          # optional
    simulation_steps=1         # optional
)
```

### Datalog Surface

State transition rules and fact persistence.

```
% Fact:
alive(alice).

% Rule:
survives(X) :- alive(X), not conflict(X).

% Dynamic update after successful step:
+= alive(alice)
```

### Clingo (ASP) Surface

Answer-set solver that validates actions against `world_rules` constraints.

```
% Program injected per simulation step:
action(proposed_action).
#show next_state/1.
```

## Capability Contract

**Inputs:**

- `world_rules` *(string, required)* — Datalog/Clingo rules defining the environment.
- `proposed_action` *(object, required)* — Shape: `{"action": str, "params": dict}`.
- `initial_state` *(object, optional)* — Initial fact set. Default `{}`.
- `simulation_steps` *(integer, optional)* — Max simulation depth. Default `1`.

**Outputs:**

- `next_state` *(object)* — World state after the action.
- `conflict` *(boolean)* — `true` if logical contradiction detected.
- `conflict_reason` *(string)* — Human-readable ASP explanation.
- `trace` *(array)* — Ordered list of per-step trace records.
- `surface_log` *(object)* — Per-surface execution results and timing.

## Composition

- `durable-execution-engine` — Persist simulation state across sessions.
- `dag-task-scheduler` — Schedule multi-step simulation trajectories.
- `observability-dashboard` — Monitor simulation metrics.
