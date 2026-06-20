---
name: inverse-zeta-generalizer
version: 1.0.0
domain: LOGIC
surfaces:
  - python
  - z3
description: >
  Generalizes the binary inverse zeta function to a continuous [0, 1] range
  over a distributive lattice, mapping truth values to probability densities
  for incomplete information.
purpose: >
  Provide the probability foundation for Jaynesian reasoning: map lattice
  implication strengths to continuous degrees of belief.
dependencies:
  - distributive-lattice-validator
inputs:
  lattice_structure:
    type: object
    required: true
    description: "Verified distributive lattice from distributive-lattice-validator"
  observation:
    type: object
    required: true
    description: "Observed evidence with lattice element weights"
  smoothing:
    type: number
    required: false
    description: "Pseudocount smoothing factor (default: 1.0)"
outputs:
  probability_distribution:
    type: object
    description: "Continuous probability distribution over lattice elements"
  information_gain:
    type: number
    description: "KL divergence from prior to posterior"
  consistency_check:
    type: boolean
    description: "True if distribution satisfies Jaynes consistency axioms"
tags:
  - zeta
  - probability
  - lattice
  - jaynes
  - python
  - z3
---

# Inverse Zeta Generalizer

Generalizes the binary inverse zeta function to continuous [0,1] over a
distributive lattice. Python computes densities. Z3 verifies consistency.

## Tick Protocol

| Id | Surface | Action                                                |
|----|---------|-------------------------------------------------------|
| 1  | Python  | Parse `lattice_structure` and `observation`           |
| 2  | Python  | Compute prior pseudocounts from lattice structure     |
| 3  | Python  | Apply Bayes update to obtain posterior distribution   |
| 4  | Z3      | Encode Jaynes consistency axioms as assertions        |
| 5  | Z3      | Verify `sat` for consistency                         |
| 6  | Python  | Compute `information_gain` and return results         |

## Surfaces

### Python Surface

```python
from em_cubed.skills.logic.inverse_zeta_generalizer import generalize_zeta

result = generalize_zeta(
    lattice_structure={"elements": ["A", "B", "C"], "order": [["A","B"],["B","C"]]},
    observation={"evidence_for": "B", "weight": 0.7},
    smoothing=1.0
)
```

### Z3 Surface

```python
from z3 import *

def verify_jaynes_consistency(probabilities):
    s = Solver()
    for p in probabilities:
        s.add(Real(p) >= 0)
        s.add(Real(p) <= 1)
    # Sum-to-one axiom
    s.add(Sum([Real(p) for p in probabilities]) == 1)
    # Cox-Jaynes consistency: P(A and B) = P(A) * P(B|A)
    return s.check() == sat
```

## Capability Contract

**Inputs:**

- `lattice_structure` *(object, required)* — Verified distributive lattice from `distributive-lattice-validator`.
- `observation` *(object, required)* — Observed evidence with lattice element weights.
- `smoothing` *(number, optional)* — Pseudocount smoothing factor. Default `1.0`.

**Outputs:**

- `probability_distribution` *(object)* — Continuous probability distribution over lattice elements.
- `information_gain` *(number)* — KL divergence from prior to posterior.
- `consistency_check` *(boolean)* — True if distribution satisfies Jaynes consistency axioms.

## Composition

- `distributive-lattice-validator` — Consumes its lattice output.
- `lattice-inclusion-exclusion-sum` — Uses probability distribution.
- `associative-chaining-product` — Chains distributions across lattice paths.
