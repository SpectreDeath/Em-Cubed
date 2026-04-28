"""Python surface integration for executing Python code."""

import importlib.util
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger()


class PythonSurface:
    """Handle Python code execution and metadata extraction."""

    def __init__(self):
        self.available = self._check_availability()
        logger.info("PythonSurface initialized", available=self.available)

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
