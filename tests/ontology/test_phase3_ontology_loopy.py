"""Unit tests for Phase 3: Kit Fine Counterfactual Fault Localization & Self-Healing Skill Loop."""

from pathlib import Path
import tempfile
from em_cubed.loopy.self_healing import SelfHealingSkillLoop
from em_cubed.ontology.schema import OntologyTriple
from em_cubed.ontology.truthmaker import ExactTruthmakerClassifier


def test_counterfactual_fault_localization():
    actual_triples = [
        OntologyTriple(subject="AgentA", predicate="executesTool", object="Tool1"),
        OntologyTriple(subject="Tool1", predicate="hasStatus", object="Success"),
    ]

    expected_preds = ["executesTool", "hasStatus", "validatesState"]

    res = ExactTruthmakerClassifier.locate_counterfactual_fault(
        proposition="Agent Execution Complete",
        expected_predicates=expected_preds,
        actual_triples=actual_triples,
    )

    assert res["fault_detected"] is True
    assert "validatesState" in res["missing_predicates"]


def test_self_healing_skill_loop():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        skills_dir = tmp_path / "skills"
        skill_file = skills_dir / "General" / "calculator" / "SKILL.md"
        skill_file.parent.mkdir(parents=True)
        skill_file.write_text("---\nname: calculator\nsurfaces:\n  - python\n---\n# Calculator", encoding="utf-8")

        healer = SelfHealingSkillLoop(skills_dir=skills_dir)
        res = healer.detect_and_repair_skill("General/calculator", "TypeError: unsupported operand type")

        assert res["repaired"] is True
        assert "Self-Healing Patch" in skill_file.read_text(encoding="utf-8")
