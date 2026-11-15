---
name: sql-aggregator
domain: DATA_PROCESSING
version: 1.0.0
surfaces:
  - python
  - sqlite
description: In-memory SQLite data aggregation and tabular querying engine. Ingests raw structured row/column records, dynamically compiles table schemas, executes parameterized aggregation queries (COUNT, SUM, AVG, MIN, MAX, GROUP BY, HAVING), filters records via SQL clauses, and returns typed summary result sets with session persistence in Python and SQLite. Use when performing relational data summaries, grouping tabular records, or executing SQL queries within agent workflows.
purpose: Aggregate and summarize tabular datasets using in-memory SQLite tables and parameterized SQL queries.
dependencies: []
tags:
  - sql-aggregator
  - sqlite-aggregation
  - group-by
  - tabular-query
  - data-summarization
  - in-memory-db
inputs:
  columns:
    type: array
    required: true
    description: List of column header names `['department', 'salary', 'experience']`.
  rows:
    type: array
    required: true
    description: List of data row tuples/lists `[['Engineering', 120000, 5], ['Sales', 95000, 3], ...]`.
  query:
    type: string
    required: false
    description: Custom SQL aggregation query (default `'SELECT COUNT(*) as count FROM input_data'`).
  group_by:
    type: array
    required: false
    description: Optional list of columns to group by `['department']`.
  aggregations:
    type: object
    required: false
    description: 'Optional mapping of columns to aggregation functions `{''salary'': ''AVG'', ''experience'': ''MAX''}`.'
outputs:
  results:
    type: array
    description: List of aggregated result row dictionaries matching query columns.
  row_count:
    type: integer
    description: Total number of records returned in the aggregation result set.
  executed_query:
    type: string
    description: Formulated SQL query executed against the in-memory database.
  execution_status:
    type: string
    description: Status string (`'ok'` or `'error'`).
---

# SQL Aggregator Engine

`sql-aggregator` executes relational **group-by and aggregation queries** over dynamic tabular datasets using **in-memory SQLite tables** orchestrated by **Python**:

$$\text{Table}(T) \leftarrow \text{Ingest}(\text{Columns}, \text{Rows}), \quad \mathcal{R} \leftarrow \sigma_{\text{filter}} \left( \gamma_{G, \text{agg}(A)} (T) \right)$$

$$\text{Query: } \text{SELECT } g_1, \dots, g_k, \text{AGG}_1(a_1), \dots \text{ FROM input\_data GROUP BY } g_1, \dots, g_k$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage SQL Aggregation Progression

```
[1. Tabular Ingest & Schema DDL Compilation] → [2. In-Memory SQLite Table Loading] → [3. Visual Brief] → [4. Checkpoint] → [5. Query Execution & Results Emit]
```

### Stage 1: Tabular Ingest & Schema DDL Compilation
1. Ingest `columns` and `rows` data arrays.
2. Validate non-empty tabular dataset ($|\text{Cols}| \ge 1, |\text{Rows}| \ge 1$).
3. Formulate DDL: `CREATE TABLE input_data (col1 TEXT, col2 REAL, ...);`.

> **Completion criterion**: Tabular schema DDL compiled.

---

### Stage 2: In-Memory SQLite Table Loading
1. Open connection to SQLite database (`:memory:` or named session).
2. Execute DDL and batch insert rows using parameterized statements:
   `INSERT INTO input_data VALUES (?, ?, ...);`.

> **Completion criterion**: Rows loaded into SQLite table without truncation.

---

### Stage 3: The Visual Brief
For tabular aggregations and grouping distributions, generate an interactive brief:
- **Location**: Write to `%TEMP%\sql-aggregator-brief-<timestamp>.html` (Windows) or `/tmp/sql-aggregator-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render SQL query syntax card, aggregated results table, and group-by category metric comparison bar chart.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before query execution:
1. If custom `query` is provided, verify query safety (prevent DROP/DELETE injections).
2. If `group_by` and `aggregations` are supplied, automatically construct validated SQL query string.

> **Completion criterion**: Safe SQL query formulated.

---

### Stage 5: Query Execution & Output Emission
1. Execute query against in-memory table and fetch all rows.
2. Format output as list of row dictionaries.
3. Emit complete `SQLAggregatorResult` record.

> **Completion criterion**: Full aggregation payload emitted.

---

## Surface References

### Python & SQLite Surface

```python
import sqlite3
from typing import Dict, List, Any, Optional

def aggregate_sql_data(
    columns: List[str],
    rows: List[List[Any]],
    query: Optional[str] = None,
    group_by: Optional[List[str]] = None,
    aggregations: Optional[Dict[str, str]] = None,
    db_path: str = ":memory:"
) -> Dict[str, Any]:
    if not columns or not rows:
        raise ValueError("missing_data: columns and rows must be non-empty.")
        
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # 1. Infer simple SQLite types from first row
    first_row = rows[0]
    col_defs = []
    for i, col in enumerate(columns):
        val = first_row[i] if i < len(first_row) else None
        if isinstance(val, int):
            col_defs.append(f"\"{col}\" INTEGER")
        elif isinstance(val, float):
            col_defs.append(f"\"{col}\" REAL")
        else:
            col_defs.append(f"\"{col}\" TEXT")
            
    create_sql = f"CREATE TABLE input_data ({', '.join(col_defs)});"
    conn.execute(create_sql)
    
    # 2. Batch Insert
    placeholders = ", ".join(["?"] * len(columns))
    insert_sql = f"INSERT INTO input_data VALUES ({placeholders});"
    conn.executemany(insert_sql, rows)
    conn.commit()
    
    # 3. Formulate Query
    if query:
        exec_sql = query
    elif group_by and aggregations:
        select_parts = [f"\"{g}\"" for g in group_by]
        for col, func in aggregations.items():
            select_parts.append(f"{func}(\"{col}\") as \"{func.lower()}_{col}\"")
        exec_sql = f"SELECT {', '.join(select_parts)} FROM input_data GROUP BY {', '.join([f'\"{g}\"' for g in group_by])};"
    elif aggregations:
        select_parts = [f"{func}(\"{col}\") as \"{func.lower()}_{col}\"" for col, func in aggregations.items()]
        exec_sql = f"SELECT {', '.join(select_parts)} FROM input_data;"
    else:
        exec_sql = "SELECT COUNT(*) as count FROM input_data;"
        
    # 4. Execute Query
    cur = conn.execute(exec_sql)
    results = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    return {
        "results": results,
        "row_count": len(results),
        "executed_query": exec_sql,
        "execution_status": "ok"
    }
```

---

## Anti-Patterns & Guardrails

- **SQL Injection Vulnerabilities** — Directly interpolating un-sanitized raw text into SQL strings without column quoting and parameterized values.
- **Empty Row Ingestion** — Attempting table creation and querying with empty row lists, raising unhandled SQLite errors.
- **Unclosed Database Connections** — Leaving in-memory SQLite connections unclosed in long-running multi-agent pipelines.
