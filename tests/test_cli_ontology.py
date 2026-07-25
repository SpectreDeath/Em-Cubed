"""Unit tests for Ontological OS CLI Suite (em_cubed.cli_ontology)."""

import os
from em_cubed.cli_ontology import main


def test_cli_ontology_validate(capsys):
    ret = main(["ontology", "validate", "--subject", "SubjA", "--predicate", "has_item", "--object", "ObjA", "--functional-prop", "has_item"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "[Ontology Ledger Validator] Triple valid: True" in captured.out


def test_cli_ontology_elicit(capsys):
    ret = main(["ontology", "elicit", "--domain-prompt", "Agricultural Logistics in Uruguay"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "[Knowledge Elicitation]" in captured.out


def test_cli_ontology_truthmaker(capsys):
    ret = main(["ontology", "truthmaker", "--proposition", "Compliance Check", "--predicates", "has_ingredient", "has_origin"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "[Truthmaker Semantics]" in captured.out


def test_cli_ontology_induce(capsys):
    ret = main(["ontology", "induce", "--subclass-name", "AutonomousTruck", "--parent-class", "Vehicle"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "[Concept Induction] Induced DL Expression:" in captured.out


def test_cli_ontology_visualize(tmp_path, capsys):
    target_html = str(tmp_path / "test_graph.html")
    ret = main(["ontology", "visualize", "--output-html", target_html])
    assert ret == 0
    assert os.path.exists(target_html)
    with open(target_html, "r", encoding="utf-8") as f:
        content = f.read()
    assert "CLI Knowledge Graph" in content


def test_cli_ontology_migrate(capsys):
    ret = main(["ontology", "migrate", "--from-pred", "has_origin", "--to-pred", "has_country_of_origin"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "[Schema Evolution] Migrated predicate 'has_origin' -> 'has_country_of_origin'" in captured.out


def test_cli_ontology_export(tmp_path, capsys):
    target_ttl = str(tmp_path / "test_export.ttl")
    ret = main(["ontology", "export", "--format", "turtle", "--output", target_ttl])
    assert ret == 0
    assert os.path.exists(target_ttl)
    with open(target_ttl, "r", encoding="utf-8") as f:
        content = f.read()
    assert "@prefix :" in content
