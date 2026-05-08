"""Hy surface integration using hy-lang."""

import importlib.util
from typing import List, Dict, Any, Optional
import structlog

from .base import SurfaceBase

logger = structlog.get_logger()


class HySurface(SurfaceBase):
    """Handle Hy code execution and function extraction."""

    @property
    def name(self) -> str:
        return "hy"

    @property
    def description(self) -> str:
        return "Hy Lisp execution"

    @property
    def available(self) -> bool:
        return self._check_availability()

    def __init__(self, timeout: Optional[float] = None) -> None:
        super().__init__(timeout)
        logger.info("HySurface initialized", available=self.available, timeout=self.timeout)

    def _check_availability(self) -> bool:
        """Check if Hy is available."""
        return importlib.util.find_spec("hy") is not None

    @staticmethod
    def extract_tags(hy_source: Optional[str]) -> List[str]:
        """Extract function names from Hy defn forms as heuristic_tags."""
        if not hy_source:
            return []
        import re

        fns = re.findall(r"\(defn\s+([a-zA-Z][a-zA-Z0-9_\-?!]*)", hy_source)
        return list(dict.fromkeys(fns))

    async def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute Hy code with timeout protection."""
        return await self._execute_impl(code, context)

    async def _execute_impl(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute Hy code - implementation with timeout protection."""
        logger.info("Executing Hy code", code_length=len(code), has_context=context is not None)

        if not self.available:
            logger.error("Attempted Hy execution but Hy not available")
            return {"status": "error", "message": "Hy not available"}

        try:
            import hy

            # Read and evaluate all forms in the code
            forms = hy.read_many(code)
            result = None
            for form in forms:
                result = hy.eval(form)

            logger.info("Hy execution successful")
            return {"status": "ok", "value": result}
        except Exception as e:
            logger.exception("Hy execution failed", error=str(e), code=code)
            return {"status": "error", "message": str(e)}

    async def health(self) -> bool:
        """Check if the surface is available."""
        return self.available
