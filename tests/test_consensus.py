"""Unit tests for MultiAgentToposConsensus."""

from em_cubed.ontology.consensus import AgentEvaluation, MultiAgentToposConsensus
from em_cubed.ontology.topos import ModalType, TruthValue


def test_topos_consensus_success():
    eval_legal = AgentEvaluation(
        agent_id="Agent_Legal",
        truth_value=TruthValue(is_boolean=True, confidence=0.95, modal_type=ModalType.NECESSARY),
    )
    eval_finance = AgentEvaluation(
        agent_id="Agent_Finance",
        truth_value=TruthValue(is_boolean=True, confidence=0.90, modal_type=ModalType.NECESSARY),
    )

    consensus_tv = MultiAgentToposConsensus.compute_consensus(
        evaluations=[eval_legal, eval_finance],
        min_consensus_confidence=0.85,
    )

    assert consensus_tv.is_satisfied() is True
    assert consensus_tv.confidence == 0.90
    assert consensus_tv.modal_type == ModalType.NECESSARY
    assert len(consensus_tv.evidence) == 2


def test_topos_consensus_modal_disagreement():
    eval_legal = AgentEvaluation(
        agent_id="Agent_Legal",
        truth_value=TruthValue(is_boolean=True, confidence=0.95, modal_type=ModalType.NECESSARY),
    )
    eval_finance = AgentEvaluation(
        agent_id="Agent_Finance",
        truth_value=TruthValue(is_boolean=True, confidence=0.90, modal_type=ModalType.POSSIBLE),
    )

    consensus_tv = MultiAgentToposConsensus.compute_consensus(
        evaluations=[eval_legal, eval_finance],
        require_modal_agreement=True,
    )

    assert consensus_tv.is_boolean is False
    assert "Modal disagreement" in consensus_tv.evidence[0]
