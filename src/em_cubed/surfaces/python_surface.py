"""Python surface integration for executing Python code."""

import asyncio
import importlib.util
import os
import pickle
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, Any, Optional
import structlog

from .base import SurfaceBase, _make_daemon_executor

logger = structlog.get_logger()


def _run_asteval_code(code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    from asteval import Interpreter

    aeval = Interpreter(excluded_symbols=['open', '__import__', 'eval', 'exec', 'compile', '__builtins__'])
    for bad in ['open', '__import__', 'eval', 'exec', 'compile', '__builtins__']:
        aeval.symtable.pop(bad, None)

    if context:
        for key, value in context.items():
            aeval.symtable[key] = value
        aeval.symtable["context"] = context

    result = aeval(code)

    if aeval.error:
        error_msg = str(aeval.error[0].msg) if hasattr(aeval.error[0], "msg") else str(aeval.error[0])
        logger.info("Python execution failed with error", error=error_msg)
        return {"status": "error", "message": error_msg}

    logger.info("Python execution successful")
    return {"status": "ok", "value": result}


def _is_picklable(value: Any) -> bool:
    try:
        pickle.dumps(value)
        return True
    except Exception:
        return False


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

    def __init__(self, timeout: Optional[float] = None):
        super().__init__(timeout)
        worker_count = self._worker_count()
        self._executor = _make_daemon_executor(max_workers=worker_count)
        self._process_executor = ProcessPoolExecutor(max_workers=worker_count)
        self._concurrency_limit = int(os.getenv("EM_CUBED_PYTHON_SURFACE_MAX_CONCURRENCY", str(worker_count)))
        self._concurrency_semaphore = asyncio.Semaphore(self._concurrency_limit) if self._concurrency_limit > 0 else None
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
    def extract_tags(python_source: Optional[str]) -> list:
        """Extract function names from Python source as heuristic_tags."""
        if not python_source:
            return []
        import re

        fns = re.findall(r"^\s*def\s+([a-zA-Z][a-zA-Z0-9_]*)\s*\(", python_source, re.MULTILINE)
        return list(dict.fromkeys(fns))

    async def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.available:
            return {
                "status": "error",
                "message": f"{self.name} surface not available"
            }
        if not await self._acquire_execution_slot():
            return {
                "status": "error",
                "message": f"PythonSurface execution rejected: concurrency limit {self._concurrency_limit} reached"
            }
        try:
            loop = asyncio.get_running_loop()
            executor = self._process_executor if _is_picklable(context) else self._executor
            future = loop.run_in_executor(executor, _run_asteval_code, code, context)
            return await asyncio.wait_for(asyncio.shield(future), timeout=self.timeout)
        except asyncio.TimeoutError:
            # Replace executor to release the stuck thread
            if self._executor is not None:
                self._executor.shutdown(wait=False)
            if self._process_executor is not None:
                self._process_executor.shutdown(wait=False)
            self._executor = _make_daemon_executor(max_workers=self._worker_count())
            self._process_executor = ProcessPoolExecutor(max_workers=self._worker_count())
            logger.warning("Surface execution timed out", timeout=self.timeout)
            return {
                "status": "error",
                "message": f"Execution timed out after {self.timeout}s"
            }
        finally:
            self._release_execution_slot()

    async def _execute_impl(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute Python code - required by abstract base class."""
        return self._run_code(code, context)

    def _run_code(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run asteval code synchronously in the executor thread."""
        logger.info("Executing Python code", code_length=len(code), has_context=context is not None)

        if not self.available:
            logger.error("Attempted Python execution but asteval not available")
            return {"status": "error", "message": "asteval not available"}

        try:
            from asteval import Interpreter

            # Create asteval interpreter with safe context
            aeval = Interpreter(excluded_symbols=['open', '__import__', 'eval', 'exec', 'compile', '__builtins__'])
            # Explicitly remove dangerous names (excluded_symbols alone is not sufficient in asteval 1.x)
            for bad in ['open', '__import__', 'eval', 'exec', 'compile', '__builtins__']:
                aeval.symtable.pop(bad, None)

            # Add context variables if provided
            if context:
                for key, value in context.items():
                    aeval.symtable[key] = value
                # Also provide the context object itself for compatibility
                aeval.symtable["context"] = context

            # Execute the code
            result = aeval(code)

            # Check for errors
            if aeval.error:
                if aeval.error and hasattr(aeval.error[0], "msg"):
                    # asteval ExceptionHolder
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
