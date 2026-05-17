"""Base class for surface plugins."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
import os
import structlog

logger = structlog.get_logger()


class SurfaceTimeoutError(Exception):
    """Raised when a surface operation times out."""
    pass


class SurfacePlugin(ABC):
    """Base class for surface plugins."""

    def __init__(self, timeout: Optional[float] = None):
        """Initialize surface plugin with optional timeout.

        Args:
            timeout: Optional timeout in seconds for surface operations
        """
        self.timeout = timeout
        self._executor = None  # Thread pool executor for async execution
        self._substrate = {}   # Shared data substrate across surfaces

    @property
    @abstractmethod
    def name(self) -> str:
        """Surface name (e.g., 'python', 'prolog')."""
        pass

    @property
    @abstractmethod
    def available(self) -> bool:
        """Check if surface dependencies are available."""
        pass

    @abstractmethod
    async def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute code on this surface."""
        pass

    @abstractmethod
    async def health(self) -> bool:
        """Check if surface is operational.

        Returns:
            True if surface is operational
        """
        pass

    @abstractmethod
    def extract_tags(self, source: Optional[str]) -> List[str]:
        """Extract relevant tags from source code.

        Args:
            source: Source code string

        Returns:
            List of tag strings
        """
        pass

    def initialize(self) -> None:
        """Optional initialization hook for plugin setup."""
        pass

    def shutdown(self) -> None:
        """Optional shutdown hook for plugin cleanup."""
        # Clean up thread pool executor
        if self._executor:
            self._executor.shutdown(wait=False)
            self._executor = None

    @property
    def substrate(self) -> Dict[str, Any]:
        """Shared data substrate across surfaces."""
        return self._substrate

    @substrate.setter
    def substrate(self, value: Dict[str, Any]) -> None:
        self._substrate = value

    async def execute_with_timeout(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute code with timeout protection.

        Args:
            code: Source code to execute
            context: Optional execution context

        Returns:
            Dict with status, value/error message
        """
        try:
            result = await asyncio.wait_for(
                self.execute(code, context),
                timeout=self.timeout or float(os.getenv("EM_CUBED_TIMEOUT", "30"))
            )
            return result
        except asyncio.TimeoutError:
            logger.warning("Surface execution timed out", timeout=self.timeout)
            return {
                "status": "error",
                "message": f"Execution timed out after {self.timeout}s"
            }