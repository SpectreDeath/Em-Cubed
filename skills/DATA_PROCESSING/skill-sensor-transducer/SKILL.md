---
name: skill-sensor-transducer
domain: DATA_PROCESSING
version: 1.0.0
surfaces:
- python
- sqlite
description: 'Normalizes low-level unstructured input into bounded typed structures. Maps raw byte streams into normalized
  key-value spaces or typed tables so downstream declarative surfaces can consume deterministic data.

  '
purpose: 'Prepare the structural grid of numbers for downstream surfaces like Prolog or Z3 without parsing raw strings. No
  inference, just deterministic transduction.

  '
dependencies:
- durable-execution-engine
tags:
- transduction
- normalization
- python
- sqlite
- sensor
- ingestion
- retinal-model
inputs:
  raw_stream:
    type: object
    required: true
    description: Unstructured raw input (bytes, telemetry logs, binary blobs)
  schema:
    type: object
    required: true
    description: Target normalized schema with field definitions
  normalization_mode:
    type: string
    required: false
    description: 'minmax | zscore | quantile (default: minmax)'
outputs:
  normalized_data:
    type: object
    description: Normalized and typed structured data
  schema_hash:
    type: string
    description: Hash of the applied schema for verification
  raw_stats:
    type: object
    description: Statistics of raw input before normalization
---

# Skill Sensor Transducer

Normalizes unstructured input into bounded typed matrices.

## Tick Protocol

| Id | Surface  | Action                                                |
|----|----------|-------------------------------------------------------|
| 1  | Python   | Parse `raw_stream` and `schema`                       |
| 2  | Python   | Compute `raw_stats` (min, max, mean, std)             |
| 3  | Python   | Apply normalization to each field per `normalization_mode` |
| 4  | SQLite   | Persist normalized record with `schema_hash`          |
| 5  | Python   | Return `normalized_data`                              |

## Surfaces

### Python Surface

```python
surfaces.skill_sensor_transducer.transduce(
    raw_stream={"packet": b"...", "timestamp": 1718888888, "value": 42},
    schema={
        "fields": [
            {"name": "timestamp", "type": "int", "bounds": [0, null]},
            {"name": "value", "type": "float", "bounds": [0, 100]}
        ]
    },
    normalization_mode="minmax"
)
```

### SQLite Surface

```sql
CREATE TABLE IF NOT EXISTS normalized_records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    schema_hash TEXT NOT NULL,
    normalized_data JSON NOT NULL,
    raw_stats JSON,
    created_at INTEGER DEFAULT (strftime('%s','now'))
);
```

## Capability Contract

**Inputs:**

- `raw_stream` *(object, required)* — Unstructured raw input (bytes, telemetry logs, binary blobs).
- `schema` *(object, required)* — Target normalized schema with field definitions.
- `normalization_mode` *(string, optional)* — `minmax`, `zscore`, or `quantile`. Default `minmax`.

**Outputs:**

- `normalized_data` *(object)* — Normalized and typed structured data.
- `schema_hash` *(string)* — Hash of the applied schema for verification.
- `raw_stats` *(object)* — Statistics of raw input before normalization.

## Composition

- `skill-invariant-filter` — Consumes `normalized_data` for relational extraction.
- `skill-constraint-resolver` — Consumes `normalized_data` for constraint solving.
- `skill-unconscious-inference` — Consumes `normalized_data` for probabilistic scoring.
