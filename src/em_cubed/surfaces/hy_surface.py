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
        return await self.execute_with_timeout(code, context)

    async def _execute_impl(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute Hy code - implementation with timeout protection."""
        logger.info("Executing Hy code", code_length=len(code), has_context=context is not None)

        if not self.available:
            logger.error("Attempted Hy execution but Hy not available")
            return {"status": "error", "message": "Hy not available"}

        try:
            import hy
            import re as _re

            def _fix_hy_cond(code: str) -> str:
                """Rewrite bracket-style (cond [... ] [...]) to flat cond form.
                This handles [test body] bracket clauses inside a (cond ...) form
                by converting them to flat cond syntax: test1 body1 test2 body2 ...
                Only applies to bracketed pairs where both elements are present."""
                try:
                    return _re.sub(
                        r'\(cond\b((?:\s*\[[^\]]+\])+)\s*\)',
                        lambda m: _rewrite_cond(m.group(1)),
                        code,
                        flags=_re.DOTALL,
                    )
                except Exception:
                    return code

            def _rewrite_cond(bracket_block: str) -> str:
                """Convert a sequence of [test result] bracket pairs to flat cond."""
                pairs = _re.findall(r'\[(.*?)\]', bracket_block, _re.DOTALL)
                flat_parts = []
                for pair in pairs:
                    # Each bracket should have exactly 2 elements
                    parts = pair.strip().split(None, 1)
                    if len(parts) == 2:
                        flat_parts.append(parts[0].strip())
                        flat_parts.append(parts[1].strip())
                    elif len(parts) == 1:
                        flat_parts.append(parts[0].strip())
                        flat_parts.append("None")
                return "(cond " + " ".join(flat_parts) + ")"

            code = _fix_hy_cond(code)

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
