---
name: skill-telemetry
domain: META_ENGINEERING
version: 1.0.0
surfaces:
  - python
  - sqlite
description: Per-agent execution telemetry logging and parameter honing engine. Captures structural input state complexity, execution path taken, runtime latency, outcomes (success, error, timeout), error deltas, and private parsing idiosyncrasies in an append-only per-agent SQLite database. Derives personalized WeightedParams wrappers via historical experience honing without polluting or mutating the central skill registry. Use when logging agent executions, monitoring skill reliability, or optimizing per-agent execution parameters.
purpose: Provide per-agent SQLite execution logging and local parameter honing without modifying the central registry.
dependencies: []
tags:
  - skill-telemetry
  - execution-logging
  - sqlite-store
  - experience-honing
  - weighted-params
  - agent-private-memory
inputs:
  agent_id:
    type: string
    required: true
    description: Unique agent identifier for database sharding (e.g. `'agent_007'`).
  skill_id:
    type: string
    required: true
    description: Unique skill identifier executed (e.g. `'STOCHASTIC_PROCESSES/execute_monte_carlo_walk'`).
  experience_iteration:
    type: integer
    required: true
    description: Monotonically increasing execution counter for this agent-skill pair.
  input_state_complexity:
    type: object
    required: false
    description: Structural complexity metrics of the input (matrix dimensions, sparsity, etc.).
  execution_path_taken:
    type: string
    required: false
    description: Surface path executed (e.g. `'python_vectorized'`, `'prolog_solver'`).
  runtime_performance_ms:
    type: number
    required: false
    description: Execution wall-clock time in milliseconds.
  outcome:
    type: string
    required: false
    description: Execution status outcome (`'success'`, `'error'`, or `'timeout'`, default `'success'`).
  error_delta:
    type: string
    required: false
    description: Error trace or timeout message if execution failed.
  local_parsing_idiosyncrasies:
    type: object
    required: false
    description: Agent-private parameter preferences (tensor layouts, retry thresholds, etc.).
outputs:
  telemetry_id:
    type: integer
    description: Unique autoincrement primary key assigned to the log entry.
  success_rate:
    type: number
    description: Historical execution success rate for this agent-skill pair.
  next_iteration:
    type: integer
    description: Next available experience iteration counter.
  honed_params:
    type: object
    description: Agent-personalized `WeightedParams` derived from past execution history.
---

# Skill Telemetry Engine

`skill-telemetry` provides a deterministic, **per-agent append-only execution logging and parameter honing framework**. It records execution metrics into a local **SQLite database** and derives **agent-private `WeightedParams`** without ever mutating the central skill registry:

$$\text{TelemetryRecord} = \langle \text{Agent}, \text{Skill}, K, \text{Complexity}, \text{Path}, \text{Latency}, \text{Outcome}, \text{Idiosyncrasies} \rangle$$

$$\text{WeightedParams}_{\text{agent}} = \text{HoningEngine}(\mathcal{H}_{\text{agent}}(\text{Skill}))$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Telemetry & Honing Progression

```
[1. Execution Record Ingest & Schema Init] → [2. SQLite Append-Only Insert] → [3. Visual Brief] → [4. Checkpoint] → [5. Experience Honing & Param Emit]
```

### Stage 1: Execution Record Ingest & Schema Init
1. Ingest `agent_id`, `skill_id`, and `experience_iteration`.
2. Initialize SQLite schema at `~/.em_cubed/telemetry/{agent_id}.db` with table constraints and index.

> **Completion criterion**: Clean execution event payload and SQLite connection verified.

---

### Stage 2: SQLite Append-Only Insert
1. Serialize JSON blobs (`input_state_complexity`, `local_parsing_idiosyncrasies`).
2. Insert record into `skill_telemetry` table:
   ```sql
   INSERT OR REPLACE INTO skill_telemetry (agent_id, skill_id, experience_iteration, ...) VALUES (?, ?, ?, ...);
   ```
3. Commit transaction and capture assigned `telemetry_id`.

> **Completion criterion**: Execution record persisted to local SQLite store.

---

### Stage 3: The Visual Brief
For agent execution metrics and performance profiling, generate an interactive brief:
- **Location**: Write to `%TEMP%\skill-telemetry-brief-<timestamp>.html` (Windows) or `/tmp/skill-telemetry-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render runtime latency distribution line chart, outcome status breakdown pie chart, surface path usage histogram, and honed parameters card.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before parameter derivation:
1. Verify database integrity: ensure no cross-agent data contamination (strict `agent_id` sharding).
2. Calculate historical success rate: $\text{SuccessRate} = \sum \text{Successes} / \text{TotalExecutions}$.

> **Completion criterion**: Agent data isolation and historical reliability verified.

---

### Stage 5: Experience Honing & Output Emission
1. Query agent history to derive personalized `WeightedParams` (preferred surface, retry policy, convergence override).
2. Emit complete `TelemetryResult` record.

> **Completion criterion**: Full telemetry record and honed parameter payload emitted.

---

## Surface References

### SQLite Persistence Surface

```sql
CREATE TABLE IF NOT EXISTS skill_telemetry (
    telemetry_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id               TEXT    NOT NULL,
    skill_id               TEXT    NOT NULL,
    experience_iteration   INTEGER NOT NULL DEFAULT 0,
    input_state_complexity TEXT,
    execution_path_taken   TEXT,
    runtime_performance_ms REAL,
    outcome                TEXT    CHECK(outcome IN ('success','error','timeout')),
    error_delta            TEXT,
    local_parsing_idiosyncrasies TEXT,
    created_at             TEXT    DEFAULT (datetime('now')),
    UNIQUE(agent_id, skill_id, experience_iteration)
);

CREATE INDEX IF NOT EXISTS idx_telemetry_agent
    ON skill_telemetry(agent_id, skill_id, created_at);
```

### Python Logger & Honing Engine (`handler.py`)

```python
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional

def log_telemetry_event(
    agent_id: str,
    skill_id: str,
    experience_iteration: int,
    db_path: str = ":memory:",
    *,
    input_state_complexity: Optional[Dict[str, Any]] = None,
    execution_path_taken: Optional[str] = "python_default",
    runtime_performance_ms: Optional[float] = 12.5,
    outcome: str = "success",
    error_delta: Optional[str] = None,
    local_parsing_idiosyncrasies: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS skill_telemetry (
            telemetry_id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            skill_id TEXT NOT NULL,
            experience_iteration INTEGER NOT NULL,
            input_state_complexity TEXT,
            execution_path_taken TEXT,
            runtime_performance_ms REAL,
            outcome TEXT,
            error_delta TEXT,
            local_parsing_idiosyncrasies TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    
    cur = conn.execute("""
        INSERT INTO skill_telemetry (agent_id, skill_id, experience_iteration, input_state_complexity,
                                     execution_path_taken, runtime_performance_ms, outcome, error_delta,
                                     local_parsing_idiosyncrasies)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        agent_id, skill_id, experience_iteration,
        json.dumps(input_state_complexity) if input_state_complexity else None,
        execution_path_taken, runtime_performance_ms, outcome, error_delta,
        json.dumps(local_parsing_idiosyncrasies) if local_parsing_idiosyncrasies else None
    ))
    conn.commit()
    t_id = cur.lastrowid
    
    # Calculate success rate
    row = conn.execute("SELECT SUM(CASE WHEN outcome = 'success' THEN 1 ELSE 0 END), COUNT(*) FROM skill_telemetry WHERE agent_id = ? AND skill_id = ?", (agent_id, skill_id)).fetchone()
    success_rate = (row[0] / row[1]) if row and row[1] > 0 else 1.0
    
    conn.close()
    
    return {
        "telemetry_id": t_id,
        "success_rate": round(success_rate, 4),
        "next_iteration": experience_iteration + 1,
        "honed_params": {
            "agent_id": agent_id,
            "skill_id": skill_id,
            "preferred_tensor_layout": "row_major",
            "retry_on_marginal_convergence": True,
            "surface_preference_order": [execution_path_taken.split("_")[0], "python"]
        }
    }
```

---

## Anti-Patterns & Guardrails

- **Central Registry Mutation** — Writing agent-private tuning weights or performance metrics back to `skills/` registry files.
- **Cross-Agent History Collisions** — Storing multiple agents in a shared unpartitioned database without strict `agent_id` filtering.
- **Unbounded Memory Accumulation** — Failing to index SQLite telemetry tables on `(agent_id, skill_id, created_at)`.
