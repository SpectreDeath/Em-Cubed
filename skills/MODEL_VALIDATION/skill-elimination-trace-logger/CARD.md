# Skill Summary Card: `skill-elimination-trace-logger`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        skill-elimination-trace-logger            │
│ Category:    MODEL_VALIDATION / IESDS Observability    │
│ Invocation:  /skill-elimination-trace-logger           │
│ Trigger:     "skill elimination trace logger", "trace  │
│              "iesds elimination trace", "log pruning", │
│              "sqlite session trace", "solver profiling"│
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Recursive-loop trace logger intercepting  │
│              strategy elimination events with causal   │
│              metadata tagging & SQLite persistence.    │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest elimination parameters & classify tag | Trace Event AST | Non-negative indices |
| **2. Table Setup** | Initialize SQLite session & trace tables | SQLite Database Schema | Tables ready |
| **3. Visual Brief** | Render elimination waterfall & mechanism donut | `%TEMP%\elimination-trace-brief-*.html`| Dark theme HTML brief |
| **4. Checkpoint** | Generate unique trace UUID & validate record | Trace Gate Record | UUID generated |
| **5. Model Emission**| Insert trace, query session count & emit payload| `EliminationTraceResult` Payload| Full trace payload emitted |

---

## Invariants & Guardrails

- [ ] **Tag Standardization**: All prunings categorized into valid metadata tags.
- [ ] **Session Coherence**: Trace records linked to session ID.
- [ ] **Trace Idempotence**: Unique trace IDs prevent duplicate insertion collisions.
