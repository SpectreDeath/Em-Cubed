"""Answer Set Programming surface via clingo."""

from typing import Any, Dict, Optional

from .base import SurfaceBase


class ClingoSurface(SurfaceBase):
    """ASP surface backed by the `clingo` Python package.

    Code is a mix of ``#const`` declarations, program rules, and optional
    ``#show`` directives.  Results are returned as a JSON-friendly mapping
    of shown atoms.
    """

    @property
    def name(self) -> str:
        return "clingo"

    @property
    def description(self) -> str:
        return "Answer Set Programming via clingo"

    @property
    def available(self) -> bool:
        return self._check_availability()

    @property
    def _spec_available(self) -> bool:
        import importlib.util
        return importlib.util.find_spec("clingo") is not None

    def _check_availability(self) -> bool:
        if not self._spec_available:
            return False
        try:
            import clingo  # noqa: F401
            return True
        except ImportError:
            return False

    @staticmethod
    def extract_tags(source: Optional[str]) -> list:
        if not source:
            return []

        import re

        tags = set()
        for match in re.finditer(r"(?<!#)(?<!\w)([a-z][a-zA-Z0-9_]*)\s*\(", source):
            candidate = match.group(1)
            if candidate not in {"show"}:
                tags.add(candidate)
        return list(tags)

    async def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self.execute_with_timeout(code, context)

    async def _execute_impl(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.available:
            return {"status": "error", "message": "clingo package is not installed"}

        import clingo

        control = clingo.Control()
        control.configuration.solve.models = 0  # type: ignore[union-attr]
        control.configuration.solve.project = 1  # type: ignore[union-attr]

        try:
            control.add("base", [], code)
            control.ground([("base", [])])
        except clingo.ClingoError as exc:  # type: ignore[attr-defined,union-attr]
            return {"status": "error", "message": f"Clingo ground/load failed: {exc}"}

        models: list = []

        def _on_model(model):
            atoms = [str(symbol) for symbol in model.symbols(atoms=True)]
            models.append(atoms)

        try:
            control.solve(on_model=_on_model)
        except Exception as exc:  # noqa: BLE001
            return {"status": "error", "message": f"Clingo solve failed: {exc}"}

        result_value: Any
        if not models:
            result_value = {"models": []}
        elif len(models) == 1:
            result_value = {"model": models[0]}
        else:
            result_value = {"models": models}

        return {"status": "ok", "value": result_value}

    async def health(self) -> bool:
        return self._check_availability()
