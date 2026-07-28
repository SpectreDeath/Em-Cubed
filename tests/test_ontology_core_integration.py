"""Integration tests for Ontological Core Re-Orientation in em-cubed."""

from dataclasses import dataclass

from em_cubed.loopy.base import BaseLoopySkill
from em_cubed.loopy.runner import LoopySkillRunner
from em_cubed.ontology.schema import OntologyTriple


@dataclass
class OrderState:
    order_id: str
    refund_id: str


class OntologyGuardedSkill(BaseLoopySkill[OrderState, str]):
    def initialize_state(self, *args, **kwargs) -> OrderState:
        # Register functional property constraint: order_id can have at most ONE refund
        self.ledger_validator.add_functional_property(predicate="has_refund")
        # Commit initial refund
        t1 = OntologyTriple(subject="Order_100", predicate="has_refund", object="Refund_A")
        self.ledger_validator.validate_and_commit(t1)
        return OrderState(order_id="Order_100", refund_id="Refund_B")

    def mutate(self, state: OrderState, iteration: int) -> tuple[OrderState, str]:
        # Attempt to issue a SECOND refund to same order
        return state, "Attempted to issue secondary refund"

    def verify(self, state: OrderState) -> tuple[bool, str]:
        # Perform Ontology Ledger Guard check
        illegal_triple = OntologyTriple(subject=state.order_id, predicate="has_refund", object=state.refund_id)
        passed, msg = self.ledger_validator.validate_and_commit(illegal_triple)
        return passed, msg

    def extract_result(self, state: OrderState) -> str:
        return "Completed"


def test_base_loopy_skill_default_ontology_ledger_guard():
    skill = OntologyGuardedSkill(max_iterations=2)
    res = LoopySkillRunner.execute(skill)

    # Must fail verification because functional property constraint blocks second refund
    assert res.success is False
    assert len(res.trajectory) == 2
    assert "Functional Property Violation" in res.trajectory[0].observation
