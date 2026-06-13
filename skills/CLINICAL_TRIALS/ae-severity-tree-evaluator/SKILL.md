---
name: ae-severity-tree-evaluator
Domain: CLINICAL_TRIALS
Version: 1.0.0
surfaces:
  - python
  - prolog
description: Multi-surface adverse event severity evaluator with Python surface for MedDRA/CTCAE grading and Prolog surface for decision pathway tree verification.
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

Evaluates structured adverse event records against MedDRA/CTCAE severity grading rules and returns a graded severity node with an explicit decision pathway tree, detecting contradictory concurrent grade assignments.

# Description

Implements severity grading rules as deterministic functions in Python and as relational clauses in Prolog. Input is a structured AE record containing lab values, clinical observations, and grading criteria. Output is the assigned severity grade together with the rule IDs that triggered, plus any detected contradictions.

## Python Surface

```python
def grade_ae_severity(lab_value, lab_units, grade_rules, ae_record):
    if "lab_name" not in ae_record or "observed_value" not in ae_record:
        return {"status": "error", "message": "ae_record must contain lab_name and observed_value"}
    try:
        observed = float(ae_record["observed_value"])
    except (TypeError, ValueError):
        return {"status": "error", "message": "observed_value must be numeric"}
    lab_name = ae_record["lab_name"]
    matched_grades = []
    for rule in grade_rules:
        r_lab = rule.get("lab_name", "")
        if r_lab != lab_name:
            continue
        r_low = rule.get("grade_low", float("-inf"))
        r_high = rule.get("grade_high", float("inf"))
        bound_lo = min(r_low, r_high)
        bound_hi = max(r_low, r_high)
        r_grade = rule.get("grade")
        if bound_lo <= observed <= bound_hi:
            matched_grades.append({"grade": r_grade, "rule_lab": r_lab, "range": [bound_lo, bound_hi]})
    if not matched_grades:
        return {"status": "ok", "grade": None, "pathway": [], "contradictions": []}
    best_grade = max(m["grade"] for m in matched_grades)
    contradictions = []
    if len(matched_grades) > 1:
        for m in matched_grades:
            if m["grade"] != best_grade:
                contradictions.append({"conflict_with": best_grade, "rule": m})
    return {
        "status": "ok",
        "grade": best_grade,
        "pathway": matched_grades,
        "contradictions": contradictions,
    }

def evaluate_ae_tree(ae_records, grade_rules):
    if not ae_records:
        return {"status": "error", "message": "ae_records must be a non-empty list"}
    all_grades = []
    pathways = []
    contradictions = []
    for rec in ae_records:
        result = grade_ae_severity(0.0, "", grade_rules, rec)
        if result["status"] == "error":
            return result
        if result["grade"] is not None:
            all_grades.append(result["grade"])
        for p in result["pathway"]:
            pathways.append(p)
        contradictions.extend(result["contradictions"])
    final_grade = max(all_grades) if all_grades else None
    return {
        "status": "ok",
        "grade": final_grade,
        "pathway": pathways,
        "contradictions": contradictions,
    }

def main(skill_input):
    ae_records = skill_input.get("ae_records", [])
    grade_rules = skill_input.get("grade_rules", [])
    return evaluate_ae_tree(ae_records, grade_rules)
```

## Prolog Surface

```prolog
severity_grade(lab_name, observed, grade) :-
    grade_rule(lab_name, grade, low, high),
    observed >= low,
    observed =< high,
    !.

grade_rule("Hemoglobin", 1, 10.0, 9.5).
grade_rule("Hemoglobin", 2, 9.4, 8.0).
grade_rule("Hemoglobin", 3, 7.9, 6.5).
grade_rule("Hemoglobin", 4, 0.0, 6.4).
grade_rule("Neutrophils", 1, 1.5, 1.0).
grade_rule("Neutrophils", 2, 0.99, 0.75).
grade_rule("Neutrophils", 3, 0.74, 0.5).
grade_rule("Neutrophils", 4, 0.0, 0.49).

contradictory(AE_ID, Grade1, Grade2) :-
    ae_record(AE_ID, Lab, Value),
    severity_grade(Lab, Value, Grade1),
    severity_grade(Lab, Value, Grade2),
    Grade1 \= Grade2.

evaluate_ae(AE_ID, Grade, Pathway, Contradictions) :-
    ae_record(AE_ID, Lab, Value),
    setof(G, severity_grade(Lab, Value, G), Grades),
    last(Grades, Grade),
    findall(rule(Lab, Value, G), severity_grade(Lab, Value, G), Pathway),
    findall(conflict(G1, G2),
            (member(G1, Grades), member(G2, Grades), G1 \= G2),
            Contradictions).
```

## Examples

```python
input_data = {
    "ae_record": {"lab_name": "Hemoglobin", "observed_value": 7.2},
    "grade_rules": [
        {"lab_name": "Hemoglobin", "grade": 1, "grade_low": 10.0, "grade_high": 9.5},
        {"lab_name": "Hemoglobin", "grade": 2, "grade_low": 9.4, "grade_high": 8.0},
        {"lab_name": "Hemoglobin", "grade": 3, "grade_low": 7.9, "grade_high": 6.5},
        {"lab_name": "Hemoglobin", "grade": 4, "grade_low": 0.0, "grade_high": 6.4},
    ],
}
# Expected: {"grade": 3, "pathway": [...], "contradictions": []}
```

```python
input_data = {
    "ae_records": [
        {"lab_name": "Hemoglobin", "observed_value": 7.2},
        {"lab_name": "Hemoglobin", "observed_value": 5.0},
    ],
    "grade_rules": [
        {"lab_name": "Hemoglobin", "grade": 1, "grade_low": 10.0, "grade_high": 9.5},
        {"lab_name": "Hemoglobin", "grade": 2, "grade_low": 9.4, "grade_high": 8.0},
        {"lab_name": "Hemoglobin", "grade": 3, "grade_low": 7.9, "grade_high": 6.5},
        {"lab_name": "Hemoglobin", "grade": 4, "grade_low": 0.0, "grade_high": 6.4},
    ],
}
# Expected: {"grade": 4, "pathway": [...], "contradictions": []}
```

```prolog
?- ae_record(ae1, Hemoglobin, 7.2), evaluate_ae(ae1, Grade, Path, C).
% Expected: Grade = 3, Path = [rule(Hemoglobin, 7.2, 3), ...], C = []
```

```prolog
?- ae_record(ae1, Hemoglobin, 7.2), evaluate_ae(ae1, Grade, Path, C).
% Expected: Grade = 3, Path = [rule(Hemoglobin, 7.2, 3), ...], C = []
```
