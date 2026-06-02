"""Tests for falling-risk-pyramid skill."""

import pytest
from pathlib import Path
from em_cubed.skills.testing import SkillTestGenerator, SkillTestRunner
from em_cubed.indexer import get_skill_metadata
from em_cubed.plugin_manager import PluginManager

SKILL_FILE = Path(__file__).parent.parent.parent / "skills" / "TECHNICAL_ANALYSIS" / "falling-risk-pyramid" / "SKILL.md"
SKILL_ID = "TECHNICAL_ANALYSIS/falling-risk-pyramid"


@pytest.fixture
def plugin_manager():
    return PluginManager()


@pytest.fixture
def test_generator(plugin_manager):
    return SkillTestGenerator(plugin_manager)


@pytest.fixture
def test_runner(plugin_manager):
    return SkillTestRunner(plugin_manager, None)


class Testfalling_risk_pyramidSkill:
    """Test suite for falling-risk-pyramid."""

    def test_metadata_valid(self):
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        assert metadata_dict is not None
        assert metadata_dict["name"] == "Falling-Risk Pyramid"
        assert metadata_dict["domain"] == "TECHNICAL_ANALYSIS"
        assert len(metadata_dict["surfaces"]) >= 1

    def test_skill_file_exists(self):
        assert SKILL_FILE.exists(), f"SKILL.md not found at {SKILL_FILE}"

    def test_cangjie_file_exists(self):
        cangjie = SKILL_FILE.parent / "SKILL_CANGJIE.md"
        assert cangjie.exists(), f"SKILL_CANGJIE.md not found at {cangjie}"

    def test_surfaces_implemented(self, plugin_manager):
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
async def test_falling_risk_pyramid_calculator():
    """Test falling-risk pyramid core logic."""
    code = '''
def compute_pyramid(entry_price, market_price, account_risk, max_levels=5):
    price_distance = abs(market_price - entry_price)
    threshold = 0.001 * entry_price
    if price_distance < threshold:
        price_distance = threshold
    
    current_level = min(int(price_distance / (0.005 * entry_price)), max_levels - 1)
    base_units = account_risk / (0.01 * entry_price)
    
    positions = []
    for level in range(current_level + 1):
        scale_factor = 1.0 + 0.5 * level
        units = int(base_units * scale_factor)
        step = 0.005 * (level + 1)
        if market_price > entry_price:
            entry_adj = entry_price * (1 + step)
            stop_loss = entry_price - (account_risk / (units * (max_levels - level)))
        else:
            entry_adj = entry_price * (1 - step)
            stop_loss = entry_price + (account_risk / (units * (max_levels - level)))
        
        positions.append({"level": level, "units": units, "entry": entry_adj, "stop_loss": stop_loss})
    
    total = 0
    for p in positions:
        total += p["units"]
    
    return {"current_level": current_level, "positions": positions, "total_units": total}

r = compute_pyramid(100.0, 105.0, 1000.0, 5)
r["current_level"] >= 0 and r["total_units"] > 0
'''
    from em_cubed.surfaces import PythonSurface
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"


@pytest.mark.asyncio
async def test_pyramid_bullish_scaling():
    """Test pyramid scaling in bullish direction."""
    code = '''
entry_price = 100.0
market_price = 103.0
price_distance = abs(market_price - entry_price)
current_level = min(int(price_distance / (0.005 * entry_price)), 4)
current_level >= 0
'''
    from em_cubed.surfaces import PythonSurface
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"
    assert result["value"] == True


@pytest.mark.asyncio
async def test_pyramid_bearish_scaling():
    """Test pyramid scaling in bearish direction."""
    code = '''
entry_price = 100.0
market_price = 95.0
price_distance = abs(market_price - entry_price)
current_level = min(int(price_distance / (0.005 * entry_price)), 4)
current_level >= 0
'''
    from em_cubed.surfaces import PythonSurface
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"
    assert result["value"] == True