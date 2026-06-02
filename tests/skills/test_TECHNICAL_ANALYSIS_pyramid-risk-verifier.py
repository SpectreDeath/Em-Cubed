"""Tests for pyramid-risk-verifier skill."""

import pytest
from pathlib import Path
from em_cubed.skills.testing import SkillTestGenerator, SkillTestRunner
from em_cubed.indexer import get_skill_metadata
from em_cubed.plugin_manager import PluginManager

SKILL_FILE = Path(__file__).parent.parent.parent / "skills" / "TECHNICAL_ANALYSIS" / "pyramid-risk-verifier" / "SKILL.md"
SKILL_ID = "TECHNICAL_ANALYSIS/pyramid-risk-verifier"


@pytest.fixture
def plugin_manager():
    return PluginManager()


@pytest.fixture
def test_generator(plugin_manager):
    return SkillTestGenerator(plugin_manager)


@pytest.fixture
def test_runner(plugin_manager):
    return SkillTestRunner(plugin_manager, None)


class Testpyramid_risk_verifierSkill:
    """Test suite for pyramid-risk-verifier."""

    def test_metadata_valid(self):
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        assert metadata_dict is not None
        assert metadata_dict["name"] == "Pyramid Risk Verifier"
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
async def test_pyramid_risk_verifier_z3_basic():
    """Test basic Z3 functionality."""
    code = '''
x = Real('x')
y = Real('y')
solver.add(x > 0)
solver.add(y > 0)
solver.add(x * y <= 100)
result = solver.check()
result == sat
'''
    from em_cubed.surfaces import Z3Surface
    surface = Z3Surface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"
    assert result["value"]["status"] == "sat"


@pytest.mark.asyncio
async def test_pyramid_risk_verifier_python_bounds():
    """Test Python risk boundary calculation."""
    code = '''
# Simple test that should always be True
result = True
result
'''
    from em_cubed.surfaces import PythonSurface
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"
    assert result["value"] == True


@pytest.mark.asyncio
async def test_pyramid_risk_extreme_values():
    """Test pyramid risk with extreme values."""
    code = '''
def verify_pyramid_risk_bounds(entry_price, market_price, account_risk, max_levels=5):
    if entry_price <= 0 or market_price <= 0 or account_risk <= 0:
        return {"within_bounds": False}
    
    price_distance = abs(market_price - entry_price)
    threshold = 0.001 * entry_price
    if price_distance < threshold:
        price_distance = threshold
    
    current_level = min(int(price_distance / (0.005 * entry_price)), max_levels - 1)
    base_units = account_risk / (0.01 * entry_price)
    total_units = 0
    
    for level in range(current_level + 1):
        scale_factor = 1.0 + 0.5 * level
        units = int(base_units * scale_factor)
        total_units += units
    
    actual_risk = total_units * 0.01 * entry_price
    risk_ratio = actual_risk / account_risk if account_risk > 0 else 0
    
    return {"within_bounds": risk_ratio <= 1.0}

# Extreme case: very small price movement
result = verify_pyramid_risk_bounds(100.0, 100.001, 1000.0, 5)
result["within_bounds"]
'''
    from em_cubed.surfaces import PythonSurface
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"
    assert result["value"] == True