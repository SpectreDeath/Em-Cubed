"""Tool handler sub-package for Em-Cubed MCP tools.

Each module exposes a ``register_all(registry: ToolRegistry)`` function
that registers its tools.  Import order determines registration order but
does not affect behaviour since tool names are unique.
"""
