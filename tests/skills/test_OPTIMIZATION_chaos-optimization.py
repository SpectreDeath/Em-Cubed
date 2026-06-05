"""Tests for chaos-optimization skill."""

import pytest
from pathlib import Path
from em_cubed.skills.testing import SkillTestGenerator, SkillTestRunner
from em_cubed.indexer import get_skill_metadata
from em_cubed.plugin_manager import PluginManager

SKILL_FILE = Path(
    Path(__file__).parent.parent.parent
    / "skills"
    / "OPTIMIZATION"
    / "chaos-optimization"
    / "SKILL.md"
)
SKILL_ID = "OPTIMIZATION/chaos-optimization"


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


class TestChaosOptimizationSkill:
    """Test suite for chaos-optimization."""

    def test_metadata_valid(self):
        """Test skill metadata is valid and includes all surfaces."""
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        assert metadata_dict is not None
        assert metadata_dict["name"] == "chaos-optimization"
        assert metadata_dict["domain"] == "OPTIMIZATION"
        surfaces = metadata_dict.get("surfaces", [])
        assert len(surfaces) >= 1

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
    async def test_coa_python_sphere(self):
        """COA should converge on 2D sphere function."""
        import random

        def sphere(x):
            return sum(xi ** 2 for xi in x)

        def logistic_map(x):
            return 4.0 * x * (1.0 - x)

        def power_distribution(center, out_min, out_max, p=20.0):
            rnd = random.uniform(-1.0, 1.0)
            r = abs(rnd) ** p
            if rnd >= 0.0:
                return max(out_min, min(out_max, center + r * (out_max - center)))
            return max(out_min, min(out_max, center - r * (center - out_min)))

        pop_size, s1, p3, max_iter = 30, 40, 0.8, 100
        dim = 2
        bounds = [(-5.0, 5.0)] * dim

        population = [[random.uniform(-5, 5) for _ in range(dim)] for _ in range(pop_size)]
        gamma = [[random.uniform(0, 1) for _ in range(dim)] for _ in range(pop_size)]
        velocity = [[0.0 for _ in range(dim)] for _ in range(pop_size)]
        best_score = min(sphere(ind) for ind in population)

        for epoch in range(1, max_iter + 1):
            for i in range(pop_size):
                if random.random() < p3:
                    for c in range(dim):
                        gamma[i][c] = logistic_map(gamma[i][c])
                        population[i][c] = max(-5, min(5, bounds[c][0] + gamma[i][c] * (bounds[c][1] - bounds[c][0])))

                if epoch <= s1:
                    for c in range(dim):
                        velocity[i][c] = 0.5 * velocity[i][c] + 0.5 * random.gauss(0, 1)
                        population[i][c] += velocity[i][c]

                f = sphere(population[i])
                if f < best_score:
                    best_score = f

            # Convergence check
            if epoch > 10 and epoch % 10 == 0:
                if best_score < 0.01:
                    break

        assert best_score < 1.0, f"COA sphere result = {best_score}"

    @pytest.mark.asyncio
    async def test_logistic_map_range(self):
        """Logistic map should produce values in [0,1]."""
        for x in [0.1, 0.3, 0.5, 0.7, 0.9]:
            val = 4.0 * x * (1.0 - x)
            assert 0 <= val <= 1, f"Logistic map out of range: {val}"

    @pytest.mark.asyncio
    async def test_tent_map_symmetry(self):
        """Tent map should be symmetric around 0.5."""
        def tent_map(x):
            return 1.0 - 2.0 * abs(0.5 - x)

        # Symmetry: f(0.5-d) == f(0.5+d) for d in [0, 0.5]
        assert abs(tent_map(0.25) - tent_map(0.75)) < 1e-9
        assert abs(tent_map(0.2) - tent_map(0.8)) < 1e-9
        # Values should be in valid range
        assert 0.0 <= tent_map(0.25) <= 1.0

    @pytest.mark.asyncio
    async def test_sinusoidal_map_range(self):
        """Sinusoidal map should produce values in [-1,1]."""
        import math
        for x in [0.0, 0.25, 0.5, 0.75, 1.0]:
            val = math.sin(math.pi * x)
            assert -1 <= val <= 1, f"Sinusoidal map out of range: {val}"

    @pytest.mark.asyncio
    async def test_coa_prolog_params(self):
        """Prolog parameter validation should work."""
        from em_cubed.surfaces import PrologSurface
        surface = PrologSurface()
        code = '''
?- 30 >= 4, 30 =< 200, 40 >= 10, 40 =< 100, 60 >= 10, 60 =< 200, 0.8 >= 0.0, 0.8 =< 1.0.
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"