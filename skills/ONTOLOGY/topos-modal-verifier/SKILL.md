---
name: topos-modal-verifier
description: Demonstrates Topos Theory Subobject Classifier (Omega) truth evaluation and categorical multi-surface morphisms across Python, Prolog, and Z3.
domain: ONTOLOGY
surfaces:
  - python
  - prolog
  - z3
version: 1.0.0
---

# Topos Modal Verifier Skill

## Overview

The `topos-modal-verifier` skill demonstrates **Phase 3 Categorical Topos Engine** in `Em-Cubed`. Based on Dr. Ken Baclawski's talk (*"What is a Topos? Introduction to the Foundations of Mathematics"*), it replaces binary $\{0, 1\}$ verification sensors with the **Subobject Classifier ($\Omega$)** truth value object.

## Features

1. **Topos Subobject Classifier ($\Omega$)**: Classifies candidate states with continuous confidence $[0.0, 1.0]$, modal necessity/possibility ($\Box / \Diamond$), and temporal step windows.
2. **Categorical Surface Morphisms**: Structure-preserving mappings converting Pydantic models into Prolog facts and Z3 SMT constraint assertions.
3. **Modal Verification**: Validates that critical system invariants hold in all accessible execution worlds (Necessary $\Box$).

## Trajectory Output Example

```json
{
  "success": true,
  "final_output": "Verified Modal Assertion",
  "trajectory": [
    {
      "iteration": 1,
      "action_taken": "Evaluated Z3 SMT and Prolog Morphisms",
      "observation": "Topos Truth Omega: Confidence 0.95 (Modal: Necessary)",
      "passed_guard": true,
      "metrics": {
        "confidence": 0.95,
        "modal_type": "Necessary"
      }
    }
  ]
}
```
