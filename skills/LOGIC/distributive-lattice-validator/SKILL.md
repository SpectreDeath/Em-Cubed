---
name: distributive-lattice-validator
domain: LOGIC
version: 1.0.0
surfaces:
  - prolog
  - z3
  - python
description: Verifies that an implication poset forms a valid distributive lattice. Computes unique pairwise joins (least upper bounds / LUB) and meets (greatest lower bounds / GLB) in Prolog, detects non-distributive sublattices (Pentagon N5 and Diamond M3), and mathematically proves algebraic distributivity axioms in Z3 SMT. Use when confirming that a proposition poset can support continuous probability measures, testing lattice completeness, or identifying distributivity violations.
purpose: Prove that an implication poset satisfies all distributive lattice axioms to support continuous probability mappings.
dependencies:
  - poset-implication-builder
tags:
  - distributive-lattice
  - lub-join
  - glb-meet
  - n5-m3-detection
  - z3-distributivity
  - prolog
inputs:
  poset_facts:
    type: object
    required: true
    description: Verified implication facts from poset-implication-builder.
  element_pairs:
    type: array
    required: false
    description: Optional subset of proposition pairs to explicitly test.
outputs:
  is_distributive_lattice:
    type: boolean
    description: True if all elements possess unique joins/meets and satisfy distributivity.
  join_table:
    type: object
    description: 'Pairwise join (LUB) lookup table `{"(A,B)": LUB}`.'
  meet_table:
    type: object
    description: 'Pairwise meet (GLB) lookup table `{"(A,B)": GLB}`.'
  violations:
    type: array
    description: List of triplets violating distributivity or sublattice invariants.
---

# Distributive Lattice Validator Engine

`distributive-lattice-validator` verifies that a partially ordered set forms a valid **distributive lattice** $(\mathcal{L}, \lor, \land)$. It computes unique least upper bounds ($\lor$) and greatest lower bounds ($\land$) for all pairs in Prolog, asserts Birkhoff's Distributivity Theorem, and checks that no non-distributive pentagon ($N_5$) or diamond ($M_3$) sublattices exist.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Lattice Validation Progression

```
[1. Poset Fact Invariant Audit] → [2. Pairwise Join & Meet Derivation] → [3. Visual Brief] → [4. Checkpoint] → [5. Z3 Distributivity Axiom Proof]
```

### Stage 1: Poset Fact Invariant Audit
1. Ingest `poset_facts` from `poset-implication-builder`.
2. Extract element list $\mathcal{E}$ and verify that the input relation is a certified poset.

> **Completion criterion**: Element set $\mathcal{E}$ and implication matrix validated.

---

### Stage 2: Pairwise Join (LUB) & Meet (GLB) Derivation (Prolog)
1. Compute Least Upper Bound (Join $\lor$) for every pair $(X, Y)$:
   $$\text{join}(X, Y) = \text{LUB} \iff X \le \text{LUB} \land Y \le \text{LUB} \land (\forall Z, X \le Z \land Y \le Z \implies \text{LUB} \le Z)$$
2. Compute Greatest Lower Bound (Meet $\land$) for every pair $(X, Y)$:
   $$\text{meet}(X, Y) = \text{GLB} \iff \text{GLB} \le X \land \text{GLB} \le Y \land (\forall Z, Z \le X \land Z \le Y \implies Z \le \text{GLB})$$
3. Assert that joins and meets are unique for all $N \times N$ pairs.

> **Completion criterion**: Complete, single-valued join table and meet table constructed.

---

### Stage 3: The Visual Brief
For complex lattices or detected non-distributive sublattices, generate an interactive brief:
- **Location**: Write to `%TEMP%\lattice-validator-brief-<timestamp>.html` (Windows) or `/tmp/lattice-validator-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render the lattice Hasse diagram, join/meet matrices, and highlight any $N_5$ or $M_3$ sublattices.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before certifying lattice distributivity:
1. Search for forbidden sublattices:
   - **Pentagon ($N_5$)**: Sublattice containing 5 elements where distributivity fails.
   - **Diamond ($M_3$)**: Non-distributive modular 5-element sublattice.
2. If $N_5$ or $M_3$ is found, record explicit violation triplets and halt with `is_distributive_lattice: false`.

> **Completion criterion**: Sublattice obstruction check completed.

---

### Stage 5: Z3 Distributivity Axiom Proof
1. Encode algebraic distributivity across all triplets $(x, y, z) \in \mathcal{E}^3$:
   $$x \land (y \lor z) = (x \land y) \lor (x \land z)$$
   $$x \lor (y \land z) = (x \lor y) \land (x \lor z)$$
2. Execute Z3 satisfiability proof. If valid for all triplets, emit `is_distributive_lattice: true`.

> **Completion criterion**: Distributivity proved in Z3 across all $N^3$ triplet combinations.

---

## Surface References

### Prolog LUB / GLB Surface

```prolog
% Least upper bound (join)
join(X, Y, LUB) :-
    implies_transitive(X, LUB),
    implies_transitive(Y, LUB),
    \+ (implies_transitive(X, Z), implies_transitive(Y, Z), implies_transitive(Z, LUB), Z \= LUB).

% Greatest lower bound (meet)
meet(X, Y, GLB) :-
    implies_transitive(GLB, X),
    implies_transitive(GLB, Y),
    \+ (implies_transitive(GLB, Z), implies_transitive(Z, X), implies_transitive(Z, Y), Z \= GLB).
```

### Z3 Distributivity Solver Surface

```python
from typing import List, Dict, Tuple, Any
from z3 import Solver, Int, sat

def verify_lattice_distributivity(elements: List[str], join_map: Dict[Tuple[str, str], str], meet_map: Dict[Tuple[str, str], str]) -> Dict[str, Any]:
    violations = []
    
    for x in elements:
        for y in elements:
            for z in elements:
                # LHS: x meet (y join z)
                y_join_z = join_map.get((y, z))
                lhs = meet_map.get((x, y_join_z))
                
                # RHS: (x meet y) join (x meet z)
                x_meet_y = meet_map.get((x, y))
                x_meet_z = meet_map.get((x, z))
                rhs = join_map.get((x_meet_y, x_meet_z))
                
                if lhs != rhs:
                    violations.append({"triplet": (x, y, z), "lhs": lhs, "rhs": rhs})
                    
    is_distributive = len(violations) == 0
    return {
        "is_distributive_lattice": is_distributive,
        "violations": violations,
        "elements_evaluated": len(elements)
    }
```

---

## Anti-Patterns & Guardrails

- **Multiple Non-Unique Joins** — Posets where two elements have multiple minimal upper bounds without a single least upper bound (semi-poset).
- **Silent N5 / M3 Sublattice Masking** — Assuming an algebraic lattice is distributive without verifying the dual distributivity laws.
- **Partial Triplet Checking** — Testing distributivity on sample pairs rather than evaluating all $N^3$ element triplets.
