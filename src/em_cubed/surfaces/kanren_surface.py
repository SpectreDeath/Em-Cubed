"""Pure relational logic surface via MiniKanren (kanren package)."""

from typing import Any, Dict, Optional

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
    def extract_tags(source: Optional[str]) -> list:
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

    async def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self.execute_with_timeout(code, context)

    async def _execute_impl(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.available:
            return {"status": "error", "message": "kanren package is not installed"}

        namespace: Dict[str, Any] = {
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
            from kanren import Var, run, Relation, fact, conde, eq, lany, lall, membero

            namespace.update(
                {
                    "var": lambda name="x": Var(name),
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

        exec_globals: Dict[str, Any] = dict(namespace)

        try:
            exec(code, exec_globals)  # noqa: S102
        except Exception as exc:
            return {"status": "error", "message": f"Kanren execution failed: {exc}"}

        value = exec_globals.get("result")
        if value is None:
            value = {
                key: val
                for key, val in exec_globals.items()
                if key not in namespace and not key.startswith("_")
            }

        return {"status": "ok", "value": value}

    async def health(self) -> bool:
        return self._check_availability()
