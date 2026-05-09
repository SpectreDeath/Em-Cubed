"""Python surface integration for executing Python code."""

import asyncio
import importlib.util
from typing import Dict, Any, Optional
import structlog

from .base import SurfaceBase
from ..plugin import SurfacePlugin

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
        return await self.execute_with_timeout(code, context)

    async def _execute_impl(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute Python code - implementation with timeout protection."""
        logger.info("Executing Python code", code_length=len(code), has_context=context is not None)

        if not self.available:
            logger.error("Attempted Python execution but asteval not available")
            return {"status": "error", "message": "asteval not available"}

        try:
            from asteval import Interpreter

            def execute_code():
                # Create asteval interpreter with safe context
                aeval = Interpreter()

                # Add context variables if provided
                if context:
                    for key, value in context.items():
                        aeval.symtable[key] = value

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

            return await asyncio.get_event_loop().run_in_executor(
                self._executor, execute_code
            )

        except Exception as e:
            logger.exception("Python execution failed", error=str(e), code=code)
            return {"status": "error", "message": str(e)}

    async def health(self) -> bool:
        """Check if the surface is available."""
        return bool(self.available)
