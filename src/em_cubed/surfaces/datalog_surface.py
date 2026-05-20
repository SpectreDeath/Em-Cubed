"""Datalog surface integration for fact-heavy relational queries."""

import asyncio
import importlib.util
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional, List
import structlog

from .base import SurfaceBase

logger = structlog.get_logger()


class DatalogSurface(SurfaceBase):
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
        # Use a dedicated executor so timeouts can be handled
        # by replacing the executor (abandoning the stuck thread)
        self._executor = ThreadPoolExecutor(max_workers=1)
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
        """Execute Datalog code with timeout protection."""
        try:
            loop = asyncio.get_running_loop()
            future = loop.run_in_executor(self._executor, self._run_code, code, context)
            return await asyncio.wait_for(asyncio.shield(future), timeout=self.timeout)
        except asyncio.TimeoutError:
            # Replace executor to release the stuck thread
            if self._executor is not None:
                self._executor.shutdown(wait=False)
            self._executor = ThreadPoolExecutor(max_workers=1)
            logger.warning("Surface execution timed out", timeout=self.timeout)
            return {
                "status": "error",
                "message": f"Execution timed out after {self.timeout}s"
            }

    async def _execute_impl(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute Datalog code - required by abstract base class."""
        return self._run_code(code, context)

    def _run_code(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run code synchronously in the executor thread."""
        logger.info("Executing Datalog code", code_length=len(code), has_context=context is not None)

        if not self.available:
            logger.error("Attempted Datalog execution but pyDatalog not available")
            return {"status": "error", "message": "pyDatalog not available"}

        try:
            from asteval import Interpreter
            from pyDatalog import pyDatalog as pd

            # Create asteval interpreter
            aeval = Interpreter()

            # Inject pyDatalog module into interpreter's namespace
            aeval.symtable['pyDatalog'] = pd

            # Add context variables if provided
            if context:
                for key, value in context.items():
                    aeval.symtable[key] = value

            # Execute the code using asteval
            result = aeval(code)

            # Check for errors from asteval
            if aeval.error:
                error_msg = str(aeval.error[0])
                logger.info("Datalog execution failed with error", error=error_msg)
                return {"status": "error", "message": error_msg}

            logger.info("Datalog execution successful")
            return {"status": "ok", "value": result, "message": "Execution completed"}

        except Exception as e:
            logger.exception("Datalog execution failed", error=str(e), code=code)
            return {"status": "error", "message": str(e)}

    async def health(self) -> bool:
        """Check if the surface is available."""
        return bool(self.available)