"""Unit tests for TripleInductionEngine."""

from em_cubed.loopy.base import LoopySkillResult
from em_cubed.ontology.graph_rag import GraphPathRAG
from em_cubed.ontology.induction import TripleInductionEngine


def test_triple_induction_success():
    rag = GraphPathRAG()
    engine = TripleInductionEngine(graph_rag=rag)

    dummy_res = LoopySkillResult(success=True, final_output="Compliance_Verified_Tier_1")
    triples = engine.induce_triples_from_result(
        result=dummy_res,
        subject_id="Org_Acme",
        predicate="has_verified_compliance",
        confidence=0.98,
    )

    assert len(triples) == 1
    assert triples[0].subject == "Org_Acme"
    assert triples[0].predicate == "has_verified_compliance"
    assert triples[0].object == "Compliance_Verified_Tier_1"
    assert triples[0].confidence == 0.98

    # Verify triple is queryable in GraphPathRAG
    paths = rag.find_paths("Org_Acme")
    assert len(paths) == 1
    assert "Compliance_Verified_Tier_1" in paths[0].nodes


def test_triple_induction_failure():
    engine = TripleInductionEngine()
    dummy_failed_res = LoopySkillResult(success=False, final_output="Failed", error_message="Error")

    triples = engine.induce_triples_from_result(
        result=dummy_failed_res,
        subject_id="Org_Acme",
        predicate="has_verified_compliance",
    )
    assert len(triples) == 0
