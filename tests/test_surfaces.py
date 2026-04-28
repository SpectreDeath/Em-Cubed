import pytest
import asyncio
from surfaces.python_runner import PythonRunner

class TestPythonRunner:
    @pytest.mark.asyncio
    async def test_execute_simple(self):
        runner = PythonRunner()
        result = await runner.execute('1 + 1', {})
        assert result.status == 'ok'
        assert result.value == 2

    @pytest.mark.asyncio
    async def test_execute_with_context(self):
        runner = PythonRunner()
        result = await runner.execute('x + y', {'x': 10, 'y': 20})
        assert result.status == 'ok'
        assert result.value == 30
