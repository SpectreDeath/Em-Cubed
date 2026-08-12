"""Tests for the ToolRegistry dispatch table (Phase 2)."""

from __future__ import annotations

from typing import Any

import pytest

from em_cubed.gateway.tool_registry import ToolRegistry


# ---------------------------------------------------------------------------
# Core registry behaviour
# ---------------------------------------------------------------------------


def test_register_and_dispatch():
    registry = ToolRegistry()
    registry.register("my_tool", lambda args: {"result": args["x"] + 1})
    result = registry.dispatch("my_tool", {"x": 41})
    assert result == {"result": 42}


def test_dispatch_unknown_tool_returns_error():
    registry = ToolRegistry()
    result = registry.dispatch("does_not_exist", {})
    assert "error" in result
    assert "does_not_exist" in result["error"]


def test_registered_names_sorted():
    registry = ToolRegistry()
    registry.register("zzz", lambda args: {})
    registry.register("aaa", lambda args: {})
    registry.register("mmm", lambda args: {})
    assert registry.registered_names() == ["aaa", "mmm", "zzz"]


def test_len():
    registry = ToolRegistry()
    assert len(registry) == 0
    registry.register("t1", lambda args: {})
    registry.register("t2", lambda args: {})
    assert len(registry) == 2


def test_handler_exception_propagates():
    registry = ToolRegistry()

    def _boom(args: dict[str, Any]) -> dict[str, Any]:
        raise ValueError("deliberate error")

    registry.register("bad_tool", _boom)
    with pytest.raises(ValueError, match="deliberate error"):
        registry.dispatch("bad_tool", {})


def test_overwrite_warns_and_replaces(caplog: pytest.LogCaptureFixture):
    import logging
    registry = ToolRegistry()
    registry.register("tool", lambda args: {"v": 1})
    with caplog.at_level(logging.WARNING, logger="em_cubed.gateway.tool_registry"):
        registry.register("tool", lambda args: {"v": 2})
    assert any("overwriting" in r.message for r in caplog.records)
    assert registry.dispatch("tool", {}) == {"v": 2}


# ---------------------------------------------------------------------------
# Handler modules register without error
# ---------------------------------------------------------------------------


def test_ontology_handlers_register():
    from em_cubed.gateway.tool_handlers import ontology_handlers
    registry = ToolRegistry()
    ontology_handlers.register_all(registry)
    names = registry.registered_names()
    assert "em_cubed_validate_triple" in names
    assert "em_cubed_elicit_ontology" in names
    assert "em_cubed_evaluate_topos" in names
    assert "em_cubed_extract_truthmakers" in names
    assert "em_cubed_prove_zkp" in names
    assert "em_cubed_check_health" in names
    assert "em_cubed_run_monad" in names


def test_skill_handlers_register():
    from em_cubed.gateway.tool_handlers import skill_handlers
    registry = ToolRegistry()
    skill_handlers.register_all(registry)
    names = registry.registered_names()
    assert "em_cubed_search_skills" in names
    assert "em_cubed_list_surfaces" in names
    assert "em_cubed_execute_skill" in names
    assert "em_cubed_auto_chain" in names


def test_workflow_handlers_register():
    from em_cubed.gateway.tool_handlers import workflow_handlers
    registry = ToolRegistry()
    workflow_handlers.register_all(registry)
    names = registry.registered_names()
    assert "em_cubed_run_dag" in names
    assert "em_cubed_check_dag_status" in names
    assert "em_cubed_run_geopolitical_sim" in names


def test_meta_handlers_register():
    from em_cubed.gateway.tool_handlers import meta_handlers
    registry = ToolRegistry()
    meta_handlers.register_all(registry)
    names = registry.registered_names()
    assert "em_cubed_server_discover" in names
    assert "serverDiscover" in names
    assert "em_cubed_lock_skills" in names


# ---------------------------------------------------------------------------
# EmCubedMCPServer uses registry
# ---------------------------------------------------------------------------


def test_mcp_server_call_tool_dispatches_via_registry():
    """EmCubedMCPServer.call_tool() must delegate to the ToolRegistry."""
    from em_cubed.gateway.mcp_server import EmCubedMCPServer
    server = EmCubedMCPServer()

    # Inject a test handler directly into the registry
    server._registry.register("test_probe", lambda args: {"probe": args.get("val")})
    result = server.call_tool("test_probe", {"val": "hello"})
    assert result == {"probe": "hello"}


def test_mcp_server_unknown_tool_returns_error():
    from em_cubed.gateway.mcp_server import EmCubedMCPServer
    server = EmCubedMCPServer()
    result = server.call_tool("nonexistent_tool", {})
    assert "error" in result


def test_mcp_server_evaluate_topos_via_registry():
    """End-to-end: em_cubed_evaluate_topos dispatches through registry to real handler."""
    from em_cubed.gateway.mcp_server import EmCubedMCPServer
    server = EmCubedMCPServer()
    result = server.call_tool("em_cubed_evaluate_topos", {"confidence": 0.95})
    assert "modal_type" in result
    assert result["modal_type"] == "Necessary"
    assert result["satisfied"] is True


def test_mcp_server_check_health_via_registry():
    from em_cubed.gateway.mcp_server import EmCubedMCPServer
    server = EmCubedMCPServer()
    result = server.call_tool("em_cubed_check_health", {})
    assert "coherence_index" in result
    assert "health_status" in result


def test_mcp_server_server_discover_via_registry():
    from em_cubed.gateway.mcp_server import EmCubedMCPServer
    server = EmCubedMCPServer()
    result = server.call_tool("em_cubed_server_discover", {})
    assert result["spec_version"] == "2026-07-28"
    assert result["stateless"] is True
