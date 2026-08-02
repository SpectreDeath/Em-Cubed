"""Pure relational logic surface via MiniKanren (kanren package)."""

from typing import Any

from .base import SurfaceBase


class KanrenSurface(SurfaceBase):
    """Relational / logic-programming surface backed by `kanren`.

    Provides a thin Python wrapper around MiniKanren so skill authors can
    declare relations, assert facts, and run queries inside a fenced
    `` ```kanren `` block.
    """

    @property
    def name(self) -> str:
        return "kanren"

    @property
    def description(self) -> str:
        return "Pure relational logic via MiniKanren"

    @property
    def available(self) -> bool:
        return self._check_availability()

    def _check_availability(self) -> bool:
        import importlib.util

        return importlib.util.find_spec("kanren") is not None

    @staticmethod
    def extract_tags(source: str | None) -> list:
        if not source:
            return []

        import re

        tags = set()

        for match in re.finditer(r"def\s+([a-zA-Z][a-zA-Z0-9_]*)", source):
            tags.add(match.group(1))

        for match in re.finditer(r"(?:relation|relational_fact|fact)\s*\(\s*([a-zA-Z][a-zA-Z0-9_]*)\s*\)", source):
            if match.lastindex and match.group(1):
                tags.add(match.group(1))

        return list(tags)

    async def _execute_impl(self, code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.available:
            return {"status": "error", "message": "kanren package is not installed"}

        import asyncio
        loop = asyncio.get_running_loop()
        try:
            return await loop.run_in_executor(None, self._run_kanren_code, code, context)
        except (TimeoutError, asyncio.CancelledError):
            return {"status": "error", "message": f"Kanren execution timed out after {self.timeout}s"}

    def _run_kanren_code(self, code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        namespace: dict[str, Any] = {
            "var": None,
            "Var": None,
            "run": None,
            "Relation": None,
            "fact": None,
            "conde": None,
            "eq": None,
            "lany": None,
            "lall": None,
            "membero": None,
            "context": context or {},
            "result": None,
        }

        try:
            from kanren import Relation, Var, conde, eq, fact, lall, lany, membero, run

            namespace.update(
                {
                    "var": Var,
                    "Var": Var,
                    "run": run,
                    "Relation": Relation,
                    "fact": fact,
                    "conde": conde,
                    "eq": eq,
                    "lany": lany,
                    "lall": lall,
                    "membero": membero,
                }
            )
        except ImportError as exc:
            return {"status": "error", "message": f"kanren import failed: {exc}"}

        exec_globals: dict[str, Any] = dict(namespace)

        try:
            exec(code, exec_globals)  # noqa: S102  # nosec B102 - kanren namespace pre-populated with allowlisted symbols only
        except Exception as exc:
            return {"status": "error", "message": f"Kanren execution failed: {exc}"}

        value = exec_globals.get("result")
        if value is None:
            value = {key: val for key, val in exec_globals.items() if key not in namespace and not key.startswith("_")}

        return {"status": "ok", "value": value}

    async def health(self) -> bool:
        return self._check_availability()
