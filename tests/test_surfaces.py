import pytest
from unittest.mock import patch

# Try to import surfaces, skip tests if dependencies are missing
try:
    from em_cubed.surfaces import PythonSurface, HySurface, Z3Surface, DatalogSurface, JanusSurface, PrologSurface
    _core_surfaces_available = True
    _hy_available = HySurface is not None and HySurface().available
    _z3_available = Z3Surface is not None and Z3Surface().available
    _datalog_available = DatalogSurface is not None and DatalogSurface().available
    _janus_available = JanusSurface is not None and JanusSurface().available
    _prolog_available = PrologSurface is not None and PrologSurface().available
except ImportError:
    PythonSurface = HySurface = Z3Surface = DatalogSurface = JanusSurface = PrologSurface = None
    _core_surfaces_available = False
    _hy_available = False
    _z3_available = False
    _datalog_available = False
    _janus_available = False
    _prolog_available = False

# Skip decorators
requires_hy = pytest.mark.skipif(not _hy_available, reason="HySurface not available")
requires_z3 = pytest.mark.skipif(not _z3_available, reason="Z3Surface not available")
requires_datalog = pytest.mark.skipif(not _datalog_available, reason="DatalogSurface not available")
requires_janus = pytest.mark.skipif(not _janus_available, reason="JanusSurface not available")
requires_prolog = pytest.mark.skipif(not _prolog_available, reason="PrologSurface not available")


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

    def test_extract_tags(self):
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
    async def test_execute_with_math_operations(self):
        surface = PythonSurface()
        result = await surface.execute("4 ** 0.5", {})
        assert result["status"] == "ok"
        assert result["value"] == 2.0

    @pytest.mark.asyncio
    async def test_execute_function_definition(self):
        surface = PythonSurface()
        code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

factorial(5)
"""
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        assert result["value"] == 120

    @pytest.mark.asyncio
    async def test_execute_list_comprehension(self):
        surface = PythonSurface()
        code = "[x**2 for x in range(1, 4)]"
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        assert result["value"] == [1, 4, 9]

    @pytest.mark.asyncio
    async def test_execute_unavailable(self):
        surface = PythonSurface()
        with patch.object(surface, '_check_availability', return_value=False):
            result = await surface.execute("1 + 1", {})
            assert result["status"] == "error"
            assert "not available" in result["message"]


@requires_hy
class TestHySurface:
    @pytest.mark.asyncio
    async def test_execute_simple(self):
        surface = HySurface()
        result = await surface.execute("(+ 1 2)")
        assert result["status"] == "ok"
        assert result["value"] == 3

    @pytest.mark.asyncio
    async def test_execute_multiple_forms(self):
        surface = HySurface()
        result = await surface.execute("(setv x 10)\n(* x 2)")
        assert result["status"] == "ok"
        assert result["value"] == 20

    @pytest.mark.asyncio
    async def test_execute_with_error(self):
        surface = HySurface()
        result = await surface.execute("(invalid-function)")
        assert result["status"] == "error"

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
        assert await surface.health() is True


@requires_z3
class TestZ3Surface:
    @pytest.mark.asyncio
    async def test_execute_simple_sat(self):
        surface = Z3Surface()
        code = """
solver = Solver()
x = Int('x')
solver.add(x > 5)
result = solver.check()
"""
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        assert result["value"]["status"] == "sat"

    @pytest.mark.asyncio
    async def test_execute_simple_unsat(self):
        surface = Z3Surface()
        code = """
solver = Solver()
x = Int('x')
solver.add(x > 5)
solver.add(x < 3)
result = solver.check()
"""
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        assert result["value"]["status"] == "unsat"

    @pytest.mark.asyncio
    async def test_execute_optimization(self):
        surface = Z3Surface()
        code = """
solver = Optimize()
x = Int('x')
solver.add(x < 10)
solver.maximize(x)
result = solver.check()
"""
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        assert result["value"]["status"] == "sat"

    def test_extract_tags(self):
        surface = Z3Surface()
        z3_source = """
x = Int('x')
y = Int('y')
solver = Solver()
solver.add(x > 0)
solver.add(y < 10)
"""
        tags = surface.extract_tags(z3_source)
        assert "Int" in tags
        assert "assertion" in tags

    @pytest.mark.asyncio
    async def test_health(self):
        surface = Z3Surface()
        assert await surface.health() is True


@requires_prolog
class TestPrologSurface:
    @pytest.mark.asyncio
    async def test_execute_simple(self):
        surface = PrologSurface()
        await surface.execute("parent(john, mary).")
        result = await surface.execute("parent(john, X)")
        assert result["status"] == "ok"
        assert result["result"][0]["X"] == "mary"

    def test_extract_tags(self):
        surface = PrologSurface()
        prolog_source = """
parent(john, mary).
grandparent(X, Z) :- parent(X, Y), parent(Y, Z).
"""
        tags = surface.extract_tags(prolog_source)
        assert "parent" in tags
        assert "grandparent" in tags

    @pytest.mark.asyncio
    async def test_health(self):
        surface = PrologSurface()
        assert await surface.health() is True


@requires_datalog
class TestDatalogSurface:
    @pytest.mark.asyncio
    async def test_execute_simple_fact(self):
        surface = DatalogSurface()
        # Test that pyDatalog is available and can be called
        code = "pyDatalog.clear()"
        result = await surface.execute(code)
        assert result["status"] == "ok"

    def test_extract_tags(self):
        surface = DatalogSurface()
        datalog_source = """
parent(X, Y) :- mother(X, Y).
mother('mary', 'john').
"""
        tags = surface.extract_tags(datalog_source)
        assert "parent" in tags
        assert "mother" in tags

    @pytest.mark.asyncio
    async def test_health(self):
        surface = DatalogSurface()
        assert await surface.health() is True


@requires_janus
class TestJanusSurface:
    @pytest.mark.asyncio
    async def test_execute_simple(self):
        surface = JanusSurface()
        await surface.execute("parent(john, mary).")
        result = await surface.execute("parent(john, X)")
        assert result["status"] == "ok"
        assert result["result"]["X"] == "mary"

    def test_extract_tags(self):
        surface = JanusSurface()
        prolog_source = """
parent(john, mary).
grandparent(X, Z) :- parent(X, Y), parent(Y, Z).
"""
        tags = surface.extract_tags(prolog_source)
        assert "parent" in tags
        assert "grandparent" in tags

    @pytest.mark.asyncio
    async def test_health(self):
        surface = JanusSurface()
        assert await surface.health() is True
