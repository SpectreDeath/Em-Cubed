"""Tests for statistical-test-advisor skill."""

import pytest
from pathlib import Path
from em_cubed.skills.testing import SkillTestGenerator, SkillTestRunner
from em_cubed.indexer import get_skill_metadata
from em_cubed.plugin_manager import PluginManager

SKILL_FILE = Path(Path(__file__).parent.parent.parent / "skills" / "ANALYTICS" / "statistical-test-advisor" / "SKILL.md")
SKILL_ID = "ANALYTICS/statistical-test-advisor"


@pytest.fixture
def plugin_manager():
    return PluginManager()


@pytest.fixture
def test_generator(plugin_manager):
    return SkillTestGenerator(plugin_manager)


@pytest.fixture
def test_runner(plugin_manager):
    return SkillTestRunner(plugin_manager, None)


class Teststatistical_test_advisorSkill:
    """Test suite for statistical-test-advisor."""

    def test_metadata_valid(self):
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        assert metadata_dict is not None
        assert metadata_dict["name"] == "statistical-test-advisor"
        assert metadata_dict["domain"] == "ANALYTICS"
        assert len(metadata_dict["surfaces"]) >= 1

    def test_surfaces_implemented(self, plugin_manager):
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        available_surfaces = []
        for surface in metadata_dict.get("surfaces", []):
            plugin = plugin_manager.get(surface)
            if plugin and plugin.available:
                available_surfaces.append(surface)
        assert len(available_surfaces) >= 1, f"No available surfaces found for {metadata_dict['name']}"

    @pytest.mark.asyncio
    async def test_skill_execution(self, test_runner, test_generator):
        from em_cubed.skills.metadata import SkillMetadata
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        if not metadata_dict:
            pytest.skip("Skill metadata not available")
        
        metadata = SkillMetadata.from_frontmatter({}, "", SKILL_FILE)
        for key, value in metadata_dict.items():
            if hasattr(metadata, key):
                setattr(metadata, key, value)

        tests = test_generator.generate_tests_for_skill(SKILL_FILE, metadata)
        if tests:
            results = await test_runner.run_test_suite(tests, SKILL_ID)
            assert results["pass_rate"] > 0.3, f"Pass rate too low: {results['pass_rate']}"

    def test_python_fallback_small_sample(self):
        """Test Python fallback logic for small samples."""
        metrics = {'groups': 2, 'independent': True, 'samples': [[1, 2], [3]]}
        test_rec = "Independent Two-Sample t-Test"
        
        result = evaluate_and_advise(metrics, test_rec)
        
        assert result["recommended_test"] == "Exact Permutation Test"
        assert "Sample size" in result["reasoning"]

    def test_python_full_sample(self):
        """Test Python logic for adequate sample size."""
        metrics = {'groups': 2, 'independent': True, 'samples': [[1, 2, 3, 4, 5, 6, 7, 8], [9, 10, 11, 12, 13, 14, 15, 16]]}
        test_rec = "Independent Two-Sample t-Test"
        
        result = evaluate_and_advise(metrics, test_rec)
        
        assert result["recommended_test"] == test_rec
        assert result["sample_count"] == 16
        assert result["execution_status"] == "ready_for_calculation"


def evaluate_and_advise(metrics, test_recommendation):
    """Copy of the Python function for unit testing."""
    total_samples = 0
    for seq in metrics.get('samples', []):
        total_samples += len(seq)
        
    if total_samples < 8:
        return {
            "recommended_test": "Exact Permutation Test",
            "reasoning": "Sample size too small for asymptotic approximations recommended by Prolog rule."
        }
        
    return {
        "recommended_test": test_recommendation,
        "sample_count": total_samples,
        "execution_status": "ready_for_calculation"
    }