# Skill Summary Card: `sql-aggregator`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        sql-aggregator                            │
│ Category:    DATA_PROCESSING / SQL Aggregations        │
│ Invocation:  /sql-aggregator                           │
│ Trigger:     "sql aggregator", "aggregate tabular data",│
│              "sqlite query", "group by sum", "sql sum" │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Aggregate and summarize tabular datasets  │
│              using in-memory SQLite tables and         │
│              parameterized SQL aggregation queries.    │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest columns & rows; compile DDL schema | Tabular Dataset AST | $|\text{Cols}| \ge 1, |\text{Rows}| \ge 1$ |
| **2. Table Load** | Create in-memory table & batch insert records | SQLite Memory Table | Records loaded |
| **3. Visual Brief** | Render query card & aggregation bar charts | `%TEMP%\sql-aggregator-brief-*.html`| Dark theme HTML brief |
| **4. Checkpoint** | Validate SQL query safety & parameter quotes | Query Gate Record | Injection guards passed |
| **5. Model Emission**| Execute SQL query, fetch rows & emit payload | `SQLAggregatorResult` Payload | Full result payload emitted |

---

## Invariants & Guardrails

- [ ] **Data Integrity Invariant**: Column count must match row elements.
- [ ] **SQL Sanitization**: All column identifiers escaped with double quotes.
- [ ] **Resource Cleanup**: In-memory database connections explicitly closed.
