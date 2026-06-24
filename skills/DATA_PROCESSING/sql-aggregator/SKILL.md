---
name: sql-aggregator
domain: DATA_PROCESSING
version: 1.0.0
surfaces:
- python
- sqlite
description: SQL aggregator for summarizing and querying tabular data with configurable grouping and filters.
compatibility: PYTHON
allowed-tools: '- read

  - write

  - edit

  - bash

  - glob

  - grep

  - codebase_search

  - task

  - sequentialthinking_sequentialthinking

  - webfetch

  - websearch

  - question

  - suggest

  '
---

## Purpose
Aggregate and summarize tabular data using SQL queries within a skill pipeline.

## Description
This skill demonstrates the use of an in-memory SQLite database to perform data aggregation tasks. Python code is used to load, validate, and transform data, while SQL is used for grouping, filtering, and computing aggregates.

## Implementation

### Python
```python
def main(skill_input):
    """Orchestrate the aggregation pipeline."""

    # 1. Prepare data (example using in-memory structure)
    raw_data = skill_input.get("data", [])
    columns = skill_input.get("columns", [])
    rows = skill_input.get("rows", [])

    if not columns or not rows:
        return {"status": "error", "message": "Missing columns or rows in input"}

    # 2. Build table schema and ingest data via SQL
    table_name = "input_data"
    col_defs = ", ".join([f"{c} TEXT" for c in columns])
    create_sql = f"CREATE TABLE {table_name} ({col_defs});"
    placeholders = ", ".join(["?" for _ in columns])
    insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders});"

    # Execute via sqlite surface with session persistence
    context = {"session_id": "sql_aggregator_session"}
    result_create = context["surfaces"]["sqlite"].execute_sync(create_sql, context)
    if result_create["status"] != "ok":
        return {"status": "error", "message": f"Failed to create table: {result_create.get('message')}"}

    for row in rows:
        result_insert = context["surfaces"]["sqlite"].execute_sync(insert_sql, [row], context)
        if result_insert["status"] != "ok":
            return {"status": "error", "message": f"Failed to insert row: {result_insert.get('message')}"}

    # 3. Perform aggregation (example: count rows)
    agg_sql = f"SELECT COUNT(*) as count FROM {table_name};"
    result_agg = context["surfaces"]["sqlite"].execute_sync(agg_sql, context)
    if result_agg["status"] != "ok":
        return {"status": "error", "message": f"Aggregation failed: {result_agg.get('message')}"}

    return {"status": "ok", "count": result_agg["value"][0]["count"]}
```

### SQLite
```sql
-- Ingested dynamically from Python orchestration
```

## Examples
```python
input_data = {
    "columns": ["id", "name"],
    "rows": [
        [1, "Alice"],
        [2, "Bob"],
        [3, "Charlie"]
    ]
}
# Expected output: {"status": "ok", "count": 3}
```
