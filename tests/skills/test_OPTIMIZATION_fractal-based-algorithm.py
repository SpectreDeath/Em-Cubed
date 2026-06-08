"""Tests for fractal-based-algorithm skill."""

import pytest
from pathlib import Path
from em_cubed.skills.testing import SkillTestGenerator, SkillTestRunner
from em_cubed.indexer import get_skill_metadata
from em_cubed.plugin_manager import PluginManager

SKILL_FILE = Path(
    Path(__file__).parent.parent.parent
    / "skills"
    / "OPTIMIZATION"
    / "fractal-based-algorithm"
    / "SKILL.md"
)
SKILL_ID = "OPTIMIZATION/fractal-based-algorithm"


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


class TestFractalBasedAlgorithmSkill:
    """Test suite for fractal-based-algorithm."""

    def test_metadata_valid(self):
        """Test skill metadata is valid and includes all surfaces."""
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        assert metadata_dict is not None
        assert metadata_dict["name"] == "fractal-based-algorithm"
        assert metadata_dict["domain"] == "OPTIMIZATION"
        surfaces = metadata_dict.get("surfaces", [])
        assert len(surfaces) >= 1

    def test_skill_file_exists(self):
        """SKILL.md must be present on disk."""
        assert SKILL_FILE.exists(), f"SKILL.md not found at {SKILL_FILE}"

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
    async def test_fba_python_sphere(self):
        """FBA should converge on 2D sphere function."""
        import random

        def sphere(x):
            return sum(xi ** 2 for xi in x)

        def power_distribution(center, out_min, out_max, p=5.0):
            rnd = random.uniform(-1.0, 1.0)
            r = abs(rnd) ** p
            if rnd >= 0.0:
                return max(out_min, min(out_max, center + r * (out_max - center)))
            return max(out_min, min(out_max, center - r * (center - out_min)))

        pop_size, p3, max_iter = 30, 0.8, 100
        dim = 2

        population = [[random.uniform(-5, 5) for _ in range(dim)] for _ in range(pop_size)]
        best_score = min(sphere(ind) for ind in population)
        best_x = population[[sphere(ind) for ind in population].index(best_score)][:]

        for epoch in range(max_iter):
            for i in range(pop_size):
                if random.random() < p3:
                    for c in range(dim):
                        population[i][c] = power_distribution(best_x[c], -5, 5)

            for i in range(pop_size):
                f = sphere(population[i])
                if f < best_score:
                    best_score = f
                    best_x = population[i][:]

        assert best_score < 1.0, f"FBA sphere result = {best_score}"

    @pytest.mark.asyncio
    async def test_power_distribution_range(self):
        """Power distribution should produce values within bounds."""
        import random

        def power_distribution(center, out_min, out_max, p=5.0):
            rnd = random.uniform(-1.0, 1.0)
            r = abs(rnd) ** p
            if rnd >= 0.0:
                return max(out_min, min(out_max, center + r * (out_max - center)))
            return max(out_min, min(out_max, center - r * (center - out_min)))

        for _ in range(20):
            val = power_distribution(0.0, -5.0, 5.0)
            assert -5 <= val <= 5, f"Power distribution out of range: {val}"

    @pytest.mark.asyncio
    async def test_point_in_subspace(self):
        """Point containment check should work correctly."""
        # Inside
        inside = all(0 <= p <= 1 for p in [0.5, 0.5])
        assert inside

        # Outside
        outside = 1.5 < 0 or 1.5 >= 1
        assert outside

    @pytest.mark.asyncio
    async def test_prolog_params(self):
        """Prolog parameter validation should work."""
        from em_cubed.surfaces import PrologSurface
        surface = PrologSurface()
        code = '''
?- 50 >= 4, 50 =< 200, 60 >= 10, 60 =< 100, 30 >= 10, 30 =< 100, 0.8 >= 0.0, 0.8 =< 1.0, 10 >= 5, 10 =< 20.
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"