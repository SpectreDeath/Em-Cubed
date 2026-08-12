"""ToolRegistry: lightweight dispatch table for Em-Cubed MCP tools.

Replaces the monolithic ``if/elif`` chain in ``EmCubedMCPServer.call_tool()``
with a registration-based pattern. Each subsystem handler module calls
``register_all(registry)`` at startup. The MCP server becomes a thin
transport layer that delegates every tool invocation to this registry.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)

ToolHandler = Callable[[dict[str, Any]], dict[str, Any]]


class ToolRegistry:
    """Registration and dispatch table for Em-Cubed MCP tool handlers.

    Usage
    -----
    >>> registry = ToolRegistry()
    >>> registry.register("my_tool", lambda args: {"result": args["x"] + 1})
    >>> registry.dispatch("my_tool", {"x": 41})
    {'result': 42}
    """

    def __init__(self) -> None:
        self._handlers: dict[str, ToolHandler] = {}

    def register(self, name: str, handler: ToolHandler) -> None:
        """Register a tool handler by name.

        Parameters
        ----------
        name:
            The exact tool name as declared in ``EmCubedMCPServer.TOOLS``.
        handler:
            A callable ``(args: dict) -> dict`` that implements the tool logic.
        """
        if name in self._handlers:
            logger.warning("ToolRegistry: overwriting existing handler for %r", name)
        self._handlers[name] = handler
        logger.debug("ToolRegistry: registered tool %r", name)

    def dispatch(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        """Dispatch a tool invocation to its registered handler.

        Parameters
        ----------
        name:
            Tool name from the MCP ``tools/call`` request.
        args:
            Arguments dict from the MCP request.

        Returns
        -------
        dict
            Handler result, or ``{"error": "Unknown tool: <name>"}`` if not registered.
        """
        handler = self._handlers.get(name)
        if handler is None:
            logger.warning("ToolRegistry: no handler registered for %r", name)
            return {"error": f"Unknown tool: {name}"}
        try:
            return handler(args)
        except Exception as exc:
            logger.exception("ToolRegistry: handler for %r raised an exception", name)
            raise exc

    def registered_names(self) -> list[str]:
        """Return the sorted list of all registered tool names."""
        return sorted(self._handlers.keys())

    def __len__(self) -> int:
        return len(self._handlers)
