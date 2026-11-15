---
name: palantir-advanced-ontology-agent
domain: ONTOLOGY
version: 1.0.0
surfaces:
  - python
  - prolog
  - z3
  - datalog
description: Palantir Foundry-style advanced ontology primitives engine. Implements derived property reducers (SUM, COUNT, MAX, AVG), bi-directional object backlink resolution, and polymorphic interface contracts over semantic knowledge graphs. Use when modeling enterprise ontology objects, calculating dynamic aggregate properties over linked graph triples, managing inverse backlinks, or enforcing shared interface contracts across disparate object types.
purpose: Execute Palantir Foundry-style derived property reducers, bi-directional backlinks, and polymorphic interface contracts.
dependencies: []
tags:
  - palantir-ontology
  - derived-properties
  - object-backlinks
  - polymorphic-interfaces
  - property-reducers
inputs:
  object_type:
    type: string
    required: true
    description: Name of the primary object type (e.g. 'Order', 'Flight', 'Account').
  linked_triples:
    type: array
    required: true
    description: Semantic triples representing linked child entities and relation edges.
  reducer_spec:
    type: object
    required: false
    description: 'Calculation rules (e.g. `{"total_cost": "SUM(LineItem.cost)"}`).'
outputs:
  materialized_object:
    type: object
    description: Entity object with calculated derived properties and resolved backlinks.
  interface_compliance:
    type: boolean
    description: True if object satisfies required interface contract properties.
  backlink_map:
    type: object
    description: Map of inverse relation edges indexed by target entity.
---

# Palantir Advanced Ontology Agent Engine

`palantir-advanced-ontology-agent` implements **Phase 9 Palantir-Style Advanced Ontology Primitives** in `Em-Cubed`. It elevates semantic triples into rich enterprise digital twins by computing real-time derived property aggregations (SUM, COUNT, AVG), resolving bi-directional graph backlinks, and binding polymorphic interface contracts.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Advanced Ontology Progression

```
[1. Schema & Link Invariant Audit] → [2. Derived Reducer Calculation] → [3. Visual Brief] → [4. Checkpoint] → [5. Backlink & Interface Bind]
```

### Stage 1: Schema & Link Invariant Audit
1. Ingest `linked_triples` and identify primary subject node and linked children.
2. Verify child numeric properties and relation predicate names.

> **Completion criterion**: Object graph indexed with typed edge relations.

---

### Stage 2: Derived Property Reducer Calculation
1. Execute aggregation reducers over linked child collections:
   - **SUM**: Aggregate monetary costs or quantities ($\sum \text{cost}_i$).
   - **COUNT**: Count linked line items or historical interactions.
   - **MAX / MIN**: Find extreme values (e.g., *latest transaction timestamp*).
2. Materialize derived fields into object state dictionary.

> **Completion criterion**: Derived properties calculated deterministically.

---

### Stage 3: The Visual Brief
For complex object schemas or multi-level backlink trees, generate an interactive brief:
- **Location**: Write to `%TEMP%\palantir-ontology-brief-<timestamp>.html` (Windows) or `/tmp/palantir-ontology-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render object card, incoming/outgoing backlinks, and reducer computation tree.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before caching or persisting materialized derived states:
1. Verify reducer numerical stability (check for zero division on AVG or missing required child values).
2. If schema violations occur against polymorphic interface, pause and report missing properties.

> **Completion criterion**: Reducer calculations certified complete and stable.

---

### Stage 5: Backlink Resolution & Polymorphic Interface Bind
1. Index inverse relation edges to establish bidirectional object navigation.
2. Validate object state against polymorphic interface definition (e.g. `IAsset`, `ITransaction`).
3. Emit materialized digital twin payload.

> **Completion criterion**: Object emitted with `interface_compliance: true` and bidirectional backlink registry.

---

## Surface References

### Python Palantir Primitives Surface

```python
from typing import List, Dict, Any

def materialize_palantir_object(subject: str, line_items: List[Dict[str, float]], interface_name: str = "ITransaction") -> Dict[str, Any]:
    # Derived property reducers
    total_cost = sum(item.get("cost", 0.0) for item in line_items)
    item_count = len(line_items)
    
    # Polymorphic interface verification
    has_required_fields = (total_cost >= 0.0) and (item_count > 0)
    
    return {
        "materialized_object": {
            "subject": subject,
            "derived_total_cost": round(total_cost, 2),
            "derived_line_item_count": item_count
        },
        "interface_compliance": has_required_fields,
        "backlink_map": {
            subject: [item.get("id") for item in line_items]
        }
    }
```

---

## Anti-Patterns & Guardrails

- **Stale Derived Cache** — Reading derived property values without re-evaluating when underlying child triples are mutated. Always compute fresh or use invalidation hooks.
- **Asymmetric Backlink Drift** — Mutating a forward edge $A \xrightarrow{rel} B$ without updating inverse backlink $B \xleftarrow{inv} A$.
- **Polymorphic Interface Fragmentation** — Defining dozens of bespoke object interfaces instead of standard reusable contracts (`IAsset`, `IEvent`, `ILocation`).
