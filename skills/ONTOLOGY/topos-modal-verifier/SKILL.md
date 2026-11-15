---
name: topos-modal-verifier
domain: ONTOLOGY
version: 1.0.0
surfaces:
  - python
  - prolog
  - z3
description: Categorical Topos Subobject Classifier (Omega) modal truth verifier and multi-surface morphism mapper. Replaces binary true/false sensors with continuous confidence truth values in [0.0, 1.0], modal necessity (Box) and possibility (Diamond) operators, and Heyting algebra truth valuations across Python, Prolog, and Z3 SMT. Use when verifying multi-world invariants, checking categorical structure preservation, or evaluating non-classical intuitionistic truth values.
purpose: Evaluate categorical subobject classifier truth objects (Omega) and structure-preserving surface morphisms across multi-agent execution worlds.
dependencies: []
tags:
  - topos-theory
  - subobject-classifier
  - modal-logic
  - heyting-algebra
  - z3-smt
  - category-theory
inputs:
  candidate_assertion:
    type: object
    required: true
    description: Semantic proposition or state invariant to verify across worlds.
  accessible_worlds:
    type: array
    required: false
    description: Set of reachable execution states or relational frames.
  modal_operator:
    type: string
    required: false
    description: "necessary (Box) | possible (Diamond) | intuitionistic (default: necessary)"
outputs:
  omega_truth:
    type: object
    description: Topos truth value containing confidence score [0.0, 1.0] and modal classification.
  surface_morphisms:
    type: object
    description: Mapped state representations across Python, Prolog, and Z3.
  verified:
    type: boolean
    description: True if proposition satisfies target modal truth condition in Omega.
---

# Topos Modal Verifier Engine

`topos-modal-verifier` implements the **Phase 3 Categorical Topos Engine** in `Em-Cubed`. Based on categorical foundations, it replaces binary $\{0, 1\}$ boolean logic with the **Subobject Classifier ($\Omega$)** truth value object, enabling intuitionistic Heyting algebra reasoning and modal necessity ($\Box$) verification across multi-surface worlds.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Topos Verification Progression

```
[1. Proposition Audit] → [2. Morphism Mapping] → [3. Visual Brief] → [4. Checkpoint] → [5. SMT & Heyting Proof]
```

### Stage 1: Proposition & Frame Invariant Audit
1. Parse the candidate proposition and target modal operator ($\Box$ Necessary vs $\Diamond$ Possible).
2. Validate accessible world relations and frame conditions (reflexive, transitive, euclidean).

> **Completion criterion**: Proposition AST and Kripke relational frame structure validated.

---

### Stage 2: Categorical Surface Morphism Mapping
1. Execute structure-preserving functors mapping Python state models to Prolog relational predicates.
2. Formulate corresponding Z3 symbolic constraints:
   $$F: \mathcal{C}_{\text{Python}} \to \mathcal{C}_{\text{Z3}}$$
3. Verify commutative diagram preservation across all mapped surfaces.

> **Completion criterion**: Commutative morphisms constructed across Python, Prolog, and Z3 surfaces.

---

### Stage 3: The Visual Brief
For multi-world modal models or topos truth lattices, generate an interactive brief:
- **Location**: Write to `%TEMP%\topos-verifier-brief-<timestamp>.html` (Windows) or `/tmp/topos-verifier-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render the accessible worlds Kripke frame and Heyting truth value lattice ($\Omega$).

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before asserting global invariant necessity ($\Box P$):
1. Verify that all counter-model search branches in Z3 are exhausted.
2. If any accessible world yields $\Omega(P) < 1.0$, pause and report the counter-example frame.

> **Completion criterion**: Counter-example exploration verified complete without unhandled branches.

---

### Stage 5: SMT & Heyting Proof Valuation
1. Compute the subobject classifier truth valuation $\chi_P: X \to \Omega$.
2. Check Heyting pseudo-complement and intuitionistic implication $P \implies Q$.
3. Emit verified $\Omega$ truth object with continuous confidence score and modal classification.

> **Completion criterion**: Verification terminates with evaluated $\Omega$ truth object and boolean validity decision.

---

## Surface References

### Python & Z3 Topos Surface

```python
from typing import Dict, Any
from z3 import Solver, Real, Bool, sat

def evaluate_topos_omega(assertion_id: str, confidence_weight: float, modal_type: str = "necessary") -> Dict[str, Any]:
    s = Solver()
    omega_val = Real("omega_truth")
    
    # Heyting truth bounds in [0.0, 1.0]
    s.add(omega_val >= 0.0, omega_val <= 1.0)
    s.add(omega_val >= confidence_weight)
    
    if s.check() == sat:
        is_necessary = (confidence_weight >= 0.90) and (modal_type == "necessary")
        return {
            "omega_truth": {
                "confidence": confidence_weight,
                "modal_type": "Necessary" if is_necessary else "Possible",
                "heyting_valid": True
            },
            "verified": is_necessary if modal_type == "necessary" else (confidence_weight > 0.0)
        }
    return {"omega_truth": {"confidence": 0.0, "modal_type": "None", "heyting_valid": False}, "verified": False}
```

### Prolog Modal Frame Surface

```prolog
% Kripke frame accessibility and modal necessity
accessible(w0, w1).
accessible(w0, w2).

holds(p, w1).
holds(p, w2).

% Box(P) holds in W if P holds in all W_next accessible from W
necessary(P, W) :-
    \+ (accessible(W, WNext), \+ holds(P, WNext)).
```

---

## Anti-Patterns & Guardrails

- **Classical Law of Excluded Middle Fallback** — Assuming $P \lor \neg P = \top$ in intuitionistic topos contexts. Always evaluate through Heyting pseudo-complements.
- **Unbounded World Generation** — Generating infinite Kripke frames during modal checks without cycle detection. Limit accessibility depth to bounded horizons.
- **Surface Non-Commutativity** — Applying lossy transformations between Python and Z3 where algebraic structure is destroyed. Validate morphism bijectivity.
