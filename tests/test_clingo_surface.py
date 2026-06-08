import pytest
from em_cubed.surfaces.clingo_surface import ClingoSurface


@pytest.mark.asyncio
async def test_clingo_surface_availability():
    surface = ClingoSurface()
    if surface._spec_available:
        assert surface.available is True
        assert await surface.health() is True
    else:
        assert surface.available is False
        assert await surface.health() is False


@pytest.mark.asyncio
async def test_clingo_surface_not_installed():
    import sys
    original = sys.modules.get("clingo")
    sys.modules["clingo"] = None
    try:
        surface = ClingoSurface()
        assert surface.available is False
        result = await surface.execute("a.")
        assert result["status"] == "error"
    finally:
        if original is not None:
            sys.modules["clingo"] = original
        else:
            del sys.modules["clingo"]


@pytest.mark.asyncio
async def test_clingo_basic_program():
    surface = ClingoSurface()
    if not surface.available:
        pytest.skip("clingo not installed")

    code = """
parent(john, mary).
parent(mary, ann).

ancestor(X, Y) :- parent(X, Y).
ancestor(X, Z) :- parent(X, Y), ancestor(Y, Z).

#show ancestor/2.
"""
    result = await surface.execute(code, {})
    assert result["status"] == "ok"
    value = result["value"]
    assert "model" in value or "models" in value


@pytest.mark.asyncio
async def test_clingo_no_models():
    surface = ClingoSurface()
    if not surface.available:
        pytest.skip("clingo not installed")

    code = """
a :- b.
b :- a.
"""
    result = await surface.execute(code, {})
    assert result["status"] == "ok"
    value = result["value"]
    assert "model" in value or "models" in value
    models = value.get("models") or value.get("model") or []
    assert len(models) == 0


def test_clingo_tag_extraction():
    code = """
parent(john, mary).
ancestor(X, Y) :- parent(X, Y).
path(X, Z) :- edge(X, Z).
sibling(X, Y) :- parent(P, X), parent(P, Y), X != Y.
"""
    tags = ClingoSurface.extract_tags(code)
    assert "parent" in tags
    assert "ancestor" in tags
    assert "path" in tags
    assert "sibling" in tags

    assert "show" not in tags


def test_clingo_extract_tags_empty():
    assert ClingoSurface.extract_tags("") == []
    assert ClingoSurface.extract_tags(None) == []
