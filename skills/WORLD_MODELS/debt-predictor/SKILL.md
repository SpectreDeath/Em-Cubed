---
name: debt-predictor
version: 1.0.0
domain: WORLD_MODELS
surfaces:
  - prolog
description: >
  Architectural cost feedback loop that warns when a product request conflicts
  with deeply embedded backend architectural constraints. Uses Prolog surface
  to evaluate the historical complexity and data-access costs of proposed actions.
purpose: >
  Bridge the gap back to the design phase by warning the system when an outside
  product request conflicts with backend architectural constraints, preventing
  bloomed PRs and technical debt.
dependencies:
  - skill-world-designer
inputs:
  target_action:
    type: string
    required: true
    description: "Proposed action to evaluate (e.g., move_export_button_to_main_screen)"
  architectural_graph:
    type: object
    required: true
    description: "Historical graph of backend architecture complexity and data-access costs"
  context:
    type: object
    required: false
    description: "Optional additional context"
outputs:
  impact_assessment:
    type: object
    description: "Assessed architectural impact of the proposed action"
  cost_level:
    type: string
    description: "low | medium | high | critical"
  recommendation:
    type: string
    description: "proceed | restructure | block"
  reasoning:
    type: string
    description: "Prolog-derived explanation for the recommendation"
tags:
  - prolog
  - architecture
  - cost-prediction
  - debt
  - technical-debt
  - feedback-loop
---

# Debt Predictor

Architectural cost feedback loop. Uses Prolog to evaluate backend impact
of proposed product actions and produces an impact assessment.

## Tick Protocol

| Id | Surface   | Action                                                |
|----|-----------|------------------------------------------------------|
| 1  | Python    | Parse `target_action` and `architectural_graph`      |
| 2  | Python    | Load architectural facts into Prolog knowledge base   |
| 3  | Prolog    | Query `evaluate_architectural_impact(TargetAction, CostLevel)` |
| 4  | Prolog    | If CostLevel == critical, retrieve reasoning chain    |
| 5  | Python    | Map CostLevel to `recommendation`                     |
| 6  | Python    | Return `impact_assessment`, `cost_level`, `recommendation`, `reasoning` |

If tick 4 detects `critical` cost -> emit `recommendation: block`.

## Surfaces

### Prolog Surface

Maintains a historical graph of backend architecture complexity and
data-access costs.

```prolog
% Architectural facts:
architectural_component(export_button_service, db_table: user_exports, join_depth: 3, cost_weight: 0.8).
architectural_component(main_screen_query, db_table: user_sessions, join_depth: 1, cost_weight: 0.2).

% Impact evaluation rules:
evaluate_architectural_impact(Action, CostLevel) :-
    requires_service(Action, Service),
    architectural_component(Service, _, JoinDepth, Weight),
    calculate_cost(JoinDepth, Weight, Cost),
    classify_cost(Cost, CostLevel).

calculate_cost(JoinDepth, Weight, Cost) :-
    Cost is JoinDepth * Weight * 100.

classify_cost(Cost, low) :- Cost < 30.
classify_cost(Cost, medium) :- Cost >= 30, Cost < 70.
classify_cost(Cost, high) :- Cost >= 70, Cost < 100.
classify_cost(Cost, critical) :- Cost >= 100.

% Example action mapping:
requires_service(move_export_button_to_main_screen, export_button_service).
requires_service(move_export_button_to_main_screen, main_screen_query).
```

### Python Surface

```python
surfaces.debt_predictor.evaluate(
    target_action="move_export_button_to_main_screen",
    architectural_graph={...}
)
```

## Capability Contract

**Inputs:**

- `target_action` *(string, required)* — Proposed action to evaluate.
- `architectural_graph` *(object, required)* — Historical graph of backend architecture complexity and data-access costs.
- `context` *(object, optional)* — Optional additional context.

**Outputs:**

- `impact_assessment` *(object)* — Assessed architectural impact of the proposed action.
- `cost_level` *(string)* — `low`, `medium`, `high`, or `critical`.
- `recommendation` *(string)* — `proceed`, `restructure`, or `block`.
- `reasoning` *(string)* — Prolog-derived explanation for the recommendation.

## Composition

- `skill-world-designer` — Uses `cost_level` to adjust simulation parameters.
- `skill-harness-builder` — Uses `recommendation` to gate harness compilation.
- `design-sync` — Provides component mapping context for debt analysis.
