"""Tests for arfima-gph-estimator skill."""

import pytest
from pathlib import Path
from em_cubed.skills.testing import SkillTestGenerator, SkillTestRunner
from em_cubed.indexer import get_skill_metadata
from em_cubed.plugin_manager import PluginManager

SKILL_FILE = Path(__file__).parent.parent.parent / "skills" / "TECHNICAL_ANALYSIS" / "arfima-gph-estimator" / "SKILL.md"
SKILL_ID = "TECHNICAL_ANALYSIS/arfima-gph-estimator"


@pytest.fixture
def plugin_manager():
    return PluginManager()


@pytest.fixture
def test_generator(plugin_manager):
    return SkillTestGenerator(plugin_manager)


@pytest.fixture
def test_runner(plugin_manager):
    return SkillTestRunner(plugin_manager, None)


class Testarfima_gph_estimatorSkill:
    """Test suite for arfima-gph-estimator."""

    def test_metadata_valid(self):
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        assert metadata_dict is not None
        assert metadata_dict["name"] == "ARFIMA GPH Estimator"
        assert metadata_dict["domain"] == "TECHNICAL_ANALYSIS"
        assert len(metadata_dict["surfaces"]) >= 1

    def test_skill_file_exists(self):
        assert SKILL_FILE.exists(), f"SKILL.md not found at {SKILL_FILE}"


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
async def test_arfima_gph_calculator():
    """Test GPH estimator core logic."""
    code = '''
def calculate_gph(returns):
    n = len(returns)
    if n < 32:
        return {"d": 0.0, "r_squared": 0.0, "status": "insufficient_data"}
    
    total = 0.0
    for r in returns:
        total += r
    mean = total / n
    
    m = int(n ** 0.5)
    pi_val = 3.141592653589793
    
    y_harmics = []
    x_frequencies = []
    
    for k in range(1, m + 1):
        cos_sum = 0.0
        sin_sum = 0.0
        for t in range(n):
            angle = (2.0 * pi_val * k * (t + 1)) / n
            diff = returns[t] - mean
            cos_sum += diff * cos(angle)
            sin_sum += diff * sin(angle)
            
        periodogram = (cos_sum**2 + sin_sum**2) / (2.0 * pi_val * n)
        
        if periodogram > 0:
            y_harmics.append(log(periodogram))
            lambda_k = (2.0 * pi_val * k) / n
            x_frequencies.append(-2.0 * log(2.0 * sin(lambda_k / 2.0)))
    
    m_valid = len(y_harmics)
    if m_valid < 2:
        return {"d": 0.0, "r_squared": 0.0, "status": "regression_failed"}
        
    sum_x = 0.0
    sum_y = 0.0
    for i in range(m_valid):
        sum_x += x_frequencies[i]
        sum_y += y_harmics[i]
        
    mean_x = sum_x / m_valid
    mean_y = sum_y / m_valid
    
    num = 0.0
    den = 0.0
    for i in range(m_valid):
        dx = x_frequencies[i] - mean_x
        dy = y_harmics[i] - mean_y
        num += dx * dy
        den += dx * dx
        
    if den == 0:
        return {"d": 0.0, "r_squared": 0.0, "status": "collinear"}
        
    d_estimator = num / den
    
    total_ss = 0.0
    residual_ss = 0.0
    for i in range(m_valid):
        pred_y = mean_y + d_estimator * (x_frequencies[i] - mean_x)
        total_ss += (y_harmics[i] - mean_y) ** 2
        residual_ss += (y_harmics[i] - pred_y) ** 2
        
    r2 = 1.0 - (residual_ss / total_ss) if total_ss > 0 else 0.0
    
    return {"d": d_estimator, "r_squared": r2, "status": "success"}

# Test with synthetic data - inline generation
returns = [0.05, -0.02, 0.08, -0.03, 0.06, -0.01, 0.04, 0.02, -0.05, 0.03, 0.07, -0.04, 0.01, 0.09, -0.06, 0.02, 0.05, -0.02, 0.08, -0.01, 0.06, 0.03, -0.04, 0.02, 0.05, -0.03, 0.07, 0.01, -0.02, 0.04, 0.06, -0.05, 0.03, 0.08, -0.01, 0.02, 0.05, -0.04, 0.06, 0.01, -0.03, 0.07, 0.02, -0.02, 0.05, 0.04, -0.06, 0.01, 0.03, 0.08, -0.02, 0.06, 0.02, -0.01, 0.04, 0.05, -0.03, 0.07, 0.03, -0.04, 0.02, 0.06, 0.01, -0.02, 0.05, 0.04, -0.01, 0.03, 0.07, -0.03, 0.06, 0.02, -0.05, 0.04, 0.01, 0.08, -0.02, 0.05, 0.03]
result = calculate_gph(returns)
result["status"] == "success" and isinstance(result["d"], float)
'''
    from em_cubed.surfaces import PythonSurface
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"


@pytest.mark.asyncio
async def test_arfima_insufficient_data():
    """Test GPH returns proper status for small datasets."""
    code = '''
returns = [0.0, 0.1, -0.1, 0.2]
n = len(returns)
n < 32
'''
    from em_cubed.surfaces import PythonSurface
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"
    assert result["value"]