"""Unit tests for ConceptInductionEngine and NeuronConceptAligner."""

from em_cubed.ontology.concept_induction import (
    ConceptInductionEngine,
    NeuronConceptAligner,
)
from em_cubed.ontology.schema import OntologyTriple


def test_concept_induction_dl_expression():
    pos_samples = [
        {"type": "Vehicle", "property": "hasFeature", "target": "CrosswalkDetection"},
    ]
    neg_samples = [
        {"disallowed_type": "PedestrianViolation"},
    ]

    expr = ConceptInductionEngine.induce_concept(
        subclass_name="AutonomousSafetyVehicle",
        positive_samples=pos_samples,
        negative_samples=neg_samples,
    )

    dl_str = expr.to_dl_syntax()
    manchester_str = expr.to_owl_manchester()

    assert "AutonomousSafetyVehicle ⊑ Vehicle" in dl_str
    assert "∃hasFeature.CrosswalkDetection" in dl_str
    assert "¬PedestrianViolation" in dl_str
    assert "Class: AutonomousSafetyVehicle" in manchester_str


def test_neuron_concept_aligner():
    latent_vector = [0.85, 0.92, 0.78]
    candidates = [
        OntologyTriple(subject="CrosswalkNode", predicate="detected_by", object="CameraNeuron_42"),
        OntologyTriple(subject="StopSignNode", predicate="detected_by", object="CameraNeuron_12"),
    ]

    aligned = NeuronConceptAligner.align_latent_cluster(
        cluster_id="Cluster_42",
        latent_vector=latent_vector,
        candidate_triples=candidates,
        top_k=1,
    )

    assert len(aligned) == 1
    assert aligned[0].subject == "NeuronCluster_Cluster_42"
    assert aligned[0].predicate == "maps_to_concept"
    assert "CrosswalkNode" in aligned[0].object
    assert aligned[0].confidence > 0.5
