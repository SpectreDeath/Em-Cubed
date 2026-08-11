"""Base class for surface plugins."""

import asyncio
import os
from abc import ABC, abstractmethod
from typing import Any

import structlog

logger = structlog.get_logger()


class SurfaceTimeoutError(Exception):
    """Raised when a surface operation times out."""


class SurfacePlugin(ABC):
    """Base class for surface plugins."""

    def __init__(self, timeout: float | None = None):
        """Initialize surface plugin with optional timeout.

        Args:
            timeout: Optional timeout in seconds for surface operations
        """
        self.timeout = timeout
        self._executor: Any | None = None  # Thread pool executor for async execution
        self._substrate: dict[str, Any] = {}  # Shared data substrate across surfaces

    @property
    @abstractmethod
    def name(self) -> str:
        """Surface name (e.g., 'python', 'prolog')."""

    @property
    @abstractmethod
    def available(self) -> bool:
        """Check if surface dependencies are available."""

    @abstractmethod
    async def execute(self, code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute code on this surface."""

    @abstractmethod
    async def health(self) -> bool:
        """Check if surface is operational.

        Returns:
            True if surface is operational
        """

    @abstractmethod
    def extract_tags(self, source: str | None) -> list[str]:
        """Extract relevant tags from source code.

        Args:
            source: Source code string

        Returns:
            List of tag strings
        """

    def initialize(self) -> None:
        """Optional initialization hook for plugin setup."""

    def shutdown(self) -> None:
        """Optional shutdown hook for plugin cleanup."""
        # Clean up thread pool executor
        if self._executor:
            self._executor.shutdown(wait=False)
            self._executor = None

    @property
    def substrate(self) -> dict[str, Any]:
        """Shared data substrate across surfaces."""
        return self._substrate

    @substrate.setter
    def substrate(self, value: dict[str, Any]) -> None:
        self._substrate = value

    async def execute_with_timeout(self, code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute code with timeout protection.

        Args:
            code: Source code to execute
            context: Optional execution context

        Returns:
            Dict with status, value/error message
        """
        try:
            result = await asyncio.wait_for(
                self.execute(code, context), timeout=self.timeout or float(os.getenv("EM_CUBED_TIMEOUT", "30"))
            )
            return result
        except (asyncio.TimeoutError, TimeoutError):
            logger.warning("Surface execution timed out", timeout=self.timeout)
            return {"status": "error", "message": f"Execution timed out after {self.timeout}s"}
