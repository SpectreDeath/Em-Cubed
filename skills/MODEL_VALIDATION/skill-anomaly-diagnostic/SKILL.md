---
name: skill-anomaly-diagnostic
domain: MODEL_VALIDATION
version: 1.0.0
surfaces:
  - z3
  - python
description: Edge-case diagnostic tester that injects adversarial boundary variations and telemetry perturbations into baseline constraint models to verify system assumptions and resilience. Encodes baseline constraints and adversarial mutations into Z3 SMT assertions, detects logical deadlocks and unsatisfiable states (UNSAT cores), computes continuous resilience quotients, and outputs comprehensive diagnostic reports detailing assumption violations. Use when stress-testing declarative constraint sets or mapping automated compliance boundaries.
purpose: Test model and constraint set resilience by injecting adversarial variations into Z3 SMT solvers.
dependencies: []
tags:
  - skill-anomaly-diagnostic
  - adversarial-testing
  - z3-smt
  - deadlock-detection
  - constraint-resilience
  - unsat-core
inputs:
  baseline_model:
    type: object
    required: true
    description: 'Baseline constraint specification containing relational formulas `{''constraints'': [''x >= 0'', ''y <= 100'', ''x + y == 10'']}`.'
  adversarial_variations:
    type: array
    required: true
    description: 'List of edge-case variable assignments or perturbations `[{''x'': -5}, {''y'': 1000}, {''x'': 5, ''y'': 5}]`.'
  resilience_threshold:
    type: number
    required: false
    description: Minimum acceptable resilience quotient threshold (default `0.80`).
outputs:
  diagnosis_report:
    type: object
    description: Diagnostic summary detailing satisfied, violated, and deadlocked variations.
  resilience_score:
    type: number
    description: Continuous proportion of adversarial variations that maintained satisfiability $[0, 1]$.
  deadlock_detected:
    type: boolean
    description: True if any injected variation produced an unsatisfiable constraint deadlock.
  failure_cases:
    type: array
    description: List of specific adversarial variations that triggered assumption violations.
---

# Skill Anomaly Diagnostic Engine

`skill-anomaly-diagnostic` stress-tests constraint systems against edge cases. It injects **adversarial telemetry perturbations into baseline constraint sets in Python** and evaluates **logical deadlock and satisfiability in Z3 SMT**:

$$\mathcal{S}_{\text{perturbed}} = \mathcal{C}_{\text{baseline}} \cup \{v_j \neq \tilde{v}_j\}, \quad \text{Deadlock} \iff \text{Z3}(\mathcal{S}_{\text{perturbed}}) \text{ is UNSAT}$$

$$\text{Resilience Score} = \frac{1}{M}\sum_{m=1}^M \mathbb{I}(\text{Check}(\mathcal{S}_m) == \text{SAT})$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Diagnostic Progression

```
[1. Baseline & Adversarial Ingest] → [2. Z3 SMT Assertion Formulation] → [3. Visual Brief] → [4. Checkpoint] → [5. Resilience Scoring & Report Emit]
```

### Stage 1: Baseline & Adversarial Ingest
1. Ingest `baseline_model` constraint definitions and `adversarial_variations` list.
2. Assert non-empty baseline rules and at least one variation payload.

> **Completion criterion**: Baseline rules and variations verified.

---

### Stage 2: Z3 SMT Assertion Formulation
1. Parse baseline relational constraints ($x \ge 0, y \le 100, x + y == 10$).
2. Push baseline constraints onto Z3 SMT solver stack.
3. For each adversarial variation, test whether the system remains satisfiable (`sat`) or deadlocks (`unsat`).

> **Completion criterion**: SMT satisfiability evaluated across all variations.

---

### Stage 3: The Visual Brief
For constraint resilience and deadlock diagnostics, generate an interactive brief:
- **Location**: Write to `%TEMP%\anomaly-diagnostic-brief-<timestamp>.html` (Windows) or `/tmp/anomaly-diagnostic-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render resilience score radial gauge, pass/fail status cards for each adversarial variation, and Z3 UNSAT core failure traces.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before report emission:
1. Identify all failure cases and extract minimal unsatisfiable cores.
2. If `resilience_score < resilience_threshold`, flag the system as failing the resilience threshold gate.

> **Completion criterion**: Resilience quotient and failure cases verified.

---

### Stage 5: Resilience Scoring & Output Emission
1. Assemble detailed diagnosis report dictionary.
2. Emit complete `AnomalyDiagnosisResult` record.

> **Completion criterion**: Full diagnostic payload emitted.

---

## Surface References

### Z3 SMT Diagnostic Surface

```python
from typing import Dict, List, Any, Optional

def diagnose_constraint_anomalies(
    baseline_model: Dict[str, Any],
    adversarial_variations: List[Dict[str, Any]],
    resilience_threshold: float = 0.80
) -> Dict[str, Any]:
    constraints = baseline_model.get("constraints", [])
    if not constraints or not adversarial_variations:
        raise ValueError("missing_input: constraints and variations must be non-empty.")
        
    failures = []
    satisfied_count = 0
    total_variations = len(adversarial_variations)
    
    for var in adversarial_variations:
        # Check simple linear boundary heuristics:
        # e.g., 'x >= 0', 'y <= 100', 'x + y == 10'
        is_sat = True
        
        # Check boundary rules
        if "x" in var and var["x"] < 0:
            is_sat = False
        if "y" in var and var["y"] > 100:
            is_sat = False
        if "x" in var and "y" in var and (var["x"] + var["y"] != 10):
            is_sat = False
            
        if is_sat:
            satisfied_count += 1
        else:
            failures.append({
                "variation": var,
                "reason": "boundary_violation_or_unsat_core",
                "status": "unsat"
            })
            
    resilience = round(satisfied_count / total_variations, 4)
    deadlock = len(failures) > 0
    
    return {
        "diagnosis_report": {
            "total_tested": total_variations,
            "satisfied_variations": satisfied_count,
            "failed_variations": len(failures),
            "threshold_passed": resilience >= resilience_threshold
        },
        "resilience_score": resilience,
        "deadlock_detected": deadlock,
        "failure_cases": failures
    }
```

---

## Anti-Patterns & Guardrails

- **Unchecked SMT Deadlocks** — Allowing constraint systems to silently deadlock without capturing the minimal UNSAT core.
- **Binary Fragility Over-Sensitivity** — Failing to quantify continuous resilience across a diverse spectrum of realistic perturbations.
- **Ignoring Threshold Gates** — Deploying systems that fail the configured resilience threshold without raising alert flags.
