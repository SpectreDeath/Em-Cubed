"""Real-Time Dynamic Ontology Stream Ingestion & Event-Driven Reactive Reasoning Engine.

Processes continuous triple state mutation events (ASSERT, RETRACT, MUTATE)
and evaluates event-driven reactive rules against active ontology ledgers.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum

from em_cubed.ontology.schema import OntologyTriple
from em_cubed.ontology.topos import SubobjectClassifier, TruthValue

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of streaming semantic state mutation events."""

    ASSERT_TRIPLE = "ASSERT_TRIPLE"
    RETRACT_TRIPLE = "RETRACT_TRIPLE"
    MUTATE_PROPERTY = "MUTATE_PROPERTY"


@dataclass
class StreamEvent:
    """Represents a single streaming semantic mutation event."""

    event_id: str
    event_type: EventType
    triple: OntologyTriple
    timestamp: float
    source_id: str = "stream_source"


@dataclass
class ReactiveRule:
    """Defines an event-driven reactive condition and action callback."""

    rule_id: str
    target_predicate: str
    condition_fn: Callable[[StreamEvent], bool]
    action_fn: Callable[[StreamEvent, TruthValue], dict[str, str]]


@dataclass
class StreamProcessingResult:
    """Outcome of processing a stream event batch."""

    processed_events_count: int
    active_triples_count: int
    reactive_alerts: list[dict[str, str]] = field(default_factory=list)


class OntologyEventStreamProcessor:
    """Real-time stream processor managing continuous state mutations and reactive compliance alerts."""

    def __init__(self, initial_triples: list[OntologyTriple] | None = None) -> None:
        self.active_ledger: list[OntologyTriple] = list(initial_triples) if initial_triples else []
        self.reactive_rules: list[ReactiveRule] = []

    def register_rule(self, rule: ReactiveRule) -> None:
        """Register a reactive event-driven rule."""
        self.reactive_rules.append(rule)
        logger.info("Registered reactive rule '%s' for predicate '%s'", rule.rule_id, rule.target_predicate)

    def process_event(self, event: StreamEvent) -> list[dict[str, str]]:
        """Process a single streaming event and trigger reactive rules.

        Parameters
        ----------
        event : StreamEvent
            Streaming mutation event.

        Returns
        -------
        list[dict[str, str]]
            List of reactive alert messages.
        """
        alerts: list[dict[str, str]] = []

        # Apply state mutation to active ledger
        if event.event_type == EventType.ASSERT_TRIPLE:
            if event.triple not in self.active_ledger:
                self.active_ledger.append(event.triple)
        elif event.event_type == EventType.RETRACT_TRIPLE:
            if event.triple in self.active_ledger:
                self.active_ledger.remove(event.triple)
        elif event.event_type == EventType.MUTATE_PROPERTY:
            # Replace existing subject-predicate triples with new object
            self.active_ledger = [
                t
                for t in self.active_ledger
                if not (t.subject == event.triple.subject and t.predicate == event.triple.predicate)
            ]
            self.active_ledger.append(event.triple)

        # Evaluate Topos modal truth over event
        tv = SubobjectClassifier.evaluate_confidence(1.0 if event.event_type != EventType.RETRACT_TRIPLE else 0.0)

        # Evaluate registered reactive rules matching event predicate
        for rule in self.reactive_rules:
            if rule.target_predicate == event.triple.predicate and rule.condition_fn(event):
                alert = rule.action_fn(event, tv)
                alerts.append(alert)
                logger.warning("Reactive Rule Triggered [%s]: %s", rule.rule_id, alert)

        return alerts

    def process_stream_batch(self, events: list[StreamEvent]) -> StreamProcessingResult:
        """Process a batch of streaming events.

        Parameters
        ----------
        events : list[StreamEvent]
            Batch of streaming events.

        Returns
        -------
        StreamProcessingResult
            Stream processing report.
        """
        all_alerts: list[dict[str, str]] = []
        for ev in events:
            alerts = self.process_event(ev)
            all_alerts.extend(alerts)

        return StreamProcessingResult(
            processed_events_count=len(events),
            active_triples_count=len(self.active_ledger),
            reactive_alerts=all_alerts,
        )
