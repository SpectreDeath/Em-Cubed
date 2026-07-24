"""Unit tests for FederatedOntologyRegistry."""

from em_cubed.ontology.federated_registry import FederatedOntologyRegistry
from em_cubed.ontology.schema import OntologyTriple


def test_federated_ontology_registry_sync_and_alignment():
    registry = FederatedOntologyRegistry()

    t1 = OntologyTriple(subject="Order_1", predicate="has_refund", object="Refund_1", confidence=1.0)
    t2 = OntologyTriple(subject="Order_1", predicate="has_refund", object="Refund_1", confidence=1.0)

    # Node A sync
    ok1, chk1 = registry.sync_triples("Node_A", [t1])
    assert ok1 is True
    assert len(chk1) == 64

    # Node B sync identical triple
    ok2, chk2 = registry.sync_triples("Node_B", [t2])
    assert ok2 is True
    assert chk1 == chk2

    # Verify swarm alignment
    aligned, msg = registry.verify_swarm_alignment()
    assert aligned is True
    assert "Swarm fully aligned" in msg


def test_federated_ontology_registry_misalignment():
    registry = FederatedOntologyRegistry()

    t1 = OntologyTriple(subject="Order_1", predicate="has_refund", object="Refund_1", confidence=1.0)
    t2 = OntologyTriple(subject="Order_1", predicate="has_refund", object="Refund_DIFFERENT", confidence=1.0)

    registry.sync_triples("Node_A", [t1])
    registry.sync_triples("Node_B", [t2])

    aligned, msg = registry.verify_swarm_alignment()
    assert aligned is False
    assert "Swarm misalignment detected" in msg
