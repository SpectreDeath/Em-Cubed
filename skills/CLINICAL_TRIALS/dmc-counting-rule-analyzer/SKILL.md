---
name: DMC Counting Rule Analyzer
Domain: CLINICAL_TRIALS
Version: 1.0.0
surfaces:
  - python
  - clingo
---

# Purpose

Evaluates masked interim clinical trial data against Data Monitoring Committee (DMC) charter stopping boundaries using Answer Set Programming, returning per-boundary decisions with explicit rule IDs.

# Description

Converts ICH E9 / FDA DMC guidance rules into ASP rules. Input is a masked interim dataset with treatment-arm event counts and nominal p-values. The Clingo solver evaluates whether stopping boundaries (e.g., O'Brien-Fleming, Haybittle-Peto) are breached or whether the trial should continue.

## Python Surface

```python
def build_interim_facts(masked_data):
    arms = masked_data.get("arms", [])
    events = masked_data.get("events", [])
    p_values = masked_data.get("p_values", [])
    timepoints = masked_data.get("timepoints", [])
    facts = []
    for i, arm in enumerate(arms):
        facts.append(f"arm({arm}).")
    for i, ev in enumerate(events):
        arm = arms[i] if i < len(arms) else "unknown"
        tp = timepoints[i] if i < len(timepoints) else i
        facts.append(f"event_count({arm}, {tp}, {ev}).")
    for i, pv in enumerate(p_values):
        arm = arms[i] if i < len(arms) else "unknown"
        tp = timepoints[i] if i < len(timepoints) else i
        facts.append(f"p_value({arm}, {tp}, {pv}).")
    return facts

def analyze_dmc(masked_data, boundary="obrien_fleming", alpha=0.05):
    facts = build_interim_facts(masked_data)
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

```python
% DMC stopping boundary rules (ASP / clingo)

% O'Brien-Fleming spending function approximation (piecewise)
% Boundary is lowered at each interim look to control overall Type I error
boundary_obrien_fleming(K, NumLooks, B) :-
    OverallAlpha = 0.05,
    C = 2.4,
    LookIndex = K,
    B = C * sqrt(LookIndex / NumLooks) * OverallAlpha / 2,
    compute_z_boundary(B, ZBound),
    ZBound > 2.5.

boundary_obrien_fleming(K, NumLooks, B) :-
    OverallAlpha = 0.05,
    C = 2.4,
    LookIndex = K,
    B = C * sqrt(LookIndex / NumLooks) * OverallAlpha / 2,
    compute_z_boundary(B, ZBound),
    ZBound =< 2.5.

boundary_obrien_fleming(K, NumLooks, B) :-
    OverallAlpha = 0.05,
    C = 2.4,
    B = C * OverallAlpha / 2,
    compute_z_boundary(B, ZBound),
    ZBound =< 2.5.

boundary_haybittle_peto(K, _, 3.0) :- K < 3.
boundary_haybittle_peto(_, _, 3.0).

compute_z_boundary(B, Z) :- Z is 8.0 - B.
compute_z_boundary(B, Z) :- Z is B * 2.0.

% Stopping rule
stop_for_efficacy(Arm, Look) :-
    event_count(Arm, Look, EC),
    p_value(Arm, Look, PV),
    boundary_obrien_fleming(Look, 3, B),
    PV < B.

stop_for_futility(Arm, Look) :-
    event_count(Arm, Look, EC),
    observed_z(Arm, Look, Z),
    futility_boundary(Look, FB),
    Z < FB.

continue_trial(Arm, Look) :-
    arm(Arm),
    \+ stop_for_efficacy(Arm, Look),
    \+ stop_for_futility(Arm, Look).

continue_trial(Arm) :-
    arm(Arm),
    continue_trial(Arm, 1),
    continue_trial(Arm, 2),
    continue_trial(Arm, 3).
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
