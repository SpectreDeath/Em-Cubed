import pytest
from em_cubed.plugin_manager import PluginManager

@pytest.fixture
def plugin_manager():
    return PluginManager()

@pytest.mark.asyncio
async def test_python_prolog_orchestration_sync(plugin_manager):
    """Test that a Python skill can call Prolog synchronously via the bridge with tracing."""
    from em_cubed.skills.telemetry import ExecutionRecord, TraceContext, get_telemetry_collector
    from em_cubed.skills.executor import TelemetryProxy
    from datetime import datetime
    
    python_code = """
prolog = context["surfaces"]["prolog"]
prolog.execute_sync("fact(a).")
prolog.execute_sync("fact(b).")
res = prolog.execute_sync("fact(X)")
result = {"found": [r["X"] for r in res.get("result", [])]}
result
"""
    python_surface = plugin_manager.get("python")
    
    # Setup tracing
    record = ExecutionRecord(skill_id="test_prolog", timestamp=datetime.utcnow(), success=True, execution_time_ms=0)
    trace_ctx = TraceContext(record)
    
    # Prepare context with proxies
    surfaces = plugin_manager._plugins
    proxies = {name: TelemetryProxy(surf, trace_ctx) for name, surf in surfaces.items()}
    context = {"surfaces": proxies, "skill_input": {}, "trace": trace_ctx, "context": {}}
    # Inject context itself for compatibility as fixed earlier
    context["context"] = context
    
    result = await python_surface.execute(python_code, context)
    
    assert result["status"] == "ok"
    assert "a" in result["value"]["found"]
    
    # Verify tracing
    assert record.trace_id is not None
    assert len(record.spans) >= 3
    assert record.spans[0].surface == "prolog"

@pytest.mark.asyncio
async def test_python_hy_orchestration_sync(plugin_manager):
    """Test that a Python skill can call Hy synchronously via the bridge with tracing."""
    from em_cubed.skills.telemetry import ExecutionRecord, TraceContext
    from em_cubed.skills.executor import TelemetryProxy
    from datetime import datetime
    
    python_code = """
hy = context["surfaces"]["hy"]
res = hy.execute_sync("(+ 1 2 3)")
result = {"sum": res.get("value")}
result
"""
    python_surface = plugin_manager.get("python")
    
    # Setup tracing
    record = ExecutionRecord(skill_id="test_hy", timestamp=datetime.utcnow(), success=True, execution_time_ms=0)
    trace_ctx = TraceContext(record)
    
    # Prepare context
    surfaces = plugin_manager._plugins
    proxies = {name: TelemetryProxy(surf, trace_ctx) for name, surf in surfaces.items()}
    context = {"surfaces": proxies, "skill_input": {}, "trace": trace_ctx}
    context["context"] = context
    
    result = await python_surface.execute(python_code, context)
    
    assert result["status"] == "ok"
    assert result["value"]["sum"] == 6
    
    # Verify tracing
    assert len(record.spans) >= 1
    assert record.spans[0].surface == "hy"
