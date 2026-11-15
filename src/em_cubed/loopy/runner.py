"""Loopy Skill Runner and Execution Scope Controller.

Provides robust runner scopes to execute loopy skills with isolation, timeout guards,
trajectory logging, fault containment, and automated audit/evolution hooks.
"""

from __future__ import annotations

import concurrent.futures
import logging
from collections.abc import Callable
from typing import Any, TypeVar

from em_cubed.loopy.audit import AuditReport, TrajectoryAuditor
from em_cubed.loopy.base import BaseLoopySkill, LoopTrajectory, LoopySkillResult

logger = logging.getLogger(__name__)

T_State = TypeVar("T_State")
T_Result = TypeVar("T_Result")


class LoopySkillRunner:
    """Deep execution scope controller executing loopy skills with resilience, isolation, and audit hooks."""

    @staticmethod
    def execute(
        skill: BaseLoopySkill[T_State, T_Result],
        *args: Any,
        timeout: float | None = None,
        audit_collector: list[AuditReport] | Callable[[AuditReport], None] | None = None,
        evolution_engine: Any | None = None,
        **kwargs: Any,
    ) -> LoopySkillResult[T_Result]:
        """Execute a loopy skill within a controlled, isolated runner scope.

        Parameters
        ----------
        skill : BaseLoopySkill[T_State, T_Result]
            Instantiated loopy skill.
        *args : Any
            Positional arguments passed to skill initialization.
        timeout : float | None
            Optional maximum execution timeout in seconds.
        audit_collector : list or callable | None
            Optional target container or handler to receive the generated AuditReport.
        evolution_engine : Any | None
            Optional SkillEvolutionEngine instance to automatically receive the audit report.
        **kwargs : Any
            Keyword arguments passed to skill initialization.

        Returns
        -------
        LoopySkillResult[T_Result]
            Execution outcome, status, error messages, and trajectory history.
        """
        skill_name = skill.__class__.__name__
        logger.info("LoopySkillRunner dispatching skill: %s (timeout=%s)", skill_name, timeout)

        result: LoopySkillResult[T_Result]
        try:
            if timeout is not None and timeout > 0:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(skill.run, *args, **kwargs)
                    try:
                        result = future.result(timeout=timeout)
                    except TimeoutError:
                        logger.warning("Loopy skill '%s' exceeded timeout of %.2fs", skill_name, timeout)
                        result = LoopySkillResult(
                            success=False,
                            final_output=None,  # type: ignore[arg-type]
                            trajectory=[
                                LoopTrajectory(
                                    iteration=0,
                                    action_taken="execution_timeout_guard",
                                    observation=f"Execution exceeded timeout limit of {timeout}s",
                                    passed_guard=False,
                                    metrics={"timeout_seconds": timeout},
                                )
                            ],
                            error_message=f"Loopy skill execution timed out after {timeout} seconds.",
                        )
            else:
                result = skill.run(*args, **kwargs)

        except Exception as exc:
            logger.exception("Unhandled error during loopy skill '%s' execution: %s", skill_name, exc)
            result = LoopySkillResult(
                success=False,
                final_output=None,  # type: ignore[arg-type]
                trajectory=[
                    LoopTrajectory(
                        iteration=0,
                        action_taken="exception_containment",
                        observation=f"Captured unhandled error: {exc}",
                        passed_guard=False,
                    )
                ],
                error_message=f"Execution failed: {exc}",
            )

        # Automatic audit report generation and dispatch
        try:
            audit_report = TrajectoryAuditor.generate_audit_report(skill_name, result)

            if audit_collector is not None:
                if isinstance(audit_collector, list):
                    audit_collector.append(audit_report)
                elif callable(audit_collector):
                    audit_collector(audit_report)

            if evolution_engine is not None and hasattr(evolution_engine, "record_audit"):
                evolution_engine.record_audit(audit_report)

        except Exception as audit_err:
            logger.warning("Failed to auto-dispatch audit report for '%s': %s", skill_name, audit_err)

        return result

    @classmethod
    def execute_with_audit(
        cls,
        skill: BaseLoopySkill[T_State, T_Result],
        *args: Any,
        timeout: float | None = None,
        evolution_engine: Any | None = None,
        **kwargs: Any,
    ) -> tuple[LoopySkillResult[T_Result], AuditReport]:
        """Execute a loopy skill and return both the execution result and the generated audit report."""
        captured_reports: list[AuditReport] = []
        result = cls.execute(
            skill,
            *args,
            timeout=timeout,
            audit_collector=captured_reports,
            evolution_engine=evolution_engine,
            **kwargs,
        )
        report = (
            captured_reports[0]
            if captured_reports
            else TrajectoryAuditor.generate_audit_report(skill.__class__.__name__, result)
        )
        return result, report

