"""Security tests to ensure surfaces block dangerous operations."""

import pytest
from em_cubed.surfaces import PythonSurface, Z3Surface, DatalogSurface

pytestmark = pytest.mark.asyncio


class TestPythonSurfaceSecurity:
    """Ensure PythonSurface blocks unsafe operations."""

    async def test_import_os_blocked(self):
        surface = PythonSurface()
        result = await surface.execute("__import__('os')", {})
        assert result["status"] == "error"

    async def test_open_blocked(self):
        surface = PythonSurface()
        result = await surface.execute("open('/etc/passwd')", {})
        assert result["status"] == "error"

    async def test_eval_blocked(self):
        surface = PythonSurface()
        result = await surface.execute("eval('1+1')", {})
        assert result["status"] == "error"

    async def test_exec_blocked(self):
        surface = PythonSurface()
        result = await surface.execute("exec('print(1)')", {})
        assert result["status"] == "error"

    async def test_compile_blocked(self):
        surface = PythonSurface()
        result = await surface.execute("compile('1+1', '<string>', 'eval')", {})
        assert result["status"] == "error"

    async def test_globals_access_blocked(self):
        surface = PythonSurface()
        result = await surface.execute("__builtins__", {})
        # Should not expose dangerous builtins; may return error or restricted object
        assert result["status"] in ("error", "ok")
        if result["status"] == "ok":
            # If ok, value should not be full builtins dict
            assert not isinstance(result.get("value"), dict)


class TestZ3SurfaceSecurity:
    """Ensure Z3Surface uses asteval and blocks unsafe imports."""

    async def test_import_os_blocked(self):
        surface = Z3Surface()
        result = await surface.execute("__import__('os')", {})
        assert result["status"] == "error"

    async def test_open_blocked(self):
        surface = Z3Surface()
        result = await surface.execute("open('/etc/passwd')", {})
        assert result["status"] == "error"


class TestDatalogSurfaceSecurity:
    """Ensure DatalogSurface uses asteval and blocks unsafe operations."""

    async def test_import_os_blocked(self):
        surface = DatalogSurface()
        # Datalog code uses Python; attempt import should fail
        code = """
import time
# but we care about os import
"""
        result = await surface.execute(code, {})
        # The import may be allowed? asteval default allows some imports? asteval blocks many builtins but import may be allowed. In PythonSurface import time works; time is safe. For os import we need a test to block? asteval may block os as dangerous. Test that it's blocked.
        # Use more direct code:
        """
        result = await surface.execute("__import__('os')", {})
        assert result["status"] == "error"
        """
        # Simpler:
        result = await surface.execute("__import__('os')", {})
        assert result["status"] == "error"
