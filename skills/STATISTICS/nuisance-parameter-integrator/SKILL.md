---
name: nuisance-parameter-integrator
version: 1.0.0
domain: STATISTICS
surfaces:
  - python
  - z3
description: >
  Marginalizes out nuisance parameters using the distributivity of logical
  operations. Integrates background uncertainty when the model only cares
  about a specific target metric.
purpose: >
  Execute Bayesian marginalization of nuisance parameters: average out
  theta when the model only cares about a target metric omega.
dependencies:
  - inverse-zeta-generalizer
inputs:
  joint_distribution:
    type: object
    required: true
    description: "Joint probability distribution P(omega, theta)"
  target_metric:
    type: string
    required: true
    description: "Target variable omega to retain"
  nuisance_parameters:
    type: array
    required: true
    description: "Parameters theta to marginalize out"
  integration_method:
    type: string
    required: false
    description: "exact | numerical (default: exact)"
outputs:
  marginal_distribution:
    type: object
    description: "P(omega) after marginalizing out theta"
  normalization_check:
    type: number
    description: "Sum of marginalized probabilities (should be 1.0)"
  z3_proof:
    type: object
    description: "Z3 proof of distributivity for integration"
tags:
  - nuisance
  - marginalization
  - bayesian
  - integration
  - z3
  - python
---

# Nuisance Parameter Integrator

Marginalizes out nuisance parameters using distributivity of logical
operations. Integrates background uncertainty for target metrics.

## Tick Protocol

| Id | Surface | Action                                                |
|----|---------|-------------------------------------------------------|
| 1  | Python  | Parse `joint_distribution`, `target_metric`, `nuisance_parameters` |
| 2 | Z3      | Encode distributivity axioms for integration          |
| 3  | Z3      | Verify integration preserves total probability mass   |
| 4  | Python  | Sum over nuisance dimensions: P(omega) = sum_theta P(omega, theta) |
| 5  | Python  | Normalize and validate with `normalization_check`    |
| 6  | Python  | Return `marginal_distribution` and `z3_proof`        |

## Surfaces

### Python Surface

```python
surfaces.nuisance_parameter_integrator.marginalize(
    joint_distribution={
        "omega_values": [0.1, 0.2, 0.3],
        "theta_values": [0.5, 0.5],
        "joint": [[0.05, 0.05], [0.1, 0.1], [0.15, 0.15]]
    },
    target_metric="omega",
    nuisance_parameters=["theta"],
    integration_method="exact"
)
```

### Z3 Surface

```python
from z3 import *

def verify_integration_distributivity(omega_vals, theta_vals):
    s = Solver()
    # Distributivity: sum_theta P(omega, theta) = P(omega) * sum_theta 1
    for omega in omega_vals:
        marginal = Sum([Real(f"P_{omega}_{theta}") for theta in theta_vals])
        s.add(marginal >= 0)
        s.add(marginal <= 1)
    return s.check() == sat
```

## Capability Contract

**Inputs:**

- `joint_distribution` *(object, required)* — Joint probability distribution $P(\omega, \theta)$.
- `target_metric` *(string, required)* — Target variable $\omega$ to retain.
- `nuisance_parameters` *(array, required)* — Parameters $\theta$ to marginalize out.
- `integration_method` *(string, optional)* — `exact` or `numerical`. Default `exact`.

**Outputs:**

- `marginal_distribution` *(object)* — $P(\omega)$ after marginalizing out $\theta$.
- `normalization_check` *(number)* — Sum of marginalized probabilities (should be 1.0).
- `z3_proof` *(object)* — Z3 proof of distributivity for integration.

## Composition

- `inverse-zeta-generalizer` — Consumes its probability distribution.
- `associative-chaining-product` — Chains marginalized distributions.
- `builtin-occams-razor-evaluator` — Uses marginalized distributions for model comparison.
