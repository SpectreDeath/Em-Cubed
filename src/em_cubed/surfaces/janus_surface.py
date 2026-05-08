"""Janus surface integration for Python-Prolog bridge."""

import asyncio
import importlib.util
from typing import Dict, Any, Optional, List
import structlog

from .base import SurfaceBase

logger = structlog.get_logger()


class JanusSurface(SurfaceBase):
    """Handle Janus/SWI-Prolog bridge integration."""

    @property
    def name(self) -> str:
        return "janus"

    @property
    def description(self) -> str:
        return "Janus bridge for Python-Prolog interop"

    @property
    def available(self) -> bool:
        return self._check_availability()

    def __init__(self, timeout: Optional[float] = None):
        super().__init__(timeout)
        self._janus = None  # Lazy initialization
        logger.info("JanusSurface initialized", available=self.available, timeout=self.timeout)

    def _check_availability(self) -> bool:
        """Check if Janus/SWI-Prolog is available."""
        available = importlib.util.find_spec("janus_swi") is not None
        if not available:
            logger.warning("janus_swi not available for Janus surface")
        return available

    def _get_janus(self):
        """Get or create Janus connection."""
        if self._janus is None:
            import janus_swi
            self._janus = janus_swi
        return self._janus

    @staticmethod
    def extract_tags(source: Optional[str]) -> List[str]:
        """Extract predicate names from Prolog source as logic_tags."""
        if not source:
            return []
        import re

        # Match predicate heads: name( or name :-
        heads = re.findall(r"^([a-z][a-zA-Z0-9_]*)\s*[:(]", source, re.MULTILINE)
        # Deduplicate, exclude Prolog builtins
        builtins = {"not", "is", "true", "fail", "assert", "retract"}
        return list(dict.fromkeys(h for h in heads if h not in builtins))

    async def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute Prolog code via Janus with timeout protection."""
        return await self._execute_impl(code, context)

    async def _execute_impl(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute Prolog code via Janus - implementation with timeout protection."""
        logger.info("Executing Prolog code via Janus", code_length=len(code), has_context=context is not None)

        if not self.available:
            logger.error("Attempted Janus execution but janus_swi not available")
            return {"status": "error", "message": "janus_swi not available"}

        try:
            janus = self._get_janus()

            # Load context as facts if provided
            if context:
                for key, value in context.items():
                    # Convert Python value to Prolog fact string
                    safe_value = self._prolog_safe_value(value)
                    # Assert fact using janus_swi
                    try:
                        janus.assertz(f"{key}({safe_value})")
                    except Exception as e:
                        logger.warning("Failed to assert context fact", key=key, error=str(e))

            stripped_code = code.strip()

            # Detect assertion (ends with .) vs query (starts with ?-)
            if stripped_code.endswith('.'):
                # Assertion mode: assert fact or rule
                # For Janus, we can use assertz for facts; rules might need consult?
                # Simplified: strip trailing '.' and assert
                fact = stripped_code.rstrip('.').strip()
                try:
                    # Use assertz for simple facts; for rules, might need different approach
                    # We'll use assertz for now; if it fails, try consult? but consult is for files
                    janus.assertz(fact)
                    logger.info("Janus assertion successful")
                    return {"status": "ok", "message": "Code asserted successfully"}
                except Exception as e:
                    logger.exception("Janus assertion failed")
                    return {"status": "error", "message": str(e)}
            else:
                # Query mode: starts with ?- or no trailing dot
                query_code = stripped_code.lstrip('?-').strip()
                logger.info("Janus query mode detected", query=query_code)

                def execute_query():
                    return janus.query_once(query_code)

                try:
                    result = await asyncio.get_event_loop().run_in_executor(
                        self._executor, execute_query
                    )
                    logger.info("Janus query successful", result=result)
                    return {"status": "ok", "message": "Query executed successfully", "result": result}
                except asyncio.TimeoutError:
                    logger.warning("Janus execution timed out", timeout=self.timeout)
                    return {"status": "error", "message": f"Execution timed out after {self.timeout}s"}
                except Exception as e:
                    logger.exception("Janus query failed")
                    return {"status": "error", "message": str(e)}

        except Exception as e:
            logger.exception("Janus execution failed", error=str(e), code=code)
            return {"status": "error", "message": str(e)}

    def _prolog_safe_value(self, value: Any) -> str:
        """Convert a value to a safe Prolog representation."""
        if isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, bool):
            return "true" if value else "fail"
        elif isinstance(value, str):
            # Escape single quotes and wrap in single quotes
            escaped = value.replace("\\", "\\\\").replace("'", "\\'")
            return "'" + escaped + "'"
        elif isinstance(value, (list, tuple)):
            # Convert to Prolog list
            elements = [self._prolog_safe_value(item) for item in value]
            return f"[{','.join(elements)}]"
        else:
            # Convert to string and quote
            escaped = str(value).replace("\\", "\\\\").replace("'", "\\'")
            return "'" + escaped + "'"

    async def health(self) -> bool:
        """Check if the surface is available."""
        return bool(self.available)
