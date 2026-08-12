"""Meta tool handlers: server_discover, lock_skills."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from em_cubed.gateway.tool_registry import ToolRegistry

# Number of tools — kept as a module-level constant so the handler doesn't
# need to import EmCubedMCPServer (which would create a circular import).
# Updated automatically when MCP_TOOLS_COUNT is set by the server at init.
_tools_count: int = 0


def _handle_server_discover(args: dict[str, Any]) -> dict[str, Any]:
    return {
        "spec_version": "2026-07-28",
        "protocolVersion": "2026-07-28",
        "stateless": True,
        "server_info": {"name": "em-cubed", "version": "0.8.0"},
        "capabilities": {
            "stateless_transport": True,
            "routing_headers": ["MCP-Method", "MCP-Name"],
            "interactive_mode": "input_required",
            "tools": _tools_count,
        },
        "_meta": {
            "handshake_required": False,
            "mcp_session_id_deprecated": True,
        },
    }


def _handle_lock_skills(args: dict[str, Any]) -> dict[str, Any]:
    verify = args.get("verify", False)
    # Stub: real implementation would cryptographically sign/verify registry.
    return {"verified": verify, "status": "ok"}


def set_tools_count(count: int) -> None:
    """Allow the MCP server to inject the total tool count for server_discover."""
    global _tools_count
    _tools_count = count


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register_all(registry: "ToolRegistry") -> None:
    """Register meta tool handlers with *registry*."""
    registry.register("em_cubed_server_discover", _handle_server_discover)
    registry.register("serverDiscover", _handle_server_discover)  # legacy alias
    registry.register("em_cubed_lock_skills", _handle_lock_skills)
