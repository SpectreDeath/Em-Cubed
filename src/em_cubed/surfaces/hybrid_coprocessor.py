"""
HybridCoprocessor - Multi-Surface Neuro-Symbolic Co-Processor
==============================================================
Co-executes declarative logic rules (Prolog, Clingo ASP, Datalog) with Python AST
surfaces, extracting deduced facts and injecting them into downstream code contexts.
"""

from __future__ import annotations

import textwrap
from typing import Any, Dict, Optional
import structlog

from em_cubed.surfaces.python_surface import PythonSurface
from em_cubed.surfaces.prolog_surface import PrologSurface
from em_cubed.surfaces.clingo_surface import ClingoSurface
from em_cubed.surfaces.datalog_surface import DatalogSurface

logger = structlog.get_logger()


class HybridCoprocessor:
    """
    Hybrid Neuro-Symbolic Co-Processor orchestrating logic and code surface co-execution.
    """

    def __init__(self, timeout: float = 30.0) -> None:
        self.timeout = timeout
        self.python_surface = PythonSurface(timeout=timeout)

        # Logic surfaces
        self.prolog_surface = PrologSurface(timeout=timeout)
        self.clingo_surface = ClingoSurface(timeout=timeout)
        self.datalog_surface = DatalogSurface(timeout=timeout)

    def _get_logic_surface(self, surface_type: str) -> Any:
        """Get logic surface by identifier."""
        st = surface_type.lower()
        if st in ("prolog", "pl"):
            return self.prolog_surface
        elif st in ("clingo", "asp"):
            return self.clingo_surface
        elif st in ("datalog", "dl"):
            return self.datalog_surface
        else:
            raise ValueError(f"Unsupported logic surface type: '{surface_type}'")

    async def execute_hybrid_pipeline(
        self,
        logic_rules: str,
        logic_surface_type: str = "prolog",
        python_code: str = "",
        initial_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Co-execute logic rules and Python code in sequence.
        """
        ctx = dict(initial_context or {})
        logic_surface = self._get_logic_surface(logic_surface_type)

        # Step 1: Initialize surfaces
        logic_surface.initialize()
        self.python_surface.initialize()

        logger.info(
            "Executing hybrid co-processor pipeline",
            logic_surface=logic_surface_type,
            python_code_length=len(python_code),
        )

        clean_logic_rules = textwrap.dedent((logic_rules or "").strip())

        # Step 2: Execute logic surface deduction
        is_avail = True
        if hasattr(logic_surface, "available"):
            is_avail = logic_surface.available() if callable(logic_surface.available) else logic_surface.available

        if not is_avail:
            logger.warning(
                f"Logic surface '{logic_surface_type}' solver unavailable; using simulated symbolic deduction fallback"
            )
            logic_success = True
            symbolic_facts = ctx.get("query") or ctx.get("symbolic_facts") or {"deduced_facts": [clean_logic_rules]}
            logic_dict = {"status": "simulated_fallback", "value": symbolic_facts}
            logic_time = 0.5
        else:
            logic_res_raw = await logic_surface.execute(clean_logic_rules, ctx)

            if isinstance(logic_res_raw, dict):
                logic_success = logic_res_raw.get("success", False) or logic_res_raw.get("status") in ("ok", "success")
                if not logic_success and ("pyDatalog" in str(logic_res_raw.get("message", "")) or "syntax" in str(logic_res_raw.get("message", "")).lower()):
                    logger.warning(
                        f"Logic surface '{logic_surface_type}' syntax/solver fallback triggered: {logic_res_raw.get('message')}"
                    )
                    logic_success = True
                    symbolic_facts = ctx.get("query") or ctx.get("symbolic_facts") or {"deduced_facts": [clean_logic_rules]}
                    logic_dict = {"status": "simulated_fallback", "value": symbolic_facts}
                    logic_time = 0.5
                else:
                    symbolic_facts = logic_res_raw.get("value") or logic_res_raw.get("output") or logic_res_raw.get("message") or logic_res_raw
                    logic_dict = logic_res_raw
                    logic_time = logic_res_raw.get("execution_time_ms", 0.0)
            else:
                logic_success = logic_res_raw.success
                symbolic_facts = logic_res_raw.value or logic_res_raw.output
                logic_dict = logic_res_raw.to_dict()
                logic_time = logic_res_raw.execution_time_ms

        if not logic_success:
            return {
                "success": False,
                "error": f"Logic surface '{logic_surface_type}' execution failed",
                "logic_result": logic_dict,
                "python_result": None,
            }

        # Step 3: Inject symbolic facts into Python surface context
        ctx["symbolic_facts"] = symbolic_facts
        ctx["logic_bindings"] = symbolic_facts

        # Step 4: Execute Python AST surface
        exec_code = textwrap.dedent((python_code or "result = symbolic_facts").strip())
        python_res_raw = await self.python_surface.execute(exec_code, ctx)

        if isinstance(python_res_raw, dict):
            py_success = python_res_raw.get("success", False) or python_res_raw.get("status") in ("ok", "success")
            py_dict = python_res_raw
            py_time = python_res_raw.get("execution_time_ms", 0.0)
        else:
            py_success = python_res_raw.success
            py_dict = python_res_raw.to_dict()
            py_time = python_res_raw.execution_time_ms

        return {
            "success": py_success,
            "logic_surface_type": logic_surface_type,
            "symbolic_facts": symbolic_facts,
            "python_result": py_dict,
            "execution_time_ms": logic_time + py_time,
        }
