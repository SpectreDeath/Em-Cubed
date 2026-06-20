---
name: skill-anomaly-diagnostic
version: 1.0.0
domain: MODEL_VALIDATION
surfaces:
  - z3
  - python
description: >
  Edge-case diagnostic tester that injects adversarial or boundary telemetry
  variations to verify system assumptions hold. Uses Z3 assertions to
  validate constraint resilience and expose logical deadlocks.
purpose: >
  Map out an automated testing boundary that asserts compliance gates
  against the skill system itself, ensuring background constraints do not
  create deadlocks when unexpected real-world data patterns appear.
dependencies:
  - skill-unconscious-inference
inputs:
  baseline_model:
    type: object
    required: true
    description: "Baseline model or constraint set to test"
  adversarial_variations:
    type: array
    required: true
    description: "Edge-case input variations to inject"
  resilience_threshold:
    type: number
    required: false
    description: "Minimum acceptable resilience score (default: 0.8)"
outputs:
  diagnosis_report:
    type: object
    description: "Full diagnostic report with assumption violations"
  resilience_score:
    type: number
    description: "Overall system resilience to adversarial inputs"
  deadlock_detected:
    type: boolean
    description: "True if constraint deadlock was detected"
  failure_cases:
    type: array
    description: "List of inputs that caused assumption violations"
tags:
  - anomaly
  - diagnostic
  - z3
  - smt
  - testing
  - edge-case
  - illusion
  - resilience
---

# Skill Anomaly Diagnostic

Edge-case diagnostic tester. Injects adversarial or boundary telemetry
variations to verify system assumptions hold. Uses Z3 assertions to
validate constraint resilience.

## Tick Protocol

| Id | Surface | Action                                                |
|----|---------|-------------------------------------------------------|
| 1  | Python  | Parse `baseline_model` and `adversarial_variations`  |
| 2  | Python  | Generate Z3 assertions from baseline constraints     |
| 3  | Z3      | Push baseline assertions; capture model               |
| 4  | Z3      | For each adversarial variation, push modified assert  |
| 5  | Z3      | Detect `unsat` or deadlock conditions                 |
| 6  | Python  | Aggregate into `diagnosis_report` and `resilience_score` |

If tick 5 detects `unsat` or deadlock -> emit `deadlock_detected: true`.

## Surfaces

### Z3 Surface

```python
from z3 import *

def diagnose_anomaly(baseline_assertions, variation):
    solver = Solver()
    # Baseline constraints
    for assertion in baseline_assertions:
        solver.add(assertion)
    # Adversarial variation
    for key, val in variation.items():
        solver.add(parse_one(key) != val)
    if solver.check() == sat:
        return {"resilient": True, "model": solver.model()}
    return {"resilient": False, "failure": str(solver.unsat_core())}
```

### Python Surface

```python
surfaces.skill_anomaly_diagnostic.run_diagnosis(
    baseline_model={"constraints": ["x >= 0", "y <= 100", "x + y == 10"]},
    adversarial_variations=[
        {"x": -5},  # boundary violation
        {"y": 1000},  # threshold overflow
        {"x": 5, "y": 5}  # coherent but edge-case
    ],
    resilience_threshold=0.8
)
```

## Capability Contract

**Inputs:**

- `baseline_model` *(object, required)* — Baseline model or constraint set to test.
- `adversarial_variations` *(array, required)* — Edge-case input variations to inject.
- `resilience_threshold` *(number, optional)* — Minimum acceptable resilience score. Default `0.8`.

**Outputs:**

- `diagnosis_report` *(object)* — Full diagnostic report with assumption violations.
- `resilience_score` *(number)* — Overall system resilience to adversarial inputs.
- `deadlock_detected` *(boolean)* — True if constraint deadlock was detected.
- `failure_cases` *(array)* — List of inputs that caused assumption violations.

## Composition

- `skill-unconscious-inference` — Receives `diagnosis_report` for resilience scoring.
- `skill-constraint-resolver` — Receives adversarial variations as `observables`.
- `skill-sensor-transducer` — Indirect via constraint resolver.
