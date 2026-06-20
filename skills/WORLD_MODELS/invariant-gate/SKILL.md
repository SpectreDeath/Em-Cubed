---
name: invariant-gate
version: 1.0.0
domain: WORLD_MODELS
surfaces:
  - z3
  - python
description: >
  External constraint verification using Z3 SMT solver and Python surface.
  Evaluates whether a proposed change meets high-level non-code criteria
  such as organizational accessibility audits, compliance standards, or
  business roadmaps.
purpose: >
  Treat non-code constraints as strict logical assertions and reject code
  patches that violate them before the harness builder compiles them.
dependencies:
  - skill-world-designer
inputs:
  proposed_patch:
    type: object
    required: true
    description: "Proposed code change to verify"
  accessibility_rules:
    type: object
    required: false
    description: "Accessibility constraint rules (e.g., Section 508, WCAG)"
  compliance_rules:
    type: object
    required: false
    description: "Compliance constraint rules (e.g., GDPR, HIPAA)"
  business_rules:
    type: object
    required: false
    description: "Business roadmap constraints"
outputs:
  gate_result:
    type: string
    description: "passed | failed | inconclusive"
  violations:
    type: array
    description: "List of constraint violations found"
  proof:
    type: object
    description: "Z3 proof and model if passed"
tags:
  - z3
  - smt
  - invariant
  - constraint-verification
  - accessibility
  - compliance
  - gate
---

# Invariant Gate

External constraint verification using Z3 SMT solver. Treats non-code
constraints as strict logical assertions and rejects violating patches.

## Tick Protocol

| Id | Surface | Action                                                |
|----|---------|-------------------------------------------------------|
| 1  | Python  | Parse `proposed_patch` and constraint rules           |
| 2  | Z3      | Encode accessibility rules as SMT assertions          |
| 3  | Z3      | Encode compliance rules as SMT assertions             |
| 4  | Z3      | Encode business rules as SMT assertions               |
| 5  | Z3      | Check `sat` across all constraint families            |
| 6  | Z3      | If `sat`, extract model; if `unsat`, extract unsat core|
| 7  | Python  | Aggregate results into `gate_result` and `violations` |

If any constraint family returns `unsat` -> emit `gate_result: failed`.

## Surfaces

### Z3 Surface

```python
from z3 import *

def verify_accessibility(patch_metrics, rules):
    solver = Solver()
    has_labels = Bool("has_labels")
    has_aria = Bool("has_aria")
    keyboard_nav = Bool("keyboard_nav")
    solver.add(has_labels == rules.get("requires_labels", True))
    solver.add(has_aria == rules.get("requires_aria", True))
    solver.add(keyboard_nav == rules.get("requires_keyboard", True))
    if solver.check() == sat:
        return {"passed": True, "model": solver.model()}
    return {"passed": False, "violations": ["accessibility constraint failed"]}
```

### Python Surface

```python
surfaces.invariant_gate.evaluate(
    proposed_patch={...},
    accessibility_rules={...},
    compliance_rules={...},
    business_rules={...}
)
```

## Capability Contract

**Inputs:**

- `proposed_patch` *(object, required)* — Proposed code change to verify.
- `accessibility_rules` *(object, optional)* — Accessibility constraint rules (e.g., Section 508, WCAG).
- `compliance_rules` *(object, optional)* — Compliance constraint rules (e.g., GDPR, HIPAA).
- `business_rules` *(object, optional)* — Business roadmap constraints.

**Outputs:**

- `gate_result` *(string)* — `passed`, `failed`, or `inconclusive`.
- `violations` *(array)* — List of constraint violations found.
- `proof` *(object)* — Z3 model and satisfaction evidence.

## Composition

- `skill-world-designer` — Uses `gate_result` to approve simulation outcomes.
- `skill-harness-builder` — Blocks compilation if `gate_result: failed`.
- `design-sync` —Provides component context for accessibility checking.
