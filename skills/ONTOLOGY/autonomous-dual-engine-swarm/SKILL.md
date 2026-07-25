---
name: autonomous-dual-engine-swarm
description: Demonstrates Phase 17 Autonomous Dual-Engine Swarm Orchestrator, executing full-lifecycle multi-agent workflows combining SME Harvester empirical memory with Em-Cubed formal ontology.
domain: ONTOLOGY
surfaces:
  - python
  - prolog
  - z3
  - datalog
version: 1.0.0
---

# Autonomous Dual-Engine Swarm Skill

## Overview

The `autonomous-dual-engine-swarm` skill demonstrates **Phase 17 Autonomous Dual-Engine Swarm Orchestrator** in `Em-Cubed`.

## Full Swarm Lifecycle

```
[ Ingest Raw Data ] ──► KnowledgeElicitation ──► DL Concept Guard (C ⊑ D)
                                                        │
                                                        ▼
[ RDF Turtle Export ] ◄── Health & Self-Healing ◄── Topos Ω & Truthmaker (s ⊩ A)
```

## Execution Outcome Example

```json
{
  "triples_count": 3,
  "modal_truth": "POSSIBLE",
  "truthmaker_satisfied": true,
  "coherence_index": 1.0,
  "health_status": "HEALTHY",
  "rdf_turtle_length": 340
}
```
