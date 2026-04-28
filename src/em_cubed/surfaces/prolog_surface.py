"""Prolog surface integration using pyswip."""

import importlib.util
from typing import List, Dict, Any, Optional
import structlog

logger = structlog.get_logger()


class PrologSurface:
    """Handle Prolog code execution and predicate extraction."""

    def __init__(self) -> None:
        self.available = self._check_availability()
        logger.info("PrologSurface initialized", available=self.available)

    def _check_availability(self) -> bool:
        """Check if PySWIP is available."""
        available = importlib.util.find_spec("pyswip") is not None
        if not available:
            logger.warning("PySWIP not available for Prolog surface")
        return available

    def extract_tags(self, prolog_source: Optional[str]) -> List[str]:
        """Extract predicate names from Prolog source as logic_tags."""
        if not prolog_source:
            return []
        import re

        # Match predicate heads: name( or name :-
        heads = re.findall(r"^([a-z][a-zA-Z0-9_]*)\s*[:(]", prolog_source, re.MULTILINE)
        # Deduplicate, exclude Prolog builtins
        builtins = {"not", "is", "true", "fail", "assert", "retract"}
        return list(dict.fromkeys(h for h in heads if h not in builtins))

    def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute Prolog code and return results."""
        logger.info("Executing Prolog code", code_length=len(code), has_context=context is not None)

        if not self.available:
            logger.error("Attempted Prolog execution but PySWIP not available")
            return {"status": "error", "message": "PySWIP not available"}

        try:
            from pyswip import Prolog

            prolog = Prolog()
            # Load context as facts if provided
            if context:
                for key, value in context.items():
                    prolog.assertz(f"{key}({value})")

            # Try assertz first (for assertions without trailing dot)
            stripped = code.strip().rstrip(".")
            if stripped:
                prolog.assertz(stripped)
            # Try querying if assertz doesn't work or for queries
            try:
                result = list(prolog.query(code))
                logger.info("Prolog execution successful", result_count=len(result))
                return {"status": "ok", "message": "Code executed successfully", "result": result}
            except Exception:
                # Query failed, but assertz might have succeeded
                logger.info("Prolog execution successful (assertz)")
                return {"status": "ok", "message": "Code executed successfully"}

        except Exception as e:
            logger.exception("Prolog execution failed", error=str(e), code=code)
            return {"status": "error", "message": str(e)}

    def health(self) -> bool:
        """Check if the surface is available."""
        return self.available
