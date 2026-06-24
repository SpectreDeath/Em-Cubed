---
name: design-sync
domain: DESIGN_SYSTEMS
version: 1.0.0
surfaces:
- datalog
- prolog
description: 'Bi-directional design-system bridge. Datalog surface stores declarative component equivalencies and token mappings.
  Prolog surface derives equivalency rules and compliance verdicts before the harness builder touches the codebase.

  '
purpose: 'Prevent agents from introducing generic UI elements or design-token drift by checking proposed work against the
  canonical design system. This is the Sloan bridge: codebase logic to external product/design invariants.

  '
dependencies:
- skill-harness-builder
tags:
- design-system
- component-mapping
- equivalency
- datalog
- prolog
- invariant
- Sloan-harness-engineering
inputs:
  design_tokens:
    type: object
    required: true
    description: Extracted design tokens from Figma, tokens.json, or a design system
  target_component:
    type: string
    required: true
    description: UI component or element under evaluation
  codebase_context:
    type: object
    required: false
    description: Inventory of existing code components to cross-check
outputs:
  component_mapping:
    type: object
    description: Mapped equivalent component in the design system
  compliance_status:
    type: string
    description: compliant | mismatch | missing
  constraint_violations:
    type: array
    description: List of design-system violations detected
  recommended_component:
    type: string
    description: Canonical component name the harness should use
---

# Design System Sync

Bi-directional bridge between design-system specifications and the
skill-harness-builder. Datalog holds the canonical component facts.
Prolog derives equivalency and compliance verdicts.

## Tick Protocol

| Id | Surface   | Action                                                        |
|----|-----------|---------------------------------------------------------------|
| 1  | Python    | Parse `design_tokens` and `target_component`                 |
| 2  | Datalog   | Assert design-system facts from `design_tokens`               |
| 3  | Datalog   | Assert codebase facts from `codebase_context`                 |
| 4  | Prolog    | Query equivalency rules for `target_component`                |
| 5  | Prolog    | Run invariant checks (generic-forbidden, tier-requirements)  |
| 6  | Python    | Aggregate into `compliance_status`, `constraint_violations`   |

If tick 5 returns no valid mapping -> emit `compliance_status: mismatch`.

## Surfaces

### Datalog Surface

Canonical fact store for the design system and codebase inventory.

```datalog
% Design-system facts
+design_component(export_button, figma_node_id, "btn-export-01", tier: required).
+design_token(color_primary, "#007AFF").
+design_token(radius_md, 8).
+design_token(requires_approved_component, true).

% Codebase facts
+code_component(export_button, path: "src/ui/ExportButton.tsx").
+code_component(primary_button, path: "src/ui/PrimaryButton.tsx").
+code_component(button, path: "src/ui/Button.tsx").
```

### Prolog Surface

Equivalency derivation and compliance checks.

```prolog
% Equivalency: code component must match design component on tier
must_use_component(DesignComponent, RequiredCodeComponent) :-
    design_component(DesignComponent, _, _, tier: required),
    code_component(RequiredCodeComponent, _, _),
    design_component(DesignComponent, _, _, name_alias: RequiredCodeComponent).

% Generic-component guard (Sloan external-context invariant)
generic_forbidden(GenericName) :-
    design_component(_, _, _, requires_approved_component: true),
    code_component(GenericName, _, _),
    GenericName \= RequiredComponent,
    GenericName \= DesignComponent.

% Tier-requirement guard
tier_required_but_unmapped(RequiredTier) :-
    design_component(_, _, _, tier: RequiredTier),
    \+ code_component(_, _, _: RequiredTier).
```

### Python Surface

```python
surfaces.design_sync.map_equivalents(
    design_tokens={
        "components": [
            {"name": "ExportButton", "figma_id": "btn-export-01", "tier": "required"}
        ],
        "tokens": {"color_primary": "#007AFF", "radius_md": 8}
    },
    target_component="export_button",
    codebase_context={
        "components": [
            {"name": "ExportButton", "path": "src/ui/ExportButton.tsx"},
            {"name": "Button", "path": "src/ui/Button.tsx"}
        ]
    }
)
```

## Capability Contract

**Inputs:**

- `design_tokens` *(object, required)* — Extracted design tokens from Figma, tokens.json, or a design system.
- `target_component` *(string, required)* — UI component or element under evaluation.
- `codebase_context` *(object, optional)* — Inventory of existing code components to cross-check.

**Outputs:**

- `component_mapping` *(object)* — Mapped equivalent component in the design system.
- `compliance_status` *(string)* — `compliant`, `mismatch`, or `missing`.
- `constraint_violations` *(array)* — List of design-system violations detected.
- `recommended_component` *(string)* — Canonical component name the harness should use.

## Sloan Failure Mode Guard

This skill directly addresses the failure mode in the Sloan talk:

> *"An agent might create a standard React button that passes structural tests
> but breaks organizational accessibility compliance, simply because it didn't
> know a specialized ExportButton design component existed."*

When `skill-harness-builder` is invoked, it should call `design-sync` first.
If `compliance_status == mismatch`, the harness builder aborts before
executing any tool that writes to the codebase.

## Composition

- `skill-harness-builder` — Uses `compliance_status` and `recommended_component` to gate sandbox builds.
- `skill-world-designer` — Uses `design_tokens` as grounding facts for simulation.
- `invariant-gate` — Receives mapped component for accessibility/compliance enforcement.
