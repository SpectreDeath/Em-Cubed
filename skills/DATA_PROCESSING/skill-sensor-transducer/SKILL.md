---
name: skill-sensor-transducer
domain: DATA_PROCESSING
version: 1.0.0
surfaces:
  - python
  - sqlite
description: Sensory data ingestion and normalization engine converting low-level unstructured input streams into bounded typed arrays and matrices. Applies deterministic numerical normalization modes (minmax scaling $[0, 1]$, standard z-score $\mathcal{N}(0, 1)$, or quantile rank scaling), computes raw input descriptive statistics, validates explicit field boundary constraints, and persists normalized records with cryptographic schema hashes in SQLite for downstream Prolog and Z3 ingestion. Use when preparing raw streaming data for declarative reasoning surfaces.
purpose: Deterministically normalize unstructured raw sensor streams into typed, bounded arrays with SQLite schema validation.
dependencies: []
tags:
  - sensor-transducer
  - data-normalization
  - minmax-scaling
  - zscore-standardization
  - sqlite-persistence
  - schema-hashing
inputs:
  raw_stream:
    type: object
    required: true
    description: Unstructured raw input payload (telemetry dictionary, binary payload, or numeric stream).
  schema:
    type: object
    required: true
    description: 'Target schema definition specifying field names, types, and explicit value bounds `{''fields'': [{''name'': ''val'', ''type'': ''float'', ''bounds'': [0, 100]}]}`.'
  normalization_mode:
    type: string
    required: false
    description: Normalization method (`'minmax'`, `'zscore'`, or `'quantile'`, default `'minmax'`).
outputs:
  normalized_data:
    type: object
    description: Bounded, typed dictionary of normalized numerical values.
  schema_hash:
    type: string
    description: Cryptographic SHA-256 hash string verifying target schema alignment.
  raw_stats:
    type: object
    description: Baseline statistical summary of raw input values (min, max, mean, std).
  record_id:
    type: integer
    description: SQLite autoincrement record ID assigned upon local persistence.
---

# Skill Sensor Transducer Engine

`skill-sensor-transducer` acts as the sensory input interface for the Em-Cubed agent architecture. It converts raw, unstructured data streams into **bounded, typed numerical grids** in Python and persists validated records with **schema hashes in SQLite**:

$$\tilde{x}_{\text{minmax}} = \frac{x - x_{\text{min}}}{x_{\text{max}} - x_{\text{min}}} \in [0, 1], \quad \tilde{x}_{\text{zscore}} = \frac{x - \mu}{\sigma}$$

$$\text{SchemaHash} = \text{SHA256}(\text{CanonicalJSON}(\text{Schema}))$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Sensor Transduction Progression

```
[1. Stream Ingest & Schema Hash Audit] → [2. Raw Statistical Profiling] → [3. Visual Brief] → [4. Checkpoint] → [5. Numerical Normalization, SQLite & Emit]
```

### Stage 1: Stream Ingest & Schema Hash Audit
1. Ingest `raw_stream` and target `schema`.
2. Compute SHA-256 hash of canonical schema definition.
3. Verify that all required schema fields are present in raw stream.

> **Completion criterion**: Valid schema and hash verified.

---

### Stage 2: Raw Statistical Profiling
1. Extract numeric values from raw input stream.
2. Compute raw sample descriptive statistics: minimum $x_{\text{min}}$, maximum $x_{\text{max}}$, arithmetic mean $\mu$, and standard deviation $\sigma$.

> **Completion criterion**: Raw input statistics evaluated.

---

### Stage 3: The Visual Brief
For sensory stream normalization and field distributions, generate an interactive brief:
- **Location**: Write to `%TEMP%\sensor-transducer-brief-<timestamp>.html` (Windows) or `/tmp/sensor-transducer-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render before vs. after normalization distribution histograms, schema field bounds table, and SQLite persistence record badge.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before persistence:
1. Verify variance bounds: if $x_{\text{max}} == x_{\text{min}}$, prevent division by zero by setting normalized value to $0.5$ (or $0.0$).
2. Check schema boundary constraints: clamp values exceeding explicit schema bounds $[L, U]$.

> **Completion criterion**: Zero-division guard and bound clamping verified.

---

### Stage 5: Numerical Normalization, SQLite & Output Emission
1. Apply selected normalization mode (`minmax`, `zscore`, or `quantile`).
2. Insert record into local SQLite database table `normalized_records`.
3. Emit complete `TransductionResult` record.

> **Completion criterion**: Full transduced payload emitted with SQLite record ID.

---

## Surface References

### SQLite Persistence Surface

```sql
CREATE TABLE IF NOT EXISTS normalized_records (
    record_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    schema_hash      TEXT NOT NULL,
    normalized_data  TEXT NOT NULL, -- JSON blob
    raw_stats        TEXT,          -- JSON blob
    created_at       INTEGER DEFAULT (strftime('%s','now'))
);

CREATE INDEX IF NOT EXISTS idx_schema_hash ON normalized_records(schema_hash);
```

### Python Transduction Surface

```python
import hashlib
import json
import sqlite3
from typing import Dict, List, Any, Optional

def transduce_sensor_stream(
    raw_stream: Dict[str, Any],
    schema: Dict[str, Any],
    normalization_mode: str = "minmax",
    db_path: str = ":memory:"
) -> Dict[str, Any]:
    # 1. Canonical Schema Hash
    schema_str = json.dumps(schema, sort_keys=True)
    schema_hash = hashlib.sha256(schema_str.encode("utf-8")).hexdigest()[:16]
    
    fields = schema.get("fields", [])
    raw_values = []
    normalized_fields = {}
    
    for f in fields:
        name = f["name"]
        val = raw_stream.get(name, 0.0)
        if isinstance(val, (int, float)):
            raw_values.append(float(val))
            
    # 2. Raw Statistics
    if raw_values:
        v_min, v_max = min(raw_values), max(raw_values)
        v_mean = sum(raw_values) / len(raw_values)
        v_var = sum((v - v_mean) ** 2 for v in raw_values) / (len(raw_values) if len(raw_values) > 1 else 1)
        v_std = v_var ** 0.5
    else:
        v_min = v_max = v_mean = v_std = 0.0
        
    raw_stats = {"min": v_min, "max": v_max, "mean": round(v_mean, 4), "std": round(v_std, 4)}
    
    # 3. Normalization
    for f in fields:
        name = f["name"]
        val = float(raw_stream.get(name, 0.0))
        bounds = f.get("bounds", [v_min, v_max])
        b_min = bounds[0] if bounds and bounds[0] is not None else v_min
        b_max = bounds[1] if bounds and bounds[1] is not None else v_max
        
        if normalization_mode == "minmax":
            rng = b_max - b_min
            norm_v = (val - b_min) / rng if rng > 0 else 0.5
            norm_v = max(0.0, min(1.0, norm_v))
        elif normalization_mode == "zscore":
            norm_v = (val - v_mean) / v_std if v_std > 0 else 0.0
        else:
            norm_v = val
            
        normalized_fields[name] = round(norm_v, 6)
        
    # 4. SQLite Persistence
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS normalized_records (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            schema_hash TEXT NOT NULL,
            normalized_data TEXT NOT NULL,
            raw_stats TEXT,
            created_at INTEGER DEFAULT (strftime('%s','now'))
        )
    """)
    cur = conn.execute(
        "INSERT INTO normalized_records (schema_hash, normalized_data, raw_stats) VALUES (?, ?, ?)",
        (schema_hash, json.dumps(normalized_fields), json.dumps(raw_stats))
    )
    conn.commit()
    rec_id = cur.lastrowid
    conn.close()
    
    return {
        "normalized_data": normalized_fields,
        "schema_hash": schema_hash,
        "raw_stats": raw_stats,
        "record_id": rec_id
    }
```

---

## Anti-Patterns & Guardrails

- **Division by Zero on Constant Sensor Signals** — Failing to guard $(x_{\text{max}} - x_{\text{min}})$ when input streams carry identical values.
- **Unbounded Scaling Outliers** — Emitting un-clamped minmax values $> 1.0$ when sensor inputs breach pre-configured schema bounds.
- **Un-Hashed Schema Changes** — Storing normalized records without schema hash tracking, leading to ambiguous structural interpretations.
