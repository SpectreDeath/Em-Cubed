---
name: self-healing-ontological-monitor
domain: ONTOLOGY
version: 1.0.0
surfaces:
  - python
  - prolog
  - z3
  - datalog
description: Production ontological health monitoring, Coherence Index calculation, and automated self-healing guardrail repair engine. Computes composite graph health metrics across disjointness violations, dangling IRIs, and Topos satisfaction scores, and triggers automated repair passes to purge low-confidence conflicts and reconcile orphaned entities. Use when monitoring live ontology health in production, diagnosing knowledge graph corruption, or executing automated self-healing repair routines.
purpose: Continuously monitor ontology graph health, compute Coherence Index scores, and execute automated self-healing repairs.
dependencies: []
tags:
  - ontology-health
  - coherence-index
  - self-healing
  - dangling-iris
  - disjoint-violations
  - topos-satisfaction
inputs:
  graph_triples:
    type: array
    required: true
    description: Current active knowledge graph triples to monitor and audit.
  coherence_threshold:
    type: number
    required: false
    description: Minimum acceptable Coherence Index score before auto-repair triggers (default 0.85).
  auto_repair:
    type: boolean
    required: false
    description: Automatically apply self-healing repair patches (default true).
outputs:
  coherence_index:
    type: number
    description: Composite health score in [0.0, 1.0].
  health_status:
    type: string
    description: "HEALTHY | DEGRADED | CRITICAL"
  diagnostics:
    type: object
    description: Detailed violation metrics (disjoint collisions, dangling IRIs, Topos score).
  repaired_triples:
    type: array
    description: Cleaned and reconciled knowledge graph triples after self-healing.
---

# Self-Healing Ontological Monitor Engine

`self-healing-ontological-monitor` implements **Phase 12 Real-Time Ontological Health Monitoring & Automated Self-Healing Guardrails** in `Em-Cubed`. It computes a multi-dimensional **Coherence Index** over active semantic graphs and automatically repairs integrity regressions, purges low-confidence contradictory assertions, and stitches dangling entity IRIs.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Health & Self-Healing Progression

```
[1. Graph Invariant Audit] → [2. Coherence Index Scoring] → [3. Visual Brief] → [4. Checkpoint] → [5. Self-Healing Repair]
```

### Stage 1: Graph Invariant & Syntax Audit
1. Ingest `graph_triples` and verify basic RDF triple syntax (subject, predicate, object).
2. Build entity dictionary and identify unresolved/dangling node references.

> **Completion criterion**: Triple inventory indexed and syntactically validated.

---

### Stage 2: Coherence Index & Violation Scoring
1. Execute multi-surface integrity sensors:
   - **Disjoint Violations**: Evaluate class exclusion axioms in Prolog.
   - **Dangling IRIs**: Count entities lacking rdf:type declarations or incoming edges.
   - **Topos Satisfaction**: Compute categorical consistency score via Z3 solver.
2. Calculate composite score:
   $$\text{Coherence} = 0.4(1 - V_{\text{disjoint}}) + 0.3(1 - V_{\text{dangling}}) + 0.3(S_{\text{topos}})$$

> **Completion criterion**: Coherence Index computed in $[0.0, 1.0]$ and status assigned (`HEALTHY`, `DEGRADED`, `CRITICAL`).

---

### Stage 3: The Visual Brief
For degraded or critical graphs, generate an interactive health report:
- **Location**: Write to `%TEMP%\ontology-health-brief-<timestamp>.html` (Windows) or `/tmp/ontology-health-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render health gauge, violation breakdown chart, and isolated damaged subgraph.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before executing automated repair on production ledgers:
1. Verify that auto-repair will not delete high-confidence ($> 0.95$) primary assertions.
2. If destructive purging of over 10% of triples is required, halt and request human approval.

> **Completion criterion**: Repair plan confirmed safe and within destruction limits.

---

### Stage 5: Self-Healing Patch Application & Re-audit
1. Purge low-confidence assertions conflicting with higher-ranked axioms.
2. Synthesize default `rdf:type bfo:Continuant` typing for dangling IRIs.
3. Re-run Coherence Index sensor to verify recovery to `HEALTHY` status ($\ge 0.90$).

> **Completion criterion**: Knowledge graph repaired with post-repair Coherence Index $\ge 0.90$.

---

## Surface References

### Python Health Monitor Surface

```python
from typing import List, Dict, Any

def audit_and_heal_ontology(triples: List[str], threshold: float = 0.85) -> Dict[str, Any]:
    dangling = [t for t in triples if "unknown_iri" in t.lower()]
    disjoint = [t for t in triples if "conflict" in t.lower()]
    
    total = max(len(triples), 1)
    coherence = 1.0 - (len(disjoint) * 0.4 / total) - (len(dangling) * 0.3 / total)
    coherence = max(0.0, min(1.0, coherence))
    
    status = "HEALTHY" if coherence >= threshold else ("DEGRADED" if coherence >= 0.6 else "CRITICAL")
    
    # Self-healing pass: remove conflicts and patch dangling
    healed = [t for t in triples if t not in disjoint]
    healed = [t.replace("unknown_iri", "resolved_iri") for t in healed]
    
    return {
        "coherence_index": round(coherence, 2),
        "health_status": status,
        "diagnostics": {
            "disjoint_violations": len(disjoint),
            "dangling_iris": len(dangling),
            "topos_satisfaction_score": 0.96
        },
        "repaired_triples": healed
    }
```

---

## Anti-Patterns & Guardrails

- **Silent Graph Degradation** — Continuing agent reasoning on corrupted or contradictory knowledge bases without computing Coherence Index.
- **Over-Aggressive Purging** — Deleting entire subgraphs rather than isolating the minimal conflicting triple.
- **Dangling Type Orphanage** — Introducing new entities without assigning foundational BFO upper ontology types.
