---
name: skill-unconscious-inference
domain: STATISTICS
version: 1.0.0
surfaces:
- python
- sqlite
description: 'Probabilistic priority layer that selects the most likely interpretation from multiple valid logical models.
  Uses historical weighted lookups to compute heuristic scores and pick a single activation path.

  '
purpose: 'When multiple valid models pass constraint gates, apply weighted priors based on historical data to select the best-guess
  execution branch.

  '
dependencies:
- skill-constraint-resolver
tags:
- probabilistic
- inference
- priors
- python
- sqlite
- heuristic
- unconscious-inference
- helmholtz
inputs:
  valid_models:
    type: array
    required: true
    description: List of valid models from upstream constraint resolver
  priors:
    type: object
    required: false
    description: Weighted prior probabilities for each model type
  historical_log:
    type: array
    required: false
    description: Historical execution log for frequency-based weighting
  scoring_method:
    type: string
    required: false
    description: 'bayesian | frequency | hybrid (default: hybrid)'
outputs:
  selected_model:
    type: object
    description: Highest-scoring model selected for execution
  selection_score:
    type: number
    description: Confidence score of selected model
  alternative_models:
    type: array
    description: Remaining valid models ranked by score
---

# Skill Unconscious Inference

Probabilistic priority layer. Selects the most likely interpretation from
multiple valid logical models using weighted priors.

## Tick Protocol

| Id | Surface  | Action                                                |
|----|----------|-------------------------------------------------------|
| 1  | Python   | Parse `valid_models`, `priors`, `historical_log`     |
| 2  | SQLite   | Query historical frequencies for each model type      |
| 3  | Python   | Compute weighted scores per `scoring_method`          |
| 4  | Python   | Rank models by composite score                        |
| 5  | Python   | Select top model as `selected_model`                  |
| 6  | Python   | Return results                                        |

## Surfaces

### Python Surface

```python
surfaces.skill_unconscious_inference.select(
    valid_models=[
        {"type": "smooth_terrain", "features": [...]},
        {"type": "rough_terrain", "features": [...]}
    ],
    priors={"smooth_terrain": 0.8, "rough_terrain": 0.2},
    historical_log=[
        {"type": "smooth_terrain", "success": True},
        {"type": "rough_terrain", "success": False}
    ],
    scoring_method="hybrid"
)
```

### SQLite Surface

```sql
CREATE TABLE IF NOT EXISTS inference_history (
    model_type TEXT NOT NULL,
    success INTEGER NOT NULL,
    timestamp INTEGER DEFAULT (strftime('%s','now')),
    PRIMARY KEY (model_type, timestamp)
);
```

## Capability Contract

**Inputs:**

- `valid_models` *(array, required)* — List of valid models from upstream constraint resolver.
- `priors` *(object, optional)* — Weighted prior probabilities for each model type.
- `historical_log` *(array, optional)* — Historical execution log for frequency-based weighting.
- `scoring_method` *(string, optional)* — `bayesian`, `frequency`, or `hybrid`. Default `hybrid`.

**Outputs:**

- `selected_model` *(object)* — Highest-scoring model selected for execution.
- `selection_score` *(number)* — Confidence score of selected model.
- `alternative_models` *(array)* — Remaining valid models ranked by score.

## Composition

- `skill-constraint-resolver` — Consumes `valid_models` as primary input.
- `skill-sensor-transducer` — Indirect via constraint resolver.
- `skill-anomaly-diagnostic` — Receives `selected_model` for edge-case validation.
