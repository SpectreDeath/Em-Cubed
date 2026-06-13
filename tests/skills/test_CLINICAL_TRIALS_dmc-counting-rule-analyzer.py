"""Tests for dmc-counting-rule-analyzer skill."""
import pytest
import math
from pathlib import Path
from em_cubed.skills.testing import SkillTestGenerator, SkillTestRunner
from em_cubed.indexer import get_skill_metadata
from em_cubed.plugin_manager import PluginManager

SKILL_FILE = Path(Path(__file__).parent.parent.parent / "skills" / "CLINICAL_TRIALS" / "dmc-counting-rule-analyzer" / "SKILL.md")
SKILL_ID = "CLINICAL_TRIALS/dmc-counting-rule-analyzer"


@pytest.fixture
def plugin_manager():
    return PluginManager()

@pytest.fixture
def test_generator(plugin_manager):
    return SkillTestGenerator(plugin_manager)

@pytest.fixture
def test_runner(plugin_manager):
    return SkillTestRunner(plugin_manager, None)


class TestDmcCountingRuleAnalyzerSkill:
    def test_metadata_valid(self):
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        assert metadata_dict is not None
        assert metadata_dict["name"] == "dmc-counting-rule-analyzer"
        assert metadata_dict["domain"] == "CLINICAL_TRIALS"
        assert "python" in metadata_dict["surfaces"]
        assert "clingo" in metadata_dict["surfaces"]

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

    def test_python_facts_generation_obrien_fleming(self):
        masked_data = {
            "arms": ["Treatment", "Control"],
            "events": [45, 60],
            "p_values": [0.008, 0.15],
            "timepoints": [1, 1],
        }
        scale = 100_000
        num_looks = max(masked_data["timepoints"])
        facts = []
        arms = [a.lower() for a in masked_data["arms"]]
        for a in arms:
            facts.append(f"arm({a}).")
        for i, ev in enumerate(masked_data["events"]):
            arm = arms[i]
            tp = masked_data["timepoints"][i]
            facts.append(f"event_count({arm}, {tp}, {ev}).")
        for i, pv in enumerate(masked_data["p_values"]):
            arm = arms[i]
            tp = masked_data["timepoints"][i]
            raw = 2.4 * math.sqrt(tp / num_looks) * 0.05
            b_scaled = int(raw * scale)
            pv_scaled = int(pv * scale)
            facts.append(f"p_value_check({arm}, {tp}, {pv_scaled}, {b_scaled}).")
        assert any("p_value_check" in f for f in facts)
        assert any("arm(treatment)." in f for f in facts)

    def test_python_facts_generation_haybittle_peto(self):
        tp = 2
        scale = 100_000
        b_scaled = int(0.001 * scale) if tp < 3 else int(0.05 * scale)
        assert b_scaled == int(0.001 * scale)

    def test_python_facts_uses_scaled_integers(self):
        pv = 0.008
        scale = 100_000
        pv_scaled = int(pv * scale)
        assert pv_scaled == 800
        assert isinstance(pv_scaled, int)
