"""Python surface integration for executing Python code with process isolation."""

import asyncio
import importlib.util
import os
import pickle
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, TimeoutError as FutureTimeoutError
from typing import Any

import structlog

from .base import SurfaceBase, _make_daemon_executor

logger = structlog.get_logger()

# Process pool singleton (lazy)
_PROCESS_POOL: ProcessPoolExecutor | None = None


def _get_process_pool(max_workers: int | None = None) -> ProcessPoolExecutor:
    """Lazily create and return a ProcessPoolExecutor using spawn context.

    We use a small pool to avoid the overhead of spawning per-eval while still
    isolating interpreter state between evaluations.
    """
    global _PROCESS_POOL
    if _PROCESS_POOL is None:
        workers = max_workers if max_workers is not None else max(1, min(4, (multiprocessing.cpu_count() or 1)))
        ctx = multiprocessing.get_context("spawn")
        _PROCESS_POOL = ProcessPoolExecutor(max_workers=workers, mp_context=ctx)
    return _PROCESS_POOL


def _raise_missing_builtin(name: str):
    raise RuntimeError(f"builtin {name} is not available in this environment")


def _ensure_asteval_builtins(aeval) -> None:
    """Ensure aeval has a usable __builtins__ mapping and compile available.

    This keeps asteval internals working while avoiding exposing dangerous
    top-level names.
    """
    try:
        import builtins as _builtins

        base = getattr(_builtins, "__dict__", _builtins.__dict__)

        if "__builtins__" not in aeval.symtable or not isinstance(aeval.symtable["__builtins__"], dict):
            aeval.symtable["__builtins__"] = base.copy()

        bmap = aeval.symtable["__builtins__"]

        for name in ("compile", "eval", "exec", "__import__", "open"):
            try:
                val = bmap.get(name)
                if not callable(val):
                    native = getattr(_builtins, name, None)
                    if callable(native):
                        bmap[name] = native
                    else:
                        # bind name into default param to avoid late-binding closure pitfall
                        bmap[name] = (lambda nm: (lambda *a, **k: _raise_missing_builtin(nm)))(name)
            except Exception:
                native = getattr(_builtins, name, None)
                if callable(native):
                    bmap[name] = native
                else:
                    bmap[name] = (lambda nm: (lambda *a, **k: _raise_missing_builtin(nm)))(name)

        problematic = [n for n in ("compile", "eval", "exec", "__import__", "open") if not callable(bmap.get(n))]
        if problematic:
            logger.error("asteval builtins fallback left non-callable entries", problematic=problematic)
            for name in problematic:
                bmap[name] = (lambda nm: (lambda *a, **k: _raise_missing_builtin(nm)))(name)

    except Exception as _e:
        logger.exception("Failed to ensure builtins for asteval", error=str(_e))


def _child_eval(code: str, context: dict | None) -> dict[str, Any]:
    """Evaluate code inside a child process using asteval and return a serializable result dict.

    This function is executed in a separate process so it must not close over
    unpicklable state.
    """
    try:
        from asteval import Interpreter

        aeval = Interpreter(excluded_symbols=["open", "__import__", "eval", "exec"])
        for bad in ["open", "__import__", "eval", "exec"]:
            aeval.symtable.pop(bad, None)

        _ensure_asteval_builtins(aeval)

        if context:
            # Only copy simple mapping entries; user is responsible for picklable context
            for k, v in (context.items() if isinstance(context, dict) else ()):
                aeval.symtable[k] = v
            aeval.symtable["context"] = context

        result = aeval(code)
        if result is None and "result" in aeval.symtable and aeval.symtable["result"] is not None:
            result = aeval.symtable["result"]

        if aeval.error:
            try:
                details = [getattr(e, "msg", repr(e)) for e in aeval.error]
            except Exception:
                details = [repr(e) for e in aeval.error]
            return {"status": "error", "message": details[0] if details else "asteval error", "aeval_errors": details}

        return {"status": "ok", "value": result}

    except Exception as e:
        # Return stringified exception to the caller
        return {"status": "error", "message": str(e)}


class PythonSurface(SurfaceBase):
    """Handle Python code execution and metadata extraction."""

    @property
    def name(self) -> str:
        return "python"

    @property
    def description(self) -> str:
        return "Safe Python execution with asteval"

    @property
    def available(self) -> bool:
        return self._check_availability()

    def __init__(self, timeout: float | None = None):
        super().__init__(timeout)
        worker_count = self._worker_count()
        # keep a thread executor for non-asteval tasks; asteval runs in process pool
        self._executor = _make_daemon_executor(max_workers=worker_count)
        self._concurrency_limit = int(os.getenv("EM_CUBED_PYTHON_SURFACE_MAX_CONCURRENCY", str(worker_count)))
        logger.info("PythonSurface initialized", available=self.available, timeout=self.timeout, workers=worker_count)

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

        fns = re.findall(r"^\s*def\s+([a-zA-Z][a-zA-Z0-9_]*)\s*\(", python_source, re.MULTILINE)
        return list(dict.fromkeys(fns))

    async def _execute_impl(self, code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute Python code safely using an isolated process pool for asteval."""
        if not self.available:
            return {"status": "error", "message": f"{self.name} surface not available"}

        # Ensure context is serializable for process execution
        try:
            pickle.dumps(context)
        except Exception:
            return {"status": "error", "message": "context must be serializable for process-isolated execution"}

        pool = _get_process_pool(max_workers=self._worker_count())
        future = pool.submit(_child_eval, code, context)
        timeout = self.timeout if self.timeout is not None else 5.0

        loop = asyncio.get_running_loop()

        try:
            # Wait for result in a thread to avoid blocking the event loop
            result = await loop.run_in_executor(None, lambda: future.result(timeout=timeout))
            return result
        except FutureTimeoutError:
            future.cancel()
            return {"status": "error", "message": "execution timed out"}
        except Exception as e:
            # future.result can raise exceptions if the child process returned an error dict
            try:
                if future.done():
                    val = future.result()
                    return val
            except Exception:
                pass
            return {"status": "error", "message": str(e)}

    def _run_code(self, code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Run asteval code synchronously using the process pool."""
        logger.info("Executing Python code", code_length=len(code), has_context=context is not None)

        if not self.available:
            logger.error("Attempted Python execution but asteval not available")
            return {"status": "error", "message": "asteval not available"}

        # Ensure context is serializable
        try:
            pickle.dumps(context)
        except Exception:
            return {"status": "error", "message": "context must be serializable for process-isolated execution"}

        pool = _get_process_pool(max_workers=self._worker_count())
        future = pool.submit(_child_eval, code, context)
        timeout = self.timeout if self.timeout is not None else 5.0

        try:
            result = future.result(timeout=timeout)
            return result
        except FutureTimeoutError:
            future.cancel()
            return {"status": "error", "message": "execution timed out"}
        except Exception as e:
            try:
                if future.done():
                    return future.result()
            except Exception:
                pass
            logger.exception("Python execution failed", error=str(e), code=code)
            return {"status": "error", "message": str(e)}

    async def health(self) -> bool:
        """Check if the surface is available."""
        return bool(self.available)
