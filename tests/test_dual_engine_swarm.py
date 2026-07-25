"""Unit tests for Autonomous Dual-Engine Swarm Orchestrator."""

from em_cubed.orchestration.dual_engine_swarm import (
    DualEngineSwarmOrchestrator,
    SwarmRunConfig,
)


def test_swarm_lifecycle_execution():
    config = SwarmRunConfig(
        domain_prompt="Maritime Logistics in South America",
        raw_ingested_text="Vessel Alpha arrived at Montevideo Port carrying raw materials.",
        target_subclass="MaritimeVessel",
        confidence_threshold=0.85,
    )

    report = DualEngineSwarmOrchestrator.run_swarm_lifecycle(config)

    assert len(report.triples) > 0
    assert report.modal_truth is not None
    assert report.truthmaker is not None
    assert "MaritimeVessel" in report.dl_concept_expression
    assert report.health_report.health_status == "HEALTHY"
    assert "@prefix :" in report.rdf_turtle_output
