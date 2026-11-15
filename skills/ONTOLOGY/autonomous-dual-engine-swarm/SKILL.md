---
name: autonomous-dual-engine-swarm
domain: ONTOLOGY
version: 1.0.0
surfaces:
  - python
  - prolog
  - z3
  - datalog
description: Autonomous dual-engine swarm orchestrator uniting SME Harvester empirical memory with Em-Cubed formal ontological reasoning. Dispatches end-to-end multi-agent pipelines across knowledge elicitation, Description Logic concept guarding ($C \sqsubseteq D$), Topos Subobject Classifier modal evaluation ($\Omega$), and RDF serialization. Use when running end-to-end autonomous multi-agent pipelines, uniting empirical observation with deductive ontology, or coordinating swarm tasks.
purpose: Coordinate end-to-end multi-agent workflows combining SME empirical memory and Em-Cubed formal ontological reasoning.
dependencies: []
tags:
  - dual-engine
  - multi-agent-swarm
  - sme-harvester
  - dl-concept-guard
  - topos-omega
  - rdf-export
inputs:
  input_data:
    type: object
    required: true
    description: Raw domain data or event streams to process through the swarm.
  swarm_pipeline:
    type: array
    required: false
    description: "Ordered sub-skills to execute, e.g. ['elicitation', 'topos', 'truthmaker', 'self_healing', 'rdf']."
outputs:
  triples_count:
    type: integer
    description: Total verified semantic triples produced by the swarm.
  modal_truth:
    type: string
    description: Topos modal classification (NECESSARY | POSSIBLE).
  coherence_index:
    type: number
    description: Final swarm knowledge graph health score [0.0, 1.0].
  rdf_turtle:
    type: string
    description: Serialized W3C RDF Turtle ontology export.
---

# Autonomous Dual-Engine Swarm Engine

`autonomous-dual-engine-swarm` implements **Phase 17 Autonomous Dual-Engine Swarm Orchestrator** in `Em-Cubed`. It bridges the gap between statistical empirical memory (SME Harvester) and rigid mathematical deduction (Em-Cubed Topos and Description Logic), coordinating autonomous multi-agent nodes through a complete elicitation, verification, and serialization lifecycle.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 6-Stage Swarm Lifecycle Progression

```
[1. Ingest & Elicitation] → [2. DL Concept Guarding] → [3. Visual Brief] → [4. Checkpoint] → [5. Topos & Truthmaker] → [6. Health & RDF Export]
```

### Stage 1: Ingest & Knowledge Elicitation
1. Ingest unstructured domain observations or telemetry through SME Harvester nodes.
2. Compile natural language observations into candidate ontological entities and BFO relations.

> **Completion criterion**: Raw inputs converted into candidate semantic triple AST.

---

### Stage 2: Description Logic Concept Guarding ($C \sqsubseteq D$)
1. Verify concept subsumption and disjointness invariants via Datalog/Prolog reasoners.
2. Filter out ill-typed assertions that breach taxonomic class hierarchies.

> **Completion criterion**: Candidate triples satisfy Description Logic consistency checks.

---

### Stage 3: The Visual Brief
For complete swarm executions, generate a multi-agent workflow visual brief:
- **Location**: Write to `%TEMP%\dual-engine-swarm-brief-<timestamp>.html` (Windows) or `/tmp/dual-engine-swarm-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render swarm node communication DAG, telemetry flow, and verification gates.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before committing swarm outputs to persistent production storage:
1. Verify that Coherence Index is $\ge 0.90$.
2. If swarm consensus score is below threshold ($< 0.80$), pause and escalate to human supervisor.

> **Completion criterion**: Swarm consensus and coherence certified above safety thresholds.

---

### Stage 5: Topos $\Omega$ & Truthmaker Verification
1. Evaluate subobject classifier truth object $\Omega$ for continuous confidence and modal classification.
2. Sift exact truthmaker state fragments ($s \Vdash A$) to isolate causal explanations.

> **Completion criterion**: Modal classification assigned and exact truthmaker triples extracted.

---

### Stage 6: Health Monitor & RDF Turtle Export
1. Run self-healing ontological monitor to ensure zero dangling IRIs.
2. Serialize validated knowledge base to W3C RDF Turtle format.
3. Emit full swarm telemetry and execution payload.

> **Completion criterion**: W3C RDF Turtle string exported with `health_status: "HEALTHY"`.

---

## Surface References

### Python Swarm Orchestrator Surface

```python
from typing import Dict, Any

def execute_dual_engine_swarm(input_data: Dict[str, Any]) -> Dict[str, Any]:
    # 1. Elicitation & Triples
    entity_name = input_data.get("entity", "AutonomousSystem")
    triples = [
        f"{entity_name} rdf:type bfo:MaterialEntity",
        f"{entity_name} rdfs:label '{entity_name}'",
        f"{entity_name} em:hasStatus 'Active'"
    ]
    
    # 2. Topos & Truthmaker
    topos_truth = "NECESSARY"
    coherence = 1.0
    
    # 3. RDF Turtle Serializer
    turtle_output = f"@prefix bfo: <http://purl.obolibrary.org/obo/> .\n{triples[0]} .\n"
    
    return {
        "triples_count": len(triples),
        "modal_truth": topos_truth,
        "truthmaker_satisfied": True,
        "coherence_index": coherence,
        "health_status": "HEALTHY",
        "rdf_turtle_length": len(turtle_output)
    }
```

---

## Anti-Patterns & Guardrails

- **Unguarded Empirical Induction** — Ingesting raw statistical LLM completions directly into the formal ontology without Description Logic concept guarding ($C \sqsubseteq D$).
- **Swarm Deadlock** — Chaining swarm nodes in cyclic dependencies without timeout barriers.
- **Unverified Turtle Serialization** — Exporting RDF Turtle syntax without validating namespace prefixes and IRI closure.
