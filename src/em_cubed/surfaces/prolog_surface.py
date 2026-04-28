"""Prolog surface integration using pyswip."""

import importlib.util
from typing import List, Dict, Any, Optional
import structlog

logger = structlog.get_logger()


class PrologSurface:
    """Handle Prolog code execution and predicate extraction."""

    def __init__(self) -> None:
        self.available = self._check_availability()
        self._prolog = None  # Lazy initialization of Prolog interpreter
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

    def _get_prolog(self):
        """Get or create the Prolog interpreter instance."""
        if self._prolog is None:
            from pyswip import Prolog
            self._prolog = Prolog()
        return self._prolog

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

    def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute Prolog code and return results."""
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

            # Detect mode: assert (ends with .) vs query (starts with ?- or no .)
            if stripped_code.endswith('.'):
                # Assert mode: fact or rule
                logger.info("Prolog assert mode detected")
                prolog.assertz(stripped_code.rstrip('.'))
                logger.info("Prolog assertion successful")
                return {"status": "ok", "message": "Code asserted successfully"}
            else:
                # Query mode: starts with ?- or no trailing .
                query_code = stripped_code.lstrip('?-').strip()
                logger.info("Prolog query mode detected", query=query_code)

                # Execute query with timeout (limit to 1000 solutions)
                from concurrent.futures import ThreadPoolExecutor, TimeoutError

                def execute_query():
                    return list(prolog.query(query_code))

                try:
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(execute_query)
                        result = future.result(timeout=10.0)  # 10 second timeout
                except TimeoutError:
                    logger.warning("Prolog query timed out", query=query_code)
                    return {"status": "error", "message": "Query execution timed out"}

                if len(result) > 1000:
                    result = result[:1000]  # Truncate for safety

                logger.info("Prolog query successful", result_count=len(result))
                return {"status": "ok", "message": "Query executed successfully", "result": result}

        except Exception as e:
            logger.exception("Prolog execution failed", error=str(e), code=code)
            return {"status": "error", "message": str(e)}

    def health(self) -> bool:
        """Check if the surface is available."""
        return self.available
