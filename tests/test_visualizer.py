"""Unit tests for KnowledgeGraphVisualizer HTML renderers."""

from em_cubed.loopy.audit import AuditReport, ProofTraceAnnotation
from em_cubed.ontology.graph_rag import SubgraphPath
from em_cubed.ontology.schema import OntologyTriple
from em_cubed.ontology.visualizer import KnowledgeGraphVisualizer


def test_visualizer_subgraph_html():
    t1 = OntologyTriple(subject="Order_1", predicate="has_status", object="Approved")
    path = SubgraphPath(nodes=["Order_1", "Approved"], predicates=["has_status"], triples=[t1])

    html = KnowledgeGraphVisualizer.render_subgraph_html([path], title="Test Explorer")
    assert "<!DOCTYPE html>" in html
    assert "Test Explorer" in html
    assert "Order_1" in html
    assert "Approved" in html


def test_visualizer_audit_report_html():
    proof = ProofTraceAnnotation(
        iteration=1,
        proof_type="Deductive",
        solver_used="Z3 SMT",
        proof_details="Passed all assertions",
        verified=True,
    )
    report = AuditReport(skill_name="TestSkill", success=True, proof_annotations=[proof])

    html = KnowledgeGraphVisualizer.render_audit_report_html(report)
    assert "<!DOCTYPE html>" in html
    assert "Audit Trail: TestSkill" in html
    assert "Z3 SMT" in html
    assert "VERIFIED" in html
