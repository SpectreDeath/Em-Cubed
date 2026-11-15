---
name: knowledge-elicitation-framework
domain: ONTOLOGY
version: 1.0.0
surfaces:
  - python
  - prolog
  - datalog
description: End-to-end knowledge elicitation pipeline compiling unstructured natural language into formal BFO/CCO ontologies. Executes the 6-stage operational pipeline through Domain-Specific Questions (DSQ), Ranganathan PMEST facet classification (Personality, Matter, Energy, Space, Time), Competency Questions (CQ), OntoClean Independent Continuant vs Relative Role partitioning with opaque IRIs, Common Logic Echo dialogue generation, and formal triple extraction. Use when converting messy executive transcripts into formal ontologies, eliciting supply chain schemas, or partitioning entities with OntoClean rigor.
purpose: Transform unstructured executive transcripts and domain expert language into formal, OntoClean-partitioned BFO/CCO knowledge graphs.
dependencies: []
tags:
  - knowledge-elicitation
  - pmest-facets
  - ontoclean
  - competency-questions
  - bfo-alignment
  - common-logic-echo
inputs:
  transcript_text:
    type: string
    required: true
    description: Natural language text, interview transcript, or domain specification.
  ontology_prefix:
    type: string
    required: false
    description: "Namespace prefix for opaque IRIs (e.g. 'USO', 'AGRI', 'SUPPLY'). Default 'USO'."
outputs:
  pmest_facets:
    type: object
    description: Classified terms across Personality, Matter, Energy, Space, and Time.
  competency_questions:
    type: array
    description: Derived precision Competency Questions (CQs).
  ontoclean_partitions:
    type: array
    description: Partitioned entities (Independent Continuant vs Relative Role) with opaque IRIs.
  formal_triples:
    type: array
    description: Verified BFO/CCO ontology triple assertions.
---

# Knowledge Elicitation Framework Engine

`knowledge-elicitation-framework` implements the authoritative 6-stage operational pipeline in `Em-Cubed` for eliciting formal, machine-actionable ontologies from unstructured domain expert transcripts and interviews.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 6-Stage Elicitation Progression

```
[1. Strategic DSQ] → [2. PMEST Facet Analysis] → [3. CQ Disambiguation] → [4. OntoClean Partition] → [5. Common Logic Echo] → [6. BFO Alignment]
```

### Stage 1: Strategic Foundation & DSQ Formulation
1. Deconstruct vague executive concerns into granular Domain-Specific Questions (DSQs).
2. Isolate core operational scope and domain boundaries.

> **Completion criterion**: Discrete DSQs formulated targeting specific epistemic gaps.

---

### Stage 2: Idea Plane PMEST Facet Classification
1. Classify extracted concepts across Ranganathan's fundamental facets:
   - **Personality**: Core focal entities (e.g., *Folic Acid, Rice Plant*).
   - **Matter**: Material composition / physical properties (*Molecular Weight, Nitrogen*).
   - **Energy**: Active processes, transformations (*Chemical Synthesis, Transportation*).
   - **Space**: Spatial locations, geo boundaries (*Uruguay, Factory Floor*).
   - **Time**: Temporal bounds (*2024 Harvest Period*).

> **Completion criterion**: All key domain terms mapped into 5 PMEST facet buckets with zero orphans.

---

### Stage 3: Competency Question (CQ) Disambiguation
1. Derive formal Competency Questions (CQs) that the final ontology must answer.
2. Resolve polysemy and conceptual ambiguities through structured questions.

> **Completion criterion**: Explicit list of checkable Competency Questions generated.

---

### Stage 4: OntoClean Partitioning & Opaque IRIs
1. Apply OntoClean metaphysical rigor:
   - **Independent Continuant**: Entities existing independently of relational contexts (`USO_001001: Folic Acid`).
   - **Relative Role / Realizable**: Extrinsic entities existing only in context of a relation (`USO_001002: Regulated Product`).
2. Mint non-semantic, opaque IRIs (`PREFIX_XXXXXX`) to prevent semantic drift.

> **Completion criterion**: Entities partitioned into rigid kinds vs roles with minted opaque IRIs.

---

### Stage 5: Common Logic Echo Verification
1. Generate natural language echo dialogues confirming ontological commitments with domain experts:
   > *"Is 'Regulated Product' an extrinsic role played by an independent entity within the context 'Uruguayan Regulatory Framework'?"*
2. Verify expert alignment.

> **Completion criterion**: Confirmation echo dialogue generated and validated.

---

### Stage 6: BFO / CCO Formal Triple Extraction
1. Ground partitioned entities into BFO upper classes and CCO relations.
2. Emit formal `OntologyTriple` assertions ready for ledger ingestion.

> **Completion criterion**: Formal triples extracted and validated with zero disjointness violations.

---

## Surface References

### Python Knowledge Elicitation Surface

```python
from typing import Dict, Any, List

def run_elicitation_pipeline(text: str, prefix: str = "USO") -> Dict[str, Any]:
    pmest = {
        "personality": ["Folic Acid", "Rice Plant"],
        "matter": ["Molecular Weight", "Nitrogen Content"],
        "energy": ["Chemical Synthesis", "Quality Inspection"],
        "space": ["Uruguay", "Processing Facility"],
        "time": ["2024 Harvest"]
    }
    
    partitions = [
        {"id": f"{prefix}_001001", "label": "Folic Acid", "type": "bfo:IndependentContinuant"},
        {"id": f"{prefix}_001002", "label": "Regulated Product", "type": "bfo:Role", "context": "RegulatoryFramework"}
    ]
    
    triples = [
        f"{prefix}_001001 rdf:type bfo:IndependentContinuant",
        f"{prefix}_001002 rdf:type bfo:Role",
        f"{prefix}_001001 bfo:bearerOf {prefix}_001002"
    ]
    
    return {
        "pmest_facets": pmest,
        "competency_questions": ["What is the chemical variety and regulatory status of this batch?"],
        "ontoclean_partitions": partitions,
        "formal_triples": triples
    }
```

---

## Anti-Patterns & Guardrails

- **Semantic IRIs** — Naming IRIs like `ex:FolicAcidThatIsRegulated` rather than opaque codes `USO_001001`. Always use opaque IRIs.
- **Confusing Roles with Independent Kinds** — Modeling `Customer` or `RegulatedProduct` as a subclass of `MaterialEntity` rather than an extrinsic `Role` borne by an entity.
- **Skipping PMEST Faceting** — Jumping directly from natural language to triples without structuring the idea plane.
