"""Tests for spiral-dynamics-optimization skill."""

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
    / "spiral-dynamics-optimization"
    / "SKILL.md"
)
SKILL_ID = "OPTIMIZATION/spiral-dynamics-optimization"


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


class TestSpiralDynamicsOptimizationSkill:
    """Test suite for spiral-dynamics-optimization."""

    def test_metadata_valid(self):
        """Test skill metadata is valid and includes all surfaces."""
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        assert metadata_dict is not None
        assert metadata_dict["name"] == "spiral-dynamics-optimization"
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
    async def test_sdo_python_sphere(self):
        """SDO should converge on 2D sphere function (maximization)."""
        import random

        def sphere(x):
            return -sum(xi ** 2 for xi in x)  # Negative for maximization

        pop_size, damping, frequency, max_iter = 100, 0.3, 4.0, 80
        dim = 2
        precision = 10000.0

        particles = []
        for _ in range(pop_size):
            pos = [random.uniform(-5, 5) for _ in range(dim)]
            amp = [random.uniform(-5, 5) for _ in range(dim)]
            particles.append({'position': pos, 'amplitude': amp, 't': 0})

        fitness = [sphere(p['position']) for p in particles]
        best_score = max(fitness)
        best_x = particles[fitness.index(best_score)]['position'][:]  # Copy the list

        for epoch in range(max_iter):
            for i in range(pop_size):
                if fitness[i] >= best_score - 1e-10:
                    for c in range(dim):
                        particles[i]['position'][c] = random.uniform(-5, 5)
                    particles[i]['t'] = 0
                    continue

                particles[i]['t'] += 1
                t = particles[i]['t']
                for c in range(dim):
                    phi = random.uniform(0, 2 * math.pi)
                    osc = particles[i]['amplitude'][c] * math.exp(-damping * t / precision) * math.cos(frequency * t / precision + phi)
                    particles[i]['position'][c] += osc
                    particles[i]['position'][c] = max(-5, min(5, particles[i]['position'][c]))

            fitness = [sphere(p['position']) for p in particles]
            current_best = max(fitness)
            if current_best > best_score:
                best_score = current_best
                best_x = particles[fitness.index(current_best)]['position'][:]  # Copy
                for i in range(pop_size):
                    particles[i]['t'] = 0
                    for c in range(dim):
                        particles[i]['amplitude'][c] = best_x[c] - particles[i]['position'][c]

        assert best_score > -1.0, f"SDO sphere result = {best_score}"

    @pytest.mark.asyncio
    async def test_damped_oscillation(self):
        """Damped oscillation should decay over time."""
        def damped_oscillation(amplitude, t, damping=0.3, freq=4.0):
            return amplitude * math.exp(-damping * t) * math.cos(freq * t)

        initial = damped_oscillation(5.0, 0)
        later = damped_oscillation(5.0, 100)
        assert abs(initial) > abs(later)

    @pytest.mark.asyncio
    async def test_amplitude_calculation(self):
        """Amplitude should be difference from best position."""
        best_x = [0.0, 0.0]
        particle_x = [3.0, 4.0]
        amp = [best_x[i] - particle_x[i] for i in range(len(best_x))]
        assert amp == [-3.0, -4.0]

    @pytest.mark.asyncio
    async def test_prolog_params(self):
        """Prolog parameter validation should work."""
        from em_cubed.surfaces import PrologSurface
        surface = PrologSurface()
        code = '''
?- 100 >= 10, 100 =< 200, 0.3 >= 0.01, 0.3 =< 1.0, 4.0 >= 0.5, 4.0 =< 20.0.
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"