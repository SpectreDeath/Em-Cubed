# Skills Quality Framework Guide

## Overview

The Skills Quality Framework provides comprehensive tooling for skill development, validation, testing, and composition in Em-Cubed.

## Architecture

The framework consists of these core modules:

- **metadata.py**: Extended skill metadata with schemas, dependencies, quality thresholds
- **validator.py**: Multi-dimensional skill validation (structure, content, code quality)
- **registry.py**: Enhanced skill registry with quality metrics and composition graph
- **composer.py**: Skill composition and orchestration (sequential, parallel, conditional)
- **benchmark.py**: Performance benchmarking suite
- **recommender.py**: Intelligent skill recommendation engine
- **telemetry.py**: Runtime execution telemetry and usage tracking
- **testing.py**: Automated test generation and execution
- **quality_pipeline.py**: End-to-end quality assurance pipeline
- **executor.py**: Runtime skill execution loader/invoker

## Usage

### CLI Commands

```bash
# Index skills into registry
em3 index skills/ -o registry.json

# Validate all skills (structure, quality)
em3 validate --skills-dir skills/

# Run full quality pipeline
em3 quality --benchmark

# Run tests for a specific skill
em3 test NLP/natural-language-generator

# Get skill recommendations
em3 recommend "need sentiment analysis on text"

# Compose skills
em3 compose --source NLP/preprocessor --target NLP/analyzer --output plan.json
```

### Python API

```python
from pathlib import Path
from em_cubed.skills import (
    SkillRegistry, SkillValidator, SkillComposer,
    SkillRecommender, SkillBenchmark, SkillQualityPipeline,
    initialize_telemetry
)
from em_cubed.plugin_manager import PluginManager

# Initialize
skills_dir = Path("skills")
registry_file = Path("registry.json")
plugin_manager = PluginManager()
registry = SkillRegistry(skills_dir, registry_file)

# Validate a skill
validator = SkillValidator()
metadata = registry.get_skill("NLP/sentiment-intelligence-engine")
result = validator.validate_skill_file(
    skills_dir / "NLP" / "sentiment-intelligence-engine" / "SKILL.md",
    metadata
)
print(f"Quality score: {result.quality_score:.2%}")
for issue in result.issues:
    print(f"  {issue.code}: {issue.message}")

# Compose skills
composer = SkillComposer(plugin_manager, registry)
from em_cubed.skills.composer import CompositionStep, CompositionPattern

plan = composer.create_pipeline([
    CompositionStep(
        skill_id="NLP/text-preprocessor",
        input_mapping={"text": "input.text"},
        output_mapping={"tokens": "context.tokens"}
    ),
    CompositionStep(
        skill_id="NLP/sentiment-intelligence-engine",
        input_mapping={"tokens": "context.tokens"},
        output_mapping={"sentiment": "output.score"}
    ),
])

import asyncio
result = asyncio.run(composer.compose(plan, {"input": {"text": "Hello world"}}))
print(f"Result: {result.get_output()}")
```

## Skill Metadata Schema

Skills are defined in `SKILL.md` files with YAML frontmatter and code blocks:

```yaml
---
name: My Skill
Domain: NLP
Version: 1.0.0
surfaces:
  - python
  - prolog
  - hy
dependencies:
  - skill_id: "NLP/tokenizer"
    version_range: ">=1.0.0"
input_schema:
  type: object
  properties:
    text:
      type: string
  required: ["text"]
output_schema:
  type: object
  properties:
    sentiment:
      type: number
capabilities:
  surfaces: ["python"]
  permissions: ["network"]  # optional
  resources:
    memory_mb: 256
compatibility:
  min_version: "0.5.0"
quality_thresholds:
  min_test_coverage: 0.8
  min_success_rate: 0.7
---
```

## Quality Standards

Skills must meet minimum quality thresholds:

| Metric | Threshold | Description |
|--------|-----------|-------------|
| Surface Count | ≥1 | Must implement at least 1 surface |
| Purpose Length | ≥10 chars | Descriptive purpose statement |
| Description Length | ≥20 chars | Detailed description |
| Test Coverage | ≥80% | Code coverage target |
| Success Rate | ≥70% | Runtime execution success |
| Max Execution Time | ≤30s | Timeout protection |

Validation scores range 0-1:
- **0.7+**: High quality (passing)
- **0.3-0.69**: Needs improvement (passes but with warnings)
- **<0.3**: Failing (does not meet minimum standards)

## Testing

### Auto-Generated Tests

The framework generates test files for all skills:

```bash
# Generate test scaffolding
python tests/generate_skill_tests.py

# This creates tests/skills/test_<domain>_<skill-name>.py
```

Each generated test includes:
- Metadata validation
- Surface availability checks
- Basic execution test (mocked)
- Schema validation

### Writing Custom Tests

Add test blocks in your SKILL.md:

````markdown
## Testing

```python
def test_my_skill():
    result = my_skill.execute({"input": "test"})
    assert result["status"] == "ok"
    assert "output" in result
```
````

### Running Tests

```bash
# All skills
em3 test

# Specific skill
em3 test NLP/text-generator --generate

# With pytest directly
pytest tests/skills/ -v
```

## Skill Composition

Skills can be chained together in various patterns:

### Sequential Pipeline

```python
plan = composer.create_pipeline([
    CompositionStep("SkillA", {"in": "input"}, {"mid": "data"}),
    CompositionStep("SkillB", {"mid": "data"}, {"out": "output"}),
])
```

### Parallel Execution

```python
plan = composer.create_parallel([
    CompositionStep("SkillA", ...),
    CompositionStep("SkillB", ...),
])
```

### Conditional

```python
def condition(ctx):
    return ctx.data.get("should_run", True)

step = CompositionStep("SkillA", condition=condition)
```

## Telemetry

Automatic usage tracking is enabled. Metrics recorded:

- Execution counts (success/failure)
- Execution time (mean, p95, p99)
- Token usage estimation
- Error classification
- Performance history (rolling windows)

Access telemetry:

```python
from em_cubed.skills import get_telemetry_collector

collector = get_telemetry_collector()
metrics = collector.get_skill_metrics("NLP/generator", window_seconds=3600)
print(f"Success rate: {metrics['success_rate']:.1%}")
```

## Benchmarking

```python
from em_cubed.skills import SkillBenchmark, BenchmarkConfig

benchmark = SkillBenchmark(plugin_manager, registry)

# Run benchmarks
config = BenchmarkConfig(
    warmup_iterations=3,
    measurement_iterations=20,
)
result = await benchmark.benchmark_skill("NLP/generator", config)

print(f"Mean time: {result.mean_execution_time:.3f}s")
print(f"P95: {result.p95_execution_time:.3f}s")
print(f"Memory: {result.avg_memory_mb:.1f} MB")
```

## Recommendations

The recommendation engine suggests skills based on task requirements:

```python
from em_cubed.skills import SkillRecommender, TaskRequirement

recommender = SkillRecommender(registry)
requirements = TaskRequirement(
    category="NLP",
    surfaces=["python"],
    capabilities=["text-generation"],
    complexity="medium",
    min_success_rate=0.8,
)

suggestions = recommender.recommend(requirements, limit=5)
for s in suggestions:
    print(f"{s.name} - relevance: {s.relevance_score:.2%}")
```

## Extending the Framework

### Custom Validator

```python
class MyValidator(SkillValidator):
    def _validate_content(self, result, metadata):
        # Custom checks
        pass
```

### Custom Recommender

```python
class MyRecommender(SkillRecommender):
    def _score_skill(self, skill, requirement):
        # Custom scoring logic
        return score, criteria
```

### Custom Composer

```python
class MyComposer(SkillComposer):
    async def _execute_step(self, step, context):
        # Custom execution logic
        pass
```

## Contributing

When adding new skills:

1. Create `skills/<DOMAIN>/<skill-name>/SKILL.md`
2. Implement Python, Prolog, Hy surfaces (at least 1 required)
3. Add input/output schemas
4. Write tests in Testing section
5. Run `em3 validate` to check quality
6. Run `em3 quality` for full pipeline
7. Submit PR with updated skill files

See `CONTRIBUTING.md` for full guidelines.
