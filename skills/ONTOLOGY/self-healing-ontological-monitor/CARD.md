# Skill Summary Card: `self-healing-ontological-monitor`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        self-healing-ontological-monitor          │
│ Category:    ONTOLOGY / Health Monitoring & Repair     │
│ Invocation:  /self-healing-ontological-monitor         │
│ Trigger:     "monitor ontology health",                │
│              "compute coherence index", "self healing",│
│              "repair dangling iris", "graph audit"     │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Real-time Coherence Index calculation,    │
│              violation diagnosis, and automated        │
│              self-healing repair passes.               │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Invariant Audit** | Ingest triples and verify RDF triple syntax | Triple Inventory AST | Syntax validated and entities indexed |
| **2. Coherence Scoring**| Calculate disjoint, dangling & Topos metrics | Coherence Index [0, 1] | Health score computed with status |
| **3. Visual Brief** | Render health dashboard and damaged subgraph | `%TEMP%\ontology-health-brief-*.html` | Dark theme HTML gauge and graph |
| **4. Checkpoint** | Gate destructive auto-purging operations | Destruction Safety Check | High-confidence assertion protection verified |
| **5. Self-Healing** | Purge low-confidence conflicts & stitch IRIs | Repaired Triple Store | Post-repair Coherence Index $\ge 0.90$ |

---

## Invariants & Guardrails

- [ ] **Coherence Threshold**: Automatically alert and heal if Coherence Index drops below $0.85$.
- [ ] **Conservative Destruction**: Never purge $> 10\%$ of knowledge base triples without explicit checkpoint approval.
- [ ] **BFO Typing Invariant**: All stitched dangling IRIs must be typed under `bfo:Continuant` or `bfo:Occurrent`.
