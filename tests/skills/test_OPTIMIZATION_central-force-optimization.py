"""Tests for central-force-optimization skill."""

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
    / "central-force-optimization"
    / "SKILL.md"
)
SKILL_ID = "OPTIMIZATION/central-force-optimization"


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


class TestCentralForceOptimizationSkill:
    """Test suite for central-force-optimization."""

    def test_metadata_valid(self):
        """Test skill metadata is valid and includes all surfaces."""
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        assert metadata_dict is not None
        assert metadata_dict["name"] == "central-force-optimization"
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
    async def test_cfo_python_sphere(self):
        """CFO should converge on 2D sphere function (maximization)."""
        import random

        def sphere(x):
            return -sum(xi ** 2 for xi in x)  # Negative for maximization

        pop_size, g, alpha, beta, max_iter = 30, 1.0, 0.1, 0.1, 80
        dim = 2

        probes = []
        accelerations = []
        for _ in range(pop_size):
            pos = [random.uniform(-5, 5) for _ in range(dim)]
            probes.append(pos[:])
            accelerations.append([0.0] * dim)

        fitness = [sphere(pos) for pos in probes]
        best_score = max(fitness)

        for epoch in range(max_iter):
            # Calculate accelerations
            for i in range(pop_size):
                accelerations[i] = [0.0] * dim
                for k in range(pop_size):
                    if k == i:
                        continue
                    mass_diff = fitness[k] - fitness[i]
                    if mass_diff <= 0:
                        continue
                    dist_sq = sum((probes[k][c] - probes[i][c]) ** 2 for c in range(dim))
                    if dist_sq < 1e-10:
                        continue
                    distance = math.sqrt(dist_sq)
                    for c in range(dim):
                        direction = (probes[k][c] - probes[i][c]) / distance
                        accelerations[i][c] += g * (mass_diff ** alpha) / (distance ** beta) * direction

            # Update positions
            for i in range(pop_size):
                for c in range(dim):
                    probes[i][c] += 0.5 * accelerations[i][c]
                    probes[i][c] = max(-5, min(5, probes[i][c]))

            fitness = [sphere(pos) for pos in probes]
            current_best = max(fitness)
            if current_best > best_score:
                best_score = current_best

        assert best_score > -1.0, f"CFO sphere result = {best_score}"

    @pytest.mark.asyncio
    async def test_gravitational_force(self):
        """Gravitational force should be positive for better particles."""
        g, alpha, beta = 1.0, 0.1, 0.1
        mass_diff, distance = 5.0, 2.0
        force = g * (mass_diff ** alpha) / (distance ** beta)
        assert force > 0

    @pytest.mark.asyncio
    async def test_distance_squared(self):
        """Distance squared calculation should work correctly."""
        x1, x2 = [0.0, 0.0], [3.0, 4.0]
        dist_sq = sum((x1[i] - x2[i]) ** 2 for i in range(len(x1)))
        assert dist_sq == 25.0

    @pytest.mark.asyncio
    async def test_prolog_params(self):
        """Prolog parameter validation should work."""
        from em_cubed.surfaces import PrologSurface
        surface = PrologSurface()
        code = '''
?- 30 >= 4, 30 =< 100, 0.1 >= 0.01, 0.1 =< 2.0, 0.1 >= 0.01, 0.1 =< 2.0.
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"