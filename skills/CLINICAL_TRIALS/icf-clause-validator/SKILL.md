---
name: Informed Consent Form Clause Validator
Domain: CLINICAL_TRIALS
Version: 1.0.0
surfaces:
  - python
  - z3
---

# Purpose

Validates that a parsed/annotated informed consent form contains all mandatory regulatory clauses required by 21 CFR Part 50 and returns missing clause IDs with an unsat core when the document is incomplete.

# Description

Encodes the eight required consent elements as boolean constraints in Z3. Python pre-processes the ICF text into an annotated clause dictionary. Z3 checks mandatory presence and structural soundness (e.g., risks section cannot be empty if procedures section is non-empty). Returns missing clause IDs and an unsat core for incomplete filings.

## Python Surface

```python
def parse_icf_sections(icf_text):
    required_present = {
        "research_purpose": bool(icf_text.get("research_purpose", "")),
        "study_duration": bool(icf_text.get("study_duration", "")),
        "procedures": bool(icf_text.get("procedures", "")),
        "risks": bool(icf_text.get("risks", "")),
        "benefits": bool(icf_text.get("benefits", "")),
        "alternatives": bool(icf_text.get("alternatives", "")),
        "confidentiality": bool(icf_text.get("confidentiality", "")),
        "voluntary_participation": bool(icf_text.get("voluntary_participation", "")),
        "contact_info": bool(icf_text.get("contact_info", "")),
        "compensation": bool(icf_text.get("compensation", "")),
    }
    return required_present

def validate_icf_z3(icf_text):
    from z3 import Bool, Solver, sat, unsat, And, Not

    clauses = parse_icf_sections(icf_text)
    bools = {k: Bool(k) for k in clauses}
    solver = Solver()
    for k, present in clauses.items():
        solver.add(bools[k] == present)
    risks_empty = not clauses.get("risks", False)
    procedures_nonempty = clauses.get("procedures", False)
    if risks_empty and procedures_nonempty:
        solver.add(Not(bools["risks"]))
    missing = [k for k, v in clauses.items() if not v]
    if solver.check() == unsat:
        return {
            "status": "ok",
            "valid_icf": False,
            "missing_clauses": missing,
            "unsat_core": missing,
        }
    return {
        "status": "ok",
        "valid_icf": True,
        "missing_clauses": missing,
        "unsat_core": [],
    }

def main(skill_input):
    icf_text = skill_input.get("icf_text", {})
    return validate_icf_z3(icf_text)
```

## Z3 Surface

```python
from z3 import Bool, Solver, sat, unsat, And, Not

def z3_validate_icf(icf_text):
    clauses = parse_icf_sections(icf_text)
    bools = {k: Bool(k) for k in clauses}
    solver = Solver()
    for k, present in clauses.items():
        solver.add(bools[k] == present)
    risks_empty = not clauses.get("risks", False)
    if risks_empty:
        solver.add(Not(bools["risks"]))
    if solver.check() == unsat:
        return {"status": "invalid", "missing": [k for k, v in clauses.items() if not v]}
    return {"status": "valid", "missing": []}
```

## Examples

```python
input_data = {
    "icf_text": {
        "research_purpose": "Study will evaluate drug X for condition Y.",
        "study_duration": "12 weeks with 6 follow-up visits.",
        "procedures": "Blood draws at each visit, ECG at baseline.",
        "risks": "",
        "benefits": "No direct benefit to subject.",
        "alternatives": "Subject may choose standard of care outside study.",
        "confidentiality": "Data will be de-identified per HIPAA.",
        "voluntary_participation": "Participation is voluntary; subject may withdraw.",
        "contact_info": "PI: Dr. Smith, 555-1234.",
        "compensation": "No compensation for participation.",
    }
}
# Expected: {"valid_icf": False, "missing_clauses": ["risks"], "unsat_core": ["risks"]}
```
