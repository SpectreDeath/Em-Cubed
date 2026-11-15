---
name: epistemological-independence-filter
domain: DECISION_MAKING
version: 1.0.0
surfaces:
  - python
  - prolog
description: Validates whether two subsystems satisfy Jaynesian logical independence based on epistemic knowledge states rather than physical randomness. Proves that knowledge covers propositions without imposing structural constraints in Prolog ($K \vdash A \land K \vdash B \land \neg \text{Constrains}(K, A, B)$), verifies product factorization $P(A \land B \mid K) = P(A \mid K) \cdot P(B \mid K)$, and constructs the direct cross-product state space $S_1 \times S_2$ in Python. Use when preventing structural dependency paradoxes, validating Bayesian factorizations, or decoupling orthogonal decision subproblems.
purpose: Validate epistemic logical independence between subsystems and construct direct cross-product spaces.
dependencies:
  - DECISION_MAKING/associative-chaining-product
tags:
  - epistemological-independence
  - jaynesian-probability
  - cross-product-space
  - logical-independence
  - knowledge-state
  - prolog-reasoning
inputs:
  system_a:
    type: object
    required: true
    description: 'First subsystem containing propositions and marginal probabilities `{''propositions'': [...], ''probabilities'': {...}}`.'
  system_b:
    type: object
    required: true
    description: 'Second subsystem containing propositions and marginal probabilities `{''propositions'': [...], ''probabilities'': {...}}`.'
  knowledge_state:
    type: object
    required: false
    description: 'Current background knowledge constraints `{''covers'': [...], ''constraints'': [...]}`.'
outputs:
  independence_status:
    type: string
    description: Qualitative status (`'independent'`, `'dependent'`, or `'inconclusive'`).
  cross_product_space:
    type: object
    description: Direct product space $S_1 \times S_2$ with joint probabilities if independent.
  knowledge_constraints:
    type: array
    description: Active constraints that restrict or violate logical independence.
---

# Epistemological Independence Filter Engine

`epistemological-independence-filter` enforces Jaynes' principle that **probability represents a state of knowledge rather than physical frequency**. It checks **epistemic constraints in Prolog** and constructs the **direct Cartesian cross-product space** in **Python**:

$$P(A \land B \mid K) = P(A \mid K) \cdot P(B \mid K) \iff \text{Independent}(A, B \mid K)$$

$$\mathcal{S}_{AB} = \mathcal{S}_A \times \mathcal{S}_B = \{ (s_a, s_b) \mid s_a \in \mathcal{S}_A, s_b \in \mathcal{S}_B \}, \quad P(s_a, s_b) = P(s_a) \cdot P(s_b)$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Independence Filter Progression

```
[1. Subsystem Ingest & Proposition Audit] → [2. Prolog Epistemic Coverage Proof] → [3. Visual Brief] → [4. Checkpoint] → [5. Cross-Product Synthesis & Emit]
```

### Stage 1: Subsystem Ingest & Proposition Audit
1. Ingest `system_a`, `system_b`, and `knowledge_state`.
2. Extract propositions and verify marginal probability normalization for both systems ($\sum P_a = 1.0, \sum P_b = 1.0$).

> **Completion criterion**: Clean subsystem propositions and probabilities verified.

---

### Stage 2: Prolog Epistemic Coverage Proof
1. Prove knowledge coverage in Prolog:
   ```prolog
   epistemologically_independent(A, B, Knowledge) :-
       knowledge_covers(Knowledge, A),
       knowledge_covers(Knowledge, B),
       \+ knowledge_constrains(Knowledge, A, B).
   ```
2. Verify that no linking constraint `link(A, B)` exists in background knowledge $K$.

> **Completion criterion**: Epistemic independence certified in Prolog.

---

### Stage 3: The Visual Brief
For epistemic decoupling and product spaces, generate an interactive brief:
- **Location**: Write to `%TEMP%\epistemological-independence-brief-<timestamp>.html` (Windows) or `/tmp/epistemological-independence-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render subsystem Venn/interaction diagram, knowledge constraint graph, and Cartesian cross-product probability grid.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before constructing product space:
1. If epistemic constraints link $A$ and $B$, set status to `'dependent'` and return active constraints without forming cross product.
2. If knowledge does not cover both propositions, set status to `'inconclusive'`.

> **Completion criterion**: Independence status classified unambiguously.

---

### Stage 5: Cross-Product Synthesis & Output Emission
1. If status is `'independent'`: compute Cartesian product of state spaces and joint probabilities $P(s_a, s_b) = P(s_a) \cdot P(s_b)$.
2. Verify that joint distribution sums to 1.0 ($\sum_{a,b} P(a, b) = 1.0$).
3. Emit complete `IndependenceResult` record.

> **Completion criterion**: Full cross-product payload emitted.

---

## Surface References

### Prolog Epistemic Surface

```prolog
:- module(epistemological_independence, [
    epistemologically_independent/3,
    knowledge_covers/2,
    knowledge_constrains/3
]).

epistemologically_independent(A, B, Knowledge) :-
    knowledge_covers(Knowledge, A),
    knowledge_covers(Knowledge, B),
    \+ knowledge_constrains(Knowledge, A, B).

knowledge_covers(Knowledge, Prop) :-
    member(covers(Prop), Knowledge).

knowledge_constrains(Knowledge, A, B) :-
    member(link(A, B), Knowledge) ;
    member(link(B, A), Knowledge).
```

### Python Calculation Surface

```python
from typing import Dict, List, Any, Optional

def filter_epistemological_independence(
    system_a: Dict[str, Any],
    system_b: Dict[str, Any],
    knowledge_state: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    k_state = knowledge_state or {}
    covers = set(k_state.get("covers", []))
    constraints = k_state.get("constraints", [])
    
    props_a = system_a.get("propositions", [])
    props_b = system_b.get("propositions", [])
    probs_a = system_a.get("probabilities", {})
    probs_b = system_b.get("probabilities", {})
    
    # 1. Epistemic coverage check
    covered_a = all(p in covers for p in props_a) if covers else True
    covered_b = all(p in covers for p in props_b) if covers else True
    
    if not (covered_a and covered_b):
        return {
            "independence_status": "inconclusive",
            "cross_product_space": None,
            "knowledge_constraints": ["insufficient_epistemic_coverage"]
        }
        
    # 2. Constraint linkage check
    active_constraints = []
    for c in constraints:
        for pa in props_a:
            for pb in props_b:
                if (c.get("from") == pa and c.get("to") == pb) or (c.get("from") == pb and c.get("to") == pa):
                    active_constraints.append(f"link({pa}, {pb})")
                    
    if active_constraints:
        return {
            "independence_status": "dependent",
            "cross_product_space": None,
            "knowledge_constraints": active_constraints
        }
        
    # 3. Construct Cartesian cross-product space
    joint_states = []
    joint_probs = {}
    for pa in props_a:
        for pb in props_b:
            state_pair = f"({pa}, {pb})"
            prob_pair = probs_a.get(pa, 1.0 / len(props_a)) * probs_b.get(pb, 1.0 / len(props_b))
            joint_states.append(state_pair)
            joint_probs[state_pair] = round(prob_pair, 6)
            
    return {
        "independence_status": "independent",
        "cross_product_space": {
            "dimensions": [len(props_a), len(props_b)],
            "states": joint_states,
            "joint_probabilities": joint_probs,
            "total_mass": round(sum(joint_probs.values()), 6)
        },
        "knowledge_constraints": []
    }
```

---

## Anti-Patterns & Guardrails

- **Conflating Physical Independence with Epistemic Independence** — Treating uncoupled physical systems as independent even when background knowledge links their states.
- **Unchecked Cartesian Probability Expansion** — Building product spaces for dependent systems, producing corrupted joint probability estimates.
- **Incomplete Knowledge Coverage** — Declaring systems independent when background knowledge contains no information about one of the subsystems.
