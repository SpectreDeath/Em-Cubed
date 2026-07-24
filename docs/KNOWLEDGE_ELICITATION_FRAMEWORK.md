# Knowledge Elicitation Framework: From Natural Language to Formal Ontology (`em-cubed`)

## Overview

The **Knowledge Elicitation Framework** in `Em-Cubed` (`em_cubed.ontology.elicitation`) provides an end-to-end operational pipeline for bridging executive natural language and domain expert interviews into machine-actionable, BFO/OntoClean-aligned formal ontologies.

---

## The 6-Stage Operational Pipeline

### 1. Strategic Foundation: Scoping & Value Alignment
Ontological development is grounded in decision support and Net Present Value (NPV) risk mitigation. High-level concerns are converted into **Decision Support Questions (DSQs)**.

- **Vague Concern**: *"Sourcing Risk"*
- **Granular DSQ**: *"What is the specific country of origin and chemical variety for the folic acid in this shipment?"*

### 2. The Idea Plane: Faceted Analysis & Conceptualization
Treats domain knowledge as an adaptive, biological growth model using Ranganathan's **PMEST Framework**:
- **[P]ersonality**: Core identity (e.g. Folic Acid, Rice Plant).
- **[M]atter**: Material substances and intrinsic properties (e.g. Molecular Weight, Nitrogen).
- **[E]nergy**: Actions, processes, and operations (e.g. Chemical Synthesis, Harvesting).
- **[S]pace**: Geographical and spatial dimensions (e.g. Uruguay, Factory Floor).
- **[T]ime**: Temporal periods (e.g. 2024 Harvest Season).

### 3. Disambiguation: The DSQ-to-CQ Iterative Loop
Translates DSQs into pedantic **Competency Questions (CQs)** to expose gaps and ambiguities prior to modeling.
- **CQ Example**: *"Does 'origin' refer to the location of raw material harvest or the location of final chemical synthesis?"*

### 4. Structural Integrity: OntoClean & BFO Partitioning
Prevents "cheating" and logical debt by strictly partitioning concepts into:
- **Independent Things** (`INDEPENDENT_CONTINUANT`): Defined strictly by intrinsic physical structure (e.g. `Folic Acid`).
- **Relative Things / Roles** (`RELATIVE_ROLE`): Extrinsic status assigned by context (e.g. `Regulated Product` in the context of `Uruguayan Regulatory Framework`).
- **Opaque IRIs**: Mandates machine IRIs (e.g. `USO_001001`) to decouple internal logic from natural language label shifts.

### 5. Common Logic Echo Dialogue
Utilizes Common Logic (ISO/IEC 24707) as a human-computer confirmation dialogue:
- **Echo String**: *"Is 'Regulated Product' an extrinsic role played by an independent entity within context 'Uruguayan Regulatory Framework'?"*

### 6. Formalization & Alignment (BFO / CCO / IOF)
Extracts formal `OntologyTriple` assertions mapped to Basic Formal Ontology (`bfo:IndependentContinuant`, `bfo:Role`), Common Core Ontologies (`cco`), and Industrial Ontologies Foundry (`iof`).

---

## Python API Usage

```python
from em_cubed.ontology.elicitation import EntityType, KnowledgeElicitationPipeline

pipeline = KnowledgeElicitationPipeline(prefix="USO")

# Add DSQ
pipeline.add_dsq(
    vague_concern="Sourcing Risk",
    granular_dsq="What is the specific country of origin and chemical variety for folic acid?",
)

# Analyze PMEST Facets
pipeline.analyze_pmest(
    personality=["Folic Acid"],
    matter=["Molecular Weight"],
    energy=["Chemical Synthesis"],
    space=["Uruguay"],
    time=["2024 Harvest"],
)

# Partition Entity
partition = pipeline.partition_entity(
    name="Regulated Product",
    entity_type=EntityType.RELATIVE_ROLE,
    definition="A product subjected to legal oversight.",
    role="Uruguayan Regulatory Framework",
)

# Extract Formal Triples
triples = pipeline.extract_formal_triples()
```
