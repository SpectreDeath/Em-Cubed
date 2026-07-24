"""Dynamic Knowledge Graph Triple Induction Engine.

Automatically induces new verified OntologyTriple assertions from successful loopy skill results
and registers them into GraphPathRAG repositories with confidence weights.
"""

from __future__ import annotations

import logging
from typing import Any

from em_cubed.loopy.base import LoopySkillResult
from em_cubed.ontology.graph_rag import GraphPathRAG
from em_cubed.ontology.schema import OntologyTriple

logger = logging.getLogger(__name__)


class TripleInductionEngine:
    """Engine executing dynamic triple induction from verified skill outputs."""

    def __init__(self, graph_rag: GraphPathRAG | None = None) -> None:
        self.graph_rag = graph_rag or GraphPathRAG()

    def induce_triples_from_result(
        self,
        result: LoopySkillResult[Any],
        subject_id: str,
        predicate: str,
        confidence: float = 0.95,
    ) -> list[OntologyTriple]:
        """Induce new OntologyTriple assertions from a successful LoopySkillResult.

        Parameters
        ----------
        result : LoopySkillResult[Any]
            Successful skill execution outcome.
        subject_id : str
            Entity ID subject.
        predicate : str
            Semantic relation predicate.
        confidence : float
            Assigned confidence score (default 0.95).

        Returns
        -------
        list[OntologyTriple]
            Newly induced triples.
        """
        if not result.success:
            logger.warning("Cannot induce triples from failed skill result.")
            return []

        induced: list[OntologyTriple] = []
        obj_val = str(result.final_output).replace("\n", " ").strip()

        triple = OntologyTriple(
            subject=subject_id,
            predicate=predicate,
            object=obj_val,
            confidence=confidence,
        )

        self.graph_rag.add_triple(triple)
        induced.append(triple)
        logger.info("Induced new OntologyTriple: (%s, %s, %s) [conf=%.2f]", subject_id, predicate, obj_val[:30], confidence)
        return induced
