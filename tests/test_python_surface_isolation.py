"""Tests for PythonSurface sandbox correctness and process isolation.

These tests verify:
1. Safe arithmetic and standard builtins work correctly.
2. Dangerous builtins (open, __import__, eval, exec) are blocked and return
   a controlled error dict rather than propagating an exception.
3. An infinite-loop snippet times out within the expected window and leaves
   no zombie child processes behind.
"""

from __future__ import annotations

import asyncio
import os
import time

import psutil
import pytest

try:
    from em_cubed.surfaces.python_surface import PythonSurface, run_isolated_eval

    _available = PythonSurface().available
except ImportError:
    _available = False

pytestmark = pytest.mark.skipif(not _available, reason="asteval not available")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _child_pids_before() -> set[int]:
    """Return PIDs of all current child processes of this test process."""
    try:
        proc = psutil.Process(os.getpid())
        return {c.pid for c in proc.children(recursive=True)}
    except Exception:  # noqa: BLE001
        return set()


# ---------------------------------------------------------------------------
# A1 — Basic evaluation succeeds
# ---------------------------------------------------------------------------

class TestEvalBasic:
    @pytest.mark.asyncio
    async def test_arithmetic(self):
        surface = PythonSurface(timeout=10.0)
        result = await surface.execute("1 + 1", {})
        assert result["status"] == "ok", f"Unexpected result: {result}"
        assert result["value"] == 2

    @pytest.mark.asyncio
    async def test_len_builtin(self):
        surface = PythonSurface(timeout=10.0)
        result = await surface.execute("len([1, 2, 3])", {})
        assert result["status"] == "ok", f"Unexpected result: {result}"
        assert result["value"] == 3

    @pytest.mark.asyncio
    async def test_context_injection(self):
        surface = PythonSurface(timeout=10.0)
        result = await surface.execute("x + y", {"x": 10, "y": 20})
        assert result["status"] == "ok", f"Unexpected result: {result}"
        assert result["value"] == 30

    @pytest.mark.asyncio
    async def test_list_comprehension(self):
        surface = PythonSurface(timeout=10.0)
        result = await surface.execute("[i * 2 for i in range(5)]", {})
        assert result["status"] == "ok", f"Unexpected result: {result}"
        assert result["value"] == [0, 2, 4, 6, 8]

    @pytest.mark.asyncio
    async def test_string_ops(self):
        surface = PythonSurface(timeout=10.0)
        result = await surface.execute("str(42).zfill(5)", {})
        assert result["status"] == "ok", f"Unexpected result: {result}"
        assert result["value"] == "00042"

    @pytest.mark.asyncio
    async def test_multiline_with_result_var(self):
        surface = PythonSurface(timeout=10.0)
        code = "z = 5\nresult = z * 2"
        result = await surface.execute(code, {})
        assert result["status"] == "ok", f"Unexpected result: {result}"
        assert result["value"] == 10


# ---------------------------------------------------------------------------
# A2 — Restricted builtins are blocked
# ---------------------------------------------------------------------------

class TestEvalRestricted:
    """Each dangerous builtin must return status='error' with a controlled message."""

    def _assert_blocked(self, result: dict, symbol: str) -> None:
        assert result["status"] == "error", (
            f"Expected 'error' for '{symbol}' but got: {result}"
        )
        msg = result.get("message", "")
        # Accept any of these message patterns from asteval's ExceptionHolder:
        #   "Error running function 'exec' with args ..."  (our wrapper was called)
        #   "'exec' is not available in the sandboxed environment"  (direct RuntimeError)
        #   "name 'exec' is not defined"  (NameError — symbol was fully removed)
        assert (
            symbol in msg
            or "not available" in msg
            or "not defined" in msg
            or "Error running function" in msg
            or "blocked" in msg.lower()
        ), (f"Error message for '{symbol}' is unexpected: {msg!r}")


    @pytest.mark.asyncio
    async def test_open_blocked(self):
        surface = PythonSurface(timeout=10.0)
        result = await surface.execute("open('test.txt', 'r')", {})
        self._assert_blocked(result, "open")

    @pytest.mark.asyncio
    async def test_import_blocked(self):
        surface = PythonSurface(timeout=10.0)
        result = await surface.execute("__import__('os')", {})
        self._assert_blocked(result, "__import__")

    @pytest.mark.asyncio
    async def test_eval_blocked(self):
        surface = PythonSurface(timeout=10.0)
        result = await surface.execute("eval('1+1')", {})
        self._assert_blocked(result, "eval")

    @pytest.mark.asyncio
    async def test_exec_blocked(self):
        surface = PythonSurface(timeout=10.0)
        result = await surface.execute("exec('x=1')", {})
        self._assert_blocked(result, "exec")

    @pytest.mark.asyncio
    async def test_compile_blocked(self):
        surface = PythonSurface(timeout=10.0)
        result = await surface.execute("compile('1+1', '<>', 'eval')", {})
        self._assert_blocked(result, "compile")

    @pytest.mark.asyncio
    async def test_breakpoint_blocked(self):
        surface = PythonSurface(timeout=10.0)
        result = await surface.execute("breakpoint()", {})
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_builtins_not_accessible(self):
        """Confirm __builtins__ is restricted (cannot access open via __builtins__)."""
        surface = PythonSurface(timeout=10.0)
        result = await surface.execute("__builtins__['open']('x')", {})
        # Either the key is missing or the call fails — both are acceptable.
        assert result["status"] == "error"


# ---------------------------------------------------------------------------
# A3 — Timeout enforcement
# ---------------------------------------------------------------------------

class TestTimeoutTerminates:
    """Verify that timed-out evaluations are reported correctly.

    Architecture note
    -----------------
    The async ``PythonSurface.execute()`` path uses a thread executor with
    ``asyncio.wait_for`` for timeout (advisory — the thread may finish later
    but the caller receives the timeout error immediately).

    The synchronous ``run_isolated_eval()`` path uses a spawned child process
    with hard ``terminate()`` enforcement — no zombie can remain.
    """

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)  # outer guard: test must complete within 30 s
    async def test_infinite_loop_returns_timeout(self):
        """An infinite loop must produce a timeout error dict, not hang the caller."""
        surface = PythonSurface(timeout=2.0)
        t0 = time.monotonic()
        result = await surface.execute("while True: pass", {})
        elapsed = time.monotonic() - t0

        assert result["status"] == "error", f"Expected error, got: {result}"
        msg = result.get("message", "")
        assert "timed out" in msg.lower() or "timeout" in msg.lower(), (
            f"Error message should mention timeout, got: {msg!r}"
        )
        # Async path: asyncio.wait_for fires at timeout; add 5 s OS buffer.
        assert elapsed < 10.0, f"Took too long to time out: {elapsed:.1f}s"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_no_new_processes_from_async_path(self):
        """The async execute() path must NOT spawn child processes (thread-only)."""
        pids_before = _child_pids_before()

        surface = PythonSurface(timeout=2.0)
        result = await surface.execute("while True: pass", {})
        assert result["status"] == "error"

        # Allow asyncio to settle.
        await asyncio.sleep(0.5)

        pids_after = _child_pids_before()
        new_pids = pids_after - pids_before
        assert len(new_pids) == 0, (
            f"Unexpected child processes spawned by async execute(): {new_pids}"
        )

    def test_run_isolated_eval_timeout_sync(self):
        """Synchronous run_isolated_eval enforces timeout via process termination."""
        t0 = time.monotonic()
        result = run_isolated_eval("while True: pass", {}, timeout=2.0)
        elapsed = time.monotonic() - t0

        assert result["status"] == "error"
        msg = result.get("message", "")
        assert "timed out" in msg.lower() or "timeout" in msg.lower(), (
            f"Expected timeout message, got: {msg!r}"
        )
        assert elapsed < 10.0, f"sync timeout took too long: {elapsed:.1f}s"

    def test_run_isolated_eval_no_zombie(self):
        """After run_isolated_eval timeout, no child process should remain."""
        pids_before = _child_pids_before()

        result = run_isolated_eval("while True: pass", {}, timeout=2.0)
        assert result["status"] == "error"

        import time as _time
        _time.sleep(1.0)  # allow OS to reap the process

        pids_after = _child_pids_before()
        new_pids = pids_after - pids_before
        assert len(new_pids) == 0, (
            f"Zombie/lingering pids after run_isolated_eval timeout: {new_pids}"
        )

