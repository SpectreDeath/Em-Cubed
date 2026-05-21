"""Tests for hy_fuzzy_logic skill."""

import pytest
from pathlib import Path
from em_cubed.skills.testing import SkillTestGenerator, SkillTestRunner
from em_cubed.indexer import get_skill_metadata
from em_cubed.plugin_manager import PluginManager

SKILL_FILE = Path(Path(__file__).parent.parent.parent / "skills" / "General" / "hy_fuzzy_logic" / "SKILL.md")
SKILL_ID = "General/hy_fuzzy_logic"


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


class Testhy_fuzzy_logicSkill:
    """Test suite for hy_fuzzy_logic."""

    def test_metadata_valid(self):
        """Test skill metadata is valid."""
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        assert metadata_dict is not None
        assert metadata_dict["name"] == "hy_fuzzy_logic"
        assert metadata_dict["domain"] == "General"
        assert len(metadata_dict["surfaces"]) >= 1

    def test_surfaces_implemented(self, plugin_manager):
        """Test at least one required surface is available."""
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        available_surfaces = []
        for surface in metadata_dict.get("surfaces", []):
            plugin = plugin_manager.get(surface)
            if plugin and plugin.available:
                available_surfaces.append(surface)
        assert len(available_surfaces) >= 1, f"No available surfaces found for {metadata_dict['name']}"

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

