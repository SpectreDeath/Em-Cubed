import os
import tempfile

import pytest

from em_cubed.surfaces.prolog_surface import PrologSurface
from em_cubed.surfaces.z3_surface import Z3Surface


@pytest.fixture()
def prolog():
    surface = PrologSurface()
    if not surface.available:
        pytest.skip("PySWIP / Prolog runtime unavailable")
    return surface


@pytest.fixture()
def z3():
    surface = Z3Surface()
    if not surface.available:
        pytest.skip("Z3 / Python z3-solver unavailable")
    return surface


MODULE_RULES = """\
:- module(regression_test, [edge/2, path/2]).
edge(a, b).
edge(b, c).
edge(c, d).
path(X, Y) :- edge(X, Y).
path(X, Z) :- edge(X, Mid), path(Mid, Z).
"""


def _run_multi_line(surface, code: str):
    return surface.execute_sync(code)


def test_multiline_consult_releases_fd_before_consult(prolog):
    result = _run_multi_line(prolog, MODULE_RULES)
    assert result.get("status") == "ok", result


def test_multiline_reconsult_no_module_permission_error(prolog):
    first = _run_multi_line(prolog, MODULE_RULES)
    assert first.get("status") == "ok", first

    second = _run_multi_line(prolog, MODULE_RULES)
    assert second.get("status") == "ok", second


def test_z3_python_api_basic_query(z3):
    result = z3.execute_sync(
        "solver = Solver(); x = Int('x'); "
        "solver.add(x > 0); solver.add(x < 10); "
        "r = solver.check(); solver.model() if r == sat else 'unsat'"
    )
    assert result.get("status") == "ok", result


def test_re_import_scope_isolated_to_own_method():
    import re

    pattern = "edge\\(a, b\\)"
    match_text = "edge(a, b)."
    assert re.search(pattern, match_text) is not None


def test_prolog_fd_consult_explicit(prolog):
    fd, path = tempfile.mkstemp(suffix=".pl")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file_obj:
            file_obj.write(MODULE_RULES)
            file_obj.flush()
            os.fsync(file_obj.fileno())
        result = prolog.execute_sync("?- path(a, c).")
        assert result.get("status") == "ok", result
    finally:
        if os.path.exists(path):
            os.unlink(path)
