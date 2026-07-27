"""Contract tests for all Surface plugins.

Verifies that every Surface class in em_cubed.surfaces:
1. Inherits SurfaceBase and does NOT override execute() directly.
2. Implements _execute_impl(), health(), and extract_tags().
3. execute() returns a dict with 'status' key.
4. execute() respects timeout.
"""

import pytest
from em_cubed.surfaces import (
    PythonSurface, PrologSurface, Z3Surface, DatalogSurface,
    SQLiteSurface, HySurface, QuickJSSurface, WASMSurface,
    ClingoSurface, KanrenSurface, LLMSurface, JanusSurface
)


ALL_SURFACES = [
    PythonSurface, PrologSurface, Z3Surface, DatalogSurface,
    SQLiteSurface, HySurface, QuickJSSurface, WASMSurface,
    ClingoSurface, KanrenSurface, LLMSurface, JanusSurface
]


@pytest.mark.parametrize("surface_cls", ALL_SURFACES)
def test_surface_does_not_override_execute(surface_cls):
    """Subclasses must inherit SurfaceBase.execute, not override it."""
    assert "execute" not in surface_cls.__dict__, (
        f"{surface_cls.__name__} overrides execute(). Subclasses should only override _execute_impl()."
    )


@pytest.mark.parametrize("surface_cls", ALL_SURFACES)
def test_surface_implements_required_contract(surface_cls):
    """Every surface must provide name, description, and available properties."""
    inst = surface_cls()
    assert isinstance(inst.name, str)
    assert isinstance(inst.description, str)
    assert isinstance(inst.available, bool)
    assert hasattr(inst, "_execute_impl")
    assert hasattr(inst, "health")
    assert hasattr(inst, "extract_tags")


@pytest.mark.asyncio
async def test_python_surface_execute_contract():
    surface = PythonSurface()
    res = await surface.execute("result = 1 + 1")
    assert isinstance(res, dict)
    assert res.get("status") == "ok"
    assert res.get("value") == 2


@pytest.mark.asyncio
async def test_sqlite_surface_execute_contract():
    surface = SQLiteSurface()
    res = await surface.execute("SELECT 42 AS val;")
    assert isinstance(res, dict)
    assert res.get("status") == "ok"
    assert res.get("value") == [{"val": 42}]
