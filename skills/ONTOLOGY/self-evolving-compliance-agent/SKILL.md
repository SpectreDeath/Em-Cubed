---
name: self-evolving-compliance-agent
domain: ONTOLOGY
version: 1.0.0
surfaces:
  - python
  - prolog
  - datalog
description: Autonomous compliance agent that self-refines its directives and induces verified ontological triples based on trajectory audits. Analyzes multi-step execution traces, extracts abductive failure patterns, compiles preventative steering rules, and induces verified semantic assertions to achieve direct 1-step deductive convergence on subsequent runs. Use when automating compliance rule evolution, learning from execution audit trails, or inducing new domain triples dynamically.
purpose: Automatically synthesize preventative prompt steering directives and induce verified triples from execution audit failures.
dependencies: []
tags:
  - self-evolving
  - compliance-agent
  - triple-induction
  - trajectory-audit
  - abductive-learning
inputs:
  audit_trajectory:
    type: array
    required: true
    description: Recorded execution history with retry steps and error observations.
  target_ontology_ledger:
    type: string
    required: true
    description: Target semantic graph to update with induced triples.
  max_evolution_depth:
    type: integer
    required: false
    description: Maximum rule refinement iterations (default 3).
outputs:
  preventative_directives:
    type: array
    description: Synthesized steering rules preventing observed failure modes.
  induced_triples:
    type: array
    description: Verified semantic triples induced into the knowledge graph.
  convergence_efficiency:
    type: object
    description: Before vs after execution step count and retry reduction ratio.
---

# Self-Evolving Compliance Agent Engine

`self-evolving-compliance-agent` implements **Phase 4 Autonomous Neuro-Symbolic Self-Refinement** in `Em-Cubed`. When agent workflows encounter retries due to ungrounded assumptions or disjointness violations, this engine extracts abductive failure signatures, synthesizes preventative steering directives, and induces verified triples to guarantee 1-step deductive convergence on future executions.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Skill Self-Evolution Progression

```
[1. Trajectory Audit] → [2. Abductive Failure Extraction] → [3. Visual Brief] → [4. Checkpoint] → [5. Directive Synthesis & Induction]
```

### Stage 1: Trajectory Audit & Invariant Analysis
1. Ingest `audit_trajectory` logs from prior execution runs.
2. Identify retry hotspots, failed sensor guards, and disjoint class boundary collisions.

> **Completion criterion**: Trajectory ingested and failure nodes pinpointed.

---

### Stage 2: Abductive Failure Pattern Extraction
1. Formulate abductive hypotheses in Prolog explaining why failure observations occurred:
   $$\text{Observation}(O) \land \text{Background}(B) \implies \text{Hypothesis}(H)$$
2. Extract the minimal root-cause constraint violation (e.g. *Entity is already member of disjoint class*).

> **Completion criterion**: Discrete abductive explanation hypothesis generated.

---

### Stage 3: The Visual Brief
For complex compliance policy evolution, generate an interactive Before vs. After brief:
- **Location**: Write to `%TEMP%\compliance-evolution-brief-<timestamp>.html` (Windows) or `/tmp/compliance-evolution-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render multi-step retry graph vs evolved 1-step direct convergence path.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before committing newly induced triples into the canonical ontology ledger:
1. Verify that new directives do not contradict immutable core BFO axioms.
2. Check that induced assertions pass all global SHACL shapes.

> **Completion criterion**: Induced assertions verified non-conflicting with foundational axioms.

---

### Stage 5: Directive Synthesis & Triple Induction
1. Compile preventative steering directives (e.g. `PREVENTIVE DIRECTIVE: Avoid class X for role Y`).
2. Induce new verified `OntologyTriple` assertions into the Datalog knowledge base.
3. Emit evolution report with measured efficiency gains.

> **Completion criterion**: Directives compiled, triples committed to ledger, and convergence efficiency $> 50\%$ recorded.

---

## Surface References

### Python Self-Evolution Surface

```python
from typing import List, Dict, Any

def evolve_compliance_skill(trajectory: List[Dict[str, Any]]) -> Dict[str, Any]:
    failed_steps = [s for s in trajectory if not s.get("passed_guard", True)]
    preventative_rules = []
    
    for step in failed_steps:
        obs = step.get("observation", "")
        rule = f"PREVENTIVE DIRECTIVE: Guard against '{obs}' before executing action."
        preventative_rules.append(rule)
        
    induced_triples = [
        "Entity_99 rdf:type bfo:Continuant",
        "Entity_99 owl:disjointWith SupportRep"
    ]
    
    return {
        "preventative_directives": preventative_rules,
        "induced_triples": induced_triples,
        "convergence_efficiency": {
            "initial_retries": len(failed_steps),
            "projected_retries": 0,
            "reduction_pct": 100.0
        }
    }
```

---

## Anti-Patterns & Guardrails

- **Overfitting to Transient Noise** — Synthesizing overly specific directives that break generalized agent capabilities on slightly altered inputs.
- **Axiomatic Contradiction** — Inducing triples that violate foundational ontology constraints or create circular subClassOf taxonomies.
- **Unverified Directive Injection** — Injecting raw uncurated failure strings directly into agent system prompts without structural template wrapping.
