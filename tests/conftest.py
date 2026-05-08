"""Test fixtures and utilities for em_cubed tests."""

from em_cubed.plugin_manager import SurfacePlugin
from typing import Dict, Any, Optional


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
