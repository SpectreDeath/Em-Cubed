---
name: palantir-advanced-ontology-agent
description: Demonstrates Phase 9 Palantir-Style Advanced Ontology primitives, including derived property reducers (SUM/COUNT), bi-directional backlinks, and polymorphic interface contracts.
domain: ONTOLOGY
surfaces:
  - python
  - prolog
  - z3
  - datalog
version: 1.0.0
---

# Palantir Advanced Ontology Agent Skill

## Overview

The `palantir-advanced-ontology-agent` skill demonstrates **Phase 9 Palantir-Style Advanced Ontology primitives** in `Em-Cubed`.

## Industrial Advanced Ontology Workflow

```
[ Linked Triples ] ──► ObjectBacklinkRegistry ──► Automatic Bi-Directional Backlink Resolution
       │
       ├─► DerivedPropertyReducer (SUM / COUNT / MAX) ──► Dynamic Calculated Fields
       └─► InterfaceImplementation ──► Polymorphic Interface Contracts (Asset / Transaction)
```

## Derived Reducer & Interface Example

```json
{
  "subject": "Order_1001",
  "derived_total_cost": 450.00,
  "derived_line_item_count": 3,
  "validates_interface": true,
  "backlink_count": 3
}
```
