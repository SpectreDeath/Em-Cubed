"""Palantir-Style Advanced Ontology Engine.

Implements core industrial primitives from Landon Carter's Palantir DevCon presentation:
1. Derived Properties & Declarative Reducers (SUM, COUNT, MAX, AVG) over linked triples.
2. Polymorphic Ontology Interfaces & Implementation Contracts.
3. Bi-directional Object Backlink Resolution.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum

from em_cubed.ontology.schema import OntologyTriple

logger = logging.getLogger(__name__)


class ReducerType(str, Enum):
    """Declarative Property Reducers."""

    SUM = "SUM"
    COUNT = "COUNT"
    MAX = "MAX"
    MIN = "MIN"
    AVG = "AVG"


class DerivedPropertyReducer:
    """Computes dynamic derived properties over linked triple object sets."""

    @staticmethod
    def compute_reducer(
        triples: list[OntologyTriple],
        subject: str,
        predicate: str,
        reducer_type: ReducerType,
    ) -> float | int:
        """Calculate dynamic derived property value for a subject and predicate.

        Parameters
        ----------
        triples : list[OntologyTriple]
            Full list of active triples.
        subject : str
            Target subject IRI.
        predicate : str
            Target predicate IRI.
        reducer_type : ReducerType
            Reducer type (SUM, COUNT, MAX, MIN, AVG).

        Returns
        -------
        float | int
            Computed dynamic property value.
        """
        matching = [t for t in triples if t.subject == subject and t.predicate == predicate]
        if not matching:
            logger.info("No matching triples found for (%s, %s). Returning 0.", subject, predicate)
            return 0

        if reducer_type == ReducerType.COUNT:
            return len(matching)

        numeric_vals: list[float] = []
        for t in matching:
            try:
                numeric_vals.append(float(t.object))
            except ValueError:
                logger.warning("Object '%s' is not numeric for reducer %s", t.object, reducer_type)

        if not numeric_vals:
            return 0

        if reducer_type == ReducerType.SUM:
            return sum(numeric_vals)
        elif reducer_type == ReducerType.MAX:
            return max(numeric_vals)
        elif reducer_type == ReducerType.MIN:
            return min(numeric_vals)
        elif reducer_type == ReducerType.AVG:
            return sum(numeric_vals) / len(numeric_vals)
        return 0


@dataclass
class OntologyInterface:
    """Abstract Ontology Interface contract defining required properties."""

    name: str
    required_predicates: list[str] = field(default_factory=list)


class InterfaceImplementation:
    """Validates whether a set of triples satisfies an abstract OntologyInterface."""

    @staticmethod
    def validates_interface(
        triples: list[OntologyTriple],
        subject: str,
        interface: OntologyInterface,
    ) -> bool:
        """Check if subject has all required predicates specified by the interface."""
        subject_predicates = {t.predicate for t in triples if t.subject == subject}
        missing = set(interface.required_predicates) - subject_predicates

        if missing:
            logger.warning("Subject '%s' missing required interface predicates: %s", subject, missing)
            return False

        logger.info("Subject '%s' successfully validates interface '%s'.", subject, interface.name)
        return True


class ObjectBacklinkRegistry:
    """Manages bi-directional link types and automatic backlink queries."""

    def __init__(self) -> None:
        self.forward_links: dict[tuple[str, str], str] = {}
        self.reverse_links: dict[tuple[str, str], str] = {}

    def register_link_type(self, forward_predicate: str, backlink_predicate: str) -> None:
        """Register a bi-directional link pair (e.g. has_line_item <-> belongs_to_order)."""
        self.forward_links[("forward", forward_predicate)] = backlink_predicate
        self.reverse_links[("backlink", backlink_predicate)] = forward_predicate
        logger.info("Registered bi-directional link: %s <-> %s", forward_predicate, backlink_predicate)

    def get_backlinks(
        self,
        triples: list[OntologyTriple],
        target_object: str,
        backlink_predicate: str,
    ) -> list[OntologyTriple]:
        """Query automatic backlinks pointing to target_object via registered backlink_predicate."""
        forward_pred = self.reverse_links.get(("backlink", backlink_predicate))
        if not forward_pred:
            logger.warning("Unregistered backlink predicate '%s'", backlink_predicate)
            return []

        # Find all subjects where subject --forward_pred--> target_object
        backlinks: list[OntologyTriple] = []
        for t in triples:
            if t.object == target_object and t.predicate == forward_pred:
                backlink_triple = OntologyTriple(
                    subject=target_object,
                    predicate=backlink_predicate,
                    object=t.subject,
                    confidence=t.confidence,
                )
                backlinks.append(backlink_triple)

        return backlinks
