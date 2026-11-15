---
name: tri-engine-cross-domain-transfer
domain: ONTOLOGY
version: 1.0.0
surfaces:
  - python
  - prolog
  - datalog
description: Cross-domain knowledge transfer and concept mapping engine using Basic Formal Ontology (BFO) upper categories. Maps domain concept taxonomies across biodefense, geopolitical crisis, supply chain, and financial audit domains through top-level BFO alignments (Material Entity, Process, Role), preserving relational semantics and transferring rule sets without manual re-engineering. Use when transferring knowledge across distinct domain silos, unifying cross-domain entity taxonomies, or mapping heterogeneous ontologies.
purpose: Map concept taxonomies and transfer relational triple assertions across disparate domain silos via BFO upper categories.
dependencies: []
tags:
  - cross-domain-transfer
  - bfo-upper-ontology
  - taxonomy-mapping
  - concept-alignment
  - semantic-transfer
inputs:
  source_domain:
    type: string
    required: true
    description: Source domain identifier (e.g. 'Biodefense', 'Epidemiology').
  target_domain:
    type: string
    required: true
    description: Target domain identifier (e.g. 'Geopolitics', 'FinancialAudit').
  source_triples:
    type: array
    required: true
    description: Knowledge triples in source domain to map and transfer.
  concept_overrides:
    type: object
    required: false
    description: Explicit domain-specific term translation mappings.
outputs:
  transferred_triples:
    type: array
    description: Transformed knowledge triples valid in the target domain ontology.
  alignment_confidence:
    type: number
    description: Semantic alignment confidence score in [0.0, 1.0].
  bfo_upper_category:
    type: string
    description: Shared BFO upper-level category (e.g. 'bfo:MaterialEntity', 'bfo:Process').
---

# Tri-Engine Cross-Domain Knowledge Transfer Engine

`tri-engine-cross-domain-transfer` bridges isolated domain silos (such as biodefense, geopolitical escalation, and financial audit) by projecting domain concepts onto shared **Basic Formal Ontology (BFO)** upper categories ($MaterialEntity, Process, Role, Disposition$). This allows abstract relational patterns learned in one domain (e.g. epidemic diffusion) to be transferred directly into another (e.g. cyber contagion or financial panic).

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Cross-Domain Transfer Progression

```
[1. Source Domain Invariant Audit] → [2. BFO Category Alignment] → [3. Visual Brief] → [4. Checkpoint] → [5. Triple Translation & Verification]
```

### Stage 1: Source Domain Invariant Audit
1. Ingest `source_triples` and verify domain taxonomy definitions.
2. Index entity subjects, predicates, and objects into relational AST.

> **Completion criterion**: Source triples parsed and indexed against source domain schema.

---

### Stage 2: BFO Upper Category Alignment
1. Map source and target concepts to common BFO upper taxonomy roots:
   $$\text{PathogenVariant} \xrightarrow{\text{subClassOf}} \text{bfo:MaterialEntity} \xleftarrow{\text{subClassOf}} \text{StateActor}$$
   $$\text{OutbreakEvent} \xrightarrow{\text{subClassOf}} \text{bfo:Process} \xleftarrow{\text{subClassOf}} \text{MilitaryConflict}$$
2. Compute semantic alignment confidence based on structural similarity and taxonomic distance.

> **Completion criterion**: Concepts mapped to common BFO upper category with alignment score $\ge 0.80$.

---

### Stage 3: The Visual Brief
For complex cross-domain taxonomy alignments, generate an interactive visual brief:
- **Location**: Write to `%TEMP%\cross-domain-transfer-brief-<timestamp>.html` (Windows) or `/tmp/cross-domain-transfer-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render the bipartite taxonomy graph linking source domain, BFO upper nodes, and target domain.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before injecting transferred assertions into the target domain ledger:
1. Verify that transferred predicates do not violate target domain class disjointness axioms.
2. If alignment confidence is below threshold ($< 0.75$), pause and request human validation.

> **Completion criterion**: Transferred assertions verified compliant with target ontology constraints.

---

### Stage 5: Triple Translation & Ledger Emit
1. Apply mapping dictionary to substitute subjects, predicates, and objects.
2. Emit target-domain triples along with alignment report and BFO classification.

> **Completion criterion**: Output triples emitted and validated under target domain schema.

---

## Surface References

### Python Cross-Domain Transfer Surface

```python
from typing import List, Dict, Any

class CrossDomainTransferEngine:
    @staticmethod
    def map_and_transfer(source_triples: List[Dict[str, str]], source_dom: str, target_dom: str) -> Dict[str, Any]:
        # Mapping rules via BFO upper categories
        term_map = {
            "PathogenVariant_X": "StateActor_Alpha",
            "causes": "initiates",
            "OutbreakEvent_01": "ConflictEvent_01"
        }
        
        transferred = []
        for t in source_triples:
            s = term_map.get(t.get("subject", ""), t.get("subject", ""))
            p = term_map.get(t.get("predicate", ""), t.get("predicate", ""))
            o = term_map.get(t.get("object", ""), t.get("object", ""))
            transferred.append({"subject": s, "predicate": p, "object": o, "domain": target_dom})
            
        return {
            "transferred_triples": transferred,
            "alignment_confidence": 0.92,
            "bfo_upper_category": "bfo:Process"
        }
```

---

## Anti-Patterns & Guardrails

- **Category Mixing** — Mapping a BFO `Continuant` (e.g. an object or actor) to a BFO `Occurrent` (e.g. an event or process). Always preserve category parity.
- **Predicate Meaning Inversion** — Transferring causal predicates (`causes`, `inhibits`) into passive or ungrounded associations without directionality checks.
- **Orphaned Target Triples** — Transferring assertions without verifying that mapped target concepts exist in target taxonomy.
