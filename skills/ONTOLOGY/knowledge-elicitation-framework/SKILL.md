---
name: knowledge-elicitation-framework
description: Demonstrates end-to-end Knowledge Elicitation pipeline from Natural Language DSQs to PMEST Facets, OntoClean Independent vs Role partitioning, and Common Logic Echoes using the Uruguay Supplement Ontology (USO) agricultural supply chain use case.
domain: ONTOLOGY
surfaces:
  - python
  - prolog
  - datalog
version: 1.0.0
---

# Knowledge Elicitation Framework Skill (USO Use Case)

## Overview

The `knowledge-elicitation-framework` skill demonstrates the 6-stage operational pipeline for eliciting formal, machine-actionable ontologies from messy domain expert natural language transcripts.

## 6-Stage Elicitation Workflow

```
[ Strategic Foundation ] ──> DSQ 1: "What is the specific country of origin and chemical variety for folic acid?"
                                  │
                                  ▼
[ Idea Plane PMEST ]     ──> Personality: [Folic Acid, Rice Plant]
                             Matter: [Molecular Weight, Nitrogen]
                             Energy: [Chemical Synthesis, Manufacturing]
                             Space: [Uruguay, Factory Floor]
                             Time: [2024 Harvest Period]
                                  │
                                  ▼
[ Disambiguation Loop ]  ──> CQ 1: "Does origin refer to raw material harvest location or synthesis factory?"
                                  │
                                  ▼
[ OntoClean Partition ]  ──> Independent Thing: "Folic Acid" (USO_001001)
                             Relative Role: "Regulated Product" (USO_001002) in context of "Uruguayan Regulatory Framework"
                                  │
                                  ▼
[ Common Logic Echo ]    ──> "Is 'Regulated Product' an extrinsic role played by an independent entity within context 'Uruguayan Regulatory Framework'?"
                                  │
                                  ▼
[ Formal Alignment ]     ──> BFO / CCO / IOF Formal OntologyTriples
```

## Elicitation Code Example

```python
from em_cubed.ontology.elicitation import EntityType, KnowledgeElicitationPipeline

pipeline = KnowledgeElicitationPipeline(prefix="USO")

# Stage 1: DSQ
pipeline.add_dsq(
    vague_concern="Sourcing Risk",
    granular_dsq="What is the specific country of origin and chemical variety for the folic acid in this shipment?",
)

# Stage 2: PMEST Analysis
pipeline.analyze_pmest(
    personality=["Folic Acid"],
    matter=["Molecular Weight"],
    energy=["Chemical Synthesis"],
    space=["Uruguay"],
    time=["2024 Harvest"],
)

# Stage 3: CQ
pipeline.derive_cq(
    cq_id="CQ_01",
    question="Does 'origin' refer to raw material harvest location or final chemical synthesis factory?",
    classes=["IngredientOrigin", "SynthesisLocation"],
)

# Stage 4: OntoClean Partition (Opaque IRIs)
p1 = pipeline.partition_entity(
    name="Folic Acid",
    entity_type=EntityType.INDEPENDENT_CONTINUANT,
    definition="A synthetic B vitamin used in food fortification.",
)
p2 = pipeline.partition_entity(
    name="Regulated Product",
    entity_type=EntityType.RELATIVE_ROLE,
    definition="A product subjected to legal oversight.",
    role="Uruguayan Regulatory Framework",
)

# Stage 5: Common Logic Echo
echo = pipeline.generate_echo_dialogue(p2)
print(echo.natural_language_echo)

# Stage 6: Formal Triples
triples = pipeline.extract_formal_triples()
```
