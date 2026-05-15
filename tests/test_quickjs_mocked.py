"""Mocked tests for QuickJS surface implementation to increase coverage."""

import pytest
from unittest.mock import MagicMock
from em_cubed.surfaces.quickjs_surface import QuickJSSurface

@pytest.fixture
def mock_quickjs():
    """Mock pyquickjs context."""
    mock_ctx = MagicMock()
    mock_ctx.eval = MagicMock(return_value="mock_result")
    mock_module = MagicMock()
    mock_module.__spec__ = MagicMock()
    mock_module.Context = MagicMock(return_value=mock_ctx)
    return mock_module, mock_ctx

@pytest.mark.asyncio
async def test_execute_impl_mocked(monkeypatch, mock_quickjs):
    """Test execution logic directly by mocking quickjs."""
    mock_module, mock_ctx = mock_quickjs
    
    import sys
    sys.modules["quickjs"] = mock_module
    
    surface = QuickJSSurface()
    surface._check_availability = MagicMock(return_value=True)
    
    result = await surface._execute_impl("return 1;")
    assert result["status"] == "ok"
    assert result["value"] == "mock_result"
    mock_ctx.eval.assert_called_with("return 1;")
    
    del sys.modules["quickjs"]

@pytest.mark.asyncio
async def test_execute_impl_with_context_mocked(monkeypatch, mock_quickjs):
    """Test execution with context injection."""
    mock_module, mock_ctx = mock_quickjs
    import sys
    sys.modules["quickjs"] = mock_module
    
    surface = QuickJSSurface()
    surface._check_availability = MagicMock(return_value=True)
    
    context = {"x": 10, "y": "test"}
    result = await surface._execute_impl("return 1;", context=context)
    
    assert result["status"] == "ok"
    # eval is called multiple times for context
    mock_ctx.eval.assert_any_call('var x = 10;')
    mock_ctx.eval.assert_any_call('var y = "test";')
    mock_ctx.eval.assert_called_with("return 1;")
    
    del sys.modules["quickjs"]

@pytest.mark.asyncio
async def test_execute_impl_exception_mocked(monkeypatch, mock_quickjs):
    """Test exception handling during execution."""
    mock_module, mock_ctx = mock_quickjs
    mock_ctx.eval.side_effect = Exception("Eval failed")
    
    import sys
    sys.modules["quickjs"] = mock_module
    
    surface = QuickJSSurface()
    surface._check_availability = MagicMock(return_value=True)
    
    result = await surface._execute_impl("bad code")
    assert result["status"] == "error"
    assert "Eval failed" in result["message"]
    
    del sys.modules["quickjs"]
