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

### C. Dynamic Prolog Code Generation
When Python needs to construct Prolog facts/rules at runtime, inject the full Prolog string as a template variable:
```cangjie
let facts = generate_facts(family_data)  // Python generates string
let rules = load_rules()                 // Static or generated
perform EmCubed.call_surface("python", "prolog_code = \"${facts}\\n${rules}\"")
```
This pattern is used inintegrated-logic-solver where Python builds family facts dynamically.

### D. Adaptive Parameter Orchestration
For optimization skills with Hy-based adaptation, run the Hy surface mid-loop to adjust parameters:
```cangjie
for gen in 0..max_iter {
    // DE mutation/crossover (Python)
    perform EmCubed.call_surface("python", "...")

    // Validate parameters (Prolog)
    perform EmCubed.call_surface("prolog", "valid_parameters(${F}, ${CR}, ${pop_size})")

    // Adapt parameters (Hy) every N generations
    if gen % 10 == 0 {
        perform EmCubed.call_surface("hy", "de-adapt(${success_history})")
    }
}
```
Applied indifferential-evolution-solver for JADE-style adaptation.

## 5. Archetype Summary Table (Updated Sprint 3–4)
| Archetype | Surface Sequence | Best For | LOC Impact | Examples |
| :--- | :--- | :--- | :--- | :--- |
| **Linear Pipeline** | Py → Pr → Hy | NLP, ETL, Validation | **-50% to +30%** | sentiment-intelligence-engine, natural-language-generator, differential-evolution-solver, data-pipeline-orchestrator |
| **Competitive Search** | Py∥Z3 + Cj select | CSP, Optimization | **+15% (Coord)** | multi-agent-coordinator, multi-criteria-weight-calculator, constraint-satisfaction-solver |
| **Logic Refinement** | Py (norm) → Pr (reason) → Cj (synth) | Reasoning, Deduction | **+50% to +120%** (orchestrator explicit) | integrated-logic-solver, python-prolog-pipeline |
| **Confidence Synthesis** | Py (signals) + Hy (fuse) | Anomaly detection, Ensemble | **-20%** | anomaly-detection-system, ensemble-method-manager |

> **Note on LOC increases**: Logic Refinement archetypes show +50–1833% orchestrator LOC growth because original skills baked coordination logic into Python glue code (direct surface execute_sync calls). Cangjie migration exposes that glue as explicit, typed orchestration — a net maintainability gain despite LOC increase. Pipeline archetypes show -50–66% reductions by eliminating redundant data plumbing.

## 6. Validation & Metrics
Run `test_cangjie_comparison.py` to generate per-skill metrics:
- **Orchestrator LOC**: Total Cangjie function/struct lines (excluding surface blocks)
- **File size delta**: `cj - orig` in bytes (negative = compression gain)
- **Surface calls**: Count of `perform EmCubed.call_surface()` invocations
- **Functions/Structs**: Number of typed structures defined

**Sprint 3–4 aggregate (27 skills)**:
| Metric | Before | After | Change |
| :--- | :--- | :--- | :--- |
| Orchestrator LOC | 727 | 736 | +1.2% |
| Surface calls | 0 | 168 | +168 |
| Structs defined | 0 | 51 | +51 |
| Avg file size reduction | — | — | **-3,017 bytes/skill** |

Full report: `cangjie_comparison_report.md`.

## 7. Migration Checklist (For Contributors)
Before marking a skill migration complete:
- [ ] Skill uses **≥2 surfaces** in original implementation (single-surface skills do not benefit)
- [ ] Selected correct archetype from Section 2
- [ ] All input/output data modeled as **Cangjie typed structs**
- [ ] All surface calls use `perform EmCubed.call_surface("<surface>", "${template}")`
- [ ] No Python-side `context["surfaces"]` surface.execute() calls remain
- [ ] No Prolog/Hy code in Cangjie blocks (only string literals)
- [ ] Each surface code block under 50 lines
- [ ] Unit test for each surface path (mock-heavy dependencies)
- [ ] Integration test for full pipeline (orchestrator end-to-end)
- [ ] `test_cangjie_comparison.py` passes and reports skill pair

