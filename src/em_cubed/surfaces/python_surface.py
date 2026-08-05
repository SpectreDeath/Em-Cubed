"""Python surface integration for executing Python code.

Security model
--------------
Code is evaluated inside a restricted asteval Interpreter that uses a
**pop-then-wrap** strategy to sandbox dangerous builtins:

  1. All symbols in ``_BLOCKED_SYMBOLS`` are removed from the symtable.
  2. Each is re-installed as a RuntimeError-raising wrapper, so explicit
     calls produce a controlled ``{"status": "error", ...}`` response.

Thread-based isolation (default, ``execute``)
     The existing ``ThreadPoolExecutor`` is used for all async evaluations.
     Timeout is enforced by ``asyncio.wait_for`` at the ``execute_with_timeout``
     level (advisory — the thread may continue to completion but the caller
     gets the timeout error immediately).  This is safe for the common case
     because:
       - asteval cannot import OS modules (sandbox blocks them).
       - asteval evaluates pure Python expressions, not shell commands.

Process-based isolation (opt-in, ``run_isolated_eval``)
     A fresh ``multiprocessing.spawn`` child is used for strong isolation.
     The child is unconditionally ``terminate()``-d on timeout, guaranteeing
     no resource leak.  Use this for untrusted/unknown code.

     NOTE: on Windows, spawning from a *thread* (run_in_executor) can hit
     ``[WinError 6]`` handle-inheritance failures.  ``run_isolated_eval``
     therefore should be called from the *main thread* or a properly set-up
     thread context, not from inside ``loop.run_in_executor``.
"""

import asyncio
import importlib.util
import logging
import multiprocessing
import os
from typing import Any

import structlog

from .base import SurfaceBase, _make_daemon_executor

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# Symbols to block inside the asteval sandbox.
# ---------------------------------------------------------------------------
_BLOCKED_SYMBOLS: list[str] = [
    "open",
    "__import__",
    "eval",
    "exec",
    "compile",
    "__builtins__",
    "breakpoint",
    "input",
]

# Subset of _BLOCKED_SYMBOLS for which we install callable wrappers.
# "__builtins__" is NOT in this list — it is set to {} (empty dict) so that
# asteval's internal ``name in symtable["__builtins__"]`` checks don't raise
# ``TypeError: argument of type 'function' is not iterable``.
_CALLABLE_BLOCKED: list[str] = [
    "open",
    "__import__",
    "eval",
    "exec",
    "compile",
    "breakpoint",
    "input",
]


def _missing_builtin_func(name: str) -> Any:
    """Return a callable that raises RuntimeError when invoked."""

    def _blocked(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError(f"'{name}' is not available in the sandboxed environment")

    _blocked.__name__ = name
    return _blocked


def _build_restricted_interpreter(context: dict[str, Any] | None = None) -> Any:
    """Create an asteval Interpreter with dangerous symbols removed.

    Strategy (validated against asteval 1.0.9 with ``multiprocessing.spawn``):
      1. Create a standard ``Interpreter()``.
      2. Pop every blocked symbol from the symtable.
      3. Set ``__builtins__`` to an empty dict so internal ``name in __builtins__``
         checks in asteval remain safe (a function value would cause TypeError).
      4. Install RuntimeError-raising wrappers for callable blocked symbols.
      5. Inject caller-supplied context variables.
    """
    from asteval import Interpreter

    aeval = Interpreter()

    # Step 1: remove all dangerous symbols.
    for bad in _BLOCKED_SYMBOLS:
        aeval.symtable.pop(bad, None)

    # Step 2: set __builtins__ to empty dict (not a function!) so asteval's
    # internal iteration checks don't raise TypeError.
    aeval.symtable["__builtins__"] = {}

    # Step 3: install blocking wrappers for callable symbols only.
    for bad in _CALLABLE_BLOCKED:
        aeval.symtable[bad] = _missing_builtin_func(bad)

    # Step 4: inject context.
    if context:
        for key, value in context.items():
            aeval.symtable[key] = value
        aeval.symtable["context"] = context

    return aeval


def _run_asteval_in_thread(code: str, context: dict[str, Any] | None) -> dict[str, Any]:
    """Run restricted asteval evaluation in the current thread.

    Used by ``_execute_impl`` (async path with ThreadPoolExecutor).
    This is safe because the sandbox blocks all dangerous builtins.
    """
    try:
        aeval = _build_restricted_interpreter(context)
        result = aeval(code)

        if result is None and "result" in aeval.symtable and aeval.symtable["result"] is not None:
            result = aeval.symtable["result"]

        if aeval.error:
            error_msg = (
                str(aeval.error[0].msg)
                if hasattr(aeval.error[0], "msg")
                else str(aeval.error[0])
            )
            return {"status": "error", "message": error_msg}

        return {"status": "ok", "value": result}

    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": str(exc)}


# ---------------------------------------------------------------------------
# Per-eval process isolation (opt-in, for untrusted/unknown code).
# WARNING: on Windows, only call this from the main thread — spawning from
# a worker thread via run_in_executor causes [WinError 6] handle errors.
# ---------------------------------------------------------------------------

def _child_eval_runner(
    code: str,
    context: dict[str, Any] | None,
    out_q: "multiprocessing.Queue[dict[str, Any]]",
) -> None:
    """Entry point for the isolated child process.

    Must be a module-level function so it is importable by the spawned subprocess.
    """
    logging.basicConfig(level=logging.DEBUG)
    child_logger = logging.getLogger(__name__)

    try:
        aeval = _build_restricted_interpreter(context)

        # Builtins snapshot — key diagnostic when CI logs "name 'X' is not defined".
        raw_builtins = aeval.symtable.get("__builtins__")
        builtins_dict = raw_builtins if isinstance(raw_builtins, dict) else {}
        snapshot = {
            name: {
                "present": name in builtins_dict,
                "callable": callable(builtins_dict.get(name)),
            }
            for name in ("compile", "eval", "exec", "__import__", "open")
        }
        child_logger.debug(
            "builtins_snapshot pid=%d snapshot=%s", os.getpid(), snapshot
        )

        result = aeval(code)

        if result is None and "result" in aeval.symtable and aeval.symtable["result"] is not None:
            result = aeval.symtable["result"]

        if aeval.error:
            error_msg = (
                str(aeval.error[0].msg)
                if hasattr(aeval.error[0], "msg")
                else str(aeval.error[0])
            )
            out_q.put({"status": "error", "message": error_msg})
            return

        out_q.put({"status": "ok", "value": result})

    except Exception as exc:  # noqa: BLE001
        out_q.put({"status": "error", "message": str(exc)})


def run_isolated_eval(
    code: str,
    context: dict[str, Any] | None,
    timeout: float,
) -> dict[str, Any]:
    """Run *code* in a freshly spawned child process with a hard timeout.

    Uses ``multiprocessing.get_context("spawn")`` — the only portable context
    on Windows and the safest on all platforms (avoids fork+thread deadlocks).
    The child is unconditionally terminated if still alive after *timeout* seconds.

    .. warning::
        On Windows, call this only from the **main thread**.  Calling from a
        worker thread (e.g., via ``loop.run_in_executor``) causes
        ``[WinError 6] The handle is invalid`` errors during handle inheritance.
    """
    ctx = multiprocessing.get_context("spawn")
    q: multiprocessing.Queue[dict[str, Any]] = ctx.Queue()
    p = ctx.Process(target=_child_eval_runner, args=(code, context, q))
    p.start()
    p.join(timeout)

    if p.is_alive():
        p.terminate()
        p.join(2)  # give OS up to 2 s to reap the process
        if p.is_alive():
            p.kill()
            p.join(1)
        return {"status": "error", "message": f"Execution timed out after {timeout}s"}

    try:
        return q.get_nowait()
    except Exception:  # noqa: BLE001
        exit_code = p.exitcode
        return {
            "status": "error",
            "message": f"No result from child process (exit code: {exit_code})",
        }


class PythonSurface(SurfaceBase):
    """Handle Python code execution and metadata extraction."""

    @property
    def name(self) -> str:
        return "python"

    @property
    def description(self) -> str:
        return "Safe Python execution with asteval (sandboxed builtins)"

    @property
    def available(self) -> bool:
        return self._check_availability()

    def __init__(self, timeout: float | None = None):
        super().__init__(timeout)
        worker_count = self._worker_count()
        self._executor = _make_daemon_executor(max_workers=worker_count)
        self._concurrency_limit = int(
            os.getenv("EM_CUBED_PYTHON_SURFACE_MAX_CONCURRENCY", str(worker_count))
        )
        logger.info(
            "PythonSurface initialized",
            available=self.available,
            timeout=self.timeout,
            workers=worker_count,
        )

    @staticmethod
    def _worker_count() -> int:
        try:
            return max(1, int(os.getenv("EM_CUBED_PYTHON_SURFACE_WORKERS", "4")))
        except ValueError:
            return 4

    def _check_availability(self) -> bool:
        """Check if asteval is available."""
        available = importlib.util.find_spec("asteval") is not None
        if not available:
            logger.warning("asteval not available for Python surface")
        return available

    @staticmethod
    def extract_tags(python_source: str | None) -> list:
        """Extract function names from Python source as heuristic_tags."""
        if not python_source:
            return []
        import re

        fns = re.findall(
            r"^\s*def\s+([a-zA-Z][a-zA-Z0-9_]*)\s*\(", python_source, re.MULTILINE
        )
        return list(dict.fromkeys(fns))

    async def _execute_impl(
        self, code: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Execute Python code with sandboxed builtins in a thread executor.

        Uses thread-based execution (not process isolation) so that it can be
        safely called from async contexts on all platforms including Windows.
        The sandbox is enforced by ``_build_restricted_interpreter`` which
        removes and wraps all dangerous builtins before execution.
        """
        if not self.available:
            return {"status": "error", "message": f"{self.name} surface not available"}
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            _run_asteval_in_thread,
            code,
            context,
        )

    def _run_code(self, code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Run restricted evaluation synchronously (for non-async callers)."""
        logger.info(
            "Executing Python code",
            code_length=len(code),
            has_context=context is not None,
        )
        if not self.available:
            logger.error("Attempted Python execution but asteval not available")
            return {"status": "error", "message": "asteval not available"}
        return _run_asteval_in_thread(code, context)

    async def health(self) -> bool:
        """Check if the surface is available."""
        return bool(self.available)
