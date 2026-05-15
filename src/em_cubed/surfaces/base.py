"""Base class for surface plugins with timeout support."""
import asyncio
import os
from abc import ABC, abstractmethod
from ..plugin import SurfacePlugin
from concurrent.futures import ThreadPoolExecutor
import threading
from typing import Any, Dict, Optional
import structlog

logger = structlog.get_logger()


class _DaemonThreadPoolExecutor(ThreadPoolExecutor):
    """ThreadPoolExecutor that creates daemon threads so they don't block shutdown."""

    _counter = 0

    def __init__(self, max_workers=1):
        super().__init__(max_workers=max_workers)

    def _adjust_thread_count(self):
        # When threads are terminated, spawn new ones if needed
        if self._work_queue and not self._threads:
            self._spawn_thread()

    def _spawn_thread(self):
        """Spawn a new daemon thread."""
        _DaemonThreadPoolExecutor._counter += 1
        t = threading.Thread(
            target=self._worker,
            name=f"DaemonPool-{_DaemonThreadPoolExecutor._counter}",
            daemon=True
        )
        self._threads.add(t)
        t.start()

    def shutdown(self, wait=True, *, cancel_futures=False):
        super().shutdown(wait=False, cancel_futures=cancel_futures)




class SurfaceTimeoutError(Exception):
    """Raised when a surface operation times out."""
    pass



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

    def execute_sync(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Synchronous version of execute for use in non-async contexts."""
        try:
            try:
                asyncio.get_running_loop()
                # We are in a thread where a loop is already running
                # Create a new loop for this synchronous call
                new_loop = asyncio.new_event_loop()
                try:
                    return new_loop.run_until_complete(self.execute(code, context))
                finally:
                    new_loop.close()
            except RuntimeError:
                # No event loop in this thread, use asyncio.run
                return asyncio.run(self.execute(code, context))
        except Exception as e:
            return {"status": "error", "message": str(e)}

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