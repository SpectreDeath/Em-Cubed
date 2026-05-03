"""Tests for uncertainty-quantifier skill."""

import pytest
from pathlib import Path
from em_cubed.skills.testing import SkillTestGenerator, SkillTestRunner
from em_cubed.indexer import get_skill_metadata
from em_cubed.plugin_manager import PluginManager

SKILL_FILE = Path("D:/GitHub/projects/em-cubed/skills/STATISTICS/uncertainty-quantifier/SKILL.md")
SKILL_ID = "STATISTICS/uncertainty-quantifier"


@pytest.fixture
def plugin_manager():
    """Get plugin manager."""
    return PluginManager()


@pytest.fixture
def test_generator(plugin_manager):
    """Get test generator."""
    return SkillTestGenerator(plugin_manager)


@pytest.fixture
def test_runner(plugin_manager):
    """Get test runner."""
    return SkillTestRunner(plugin_manager, None)


class Testuncertainty_quantifierSkill:
    """Test suite for uncertainty-quantifier."""

    def test_metadata_valid(self):
        """Test skill metadata is valid."""
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        assert metadata_dict is not None
        assert metadata_dict["name"] == "uncertainty-quantifier"
        assert metadata_dict["domain"] == "STATISTICS"
        assert len(metadata_dict["surfaces"]) >= 1

    def test_surfaces_implemented(self, plugin_manager):
        """Test required surfaces are available."""
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        for surface in metadata_dict.get("surfaces", []):
            plugin = plugin_manager.get(surface)
            if plugin:
                assert plugin.available, f"Surface {surface} not available"

    @pytest.mark.asyncio
    async def test_skill_execution(self, test_runner, test_generator):
        """Test basic skill execution."""
        from em_cubed.skills.metadata import SkillMetadata
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        if not metadata_dict:
            pytest.skip("Skill metadata not available")
        
        metadata = SkillMetadata.from_frontmatter({}, "", SKILL_FILE)
        # Populate from dict
        for key, value in metadata_dict.items():
            if hasattr(metadata, key):
                setattr(metadata, key, value)

        tests = test_generator.generate_tests_for_skill(SKILL_FILE, metadata)
        if tests:
            results = await test_runner.run_test_suite(tests, SKILL_ID)
            # At least some tests should pass for a valid skill
            assert results["pass_rate"] > 0.3, f"Pass rate too low: {results['pass_rate']}"

