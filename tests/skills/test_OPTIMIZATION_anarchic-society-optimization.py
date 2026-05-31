"""Tests for anarchic-society-optimization skill."""

import pytest
from pathlib import Path
from em_cubed.skills.testing import SkillTestGenerator, SkillTestRunner
from em_cubed.indexer import get_skill_metadata
from em_cubed.plugin_manager import PluginManager

SKILL_FILE = Path(
    Path(__file__).parent.parent.parent
    / "skills"
    / "OPTIMIZATION"
    / "anarchic-society-optimization"
    / "SKILL.md"
)
SKILL_ID = "OPTIMIZATION/anarchic-society-optimization"


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


class TestASOOptimizerSkill:
    """Test suite for anarchic-society-optimization."""

    def test_metadata_valid(self):
        """Test skill metadata is valid and includes all four surfaces."""
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        assert metadata_dict is not None
        assert metadata_dict["name"] == "anarchic-society-optimization"
        assert metadata_dict["domain"] == "OPTIMIZATION"
        surfaces = metadata_dict.get("surfaces", [])
        assert len(surfaces) >= 1
        # All four multi-surface implementations must be declared
        for expected in ("python", "prolog", "hy", "z3"):
            assert expected in surfaces, f"Surface '{expected}' missing from skill metadata"

    def test_skill_file_exists(self):
        """SKILL.md must be present on disk."""
        assert SKILL_FILE.exists(), f"SKILL.md not found at {SKILL_FILE}"

    def test_cangjie_file_exists(self):
        """SKILL_CANGJIE.md must be present alongside SKILL.md."""
        cangjie = SKILL_FILE.parent / "SKILL_CANGJIE.md"
        assert cangjie.exists(), f"SKILL_CANGJIE.md not found at {cangjie}"

    def test_surfaces_implemented(self, plugin_manager):
        """At least one declared surface must be available in the plugin manager."""
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
    async def test_aso_python_sphere(self):
        """ASO Python core: converges near optimum on negated 2D sphere."""
        import math
        import random

        # Inline ASOOptimizer to avoid import dependency on surface
        class ASOAgent:
            def __init__(self, dim):
                self.position = [0.0] * dim
                self.prev_position = [0.0] * dim
                self.p_best = [0.0] * dim
                self.p_best_fitness = float('-inf')
                self.fitness = float('-inf')

        def clip(val, lo, hi, step):
            val = max(lo, min(hi, val))
            if step > 0.0:
                val = lo + step * round((val - lo) / step)
            return val

        def neg_sphere(x):
            return -sum(xi ** 2 for xi in x)

        dim = 2
        bounds = [(-5.0, 5.0, 0.0)] * dim
        pop_size = 30
        omega, lambda1, lambda2 = 0.7, 1.5, 1.5
        anarchy_prob = 0.1
        alpha, theta, delta = 0.5, 0.1, 0.1
        max_iter = 150

        agents = [ASOAgent(dim) for _ in range(pop_size)]
        g_best = [0.0] * dim
        g_best_f = float('-inf')

        for agent in agents:
            agent.position = [clip(random.uniform(b[0], b[1]), b[0], b[1], b[2]) for b in bounds]
            agent.prev_position = agent.position[:]
            agent.p_best = agent.position[:]
            agent.fitness = neg_sphere(agent.position)
            agent.p_best_fitness = agent.fitness
            if agent.fitness > g_best_f:
                g_best_f = agent.fitness
                g_best = agent.position[:]

        for _ in range(max_iter):
            for agent in agents:
                fi_denom = g_best_f - agent.fitness
                fi = 0.0 if abs(fi_denom) < 1e-300 else (
                    1.0 - alpha * (agent.p_best_fitness - agent.fitness) / fi_denom
                )
                ei_denom = abs(g_best_f) * theta
                if abs(ei_denom) < 1e-300:
                    ei = 0.0
                else:
                    exp_arg = min((g_best_f - agent.fitness) / ei_denom, 700.0)
                    ei = 1.0 - math.exp(-exp_arg)
                ii_denom = abs(agent.p_best_fitness) * delta
                if abs(ii_denom) < 1e-300:
                    ii = 0.0
                else:
                    exp_arg = min((agent.p_best_fitness - agent.fitness) / ii_denom, 700.0)
                    ii = 1.0 - math.exp(-exp_arg)

                new_pos = []
                for c in range(dim):
                    agent.prev_position[c] = agent.position[c]
                    if random.random() < anarchy_prob:
                        nc = random.uniform(bounds[c][0], bounds[c][1])
                    else:
                        rnd = random.random()
                        if rnd > fi:
                            r1, r2 = random.random(), random.random()
                            vel = (omega * (agent.position[c] - agent.p_best[c])
                                   + lambda1 * r1 * (agent.p_best[c] - agent.position[c])
                                   + lambda2 * r2 * (g_best[c] - agent.position[c]))
                            nc = agent.position[c] + vel
                        elif rnd < ei:
                            other = random.randint(0, pop_size - 1)
                            nc = g_best[c] if random.random() < 0.5 else agents[other].p_best[c]
                        elif rnd < ii:
                            nc = agent.p_best[c] if random.random() < 0.5 else agent.prev_position[c]
                        else:
                            nc = agent.position[c]
                    new_pos.append(clip(nc, bounds[c][0], bounds[c][1], bounds[c][2]))

                agent.position = new_pos
                agent.fitness = neg_sphere(agent.position)
                if agent.fitness > agent.p_best_fitness:
                    agent.p_best_fitness = agent.fitness
                    agent.p_best = agent.position[:]
                if agent.fitness > g_best_f:
                    g_best_f = agent.fitness
                    g_best = agent.position[:]

        # Fitness = -||x||^2; near optimum should be > -1.0
        assert g_best_f > -1.0, f"ASO 2D sphere: best_fitness={g_best_f}"

    def test_aso_index_calculations(self):
        """FI, EI, II index values should be finite floats."""
        import math

        alpha, theta, delta = 0.5, 0.1, 0.1
        curr, pbest, gbest = -5.0, -3.0, -1.0

        fi_denom = gbest - curr
        fi = 0.0 if abs(fi_denom) < 1e-300 else (
            1.0 - alpha * (pbest - curr) / fi_denom
        )
        ei_denom = gbest * theta
        ei = 0.0 if abs(ei_denom) < 1e-300 else (
            1.0 - math.exp(-(gbest - curr) / ei_denom)
        )
        ii_denom = pbest * delta
        ii = 0.0 if abs(ii_denom) < 1e-300 else (
            1.0 - math.exp(-(pbest - curr) / ii_denom)
        )

        assert math.isfinite(fi), "FI must be finite"
        assert math.isfinite(ei), "EI must be finite"
        assert math.isfinite(ii), "II must be finite"

    def test_clip_quantization(self):
        """Clip + step quantization must produce values on the step grid."""
        def clip(val, lo, hi, step):
            val = max(lo, min(hi, val))
            if step > 0.0:
                val = lo + step * round((val - lo) / step)
            return val

        result = clip(3.7, 0.0, 10.0, 1.0)
        assert result == 4.0, f"Expected 4.0, got {result}"
        result2 = clip(-7.0, -5.0, 5.0, 0.0)
        assert result2 == -5.0, f"Expected -5.0, got {result2}"

    def test_z3_bounds_inline(self):
        """Z3 should accept in-bounds positions and reject out-of-bounds."""
        try:
            from z3 import Real, Solver, And, sat

            def validate(position, bounds):
                s = Solver()
                vars_ = [Real(f"x{i}") for i in range(len(position))]
                for i, (v, (lo, hi, _)) in enumerate(zip(vars_, bounds)):
                    s.add(And(v >= lo, v <= hi))
                    s.add(v == position[i])
                return s.check() == sat

            bounds = [(-5.0, 5.0, 0.0), (-5.0, 5.0, 0.0)]
            assert validate([1.5, -2.3], bounds) is True
            assert validate([7.0, 0.0], bounds) is False
        except ImportError:
            pytest.skip("z3-solver not installed")
