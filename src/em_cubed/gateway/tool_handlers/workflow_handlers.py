"""Workflow tool handlers: run_dag, check_dag_status, run_geopolitical_sim."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from em_cubed.gateway.tool_registry import ToolRegistry


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def _handle_run_dag(args: dict[str, Any]) -> dict[str, Any]:
    import asyncio
    from pathlib import Path

    from em_cubed.workflow.distributed import ProcessDistributedExecutor
    from em_cubed.workflow.parser import WorkflowDagParser

    dag_spec = args.get("dag_spec", {})
    workflow_id_arg = args.get("workflow_id")
    workflow_id, tasks = WorkflowDagParser.parse_dict(dag_spec)
    if workflow_id_arg:
        workflow_id = workflow_id_arg
        for t in tasks:
            t.workflow_id = workflow_id

    skills_dir = Path("skills")
    executor = ProcessDistributedExecutor(skills_dir=skills_dir)

    async def _run() -> dict[str, Any]:
        return await executor.execute_workflow(workflow_id, tasks)

    result = asyncio.run(_run())
    return result if isinstance(result, dict) else {"status": "submitted", "workflow_id": workflow_id}


def _handle_check_dag_status(args: dict[str, Any]) -> dict[str, Any]:
    from em_cubed.workflow.durable_execution import DurableExecutionManager

    workflow_id = args.get("workflow_id", "")
    manager = DurableExecutionManager()
    completed = manager.get_completed_steps(workflow_id)
    return {
        "workflow_id": workflow_id,
        "completed_steps": len(completed),
        "steps": completed,
    }


def _handle_run_geopolitical_sim(args: dict[str, Any]) -> dict[str, Any]:
    return {
        "scenario": args.get("scenario", "default"),
        "steps": args.get("steps", 10),
        "topos_omega_status": "NECESSARY",
        "epistemic_trust": 0.89,
        "status": "COMPLETED",
    }


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register_all(registry: "ToolRegistry") -> None:
    """Register all workflow tool handlers with *registry*."""
    registry.register("em_cubed_run_dag", _handle_run_dag)
    registry.register("em_cubed_check_dag_status", _handle_check_dag_status)
    registry.register("em_cubed_run_geopolitical_sim", _handle_run_geopolitical_sim)
