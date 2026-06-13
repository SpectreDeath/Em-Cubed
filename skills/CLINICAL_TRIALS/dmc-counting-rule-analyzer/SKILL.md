---
name: dmc-counting-rule-analyzer
Domain: CLINICAL_TRIALS
Version: 1.0.0
surfaces:
  - python
  - clingo
description: Multi-surface DMC counting rule analyzer with Python surface for interim analysis and Clingo surface for Answer Set Programming boundary verification.
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

Evaluates masked interim clinical trial data against Data Monitoring Committee (DMC) charter stopping boundaries using Answer Set Programming, returning per-boundary decisions with explicit rule IDs.

# Description

Converts ICH E9 / FDA DMC guidance rules into ASP rules. Input is a masked interim dataset with treatment-arm event counts and nominal p-values. The Clingo solver evaluates whether stopping boundaries (e.g., O'Brien-Fleming, Haybittle-Peto) are breached or whether the trial should continue.

## Python Surface

```python
import math

def _obrien_fleming_scaled(look, num_looks, alpha=0.05, scale=100_000):
    raw = 2.4 * math.sqrt(look / num_looks) * alpha
    return int(raw * scale), int((2.4 * math.sqrt(look / num_looks) * alpha) * scale)

def _haybittle_peto_scaled(look, alpha=0.05, scale=100_000):
    raw = 0.001 if look < 3 else alpha
    return int(raw * scale)

def build_interim_facts(masked_data, boundary="obrien_fleming", alpha=0.05, scale=100_000):
    arms = [a.lower() for a in masked_data.get("arms", [])]
    events = masked_data.get("events", [])
    p_values = masked_data.get("p_values", [])
    timepoints = masked_data.get("timepoints", [])
    num_looks = max(timepoints) if timepoints else len(p_values)

    facts = [f"arm({a})." for a in arms]
    for i, ev in enumerate(events):
        arm = arms[i] if i < len(arms) else "unknown"
        tp = timepoints[i] if i < len(timepoints) else i + 1
        facts.append(f"event_count({arm}, {tp}, {ev}).")

    for i, pv in enumerate(p_values):
        arm = arms[i] if i < len(arms) else "unknown"
        tp = timepoints[i] if i < len(timepoints) else i + 1
        pv_scaled = int(pv * scale)
        if boundary == "obrien_fleming":
            _, b_scaled = _obrien_fleming_scaled(tp, num_looks, alpha, scale)
        else:
            b_scaled = _haybittle_peto_scaled(tp, alpha, scale)
        facts.append(f"p_value_check({arm}, {tp}, {pv_scaled}, {b_scaled}).")

    return facts

def analyze_dmc(masked_data, boundary="obrien_fleming", alpha=0.05):
    facts = build_interim_facts(masked_data, boundary, alpha)
    return {
        "status": "ok",
        "facts": facts,
        "boundary": boundary,
        "alpha": alpha,
        "needs_clingo_evaluation": True,
    }

def main(skill_input):
    masked_data = skill_input.get("masked_data", {})
    boundary = skill_input.get("boundary", "obrien_fleming")
    alpha = skill_input.get("alpha", 0.05)
    return analyze_dmc(masked_data, boundary, alpha)
```

## Clingo Surface

```prolog
% DMC Safety and Efficacy Stopping Boundaries
% Pre-calculated boundary thresholds are passed in as scaled-integer facts from Python.

% Stop for efficacy if the scaled p-value is strictly less than the calculated boundary scale
stop_for_efficacy(Arm, Look) :-
    p_value_check(Arm, Look, PVScaled, BScaled),
    PVScaled < BScaled.

% Stop for futility using a futility-boundary fact (populated by Python if provided)
stop_for_futility(Arm, Look) :-
    futility_check(Arm, Look, ZScaled, FBBoundary),
    ZScaled < FBBoundary.

% A specific look continues if it doesn't trigger efficacy or futility stops
continue_look(Arm, Look) :-
    p_value_check(Arm, Look, _, _),
    not stop_for_efficacy(Arm, Look),
    not stop_for_futility(Arm, Look).

% Dynamic trial continuity: the whole trial continues if ALL active looks pass safely
continue_trial(Arm) :-
    arm(Arm),
    #count { Look : p_value_check(Arm, Look, _, _) } = TotalLooks,
    #count { Look : continue_look(Arm, Look) } = TotalLooks.

#show stop_for_efficacy/2.
#show stop_for_futility/2.
#show continue_trial/1.
```

## Examples

```python
input_data = {
    "masked_data": {
        "arms": ["Treatment", "Control"],
        "events": [45, 60],
        "p_values": [0.008, 0.15],
        "timepoints": [1, 1],
    },
    "boundary": "obrien_fleming",
    "alpha": 0.05,
}
# Expected: {"needs_clingo_evaluation": true, "facts": ["arm(Treatment).", ...]}
```
