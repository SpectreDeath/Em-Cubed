---
name: validate_measurement_level
domain: STATISTICS
version: 1.0.0
surfaces:
  - prolog
  - python
description: Symbolic guardrail skill enforcing Stevens' measurement hierarchy (Nominal < Ordinal < Interval < Ratio). Resolves data-typing properties using pure first-order logic in Prolog and gates statistical test dispatching to prevent invalid parametric assumptions on categorical or ordinal data. Use when validating variable scale properties, confirming measurement permissions before ANOVA/t-tests, or routing non-parametric alternatives.
purpose: Enforce Stevens' measurement scale hierarchy in Prolog to gate downstream statistical test routing.
dependencies: []
tags:
  - measurement-level
  - stevens-hierarchy
  - prolog-guardrail
  - test-routing-gate
  - symbolic-validation
inputs:
  dataset_id:
    type: string
    required: true
    description: Dataset identifier for belief store partitioning.
  column_name:
    type: string
    required: true
    description: Name of the variable/column to evaluate.
  semantic_hint:
    type: string
    required: false
    description: Optional scale hint ('nominal', 'ordinal', 'interval', 'ratio').
outputs:
  measurement_level:
    type: string
    description: Resolved measurement scale ('nominal', 'ordinal', 'interval', 'ratio', 'unknown').
  routing_permission:
    type: string
    description: Test dispatch permission ('allowed' or 'blocked').
  permitted_test_families:
    type: array
    description: List of mathematically permissible test families for this variable scale.
---

# Validate Measurement Level Engine

`validate_measurement_level` provides symbolic guardrailing over statistical test selection by enforcing **Stevens' Measurement Scale Hierarchy** in Prolog:

$$\text{Nominal} \prec \text{Ordinal} \prec \text{Interval} \prec \text{Ratio}$$

It guarantees that parametric procedures (e.g., Pearson $r$, Student's $t$, ANOVA) are only executed on quantitative scales ($\text{Interval} \lor \text{Ratio}$), automatically blocking invalid operations on categorical or ranked variables.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Measurement Validation Progression

```
[1. Column Property Ingestion] → [2. Prolog Scale Hierarchy Resolution] → [3. Visual Brief] → [4. Checkpoint] → [5. Test Family Permission Routing]
```

### Stage 1: Column Property Ingestion
1. Ingest `dataset_id`, `column_name`, and optional `semantic_hint`.
2. Inspect column dtype, uniqueness ratio, and value domain.

> **Completion criterion**: Property signature extracted and formatted for Prolog predicate ingestion.

---

### Stage 2: Prolog Scale Hierarchy Resolution
1. Evaluate transitive dominance rules in Prolog:
   ```prolog
   dominates(ratio, interval).
   dominates(interval, ordinal).
   dominates(ordinal, nominal).
   ```
2. Unify scale with `semantic_hint` or query existing belief store `known_level/3`.

> **Completion criterion**: `measurement_level` resolved to one of the 4 canonical Stevens scales.

---

### Stage 3: The Visual Brief
For ambiguous column types or multi-variable schemas, generate an interactive brief:
- **Location**: Write to `%TEMP%\measurement-level-brief-<timestamp>.html` (Windows) or `/tmp/measurement-level-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render Stevens hierarchy ladder highlighting current variable position and allowed test dispatch gates.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before granting test execution permissions:
1. Verify that no scale contradiction exists (e.g., trying to run Pearson correlation on a nominal string column).
2. If violation is detected, set `routing_permission: "blocked"` and recommend rank or chi-square alternative.

> **Completion criterion**: Scale permission evaluated against intended statistical test family.

---

### Stage 5: Test Family Permission Routing & Emit
1. Assert resolved scale into agent working memory:
   ```prolog
   assertz(known_level(DatasetId, ColumnName, Level)).
   ```
2. Emit structured permission payload and list of permitted test families.

> **Completion criterion**: Verification output emitted with status `allowed` or `blocked`.

---

## Surface References

### Prolog Guardrail Surface

```prolog
:- module(measurement_validator, [
    validate_level/4,
    dominates/2,
    routing_permission/3,
    assert_level/3
]).

dominates(ratio, interval).
dominates(interval, ordinal).
dominates(ordinal, nominal).

validate_level(_D, _C, hint(ratio), ratio).
validate_level(_D, _C, hint(interval), interval).
validate_level(_D, _C, hint(ordinal), ordinal).
validate_level(_D, _C, hint(nominal), nominal).
validate_level(D, C, _Hint, Level) :- known_level(D, C, Level).

parametric_test(t_test).
parametric_test(one_way_anova).
parametric_test(pearson_correlation).
parametric_test(linear_regression).

non_parametric_test(mann_whitney).
non_parametric_test(wilcoxon).
non_parametric_test(kruskal_wallis).
non_parametric_test(spearman_correlation).

valid_for(Test, Level) :-
    parametric_test(Test),
    (Level = interval ; Level = ratio).

valid_for(Test, Level) :-
    non_parametric_test(Test),
    (Level = ordinal ; Level = interval ; Level = ratio).

valid_for(chi_square, nominal).

routing_permission(Test, Level, allowed) :- valid_for(Test, Level), !.
routing_permission(_Test, _Level, blocked).
```

### Python Dispatch Wrapper

```python
from typing import Dict, Any, List

def validate_measurement_level(dataset_id: str, column: str, hint: str, requested_test: str = None) -> Dict[str, Any]:
    valid_levels = {"nominal", "ordinal", "interval", "ratio"}
    level = hint.lower() if hint and hint.lower() in valid_levels else "unknown"
    
    parametric = {"t_test", "anova", "pearson_r", "ols_regression"}
    non_parametric = {"mann_whitney", "wilcoxon", "kruskal_wallis", "spearman_rho"}
    
    if level in {"interval", "ratio"}:
        allowed_families = ["PARAMETRIC", "NON_PARAMETRIC"]
    elif level == "ordinal":
        allowed_families = ["NON_PARAMETRIC"]
    elif level == "nominal":
        allowed_families = ["CATEGORICAL_CHI_SQUARE"]
    else:
        allowed_families = []
        
    permission = "allowed"
    if requested_test:
        if requested_test in parametric and level not in {"interval", "ratio"}:
            permission = "blocked"
        elif requested_test in non_parametric and level not in {"ordinal", "interval", "ratio"}:
            permission = "blocked"
            
    return {
        "measurement_level": level,
        "routing_permission": permission,
        "permitted_test_families": allowed_families,
        "dataset_id": dataset_id,
        "column_name": column
    }
```

---

## Anti-Patterns & Guardrails

- **Parametric Execution on Ordinal Likert Scales** — Treating 1-to-5 Likert categories as interval/ratio data without explicit non-parametric validation.
- **Untracked Scale Inversion** — Downgrading ratio measurements to nominal buckets without recording information loss.
- **Silent Fallthrough** — Defaulting unknown scales to `ratio` rather than halting with `measurement_level: "unknown"`.
