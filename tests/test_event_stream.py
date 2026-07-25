"""Unit tests for Real-Time Dynamic Ontology Stream Ingestion & Event-Driven Engine."""

import time

from em_cubed.ontology.event_stream import (
    EventType,
    OntologyEventStreamProcessor,
    ReactiveRule,
    StreamEvent,
)
from em_cubed.ontology.schema import OntologyTriple


def test_event_stream_processing_and_reactive_rules():
    processor = OntologyEventStreamProcessor()

    # Rule: Alert if Vessel enters a RestrictedZone
    rule = ReactiveRule(
        rule_id="RULE_RESTRICTED_ZONE",
        target_predicate="enters_zone",
        condition_fn=lambda ev: ev.triple.object == "RestrictedZone_Alpha",
        action_fn=lambda ev, tv: {
            "severity": "CRITICAL",
            "message": f"Entity {ev.triple.subject} entered restricted area {ev.triple.object}",
        },
    )
    processor.register_rule(rule)

    t1 = OntologyTriple(subject="Vessel_Alpha", predicate="enters_zone", object="RestrictedZone_Alpha")
    e1 = StreamEvent(
        event_id="EVT_001",
        event_type=EventType.ASSERT_TRIPLE,
        triple=t1,
        timestamp=time.time(),
    )

    result = processor.process_stream_batch([e1])

    assert result.processed_events_count == 1
    assert result.active_triples_count == 1
    assert len(result.reactive_alerts) == 1
    assert result.reactive_alerts[0]["severity"] == "CRITICAL"
    assert "Vessel_Alpha" in result.reactive_alerts[0]["message"]


def test_property_mutation_and_retraction():
    processor = OntologyEventStreamProcessor()

    t_init = OntologyTriple(subject="Agent_01", predicate="hasStatus", object="Inactive")
    processor.active_ledger.append(t_init)

    # Mutate property to Active
    t_mutated = OntologyTriple(subject="Agent_01", predicate="hasStatus", object="Active")
    e_mut = StreamEvent(
        event_id="EVT_002",
        event_type=EventType.MUTATE_PROPERTY,
        triple=t_mutated,
        timestamp=time.time(),
    )

    processor.process_event(e_mut)
    assert len(processor.active_ledger) == 1
    assert processor.active_ledger[0].object == "Active"

    # Retract triple
    e_ret = StreamEvent(
        event_id="EVT_003",
        event_type=EventType.RETRACT_TRIPLE,
        triple=t_mutated,
        timestamp=time.time(),
    )
    processor.process_event(e_ret)
    assert len(processor.active_ledger) == 0
