"""Tri-Engine Cross-Domain Knowledge Transfer Engine & Concept Alignment Matrix.

Maps domain concept taxonomies across biodefense, geopolitical crisis, supply chain,
and financial audit domains using Basic Formal Ontology (BFO) upper-level categories.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from em_cubed.ontology.schema import OntologyTriple

logger = logging.getLogger(__name__)


@dataclass
class DomainTransferMapping:
    """Dataclass holding cross-domain concept mapping alignment."""

    source_domain: str
    target_domain: str
    source_concept: str
    target_concept: str
    bfo_upper_category: str
    alignment_confidence: float


class CrossDomainKnowledgeTransferEngine:
    """Engine mapping ontological concepts and rules across distinct domain silos."""

    # BFO upper-level category alignment dictionary
    BFO_ALIGNMENT_MAP: dict[str, str] = {
        "PathogenVariant": "bfo:IndependentContinuant",
        "StateActor": "bfo:IndependentContinuant",
        "SupplierNode": "bfo:IndependentContinuant",
        "FinancialAccount": "bfo:IndependentContinuant",
        "OutbreakEvent": "bfo:Process",
        "MilitarySkirmish": "bfo:Process",
        "ShipmentDelay": "bfo:Process",
        "AuditAnomaly": "bfo:Process",
    }

    @classmethod
    def map_concept(
        cls,
        source_domain: str,
        target_domain: str,
        source_concept: str,
        target_concept: str,
    ) -> DomainTransferMapping:
        """Map a source domain concept to a target domain concept via BFO upper categories.

        Parameters
        ----------
        source_domain : str
            Name of the source domain (e.g. "Biodefense").
        target_domain : str
            Name of the target domain (e.g. "Geopolitics").
        source_concept : str
            Source concept class name.
        target_concept : str
            Target concept class name.

        Returns
        -------
        DomainTransferMapping
            Alignment mapping report.
        """
        source_bfo = cls.BFO_ALIGNMENT_MAP.get(source_concept, "bfo:Entity")
        target_bfo = cls.BFO_ALIGNMENT_MAP.get(target_concept, "bfo:Entity")

        # Alignment confidence is 1.0 if BFO upper categories match
        confidence = 0.95 if source_bfo == target_bfo and source_bfo != "bfo:Entity" else 0.70

        logger.info(
            "Cross-Domain Transfer [%s -> %s]: (%s :: %s) aligned with (%s :: %s) [conf=%.2f]",
            source_domain,
            target_domain,
            source_concept,
            source_bfo,
            target_concept,
            target_bfo,
            confidence,
        )

        return DomainTransferMapping(
            source_domain=source_domain,
            target_domain=target_domain,
            source_concept=source_concept,
            target_concept=target_concept,
            bfo_upper_category=source_bfo if source_bfo == target_bfo else "bfo:Entity",
            alignment_confidence=confidence,
        )

    @classmethod
    def transfer_triples(
        cls,
        source_triples: list[OntologyTriple],
        concept_map: dict[str, str],
    ) -> list[OntologyTriple]:
        """Transform source domain triples to target domain triples using concept mappings.

        Parameters
        ----------
        source_triples : list[OntologyTriple]
            Triples in source domain vocabulary.
        concept_map : dict[str, str]
            Dictionary mapping source concepts/predicates to target terms.

        Returns
        -------
        list[OntologyTriple]
            Transferred target domain triples.
        """
        transferred: list[OntologyTriple] = []
        for t in source_triples:
            new_subject = concept_map.get(t.subject, t.subject)
            new_predicate = concept_map.get(t.predicate, t.predicate)
            new_object = concept_map.get(t.object, t.object)
            transferred.append(OntologyTriple(subject=new_subject, predicate=new_predicate, object=new_object, confidence=t.confidence))
        return transferred
