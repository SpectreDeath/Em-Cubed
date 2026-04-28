"""Hy surface integration using hy-lang."""

import importlib.util
from typing import List, Dict, Any, Optional
import structlog

logger = structlog.get_logger()


class HySurface:
    """Handle Hy code execution and function extraction."""

    def __init__(self) -> None:
        self.available = self._check_availability()
        logger.info("HySurface initialized", available=self.available)

    def _check_availability(self) -> bool:
        """Check if Hy is available."""
        return importlib.util.find_spec("hy") is not None

    def extract_tags(self, hy_source: str) -> List[str]:
        """Extract function names from Hy defn forms as heuristic_tags."""
        if not hy_source:
            return []
        import re

        fns = re.findall(r"\(defn\s+([a-zA-Z][a-zA-Z0-9_\-?!]*)", hy_source)
        return list(dict.fromkeys(fns))

    def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute Hy code and return results."""
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

    def health(self) -> bool:
        """Check if the surface is available."""
        return self.available
