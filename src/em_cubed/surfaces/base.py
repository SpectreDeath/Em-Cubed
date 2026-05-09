"""Base class for surface plugins with timeout support."""
import asyncio
import os
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Optional
import structlog

logger = structlog.get_logger()


class SurfaceTimeoutError(Exception):
    """Raised when a surface operation times out."""
    pass


from ..plugin import SurfacePlugin

class SurfaceBase(SurfacePlugin, ABC):
    """Base class for all execution surfaces with timeout support."""

    def __init__(self, timeout: Optional[float] = None):
        """Initialize surface with optional timeout.

        Args:
            timeout: Maximum execution time in seconds.
                    Defaults to EM_CUBED_TIMEOUT env var or 30 seconds.
        """
        self.timeout = timeout or float(os.getenv("EM_CUBED_TIMEOUT", "30"))
        self._executor = ThreadPoolExecutor(max_workers=1)

    def initialize(self) -> None:
        """Initialize the surface. Subclasses can override this."""
        pass

    def shutdown(self) -> None:
        """Shutdown the surface. Subclasses can override this."""
        pass

    def __del__(self):
        """Clean up executor on deletion."""
        if hasattr(self, "_executor"):
            self._executor.shutdown(wait=False)

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
                self._execute_impl(code, context),
                timeout=self.timeout
            )
            return result
        except asyncio.TimeoutError:
            logger.warning("Surface execution timed out", timeout=self.timeout)
            return {
                "status": "error",
                "message": f"Execution timed out after {self.timeout}s"
            }

    @abstractmethod
    async def _execute_impl(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute code - implemented by subclasses.

        Args:
            code: Source code to execute
            context: Optional execution context

        Returns:
            Dict with status, value/error message
        """
        pass

    @abstractmethod
    async def health(self) -> bool:
        """Check if surface is available.

        Returns:
            True if surface is operational
        """
        pass

    @abstractmethod
    def extract_tags(self, source: Optional[str]) -> list:
        """Extract relevant tags from source code.

        Args:
            source: Source code string

        Returns:
            List of tag strings
        """
        pass