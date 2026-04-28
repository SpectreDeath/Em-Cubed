"""Hy surface integration using hy-lang."""

import importlib.util
from typing import List, Dict, Any, Optional


class HySurface:
    """Handle Hy code execution and function extraction."""

    def __init__(self) -> None:
        self.available = self._check_availability()

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
        if not self.available:
            return {"status": "error", "message": "Hy not available"}

        try:
            import hy

            # Execute code in Hy environment
            result = hy.eval(hy.read(code))
            return {"status": "ok", "value": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def health(self) -> bool:
        """Check if the surface is available."""
        return self.available
