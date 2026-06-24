---
name: sae-reporting-threshold-tester
domain: CLINICAL_TRIALS
version: 1.0.0
surfaces:
- python
- z3
description: Multi-surface SAE reporting threshold tester with Python surface for adverse event count analysis and Z3 surface
  for FDA 21 CFR 312.32 timing constraint verification.
compatibility: PYTHON
allowed-tools: '- read

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

  '
---

# Purpose

Determines whether observed serious adverse event counts and expected/observed ratios breach FDA 21 CFR 312.32 expedited reporting thresholds (7-day and 15-day timelines) by encoding regulatory timing constraints as arithmetic relations in Z3.

# Description

Given aggregate safety data and reporting rules, computes whether the observed event counts and ratios breach mandatory 7/15-day SUSAR reporting timelines. Z3 encodes the linear threshold constraints as arithmetic relations and returns `sat`/`unsat` with a concrete justification.

## Python Surface

```python
def compute_sae_reporting(sae_counts, expected_counts, rule):
    expedited = rule.get("expedited", False)
    threshold = rule.get("threshold", 2.0)
    observed_ratio = 0.0
    for drug, obs in sae_counts.items():
        exp = expected_counts.get(drug, 1)
        observed_ratio = max(observed_ratio, obs / exp if exp > 0 else 0)
    needs_expedited = expedited and observed_ratio >= threshold
    return {
        "status": "ok",
        "observed_ratio": observed_ratio,
        "threshold": threshold,
        "needs_expedited_reporting": needs_expedited,
    }

def main(skill_input):
    sae_counts = skill_input.get("sae_counts", {})
    expected_counts = skill_input.get("expected_counts", {})
    rule = skill_input.get("rule", {})
    return compute_sae_reporting(sae_counts, expected_counts, rule)
```

## Z3 Surface

```python
def sae_reporting_z3(observed, expected, threshold, timeline_days):
    from z3 import Solver, Real, sat

    o = Real("observed")
    e = Real("expected")
    t = Real("threshold")
    td = Real("timeline_days")

    s7 = Solver()
    s7.add(o == observed, e == expected, t == threshold, td == timeline_days)
    s7.add(o / e >= t, td <= 7)
    if s7.check() == sat:
        return {"status": "ok", "z3_result": "sat", "breaches_timeline": True, "timeline": "7-day"}

    s15 = Solver()
    s15.add(o == observed, e == expected, t == threshold, td == timeline_days)
    s15.add(o / e >= t, td > 7, td <= 15)
    if s15.check() == sat:
        return {"status": "ok", "z3_result": "sat", "breaches_timeline": True, "timeline": "15-day"}

    return {"status": "ok", "z3_result": "unsat", "breaches_timeline": False}

def main(skill_input):
    observed = float(skill_input.get("observed", 0))
    expected = float(skill_input.get("expected", 1))
    threshold = float(skill_input.get("threshold", 2.0))
    timeline_days = float(skill_input.get("timeline_days", 7))
    return sae_reporting_z3(observed, expected, threshold, timeline_days)
```

## Examples

```python
input_data = {
    "observed": 5,
    "expected": 1,
    "threshold": 2.0,
    "timeline_days": 7,
}
# Expected: {"breaches_timeline": true, "timeline": "7-day"}
```

 ```python
input_data = {
    "sae_counts": {"Drug_X": 3},
    "expected_counts": {"Drug_X": 2},
    "rule": {"expedited": True, "threshold": 1.5},
}
# Expected: {"needs_expedited_reporting": True, "observed_ratio": 1.5, "threshold": 1.5}
```
