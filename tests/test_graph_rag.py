"""Unit tests for GraphPathRAG and SubgraphPath."""

from em_cubed.ontology.graph_rag import GraphPathRAG
from em_cubed.ontology.schema import OntologyTriple


def test_graph_path_rag_multi_hop():
    rag = GraphPathRAG()
    rag.add_triple(OntologyTriple("Order_100", "placed_by", "User_A"))
    rag.add_triple(OntologyTriple("User_A", "belongs_to_org", "Org_TechCorp"))
    rag.add_triple(OntologyTriple("Org_TechCorp", "has_compliance_tier", "Tier_1"))

    paths = rag.find_paths(start_entity="Order_100", max_depth=3)
    assert len(paths) >= 2

    # Check path chain string formatting
    context_str = rag.retrieve_grounded_context("Order_100", max_depth=3)
    assert "Order_100" in context_str
    assert "placed_by" in context_str
    assert "belongs_to_org" in context_str
    assert "Tier_1" in context_str


def test_graph_path_rag_no_paths():
    rag = GraphPathRAG()
    context_str = rag.retrieve_grounded_context("UnknownEntity")
    assert "No grounded graph paths found" in context_str
