---
name: skill-elimination-trace-logger
version: 1.0.0
domain: MODEL_VALIDATION
surfaces:
  - python
  - sqlite
description: >
  Recursive-loop interceptor that logs every strategy elimination event
  inside iterated-dominance-solver. Tags each drop as HARD_LOGIC (Z3/Clingo
  pruning) or PROBABILISTIC_DECAY / EARLY_TERMINATION (bounded-rationality
  circuit-breaker). Persists structural lineage to a localized SQLite session
  table for offline profiling.
purpose: >
  Provide granular observability into the IESDS elimination pipeline by
  capturing the exact causal driver for every strategy drop, enabling
  post-hoc bias analysis and solver personality profiling.
dependencies:
  - decision-making/iterated-dominance-solver
  - decision-making/skill-bounded-rationality-constraint
inputs:
  stage_k:
    type: integer
    required: true
    description: "Current iteration count K of the IESDS loop"
  player_id:
    type: integer
    required: true
    description: "Player index whose strategy was eliminated"
  strategy_id:
    type: integer
    required: true
    description: "Strategy index that was dropped at this step"
  pruning_mechanism:
    type: string
    required: true
    description: "Causal driver: z3 | clingo | probabilistic_decay | early_termination"
  session_id:
    type: string
    required: false
    description: "Unique session identifier for trace grouping (default: auto-generated UUID)"
outputs:
  trace_id:
    type: string
    description: "Unique identifier for the logged trace entry"
  logged:
    type: boolean
    description: "True if the trace entry was successfully persisted"
  total_traces_session:
    type: integer
    description: "Total number of trace entries for the current session"
tags:
  - trace-logging
  - elimination-observability
  - iterated-dominance
  - sqlite
  - python
  - diagnostics
  - profiling
---

# Skill Elimination Trace Logger

Recursive-loop interceptor for iterated-dominance-solver. Logs every
strategy elimination event with causal-driver metadata. Persists traces
to SQLite for offline profiling.

## Tick Protocol

| Id | Surface | Action                                                |
|----|---------|-------------------------------------------------------|
| 1  | Python  | Parse `stage_k`, `player_id`, `strategy_id`, `pruning_mechanism` |
| 2  | Python  | Classify pruning mechanism into metadata tag         |
| 3  | SQLite  | Ensure session table exists (idempotent CREATE TABLE IF NOT EXISTS) |
| 4  | SQLite  | INSERT trace row with classified tag and timestamp    |
| 5  | SQLite  | COUNT total traces for current session                |
| 6  | Python  | Return `trace_id`, `logged`, `total_traces_session`  |

Classification rules:
- `z3` or `clingo` → tag = `HARD_LOGIC`
- `probabilistic_decay` → tag = `PROBABILISTIC_DECAY`
- `early_termination` → tag = `EARLY_TERMINATION`

## Surfaces

### Python Surface

```python
surfaces.skill_elimination_trace_logger.log(
    stage_k=2,
    player_id=0,
    strategy_id=1,
    pruning_mechanism="z3",
    session_id="session_abc123"
)
# Result: trace_id="trace_...", logged=True, total_traces_session=3
```

### SQLite Surface

```sql
CREATE TABLE IF NOT EXISTS elimination_trace (
    trace_id        TEXT PRIMARY KEY,
    session_id      TEXT NOT NULL,
    stage_k         INTEGER NOT NULL,
    player_id       INTEGER NOT NULL,
    strategy_id     INTEGER NOT NULL,
    pruning_mechanism TEXT NOT NULL,
    metadata_tag    TEXT NOT NULL,
    timestamp       TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (session_id) REFERENCES elimination_sessions(session_id)
);

CREATE TABLE IF NOT EXISTS elimination_sessions (
    session_id      TEXT PRIMARY KEY,
    game_definition TEXT,
    started_at      TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    completed_at    TEXT,
    total_eliminated INTEGER DEFAULT 0
);

INSERT INTO elimination_trace
    (trace_id, session_id, stage_k, player_id, strategy_id, pruning_mechanism, metadata_tag)
VALUES
    (:trace_id, :session_id, :stage_k, :player_id, :strategy_id, :pruning_mechanism, :metadata_tag);
```

## Capability Contract

**Inputs:**

- `stage_k` *(integer, required)* — Current iteration count of the IESDS loop.
- `player_id` *(integer, required)* — Player index whose strategy was eliminated.
- `strategy_id` *(integer, required)* — Strategy index that was dropped.
- `pruning_mechanism` *(string, required)* — Causal driver: `z3`, `clingo`, `probabilistic_decay`, or `early_termination`.
- `session_id` *(string, optional)* — Unique session identifier for trace grouping. Auto-generated UUID if omitted.

**Outputs:**

- `trace_id` *(string)* — Unique identifier for the logged trace entry.
- `logged` *(boolean)* — True if successfully persisted.
- `total_traces_session` *(integer)* — Total trace entries for the current session.

## Composition

- `iterated-dominance-solver` — Primary instrumentation target; this skill intercepts its loop.
- `skill-bounded-rationality-constraint` — Provides `pruning_mechanism` classification.
- `skill-decision-profile-analyzer` — Primary consumer; queries the trace table.
- `skill-sensor-transducer` — Ingests raw elimination events as normalized observables.
