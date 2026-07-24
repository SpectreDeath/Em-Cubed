"""Unit tests for SurfaceMorphism categorical surface translations."""

from pydantic import BaseModel

from em_cubed.ontology.schema import OntologyTriple
from em_cubed.surfaces.morphism import SurfaceMorphism


class SampleOrder(BaseModel):
    id: str = "order_99"
    amount: float = 149.99
    status: str = "approved"


def test_surface_morphism_pydantic_to_prolog():
    model = SampleOrder()
    facts = SurfaceMorphism.pydantic_to_prolog_facts(model)

    assert len(facts) == 2
    assert "sampleorder_amount('order_99', '149.99')." in facts
    assert "sampleorder_status('order_99', 'approved')." in facts


def test_surface_morphism_pydantic_to_z3():
    model = SampleOrder()
    assertions = SurfaceMorphism.pydantic_to_z3_assertions(model)

    assert len(assertions) == 1
    assert "(assert (>= sampleorder_amount 149.99))" in assertions


def test_surface_morphism_triple_to_datalog():
    triple = OntologyTriple(subject="Order-99", predicate="has-status", object="Approved")
    datalog_rule = SurfaceMorphism.triple_to_datalog(triple)

    assert datalog_rule == "has_status(order_99, approved)."
