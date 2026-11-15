# Skill Summary Card: `palantir-advanced-ontology-agent`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        palantir-advanced-ontology-agent          │
│ Category:    ONTOLOGY / Palantir Object Primitives     │
│ Invocation:  /palantir-advanced-ontology-agent         │
│ Trigger:     "palantir ontology", "derived reducer",   │
│              "object backlinks", "polymorphic interface"│
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Execute derived property reducers,        │
│              bi-directional backlinks, and polymorphic │
│              interface contracts over graph objects.   │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Schema Audit** | Parse linked triples and object definitions | Object Graph AST | Edge relations & numeric types validated |
| **2. Derived Reducer** | Compute SUM, COUNT, MAX aggregations | Materialized State | Derived fields calculated deterministically |
| **3. Visual Brief** | Render object twin and backlink network | `%TEMP%\palantir-ontology-brief-*.html`| Dark theme HTML object card brief |
| **4. Checkpoint** | Validate numeric stability and interface rules | Validation Record | All required interface fields present |
| **5. Backlinks & Bind**| Resolve bidirectional edges and emit | Final Object Payload | `interface_compliance: true` returned |

---

## Invariants & Guardrails

- [ ] **Bidirectional Parity**: Every forward relation must resolve an inverse backlink.
- [ ] **Deterministic Aggregation**: Reducers must handle empty child collections gracefully (e.g. `COUNT = 0`, `SUM = 0.0`).
- [ ] **Interface Type Safety**: Implemented interfaces must validate all required property contracts.
