"""Unit test suite for Cross-Domain Knowledge Transfer Engine."""

from em_cubed.ontology.cross_domain_transfer import CrossDomainKnowledgeTransferEngine
from em_cubed.ontology.schema import OntologyTriple


def test_cross_domain_concept_mapping():
    mapping = CrossDomainKnowledgeTransferEngine.map_concept(
        source_domain="Biodefense",
        target_domain="Geopolitics",
        source_concept="PathogenVariant",
        target_concept="StateActor",
    )
    assert mapping.alignment_confidence == 0.95
    assert mapping.bfo_upper_category == "bfo:IndependentContinuant"


def test_cross_domain_triple_transfer():
    source_triples = [OntologyTriple(subject="PathogenVariant_X", predicate="causes", object="OutbreakEvent_01")]
    concept_map = {
        "PathogenVariant_X": "StateActor_Alpha",
        "causes": "initiates",
        "OutbreakEvent_01": "MilitarySkirmish_01",
    }

    transferred = CrossDomainKnowledgeTransferEngine.transfer_triples(source_triples, concept_map)
    assert len(transferred) == 1
    assert transferred[0].subject == "StateActor_Alpha"
    assert transferred[0].predicate == "initiates"
    assert transferred[0].object == "MilitarySkirmish_01"
