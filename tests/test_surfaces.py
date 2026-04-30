import pytest
from unittest.mock import patch
from em_cubed.surfaces import PythonSurface, HySurface, Z3Surface, DatalogSurface


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
        surface = DatalogSurface()
        assert isinstance(await surface.health(), bool)


class TestZ3Surface:

    @pytest.mark.asyncio
    async def test_execute_simple_sat(self):
        surface = Z3Surface()
        if not surface.available:
            pytest.skip("Z3 not available")
        # Simple satisfiability problem: x > 5
        code = """
solver = Solver()
x = Int('x')
solver.add(x > 5)
result = solver.check()
"""
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        # Should be satisfiable
        assert result["value"]["status"] == "sat"

    @pytest.mark.asyncio
    async def test_execute_simple_unsat(self):
        surface = Z3Surface()
        if not surface.available:
            pytest.skip("Z3 not available")
        # Unsatisfiable problem: x > 5 and x < 3
        code = """
solver = Solver()
x = Int('x')
solver.add(x > 5)
solver.add(x < 3)
result = solver.check()
"""
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        # Should be unsatisfiable
        assert result["value"]["status"] == "unsat"

    @pytest.mark.asyncio
    async def test_execute_optimization(self):
        surface = Z3Surface()
        if not surface.available:
            pytest.skip("Z3 not available")
        # Simple optimization: maximize x where x < 10
        code = """
solver = Optimize()
x = Int('x')
solver.add(x < 10)
solver.maximize(x)
result = solver.check()
"""
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        # Should be satisfiable
        assert result["value"]["status"] == "sat"

    def test_extract_tags(self):
        surface = Z3Surface()
        z3_source = """
solver = Solver()
x = Int('x')
y = Real('y')
solver.add(x > 0)
solver.add(y < 10.0)
"""
        tags = surface.extract_tags(z3_source)
        # Should extract variable types and assertion indicators
        assert "Int" in tags or "Real" in tags
        assert "assertion" in tags

    @pytest.mark.asyncio
    async def test_execute_unavailable(self):
        surface = Z3Surface()
        # Mock availability to False
        with patch.object(surface, '_check_availability', return_value=False):
            result = await surface.execute("solver = Solver()", {})
            assert result["status"] == "error"
            assert "z3 not available" in result["message"]

    @pytest.mark.asyncio
    async def test_health(self):
        surface = Z3Surface()
        assert isinstance(await surface.health(), bool)


class TestDatalogSurface:

    @pytest.mark.asyncio
    async def test_execute_simple_fact(self):
        surface = DatalogSurface()
        if not surface.available:
            pytest.skip("pyDatalog not available")
        # Simple fact assertion
        code = """
from pyDatalog import pyDatalog
pyDatalog.create_atoms('likes')
+ (likes['john', 'pizza'])
"""
        result = await surface.execute(code)
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_execute_simple_rule(self):
        surface = DatalogSurface()
        if not surface.available:
            pytest.skip("pyDatalog not available")
        # Simple rule definition - create variables first
        code = """
from pyDatalog import pyDatalog
pyDatalog.create_atoms('parent', 'ancestor')
pyDatalog.create_terms('X, Y')
ancestor[X, Y] = parent[X, Y]
"""
        result = await surface.execute(code)
        assert result["status"] == "ok"

    def test_extract_tags(self):
        surface = DatalogSurface()
        datalog_source = """
parent(X, Y) :- mother(X, Y).
parent(X, Y) :- father(X, Y).
mother('mary', 'john').
?- parent(X, Y).
"""
        tags = surface.extract_tags(datalog_source)
        # Should extract predicate names
        assert "parent" in tags
        assert "mother" in tags
        assert "father" in tags

    @pytest.mark.asyncio
    async def test_execute_unavailable(self):
        surface = DatalogSurface()
        # Mock availability to False
        with patch.object(surface, '_check_availability', return_value=False):
            result = await surface.execute("parent('john', 'mary')")
            assert result["status"] == "error"
            assert "pyDatalog not available" in result["message"]

    @pytest.mark.asyncio
    async def test_health(self):
        surface = DatalogSurface()
        assert isinstance(await surface.health(), bool)
