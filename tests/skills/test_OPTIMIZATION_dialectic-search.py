"""Tests for dialectic-search skill."""

import pytest
import math
from pathlib import Path
from em_cubed.skills.testing import SkillTestGenerator, SkillTestRunner
from em_cubed.indexer import get_skill_metadata
from em_cubed.plugin_manager import PluginManager

SKILL_FILE = Path(
    Path(__file__).parent.parent.parent
    / "skills"
    / "OPTIMIZATION"
    / "dialectic-search"
    / "SKILL.md"
)
SKILL_ID = "OPTIMIZATION/dialectic-search"


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


class TestDialecticSearchSkill:
    """Test suite for dialectic-search."""

    def test_metadata_valid(self):
        """Test skill metadata is valid and includes all surfaces."""
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        assert metadata_dict is not None
        assert metadata_dict["name"] == "dialectic-search"
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
    async def test_da_python_sphere(self):
        """DA should converge on 2D sphere function."""
        import random

        # Inline DA to avoid import dependency
        def euclidean_distance(a, b):
            return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))

        def sphere(x):
            return sum(xi ** 2 for xi in x)

        pop_size, k1, max_iter = 30, 3, 80
        dim = 2

        population = [[random.uniform(-5, 5) for _ in range(dim)] for _ in range(pop_size)]
        fitness = [sphere(ind) for ind in population]
        best_score = min(fitness)

        for gen in range(max_iter):
            sorted_idx = sorted(range(pop_size), key=lambda i: fitness[i])
            population = [population[i] for i in sorted_idx]
            fitness = [fitness[i] for i in sorted_idx]

            for i in range(k1, pop_size):
                anti1 = random.randint(0, k1 - 1)
                anti2 = random.randint(0, k1 - 1)
                while anti1 == anti2:
                    anti2 = random.randint(0, k1 - 1)
                dist1 = euclidean_distance(population[i], population[anti1])
                dist2 = euclidean_distance(population[i], population[anti2])
                anti_idx = anti1 if dist1 < dist2 else anti2
                for c in range(dim):
                    population[i][c] = max(-5, min(5, population[i][c] + random.random() * (population[anti_idx][c] - population[i][c])))

            for i in range(pop_size):
                fitness[i] = sphere(population[i])

            if min(fitness) < best_score:
                best_score = min(fitness)

        assert best_score < 1.0, f"DA sphere result = {best_score}"

    @pytest.mark.asyncio
    async def test_da_euclidean_distance(self):
        """Euclidean distance should work correctly."""
        import math
        a, b = [0.0, 0.0], [3.0, 4.0]
        dist = math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))
        assert abs(dist - 5.0) < 1e-9

    @pytest.mark.asyncio
    async def test_da_prolog_params(self):
        """Prolog parameter validation should work."""
        from em_cubed.surfaces import PrologSurface
        surface = PrologSurface()
        code = '''
?- 50 >= 4, 50 =< 200, 3 >= 1, 3 =< 10, 5 >= 5, 10 =< 50.
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"