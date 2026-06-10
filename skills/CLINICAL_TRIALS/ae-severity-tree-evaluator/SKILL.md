---
name: AE Severity Tree Evaluator
Domain: CLINICAL_TRIALS
Version: 1.0.0
surfaces:
  - python
  - prolog
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
    lab_name = ae_record["lab_name"]
    observed = float(ae_record["observed_value"])
    matched_grades = []
    for rule in grade_rules:
        r_lab = rule.get("lab_name", "")
        if r_lab != lab_name:
            continue
        r_low = rule.get("grade_low", float("-inf"))
        r_high = rule.get("grade_high", float("inf"))
        r_grade = rule.get("grade")
        if r_low <= observed <= r_high:
            matched_grades.append({"grade": r_grade, "rule_lab": r_lab, "range": [r_low, r_high]})
    if not matched_grades:
        return {"status": "ok", "grade": None, "pathway": [], "contradictions": []}
    best = max(matched_grades, key=lambda x: x["grade"])
    contradictions = []
    if len(matched_grades) > 1:
        for m in matched_grades:
            if m is not best:
                contradictions.append({"conflict_with": best["grade"], "rule": m})
    return {
        "status": "ok",
        "grade": best["grade"],
        "pathway": matched_grades,
        "contradictions": contradictions,
    }

def main(skill_input):
    ae_record = skill_input.get("ae_record", {})
    grade_rules = skill_input.get("grade_rules", [])
    return grade_ae_severity(0.0, "", grade_rules, ae_record)
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

```prolog
?- ae_record(ae1, Hemoglobin, 7.2), evaluate_ae(ae1, Grade, Path, C).
% Expected: Grade = 3, Path = [rule(Hemoglobin, 7.2, 3), ...], C = []
```
