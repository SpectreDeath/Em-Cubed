---
name: distributive-lattice-validator
version: 1.0.0
domain: LOGIC
surfaces:
  - prolog
  - z3
description: >
  Verifies that a poset satisfies the distributive lattice axioms
  (unique joins and meets for all element pairs, distributivity of
  meet over join and vice versa).
purpose: >
  Confirm that the implication poset can support probability values
  as a continuous generalization of the inverse zeta function.
dependencies:
  - poset-implication-builder
inputs:
  poset_facts:
    type: object
    required: true
    description: "Prolog facts from poset-implication-builder"
  element_pairs:
    type: array
    required: false
    description: "Optional explicit pairs to test for join/meet"
outputs:
  is_distributive_lattice:
    type: boolean
    description: "True if all lattice axioms hold"
  join_table:
    type: object
    description: "Join (least upper bound) for tested pairs"
  meet_table:
    type: object
    description: "Meet (greatest lower bound) for tested pairs"
  violations:
    type: array
    description: "List of pairs violating distributivity"
tags:
  - lattice
  - poset
  - prolog
  - z3
  - distributive
  - verification
---

# Distributive Lattice Validator

Verifies that a poset satisfies the distributive lattice axioms.
Prolog computes joins and meets. Z3 checks distributivity constraints.

## Tick Protocol

| Id | Surface | Action                                                |
|----|---------|-------------------------------------------------------|
| 1  | Python  | Parse `poset_facts` and `element_pairs`              |
| 2  | Prolog  | Load implication facts and compute join/meet for pairs|
| 3  | Z3      | Encode join and meet as least-upper/greatest-lower bounds |
| 4  | Z3      | Assert distributivity: meet(x, join(y,z)) == join(meet(x,y), meet(x,z)) |
| 5  | Python  | Aggregate results into `is_distributive_lattice`     |

## Surfaces

### Prolog Surface

```prolog
% Least upper bound (join)
join(X, Y, LUB) :-
    implies_transitive(X, LUB),
    implies_transitive(Y, LUB),
    \+ (implies_transitive(LUB, Z), implies_transitive(X, Z), implies_transitive(Y, Z), Z \= LUB).

% Greatest lower bound (meet)
meet(X, Y, GLB) :-
    implies_transitive(GLB, X),
    implies_transitive(GLB, Y),
    \+ (implies_transitive(Z, X), implies_transitive(Z, Y), implies_transitive(Z, G), Z \= G), G == GLB).
```

### Z3 Surface

```python
from z3 import *

def verify_distributivity(elements, implies_rel):
    s = Solver()
    join = {}
    meet = {}
    # Load poset facts and compute join/meet for each pair
    for x in elements:
        for y in elements:
            lub = compute_lub(x, y, implies_rel)
            glb = compute_glb(x, y, implies_rel)
            join[(x,y)] = lub
            meet[(x,y)] = glb
    # Distributivity: meet(x, join(y,z)) == join(meet(x,y), meet(x,z))
    for x in elements:
        for y in elements:
            for z in elements:
                lhs = meet[(x, join[(y,z)])]
                rhs = join[(meet[(x,y)], meet[(x,z)])]
                s.add(lhs == rhs)
    return s.check() == sat
```

## Capability Contract

**Inputs:**

- `poset_facts` *(object, required)* — Prolog facts from `poset-implication-builder`.
- `element_pairs` *(array, optional)* — Explicit pairs to test for join/meet.

**Outputs:**

- `is_distributive_lattice` *(boolean)* — True if all lattice axioms hold.
- `join_table` *(object)* — Join for tested pairs.
- `meet_table` *(object)* — Meet for tested pairs.
- `violations` *(array)* — Pairs violating distributivity.

## Composition

- `poset-implication-builder` — Consumes its output as input.
- `inverse-zeta-generalizer` — Uses lattice structure for probability mapping.
