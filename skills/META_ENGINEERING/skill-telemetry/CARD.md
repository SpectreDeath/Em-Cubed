# Skill Summary Card: `skill-telemetry`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        skill-telemetry                           │
│ Category:    META_ENGINEERING / Execution Telemetry    │
│ Invocation:  /skill-telemetry                          │
│ Trigger:     "skill telemetry", "log execution",       │
│              "experience honing", "weighted params",   │
│              "agent private memory", "runtime metrics" │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Per-agent append-only SQLite telemetry    │
│              logging & private parameter honing        │
│              without central registry pollution.       │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest execution metrics & initialize SQLite schema | Telemetry Event AST | Valid `agent_id` verified |
| **2. Persistence** | Append record to `skill_telemetry` table in SQLite | Database Row Record | Transaction committed |
| **3. Visual Brief** | Render latency charts & surface usage breakdown | `%TEMP%\skill-telemetry-brief-*.html`| Dark theme HTML brief |
| **4. Checkpoint** | Validate agent isolation & calculate success rate | Reliability Gate Record| Agent sharding verified |
| **5. Model Emission**| Derive `WeightedParams` from history & emit payload| `TelemetryResult` Payload | Full telemetry payload emitted |

---

## Invariants & Guardrails

- [ ] **Registry Isolation Invariant**: Never write agent experience data to `skills/` registry.
- [ ] **Agent Sharding**: All database queries strictly filtered by `agent_id`.
- [ ] **Monotonic Iterations**: `experience_iteration` increments monotonically per skill.
