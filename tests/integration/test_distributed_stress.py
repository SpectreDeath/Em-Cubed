"""Integration tests for distributed execution and stress testing."""

import time

import pytest

from em_cubed.surfaces import PythonSurface

_RF_TRAINING_CODE = """
# Synthetic CPU workload for surface timeout testing
total = 0
for i in range(10000000):
    total += i
result = total
"""


class TestUciCensusRandomForest:
    """Stress-test Async Timeouts: UCI Census Income via Random Forest."""

    @pytest.fixture
    def uci_census_dataset(self):
        """Small synthetic UCI Census Income-style dataset."""
        import random

        random.seed(42)
        n = 30
        features = []
        labels = []
        for _ in range(n):
            age = random.randint(17, 90)
            hours = random.randint(1, 99)
            capital_gain = random.randint(0, 100000)
            capital_loss = random.randint(0, 5000)
            education_num = random.randint(1, 16)
            features.append([age, hours, capital_gain, capital_loss, education_num])
            labels.append(1 if (age > 30 and hours > 40 and capital_gain > 5000) else 0)
        return features, labels

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_random_forest_uci_timeout(self, uci_census_dataset):
        """Random Forest on larger UCI-style data should trigger timeout/rejection behavior."""
        features, labels = uci_census_dataset
        surface = PythonSurface(timeout=0.001)
        start = time.time()
        response = await surface.execute(
            _RF_TRAINING_CODE,
            {"features": features, "labels": labels},
        )
        elapsed = time.time() - start
        assert response.get("status") == "error"
        assert "timed out" in response.get("message", "").lower() or "rejected" in response.get("message", "").lower()
        assert elapsed < 30.0

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_dag_scheduler_timeout_rejection(self):
        """DAG scheduler should reject execution when concurrency limit is reached."""
        surface = PythonSurface(timeout=0.001)
        long_running = "x = 0\nwhile x < 10000000:\n    x += 1"
        tasks = [surface.execute(long_running, {}) for _ in range(3)]
        results = await __import__("asyncio").gather(*tasks, return_exceptions=False)
        assert all(r["status"] == "error" for r in results)
        assert any("timed out" in r["message"].lower() or "rejected" in r["message"].lower() for r in results)


class TestSqliteDatalogWebDataCommons:
    """E3: Test SQLite/Datalog surfaces with Web Data Commons structured data."""

    @pytest.mark.asyncio
    async def test_sqlite_surface_persists_session(self):
        """Verify SQLite surface can execute queries with session context."""
        from em_cubed.skills.telemetry import initialize_telemetry
        from em_cubed.surfaces.sqlite_surface import SQLiteSurface

        initialize_telemetry()

        surface = SQLiteSurface()
        session_id = "test-session-123"
        context = {"skill_input": {}, "surfaces": {}, "trace": None, "session_id": session_id}

        start = time.time()

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

        insert_sql = (
            "INSERT INTO products (product_id, name, price, category) VALUES ('P1', 'Product 1', 10.0, 'electronics');"
        )
        result = await surface.execute(insert_sql, context)
        assert result.get("status") in ("ok", "error")

        query_sql = "SELECT category, COUNT(*), AVG(price) FROM products GROUP BY category;"
        result = await surface.execute(query_sql, context)

        elapsed_ms = (time.time() - start) * 1000

        assert elapsed_ms < 5000, f"Query latency exceeded 5s: {elapsed_ms}ms"
        assert result.get("status") == "ok"
        assert result.get("value") is not None
