---
name: looped-state-compressor
domain: WORLD_MODELS
version: 1.0.0
surfaces:
- python
- sqlite
description: 'Multi-surface looped state compressor that recursively compresses execution history into dense relational state
  files. Python intercepts raw terminal traces, extracts discrete entities and state deltas, and writes to SQLite. Agent queries
  history via structured SQL.

  '
purpose: 'Prevent context bloat in long-running agent loops by compressing execution history into queryable relational state
  instead of appending to prompt context.

  '
dependencies:
- durable-execution-engine
tags:
- world-model
- state-compression
- sqlite
- context-management
- looped-transformer
- entity-extraction
inputs:
  session_id:
    type: string
    required: true
    description: Unique session identifier
  raw_trace:
    type: array
    required: true
    description: Raw execution trace entries
  compression_mode:
    type: string
    required: false
    description: delta or full (delta by default)
  max_history:
    type: integer
    required: false
    description: Max steps to retain (1000 by default)
outputs:
  compressed_state:
    type: object
    description: Latest compressed state snapshot
  entity_count:
    type: integer
    description: Number of distinct entities tracked
  delta_summary:
    type: object
    description: Aggregate state changes since last compression
  db_path:
    type: string
    description: Path to the SQLite state database
---

# Looped State Compressor

Recursively compresses execution history into dense, relational state files.
Python intercepts traces; SQLite persists entities and deltas.

## Tick Protocol

| Id | Surface  | Action                                                   |
|----|----------|----------------------------------------------------------|
| 1  | Python   | Receive raw execution trace entries                      |
| 2  | Python   | Extract discrete entities and state deltas from each step|
| 3  | SQLite   | INSERT entities into `entities` table with `session_id`  |
| 4  | SQLite   | INSERT state deltas into `state_deltas` table            |
| 5  | SQLite   | UPDATE compressed snapshot via trigger or OR REPLACE     |
| 6  | Python   | Return compressed state and delta summary                |

## Surfaces

### Python Surface

Intercepts raw terminal traces from the agent runtime.

```python
surfaces.looped_state_compressor.compress_trace(
    session_id="abc-123",
    raw_trace=[{"step": i, "surface": "...", "input": "...", "output": "..."}],
    compression_mode="delta"
)
```

### SQLite Surface

Persists compressed state for structured querying.

```sql
CREATE TABLE IF NOT EXISTS entities (
    entity_id TEXT,
    session_id TEXT,
    entity_type TEXT,
    entity_data JSON,
    first_seen INTEGER,
    last_updated INTEGER,
    PRIMARY KEY (entity_id, session_id)
);

CREATE TABLE IF NOT EXISTS state_deltas (
    delta_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    step INTEGER NOT NULL,
    entity_id TEXT,
    delta_type TEXT,            -- create | update | delete
    delta_data JSON,
    timestamp INTEGER
);

CREATE TABLE IF NOT EXISTS compressed_snapshots (
    session_id TEXT PRIMARY KEY,
    snapshot JSON,
    entity_count INTEGER,
    step_count INTEGER,
    last_compressed INTEGER
);
```

## State Extraction Heuristics

Python surface extracts entities from trace entries:

| Trace Pattern                  | Entity Type          | Delta Type |
|--------------------------------|----------------------|------------|
| New variable assignment        | `variable`           | create     |
| Tool call with named response  | `tool_result`        | create     |
| State mutation (e.g. +=)       | `state_mutation`     | update     |
| Session end signal             | `session_marker`     | update     |

## Capability Contract

**Inputs:**

- `session_id` *(string, required)* — Unique session identifier.
- `raw_trace` *(array, required)* — Raw execution trace entries from the agent.
- `compression_mode` *(string, optional)* — `delta` (only changes) or `full` (every step). Default `delta`.
- `max_history` *(integer, optional)* — Maximum steps to retain. Default `1000`.

**Outputs:**

- `compressed_state` *(object)* — Latest compressed state snapshot.
- `entity_count` *(integer)* — Number of distinct entities tracked.
- `delta_summary` *(object)* — Aggregate state changes since last compression.
- `db_path` *(string)* — Path to the SQLite state database.

## Composition

- `durable-execution-engine` — Checkpoint compressed state across sessions.
- `observability-dashboard` — Track context bloat metrics and compression ratios.
- `dag-task-scheduler` — Schedule periodic compression ticks for long-running workflows.
