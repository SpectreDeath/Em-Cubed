"""Autonomous Skill Evolution & Self-Refinement Engine.

Analyzes past AuditReport proof traces to extract failure patterns and automatically synthesize
pre-execution prompt steering directives, optimizing future loopy skill runs for 1-step convergence.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from em_cubed.loopy.audit import AuditReport

logger = logging.getLogger(__name__)


@dataclass
class EvolvedSkillDirective:
    """Refined prompt steering directives synthesized from historical audit trails."""

    skill_name: str
    preventative_rules: list[str] = field(default_factory=list)
    optimized_retry_count: int = 1


class SkillEvolutionEngine:
    """Engine executing autonomous self-refinement over skill execution histories."""

    def __init__(self) -> None:
        self.history: list[AuditReport] = []

    def record_audit(self, report: AuditReport) -> None:
        """Record an execution audit report into the evolution history."""
        self.history.append(report)

    def Evolve_skill(self, skill_name: str) -> EvolvedSkillDirective:
        """Analyze past audit reports for skill_name and synthesize optimized prompt directives.

        Parameters
        ----------
        skill_name : str
            Target loopy skill name.

        Returns
        -------
        EvolvedSkillDirective
            Synthesized steering directives to eliminate retries.
        """
        logger.info("Analyzing historical audit reports for skill '%s'...", skill_name)
        preventative_rules: list[str] = []

        skill_reports = [r for r in self.history if r.skill_name == skill_name]

        for report in skill_reports:
            for proof in report.proof_annotations:
                if not proof.verified and proof.proof_details:
                    rule = f"PREVENTIVE DIRECTIVE (From Step {proof.iteration}): Avoid '{proof.proof_details}'"
                    if rule not in preventative_rules:
                        preventative_rules.append(rule)

        logger.info("Evolved %d preventative steering rules for skill '%s'.", len(preventative_rules), skill_name)
        return EvolvedSkillDirective(
            skill_name=skill_name,
            preventative_rules=preventative_rules,
            optimized_retry_count=1 if preventative_rules else 3,
        )
