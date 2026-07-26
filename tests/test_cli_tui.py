"""Unit tests for Ontological OS Live Interactive Terminal Dashboard & TUI Workspace."""

from em_cubed.cli_tui import OntologyTUIDashboard, run_cli_tui_mode
from em_cubed.ontology.schema import OntologyTriple


def test_tui_dashboard_rendering():
    triples = [
        OntologyTriple(subject="Vessel_Alpha", predicate="has_status", object="Active"),
    ]

    snapshot = OntologyTUIDashboard.render_dashboard_snapshot(
        triples=triples,
        proposition="Maritime Telematics Compliance",
        confidence=0.92,
    )

    assert "EM-CUBED NEURO-SYMBOLIC ONTOLOGICAL OS" in snapshot
    assert "LIVE TERMINAL WORKSPACE DASHBOARD" in snapshot
    assert "(Vessel_Alpha) --[has_status]--> (Active)" in snapshot
    assert "NECESSARY" in snapshot
    assert "Coherence Index" in snapshot
    assert "PROOF_TUI_001" in snapshot


def test_run_cli_tui_mode():
    exit_code = run_cli_tui_mode()
    assert exit_code == 0
