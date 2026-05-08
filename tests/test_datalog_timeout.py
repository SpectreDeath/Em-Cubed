"""Datalog surface timeout test."""
import pytest
from em_cubed.surfaces import DatalogSurface

pytestmark = pytest.mark.asyncio


async def test_datalog_timeout():
    """Test that DatalogSurface respects timeout configuration."""
    surface = DatalogSurface()
    if not surface.available:
        pytest.skip("pyDatalog not available")
    # Override timeout to a low value
    surface.timeout = 0.1
    # Use a CPU-intensive loop to trigger timeout (imports not allowed in asteval)
    long_running_code = "i = 0\nwhile i < 100000000:\n    i += 1"
    result = await surface.execute(long_running_code, {})
    assert result["status"] == "error"
    assert "timed out" in result["message"].lower()
