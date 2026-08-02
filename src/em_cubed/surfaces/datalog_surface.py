"""Datalog surface integration for fact-heavy relational queries."""

import ast
import asyncio
import importlib.util
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import structlog

from .base import SurfaceBase

logger = structlog.get_logger()


class DatalogSurface(SurfaceBase):
    """Handle Datalog code execution and predicate extraction."""

    # NOTE: _execution_cache is intentionally an *instance* variable (set in __init__).
    # A class-level mutable dict would be shared across all instances, causing state
    # leakage between tests and concurrent surface objects.

    @property
    def name(self) -> str:
        return "datalog"

    @property
    def description(self) -> str:
        return "Datalog for fact-heavy relational queries"

    @property
    def available(self) -> bool:
        return self._check_availability()

    def __init__(self, timeout: float | None = None):
        super().__init__(timeout)
        # Use a dedicated executor so timeouts can be handled
        # by replacing the executor (abandoning the stuck thread)
        self._executor = ThreadPoolExecutor(max_workers=1)
        self.max_fact_lines = int(os.getenv("EM_CUBED_DATALOG_MAX_FACT_LINES", "5000"))
        self._concurrency_limit = int(os.getenv("EM_CUBED_DATALOG_MAX_CONCURRENCY", "1"))
        self._rejected_executions = 0
        # Per-instance cache: isolated between instances and test runs.
        self._execution_cache: dict[str, Any] = {}
        self._cache_max_entries = int(os.getenv("EM_CUBED_DATALOG_CACHE_MAX_ENTRIES", "256"))
        logger.info("DatalogSurface initialized", available=self.available, timeout=self.timeout)

    @property
    def cache_size(self) -> int:
        """Return the current number of entries in the execution cache."""
        return len(self._execution_cache)

    def clear_cache(self) -> None:
        """Clear the execution cache. Useful for test isolation and memory management."""
        self._execution_cache.clear()
        logger.debug("DatalogSurface execution cache cleared")

    def _check_availability(self) -> bool:
        """Check if pyDatalog is available and importable."""
        if importlib.util.find_spec("pyDatalog") is None:
            return False
        try:
            import pyDatalog  # noqa: F401
            return True
        except Exception as e:
            logger.warning("pyDatalog import failed", error=str(e))
            return False

    @staticmethod
    def extract_tags(source: str | None) -> list[str]:
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
        rule_head_pattern = r"^([a-z][a-zA-Z0-9_]*)\s*\([^)]*\)\s*:-"
        # Match facts: name(...).
        fact_pattern = r"^([a-z][a-zA-Z0-9_]*)\s*\([^)]*\)\s*\."
        # Match query patterns: ?- name(...).
        query_pattern = r"\?-\s*([a-z][a-zA-Z0-9_]*)\s*\("
        # Match predicates in rule bodies: , name(...) or :- name(...) or name(...) ,
        body_predicate_pattern = (
            r"(?:,|:-)\s*([a-z][a-zA-Z0-9_]*)\s*\([^)]*\)|\b([a-z][a-zA-Z0-9_]*)\s*\([^)]*\)\s*(?:,|$)"
        )

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

    async def _execute_impl(self, code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute Datalog code safely on executor thread with timeout shield."""
        loop = asyncio.get_running_loop()
        future = loop.run_in_executor(self._executor, self._run_code, code, context)
        try:
            return await asyncio.shield(future)
        except (TimeoutError, asyncio.CancelledError):
            if self._executor is not None:
                self._executor.shutdown(wait=False)
            self._executor = ThreadPoolExecutor(max_workers=1)
            raise

    def _validate_code(self, code: str) -> str | None:
        try:
            tree = ast.parse(code)
        except SyntaxError as exc:
            return f"Invalid Datalog syntax: {exc}"

        if len(code.splitlines()) > self.max_fact_lines:
            return f"Datalog fact limit exceeded: {len(code.splitlines())} > {self.max_fact_lines}"

        forbidden = (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        for node in ast.walk(tree):
            if isinstance(node, forbidden):
                return f"Statement not allowed in Datalog surface: {node.__class__.__name__}"
        return None

    def _run_code(self, code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Run code synchronously in the executor thread."""
        logger.info("Executing Datalog code", code_length=len(code), has_context=context is not None)

        import hashlib
        import json

        try:
            serialized_ctx = json.dumps(context, sort_keys=True) if context else ""
        except TypeError:
            serialized_ctx = str(context)
        cache_key = hashlib.sha256(f"{code}:{serialized_ctx}".encode()).hexdigest()
        if cache_key in self._execution_cache:
            logger.info("Datalog execution cache hit", hash=cache_key)
            return self._execution_cache[cache_key]

        if not self.available:
            logger.error("Attempted Datalog execution but pyDatalog not available")
            return {"status": "error", "message": "pyDatalog not available"}

        validation_error = self._validate_code(code)
        if validation_error:
            return {"status": "error", "message": validation_error}

        try:
            from pyDatalog import pyDatalog as pd

            namespace: dict[str, Any] = {
                "__builtins__": {
                    "abs": abs,
                    "float": float,
                    "int": int,
                    "len": len,
                    "max": max,
                    "min": min,
                    "print": print,
                    "range": range,
                    "round": round,
                    "str": str,
                    "sum": sum,
                },
                "pyDatalog": pd,
                "pd": pd,
            }

            if context:
                namespace.update(context)

            exec(code, namespace)  # noqa: S102  # nosec B102 - AST-validated allowlist; namespace restricts builtins
            result = namespace.get("result")

            res = {"status": "ok", "value": result, "message": "Execution completed"}
            # Evict oldest entry if cache is at capacity (simple FIFO eviction).
            if len(self._execution_cache) >= self._cache_max_entries:
                oldest_key = next(iter(self._execution_cache))
                del self._execution_cache[oldest_key]
                logger.debug("Datalog cache evicted oldest entry", cache_size=len(self._execution_cache))
            self._execution_cache[cache_key] = res
            return res

        except Exception as e:
            logger.exception("Datalog execution failed", error=str(e), code=code)
            return {"status": "error", "message": str(e)}

    async def health(self) -> bool:
        """Check if the surface is available."""
        return bool(self.available)
