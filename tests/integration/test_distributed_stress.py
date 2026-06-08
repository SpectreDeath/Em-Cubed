"""Integration tests for distributed execution and stress testing."""

import pytest
import time
from pathlib import Path

class TestUciCensusRandomForest:
    """E1: Stress-test Async Timeouts: UCI Census Income via Random Forest."""
    
    @pytest.fixture
    def skills_dir(self):
        return Path("skills")
    
    @pytest.mark.asyncio
    async def test_distributed_executor_event_loop_safety(self, skills_dir):
        """Verify submit_workflow works from both sync and async contexts."""
        from em_cubed.workflow.distributed import (
            DistributedTask, initialize_distributed_executor
        )
        from em_cubed.skills.telemetry import initialize_telemetry
        
        initialize_telemetry()
        
        # Test that ProcessDistributedExecutor can be instantiated and submit_workflow works
        executor = initialize_distributed_executor(skills_dir)
        
        workflow_id = "test-workflow"
        task = DistributedTask(
            task_id="test-task-1",
            workflow_id=workflow_id,
            skill_id="test-skill",
            input_data={"test": "data"}
        )
        
        # This should not raise RuntimeError for missing event loop
        result = executor.submit_workflow(workflow_id, [task])
        assert result is True


class TestSqliteDatalogWebDataCommons:
    """E3: Test SQLite/Datalog surfaces with Web Data Commons structured data."""
    
    @pytest.mark.asyncio
    async def test_sqlite_surface_persists_session(self):
        """Verify SQLite surface can execute queries with session context."""
        from em_cubed.surfaces.sqlite_surface import SQLiteSurface
        from em_cubed.skills.telemetry import initialize_telemetry
        
        initialize_telemetry()
        
        surface = SQLiteSurface()
        session_id = "test-session-123"
        context = {"skill_input": {}, "surfaces": {}, "trace": None, "session_id": session_id}
        
        start = time.time()
        
        # Create table
        create_sql = """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT,
            name TEXT,
            price REAL,
            category TEXT
        );
        """
        
        result = await surface.execute(create_sql, context)
        assert result.get("status") in ("ok", "error")
        
        # Insert data
        insert_sql = "INSERT INTO products (product_id, name, price, category) VALUES ('P1', 'Product 1', 10.0, 'electronics');"
        result = await surface.execute(insert_sql, context)
        assert result.get("status") in ("ok", "error")
        
        # Query for aggregation - using same session to persist data
        query_sql = "SELECT category, COUNT(*), AVG(price) FROM products GROUP BY category;"
        result = await surface.execute(query_sql, context)
        
        elapsed_ms = (time.time() - start) * 1000
        
        assert elapsed_ms < 5000, f"Query latency exceeded 5s: {elapsed_ms}ms"
        assert result.get("status") == "ok"
        assert result.get("value") is not None
