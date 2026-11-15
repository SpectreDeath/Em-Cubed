---
name: monadic-surface-functor
domain: ONTOLOGY
version: 1.0.0
surfaces:
  - python
  - prolog
  - z3
  - datalog
description: 'Category-theoretic surface functor mapping (F: C -> D) and monadic workflow coprocessor. Formulates structure-preserving morphisms and monadic bind (>>=) pipelines that lift and transform state representations sequentially across Python, Prolog, Z3 SMT, and Datalog with zero structural loss. Use when orchestrating cross-surface reasoning pipelines, chaining symbolic solvers monadically, or verifying categorical functor laws.'
purpose: Execute structure-preserving category-theoretic surface functors and monadic bind chains across heterogeneous computational surfaces.
dependencies: []
tags:
  - category-theory
  - surface-functors
  - monadic-workflows
  - z3-smt
  - prolog
  - datalog
inputs:
  initial_state:
    type: object
    required: true
    description: Source domain object or triple set in starting surface representation.
  functor_pipeline:
    type: array
    required: true
    description: "Ordered sequence of target surfaces, e.g. ['python', 'prolog', 'z3']."
  bind_action:
    type: string
    required: false
    description: Monadic computation action to evaluate at terminal surface.
outputs:
  lifted_monad:
    type: object
    description: Transformed monadic container with execution payload and error channel.
  functor_trace:
    type: array
    description: Step-by-step categorical morphism transition trace.
  morphism_valid:
    type: boolean
    description: True if functor identity and composition laws hold across all pipeline transitions.
---

# Monadic Surface Functor Engine

`monadic-surface-functor` implements the **Category-Theoretic Monadic Coprocessor & Surface Functor Engine** in `Em-Cubed`. It treats execution surfaces ($\mathcal{C}_{\text{Python}}, \mathcal{C}_{\text{Prolog}}, \mathcal{C}_{\text{Z3}}, \mathcal{C}_{\text{Datalog}}$) as distinct categories and orchestrates state transitions via structure-preserving functors $F: \mathcal{C} \to \mathcal{D}$ and monadic bind ($\gg=$) combinators.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Monadic Pipeline Progression

```
[1. Source State Invariant Audit] → [2. Functor Morphism Mapping] → [3. Visual Brief] → [4. Checkpoint] → [5. Monadic Bind & Evaluation]
```

### Stage 1: Source State & Category Audit
1. Verify initial state structure in source category $\mathcal{C}_0$.
2. Check that target pipeline surfaces belong to supported morphism registry.

> **Completion criterion**: Source object typed and pipeline stages validated.

---

### Stage 2: Functor Morphism Mapping ($F: \mathcal{C} \to \mathcal{D}$)
1. Apply structure-preserving object maps ($F(A)$) and arrow maps ($F(f)$).
2. Ensure functor laws hold:
   - **Identity**: $F(\text{id}_A) = \text{id}_{F(A)}$
   - **Composition**: $F(g \circ f) = F(g) \circ F(f)$

> **Completion criterion**: Surface representation lifted across categories without semantic distortion.

---

### Stage 3: The Visual Brief
For multi-stage category pipelines, generate a visual morphism commutative diagram brief:
- **Location**: Write to `%TEMP%\monadic-functor-brief-<timestamp>.html` (Windows) or `/tmp/monadic-functor-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render commutative diagram showing functor arrows between surface nodes.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before executing heavy symbolic solvers or mutating external stores:
1. Verify that the intermediate monad has not short-circuited into a failure state ($\text{Nothing} / \text{Left}(e)$).
2. If schema mismatches occurred during functor projection, pause and return diagnostic mapping error.

> **Completion criterion**: Pipeline state verified in valid monadic wrapper ($\text{Just} / \text{Right}$).

---

### Stage 5: Monadic Bind ($\gg=$) & Terminal Execution
1. Bind terminal computation action onto lifted monadic state.
2. Execute solver verification in terminal surface (e.g. Z3 satisfiability check).
3. Emit output container with transition trace and verification flag.

> **Completion criterion**: Monadic pipeline terminates with `morphism_valid: true` and evaluated result.

---

## Surface References

### Python Monadic Functor Surface

```python
from typing import Any, List, Dict

class SurfaceMonad:
    def __init__(self, value: Any, surface: str, trace: List[str] = None):
        self.value = value
        self.surface = surface
        self.trace = trace or [f"unit({surface})"]

    def bind(self, transform_fn):
        new_val, new_surface, step_desc = transform_fn(self.value, self.surface)
        return SurfaceMonad(new_val, new_surface, self.trace + [step_desc])

def functor_python_to_prolog(val: Dict[str, Any], curr_surface: str):
    # Map dictionary state to Prolog fact strings
    facts = [f"state({k}, '{v}')." for k, v in val.items()]
    return facts, "prolog", "Functor: Python -> Prolog"

def functor_prolog_to_z3(facts: List[str], curr_surface: str):
    # Map Prolog facts to Z3 clause strings
    z3_clauses = [f"assert({f.replace('.', '')})" for f in facts]
    return z3_clauses, "z3", "Functor: Prolog -> Z3 SMT"
```

---

## Anti-Patterns & Guardrails

- **Non-Functorial Mapping** — Dropping relationships or properties during surface translation that cannot be reconstructed in downstream surfaces.
- **Unchecked Monadic Exception Swallowing** — Catching and silently ignoring bind failures instead of propagating formal `Left(Error)` monadic states.
- **Law-Breaking Functors** — Implementing surface adapters where $F(g \circ f) \neq F(g) \circ F(f)$.
