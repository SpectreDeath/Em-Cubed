"""Tests for SQLite surface implementation."""

import pytest
from em_cubed.surfaces.sqlite_surface import SQLiteSurface


@pytest.fixture
def sqlite_surface():
    """Create a SQLiteSurface instance."""
    return SQLiteSurface()


@pytest.mark.asyncio
async def test_basic_select(sqlite_surface):
    """Test basic SELECT query on fresh connection."""
    result = await sqlite_surface.execute("SELECT 1 AS value")
    assert result["status"] == "ok"
    assert result["value"] == [{"value": 1}]


@pytest.mark.asyncio
async def test_multi_statement(sqlite_surface):
    """Test multi-statement execution: CREATE, INSERT, SELECT."""
    code = """
        CREATE TABLE test (id INTEGER, name TEXT);
        INSERT INTO test VALUES (1, 'Alice');
        INSERT INTO test VALUES (2, 'Bob');
        SELECT * FROM test ORDER BY id;
    """
    result = await sqlite_surface.execute(code)
    assert result["status"] == "ok"
    rows = result["value"]
    assert len(rows) == 2
    assert rows[0]["id"] == 1
    assert rows[0]["name"] == "Alice"
    assert rows[1]["id"] == 2
    assert rows[1]["name"] == "Bob"


@pytest.mark.asyncio
async def test_session_persistence(sqlite_surface):
    """Test that session persistence retains schema across calls."""
    # First call: create table with session_id
    context1 = {"session_id": "test_session"}
    create_sql = "CREATE TABLE items (id INTEGER PRIMARY KEY, value TEXT);"
    result1 = await sqlite_surface.execute(create_sql, context=context1)
    assert result1["status"] == "ok"

    # Second call: insert data using same session_id
    insert_sql = "INSERT INTO items VALUES (1, 'first'), (2, 'second');"
    result2 = await sqlite_surface.execute(insert_sql, context=context1)
    assert result2["status"] == "ok"

    # Third call: query data with same session_id
    select_sql = "SELECT * FROM items ORDER BY id;"
    result3 = await sqlite_surface.execute(select_sql, context=context1)
    assert result3["status"] == "ok"
    rows = result3["value"]
    assert len(rows) == 2
    assert rows[0]["value"] == "first"

    # Cleanup session
    sqlite_surface.close_session("test_session")


@pytest.mark.asyncio
async def test_session_isolation(sqlite_surface):
    """Test that different session_ids do not share data."""
    ctx_a = {"session_id": "session_a"}
    ctx_b = {"session_id": "session_b"}

    await sqlite_surface.execute("CREATE TABLE t (x INTEGER);", context=ctx_a)
    await sqlite_surface.execute("INSERT INTO t VALUES (42);", context=ctx_a)

    # Session B should not see table created in session A
    result = await sqlite_surface.execute("SELECT * FROM t;", context=ctx_b)
    # Should error or return empty; let's expect error because table doesn't exist
    assert result["status"] == "error"  # no such table


@pytest.mark.asyncio
async def test_error_handling_invalid_sql(sqlite_surface):
    """Test that invalid SQL returns error status."""
    result = await sqlite_surface.execute("SELECT * FROM nonexistent_table")
    assert result["status"] == "error"
    assert "message" in result


@pytest.mark.asyncio
async def test_extract_tags(sqlite_surface):
    """Test extract_tags correctly identifies table names."""
    source = """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT
        );
        CREATE TABLE orders (
            id INTEGER,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        SELECT u.name, o.id
        FROM users u
        JOIN orders o ON u.id = o.user_id;
    """
    tags = sqlite_surface.extract_tags(source)
    # Should extract table names: users, orders, maybe duplicates
    assert "users" in tags
    assert "orders" in tags


def test_health(sqlite_surface):
    """Test health check returns True (sqlite3 always available)."""
    # health is sync method
    import asyncio
    assert asyncio.run(sqlite_surface.health()) is True


@pytest.mark.asyncio
async def test_commit_behavior(sqlite_surface):
    """Test that DML statements are committed properly."""
    code = """
        CREATE TABLE nums (n INTEGER);
        INSERT INTO nums VALUES (10);
        INSERT INTO nums VALUES (20);
    """
    result = await sqlite_surface.execute(code)
    assert result["status"] == "ok"
    # Verify rows_affected
    assert result["value"]["rows_affected"] == 1  # last INSERT
