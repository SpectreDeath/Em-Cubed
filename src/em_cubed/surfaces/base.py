"""Base class for surface plugins with timeout support."""

import asyncio
import os
import threading
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import structlog

from ..plugin import SurfacePlugin

logger = structlog.get_logger()

# Lock protecting the temporary threading.Thread monkey-patch in DaemonThreadPoolExecutor.
_executor_init_lock = threading.Lock()


class DaemonThreadPoolExecutor(ThreadPoolExecutor):
    """ThreadPoolExecutor that spawns daemon threads."""

    def _adjust_thread_count(self) -> None:
        original_thread = threading.Thread

        def _daemon_thread(*args: Any, **kwargs: Any) -> threading.Thread:
            kwargs.setdefault("daemon", True)
            return original_thread(*args, **kwargs)

        with _executor_init_lock:
            threading.Thread = _daemon_thread  # type: ignore[assignment, misc]
            try:
                super()._adjust_thread_count()
            finally:
                threading.Thread = original_thread  # type: ignore[assignment, misc]


def _make_daemon_executor(max_workers: int = 1) -> ThreadPoolExecutor:
    """Create a ThreadPoolExecutor whose worker threads are daemons.
    This prevents them from keeping the Python process alive after tests/CI complete.
    """
    return DaemonThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="SurfaceExec-")


class SurfaceTimeoutError(Exception):
    """Raised when a surface operation times out."""


# ---------------------------------------------------------------------------
# Shared asteval sandbox builder
# ---------------------------------------------------------------------------

#: Symbols removed from the asteval symtable and replaced with error stubs.
BLOCKED_SYMBOLS: list[str] = [
    "open",
    "__import__",
    "eval",
    "exec",
    "compile",
    "__builtins__",
    "breakpoint",
    "input",
]

#: Subset of BLOCKED_SYMBOLS that get callable wrapper stubs (not ``{}``).
CALLABLE_BLOCKED: list[str] = [
    "open",
    "__import__",
    "eval",
    "exec",
    "compile",
    "breakpoint",
    "input",
]


def _make_blocked_callable(name: str):  # type: ignore[return]
    """Return a callable that raises RuntimeError when invoked.

    Installed as a replacement for dangerous builtins inside asteval interpreters.
    """
    def _blocked(*args, **kwargs):  # type: ignore[return]
        raise RuntimeError(f"'{name}' is not available in the sandboxed environment")
    _blocked.__name__ = name
    return _blocked


def make_sandboxed_interpreter(extra_blocked: list[str] | None = None):
    """Create a restricted ``asteval.Interpreter`` with dangerous builtins removed.

    Parameters
    ----------
    extra_blocked:
        Additional symbol names to block beyond the shared ``BLOCKED_SYMBOLS``
        list.  Useful for surface-specific restrictions.

    Returns
    -------
    asteval.Interpreter | None
        A sandboxed interpreter, or ``None`` if ``asteval`` is not installed.
    """
    try:
        import asteval  # type: ignore[import-untyped]
    except ImportError:
        return None

    interp = asteval.Interpreter()
    all_blocked = list(BLOCKED_SYMBOLS) + (extra_blocked or [])

    for sym in all_blocked:
        interp.symtable.pop(sym, None)

    for sym in CALLABLE_BLOCKED + (extra_blocked or []):
        if sym != "__builtins__":
            interp.symtable[sym] = _make_blocked_callable(sym)

    # asteval checks ``"__builtins__" in symtable`` — set to {} not a callable.
    interp.symtable["__builtins__"] = {}

    return interp


class SurfaceBase(SurfacePlugin, ABC):
    """Base class for all execution surfaces with timeout support."""

    def __init__(self, timeout: float | None = None):
        """Initialize surface with optional timeout.

        Args:
            timeout: Maximum execution time in seconds.
                    Defaults to EM_CUBED_TIMEOUT env var or 30 seconds.
        """
        if timeout is not None:
            self.timeout = float(timeout)
        else:
            default_t = "5.0" if (os.getenv("PYTEST_CURRENT_TEST") or os.getenv("CI")) else "10.0"
            self.timeout = float(os.getenv("EM_CUBED_TIMEOUT", default_t))


        self._executor = _make_daemon_executor(max_workers=1)
        self._concurrency_limit = int(os.getenv("EM_CUBED_SURFACE_MAX_CONCURRENCY", "0"))
        self._concurrency_semaphore: asyncio.Semaphore | None = None
        self._semaphore_loop: asyncio.AbstractEventLoop | None = None
        self._rejected_executions = 0

    def initialize(self) -> None:
        """Initialize the surface. Subclasses can override this."""

    def shutdown(self) -> None:
        """Shutdown the surface. Subclasses can override this."""

    def __del__(self):
        """Clean up executor on deletion."""
        if hasattr(self, "_executor"):
            self._executor.shutdown(wait=False)

    def _get_semaphore(self) -> asyncio.Semaphore | None:
        if self._concurrency_limit <= 0:
            return None
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            return None

        if (
            self._concurrency_semaphore is None
            or self._semaphore_loop is not current_loop
            or self._semaphore_loop.is_closed()
        ):
            self._semaphore_loop = current_loop
            self._concurrency_semaphore = asyncio.Semaphore(self._concurrency_limit)
        return self._concurrency_semaphore

    async def _acquire_execution_slot(self) -> bool:
        semaphore = self._get_semaphore()
        if semaphore is None:
            return True
        if semaphore.locked():
            self._rejected_executions += 1
            logger.warning(
                "Surface execution rejected by concurrency limiter",
                surface=self.name,
                limit=self._concurrency_limit,
            )
            return False
        await semaphore.acquire()
        return True

    def _release_execution_slot(self) -> None:
        semaphore = getattr(self, "_concurrency_semaphore", None)
        if semaphore is not None:
            try:
                semaphore.release()
            except ValueError:
                pass

    async def execute(self, code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute code with timeout and concurrency slot protection.

        Fulfills the SurfacePlugin abstract execute() interface by delegating
        to execute_with_timeout(), which invokes subclass _execute_impl().
        """
        return await self.execute_with_timeout(code, context)

    async def execute_with_timeout(self, code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
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
                "message": f"Surface execution rejected: concurrency limit {self._concurrency_limit} reached",
            }
        try:
            result = await asyncio.wait_for(self._execute_impl(code, context), timeout=self.timeout)
            return result
        except (asyncio.TimeoutError, TimeoutError):
            logger.warning("Surface execution timed out", timeout=self.timeout)
            return {"status": "error", "message": f"Execution timed out after {self.timeout}s"}
        finally:
            self._release_execution_slot()

    def execute_sync(self, code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
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
    async def _execute_impl(self, code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute code - implemented by subclasses.

        Args:
            code: Source code to execute
            context: Optional execution context

        Returns:
            Dict with status, value/error message
        """

    @abstractmethod
    async def health(self) -> bool:
        """Check if surface is available.

        Returns:
            True if surface is operational
        """

    @abstractmethod
    def extract_tags(self, source: str | None) -> list:
        """Extract relevant tags from source code.

        Args:
            source: Source code string

        Returns:
            List of tag strings
        """
