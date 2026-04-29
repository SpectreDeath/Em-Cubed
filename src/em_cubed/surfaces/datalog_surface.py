"""Datalog surface integration for fact-heavy relational queries."""

import importlib.util
from typing import Dict, Any, Optional, List
import structlog

from .base import SurfaceBase
from ..plugin import SurfacePlugin

logger = structlog.get_logger()


class DatalogSurface(SurfaceBase, SurfacePlugin):
    """Handle Datalog code execution and predicate extraction."""

    @property
    def name(self) -> str:
        return "datalog"

    @property
    def description(self) -> str:
        return "Datalog for fact-heavy relational queries"

    @property
    def available(self) -> bool:
        return self._check_availability()

    def __init__(self, timeout: Optional[float] = None):
        super().__init__(timeout)
        self._globals = {'__builtins__': __builtins__}
        logger.info("DatalogSurface initialized", available=self.available, timeout=self.timeout)

    def _check_availability(self) -> bool:
        """Check if pyDatalog is available."""
        available = importlib.util.find_spec("pyDatalog") is not None
        if not available:
            logger.warning("pyDatalog not available for Datalog surface")
        return available

    @staticmethod
    def extract_tags(source: Optional[str]) -> List[str]:
        """Extract predicate names from Datalog source.
        
        Looks for:
        - Predicate definitions: pred(X, Y) :- ...
        - Fact assertions: pred(a, b).
        - Query patterns: ?- pred(X, Y).
        - Predicates in rule bodies: :- pred1, pred2.
        """
        if not source:
            return []
        import re

        predicates = set()
        
        # Match predicate heads in rules: name(...) :-
        rule_head_pattern = r'^([a-z][a-zA-Z0-9_]*)\s*\([^)]*\)\s*:-'
        # Match facts: name(...).
        fact_pattern = r'^([a-z][a-zA-Z0-9_]*)\s*\([^)]*\)\s*\.'
        # Match query patterns: ?- name(...).
        query_pattern = r'\?-\s*([a-z][a-zA-Z0-9_]*)\s*\('
        # Match predicates in rule bodies: , name(...) or :- name(...) or name(...) ,
        body_predicate_pattern = r'(?:,|:-)\s*([a-z][a-zA-Z0-9_]*)\s*\([^)]*\)|\b([a-z][a-zA-Z0-9_]*)\s*\([^)]*\)\s*(?:,|$)'
        
        # Extract from heads, facts, and queries
        for pattern in [rule_head_pattern, fact_pattern, query_pattern]:
            matches = re.findall(pattern, source, re.MULTILINE | re.IGNORECASE)
            predicates.update(matches)
        
        # Extract from rule bodies
        body_matches = re.findall(body_predicate_pattern, source, re.MULTILINE | re.IGNORECASE)
        for match in body_matches:
            # Each match is a tuple with two groups, one of which is non-empty
            for group in match:
                if group:
                    predicates.add(group)
                    break
        
        return list(predicates)

    async def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute Datalog code and return results."""
        return await self.execute_with_timeout(code, context)

    async def _execute_impl(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute Datalog code - implementation with timeout protection."""
        logger.info("Executing Datalog code", code_length=len(code), has_context=context is not None)

        if not self.available:
            logger.error("Attempted Datalog execution but pyDatalog not available")
            return {"status": "error", "message": "pyDatalog not available"}

        try:
            from pyDatalog import pyDatalog

            # Import pyDatalog into our persistent globals
            if 'pyDatalog' not in self._globals:
                self._globals['pyDatalog'] = pyDatalog

            # Add context as facts if provided
            if context:
                for key, value in context.items():
                    # Create atoms for context predicates
                    pyDatalog.create_atoms(key)
                    # Add fact
                    exec(f"+ ({key}[{repr(key)}] == {repr(value)})", self._globals)

            # Execute the code using pyDatalog's syntax
            stripped_code = code.strip()

            # Check if it looks like a query (contains == pattern or starts with query-like syntax)
            if '==' in stripped_code or stripped_code.endswith('?'):
                # It's a query - evaluate it and return the result
                result = eval(stripped_code.rstrip('?'), self._globals)
                return {"status": "ok", "message": "Query executed successfully", "result": str(result)}
            else:
                # Treat as assertion (fact or rule) - just execute it
                exec(stripped_code, self._globals)
                return {"status": "ok", "message": "Code executed successfully"}

        except Exception as e:
            logger.exception("Datalog execution failed", error=str(e), code=code)
            return {"status": "error", "message": str(e)}

    async def health(self) -> bool:
        """Check if the surface is available."""
        return bool(self.available)