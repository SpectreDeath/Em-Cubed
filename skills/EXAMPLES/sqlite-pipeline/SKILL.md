---
name: SQLite Pipeline
Domain: EXAMPLES
Version: 1.0.0
surfaces:
  - python
  - sqlite
---

## Purpose
Demonstrate a Python → SQLite → Python pipeline using session persistence.

## Description
A simple example skill that sets up an in-memory SQLite database, stores some generated data, performs a query, and returns results back to Python.

## Implementation

### Python
```python
def main(skill_input):
    """Run end-to-end pipeline using SQLite session persistence."""
    session_id = "sqlite_pipeline_session"

    # Step 1: Create table
    create_sql = "CREATE TABLE IF NOT EXISTS numbers (id INTEGER PRIMARY KEY, value REAL);"
    r1 = context["surfaces"]["sqlite"].execute_sync(create_sql, {"session_id": session_id})

    if r1["status"] != "ok":
        return {"status": "error", "message": f"CREATE TABLE failed: {r1}"}

    # Step 2: Insert some sample numbers
    insert_sql = "INSERT INTO numbers (value) VALUES (?);"
    numbers = skill_input.get("numbers", [1.0, 2.5, 3.7])
    for n in numbers:
        r2 = context["surfaces"]["sqlite"].execute_sync(insert_sql, [n], {"session_id": session_id})
        if r2["status"] != "ok":
            return {"status": "error", "message": f"INSERT failed: {r2}"}

    # Step 3: Query statistics
    query_sql = "SELECT COUNT(*) as count, AVG(value) as avg, SUM(value) as total FROM numbers;"
    r3 = context["surfaces"]["sqlite"].execute_sync(query_sql, {"session_id": session_id})

    if r3["status"] != "ok":
        return {"status": "error", "message": f"SELECT failed: {r3}"}

    # Return as Python dict
    stats = r3["value"][0]  # single row
    return {
        "status": "ok",
        "count": stats["count"],
        "average": stats["avg"],
        "total": stats["total"],
        "session": session_id
    }
```

### SQLite
```sql
-- Session-persistent in-memory database
-- Execute statements via Python executor
```

## Examples
```python
input_data = {"numbers": [1.0, 2.5, 3.7]}
# Expected output: {"status": "ok", "count": 3, "average": 2.4..., "total": 7.2...}
```
