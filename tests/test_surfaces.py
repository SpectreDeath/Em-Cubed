import pytest
from unittest.mock import patch
from em_cubed.surfaces import PythonSurface, HySurface, PrologSurface


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

    @pytest.mark.asyncio
    async def test_execute_unavailable(self):
        surface = PythonSurface()
        # Mock availability to False
        with patch.object(surface, '_check_availability', return_value=False):
            result = await surface.execute("1 + 1", {})
            assert result["status"] == "error"
            assert "asteval not available" in result["message"]

    @pytest.mark.asyncio
    async def test_execute_long_error(self):
        surface = PythonSurface()
        # Create a long error message
        long_code = "raise Exception('This is a very long error message that should be handled properly and not cause any issues with the error reporting system. ' * 10)"
        result = await surface.execute(long_code, {})
        assert result["status"] == "error"
        assert "message" in result

    @pytest.mark.asyncio
    async def test_execute_asteval_exception(self):
        surface = PythonSurface()
        # This should trigger the general exception handler
        result = await surface.execute("import nonexistent_module", {})
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_availability_check_warning(self):
        with patch('importlib.util.find_spec', return_value=None):
            surface = PythonSurface()
            assert surface.available is False

class TestHySurface:

    @pytest.mark.asyncio
    async def test_execute_simple(self):
        surface = HySurface()
        if not surface.available:
            pytest.skip("Hy not available")
        result = await surface.execute("(+ 1 2)")
        assert result["status"] == "ok"
        assert result["value"] == 3

    @pytest.mark.asyncio
    async def test_execute_multiple_forms(self):
        surface = HySurface()
        if not surface.available:
            pytest.skip("Hy not available")
        result = await surface.execute("(setv x 10)\n(* x 2)")
        assert result["status"] == "ok"
        assert result["value"] == 20

    @pytest.mark.asyncio
    async def test_execute_with_error(self):
        surface = HySurface()
        if not surface.available:
            pytest.skip("Hy not available")
        result = await surface.execute("(invalid-function)")
        assert result["status"] == "error"
        assert "message" in result

    @pytest.mark.asyncio
    async def test_execute_unavailable(self):
        surface = HySurface()
        # Mock availability to False
        with patch.object(surface, '_check_availability', return_value=False):
            result = await surface.execute("(+ 1 2)")
            assert result["status"] == "error"
            assert "Hy not available" in result["message"]

    def test_extract_tags(self):
        surface = HySurface()
        hy_source = """
(defn add [x y]
  (+ x y))

(defn multiply [a b]
  (* a b))
"""
        tags = surface.extract_tags(hy_source)
        assert "add" in tags
        assert "multiply" in tags

    @pytest.mark.asyncio
    async def test_health(self):
        surface = HySurface()
        assert isinstance(await surface.health(), bool)

class TestPrologSurface:

    @pytest.mark.asyncio
    async def test_execute_assert(self):
        surface = PrologSurface()
        if not surface.available:
            pytest.skip("PySWIP not available")
        result = await surface.execute("parent(john, mary).")
        assert result["status"] == "ok"
        assert "asserted successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_execute_query(self):
        surface = PrologSurface()
        if not surface.available:
            pytest.skip("PySWIP not available")
        # First assert some facts
        await surface.execute("parent(john, mary).")
        await surface.execute("parent(mary, alice).")
        # Then query (without trailing . for query mode)
        result = await surface.execute("parent(john, X)")
        assert result["status"] == "ok"
        assert "result" in result

    @pytest.mark.asyncio
    async def test_execute_unavailable(self):
        surface = PrologSurface()
        with patch.object(surface, '_check_availability', return_value=False):
            result = await surface.execute("test.")
            assert result["status"] == "error"
            assert "PySWIP not available" in result["message"]

    def test_check_availability(self):
        surface = PrologSurface()
        # This will test the _check_availability method
        available = surface.available
        assert isinstance(available, bool)

    def test_extract_tags(self):
        surface = PrologSurface()
        prolog_source = """
parent(X, Y) :- father(X, Y).
father(john, mary).
"""
        tags = surface.extract_tags(prolog_source)
        assert "parent" in tags
        assert "father" in tags

    @pytest.mark.asyncio
    async def test_health(self):
        surface = PrologSurface()
        assert isinstance(await surface.health(), bool)
