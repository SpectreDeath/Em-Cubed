---
name: truthmaker-hyperintensional-verifier
description: Demonstrates Phase 7 Kit Fine's Truthmaker Semantics, extracting exact truthmakers (wholly relevant facts s ⊩ A) and hyperintensional groundings.
domain: ONTOLOGY
surfaces:
  - python
  - prolog
  - z3
  - datalog
version: 1.0.0
---

# Truthmaker Hyperintensional Verifier Skill

## Overview

The `truthmaker-hyperintensional-verifier` skill demonstrates **Phase 7 Kit Fine's Truthmaker Semantics** in `Em-Cubed`.

## Exact Truthmaker vs Falsemaker Workflow

```
[ Full Agent State (100 Triples) ] ──> ExactTruthmakerClassifier
                                                │
                                                ▼
                             [ Wholly Relevant Filtering ]
                                                │
                                                ├─► Exact Truthmaker (s ⊩ A): 2 Relevant Triples (Zero Junk)
                                                └─► Hyperintensional Grounding: Topic/Subject-Matter Ground
```

## Truthmaker Sensor Output Example

```json
{
  "proposition": "Folic Acid Sourcing Compliance",
  "is_satisfied": true,
  "ground_explanation": "Exact Truthmaker: Grounded in 2 wholly relevant triples",
  "exact_truthmaker_triples": [
    "USO_001001 rdf:type bfo:IndependentContinuant",
    "USO_001001 rdfs:label Folic Acid"
  ]
}
```
