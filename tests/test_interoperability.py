"""Unit tests for W3C OWL/RDF & SHACL Interoperability Engine."""

from em_cubed.ontology.interoperability import (
    OWLImporter,
    RDFSerializer,
    SHACLConstraintGenerator,
)
from em_cubed.ontology.schema import (
    FunctionalPropertyConstraint,
    OntologyTriple,
)


def test_rdf_turtle_serialization():
    triples = [
        OntologyTriple(subject="SupplierA", predicate="supplies", object="FolicAcid"),
    ]
    turtle_output = RDFSerializer.to_turtle(triples)

    assert "@prefix :" in turtle_output
    assert ":SupplierA :supplies :FolicAcid ." in turtle_output


def test_shacl_shape_generation():
    fc = [FunctionalPropertyConstraint(predicate="has_id")]
    shacl_output = SHACLConstraintGenerator.generate_shacl_shapes(fc)

    assert "@prefix sh:" in shacl_output
    assert "sh:maxCount 1" in shacl_output
    assert "sh:path :has_id" in shacl_output


def test_owl_importer():
    turtle_text = """
    @prefix : <http://em-cubed.org/ontology#> .
    :EntityX :relatesTo :EntityY .
    """

    triples = OWLImporter.from_turtle(turtle_text)
    assert len(triples) == 1
    assert triples[0].subject == "EntityX"
    assert triples[0].predicate == "relatesTo"
    assert triples[0].object == "EntityY"
