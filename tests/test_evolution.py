"""Unit tests for SkillEvolutionEngine."""

from dataclasses import dataclass

from em_cubed.loopy.audit import TrajectoryAuditor
from em_cubed.loopy.base import BaseLoopySkill
from em_cubed.loopy.evolution import SkillEvolutionEngine
from em_cubed.loopy.runner import LoopySkillRunner


@dataclass
class RetryState:
    attempt: int


class FlakySkill(BaseLoopySkill[RetryState, str]):

    def initialize_state(self, *args, **kwargs) -> RetryState:
        return RetryState(attempt=0)

    def mutate(self, state: RetryState, iteration: int) -> tuple[RetryState, str]:
        state.attempt = iteration
        return state, f"Attempt {iteration}"

    def verify(self, state: RetryState) -> tuple[bool, str]:
        if state.attempt >= 2:
            return True, "Passed on attempt 2"
        return False, "Failed constraint check on attempt 1"

    def extract_result(self, state: RetryState) -> str:
        return "Done"


def test_skill_evolution_engine():
    skill = FlakySkill(max_iterations=3)
    res = LoopySkillRunner.execute(skill)

    audit = TrajectoryAuditor.generate_audit_report("FlakySkill", res)

    engine = SkillEvolutionEngine()
    engine.record_audit(audit)

    directive = engine.Evolve_skill("FlakySkill")
    assert directive.skill_name == "FlakySkill"
    assert len(directive.preventative_rules) == 1
    assert "Failed constraint check" in directive.preventative_rules[0]
