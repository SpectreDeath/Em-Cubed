"""Unit tests for TrajectoryAuditor and AuditReport."""

from dataclasses import dataclass
from em_cubed.loopy.audit import TrajectoryAuditor
from em_cubed.loopy.base import BaseLoopySkill
from em_cubed.loopy.runner import LoopySkillRunner


@dataclass
class SimpleState:
    count: int


class SimpleLoopSkill(BaseLoopySkill[SimpleState, int]):

    def initialize_state(self, count: int) -> SimpleState:
        return SimpleState(count=count)

    def mutate(self, state: SimpleState, iteration: int) -> tuple[SimpleState, str]:
        state.count += 1
        return state, f"Incremented count to {state.count}"

    def verify(self, state: SimpleState) -> tuple[bool, str]:
        if state.count >= 2:
            return True, "Count reached target (>= 2)"
        return False, f"Count too low ({state.count})"

    def extract_result(self, state: SimpleState) -> int:
        return state.count


def test_trajectory_auditor_json_ld_export():
    skill = SimpleLoopSkill(max_iterations=3)
    res = LoopySkillRunner.execute(skill, count=0)

    report = TrajectoryAuditor.generate_audit_report("SimpleLoopSkill", res, solver_name="Python Sensor")
    assert report.skill_name == "SimpleLoopSkill"
    assert report.success is True
    assert len(report.proof_annotations) == 2

    json_ld = report.to_json_ld()
    assert "AuditReport" in json_ld
    assert "SimpleLoopSkill" in json_ld
    assert "Deductive" in json_ld
