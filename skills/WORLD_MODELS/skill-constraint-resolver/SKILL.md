---
name: skill-constraint-resolver
domain: WORLD_MODELS
version: 1.0.0
surfaces:
- clingo
- z3
description: 'Solves ill-posed inversion problems by computing the entire valid solution space under strict background axioms.
  Uses Clingo (ASP) or Z3 SMT to prune impossible states before a generative agent can loop.

  '
purpose: 'Address the math problem of solving one equation with multiple unknowns by establishing closed-world assumptions
  or strict background axioms and computing all valid states.

  '
dependencies:
- data-processing/skill-sensor-transducer
tags:
- constraint-solving
- ill-posed
- clingo
- z3
- asp
- smt
- pruning
- cocktail-party
inputs:
  observables:
    type: object
    required: true
    description: Observed data points defining the ill-posed problem
  background_axioms:
    type: object
    required: true
    description: Strict rules that constrain the solution space
  solver_mode:
    type: string
    required: false
    description: 'clingo (ASP) | z3 (SMT) (default: clingo)'
outputs:
  solution_space:
    type: array
    description: Complete set of valid solutions under axioms
  pruned_states:
    type: array
    description: States eliminated by constraint propagation
  derivation_trace:
    type: object
    description: Step-by-step constraint application trace
---

# Skill Constraint Resolver

Solves ill-posed inversion problems by computing the entire valid solution
space under strict background axioms. Prunes impossible states.

## Tick Protocol

| Id | Surface    | Action                                                |
|----|------------|-------------------------------------------------------|
| 1  | Python     | Parse `observables` and `background_axioms`           |
| 2  | Python     | Translate axioms into solver-native program           |
| 3  | Clingo/Z3  | Encode observations and axioms                        |
| 4  | Clingo/Z3  | Solve for all models / check `sat`                    |
| 5  | Python     | Extract solution space and pruned states              |
| 6  | Python     | Return aggregated results                             |

## Surfaces

### Clingo (ASP) Surface

Computes all valid answer sets under background axioms.

```prolog
:- dynamic architectural_component/4.
:- discontiguous architectural_component/4.

% Background axioms (closed-world):
object(solid).
light(source(above)).
coherent(object_id).

% Program injected per problem:
%   observation(Var1, Value1).
%   #const n = 3.
%   #show state/2.
```

### Z3 Surface

Formally verifies solution bounds and extracts models.

```python
from z3 import *

def solve_ill_posed(observables, axioms):
    solver = Solver()
    x = Int("x")
    y = Int("y")
    z = Int("z")
    solver.add(x + y + z == observables["sum"])
    solver.add(x >= 0, y >= 0, z >= 0)
    if solver.check() == sat:
        return [solver.model()]  # all models if multiple
    return []
```

### Python Surface

```python
surfaces.skill_constraint_resolver.solve(
    observables={"sum": 10, "count": 3},
    background_axioms={"solidity": "required", "coherence": "strict"},
    solver_mode="clingo"
)
```

## Capability Contract

**Inputs:**

- `observables` *(object, required)* — Observed data points defining the ill-posed problem.
- `background_axioms` *(object, required)* — Strict rules that constrain the solution space.
- `solver_mode` *(string, optional)* — `clingo` (ASP) or `z3` (SMT). Default `clingo`.

**Outputs:**

- `solution_space` *(array)* — Complete set of valid solutions under axioms.
- `pruned_states` *(array)* — States eliminated by constraint propagation.
- `derivation_trace` *(object)* — Step-by-step constraint application trace.

## Composition

- `skill-sensor-transducer` — Consumes transducer output as `observables`.
- `skill-invariant-filter` — Receives `solution_space` for relational extraction.
- `skill-unconscious-inference` — Receives `solution_space` for probabilistic scoring.
