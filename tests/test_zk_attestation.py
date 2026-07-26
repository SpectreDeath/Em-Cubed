"""Unit tests for Quantum-Resistant Cryptographic Ontological Attestation & ZKP Engine."""

from em_cubed.ontology.schema import OntologyTriple
from em_cubed.ontology.zk_attestation import (
    ZeroKnowledgeOntologyAttestor,
    ZKPAuditor,
)


def test_zk_attestation_generation_and_independent_verification():
    t1 = OntologyTriple(subject="SecretSupplier_X", predicate="has_ingredient", object="FolicAcid")
    t2 = OntologyTriple(subject="SecretSupplier_X", predicate="has_origin", object="Uruguay")

    commitment = ZeroKnowledgeOntologyAttestor.generate_attestation(
        proposition="Supply Chain Origin Verification",
        state_triples=[t1, t2],
        relevant_predicates=["has_ingredient", "has_origin"],
        proof_id="PROOF_COMPLIANCE_77",
    )

    assert commitment.proof_id == "PROOF_COMPLIANCE_77"
    assert commitment.is_satisfied is True
    assert commitment.modal_status == "Necessary"
    assert len(commitment.signature) == 64

    # Independent auditor verification without raw triples
    report = ZKPAuditor.verify_commitment(commitment)
    assert report["verification_status"] == "VERIFIED"
    assert report["signature_valid"] is True


def test_tampered_commitment_rejection():
    t1 = OntologyTriple(subject="SecretSupplier_X", predicate="has_ingredient", object="FolicAcid")

    commitment = ZeroKnowledgeOntologyAttestor.generate_attestation(
        proposition="Supply Chain Origin Verification",
        state_triples=[t1],
        relevant_predicates=["has_ingredient"],
    )

    # Tamper with Merkle state root
    commitment.merkle_state_root = "f" * 64

    report = ZKPAuditor.verify_commitment(commitment)
    assert report["verification_status"] == "REJECTED"
    assert report["signature_valid"] is False
