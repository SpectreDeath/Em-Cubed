"""Unit test suite for cross-repository tri-engine health auditing and CLI."""

from em_cubed.cli_ontology import main
from em_cubed.ontology.health_monitor import OntologicalHealthMonitor


def test_audit_tri_engine_health():
    report = OntologicalHealthMonitor.audit_tri_engine_health()
    assert report["sme_status"] == "ONLINE"
    assert report["em_cubed_status"] == "HEALTHY"
    assert report["strategify_status"] == "ONLINE"
    assert report["health_status"] == "HEALTHY"


def test_cli_health_subcommand(capsys):
    rc = main(["ontology", "health"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Tri-Engine Cross-Repository Health Audit" in captured.out
    assert "Coherence Index" in captured.out
