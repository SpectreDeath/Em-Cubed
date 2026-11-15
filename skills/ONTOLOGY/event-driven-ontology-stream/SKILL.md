---
name: event-driven-ontology-stream
domain: ONTOLOGY
version: 1.0.0
surfaces:
  - python
  - prolog
  - datalog
description: Real-time dynamic ontology stream processor and event-driven reactive reasoning engine. Ingests high-throughput telemetry event batches (e.g. IoT sensors, maritime AIS, financial transactions), applies streaming state mutations to active triple ledgers, and triggers Datalog/Prolog reactive rule alerts upon constraint violations. Use when processing streaming event data over ontologies, monitoring temporal state transitions reactively, or firing real-time alerts.
purpose: Ingest continuous event streams, mutate active ontology state, and fire reactive rule alerts in real-time.
dependencies: []
tags:
  - streaming-ontology
  - event-driven
  - reactive-rules
  - real-time-alerts
  - temporal-stream
inputs:
  event_batch:
    type: array
    required: true
    description: List of timestamped event payloads with subjects, actions, and telemetry parameters.
  reactive_rules:
    type: array
    required: false
    description: Datalog/Prolog trigger rules to evaluate on every event ingestion tick.
outputs:
  events_processed:
    type: integer
    description: Total number of ingested and processed stream events.
  active_triples_count:
    type: integer
    description: Current count of live active assertions in the streaming ledger.
  reactive_alerts:
    type: array
    description: List of triggered alert objects with severity levels and rule explanations.
---

# Event-Driven Ontology Stream Engine

`event-driven-ontology-stream` implements **Phase 18 Real-Time Dynamic Ontology Stream Ingestion & Event-Driven Reactive Reasoning** in `Em-Cubed`. It bridges high-throughput telemetry streams (AIS tracks, IoT readings, market events) with deductive semantic reasoning, dynamically mutating live triple states and evaluating reactive Datalog rules in sub-millisecond event loops.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Streaming Progression

```
[1. Stream Ingest & Schema Audit] → [2. Dynamic Triple Mutation] → [3. Visual Brief] → [4. Checkpoint] → [5. Reactive Rule Evaluation]
```

### Stage 1: Stream Ingest & Schema Invariant Audit
1. Ingest batch of event payloads and validate timestamps ($t_i \le t_{now}$).
2. Validate entity identifiers against active domain namespaces.

> **Completion criterion**: Event batch parsed and timestamped in strictly monotonic order.

---

### Stage 2: Dynamic Triple Mutation & Windowing
1. Convert events into transient triple assertions ($E_i \to \text{Triple}(S, P, O, t)$).
2. Expire aged temporal assertions outside the active sliding time window ($t < t_{\text{now}} - W$).

> **Completion criterion**: Sliding window state updated with current event assertions.

---

### Stage 3: The Visual Brief
For critical alert bursts or complex stream flows, generate an interactive brief:
- **Location**: Write to `%TEMP%\ontology-stream-brief-<timestamp>.html` (Windows) or `/tmp/ontology-stream-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render live event ingestion timeline, active sliding window, and triggered alert DAG.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before dispatching automated external actions (e.g. system emergency halts):
1. Verify alert severity level (`CRITICAL` vs `WARNING`).
2. Require human approval on high-consequence reactive counter-measures.

> **Completion criterion**: Reactive actions verified compliant with safety thresholds.

---

### Stage 5: Reactive Rule Evaluation & Alert Emit
1. Evaluate Datalog/Prolog reactive rules over updated sliding window state:
   ```prolog
   alert(critical, Rule, Msg) :- entered_zone(Entity, Zone), restricted_zone(Zone).
   ```
2. Compile and emit triggered alert notifications.

> **Completion criterion**: Event loop terminates with processed counts and emitted reactive alerts.

---

## Surface References

### Python Streaming Processor Surface

```python
from typing import List, Dict, Any

def process_ontology_stream(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    alerts = []
    active_triples = set()
    
    for ev in events:
        entity = ev.get("entity", "Vessel_1")
        action = ev.get("action", "transit")
        zone = ev.get("zone", "Zone_A")
        
        triple = f"{entity} {action} {zone}"
        active_triples.add(triple)
        
        if "restricted" in zone.lower():
            alerts.append({
                "severity": "CRITICAL",
                "rule": "RULE_RESTRICTED_ZONE",
                "message": f"{entity} entered Restricted Territorial Zone {zone}"
            })
            
    return {
        "events_processed": len(events),
        "active_triples_count": len(active_triples),
        "reactive_alerts": alerts
    }
```

---

## Anti-Patterns & Guardrails

- **Unbounded Memory Accumulation** — Ingesting streaming triples without a sliding time window or expiration policy, causing eventual memory exhaustion.
- **Alert Flooding** — Firing duplicate continuous alerts for every tick of a continuous state without event deduplication.
- **Out-of-Order State Corruption** — Applying historical stream events without validating monotonic event timestamps.
