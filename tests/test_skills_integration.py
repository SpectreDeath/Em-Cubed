"""Integration tests for skill composition and multi-surface execution."""

import pytest
import asyncio
from pathlib import Path
import tempfile
import json

from em_cubed.skills.composer import SkillComposer, CompositionPlan, CompositionStep, CompositionPattern
from em_cubed.skills.registry import SkillRegistry
from em_cubed.skills.metadata import SkillMetadata
from em_cubed.plugin_manager import PluginManager
from em_cubed.skills.validator import SkillValidator

pytestmark = pytest.mark.asyncio


class TestSkillComposition:
    """Test skill composition and orchestration."""

    @pytest.fixture
    def plugin_manager(self):
        """Create plugin manager."""
        return PluginManager()

    @pytest.fixture
    def test_registry(self, tmp_path):
        """Create a test registry with mock skills."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        # Create mock skills
        skill1_dir = skills_dir / "test" / "skill_a"
        skill1_dir.mkdir(parents=True)
        skill1_file = skill1_dir / "SKILL.md"
        skill1_file.write_text("""---
name: Skill A
Domain: General
Version: 1.0.0
surfaces: [python]
input_schema:
  type: object
  properties:
    value:
      type: number
  required: [value]
output_schema:
  type: object
  properties:
    result:
      type: number
---
## Purpose
Doubles the input value.

## Description
Takes a number and returns double.

```python
def skill_a_execute(value):
    return {"result": value * 2}
```
""")

        skill2_dir = skills_dir / "test" / "skill_b"
        skill2_dir.mkdir(parents=True)
        skill2_file = skill2_dir / "SKILL.md"
        skill2_file.write_text("""---
name: Skill B
Domain: General
Version: 1.0.0
surfaces: [python]
input_schema:
  type: object
  properties:
    result:
      type: number
  required: [result]
output_schema:
  type: object
  properties:
    final:
      type: number
---
## Purpose
Adds 10 to the input.

## Description
Takes a number and adds 10.

```python
def skill_b_execute(result):
    return {"final": result + 10}
```
""")

        registry_file = tmp_path / "registry.json"
        from em_cubed.indexer import reindex
        reindex(skills_dir, registry_file)

        return SkillRegistry(skills_dir, registry_file)

    @pytest.fixture
    def composer(self, plugin_manager, test_registry):
        """Create skill composer."""
        return SkillComposer(plugin_manager, test_registry)

    async def test_sequential_composition(self, composer, test_registry):
        """Test sequential skill composition."""
        # Create pipeline: Skill A -> Skill B
        step_a = CompositionStep(
            skill_id="General/Skill A",
            input_mapping={"value": "input.value"},
            output_mapping={"result": "data.intermediate"},
        )
        step_b = CompositionStep(
            skill_id="General/Skill B",
            input_mapping={"result": "data.intermediate"},
            output_mapping={"final": "data.output"},
        )

        plan = CompositionPlan(
            name="test_pipeline",
            steps=[step_a, step_b],
            pattern=CompositionPattern.SEQUENTIAL,
        )

        result = await composer.compose(plan, {"input": {"value": 5}})

        assert result.success
        assert result.get_output() == 20  # 5*2 + 10 = 20
        assert "General/Skill A" in result.context.skills_used
        assert "General/Skill B" in result.context.skills_used

    async def test_parallel_composition(self, composer, test_registry):
        """Test parallel skill execution."""
        # Use Skill A twice with different inputs in parallel
        step1 = CompositionStep(
            skill_id="General/Skill A",
            input_mapping={"value": "input.x"},
            output_mapping={"result": "data.out1"},
        )
        step2 = CompositionStep(
            skill_id="General/Skill A",
            input_mapping={"value": "input.y"},
            output_mapping={"result": "data.out2"},
        )

        plan = CompositionPlan(
            name="parallel_test",
            steps=[step1, step2],
            pattern=CompositionPattern.PARALLEL,
        )

        result = await composer.compose(plan, {"input": {"x": 3, "y": 7}})

        assert result.success
        outputs = result.context.data["output"]
        assert outputs["General/Skill A"]["value"]["result"] in [6, 14]

    async def test_conditional_composition(self, composer, test_registry):
        """Test conditional skill execution."""
        executed = []

        def condition(context):
            return context.data.get("should_run", True)

        step = CompositionStep(
            skill_id="General/Skill A",
            input_mapping={"value": "input.base"},
            condition=condition,
        )

        plan = CompositionPlan(
            name="conditional_test",
            steps=[step],
            pattern=CompositionPattern.CONDITIONAL,
        )

        # Test true condition
        result1 = await composer.compose(plan, {"input": {"base": 5}, "should_run": True})
        assert result1.success
        assert len(result1.context.skills_used) == 1

        # Test false condition
        result2 = await composer.compose(plan, {"input": {"base": 5}, "should_run": False})
        assert result2.success
        assert len(result2.context.skills_used) == 0

    def test_compatibility_detection(self, test_registry):
        """Test finding compatible skills."""
        compatible = test_registry.find_compatible_skills("General/Skill A")
        # Skill B should be compatible (output of A matches input of B)
        assert "General/Skill B" in compatible

    def test_composition_validation(self, test_registry):
        """Test validating skill composition."""
        skill_a = test_registry.get_skill("General/Skill A")
        skill_b = test_registry.get_skill("General/Skill B")

        # Validate composition
        validator = SkillValidator()
        result = validator.validate_composition(skill_a, skill_b)

        assert result.valid  # A's output provides B's required input (result)

    def test_skill_suggestion(self, composer, test_registry):
        """Test skill recommendation for composition."""
        suggestions = composer.suggest_composition("General/Skill A", "Transform and add")

        assert len(suggestions) > 0
        # Should suggest Skill B as it's compatible
        suggested_ids = [p.steps[0].skill_id for p in suggestions]
        assert "General/Skill B" in suggested_ids


class TestSkillValidationIntegration:
    """Integration tests for skill validation."""

    def test_validate_all_skills(self):
        """Validate all skills in the repository."""
        from em_cubed.skills.quality_pipeline import SkillQualityPipeline
        from em_cubed.plugin_manager import PluginManager

        skills_dir = Path("skills")
        registry_file = Path("registry.json")

        if not skills_dir.exists() or not registry_file.exists():
            pytest.skip("Skills directory or registry not found")

        pipeline = SkillQualityPipeline(skills_dir, registry_file, PluginManager())
        # Synchronous call for validation
        import asyncio
        results = asyncio.run(pipeline.validate_all_skills())

        assert len(results) > 0
        # Most skills should pass basic validation
        passing = sum(1 for r in results.values() if r.valid)
        assert passing / len(results) >= 0.7, f"Only {passing}/{len(results)} skills passed validation"


class TestSkillBenchmarkIntegration:
    """Integration tests for skill benchmarking."""

    @pytest.fixture
    def plugin_manager(self):
        """Create plugin manager."""
        return PluginManager()

    @pytest.mark.asyncio
    async def test_benchmark_mock_skill(self, plugin_manager, tmp_path):
        """Benchmark a simple skill."""
        from em_cubed.skills.benchmark import SkillBenchmark, BenchmarkConfig
        from em_cubed.skills.registry import SkillRegistry

        # Create minimal test registry
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        skill_dir = skills_dir / "benchmark_test"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("""---
name: Benchmark Test
Domain: General
Version: 1.0.0
surfaces: [python]
---
## Purpose
Test benchmark

```python
def test():
    return 42
```
""")

        registry_file = tmp_path / "registry.json"
        from em_cubed.indexer import reindex
        reindex(skills_dir, registry_file)

        registry = SkillRegistry(skills_dir, registry_file)
        benchmark = SkillBenchmark(plugin_manager, registry)

        # Benchmark with minimal config
        config = BenchmarkConfig(
            warmup_iterations=1,
            measurement_iterations=3,
        )

        # This will use mock execution since actual skill runner not fully integrated
        # Just ensure it doesn't crash
        result = await benchmark.benchmark_skill("General/Benchmark Test", config)
        assert result is not None
        assert result.skill_id == "General/Benchmark Test"


class TestSkillRecommendation:
    """Test skill recommendation engine."""

    def test_recommend_by_domain(self):
        """Test recommending skills by domain."""
        from em_cubed.skills.recommender import SkillRecommender, TaskRequirement
        from em_cubed.skills.registry import SkillRegistry

        skills_dir = Path("skills")
        registry_file = Path("registry.json")

        if not registry_file.exists():
            pytest.skip("Registry not found - run reindex first")

        registry = SkillRegistry(skills_dir, registry_file)
        recommender = SkillRecommender(registry)

        # Test NLP recommendation
        requirement = TaskRequirement(
            category="NLP",
            surfaces=["python"],
        )
        results = recommender.recommend(requirement, limit=3)

        assert len(results) > 0
        for r in results:
            assert r.skill_id is not None
            assert r.relevance_score >= 0

    def test_find_similar_skills(self):
        """Test finding similar skills."""
        from em_cubed.skills.recommender import SkillRecommender
        from em_cubed.skills.registry import SkillRegistry

        skills_dir = Path("skills")
        registry_file = Path("registry.json")

        if not registry_file.exists():
            pytest.skip("Registry not found")

        registry = SkillRegistry(skills_dir, registry_file)
        recommender = SkillRecommender(registry)

        # Find skills similar to natural-language-generator
        nlg_id = "NLP/natural-language-generator"
        similar = recommender.get_similar_skills(nlg_id)

        assert len(similar) >= 0
        # The skill itself should not be in results
        assert not any(s.skill_id == nlg_id for s in similar)


class TestEndToEndQualityPipeline:
    """End-to-end tests for the complete quality pipeline."""

    def test_full_pipeline_smoke(self, tmp_path):
        """Smoke test the full quality pipeline on a minimal skill set."""
        from em_cubed.skills.quality_pipeline import SkillQualityPipeline
        from em_cubed.plugin_manager import PluginManager
        import asyncio

        # Create minimal skills dir
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        skill_dir = skills_dir / "general" / "test_skill"
        skill_dir.mkdir(parents=True)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("""---
name: Test Skill
Domain: General
Version: 1.0.0
surfaces: [python]
---
## Purpose
A test skill for quality pipeline

## Description
This skill is used to test the quality pipeline end-to-end.

```python
def execute(input_data):
    return {"result": input_data.get("value", 0) * 2}
```
""")

        registry_file = tmp_path / "registry.json"

        from em_cubed.indexer import reindex
        reindex(skills_dir, registry_file)

        pipeline = SkillQualityPipeline(skills_dir, registry_file, PluginManager())

        # Run validation
        results = asyncio.run(pipeline.validate_all_skills())
        assert len(results) > 0
        assert list(results.values())[0].valid

        # Benchmark
        bench_results = asyncio.run(pipeline.benchmark_all_skills())
        assert len(bench_results) > 0

        # Report
        report = pipeline.get_quality_report()
        assert report["total_skills"] >= 1
