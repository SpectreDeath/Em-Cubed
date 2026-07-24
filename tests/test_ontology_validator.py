"""Unit tests for Neuro-Symbolic OntologyLedgerValidator."""

from pydantic import BaseModel, Field

from em_cubed.ontology.schema import OntologyTriple
from em_cubed.ontology.validator import OntologyLedgerValidator


class RefundPayloadSchema(BaseModel):
    order_id: str = Field(..., min_length=3)
    amount: float = Field(..., gt=0)
    customer_id: str


def test_ontology_validator_pydantic_door_failure():
    validator = OntologyLedgerValidator()
    invalid_payload = {"order_id": "AB", "amount": -50.0, "customer_id": "C1"}
    triple = OntologyTriple(subject="Order_123", predicate="has_refund", object="Refund_01")

    passed, msg = validator.validate_and_commit(
        new_triple=triple,
        schema_model=RefundPayloadSchema,
        raw_payload=invalid_payload,
    )
    assert passed is False
    assert "Door Schema Validation Failed" in msg


def test_ontology_validator_functional_property_constraint():
    validator = OntologyLedgerValidator()
    validator.add_functional_property("has_refund")

    t1 = OntologyTriple(subject="Order_123", predicate="has_refund", object="Refund_01")
    passed1, _ = validator.validate_and_commit(t1)
    assert passed1 is True

    t2 = OntologyTriple(subject="Order_123", predicate="has_refund", object="Refund_02")
    passed2, msg2 = validator.validate_and_commit(t2)
    assert passed2 is False
    assert "Functional Property Violation" in msg2


def test_ontology_validator_disjoint_classes_and_inferences():
    validator = OntologyLedgerValidator()
    validator.add_disjoint_classes("Customer", "SupportRep")
    validator.add_domain_range_inference("issues_payout_to", domain_class="FinanceEngine", range_class="Customer")
    validator.add_domain_range_inference("assigns_ticket_to", domain_class="System", range_class="SupportRep")

    # First triple infers User_99 is a SupportRep
    t1 = OntologyTriple(subject="Ticket_1", predicate="assigns_ticket_to", object="User_99")
    passed1, _ = validator.validate_and_commit(t1)
    assert passed1 is True

    # Second triple tries to infer User_99 is a Customer via issues_payout_to
    t2 = OntologyTriple(subject="Payout_1", predicate="issues_payout_to", object="User_99")
    passed2, msg2 = validator.validate_and_commit(t2)
    assert passed2 is False
    assert "Disjoint Class Violation" in msg2
