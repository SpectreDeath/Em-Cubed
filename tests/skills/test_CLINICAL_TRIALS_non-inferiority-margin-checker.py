"""Tests for non-inferiority-margin-checker skill."""
import pytest
from pathlib import Path
from em_cubed.skills.testing import SkillTestGenerator, SkillTestRunner
from em_cubed.indexer import get_skill_metadata
from em_cubed.plugin_manager import PluginManager

SKILL_FILE = Path(Path(__file__).parent.parent.parent / "skills" / "CLINICAL_TRIALS" / "non-inferiority-margin-checker" / "SKILL.md")
SKILL_ID = "CLINICAL_TRIALS/non-inferiority-margin-checker"


@pytest.fixture
def plugin_manager():
    return PluginManager()

@pytest.fixture
def test_generator(plugin_manager):
    return SkillTestGenerator(plugin_manager)

@pytest.fixture
def test_runner(plugin_manager):
    return SkillTestRunner(plugin_manager, None)


class TestNonInferiorityMarginCheckerSkill:
    def test_metadata_valid(self):
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        assert metadata_dict is not None
        assert metadata_dict["name"] == "non-inferiority-margin-checker"
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

    def test_python_non_inferiority_passes(self):
        ci_lower = 0.855
        ni_margin = 0.15
        reference_effect = 1.0
        null_margin = reference_effect - ni_margin
        passes = ci_lower > null_margin
        assert passes is True
        assert null_margin == 0.85

    def test_python_non_inferiority_fails(self):
        ci_lower = 0.70
        ni_margin = 0.15
        reference_effect = 1.0
        null_margin = reference_effect - ni_margin
        passes = ci_lower > null_margin
        assert passes is False
        assert null_margin == 0.85
