---
name: builtin-occams-razor-evaluator
version: 1.0.0
domain: STATISTICS
surfaces:
  - python
  - z3
description: >
  Model-comparison skill that calculates the global likelihood ratio
  (Bayes Factor) between competing architectures. Penalizes
  overparameterized models via dilution of prior probability density.
purpose: >
  Mathematically penalize over-parameterized, highly flexible models
  using Jaynesian Occam's razor: prior density dilution across extra
  dimensions lowers global likelihood.
dependencies:
  - nuisance-parameter-integrator
inputs:
  model_a:
    type: object
    required: true
    description: "First model with parameters and likelihood"
  model_b:
    type: object
    required: true
    description: "Second model with parameters and likelihood"
  data_evidence:
    type: object
    required: true
    description: "Observed data for likelihood computation"
  prior_weights:
    type: object
    required: false
    description: "Prior probabilities for each model (default: uniform)"
outputs:
  bayes_factor:
    type: number
    description: "P(data|model_a) / P(data|model_b)"
  occam_penalty:
    type: object
    description: "Penalty breakdown by model complexity"
  preferred_model:
    type: string
    description: "model_a or model_b"
  confidence:
    type: number
    description: "Confidence in model selection"
tags:
  - occam
  - bayes-factor
  - model-comparison
  - prior-dilution
  - python
  - z3
---

# Built-in Occam's Razor Evaluator

Calculates Bayes Factor between models with Occam penalty.
Python computes likelihoods. Z3 verifies prior dilution axioms.

## Tick Protocol

| Id | Surface | Action                                                |
|----|---------|-------------------------------------------------------|
| 1  | Python  | Parse `model_a`, `model_b`, `data_evidence`          |
| 2  | Z3      | Encode prior dilution axioms for each model           |
| 3  | Z3      | Compute Occam penalties across parameter dimensions   |
| 4  | Python  | Compute marginal likelihoods for each model           |
| 5  | Python  | Calculate Bayes Factor and confidence                 |
| 6  | Python  | Return `bayes_factor`, `occam_penalty`, `preferred_model` |

## Surfaces

### Python Surface

```python
surfaces.builtin_occams_razor_evaluator.compare(
    model_a={"name": "linear", "parameters": 2, "likelihood": 0.85},
    model_b={"name": "polynomial_deg5", "parameters": 6, "likelihood": 0.90},
    data_evidence={"n": 100, "log_likelihood_a": -45.2, "log_likelihood_b": -42.1},
    prior_weights={"model_a": 0.5, "model_b": 0.5}
)
```

### Z3 Surface

```python
from z3 import *

def occam_penalty(param_count, data_points):
    s = Solver()
    prior_volume = Real("prior_volume")
    # Prior density dilution: volume scales inversely with parameter count
    s.add(prior_volume == 1.0 / param_count)
    # Occam factor: ratio of prior volumes
    occam_factor = Real("occam_factor")
    s.add(occam_factor == prior_volume)
    return s.model() if s.check() == sat else None
```

## Capability Contract

**Inputs:**

- `model_a` *(object, required)* — First model with parameters and likelihood.
- `model_b` *(object, required)* — Second model with parameters and likelihood.
- `data_evidence` *(object, required)* — Observed data for likelihood computation.
- `prior_weights` *(object, optional)* — Prior probabilities for each model. Default uniform.

**Outputs:**

- `bayes_factor` *(number)* — $P(D|M_1) / P(D|M_2)$.
- `occam_penalty` *(object)* — Penalty breakdown by model complexity.
- `preferred_model` *(string)* — `model_a` or `model_b`.
- `confidence` *(number)* — Confidence in model selection.

## Composition

- `nuisance-parameter-integrator` — Provides marginalized likelihoods.
- `inverse-zeta-generalizer` — Provides prior distributions.
- `finite-limit-sequence-boundary` — Validates infinite-set limits in prior computation.
