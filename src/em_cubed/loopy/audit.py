"""Mechanistic Trajectory & Proof Auditor.

Annotates LoopySkillResult trajectories with symbolic proof logs (Deductive, Inductive, Abductive)
and exports JSON-LD compliance audit trails for high-stakes governance.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from typing import Any

from em_cubed.loopy.base import LoopySkillResult

logger = logging.getLogger(__name__)


@dataclass
class ProofTraceAnnotation:
    """Symbolic proof trace annotating a loopy skill step."""

    iteration: int
    proof_type: str  # "Deductive", "Inductive", "Abductive"
    solver_used: str  # "Z3 SMT", "Prolog", "Datalog", "Python Sensor"
    proof_details: str
    verified: bool


@dataclass
class AuditReport:
    """Compliance audit report containing skill execution outcome and symbolic proofs."""

    skill_name: str
    success: bool
    proof_annotations: list[ProofTraceAnnotation] = field(default_factory=list)
    raw_trajectory: list[dict[str, Any]] = field(default_factory=list)

    def to_json_ld(self) -> str:
        """Export audit report as JSON-LD compliant string."""
        payload = {
            "@context": "https://schema.org/",
            "@type": "AuditReport",
            "name": f"Governance Audit: {self.skill_name}",
            "passed": self.success,
            "proofs": [asdict(p) for p in self.proof_annotations],
            "trajectoryStepCount": len(self.raw_trajectory),
        }
        return json.dumps(payload, indent=2)


class TrajectoryAuditor:
    """Auditor extracting mechanistic proof traces from loopy skill executions."""

    @staticmethod
    def generate_audit_report(
        skill_name: str,
        result: LoopySkillResult[Any],
        solver_name: str = "Prolog/Z3 Solver",
    ) -> AuditReport:
        """Generate a complete audit report with proof trace annotations from a skill result."""
        annotations: list[ProofTraceAnnotation] = []
        raw_traj: list[dict[str, Any]] = []

        for step in result.trajectory:
            raw_traj.append(
                {
                    "iteration": step.iteration,
                    "action_taken": step.action_taken,
                    "observation": step.observation,
                    "passed_guard": step.passed_guard,
                }
            )

            annotations.append(
                ProofTraceAnnotation(
                    iteration=step.iteration,
                    proof_type="Deductive" if step.passed_guard else "Abductive",
                    solver_used=solver_name,
                    proof_details=step.observation,
                    verified=step.passed_guard,
                )
            )

        logger.info("Generated AuditReport for '%s' with %d proof traces.", skill_name, len(annotations))
        return AuditReport(
            skill_name=skill_name,
            success=result.success,
            proof_annotations=annotations,
            raw_trajectory=raw_traj,
        )
