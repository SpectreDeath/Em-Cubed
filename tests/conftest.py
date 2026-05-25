"""Test fixtures and utilities for em_cubed tests."""

import asyncio
from typing import Dict, Any, Optional

import pytest

from em_cubed.plugin import SurfacePlugin


class TestSurfacePlugin(SurfacePlugin):
    """Test implementation of SurfacePlugin for unit tests."""

    def __init__(self, name: str = "test", available: bool = True, timeout: Optional[float] = None):
        super().__init__(timeout)
        self._name = name
        self._available = available

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    async def _execute_impl(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"status": "ok", "value": f"test result for {code}"}

    def extract_tags(self, source: Optional[str]) -> list:
        return ["test"]

    async def health(self) -> bool:
        return self._available


@pytest.fixture(scope="session", autouse=True)
def cleanup_event_loop():
    """Ensure event loop is properly cleaned up after all tests."""
    yield
    # Force close any remaining event loops
    try:
        loop = asyncio.get_running_loop()
        if loop and not loop.is_closed():
            loop.run_until_complete(loop.shutdown_asyncgens())
    except RuntimeError:
        pass
