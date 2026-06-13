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

# Lock protecting the temporary threading.Thread monkey-patch in _make_daemon_executor.
# Without this, two surfaces initialising concurrently race on the global symbol.
_executor_init_lock = threading.Lock()


def _make_daemon_executor(max_workers: int = 1) -> ThreadPoolExecutor:
    """Create a ThreadPoolExecutor whose worker threads are daemons.
    This prevents them from keeping the Python process alive after tests/CI complete.
    """
    original_thread = threading.Thread

    def _daemon_thread(*args, **kwargs):
        kwargs.setdefault("daemon", True)
        return original_thread(*args, **kwargs)

    # Serialise the global monkey-patch so concurrent surface inits don't race.
    with _executor_init_lock:
        threading.Thread = _daemon_thread  # type: ignore[assignment, misc]
        try:
            return ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="SurfaceExec-")
        finally:
            threading.Thread = original_thread  # type: ignore[assignment, misc]




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
        self._executor = _make_daemon_executor(max_workers=1)
        self._concurrency_limit = int(os.getenv("EM_CUBED_SURFACE_MAX_CONCURRENCY", "0"))
        self._concurrency_semaphore = asyncio.Semaphore(self._concurrency_limit) if self._concurrency_limit > 0 else None
        self._rejected_executions = 0

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

    async def _acquire_execution_slot(self) -> bool:
        if self._concurrency_semaphore is None:
            return True
        if self._concurrency_semaphore.locked():
            self._rejected_executions += 1
            logger.warning(
                "Surface execution rejected by concurrency limiter",
                surface=self.name,
                limit=self._concurrency_limit,
            )
            return False
        await self._concurrency_semaphore.acquire()
        return True

    def _release_execution_slot(self) -> None:
        if self._concurrency_semaphore is not None:
            self._concurrency_semaphore.release()

    async def execute_with_timeout(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute code with timeout protection.

        Args:
            code: Source code to execute
            context: Optional execution context

        Returns:
            Dict with status, value/error message
        """
        if not await self._acquire_execution_slot():
            return {
                "status": "error",
                "message": f"Surface execution rejected: concurrency limit {self._concurrency_limit} reached"
            }
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
        finally:
            self._release_execution_slot()

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