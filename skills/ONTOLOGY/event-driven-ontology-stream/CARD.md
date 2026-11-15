# Skill Summary Card: `event-driven-ontology-stream`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        event-driven-ontology-stream              │
│ Category:    ONTOLOGY / Streaming Telemetry & Alerts   │
│ Invocation:  /event-driven-ontology-stream             │
│ Trigger:     "ingest ontology stream", "event stream", │
│              "reactive rule alert", "streaming triples"│
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Real-time telemetry event stream          │
│              ingestion, sliding window state mutation, │
│              and reactive Datalog rule alerts.         │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Stream Ingest** | Ingest and validate event timestamps | Stream Event Batch | Monotonic event timestamps verified |
| **2. Dynamic Mutation**| Mutate triples within sliding time window | Windowed State AST | Transient state updated & expired nodes purged |
| **3. Visual Brief** | Render ingestion timeline and alert DAG | `%TEMP%\ontology-stream-brief-*.html`| Dark theme HTML streaming brief |
| **4. Checkpoint** | Validate alert severity and safety gates | Safety Gate Record | Gated verification on critical halts |
| **5. Rule Evaluation** | Evaluate Datalog triggers and emit alerts | Emitted Alerts Payload | All active reactive rules evaluated |

---

## Invariants & Guardrails

- [ ] **Sliding Window Boundary**: Aged triples ($t < t_{\text{now}} - W$) automatically pruned.
- [ ] **Alert Deduplication**: Duplicate alerts suppressed within throttle windows.
- [ ] **Temporal Monotonicity**: Out-of-order event timestamps handled with explicit re-sequencing.
