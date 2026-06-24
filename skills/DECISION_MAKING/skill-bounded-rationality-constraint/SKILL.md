---
name: skill-bounded-rationality-constraint
domain: DECISION_MAKING
version: 1.0.0
surfaces:
- python
description: 'Active circuit-breaker middleware for the recursive IESDS loop in iterated-dominance-solver. Enforces fixpoint
  termination by checking iteration depth and convergence delta thresholds, preventing infinite recursion and SMT solver hangs.

  '
purpose: 'Act as a bounded rationality guardrail that forces clean early exit from the iterated dominance elimination loop
  when fixpoint is reached or computational budget is exhausted.

  '
dependencies:
- decision-making/iterated-dominance-solver
tags:
- bounded-rationality
- circuit-breaker
- fixpoint
- convergence
- recursion-guard
- python
- decision-making
inputs:
  current_iteration_k:
    type: integer
    required: true
    description: Current iteration count of the IESDS loop
  max_depth_threshold:
    type: integer
    required: true
    description: Maximum allowed iterations before forced termination
  delta_convergence:
    type: float
    required: true
    description: Minimum weight change threshold to consider converged
  previous_weights:
    type: object
    required: false
    description: Strategy weights from previous iteration dict[int, float]
  current_weights:
    type: object
    required: false
    description: Strategy weights from current iteration dict[int, float]
outputs:
  should_terminate:
    type: boolean
    description: True if loop should terminate immediately
  termination_reason:
    type: string
    description: fixpoint_reached | depth_exceeded | continue
  current_weights:
    type: object
    description: Strategy weights at current iteration (for next pass)
  iterations_performed:
    type: integer
    description: Total iterations executed so far
---

# Skill Bounded Rationality Constraint

Active circuit-breaker for recursive IESDS loops. Enforces fixpoint
termination by checking iteration depth and convergence delta thresholds.

## Tick Protocol

| Id | Surface | Action                                                |
|----|---------|-------------------------------------------------------|
| 1  | Python  | Parse `current_iteration_k`, `max_depth_threshold`, `delta_convergence` |
| 2  | Python  | Check depth: `current_iteration_k >= max_depth_threshold`? |
| 3  | Python  | If depth ok, compute max weight delta vs `previous_weights` |
| 4  | Python  | Check convergence: `max_delta < delta_convergence`?   |
| 5  | Python  | Determine `termination_reason` and `should_terminate` |
| 6  | Python  | Return control verdict to iterated-dominance-solver    |

## Surfaces

### Python Surface

```python
surfaces.skill_bounded_rationality_constraint.check(
    current_iteration_k=5,
    max_depth_threshold=10,
    delta_convergence=0.001,
    previous_weights={0: 0.30, 1: 0.25, 2: 0.20, 3: 0.25},
    current_weights={0: 0.298, 1: 0.252, 2: 0.199, 3: 0.251}
)
# Result: should_terminate=True, termination_reason="fixpoint_reached"

surfaces.skill_bounded_rationality_constraint.check(
    current_iteration_k=12,
    max_depth_threshold=10,
    delta_convergence=0.001,
    previous_weights={0: 0.30, 1: 0.25},
    current_weights={0: 0.25, 1: 0.20}
)
# Result: should_terminate=True, termination_reason="depth_exceeded"
```

## Capability Contract

**Inputs:**

- `current_iteration_k` *(integer, required)* — Current iteration count of the IESDS loop.
- `max_depth_threshold` *(integer, required)* — Maximum allowed iterations before forced termination.
- `delta_convergence` *(float, required)* — Minimum weight change threshold to consider converged.
- `previous_weights` *(object, optional)* — Strategy weights from previous iteration.
- `current_weights` *(object, optional)* — Strategy weights from current iteration.

**Outputs:**

- `should_terminate` *(boolean)* — `true` if loop should terminate immediately.
- `termination_reason` *(string)* — `fixpoint_reached`, `depth_exceeded`, or `continue`.
- `current_weights` *(object)* — Strategy weights at current iteration (for next pass).
- `iterations_performed` *(integer)* — Total iterations executed so far.

## Mathematical Foundation

Implements bounded rationality guard from Simon (1957) applied to
iterated elimination:

$$S_i^{K+1} = S_i^K \quad \text{if} \quad |w_i^{K+1} - w_i^K| < \delta \quad \forall i$$

$$K \geq K_{max} \implies \text{forced termination}$$

## Composition

- `iterated-dominance-solver` — Primary consumer; calls this skill each loop iteration.
- `skill-expected-utility-maximizer` — Receives `should_terminate` to halt EU computation.
- `skill-belief-state-updater` — Feeds weight deltas for convergence measurement.
