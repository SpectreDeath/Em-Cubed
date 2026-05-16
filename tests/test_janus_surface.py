"""Tests for Janus surface implementation with mocked dependencies."""

import pytest
from unittest.mock import MagicMock, patch
from em_cubed.surfaces.janus_surface import JanusSurface

@pytest.fixture
def mock_janus_swi():
    """Mock the janus_swi module."""
    mock_module = MagicMock()
    mock_module.__spec__ = MagicMock()
    mock_module.assertz = MagicMock()
    mock_module.query_once = MagicMock(return_value={"X": "value"})
    return mock_module

@pytest.fixture
def janus_surface(mock_janus_swi):
    """Create a JanusSurface instance with mocked janus_swi."""
    import sys
    sys.modules["janus_swi"] = mock_janus_swi
    surface = JanusSurface()
    surface._check_availability = MagicMock(return_value=True)
    surface._janus = mock_janus_swi
    yield surface
    if "janus_swi" in sys.modules:
        del sys.modules["janus_swi"]

@pytest.mark.asyncio
async def test_execute_unavailable():
    """Test execution when janus is unavailable."""
    with patch("importlib.util.find_spec", return_value=None):
        surface = JanusSurface()
        result = await surface.execute("fact.")
        assert result["status"] == "error"
        assert "not available" in result["message"]

@pytest.mark.asyncio
async def test_execute_assertion(janus_surface, mock_janus_swi):
    """Test asserting a fact."""
    result = await janus_surface.execute("parent(john, mary).")
    assert result["status"] == "ok"
    mock_janus_swi.assertz.assert_called_with("parent(john, mary)")

@pytest.mark.asyncio
async def test_execute_assertion_failure(janus_surface, mock_janus_swi):
    """Test assertion failure."""
    mock_janus_swi.assertz.side_effect = Exception("Assertion failed")
    result = await janus_surface.execute("parent(john, mary).")
    assert result["status"] == "error"
    assert "Assertion failed" in result["message"]

@pytest.mark.asyncio
async def test_execute_query(janus_surface, mock_janus_swi):
    """Test executing a query."""
    result = await janus_surface.execute("parent(john, X)")
    assert result["status"] == "ok"
    assert result["result"] == {"X": "value"}
    mock_janus_swi.query_once.assert_called_with("parent(john, X)")

@pytest.mark.asyncio
async def test_execute_query_failure(janus_surface, mock_janus_swi):
    """Test query failure."""
    mock_janus_swi.query_once.side_effect = Exception("Query failed")
    result = await janus_surface.execute("parent(john, X)")
    assert result["status"] == "error"
    assert "Query failed" in result["message"]

@pytest.mark.asyncio
async def test_context_injection(janus_surface, mock_janus_swi):
    """Test context injection into facts."""
    context = {"x": 10, "y": "test", "z": True, "w": [1, 2]}
    result = await janus_surface.execute("query(X)", context=context)
    assert result["status"] == "ok"
    
    # Verify assertions were made for context
    mock_janus_swi.assertz.assert_any_call("x(10)")
    mock_janus_swi.assertz.assert_any_call("y('test')")
    mock_janus_swi.assertz.assert_any_call("z(true)")
    mock_janus_swi.assertz.assert_any_call("w([1,2])")

@pytest.mark.asyncio
async def test_context_injection_failure_continues(janus_surface, mock_janus_swi):
    """Test context injection failure does not abort execution."""
    mock_janus_swi.assertz.side_effect = [Exception("Failed"), None]
    result = await janus_surface.execute("query(X)", context={"a": 1})
    assert result["status"] == "ok"

def test_shutdown(janus_surface):
    """Test shutdown clears references."""
    assert janus_surface._janus is not None
    janus_surface.shutdown()
    assert janus_surface._janus is None

def test_extract_tags():
    """Test extracting tags from Prolog source."""
    source = "parent(a, b).\nfact(a)."
    tags = JanusSurface.extract_tags(source)
    assert "parent" in tags
    assert "fact" in tags

def test_extract_tags_empty():
    """Test extract tags with empty source."""
    assert JanusSurface.extract_tags("") == []
    assert JanusSurface.extract_tags(None) == []
