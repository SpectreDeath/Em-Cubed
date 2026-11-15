---
name: skill-elimination-trace-logger
domain: MODEL_VALIDATION
version: 1.0.0
surfaces:
  - python
  - sqlite
description: Recursive-loop trace logging and observability interceptor for game-theoretic solvers (iterated-dominance-solver). Intercepts every strategy elimination event, classifies the causal pruning mechanism into standardized metadata tags (HARD_LOGIC for Z3 SMT/Clingo strict dominance, PROBABILISTIC_DECAY for continuous belief redistribution, or EARLY_TERMINATION for Simon bounded-rationality circuit breakers), and persists structured trace lineages into local SQLite session tables for offline solver personality profiling. Use when auditing IESDS elimination pipelines or profiling decision bias.
purpose: Intercept, classify, and persist game-theoretic strategy elimination traces into SQLite session tables.
dependencies:
  - DECISION_MAKING/iterated-dominance-solver
  - DECISION_MAKING/skill-bounded-rationality-constraint
tags:
  - skill-elimination-trace-logger
  - iesds-observability
  - strategy-pruning
  - sqlite-session-trace
  - causal-tagging
  - solver-profiling
inputs:
  stage_k:
    type: integer
    required: true
    description: Current iteration count $K$ of the iterated elimination loop.
  player_id:
    type: integer
    required: true
    description: Player index whose strategy was dropped ($0 \le p_i < N$).
  strategy_id:
    type: integer
    required: true
    description: Strategy index that was eliminated at this step.
  pruning_mechanism:
    type: string
    required: true
    description: Causal elimination driver (`'z3'`, `'clingo'`, `'probabilistic_decay'`, or `'early_termination'`).
  session_id:
    type: string
    required: false
    description: Unique session UUID for trace grouping (auto-generated if omitted).
outputs:
  trace_id:
    type: string
    description: Unique identifier assigned to the logged elimination trace event.
  logged:
    type: boolean
    description: True if trace record was successfully committed to SQLite.
  metadata_tag:
    type: string
    description: Classified category tag (`'HARD_LOGIC'`, `'PROBABILISTIC_DECAY'`, or `'EARLY_TERMINATION'`).
  total_traces_session:
    type: integer
    description: Cumulative count of elimination traces recorded for this session.
---

# Skill Elimination Trace Logger Engine

`skill-elimination-trace-logger` provides observability into game-theoretic reasoning pipelines. It intercepts strategy drops in `iterated-dominance-solver`, **classifies causal pruning mechanisms in Python**, and **persists elimination lineages to SQLite**:

$$\text{Pruning Mechanism} \xrightarrow{\text{Classify}} \text{Metadata Tag} \in \{\text{HARD\_LOGIC}, \text{PROBABILISTIC\_DECAY}, \text{EARLY\_TERMINATION}\}$$

$$\text{Trace Record: } \langle \text{TraceID}, \text{SessionID}, K, p_i, s_j, \text{Mechanism}, \text{Tag}, t_{\text{now}} \rangle \to \text{SQLite}(\texttt{elimination\_trace})$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Trace Logging Progression

```
[1. Elimination Event Ingest & Tag Classification] → [2. SQLite Session Table Setup] → [3. Visual Brief] → [4. Checkpoint] → [5. Trace Insertion & Session Count Emit]
```

### Stage 1: Elimination Event Ingest & Tag Classification
1. Ingest `stage_k`, `player_id`, `strategy_id`, and `pruning_mechanism`.
2. Classify mechanism into standard metadata tag:
   - `'z3'` or `'clingo'` $\to$ `HARD_LOGIC`
   - `'probabilistic_decay'` $\to$ `PROBABILISTIC_DECAY`
   - `'early_termination'` $\to$ `EARLY_TERMINATION`

> **Completion criterion**: Valid elimination parameters and metadata tag assigned.

---

### Stage 2: SQLite Session Table Setup
1. Open connection to SQLite database (`:memory:` or localized file).
2. Ensure idempotent presence of `elimination_sessions` and `elimination_trace` tables.

> **Completion criterion**: SQLite tables and foreign key constraints initialized.

---

### Stage 3: The Visual Brief
For solver elimination dynamics and iteration waterfalls, generate an interactive brief:
- **Location**: Write to `%TEMP%\elimination-trace-brief-<timestamp>.html` (Windows) or `/tmp/elimination-trace-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render elimination sequence waterfall timeline, pruning mechanism distribution donut chart, and active session trace table.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before trace commit:
1. Verify non-negative indices ($K \ge 0, p_i \ge 0, s_j \ge 0$).
2. Assign unique trace UUID: `trace_<uuid>`.

> **Completion criterion**: Valid trace record structure verified.

---

### Stage 5: Trace Insertion & Output Emission
1. Insert record into `elimination_trace` table.
2. Query total trace count for active `session_id`.
3. Emit complete `EliminationTraceResult` record.

> **Completion criterion**: Full elimination trace payload emitted with total count.

---

## Surface References

### SQLite Trace Storage Surface

```sql
CREATE TABLE IF NOT EXISTS elimination_sessions (
    session_id       TEXT PRIMARY KEY,
    game_definition  TEXT,
    started_at       TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    completed_at     TEXT,
    total_eliminated INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS elimination_trace (
    trace_id          TEXT PRIMARY KEY,
    session_id        TEXT NOT NULL,
    stage_k           INTEGER NOT NULL,
    player_id         INTEGER NOT NULL,
    strategy_id       INTEGER NOT NULL,
    pruning_mechanism TEXT NOT NULL,
    metadata_tag      TEXT NOT NULL,
    timestamp         TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (session_id) REFERENCES elimination_sessions(session_id)
);

CREATE INDEX IF NOT EXISTS idx_trace_session ON elimination_trace(session_id, stage_k);
```

### Python Interceptor Surface

```python
import sqlite3
import uuid
from typing import Dict, List, Any, Optional

def log_elimination_event(
    stage_k: int,
    player_id: int,
    strategy_id: int,
    pruning_mechanism: str,
    session_id: Optional[str] = None,
    db_path: str = ":memory:"
) -> Dict[str, Any]:
    sess_id = session_id or f"sess_{str(uuid.uuid4())[:8]}"
    trace_id = f"trace_{str(uuid.uuid4())[:8]}"
    
    # 1. Classification
    mech = pruning_mechanism.lower()
    if mech in ("z3", "clingo", "hard_logic"):
        tag = "HARD_LOGIC"
    elif "decay" in mech or "probabilistic" in mech:
        tag = "PROBABILISTIC_DECAY"
    elif "early" in mech or "circuit" in mech:
        tag = "EARLY_TERMINATION"
    else:
        tag = "CUSTOM_PRUNING"
        
    # 2. SQLite Persistence
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS elimination_sessions (
            session_id TEXT PRIMARY KEY,
            game_definition TEXT,
            started_at TEXT DEFAULT (datetime('now')),
            completed_at TEXT,
            total_eliminated INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS elimination_trace (
            trace_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            stage_k INTEGER NOT NULL,
            player_id INTEGER NOT NULL,
            strategy_id INTEGER NOT NULL,
            pruning_mechanism TEXT NOT NULL,
            metadata_tag TEXT NOT NULL,
            timestamp TEXT DEFAULT (datetime('now'))
        )
    """)
    
    conn.execute("INSERT OR IGNORE INTO elimination_sessions (session_id) VALUES (?)", (sess_id,))
    conn.execute(
        "INSERT INTO elimination_trace VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))",
        (trace_id, sess_id, stage_k, player_id, strategy_id, pruning_mechanism, tag)
    )
    conn.execute(
        "UPDATE elimination_sessions SET total_eliminated = total_eliminated + 1 WHERE session_id = ?",
        (sess_id,)
    )
    conn.commit()
    
    row = conn.execute("SELECT COUNT(*) FROM elimination_trace WHERE session_id = ?", (sess_id,)).fetchone()
    total_traces = row[0] if row else 1
    conn.close()
    
    return {
        "trace_id": trace_id,
        "logged": True,
        "metadata_tag": tag,
        "total_traces_session": total_traces
    }
```

---

## Anti-Patterns & Guardrails

- **Un-Categorized Pruning Events** — Logging strategy drops without standard metadata classification tags.
- **Un-Indexed Session Queries** — Querying large elimination trace databases without indexing on `(session_id, stage_k)`.
- **Orphan Trace Insertion** — Storing trace records without establishing an active `elimination_sessions` parent record.
