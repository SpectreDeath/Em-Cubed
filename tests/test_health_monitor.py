"""Unit tests for Ontological Health Monitoring & Self-Healing Guardrails Engine."""

from em_cubed.ontology.health_monitor import (
    OntologicalHealthMonitor,
    SelfHealingGuardrailEngine,
)
from em_cubed.ontology.schema import OntologyTriple


def test_health_monitor_auditing():
    triples = [
        OntologyTriple(subject="EntityA", predicate="relates_to", object="EntityB", confidence=0.95),
        OntologyTriple(subject="EntityB", predicate="relates_to", object="EntityC", confidence=0.90),
    ]

    report = OntologicalHealthMonitor.audit_health(triples)
    assert report.total_triples == 2
    assert report.coherence_index > 0.80
    assert report.health_status == "HEALTHY"


def test_self_healing_guardrail_repair():
    triples = [
        OntologyTriple(subject="GoodEntity", predicate="has_fact", object="Valid", confidence=0.95),
        OntologyTriple(subject="BadEntity", predicate="has_fact", object="Corrupted", confidence=0.20),
    ]

    healed = SelfHealingGuardrailEngine.self_heal_triples(triples, min_confidence_threshold=0.50)
    assert len(healed) == 1
    assert healed[0].subject == "GoodEntity"
    assert healed[0].confidence == 0.95
