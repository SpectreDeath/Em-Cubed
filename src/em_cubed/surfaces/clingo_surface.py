"""Answer Set Programming surface via clingo."""

from typing import Any

from .base import SurfaceBase


try:
    import clingo  # noqa: F401
    _CLINGO_AVAILABLE = True
except Exception:
    _CLINGO_AVAILABLE = False


class ClingoSurface(SurfaceBase):
    """ASP surface backed by the `clingo` Python package.

    Code is a mix of ``#const`` declarations, program rules, and optional
    ``#show`` directives.  Results are returned as a JSON-friendly mapping
    of shown atoms.
    """

    def __init__(self, timeout: float | None = None):
        super().__init__(timeout)
        self._execution_cache: dict[str, Any] = {}

    def clear_cache(self) -> None:
        """Clear the execution cache."""
        self._execution_cache.clear()

    @property
    def name(self) -> str:
        return "clingo"

    @property
    def description(self) -> str:
        return "Answer Set Programming via clingo"

    @property
    def available(self) -> bool:
        return _CLINGO_AVAILABLE

    @property
    def _spec_available(self) -> bool:
        return _CLINGO_AVAILABLE

    def _check_availability(self) -> bool:
        return _CLINGO_AVAILABLE


    @staticmethod
    def extract_tags(source: str | None) -> list:
        if not source:
            return []

        import re

        tags = set()
        for match in re.finditer(r"(?<!#)(?<!\w)([a-z][a-zA-Z0-9_]*)\s*\(", source):
            candidate = match.group(1)
            if candidate not in {"show"}:
                tags.add(candidate)
        return list(tags)

    async def _execute_impl(self, code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.available:
            return {"status": "error", "message": "clingo package is not installed"}

        import hashlib
        import json

        serialized_ctx = json.dumps(context, sort_keys=True) if context else ""
        cache_key = hashlib.sha256(f"{code}:{serialized_ctx}".encode()).hexdigest()
        if cache_key in self._execution_cache:
            return self._execution_cache[cache_key]

        import clingo

        control = clingo.Control()
        control.configuration.solve.models = 0  # type: ignore[union-attr]
        control.configuration.solve.project = 1  # type: ignore[union-attr]

        try:
            control.add("base", [], code)
            control.ground([("base", [])])
        except RuntimeError as exc:
            return {"status": "error", "message": f"Clingo ground/load failed: {exc}"}

        models: list = []

        def _on_model(model):
            atoms = [str(symbol) for symbol in model.symbols(atoms=True)]
            models.append(atoms)

        try:
            control.solve(on_model=_on_model)
        except RuntimeError as exc:
            return {"status": "error", "message": f"Clingo solve failed: {exc}"}

        result_value: Any
        if not models:
            result_value = {"models": []}
        elif len(models) == 1:
            result_value = {"model": models[0]}
        else:
            result_value = {"models": models}

        res = {"status": "ok", "value": result_value}
        self._execution_cache[cache_key] = res
        return res

    async def health(self) -> bool:
        return self._check_availability()
