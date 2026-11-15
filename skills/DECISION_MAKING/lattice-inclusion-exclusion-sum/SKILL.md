---
name: lattice-inclusion-exclusion-sum
domain: DECISION_MAKING
version: 1.0.0
surfaces:
  - python
  - prolog
description: Implements the general inclusion-exclusion sum rule for overlapping logical propositions defined over a lattice structure using meet and join intersections. Resolves algebraic lattice meet $\text{meet}(A, B) = A \land B$ and join $\text{join}(A, B) = A \lor B$ relationships in Prolog, looks up marginal and conditional probabilities, and computes the composite disjunctive probability $P(A \lor B \mid C) = P(A \mid C) + P(B \mid C) - P(A \land B \mid C)$ in Python. Use when combining overlapping hypothesis spaces, calculating union probabilities on posets, or validating lattice probability distributions.
purpose: Compute lattice-native inclusion-exclusion probability sums with structural meet/join topology in Prolog.
dependencies:
  - ONTOLOGY/inverse-zeta-generalizer
tags:
  - lattice-sum
  - inclusion-exclusion
  - meet-join
  - disjunctive-probability
  - bayesian-lattice
  - prolog-topology
inputs:
  probability_distribution:
    type: object
    required: true
    description: 'Probability mapping over lattice elements (e.g. `{''A'': 0.4, ''B'': 0.3, ''meet(A,B)'': 0.1, ''top'': 1.0}`).'
  target_elements:
    type: array
    required: true
    description: Pair or list of target proposition elements to combine `['A', 'B']`.
  condition:
    type: string
    required: false
    description: Conditioning element $C$ (default `'top'` for unconditional).
outputs:
  combined_probability:
    type: number
    description: Evaluated union probability $P(A \lor B \mid C)$ computed via lattice inclusion-exclusion.
  decomposition:
    type: object
    description: Breakdown of individual marginal and intersection terms.
  intersection_element:
    type: string
    description: Structural meet element identifier representing $A \land B$.
---

# Lattice Inclusion-Exclusion Sum Engine

`lattice-inclusion-exclusion-sum` evaluates disjunctive probabilities across overlapping logical propositions by resolving their algebraic **meet and join operations in Prolog** and computing the **inclusion-exclusion sum rule** in **Python**:

$$P(A \lor B \mid C) = P(A \mid C) + P(B \mid C) - P(A \land B \mid C)$$

$$P\left(\bigvee_{i=1}^n A_i \;\middle|\; C\right) = \sum_{k=1}^n (-1)^{k-1} \sum_{1 \le i_1 < \dots < i_k \le n} P\left(\bigwedge_{j=1}^k A_{i_j} \;\middle|\; C\right)$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Inclusion-Exclusion Progression

```
[1. Distribution Ingest & Target Audit] → [2. Prolog Meet/Join Resolution] → [3. Visual Brief] → [4. Checkpoint] → [5. Sum Rule Calculation & Emit]
```

### Stage 1: Distribution Ingest & Target Audit
1. Ingest `probability_distribution`, `target_elements` (length $\ge 2$), and optional `condition`.
2. Verify that target elements exist in the lattice element universe.

> **Completion criterion**: Clean lattice elements and distribution map verified.

---

### Stage 2: Prolog Meet/Join Resolution
1. Query Prolog lattice module for the greatest lower bound (meet):
   ```prolog
   meet(A, B, IntersectionElement).
   ```
2. Verify that conditioning element $C$ is structurally consistent ($C \implies \text{Top}$).

> **Completion criterion**: Structural meet element resolved.

---

### Stage 3: The Visual Brief
For disjunctive probability unions and lattice overlaps, generate an interactive brief:
- **Location**: Write to `%TEMP%\lattice-sum-brief-<timestamp>.html` (Windows) or `/tmp/lattice-sum-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render Hasse diagram of lattice elements with highlighted target nodes, Venn/Euler term breakdown, and inclusion-exclusion arithmetic bar chart.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before finalizing combination:
1. Verify individual terms: $P(A \mid C) \ge 0$, $P(B \mid C) \ge 0$, $P(A \land B \mid C) \le \min(P(A \mid C), P(B \mid C))$.
2. Verify sum rule bounds: $0.0 \le P(A \lor B \mid C) \le 1.0$.

> **Completion criterion**: Fréchet probability bounds verified.

---

### Stage 5: Sum Rule Calculation & Output Emission
1. Calculate disjunctive sum: $P_{\text{union}} = P(A \mid C) + P(B \mid C) - P(A \land B \mid C)$.
2. Record term decomposition dictionary.
3. Emit complete `LatticeSumResult` record.

> **Completion criterion**: Full inclusion-exclusion sum payload emitted.

---

## Surface References

### Prolog Lattice Surface

```prolog
:- module(lattice_sum, [
    meet/3,
    join/3,
    condition_valid/2
]).

meet(A, B, Intersection) :-
    glbf(A, B, Intersection).

join(A, B, Union) :-
    lub(A, B, Union).

condition_valid(top, _).
condition_valid(C, Element) :- implies(C, Element).
```

### Python Calculation Surface

```python
from typing import Dict, List, Any, Optional

def compute_lattice_sum(
    probability_distribution: Dict[str, float],
    target_elements: List[str],
    condition: Optional[str] = "top"
) -> Dict[str, Any]:
    if len(target_elements) < 2:
        raise ValueError("insufficient_elements: Requires at least 2 target elements.")
        
    a, b = target_elements[0], target_elements[1]
    
    # Lookup individual and intersection probabilities
    p_a = probability_distribution.get(a, probability_distribution.get(f"P({a}|{condition})", 0.0))
    p_b = probability_distribution.get(b, probability_distribution.get(f"P({b}|{condition})", 0.0))
    
    meet_key1 = f"meet({a},{b})"
    meet_key2 = f"meet({b},{a})"
    meet_key3 = f"{a}_and_{b}"
    
    p_meet = probability_distribution.get(
        meet_key1,
        probability_distribution.get(
            meet_key2,
            probability_distribution.get(meet_key3, 0.0)
        )
    )
    
    # Fréchet inequality validation
    if p_meet > min(p_a, p_b) + 1e-6:
        raise ValueError(f"frechet_violation: P(A and B) = {p_meet} > min({p_a}, {p_b}).")
        
    p_union = p_a + p_b - p_meet
    p_union = max(0.0, min(1.0, p_union))
    
    return {
        "combined_probability": round(p_union, 6),
        "decomposition": {
            "P(A|C)": p_a,
            "P(B|C)": p_b,
            "P(A and B|C)": p_meet,
            "formula": "P(A) + P(B) - P(A and B)"
        },
        "intersection_element": meet_key1
    }
```

---

## Anti-Patterns & Guardrails

- **Venn Diagram Assumptions on Non-Distributive Lattices** — Applying standard inclusion-exclusion on lattices where the distributive law fails ($A \land (B \lor C) \neq (A \land B) \lor (A \land C)$).
- **Fréchet Bound Violations** — Allowing $P(A \land B) > \min(P(A), P(B))$, indicating corrupted joint distributions.
- **Double Counting Disjoint Elements** — Subtracting non-zero meet terms for mutually exclusive propositions where $\text{meet}(A, B) = \bot$ ($P(\bot) = 0$).
