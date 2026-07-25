---
name: self-healing-ontological-monitor
description: Demonstrates Phase 12 Production Ontological Health Monitoring, Coherence Index calculation, and automated Self-Healing Guardrail repairs over corrupted knowledge graphs.
domain: ONTOLOGY
surfaces:
  - python
  - prolog
  - z3
  - datalog
version: 1.0.0
---

# Self-Healing Ontological Monitor Skill

## Overview

The `self-healing-ontological-monitor` skill demonstrates **Phase 12 Real-Time Ontological Health Monitoring & Automated Self-Healing Guardrails** in `Em-Cubed`.

## Self-Healing Workflow

```
[ Active Triples ] ──► OntologicalHealthMonitor ──► Coherence Index (0.0 to 1.0) & Health Status
                             │
                             ▼
                  [ Low Coherence Detected ]
                             │
                             ▼
                SelfHealingGuardrailEngine
                             │
                             ▼
         [ Purge Low-Confidence Conflicts & Repair IRIs ]
```

## REST & Sensor Diagnostics Example

```json
{
  "total_triples": 150,
  "coherence_index": 0.94,
  "disjoint_violations": 0,
  "dangling_iris": 1,
  "topos_satisfaction_score": 0.96,
  "health_status": "HEALTHY",
  "self_healing_repaired_count": 2
}
```
