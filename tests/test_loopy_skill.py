"""Unit tests for BaseLoopySkill, LoopySkillRunner, and TextLoopMiner."""

from dataclasses import dataclass, field

from em_cubed.loopy.base import BaseLoopySkill
from em_cubed.loopy.miner import TextLoopMiner
from em_cubed.loopy.runner import LoopySkillRunner


@dataclass
class MockCodeState:
    code: str
    linter_errors: list[str] = field(default_factory=list)


class MockAutoFixerSkill(BaseLoopySkill[MockCodeState, str]):
    """Demonstration loopy skill for auto-fixing python code."""

    def initialize_state(self, initial_code: str) -> MockCodeState:
        return MockCodeState(code=initial_code, linter_errors=["E501 line too long", "F401 unused import"])

    def mutate(self, state: MockCodeState, iteration: int) -> tuple[MockCodeState, str]:
        if state.linter_errors:
            removed_err = state.linter_errors.pop(0)
            state.code += f" # fixed {removed_err}"
            action = f"Applied patch for {removed_err}"
        else:
            action = "No errors remaining"
        return state, action

    def verify(self, state: MockCodeState) -> tuple[bool, str]:
        if not state.linter_errors:
            return True, "Linter passed (0 errors)"
        return False, f"Linter failed with {len(state.linter_errors)} errors"

    def extract_result(self, state: MockCodeState) -> str:
        return state.code


def test_loopy_skill_success_trajectory():
    skill = MockAutoFixerSkill(max_iterations=5)
    res = LoopySkillRunner.execute(skill, initial_code="def foo(): pass")

    assert res.success is True
    assert len(res.trajectory) == 2
    assert res.trajectory[0].passed_guard is False
    assert res.trajectory[1].passed_guard is True
    assert "fixed" in res.final_output


def test_loopy_skill_max_iterations_failure():
    skill = MockAutoFixerSkill(max_iterations=1)
    res = LoopySkillRunner.execute(skill, initial_code="def foo(): pass")

    assert res.success is False
    assert res.error_message is not None
    assert "Hit max iterations" in res.error_message


def test_text_loop_miner():
    miner = TextLoopMiner()
    sop_text = """
    WHEN a customer requests a refund
    DO check order status and calculate eligible amount
    UNTIL verify exit code == 0 and refund confirmation is logged
    """
    loops = miner.mine_loops_from_text(sop_text, default_name="RefundLoop")
    assert len(loops) == 1
    assert loops[0].name == "RefundLoop"
    assert "WHEN" in loops[0].trigger.upper()
    assert len(loops[0].action_sequence) > 0


class SlowLoopSkill(BaseLoopySkill[int, str]):
    def initialize_state(self, *args, **kwargs) -> int:
        return 0

    def mutate(self, state: int, iteration: int) -> tuple[int, str]:
        import time

        time.sleep(0.5)
        return state + 1, "slept"

    def verify(self, state: int) -> tuple[bool, str]:
        return False, "Not done"

    def extract_result(self, state: int) -> str:
        return "slow"


class CrashingSkill(BaseLoopySkill[int, str]):
    def initialize_state(self, *args, **kwargs) -> int:
        return 0

    def mutate(self, state: int, iteration: int) -> tuple[int, str]:
        raise RuntimeError("Fatal simulator explosion")

    def verify(self, state: int) -> tuple[bool, str]:
        return False, "err"

    def extract_result(self, state: int) -> str:
        return "err"


def test_loopy_skill_timeout_enforcement():
    skill = SlowLoopSkill(max_iterations=10)
    res = LoopySkillRunner.execute(skill, timeout=0.1)

    assert res.success is False
    assert res.error_message is not None
    assert "timed out" in res.error_message.lower()
    assert len(res.trajectory) == 1
    assert res.trajectory[0].action_taken == "execution_timeout_guard"


def test_loopy_skill_exception_containment():
    skill = CrashingSkill(max_iterations=5)
    res = LoopySkillRunner.execute(skill)

    assert res.success is False
    assert res.error_message is not None
    assert "Fatal simulator explosion" in res.error_message
    assert len(res.trajectory) == 1
    assert res.trajectory[0].action_taken == "exception_containment"


def test_loopy_skill_execute_with_audit_and_evolution():
    from em_cubed.loopy.evolution import SkillEvolutionEngine

    skill = MockAutoFixerSkill(max_iterations=5)
    engine = SkillEvolutionEngine()

    res, report = LoopySkillRunner.execute_with_audit(
        skill,
        initial_code="def foo(): pass",
        evolution_engine=engine,
    )

    assert res.success is True
    assert report.skill_name == "MockAutoFixerSkill"
    assert report.success is True
    assert len(report.proof_annotations) == 2
    assert len(engine.history) == 1
    assert engine.history[0].skill_name == "MockAutoFixerSkill"

