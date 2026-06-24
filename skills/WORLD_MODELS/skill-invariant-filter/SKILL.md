---
name: skill-invariant-filter
domain: WORLD_MODELS
version: 1.0.0
surfaces:
- datalog
- prolog
description: 'Relational invariant extraction and topological equivalence filter. Decouples structural identity from superficial
  data modifications, matching on connectivity and architectural signatures while masking noise.

  '
purpose: 'Maintain perceptual constancy across transformed data. Maps disparate structural representations into a single normalized
  logic identity using relational rules.

  '
dependencies:
- skill-sensor-transducer
tags:
- invariant
- constancy
- datalog
- prolog
- equivalence
- noise-filter
- car-vision
inputs:
  normalized_data:
    type: object
    required: true
    description: Normalized data from skill-sensor-transducer
  invariant_schema:
    type: object
    required: true
    description: Rules defining topological invariants to match on
  noise_threshold:
    type: number
    required: false
    description: 'Maximum acceptable noise level (default: 0.1)'
outputs:
  normalized_identity:
    type: object
    description: Topological invariant representation
  noise_masked_fields:
    type: array
    description: Fields where noise exceeded threshold
  equivalence_score:
    type: number
    description: Similarity score against invariant schema
---

# Skill Invariant Filter

Relational invariant extraction and topological equivalence filter.
Decouples structural identity from superficial data modifications.

## Tick Protocol

| Id | Surface   | Action                                                |
|----|-----------|-------------------------------------------------------|
| 1  | Python    | Parse `normalized_data` and `invariant_schema`       |
| 2  | Datalog   | Assert transformed facts into fact store              |
| 3  | Prolog    | Query topological invariants from `invariant_schema`  |
| 4  | Prolog    | Apply noise-masking filter over transient fields      |
| 5  | Python    | Compute `equivalence_score` against schema            |
| 6  | Python    | Return `normalized_identity` and `noise_masked_fields` |

## Surfaces

### Datalog Surface

Stores normalized facts from the transducer.

```datalog
% Ingested facts from sensor
+observation(object_id, feature_vector, timestamp).
+observation(light_source, direction: above, intensity: 0.8).

% Invariant schema facts
+invariant(object_id, connectivity: required).
+invariant(dependency_graph, isomorphism: strict).
```

### Prolog Surface

Topological invariant matching with noise masking.

```prolog
% Equivalence under noise: match if structural signature holds
equivalent(ObjectA, ObjectB) :-
    observation(ObjectA, FeaturesA, _),
    observation(ObjectB, FeaturesB, _),
    topological_invariant(FeaturesA, Sig),
    topological_invariant(FeaturesB, Sig),
    noise_within_threshold(FeaturesA, FeaturesB, Threshold).

% Noise masking: fields exceeding threshold are discarded
noise_within_threshold(FA, FB, Threshold) :-
    findall(Diff, (feature_diff(FA, FB, Diff)), Diffs),
    max_list(Diffs, MaxDiff),
    MaxDiff =< Threshold.

topological_invariant(Features, Signature) :-
    extract_connectivity(Features, Connectivity),
    extract_dependencies(Features, Dependencies),
    Signature = connectivity(Connectivity, Dependencies).
```

### Python Surface

```python
surfaces.skill_invariant_filter.filter(
    normalized_data={"features": [...], "timestamp": 1718888888},
    invariant_schema={"connectivity": "required", "isomorphism": "strict"},
    noise_threshold=0.1
)
```

## Capability Contract

**Inputs:**

- `normalized_data` *(object, required)* — Normalized data from `skill-sensor-transducer`.
- `invariant_schema` *(object, required)* — Rules defining topological invariants to match on.
- `noise_threshold` *(number, optional)* — Maximum acceptable noise level. Default `0.1`.

**Outputs:**

- `normalized_identity` *(object)* — Topological invariant representation.
- `noise_masked_fields` *(array)* — Fields where noise exceeded threshold.
- `equivalence_score` *(number)* — Similarity score against invariant schema.

## Composition

- `skill-sensor-transducer` — Downstream consumer of `normalized_data`.
- `skill-constraint-resolver` — Provides invariants as `background_axioms`.
- `skill-unconscious-inference` — Uses `normalized_identity` for probabilistic scoring.
