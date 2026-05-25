"""Tests for QuickJS surface implementation."""

import pytest
from em_cubed.surfaces.quickjs_surface import QuickJSSurface


@pytest.fixture
def quickjs_surface():
    """Create a QuickJSSurface instance."""
    return QuickJSSurface()


@pytest.mark.asyncio
async def test_basic_arithmetic(quickjs_surface):
    """Test basic arithmetic expression evaluation."""
    if not quickjs_surface.available:
        pytest.skip("pyquickjs not installed")
    result = await quickjs_surface.execute("1 + 2 * 3")
    assert result["status"] == "ok"
    # Should be 7. quickjs may return int
    assert result["value"] == 7


@pytest.mark.asyncio
async def test_context_injection_primitives(quickjs_surface):
    """Test that context variables are injected into JS context."""
    if not quickjs_surface.available:
        pytest.skip("pyquickjs not installed")
    context = {
        "x": 10,
        "name": "test",
        "flag": True,
        "items": [1, 2, 3],
        "mapping": {"a": 1, "b": 2}
    }
    code = "JSON.stringify({x, name, flag, items, mapping})"
    result = await quickjs_surface.execute(code, context=context)
    assert result["status"] == "ok"
    import json
    output = json.loads(result["value"])
    assert output["x"] == 10
    assert output["name"] == "test"
    assert output["flag"] is True
    assert output["items"] == [1, 2, 3]
    assert output["mapping"] == {"a": 1, "b": 2}


@pytest.mark.asyncio
async def test_context_injection_null(quickjs_surface):
    """Test that null context is injected correctly."""
    if not quickjs_surface.available:
        pytest.skip("pyquickjs not installed")
    context = {"none_val": None}
    result = await quickjs_surface.execute("none_val === null", context=context)
    assert result["status"] == "ok"
    # JS boolean result should be true
    assert result["value"] is True


@pytest.mark.asyncio
async def test_invalid_js_returns_error(quickjs_surface):
    """Test that invalid JavaScript produces error."""
    if not quickjs_surface.available:
        pytest.skip("pyquickjs not installed")
    result = await quickjs_surface.execute("this is not valid js!!!")
    assert result["status"] == "error"
    assert "message" in result


def test_available_property(quickjs_surface):
    """Test available property reflects pyquickjs installation."""
    # Just check type bool; actual availability depends on environment
    assert isinstance(quickjs_surface.available, bool)


def test_extract_tags():
    """Test extract_tags finds function names."""
    surface = QuickJSSurface()
    source = """
        function foo() { return 1; }
        const bar = function() {};
        const baz = () => {};
        // Not a function: const obj = { method() {} };
    """
    tags = surface.extract_tags(source)
    assert "foo" in tags
    assert "bar" in tags


def test_extract_tags_empty():
    """Test extract_tags with empty source."""
    surface = QuickJSSurface()
    assert surface.extract_tags(None) == []
    assert surface.extract_tags("") == []


@pytest.mark.asyncio
async def test_quickjs_without_pyquickjs(monkeypatch):
    """Test that surface reports unavailable and returns error if pyquickjs missing."""
    # Mock import to fail
    import importlib.util
    original_find_spec = importlib.util.find_spec

    def mock_find_spec(name, package=None):
        if name == "quickjs":
            return None
        return original_find_spec(name, package)

    monkeypatch.setattr(importlib.util, "find_spec", mock_find_spec)
    surface = QuickJSSurface()
    assert surface.available is False
    result = await surface.execute("1+1")
    assert result["status"] == "error"
    assert "pyquickjs not available" in result["message"]
