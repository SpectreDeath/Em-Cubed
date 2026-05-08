"""Concurrent execution tests for multiple surfaces."""

import asyncio
import pytest
from em_cubed.surfaces import PythonSurface, PrologSurface, HySurface

pytestmark = pytest.mark.asyncio


class TestConcurrentExecution:
    """Test concurrent execution across multiple surfaces."""

    async def test_concurrent_python_executions(self):
        """Multiple Python surface calls in parallel should all succeed."""
        surface = PythonSurface()
        tasks = [
            surface.execute("x * 2", {"x": i})
            for i in range(10)
        ]
        results = await asyncio.gather(*tasks)

        assert all(r["status"] == "ok" for r in results)
        values = [r["value"] for r in results]
        assert values == [i * 2 for i in range(10)]

    async def test_concurrent_mixed_surfaces(self):
        """Concurrent calls on different surfaces when all are available."""
        surfaces = []
        py = PythonSurface()
        surfaces.append(py)
        # Try Prolog if available
        try:
            prolog = PrologSurface()
            if prolog.available:
                surfaces.append(prolog)
        except Exception:
            pass
        try:
            hy = HySurface()
            if hy.available:
                surfaces.append(hy)
        except Exception:
            pass

        if not surfaces:
            pytest.skip("No surfaces available for concurrency test")

        # Create mixed tasks
        tasks = []
        for surf in surfaces:
            if surf.name == "python":
                tasks.append(surf.execute("1 + 1", {}))
            elif surf.name == "prolog":
                tasks.append(surf.execute("X is 1 + 1", {}))
            elif surf.name == "hy":
                tasks.append(surf.execute("(+ 1 1)", {}))

        results = await asyncio.gather(*tasks, return_exceptions=False)

        # All should succeed
        for r in results:
            assert r["status"] == "ok"

    async def test_concurrent_timeout_behavior(self):
        """Concurrent timeouts should not deadlock."""
        surface = PythonSurface(timeout=0.1)
        # Use a CPU-intensive loop that will exceed the timeout
        # (imports are blocked by asteval, so we use a tight loop)
        long_running_code = "i = 0\nwhile i < 100000000:\n    i += 1"
        tasks = [
            surface.execute(long_running_code, {})
            for _ in range(3)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=False)

        # All should error with timeout
        for r in results:
            assert r["status"] == "error"
            assert "timed out" in r["message"].lower()
