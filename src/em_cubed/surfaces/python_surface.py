"""Python surface integration for executing Python code."""

import asyncio
import importlib.util
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional
import structlog

from .base import SurfaceBase

logger = structlog.get_logger()


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
        # Use a dedicated executor so timeouts can be handled
        # by replacing the executor (abandoning the stuck thread)
        self._executor = ThreadPoolExecutor(max_workers=1)
        logger.info("PythonSurface initialized", available=self.available, timeout=self.timeout)

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
        """Execute Python code and return results using asteval for safety."""
        try:
            loop = asyncio.get_running_loop()
            future = loop.run_in_executor(self._executor, self._run_code, code, context)
            return await asyncio.wait_for(asyncio.shield(future), timeout=self.timeout)
        except asyncio.TimeoutError:
            # Replace executor to release the stuck thread
            self._executor.shutdown(wait=False)
            self._executor = ThreadPoolExecutor(max_workers=1)
            logger.warning("Surface execution timed out", timeout=self.timeout)
            return {
                "status": "error",
                "message": f"Execution timed out after {self.timeout}s"
            }

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
            aeval = Interpreter()

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
