"""Unit tests for verify_topos execution inside BaseLoopySkill."""

from dataclasses import dataclass

from em_cubed.loopy.base import BaseLoopySkill
from em_cubed.loopy.runner import LoopySkillRunner
from em_cubed.ontology.topos import ModalType, SubobjectClassifier, TruthValue


@dataclass
class ToposState:
    confidence: float


class ModalToposSkill(BaseLoopySkill[ToposState, str]):
    def initialize_state(self, initial_confidence: float) -> ToposState:
        return ToposState(confidence=initial_confidence)

    def mutate(self, state: ToposState, iteration: int) -> tuple[ToposState, str]:
        state.confidence += 0.2
        return state, f"Boosted confidence to {state.confidence:.2f}"

    def verify(self, state: ToposState) -> tuple[bool, str]:
        return state.confidence >= 0.8, f"Confidence = {state.confidence:.2f}"

    def verify_topos(self, state: ToposState) -> TruthValue:
        is_true = state.confidence >= 0.8
        return SubobjectClassifier.classify_modal(
            is_true=is_true,
            modal_type=ModalType.NECESSARY,
            confidence=state.confidence,
            message=f"Modal Necessary Truth: {state.confidence:.2f}",
        )

    def extract_result(self, state: ToposState) -> str:
        return f"Verified with confidence {state.confidence:.2f}"


def test_topos_skill_execution():
    skill = ModalToposSkill(max_iterations=5)
    res = LoopySkillRunner.execute(skill, initial_confidence=0.5)

    assert res.success is True
    assert len(res.trajectory) == 2
    assert res.trajectory[0].passed_guard is False
    assert res.trajectory[1].passed_guard is True
    assert res.trajectory[1].metrics["modal_type"] == "Necessary"
    assert res.trajectory[1].metrics["confidence"] >= 0.8
