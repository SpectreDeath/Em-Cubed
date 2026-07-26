"""Unit test suite for Tri-Engine Swarm Capacity Scaler."""

from em_cubed.orchestration.swarm_scaler import SwarmCapacityScaler


def test_swarm_scaler_simulation_heavy():
    report = SwarmCapacityScaler.calculate_allocation(total_workers=12, coherence_index=0.95, epistemic_trust=0.89)
    assert report.total_workers == 12
    assert report.scaling_mode == "SIMULATION_HEAVY"
    assert report.sme_workers + report.em_cubed_workers + report.strategify_workers == 12


def test_swarm_scaler_perception_heavy():
    report = SwarmCapacityScaler.calculate_allocation(total_workers=12, coherence_index=0.95, epistemic_trust=0.60)
    assert report.scaling_mode == "PERCEPTION_HEAVY"
    assert report.sme_workers > 3


def test_swarm_scaler_reasoning_heavy():
    report = SwarmCapacityScaler.calculate_allocation(total_workers=12, coherence_index=0.75, epistemic_trust=0.75)
    assert report.scaling_mode == "REASONING_HEAVY"
    assert report.em_cubed_workers > 4
