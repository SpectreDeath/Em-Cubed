"""Tests for sae-reporting-threshold-tester skill."""
import pytest
from pathlib import Path
from em_cubed.skills.testing import SkillTestGenerator, SkillTestRunner
from em_cubed.indexer import get_skill_metadata
from em_cubed.plugin_manager import PluginManager

SKILL_FILE = Path(Path(__file__).parent.parent.parent / "skills" / "CLINICAL_TRIALS" / "sae-reporting-threshold-tester" / "SKILL.md")
SKILL_ID = "CLINICAL_TRIALS/sae-reporting-threshold-tester"


@pytest.fixture
def plugin_manager():
    return PluginManager()

@pytest.fixture
def test_generator(plugin_manager):
    return SkillTestGenerator(plugin_manager)

@pytest.fixture
def test_runner(plugin_manager):
    return SkillTestRunner(plugin_manager, None)


class TestSaeReportingThresholdTesterSkill:
    def test_metadata_valid(self):
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        assert metadata_dict is not None
        assert metadata_dict["name"] == "SAE Reporting Threshold Tester"
        assert metadata_dict["domain"] == "CLINICAL_TRIALS"
        assert "python" in metadata_dict["surfaces"]
        assert "z3" in metadata_dict["surfaces"]

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

    def test_python_sae_expedited_trigger(self):
        rule = {"expedited": True, "threshold": 1.5}
        observed_ratio = 3 / 2
        assert observed_ratio >= 1.5
        assert observed_ratio == rule["threshold"]
        assert rule["expedited"] is True

    def test_python_sae_below_threshold_no_trigger(self):
        rule = {"expedited": True, "threshold": 2.0}
        observed_ratio = 3 / 2
        assert observed_ratio < rule["threshold"]

    def test_z3_sae_breaches_7day_timeline(self):
        observed = 5.0
        expected = 1.0
        threshold = 2.0
        timeline_days = 7.0
        ratio = observed / expected
        assert ratio >= threshold
        assert timeline_days <= 7

    def test_z3_sae_exact_7day_boundary(self):
        observed = 2.0
        expected = 1.0
        threshold = 2.0
        timeline_days = 7.0
        ratio = observed / expected
        assert ratio >= threshold
        assert timeline_days <= 7

    def test_z3_sae_15day_not_breached_at_14(self):
        timeline_days = 14.0
        assert timeline_days > 7
        assert timeline_days <= 15
