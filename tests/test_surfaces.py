import pytest
from em_cubed.surfaces import PythonSurface


class TestPythonSurface:
    @pytest.mark.asyncio
    async def test_execute_simple(self):
        surface = PythonSurface()
        result = await surface.execute("1 + 1", {})
        assert result["status"] == "ok"
        assert result["value"] == 2

    @pytest.mark.asyncio
    async def test_execute_with_context(self):
        surface = PythonSurface()
        result = await surface.execute("x + y", {"x": 10, "y": 20})
        assert result["status"] == "ok"
        assert result["value"] == 30

    @pytest.mark.asyncio
    async def test_execute_statement(self):
        surface = PythonSurface()
        result = await surface.execute("z = 5\nz * 2", {})
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_extract_tags(self):
        source = """
def hello():
    pass

def world():
    return 42
"""
        tags = PythonSurface.extract_tags(source)
        assert "hello" in tags
        assert "world" in tags

    @pytest.mark.asyncio
    async def test_health(self):
        surface = PythonSurface()
        assert await surface.health() is True
