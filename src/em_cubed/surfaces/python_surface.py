"""Python surface integration for executing Python code."""

import asyncio
import importlib.util
import os
from typing import Any

import structlog

from .base import SurfaceBase, _make_daemon_executor

logger = structlog.get_logger()


def _ensure_asteval_builtins(aeval) -> None:
    """Ensure aeval has a usable __builtins__ mapping and compile available.

    This is defensive: asteval internals expect a mapping under __builtins__ and
    access to compile for AST handling (f-strings / JoinedStr nodes). We do not
    expose dangerous names at the top-level symtable (open, __import__, eval, exec).
    """
    try:
        import builtins as _builtins

        # Use the builtins mapping as a base (copy to avoid mutating global builtins)
        base = getattr(_builtins, "__dict__", _builtins.__dict__)

        # Ensure __builtins__ is present and is a dict mapping for asteval internals
        if "__builtins__" not in aeval.symtable or not isinstance(aeval.symtable["__builtins__"], dict):
            aeval.symtable["__builtins__"] = base.copy()

        bmap = aeval.symtable["__builtins__"]

        # Ensure critical callables are present and callable. If missing or not callable,
        # restore them from the real builtins module. This keeps asteval internals working
        # while not adding these names to the top-level symtable.
        for name in ("compile", "eval", "exec", "__import__", "open"):
            try:
                val = bmap.get(name)
                if not callable(val):
                    native = getattr(_builtins, name, None)
                    if callable(native):
                        bmap[name] = native
                    else:
                        # last resort: set to a simple wrapper that raises if called
                        bmap[name] = lambda *a, **k: (_raise_missing_builtin(name))
            except Exception:
                # Keep going — diagnostics will capture the state if something is wrong.
                continue
    except Exception as _e:
        # Fail-open for diagnostics — we'll still surface errors from aeval.error below.
        logger.debug("Failed to ensure builtins for asteval", exc=str(_e))


def _raise_missing_builtin(name: str):
    raise RuntimeError(f"builtin {name} is not available in this environment")


def _run_asteval_code(code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    from asteval import Interpreter

    # Keep asteval internals available — only remove dangerous top-level names.
    aeval = Interpreter(excluded_symbols=["open", "__import__", "eval", "exec"])
    for bad in ["open", "__import__", "eval", "exec"]:
        aeval.symtable.pop(bad, None)

    # Defensive guarantee for interpreter internals
    _ensure_asteval_builtins(aeval)

    if context:
        for key, value in context.items():
            aeval.symtable[key] = value
        aeval.symtable["context"] = context

    result = aeval(code)
    if result is None and "result" in aeval.symtable and aeval.symtable["result"] is not None:
        result = aeval.symtable["result"]

    if aeval.error:
        # Log full error object for diagnostics
        try:
            details = [getattr(e, "msg", repr(e)) for e in aeval.error]
        except Exception:
            details = [repr(e) for e in aeval.error]
        # Additional snapshot for diagnostics
        try:
            builtins_snapshot = {}
            bmap = aeval.symtable.get("__builtins__", {})
            for name in ("compile", "eval", "exec", "__import__", "open"):
                builtins_snapshot[name] = {
                    "present": name in bmap,
                    "callable": callable(bmap.get(name)),
                    "repr": repr(bmap.get(name))[:200],
                }
            snapshot = {
                "aeval_keys": list(aeval.symtable.keys()),
                "has_builtins": "__builtins__" in aeval.symtable,
                "builtins_snapshot": builtins_snapshot,
            }
        except Exception:
            snapshot = {}
        logger.info("Python execution failed with error", errors=details, snapshot=snapshot)
        return {"status": "error", "message": details[0] if details else "asteval error"}

    logger.info("Python execution successful")
    return {"status": "ok", "value": result}


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
        """Execute Python code safely using asteval."""
        if not self.available:
            return {"status": "error", "message": f"{self.name} surface not available"}
        loop = asyncio.get_running_loop()
        future = loop.run_in_executor(self._executor, _run_asteval_code, code, context)
        try:
            return await future
        except (TimeoutError, asyncio.CancelledError):
            if self._executor is not None:
                self._executor.shutdown(wait=False)
            self._executor = _make_daemon_executor(max_workers=self._worker_count())
            raise

    def _run_code(self, code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Run asteval code synchronously in the executor thread."""
        logger.info("Executing Python code", code_length=len(code), has_context=context is not None)

        if not self.available:
            logger.error("Attempted Python execution but asteval not available")
            return {"status": "error", "message": "asteval not available"}

        try:
            from asteval import Interpreter

            # Keep asteval internals available — only remove dangerous top-level names.
            aeval = Interpreter(excluded_symbols=["open", "__import__", "eval", "exec"])
            for bad in ["open", "__import__", "eval", "exec"]:
                aeval.symtable.pop(bad, None)

            # Defensive guarantee for interpreter internals
            _ensure_asteval_builtins(aeval)

            if context:
                for key, value in context.items():
                    aeval.symtable[key] = value
                aeval.symtable["context"] = context

            result = aeval(code)
            if result is None and "result" in aeval.symtable and aeval.symtable["result"] is not None:
                result = aeval.symtable["result"]

            if aeval.error:
                # Log full error object for diagnostics
                try:
                    details = [getattr(e, "msg", repr(e)) for e in aeval.error]
                except Exception:
                    details = [repr(e) for e in aeval.error]
                try:
                    builtins_snapshot = {}
                    bmap = aeval.symtable.get("__builtins__", {})
                    for name in ("compile", "eval", "exec", "__import__", "open"):
                        builtins_snapshot[name] = {
                            "present": name in bmap,
                            "callable": callable(bmap.get(name)),
                            "repr": repr(bmap.get(name))[:200],
                        }
                    snapshot = {
                        "aeval_keys": list(aeval.symtable.keys()),
                        "has_builtins": "__builtins__" in aeval.symtable,
                        "builtins_snapshot": builtins_snapshot,
                    }
                except Exception:
                    snapshot = {}
                logger.info("Python execution failed with error", errors=details, snapshot=snapshot)
                return {"status": "error", "message": details[0] if details else "asteval error"}

            logger.info("Python execution successful")
            return {"status": "ok", "value": result}

        except Exception as e:
            logger.exception("Python execution failed", error=str(e), code=code)
            return {"status": "error", "message": str(e)}

    async def health(self) -> bool:
        """Check if the surface is available."""
        return bool(self.available)
