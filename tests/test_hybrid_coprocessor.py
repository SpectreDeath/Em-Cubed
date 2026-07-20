"""
Unit Tests for HybridCoprocessor in em-cubed
=============================================
Tests Prolog/Clingo/Datalog logic surface co-execution with Python AST surface.
"""

from __future__ import annotations

import pytest

from em_cubed.plugin_manager import PluginManager
from em_cubed.surfaces.hybrid_coprocessor import HybridCoprocessor


class TestHybridCoprocessor:
    """Test Multi-Surface Hybrid Co-Processor."""

    @pytest.mark.asyncio
    async def test_prolog_python_hybrid_pipeline(self):
        coprocessor = HybridCoprocessor(timeout=10.0)

        prolog_rules = """
        parent(pam, bob).
        parent(tom, bob).
        grandparent(X, Y) :- parent(X, Z), parent(Z, Y).
        """

        python_script = "result = {'facts': symbolic_facts, 'status': 'co_processed'}"

        res = await coprocessor.execute_hybrid_pipeline(
            logic_rules=prolog_rules,
            logic_surface_type="prolog",
            python_code=python_script,
            initial_context={"query": "parent(pam, bob)"},
        )

        assert res["success"] is True
        assert res["logic_surface_type"] == "prolog"
        assert "symbolic_facts" in res
        assert res["python_result"]["status"] == "ok"
        assert res["python_result"]["value"]["status"] == "co_processed"

    @pytest.mark.asyncio
    async def test_datalog_python_hybrid_pipeline(self):
        coprocessor = HybridCoprocessor(timeout=10.0)

        datalog_rules = """
        edge(a, b).
        edge(b, c).
        path(X, Y) :- edge(X, Y).
        """

        python_script = "result = {'count': 1, 'status': 'co_processed'}"

        res = await coprocessor.execute_hybrid_pipeline(
            logic_rules=datalog_rules,
            logic_surface_type="datalog",
            python_code=python_script,
        )

        print("DATALOG PIPELINE RES:", res)
        assert res["success"] is True
        assert res["logic_surface_type"] == "datalog"
        assert res["python_result"]["status"] == "ok"

    def test_plugin_manager_hybrid_coprocessor_factory(self):
        pm = PluginManager()
        coprocessor = pm.get_hybrid_coprocessor(timeout=15.0)

        assert isinstance(coprocessor, HybridCoprocessor)
        assert coprocessor.timeout == 15.0
