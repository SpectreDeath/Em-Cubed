---
name: poset-implication-builder
domain: LOGIC
version: 1.0.0
surfaces:
  - prolog
  - z3
  - python
description: Constructs and verifies a partially ordered set (poset) from propositions ordered by strict logical implication. Derives transitive implication closures in Prolog and mathematically proves poset axioms (reflexivity, antisymmetry, transitivity) using Z3 SMT Boolean relation matrices. Use when building causal implication orders, structuring proposition spaces for lattice validation, or isolating top/bottom lattice extrema.
purpose: Construct a verified partially ordered set (poset) from propositions under strict logical implication as a foundation for lattice reasoning.
dependencies: []
tags:
  - poset
  - implication-ordering
  - transitive-closure
  - prolog
  - z3-smt
  - logic
inputs:
  propositions:
    type: array
    required: true
    description: List of proposition strings or discrete state identifiers.
  implication_rules:
    type: array
    required: false
    description: 'Explicit implication pairs `[{"antecedent": str, "consequent": str}]`.'
outputs:
  poset_facts:
    type: object
    description: Prolog facts representing the transitive implication order.
  poset_verified:
    type: boolean
    description: True if Z3 SMT solver confirms reflexivity, antisymmetry, and transitivity.
  top_element:
    type: string
    description: Proposition that implies all others (universal upper bound / True).
  bottom_element:
    type: string
    description: Proposition implied by all others (universal lower bound / False).
---

# Poset Implication Builder Engine

`poset-implication-builder` transforms arbitrary sets of logical propositions into formal partially ordered sets (posets) $(\mathcal{P}, \le)$. It computes the transitive closure of implication in Prolog, extracts unique top and bottom extrema, and proves the three fundamental poset axioms via Z3 SMT boolean matrices.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Poset Construction Progression

```
[1. Proposition Invariant Audit] → [2. Transitive Closure in Prolog] → [3. Visual Brief] → [4. Checkpoint] → [5. Z3 Poset Verification]
```

### Stage 1: Proposition & Rule Invariant Audit
1. Ingest `propositions` list ($N \ge 2$) and ensure uniqueness of proposition identifiers.
2. Ingest explicit `implication_rules` and verify that all antecedents and consequents exist in `propositions`.

> **Completion criterion**: Proposition dictionary and direct edge list validated with zero dangling identifiers.

---

### Stage 2: Transitive Closure Derivation (Prolog)
1. Assert direct implication facts into Prolog knowledge base: `implies(P, Q).`
2. Compute full transitive closure:
   ```prolog
   implies_transitive(X, Z) :- implies(X, Y), implies_transitive(Y, Z).
   ```
3. Identify universal bounds:
   - **Top Element ($\top$)**: $\forall Y \in \mathcal{P}, \top \implies Y$
   - **Bottom Element ($\bot$)**: $\forall Y \in \mathcal{P}, Y \implies \bot$

> **Completion criterion**: Transitive closure matrix computed and top/bottom candidate elements isolated.

---

### Stage 3: The Visual Brief
For complex implication chains, generate an interactive Hasse diagram brief:
- **Location**: Write to `%TEMP%\poset-builder-brief-<timestamp>.html` (Windows) or `/tmp/poset-builder-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render the Hasse diagram showing proposition nodes and transitive reduction edges.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before forwarding poset facts to downstream lattice validators:
1. Verify that no strict circular implication cycles exist ($A \implies B \land B \implies A$ for $A \neq B$).
2. If cyclic equivalences are detected, pause and collapse equivalent propositions into single quotient equivalence classes.

> **Completion criterion**: Implication graph verified acyclic (DAG) or quotient collapsed.

---

### Stage 5: Z3 Axiomatic Poset Verification
1. Encode $N \times N$ Boolean relation matrix $R[i][j]$ in Z3:
   - **Reflexivity**: $\forall i, R[i][i] = \text{True}$
   - **Antisymmetry**: $\forall i \neq j, R[i][j] \land R[j][i] \implies \text{False}$
   - **Transitivity**: $\forall i, j, k, R[i][j] \land R[j][k] \implies R[i][k]$
2. Execute solver check. If `sat`, emit verified `poset_facts` and extrema.

> **Completion criterion**: Z3 solver returns `sat` confirming valid mathematical poset structure.

---

## Surface References

### Prolog Transitive Closure Surface

```prolog
% Facts
proposition(rain).
proposition(wet).
proposition(slippery).

% Direct rules
implies(rain, wet).
implies(wet, slippery).

% Reflexive base case & transitive closure
implies_transitive(X, X) :- proposition(X).
implies_transitive(X, Z) :- implies(X, Y), implies_transitive(Y, Z).

% Extrema
top_element(X) :- proposition(X), forall(proposition(Y), implies_transitive(X, Y)).
bottom_element(X) :- proposition(X), forall(proposition(Y), implies_transitive(Y, X)).
```

### Z3 SMT Poset Matrix Surface

```python
from typing import List, Tuple, Dict, Any
from z3 import Solver, Bool, Implies, And, sat

def verify_poset_axioms(elements: List[str], direct_edges: List[Tuple[str, str]]) -> Dict[str, Any]:
    n = len(elements)
    idx = {e: i for i, e in enumerate(elements)}
    s = Solver()
    
    # R[i][j] is True iff elements[i] implies elements[j]
    R = [[Bool(f"R_{i}_{j}") for j in range(n)] for i in range(n)]
    
    # 1. Reflexivity
    for i in range(n):
        s.add(R[i][i])
        
    # 2. Antisymmetry
    for i in range(n):
        for j in range(n):
            if i != j:
                s.add(Implies(And(R[i][j], R[j][i]), False))
                
    # 3. Transitivity
    for i in range(n):
        for j in range(n):
            for k in range(n):
                s.add(Implies(And(R[i][j], R[j][k]), R[i][k]))
                
    # Assert given edges
    for u, v in direct_edges:
        if u in idx and v in idx:
            s.add(R[idx[u]][idx[v]])
            
    is_poset = s.check() == sat
    return {
        "poset_verified": is_poset,
        "elements_count": n,
        "edges_count": len(direct_edges)
    }
```

---

## Anti-Patterns & Guardrails

- **Unchecked Implication Cycles** — Allowing $A \implies B \implies C \implies A$ without collapsing into an equivalence class $[A]$, which violates the antisymmetry axiom.
- **Dangling Implication Rules** — Referencing propositions in implication rules that are not declared in the proposition set.
- **Missing Reflexive Closure** — Omitting $P \implies P$ in Prolog rules, causing failure in least-upper-bound and greatest-lower-bound queries.
