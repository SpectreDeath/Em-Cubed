# Cangjie Migration Guidelines

This guide outlines the best practices for migrating existing Em-Cubed skills to the Cangjie Surface, based on the performance metrics of the 0.5.0 validation suite.

## 1. The Orchestration Pattern (The "Why")
The primary goal of migrating to Cangjie is to move from **Surface-Local Monoliths** to **Cross-Surface Composition**. 
- **Original**: Surfaces (Python, Prolog) often contained redundant data structures and "glue" to handle failures from other surfaces.
- **Cangjie**: The Cangjie `func main()` acts as a typed orchestrator, allowing each surface to remain "Pure" (focused only on its specific logic).

## 2. Archetypes of Migration

| Archetype | Best For | Strategy | LOC Impact |
| :--- | :--- | :--- | :--- |
| **Linear Pipeline** | Validation, Statistics | Python (Compute) → Prolog (Validate) → Hy (Score). | **-50%** |
| **Competitive Search** | Optimization, CSP | Run multiple surfaces (Z3 vs Python) and use CJ to select the best result. | **+15% (Coord)** |
| **Logic Refinement** | Decision Making | Python (Normalize) → Prolog (Prune) → CJ (Synthesize). | **-30%** |
| **Confidence Synthesis** | Monitoring, Anomalies | Combine multiple detection signals (Python) using fuzzy logic (Hy). | **-20%** |

## 3. Core Implementation Rules

### A. Use Typed Structs for Domain Modeling
Always define a `struct` in Cangjie to represent your input data. This acts as the "Single Source of Truth."
```cangjie
struct UQInput {
    variables: Map<String, UncertaintyDistribution>;
    model_expression: String;
}
```

### B. Leverage Template Injection
Avoid manual JSON serialization. Inject Cangjie variables directly into surface strings using `${}`.
```cangjie
let py_result = perform EmCubed.call_surface("python", "results = model(${uq_data.variables})");
```

### C. Functional Effect Handling
Use the `perform` keyword to treat surface calls as "Effects." This linearizes the logic and removes the need for deep nesting or complex `try/except` blocks in Python.

## 4. Evaluation of Migration Success
- **Orchestration Transparency**: If orchestration LOC increases, it usually means logic has been moved from hidden framework glue into the explicit skill definition.
- **Surface Purity**: Each surface block should be under 50 lines and contain zero "coordination" logic.
- **Type Safety**: Cross-surface data should be validated by the Cangjie compiler via ADTs and Structs.
