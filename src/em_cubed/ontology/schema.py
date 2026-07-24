"""Ontology Schema Definitions & Constraint Predicates.

Defines OntologyTriples, FunctionalPropertyConstraints, DisjointClassConstraints, and DomainRangeInferences.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class OntologyTriple:
    """Represents a Subject-Predicate-Object semantic triple."""

    subject: str
    predicate: str
    object: str
    confidence: float = 1.0


@dataclass
class FunctionalPropertyConstraint:
    """OWL Functional Property: Enforces at most ONE object for a given (subject, predicate) pair."""

    predicate: str

    def check_violation(self, existing_triples: list[OntologyTriple], new_triple: OntologyTriple) -> str | None:
        """Check if adding new_triple violates functional property single-value rule."""
        if new_triple.predicate != self.predicate:
            return None

        for t in existing_triples:
            if t.subject == new_triple.subject and t.predicate == self.predicate and t.object != new_triple.object:
                return (
                    f"Functional Property Violation on predicate '{self.predicate}': "
                    f"Subject '{new_triple.subject}' already has value '{t.object}', "
                    f"cannot assign second value '{new_triple.object}'."
                )
        return None


@dataclass
class DisjointClassConstraint:
    """OWL Disjoint Classes: Enforces entity role separation (e.g. SupportRep vs Customer)."""

    class_a: str
    class_b: str

    def check_violation(self, entity_classes: dict[str, set[str]], entity_id: str, new_class: str) -> str | None:
        """Check if assigning new_class to entity_id violates class disjointness."""
        current_classes = entity_classes.get(entity_id, set())

        if new_class == self.class_a and self.class_b in current_classes:
            return f"Disjoint Class Violation: Entity '{entity_id}' is already '{self.class_b}', cannot also be '{self.class_a}'."
        if new_class == self.class_b and self.class_a in current_classes:
            return f"Disjoint Class Violation: Entity '{entity_id}' is already '{self.class_a}', cannot also be '{self.class_b}'."
        return None


@dataclass
class DomainRangeInference:
    """OWL Domain/Range Inference: Automatically infers subject/object types from predicates."""

    predicate: str
    domain_class: str
    range_class: str

    def infer(self, triple: OntologyTriple) -> list[tuple[str, str]]:
        """Infer (entity_id, class_name) types if triple.predicate matches."""
        if triple.predicate == self.predicate:
            return [
                (triple.subject, self.domain_class),
                (triple.object, self.range_class),
            ]
        return []
