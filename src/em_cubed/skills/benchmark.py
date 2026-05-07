"""Performance benchmarking suite for skills.

Provides standardized benchmarks for measuring skill execution performance,
resource usage, and quality metrics across different surfaces.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, cast
import time
try:
    import psutil
    _psutil_available = True
except ImportError:
    psutil = None
    _psutil_available = False
from pathlib import Path
import json
import statistics
from datetime import datetime
from collections import defaultdict

import structlog

from .registry import SkillRegistry
from .metadata import SkillMetadata

logger = structlog.get_logger()


@dataclass
class BenchmarkConfig:
    """Configuration for a benchmark run."""
    warmup_iterations: int = 3
    measurement_iterations: int = 10
    timeout: float = 30.0
    memory_limit_mb: float = 512.0
    concurrent_executions: int = 1
    include_surfaces: List[str] = field(default_factory=list)  # Empty = all available

    def to_dict(self) -> Dict[str, Any]:
        return {
            "warmup_iterations": self.warmup_iterations,
            "measurement_iterations": self.measurement_iterations,
            "timeout": self.timeout,
            "memory_limit_mb": self.memory_limit_mb,
            "concurrent_executions": self.concurrent_executions,
            "include_surfaces": self.include_surfaces,
        }


@dataclass
class BenchmarkResult:
    """Results from a single benchmark execution."""
    skill_id: str
    surface: str
    iterations: int
    timestamp: str
    config: Dict[str, Any]
    mean_execution_time: float
    median_execution_time: float
    p95_execution_time: float
    p99_execution_time: float
    min_execution_time: float
    max_execution_time: float
    std_execution_time: float
    peak_memory_mb: float
    avg_memory_mb: float
    success_rate: float
    error_rate: float
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "surface": self.surface,
            "iterations": self.iterations,
            "timing": {
                "mean": self.mean_execution_time,
                "median": self.median_execution_time,
                "p95": self.p95_execution_time,
                "p99": self.p99_execution_time,
                "min": self.min_execution_time,
                "max": self.max_execution_time,
                "std": self.std_execution_time,
            },
            "resources": {
                "peak_memory_mb": self.peak_memory_mb,
                "avg_memory_mb": self.avg_memory_mb,
            },
            "quality": {
                "success_rate": self.success_rate,
                "error_rate": self.error_rate,
                "errors": self.errors[:10],  # First 10 errors
            },
            "timestamp": self.timestamp,
            "config": self.config,
        }

    @classmethod
    def from_timing_data(cls, skill_id: str, surface: str, times: List[float],
                         memory_samples: List[float], errors: List[str], config: BenchmarkConfig) -> "BenchmarkResult":
        """Construct result from raw timing data."""
        iterations = len(times)
        timestamp = datetime.utcnow().isoformat()

        if times:
            sorted_times = sorted(times)
            p95_idx = int(0.95 * len(times)) - 1
            p99_idx = int(0.99 * len(times)) - 1
            p95 = sorted_times[min(p95_idx, len(times)-1)]
            p99 = sorted_times[min(p99_idx, len(times)-1)]

            result = cls(
                skill_id=skill_id,
                surface=surface,
                iterations=iterations,
                mean_execution_time=statistics.mean(times),
                median_execution_time=statistics.median(times),
                p95_execution_time=p95,
                p99_execution_time=p99,
                min_execution_time=min(times),
                max_execution_time=max(times),
                std_execution_time=statistics.stdev(times) if len(times) > 1 else 0.0,
                peak_memory_mb=max(memory_samples) if memory_samples else 0.0,
                avg_memory_mb=statistics.mean(memory_samples) if memory_samples else 0.0,
                success_rate=1.0 - (len(errors) / iterations if iterations > 0 else 0.0),
                error_rate=len(errors) / iterations if iterations > 0 else 0.0,
                errors=errors[:10],
                timestamp=timestamp,
                config=config.to_dict(),
            )
        else:
            result = cls(
                skill_id=skill_id, surface=surface, iterations=0,
                mean_execution_time=0.0, median_execution_time=0.0,
                p95_execution_time=0.0, p99_execution_time=0.0,
                min_execution_time=0.0, max_execution_time=0.0,
                std_execution_time=0.0, peak_memory_mb=0.0,
                avg_memory_mb=0.0, success_rate=0.0, error_rate=1.0,
                errors=["No successful executions"], timestamp=timestamp,
                config=config.to_dict(),
            )

        return result


class SkillBenchmark:
    """Run and record performance benchmarks for skills."""

    def __init__(self, plugin_manager, skill_registry: SkillRegistry, skills_dir: Optional[Path] = None):
        self.plugin_manager = plugin_manager
        self.registry = skill_registry
        self.skills_dir = skills_dir
        self.logger = logger.bind(component="skill_benchmark")
        self._benchmark_data: Dict[str, List[BenchmarkResult]] = defaultdict(list)

    async def benchmark_skill(self, skill_id: str, config: Optional[BenchmarkConfig] = None,
                              test_input: Optional[Dict[str, Any]] = None) -> BenchmarkResult:
        """Benchmark a single skill across its surfaces."""
        config = config or BenchmarkConfig()
        skill = self.registry.get_skill(skill_id)
        if not skill:
            raise ValueError(f"Skill '{skill_id}' not found")

        self.logger.info("Starting benchmark", skill_id=skill_id, config=config.to_dict())

        # Determine which surfaces to benchmark
        surfaces_to_test = config.include_surfaces if config.include_surfaces else skill.surfaces
        if not surfaces_to_test:
            self.logger.warning("No surfaces to benchmark", skill_id=skill_id)
            surfaces_to_test = ["python"]  # Fallback

        # Benchmark each surface
        all_results = []
        for surface in surfaces_to_test:
            plugin = self.plugin_manager.get(surface)
            if not plugin or not plugin.available:
                self.logger.warning("Surface not available, skipping", surface=surface, skill=skill_id)
                continue

            result = await self._benchmark_surface(skill, plugin, config, test_input)
            all_results.append(result)
            self._benchmark_data[f"{skill_id}/{surface}"].append(result)

        # Return the first (or best) result
        if all_results:
            best = max(all_results, key=lambda r: r.success_rate * (1.0 / max(r.mean_execution_time, 0.001)))
            return best
        else:
            return BenchmarkResult(
                skill_id=skill_id, surface="none", iterations=0,
                mean_execution_time=0.0, median_execution_time=0.0,
                p95_execution_time=0.0, p99_execution_time=0.0,
                min_execution_time=0.0, max_execution_time=0.0,
                std_execution_time=0.0, peak_memory_mb=0.0, avg_memory_mb=0.0,
                success_rate=0.0, error_rate=1.0, errors=["No surfaces available"],
                timestamp=datetime.utcnow().isoformat(), config=config.to_dict(),
            )

    async def _benchmark_surface(self, skill: SkillMetadata, plugin, config: BenchmarkConfig,
                                 test_input: Optional[Dict[str, Any]]) -> BenchmarkResult:
        """Benchmark a skill on a specific surface."""
        assert skill.skill_id is not None, "Skill must have a valid ID"
        # Prepare test input
        if test_input is None:
            test_input = self._generate_test_input(skill)

        # Warmup
        for _ in range(config.warmup_iterations):
            try:
                await self._execute_skill_once(skill, plugin, test_input)
            except Exception:
                pass

        # Measurement phase
        times = []
        memory_samples: List[float] = [] if _psutil_available else []
        errors = []

        process = psutil.Process() if _psutil_available else None
        # Ensure process is not None when psutil is available
        if _psutil_available:
            assert process is not None, "psutil.Process() should not be None"
        for i in range(config.measurement_iterations):
            mem_before = None
            if _psutil_available:
                assert process is not None, "Process should be available when psutil is available"
                mem_before = process.memory_info().rss / 1024 / 1024  # MB
            start = time.perf_counter()
            try:
                result = await self._execute_skill_once(skill, plugin, test_input)
                elapsed = time.perf_counter() - start
                if _psutil_available and mem_before is not None:
                    assert process is not None, "Process should be available"
                    mem_after = process.memory_info().rss / 1024 / 1024
                    memory_samples.append(mem_after - mem_before)
                times.append(elapsed)
                if result.get("status") != "ok":
                    errors.append(result.get("message", "Unknown error"))
            except Exception as e:
                elapsed = time.perf_counter() - start
                times.append(elapsed)
                errors.append(str(e))
                if _psutil_available and mem_before is not None:
                    assert process is not None, "Process should be available"
                    mem_after = process.memory_info().rss / 1024 / 1024
                    memory_samples.append(mem_after - mem_before)

        return BenchmarkResult.from_timing_data(
            skill_id=skill.skill_id,
            surface=plugin.name,
            times=times,
            memory_samples=memory_samples,
            errors=errors,
            config=config,
        )

    async def _execute_skill_once(self, skill: SkillMetadata, plugin, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a skill once using the actual surface plugin."""
        import re

        skill_path = None
        if skill.path:
            skill_path = Path(skill.path)
        elif self.skills_dir:
            skill_path = self.skills_dir / skill.domain / skill.name / "SKILL.md"

        if not skill_path or not skill_path.exists():
            return {"status": "error", "message": f"Skill file not found for {skill.skill_id}"}

        content = skill_path.read_text(encoding="utf-8")

        code_blocks: Dict[str, str] = {}
        for match in re.finditer(r"```(\w+)\s*\r?\n(.*?)```", content, re.DOTALL):
            lang = match.group(1).lower()
            code = match.group(2).strip()
            code_blocks[lang] = code

        code = code_blocks.get(plugin.name, "")
        if not code:
            return {"status": "error", "message": f"No {plugin.name} code block found in {skill.skill_id}"}

        context = {"input": input_data}
        try:
            result = await plugin.execute(code, context)
            return cast(Dict[str, Any], result)
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _generate_test_input(self, skill: SkillMetadata) -> Dict[str, Any]:
        """Generate a valid test input based on skill's input schema."""
        if skill.input_schema.properties:
            # Generate from schema properties
            input_data: Dict[str, Any] = {}
            for prop_name, prop_def in skill.input_schema.properties.items():
                if prop_def.get("type") == "string":
                    input_data[prop_name] = "test_value"
                elif prop_def.get("type") == "number":
                    input_data[prop_name] = 42.0
                elif prop_def.get("type") == "integer":
                    input_data[prop_name] = 42
                elif prop_def.get("type") == "boolean":
                    input_data[prop_name] = True
                elif prop_def.get("type") == "array":
                    input_data[prop_name] = []
                else:
                    input_data[prop_name] = {}
            return input_data
        return {"input": "test"}

    def get_benchmark_history(self, skill_id: str, surface: Optional[str] = None) -> List[BenchmarkResult]:
        """Get historical benchmark results."""
        if surface:
            return self._benchmark_data.get(f"{skill_id}/{surface}", [])
        # Aggregate across surfaces
        results = []
        for k, v in self._benchmark_data.items():
            if k.startswith(f"{skill_id}/"):
                results.extend(v)
        return results

    def get_performance_report(self, skill_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate a performance comparison report."""
        skills_to_report = skill_ids or list(self._skills.keys()) if hasattr(self, '_skills') else []

        report: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "skills": {},
        }

        for skill_id in skills_to_report:
            history = self.get_benchmark_history(skill_id)
            if history:
                latest = history[-1]
                report["skills"][skill_id] = {
                    "surface": latest.surface,
                    "mean_time": latest.mean_execution_time,
                    "success_rate": latest.success_rate,
                    "memory_mb": latest.avg_memory_mb,
                    "timestamp": latest.timestamp,
                }

        return report

    def export_benchmarks(self, output_path: Path) -> None:
        """Export all benchmark data to JSON."""
        data = {}
        for key, results in self._benchmark_data.items():
            data[key] = [r.to_dict() for r in results]

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        self.logger.info("Exported benchmarks", path=str(output_path))
