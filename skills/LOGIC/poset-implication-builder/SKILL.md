---
name: poset-implication-builder
domain: LOGIC
version: 1.0.0
surfaces:
- prolog
- z3
description: 'Constructs a partially ordered set (poset) from a set of propositions ordered by strict logical implication.
  Prolog derives implication rules; Z3 verifies the poset structure.

  '
purpose: 'Take an arbitrary set of propositions and build the corresponding poset so that probability values can emerge as
  a continuous generalization of the inverse zeta function over the lattice.

  '
dependencies:
- distributive-lattice-validator
tags:
- lattice
- poset
- implication
- prolog
- z3
- logic
inputs:
  propositions:
    type: array
    required: true
    description: List of proposition strings or identifiers
  implication_rules:
    type: array
    required: false
    description: Optional explicit implication rules
outputs:
  poset_facts:
    type: object
    description: Prolog facts representing the implication order
  poset_verified:
    type: boolean
    description: True if Z3 confirms valid poset structure
  top_element:
    type: string
    description: Proposition that implies all others (top)
  bottom_element:
    type: string
    description: Proposition implied by all others (bottom)
---

# Poset Implication Builder

Constructs a poset from propositions under strict logical implication.
Prolog derives the order; Z3 verifies antisymmetry and transitivity.

## Tick Protocol

| Id | Surface | Action                                                |
|----|---------|-------------------------------------------------------|
| 1  | Python  | Parse `propositions` and `implication_rules`         |
| 2  | Prolog  | Assert proposition facts and implication clauses      |
| 3  | Prolog  | Compute transitive closure of implication relation    |
| 4  | Z3      | Assert poset axioms (reflexive, antisymmetric, transitive) |
| 5  | Z3      | Check `sat` to confirm no contradictions              |
| 6  | Python  | Extract `top_element` and `bottom_element`            |

## Surfaces

### Prolog Surface

```prolog
% Facts
proposition(rain).
proposition(wet).
proposition(slippery).

% Implication rules
implies(rain, wet).
implies(wet, slippery).

% Transitive closure
implies_transitive(X, Z) :- implies(X, Y), implies_transitive(Y, Z).

% Poset checks
poset_axiom(reflexive) :- forall(X, implies(X, X)).
poset_axiom(antisymmetric) :- forall(X,Y, (implies(X,Y), implies(Y,X) -> X == Y)).
poset_axiom(transitive) :- forall(X,Y,Z, (implies(X,Y), implies(Y,Z) -> implies(X,Z))).

% Top and bottom
top_element(X) :- forall(Y, implies(X, Y)).
bottom_element(X) :- forall(Y, implies(Y, X)).
```

### Z3 Surface

```python
from z3 import *

def verify_poset(elements, relations):
    s = Solver()
    # Encode elements as Ints
    idx = {e: i for i, e in enumerate(elements)}
    n = len(elements)
    # Adjacency matrix: rel[i][j] = True iff elements[i] implies elements[j]
    rel = [Bool(f"rel_{i}_{j}") for i in range(n) for j in range(n)]
    # Reflexive
    for i in range(n):
        s.add(rel[i*n + i])
    # Antisymmetric: rel[i][j] and rel[j][i] implies i == j
    for i in range(n):
        for j in range(n):
            if i != j:
                s.add(Implies(And(rel[i*n + j], rel[j*n + i]), False))
    # Transitive
    for i in range(n):
        for j in range(n):
            for k in range(n):
                s.add(Implies(And(rel[i*n + j], rel[j*n + k]), rel[i*n + k]))
    # Assert known relations
    for a, b in relations:
        s.add(rel[idx[a]*n + idx[b]])
    return s.check() == sat
```

## Capability Contract

**Inputs:**

- `propositions` *(array, required)* — List of proposition strings or identifiers.
- `implication_rules` *(array, optional)* — Explicit implication rules `[{"antecedent": str, "consequent": str}]`.

**Outputs:**

- `poset_facts` *(object)* — Prolog facts representing the implication order.
- `poset_verified` *(boolean)* — True if Z3 confirms valid poset structure.
- `top_element` *(string)* — Proposition that implies all others.
- `bottom_element` *(string)* — Proposition implied by all others.

## Composition

- `distributive-lattice-validator` — Receives `poset_facts` for lattice check.
- `inverse-zeta-generalizer` — Uses poset structure for probability mapping.
- `iterated-dominance-solver` — Uses poset for strategy dominance ordering.
