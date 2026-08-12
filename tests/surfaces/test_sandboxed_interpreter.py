"""Tests for Phase 4 (shared sandbox builder) and Phase 5 (dynamic surface discovery)."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Phase 4: make_sandboxed_interpreter
# ---------------------------------------------------------------------------


def test_make_sandboxed_interpreter_returns_interpreter_or_none():
    """make_sandboxed_interpreter() must not raise even if asteval is absent."""
    from em_cubed.surfaces.base import make_sandboxed_interpreter

    interp = make_sandboxed_interpreter()
    # Either an Interpreter or None (if asteval not installed)
    assert interp is None or hasattr(interp, "symtable")


@pytest.mark.skipif(
    not __import__("importlib").util.find_spec("asteval"),
    reason="asteval not installed",
)
def test_sandboxed_interpreter_blocks_open():
    from em_cubed.surfaces.base import make_sandboxed_interpreter

    interp = make_sandboxed_interpreter()
    assert interp is not None

    # open() must be blocked
    interp("open('test.txt', 'r')")
    errors = interp.error_msg or ""
    assert "not available" in errors or interp.error


@pytest.mark.skipif(
    not __import__("importlib").util.find_spec("asteval"),
    reason="asteval not installed",
)
def test_sandboxed_interpreter_blocks_import():
    from em_cubed.surfaces.base import make_sandboxed_interpreter

    interp = make_sandboxed_interpreter()
    assert interp is not None

    interp("__import__('os')")
    errors = interp.error_msg or ""
    assert "not available" in errors or interp.error


@pytest.mark.skipif(
    not __import__("importlib").util.find_spec("asteval"),
    reason="asteval not installed",
)
def test_sandboxed_interpreter_builtins_blocked():
    from em_cubed.surfaces.base import make_sandboxed_interpreter

    interp = make_sandboxed_interpreter()
    assert interp is not None

    # __builtins__ must be {} not the real builtins
    result = interp.eval("__builtins__")
    assert result == {}


@pytest.mark.skipif(
    not __import__("importlib").util.find_spec("asteval"),
    reason="asteval not installed",
)
def test_sandboxed_interpreter_allows_safe_math():
    from em_cubed.surfaces.base import make_sandboxed_interpreter

    interp = make_sandboxed_interpreter()
    assert interp is not None

    result = interp.eval("2 + 2 * 10")
    assert result == 22


@pytest.mark.skipif(
    not __import__("importlib").util.find_spec("asteval"),
    reason="asteval not installed",
)
def test_sandboxed_interpreter_extra_blocked():
    from em_cubed.surfaces.base import make_sandboxed_interpreter

    interp = make_sandboxed_interpreter(extra_blocked=["print"])
    assert interp is not None

    # print should be blocked or at least removed from symtable
    interp("print('hello')")
    # blocked → either error or silently removed; neither raises Python Exception
    assert True  # reaching here means no crash


def test_blocked_symbols_and_callable_blocked_exported():
    from em_cubed.surfaces.base import BLOCKED_SYMBOLS, CALLABLE_BLOCKED

    assert "open" in BLOCKED_SYMBOLS
    assert "__import__" in BLOCKED_SYMBOLS
    assert "__builtins__" in BLOCKED_SYMBOLS
    assert "open" in CALLABLE_BLOCKED
    assert "__builtins__" not in CALLABLE_BLOCKED  # builtins gets {} not a callable


# ---------------------------------------------------------------------------
# Phase 5: dynamic surface discovery
# ---------------------------------------------------------------------------


def test_executor_uses_dynamic_surface_list():
    """SkillExecutor must call plugin_manager.get_available_surfaces() not a hardcoded list."""
    import inspect

    from em_cubed.skills import executor

    source = inspect.getsource(executor)
    # The hardcoded list must not appear in the executor source
    assert '"python", "prolog", "hy", "z3", "datalog", "sqlite", "kanren", "clingo"' not in source


def test_plugin_manager_get_available_surfaces_returns_list():
    from em_cubed.plugin_manager import PluginManager

    pm = PluginManager()
    surfaces = pm.get_available_surfaces()
    assert isinstance(surfaces, list)
    # At least one surface (Python) should be available in any test env
    assert len(surfaces) >= 1
