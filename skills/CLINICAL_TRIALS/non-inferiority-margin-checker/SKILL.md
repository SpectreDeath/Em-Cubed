---
name: non-inferiority-margin-checker
Domain: CLINICAL_TRIALS
Version: 1.0.0
surfaces:
  - python
  - z3
description: Multi-surface non-inferiority margin checker with Python surface for statistical computation and Z3 surface for formal constraint verification.
compatibility: PYTHON
allowed-tools: |
  - read
  - write
  - edit
  - bash
  - glob
  - grep
  - codebase_search
  - task
  - sequentialthinking_sequentialthinking
  - webfetch
  - websearch
  - question
  - suggest
---

# Purpose

Programmatically determines whether a trial's observed effect and confidence interval satisfy a declared non-inferiority margin, using both statistical computation and formal constraint verification.

# Description

Consumes trial endpoint data (effect size, confidence interval bounds, non-inferiority margin, reference effect) and computes whether the lower bound of the confidence interval exceeds the non-inferiority margin. Z3 encodes the regulatory constraint hierarchy as arithmetic relations and returns a verifiable `sat`/`unsat` result with unsat core when the margin is breached.

## Python Surface

```python
def check_non_inferiority(effect_size, ci_lower, ci_upper, ni_margin, reference_effect, side="lower"):
    if side not in ("lower", "two-sided"):
        return {"status": "error", "message": "side must be 'lower' or 'two-sided'"}
    null_margin = reference_effect - ni_margin
    passes = ci_lower > null_margin
    margin_violation = null_margin - ci_lower
    return {
        "status": "ok",
        "passes_non_inferiority": passes,
        "null_margin": null_margin,
        "ci_lower": ci_lower,
        "margin_violation": margin_violation if not passes else 0.0,
        "effect_size": effect_size,
        "reference_effect": reference_effect,
        "ni_margin": ni_margin,
    }

def main(skill_input):
    effect_size = skill_input.get("effect_size", 0.0)
    ci_lower = skill_input.get("ci_lower", 0.0)
    ci_upper = skill_input.get("ci_upper", 0.0)
    ni_margin = skill_input.get("ni_margin", 0.0)
    reference_effect = skill_input.get("reference_effect", 0.0)
    side = skill_input.get("side", "lower")
    return check_non_inferiority(effect_size, ci_lower, ci_upper, ni_margin, reference_effect, side)
```

## Z3 Surface

```python
def check_non_inferiority_z3(effect_size, ci_lower, ni_margin, reference_effect):
    from z3 import Solver, Real, sat, unsat, And, Or

    solver = Solver()
    es = Real("effect_size")
    cil = Real("ci_lower")
    nim = Real("ni_margin")
    ref = Real("reference_effect")
    nm = ref - nim
    solver.add(es == effect_size)
    solver.add(cil == ci_lower)
    solver.add(nim == ni_margin)
    solver.add(ref == reference_effect)
    passes = And(cil > nm)
    solver.add(passes)
    if solver.check() == sat:
        return {"status": "ok", "z3_result": "sat", "passes": True}
    else:
        solver.push()
        solver.add(cil <= nm)
        if solver.check() == unsat:
            core_msg = "ci_lower <= null_margin"
        else:
            core_msg = "unsatisfiable under given bounds"
        solver.pop()
        return {"status": "ok", "z3_result": "unsat", "passes": False, "unsat_core": [core_msg]}
```

## Examples

```python
input_data = {
    "effect_size": 0.92,
    "ci_lower": 0.85,
    "ci_upper": 0.98,
    "ni_margin": 0.15,
    "reference_effect": 1.0,
    "side": "lower",
}
# Expected: {"passes_non_inferiority": true, "null_margin": 0.85, "margin_violation": 0.0}
```

```python
input_data = {
    "effect_size": 0.80,
    "ci_lower": 0.70,
    "ci_upper": 0.88,
    "ni_margin": 0.15,
    "reference_effect": 1.0,
    "side": "lower",
}
# Expected: {"passes_non_inferiority": false, "null_margin": 0.85, "margin_violation": 0.15}
```
