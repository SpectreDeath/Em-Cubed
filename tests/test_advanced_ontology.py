"""Unit tests for Palantir-Style Advanced Ontology Engine."""

from em_cubed.ontology.advanced_ontology import (
    DerivedPropertyReducer,
    InterfaceImplementation,
    ObjectBacklinkRegistry,
    OntologyInterface,
    ReducerType,
)
from em_cubed.ontology.schema import OntologyTriple


def test_derived_property_reducers():
    triples = [
        OntologyTriple(subject="Order_100", predicate="has_amount", object="150.0"),
        OntologyTriple(subject="Order_100", predicate="has_amount", object="300.0"),
        OntologyTriple(subject="Order_100", predicate="has_line_item", object="Item_A"),
        OntologyTriple(subject="Order_100", predicate="has_line_item", object="Item_B"),
    ]

    total_sum = DerivedPropertyReducer.compute_reducer(
        triples=triples,
        subject="Order_100",
        predicate="has_amount",
        reducer_type=ReducerType.SUM,
    )
    assert total_sum == 450.0

    count_items = DerivedPropertyReducer.compute_reducer(
        triples=triples,
        subject="Order_100",
        predicate="has_line_item",
        reducer_type=ReducerType.COUNT,
    )
    assert count_items == 2

    max_amount = DerivedPropertyReducer.compute_reducer(
        triples=triples,
        subject="Order_100",
        predicate="has_amount",
        reducer_type=ReducerType.MAX,
    )
    assert max_amount == 300.0


def test_ontology_interface_implementation():
    triples = [
        OntologyTriple(subject="Vessel_Alpha", predicate="has_id", object="V100"),
        OntologyTriple(subject="Vessel_Alpha", predicate="has_capacity", object="50000"),
    ]

    interface = OntologyInterface(name="AssetInterface", required_predicates=["has_id", "has_capacity"])
    valid = InterfaceImplementation.validates_interface(triples, "Vessel_Alpha", interface)
    assert valid is True

    invalid_interface = OntologyInterface(name="FinancialInterface", required_predicates=["has_id", "has_balance"])
    invalid = InterfaceImplementation.validates_interface(triples, "Vessel_Alpha", invalid_interface)
    assert invalid is False


def test_object_backlinks():
    registry = ObjectBacklinkRegistry()
    registry.register_link_type(forward_predicate="has_child_item", backlink_predicate="parent_order_of")

    triples = [
        OntologyTriple(subject="Order_100", predicate="has_child_item", object="Item_X"),
        OntologyTriple(subject="Order_100", predicate="has_child_item", object="Item_Y"),
    ]

    backlinks = registry.get_backlinks(triples, target_object="Item_X", backlink_predicate="parent_order_of")
    assert len(backlinks) == 1
    assert backlinks[0].subject == "Item_X"
    assert backlinks[0].predicate == "parent_order_of"
    assert backlinks[0].object == "Order_100"
