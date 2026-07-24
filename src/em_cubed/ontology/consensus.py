"""Multi-Agent Topos Consensus Engine.

Computes categorical consensus truth objects (Omega_consensus = Omega_A ^ Omega_B)
across distributed agent swarm evaluations using categorical meet (pullback) operations.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from em_cubed.ontology.topos import ModalType, TruthValue

logger = logging.getLogger(__name__)


@dataclass
class AgentEvaluation:
    """Individual agent evaluation containing agent_id and TruthValue."""

    agent_id: str
    truth_value: TruthValue


class MultiAgentToposConsensus:
    """Engine computing categorical meet consensus across multi-agent truth evaluations."""

    @staticmethod
    def compute_consensus(
        evaluations: list[AgentEvaluation],
        min_consensus_confidence: float = 0.8,
        require_modal_agreement: bool = True,
    ) -> TruthValue:
        """Compute the categorical meet truth value (Omega_consensus) across agent evaluations.

        Parameters
        ----------
        evaluations : list[AgentEvaluation]
            List of agent evaluations.
        min_consensus_confidence : float
            Minimum required consensus confidence threshold (default 0.8).
        require_modal_agreement : bool
            If True, enforces that all agents must agree on modal logic classification.

        Returns
        -------
        TruthValue
            Synthesized Consensus TruthValue object.
        """
        if not evaluations:
            logger.warning("Empty agent evaluations list for consensus computation.")
            return TruthValue(is_boolean=False, confidence=0.0, evidence=["No evaluations provided"])

        logger.info("Computing Topos Consensus across %d agent evaluations...", len(evaluations))

        all_boolean = all(e.truth_value.is_boolean for e in evaluations)
        min_conf = min(e.truth_value.confidence for e in evaluations)
        evidence_chain: list[str] = []

        modal_types = {e.truth_value.modal_type for e in evaluations}
        if require_modal_agreement and len(modal_types) > 1:
            logger.warning("Modal disagreement among agents: %s", modal_types)
            return TruthValue(
                is_boolean=False,
                confidence=min_conf,
                modal_type=ModalType.ASSERTION,
                evidence=["Modal disagreement among agents"],
            )

        consensus_modal = evaluations[0].truth_value.modal_type

        for e in evaluations:
            evidence_chain.append(f"[{e.agent_id}]: conf={e.truth_value.confidence:.2f}")

        is_satisfied = all_boolean and min_conf >= min_consensus_confidence
        logger.info("Consensus computed: satisfied=%s, conf=%.2f, modal=%s", is_satisfied, min_conf, consensus_modal.value)

        return TruthValue(
            is_boolean=is_satisfied,
            confidence=min_conf,
            modal_type=consensus_modal,
            evidence=evidence_chain,
        )
