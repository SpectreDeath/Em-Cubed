"""Prolog surface integration using pyswip."""

import asyncio
import importlib.util
from typing import List, Dict, Any, Optional
import structlog

from .base import SurfaceBase

logger = structlog.get_logger()


class PrologSurface(SurfaceBase):
    """Handle Prolog code execution and predicate extraction."""

    @property
    def name(self) -> str:
        return "prolog"

    @property
    def description(self) -> str:
        return "Prolog execution via PySWIP"

    @property
    def available(self) -> bool:
        return self._check_availability()

    def __init__(self, timeout: Optional[float] = None) -> None:
        super().__init__(timeout)
        self._prolog = None  # Lazy initialization of Prolog interpreter
        logger.info("PrologSurface initialized", available=self.available, timeout=self.timeout)

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

    def _get_prolog(self):
        """Get or create the Prolog interpreter instance."""
        if self._prolog is None:
            from pyswip import Prolog
            self._prolog = Prolog()
        return self._prolog

    def shutdown(self) -> None:
        """Shutdown Prolog engine."""
        if self._prolog is not None:
            logger.info("Shutting down Prolog surface")
            self._prolog = None

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

    async def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute Prolog code and return results."""
        return await self.execute_with_timeout(code, context)

    async def _execute_impl(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute Prolog code - implementation with timeout protection."""
        logger.info("Executing Prolog code", code_length=len(code), has_context=context is not None)

        if not self.available:
            logger.error("Attempted Prolog execution but PySWIP not available")
            return {"status": "error", "message": "PySWIP not available"}

        try:
            prolog = self._get_prolog()
            # Load context as facts if provided
            if context:
                for key, value in context.items():
                    safe_value = self._prolog_safe_value(value)
                    prolog.assertz(f"{key}({safe_value})")

            stripped_code = code.strip()

            # Built-ins that modify the dynamic database and should be
            # executed as goals, NOT asserted as facts/rules.
            _IMPURE_BUILTINS = {
                "retractall", "retract", "asserta", "assertz",
                "abolish", "flush_output", "flush", "close",
                "op", "set_prolog_flag", "setof", "bagof",
                "findall", "maplist", "call", "once",
            }

            # Improved mode detection:
            # - Explicit queries start with ?-
            # - Impure built-ins that modify the DB are always executed as goals
            # - Code containing rule definitions (:-) followed by ?- is split into assert + query
            # - Otherwise, trailing . indicates assertion (fact/rule)
            is_query = False
            processed_code = stripped_code

            if stripped_code.startswith('?-'):
                # Explicit query mode
                is_query = True
                processed_code = stripped_code[2:].strip()
            elif '?-' in stripped_code:
                # Mixed rule + query: split and assert rules first
                parts = stripped_code.split('?-')
                rule_part = parts[0].strip()
                query_part = parts[1].strip().rstrip('.').strip()

                # Assert the rule using direct Python call to SWI-Prolog
                if rule_part:
                    try:
                        # Flatten to single line and format properly for assertz
                        rule_flat = ' '.join(rule_part.split())
                        # pyswip assertz expects the rule without trailing period
                        rule_clean = rule_flat.rstrip('.')
                        # Use the internal call to handle multi-line rules
                        prolog.assertz(rule_clean)
                        logger.info("Prolog rule asserted successfully")
                    except Exception as assert_err:
                        logger.warning("Prolog rule assertion warning", error=str(assert_err))

                processed_code = query_part
                is_query = True
                logger.info("Mixed Prolog rule/query detected, asserting rules then querying", query=processed_code)
            elif stripped_code.endswith('.'):
                # Check if this is an impure built-in (database-modifying command)
                head_word = stripped_code.split('(')[0].split(' ')[0].strip().rstrip('.')
                if head_word in _IMPURE_BUILTINS:
                    is_query = True
                    processed_code = stripped_code.rstrip('.').strip()
                elif ' is ' in stripped_code:
                    # Arithmetic/evaluation expression - treat as query
                    import re
                    if re.search(r'\d|\+|\-|\*|\/|//', stripped_code):
                        is_query = True
                        processed_code = stripped_code.rstrip('.').strip()
                    else:
                        processed_code = stripped_code.rstrip('.').strip()
                else:
                    # Treat as assertion (fact/rule)
                    processed_code = stripped_code.rstrip('.').strip()
            else:
                # No trailing period, treat as query
                is_query = True
                processed_code = stripped_code

            if is_query:
                # Query mode: starts with ?- or determined to be query
                logger.info("Prolog query mode detected", query=processed_code)

                # Execute query with configurable timeout (limit to 1000 solutions)
                def execute_query():
                    return list(prolog.query(processed_code))

                try:
                    result = await asyncio.get_event_loop().run_in_executor(
                        self._executor, execute_query
                    )
                except asyncio.TimeoutError:
                    logger.warning("Prolog query timed out", query=processed_code, timeout=self.timeout)
                    return {"status": "error", "message": f"Query execution timed out after {self.timeout}s"}

                if len(result) > 1000:
                    result = result[:1000]  # Truncate for safety

                logger.info("Prolog query successful", result_count=len(result))
                return {"status": "ok", "message": "Query executed successfully", "result": result}
            else:
                # Assertion mode: fact or rule
                logger.info("Prolog assert mode detected")
                prolog.assertz(processed_code)
                logger.info("Prolog assertion successful")
                return {"status": "ok", "message": "Code asserted successfully"}

        except Exception as e:
            logger.exception("Prolog execution failed", error=str(e), code=code)
            return {"status": "error", "message": str(e)}

    async def health(self) -> bool:
        """Check if the surface is available."""
        return self.available
