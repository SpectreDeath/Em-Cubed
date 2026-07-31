"""Python surface integration for executing Python code."""

import asyncio
import importlib.util
import os
from typing import Any

import structlog

from .base import SurfaceBase, _make_daemon_executor

logger = structlog.get_logger()


def _run_asteval_code(code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    from asteval import Interpreter

    aeval = Interpreter(excluded_symbols=["open", "__import__", "eval", "exec", "compile", "__builtins__"])
    for bad in ["open", "__import__", "eval", "exec", "compile", "__builtins__"]:
        aeval.symtable.pop(bad, None)

    if context:
        for key, value in context.items():
            aeval.symtable[key] = value
        aeval.symtable["context"] = context

    result = aeval(code)
    if result is None and "result" in aeval.symtable and aeval.symtable["result"] is not None:
        result = aeval.symtable["result"]

    if aeval.error:
        error_msg = str(aeval.error[0].msg) if hasattr(aeval.error[0], "msg") else str(aeval.error[0])
        logger.info("Python execution failed with error", error=error_msg)
        return {"status": "error", "message": error_msg}

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
        return await asyncio.shield(future)

    def _run_code(self, code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Run asteval code synchronously in the executor thread."""
        logger.info("Executing Python code", code_length=len(code), has_context=context is not None)

        if not self.available:
            logger.error("Attempted Python execution but asteval not available")
            return {"status": "error", "message": "asteval not available"}

        try:
            from asteval import Interpreter

            aeval = Interpreter(excluded_symbols=["open", "__import__", "eval", "exec", "compile", "__builtins__"])
            for bad in ["open", "__import__", "eval", "exec", "compile", "__builtins__"]:
                aeval.symtable.pop(bad, None)

            if context:
                for key, value in context.items():
                    aeval.symtable[key] = value
                aeval.symtable["context"] = context

            result = aeval(code)
            if result is None and "result" in aeval.symtable and aeval.symtable["result"] is not None:
                result = aeval.symtable["result"]

            if aeval.error:
                if aeval.error and hasattr(aeval.error[0], "msg"):
                    error_msg = str(aeval.error[0].msg)
                else:
                    error_msg = str(aeval.error[0]) if aeval.error else "Unknown error"
                logger.info("Python execution failed with error", error=error_msg)
                return {"status": "error", "message": error_msg}

            logger.info("Python execution successful")
            return {"status": "ok", "value": result}

        except Exception as e:
            logger.exception("Python execution failed", error=str(e), code=code)
            return {"status": "error", "message": str(e)}

    async def health(self) -> bool:
        """Check if the surface is available."""
        return bool(self.available)