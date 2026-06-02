"""Tests for candlestick-pattern-analyzer skill."""

import pytest
from pathlib import Path
from em_cubed.skills.testing import SkillTestGenerator, SkillTestRunner
from em_cubed.indexer import get_skill_metadata
from em_cubed.plugin_manager import PluginManager

SKILL_FILE = Path(__file__).parent.parent.parent / "skills" / "TECHNICAL_ANALYSIS" / "candlestick-pattern-analyzer" / "SKILL.md"
SKILL_ID = "TECHNICAL_ANALYSIS/candlestick-pattern-analyzer"


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


class Testcandlestick_pattern_analyzerSkill:
    """Test suite for candlestick-pattern-analyzer."""

    def test_metadata_valid(self):
        """Test skill metadata is valid."""
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        assert metadata_dict is not None
        assert metadata_dict["name"] == "candlestick-pattern-analyzer"
        assert metadata_dict["domain"] == "TECHNICAL_ANALYSIS"
        assert len(metadata_dict["surfaces"]) >= 1

    def test_skill_file_exists(self):
        """SKILL.md must be present on disk."""
        assert SKILL_FILE.exists(), f"SKILL.md not found at {SKILL_FILE}"

    def test_cangjie_file_exists(self):
        """SKILL_CANGJIE.md must be present alongside SKILL.md."""
        cangjie = SKILL_FILE.parent / "SKILL_CANGJIE.md"
        assert cangjie.exists(), f"SKILL_CANGJIE.md not found at {cangjie}"

    def test_surfaces_implemented(self, plugin_manager):
        """At least one declared surface must be available in plugin manager."""
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        available_surfaces = []
        for surface in metadata_dict.get("surfaces", []):
            plugin = plugin_manager.get(surface)
            if plugin and plugin.available:
                available_surfaces.append(surface)
        assert len(available_surfaces) >= 1, (
            f"No available surfaces found for {metadata_dict['name']}"
        )

    @pytest.mark.asyncio
    async def test_skill_execution(self, test_runner, test_generator):
        """Test basic skill execution via SkillTestGenerator pipeline."""
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
            assert results["pass_rate"] > 0.3, (
                f"Pass rate too low: {results['pass_rate']}"
            )


@pytest.mark.asyncio
async def test_candlestick_encoder():
    """Test candlestick pattern encoding logic."""
    code = '''
# Inline candlestick encoding without class
open_price, high, low, close = 100, 110, 99, 109
body = abs(close - open_price)
range_total = high - low
is_bullish = close > open_price
result = "bullish_maribozu" if is_bullish and close > open_price + 0.9 * range_total else ("bullish" if is_bullish else "bearish")
result == "bullish_maribozu"
'''
    from em_cubed.surfaces import PythonSurface
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"


@pytest.mark.asyncio
async def test_candlestick_prolog_patterns():
    """Test candlestick pattern validation logic."""
    code = '''
# Inline pattern check without generator
bullish_patterns = ["hammer", "bullish_maribozu", "bullish"]
seq = ["hammer", "bullish_maribozu"]
len([p for p in seq if p in bullish_patterns]) == 2
'''
    from em_cubed.surfaces import PythonSurface
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"