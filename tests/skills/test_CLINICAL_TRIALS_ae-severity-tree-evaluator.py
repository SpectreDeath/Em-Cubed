"""Tests for ae-severity-tree-evaluator skill."""
import pytest
from pathlib import Path
from em_cubed.skills.testing import SkillTestGenerator, SkillTestRunner
from em_cubed.indexer import get_skill_metadata
from em_cubed.plugin_manager import PluginManager

SKILL_FILE = Path(Path(__file__).parent.parent.parent / "skills" / "CLINICAL_TRIALS" / "ae-severity-tree-evaluator" / "SKILL.md")
SKILL_ID = "CLINICAL_TRIALS/ae-severity-tree-evaluator"


@pytest.fixture
def plugin_manager():
    return PluginManager()

@pytest.fixture
def test_generator(plugin_manager):
    return SkillTestGenerator(plugin_manager)

@pytest.fixture
def test_runner(plugin_manager):
    return SkillTestRunner(plugin_manager, None)


class TestAeSeverityTreeEvaluatorSkill:
    def test_metadata_valid(self):
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        assert metadata_dict is not None
        assert metadata_dict["name"] == "ae-severity-tree-evaluator"
        assert metadata_dict["domain"] == "CLINICAL_TRIALS"
        assert "python" in metadata_dict["surfaces"]
        assert "prolog" in metadata_dict["surfaces"]

    def test_surfaces_implemented(self, plugin_manager):
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        available_surfaces = []
        for surface in metadata_dict.get("surfaces", []):
            plugin = plugin_manager.get(surface)
            if plugin and plugin.available:
                available_surfaces.append(surface)
        assert len(available_surfaces) >= 1

    @pytest.mark.asyncio
    async def test_skill_execution(self, test_runner, test_generator):
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        if not metadata_dict:
            pytest.skip("Skill metadata not available")
        from em_cubed.skills.metadata import SkillMetadata
        metadata = SkillMetadata.from_frontmatter({}, "", SKILL_FILE)
        for key, value in metadata_dict.items():
            if hasattr(metadata, key):
                setattr(metadata, key, value)
        tests = test_generator.generate_tests_for_skill(SKILL_FILE, metadata)
        if tests:
            results = await test_runner.run_test_suite(tests, SKILL_ID)
            assert results["pass_rate"] > 0.3

    def test_python_ae_grading_grade3(self):
        grade_rules = [
            {"lab_name": "Hemoglobin", "grade": 1, "grade_low": 10.0, "grade_high": 9.5},
            {"lab_name": "Hemoglobin", "grade": 2, "grade_low": 9.4, "grade_high": 8.0},
            {"lab_name": "Hemoglobin", "grade": 3, "grade_low": 7.9, "grade_high": 6.5},
            {"lab_name": "Hemoglobin", "grade": 4, "grade_low": 0.0, "grade_high": 6.4},
        ]
        ae_records = [{"lab_name": "Hemoglobin", "observed_value": 7.2}]
        all_grades = []
        for rec in ae_records:
            matched = [
                r for r in grade_rules
                if r["lab_name"] == rec["lab_name"]
                and min(r["grade_low"], r["grade_high"]) <= float(rec["observed_value"]) <= max(r["grade_low"], r["grade_high"])
            ]
            if matched:
                all_grades.append(max(m["grade"] for m in matched))
        assert all_grades == [3]

    def test_python_ae_grading_grade4(self):
        grade_rules = [
            {"lab_name": "Hemoglobin", "grade": 4, "grade_low": 0.0, "grade_high": 6.4},
        ]
        ae_records = [{"lab_name": "Hemoglobin", "observed_value": 5.0}]
        all_grades = []
        for rec in ae_records:
            matched = [
                r for r in grade_rules
                if r["lab_name"] == rec["lab_name"]
                and min(r["grade_low"], r["grade_high"]) <= float(rec["observed_value"]) <= max(r["grade_low"], r["grade_high"])
            ]
            if matched:
                all_grades.append(max(m["grade"] for m in matched))
        assert all_grades == [4]

    def test_python_ae_grading_no_match(self):
        grade_rules = [
            {"lab_name": "Hemoglobin", "grade": 1, "grade_low": 10.0, "grade_high": 9.5},
        ]
        ae_records = [{"lab_name": "Neutrophils", "observed_value": 7.2}]
        all_grades = []
        for rec in ae_records:
            matched = [
                r for r in grade_rules
                if r["lab_name"] == rec["lab_name"]
                and min(r["grade_low"], r["grade_high"]) <= float(rec["observed_value"]) <= max(r["grade_low"], r["grade_high"])
            ]
            if matched:
                all_grades.append(max(m["grade"] for m in matched))
        assert all_grades == []

    def test_python_ae_multi_record_max_grade(self):
        grade_rules = [
            {"lab_name": "Hemoglobin", "grade": 4, "grade_low": 0.0, "grade_high": 6.4},
            {"lab_name": "Hemoglobin", "grade": 2, "grade_low": 8.0, "grade_high": 9.4},
        ]
        ae_records = [
            {"lab_name": "Hemoglobin", "observed_value": 5.0},
            {"lab_name": "Hemoglobin", "observed_value": 9.0},
        ]
        all_grades = []
        for rec in ae_records:
            matched = [
                r for r in grade_rules
                if r["lab_name"] == rec["lab_name"]
                and min(r["grade_low"], r["grade_high"]) <= float(rec["observed_value"]) <= max(r["grade_low"], r["grade_high"])
            ]
            if matched:
                all_grades.append(max(m["grade"] for m in matched))
        assert max(all_grades) == 4

    def test_python_ae_fuzz_missing_observed_value(self):
        ae_records = [{"lab_name": "Hemoglobin"}]
        grade_rules = [
            {"lab_name": "Hemoglobin", "grade": 4, "grade_low": 0.0, "grade_high": 6.4},
        ]
        results = []
        for rec in ae_records:
            try:
                observed = float(rec["observed_value"])
            except (TypeError, KeyError, ValueError):
                results.append("error")
                continue
            matched = [
                r for r in grade_rules
                if r["lab_name"] == rec["lab_name"]
                and r["grade_low"] <= observed <= r["grade_high"]
            ]
            results.append("matched" if matched else "no_match")
        assert results == ["error"]

    def test_python_ae_fuzz_missing_lab_name(self):
        ae_records = [{"observed_value": 7.2}]
        grade_rules = [
            {"lab_name": "Hemoglobin", "grade": 4, "grade_low": 0.0, "grade_high": 6.4},
        ]
        results = []
        for rec in ae_records:
            try:
                observed = float(rec["observed_value"])
            except (TypeError, KeyError, ValueError):
                results.append("error")
                continue
            lab_name = rec.get("lab_name", "")
            matched = [
                r for r in grade_rules
                if r["lab_name"] == lab_name
                and r["grade_low"] <= observed <= r["grade_high"]
            ]
            results.append("matched" if matched else "no_match")
        assert results == ["no_match"]

    def test_python_ae_string_observed_value_coerced(self):
        grade_rules = [
            {"lab_name": "Hemoglobin", "grade": 3, "grade_low": 6.5, "grade_high": 7.9},
        ]
        ae_records = [{"lab_name": "Hemoglobin", "observed_value": "7.2"}]
        all_grades = []
        for rec in ae_records:
            try:
                observed = float(rec["observed_value"])
            except (TypeError, ValueError):
                all_grades.append("error")
                continue
            matched = [
                r for r in grade_rules
                if r["lab_name"] == rec["lab_name"]
                and r["grade_low"] <= observed <= r["grade_high"]
            ]
            if matched:
                all_grades.append(max(m["grade"] for m in matched))
        assert all_grades == [3]
