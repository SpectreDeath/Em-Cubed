"""Skill quality pipeline - integrates validation, testing, and metrics.

This module provides end-to-end quality assurance for skills.
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import structlog

from .metadata import SkillMetadata
from .validator import SkillValidator, ValidationResult
from .registry import SkillRegistry, QualityMetrics
from .testing import SkillTestGenerator, SkillTestRunner, TestCase, TestResult
from .benchmark import SkillBenchmark, BenchmarkConfig

logger = structlog.get_logger()


class SkillQualityPipeline:
    """End-to-end quality pipeline for skills."""

    def __init__(self, skills_dir: Path, registry_file: Path,
                 plugin_manager=None):
        self.skills_dir = skills_dir
        self.registry_file = registry_file
        self.validator = SkillValidator()
        self.registry = SkillRegistry(skills_dir, registry_file)
        self.test_generator = SkillTestGenerator(plugin_manager)
        self.test_runner = SkillTestRunner(plugin_manager, self.registry)
        self.benchmark = SkillBenchmark(plugin_manager, self.registry)
        self.logger = logger.bind(component="quality_pipeline")

    async def validate_all_skills(self) -> Dict[str, ValidationResult]:
        """Validate all skills in the skills directory."""
        results = {}

        for skill_file in self._discover_skill_files():
            try:
                skill_id = self._extract_skill_id(skill_file)
                metadata = self._load_skill_metadata(skill_file)
                if metadata:
                    result = self.validator.validate_skill_file(skill_file, metadata)
                    results[skill_id] = result

                    # Store validation score
                    qm = self.registry.get_quality(skill_id)
                    if qm:
                        qm.validation_score = result.quality_score
                        qm.last_validation = datetime.utcnow()
                        qm.issues = [i.to_dict() for i in result.issues]
            except Exception as e:
                self.logger.error("Validation failed", skill=skill_file.name, error=str(e))

        self.registry._save_registry()
        return results

    async def test_all_skills(self, generate_tests: bool = True) -> Dict[str, Dict[str, Any]]:
        """Run tests for all skills."""
        results = {}
        import traceback

        for skill_id, skill in self.registry._skills.items():
            try:
                # Generate or load tests
                skill_path = None
                if skill.path:
                    skill_path = Path(skill.path)
                    if not skill_path.exists():
                        skill_path = None

                if generate_tests and skill_path and skill_path.exists():
                    tests = self.test_generator.generate_tests_for_skill(skill_path, skill)
                else:
                    # Skip test execution; rely on validation only
                    results[skill_id] = {
                        "total_tests": 0,
                        "passed": 0,
                        "failed": 0,
                        "pass_rate": 0.0,
                        "skipped": True,
                        "reason": "no tests available",
                    }
                    continue

                # Run tests
                summary = await self.test_runner.run_test_suite(tests, skill_id)
                results[skill_id] = summary

                # Update registry with test coverage
                qm = self.registry.get_quality(skill_id)
                if qm:
                    qm.test_coverage = summary["pass_rate"]

            except Exception as e:
                tb = traceback.format_exc()
                self.logger.error("Testing failed", skill=skill_id, error=str(e), traceback=tb)
                results[skill_id] = {"error": str(e), "traceback": tb}

        return results

    async def benchmark_all_skills(self, config: Optional[BenchmarkConfig] = None) -> Dict[str, BenchmarkResult]:
        """Benchmark all skills."""
        config = config or BenchmarkConfig()
        results = {}

        for skill_id in self.registry._skills:
            try:
                result = await self.benchmark.benchmark_skill(skill_id, config)
                results[skill_id] = result
            except Exception as e:
                self.logger.error("Benchmark failed", skill=skill_id, error=str(e))

        return results

    def get_quality_report(self) -> Dict[str, Any]:
        """Generate a comprehensive quality report."""
        skills = self.registry.list_skills()
        total = len(skills)
        passing = 0
        failing = 0
        quality_distribution = {"high": 0, "medium": 0, "low": 0}

        for skill in skills:
            qm = self.registry.get_quality(skill.skill_id)
            if qm and qm.validation_score >= 0.7:
                passing += 1
                if qm.validation_score >= 0.9:
                    quality_distribution["high"] += 1
                else:
                    quality_distribution["medium"] += 1
            else:
                failing += 1
                quality_distribution["low"] += 1

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_skills": total,
            "passing_quality": passing,
            "failing_quality": failing,
            "quality_distribution": quality_distribution,
            "pass_rate": passing / total if total > 0 else 0.0,
            "registry_stats": self.registry.get_statistics(),
        }

    def _discover_skill_files(self) -> List[Path]:
        """Discover all skill files."""
        skill_files = []
        for skill_file in self.skills_dir.glob("**/SKILL.md"):
            skill_files.append(skill_file)
        for skill_file in self.skills_dir.glob("**/SKILL_*.md"):
            skill_files.append(skill_file)
        return skill_files

    def _extract_skill_id(self, skill_file: Path) -> str:
        """Extract skill ID from file path."""
        return f"{skill_file.parent.parent.name}/{skill_file.parent.name}"

    def _load_skill_metadata(self, skill_file: Path) -> Optional[SkillMetadata]:
        """Load SkillMetadata from file."""
        from .metadata import SkillMetadata
        try:
            with open(skill_file, encoding="utf-8") as f:
                content = f.read()
            import yaml
            parts = content.split("---", 2)
            if len(parts) < 3:
                return None
            fm = yaml.safe_load(parts[1]) or {}
            return SkillMetadata.from_frontmatter(fm, parts[2], skill_file)
        except Exception as e:
            self.logger.error("Failed to load metadata", path=str(skill_file), error=str(e))
            return None

    def _load_existing_tests(self, skill_id: str) -> List[TestCase]:
        """Load existing tests from test directory."""
        tests = []
        test_dir = Path("tests") / "skills" / skill_id.replace("/", "_")
        if test_dir.exists():
            for test_file in test_dir.glob("test_*.py"):
                # Load test (simplified)
                pass
        return tests


# Convenience functions for CLI usage

async def run_quality_pipeline(skills_dir: Path, registry_file: Path,
                              plugin_manager=None) -> Dict[str, Any]:
    """Run the complete quality pipeline."""
    pipeline = SkillQualityPipeline(skills_dir, registry_file, plugin_manager)

    logger.info("Starting quality pipeline", skills_dir=str(skills_dir))

    # Phase 1: Validation
    validation_results = await pipeline.validate_all_skills()

    # Phase 2: Testing
    test_results = await pipeline.test_all_skills()

    # Phase 3: Benchmarking
    benchmark_results = await pipeline.benchmark_all_skills()

    # Generate report
    report = pipeline.get_quality_report()
    report["validation"] = {k: v.to_dict() for k, v in validation_results.items()}
    report["testing"] = test_results

    logger.info("Quality pipeline complete",
                total=report["total_skills"],
                passing=report["passing_quality"])

    return report


def generate_all_skill_tests(skills_dir: Path, output_dir: Path = Path("tests/skills")) -> None:
    """Generate test files for all skills."""
    output_dir.mkdir(parents=True, exist_ok=True)

    from .metadata import SkillMetadata

    for skill_file in skills_dir.glob("**/SKILL.md"):
        try:
            with open(skill_file, encoding="utf-8") as f:
                content = f.read()
            import yaml
            parts = content.split("---", 2)
            if len(parts) < 3:
                continue
            fm = yaml.safe_load(parts[1]) or {}
            metadata = SkillMetadata.from_frontmatter(fm, parts[2], skill_file)

            # Generate test file
            skill_id = metadata.skill_id.replace("/", "_")
            test_file = output_dir / f"test_{skill_id}.py"

            test_code = generate_test_code(metadata, skill_file)
            test_file.write_text(test_code, encoding="utf-8")

            logger.debug("Generated test file", skill=metadata.name, path=str(test_file))
        except Exception as e:
            logger.error("Failed to generate tests", path=str(skill_file), error=str(e))


def generate_test_code(metadata: SkillMetadata, skill_file: Path) -> str:
    """Generate pytest test code for a skill."""
    import re  # Import for safe_name sanitization

    skill_id = metadata.skill_id
    # Sanitize name for use in Python identifiers (class names)
    safe_name = "".join(c if c.isalnum() else "_" for c in metadata.name)
    # Ensure it starts with letter
    if safe_name and safe_name[0].isdigit():
        safe_name = f"_{safe_name}"

    # Use absolute path for SKILL_FILE reference (POSIX style for cross-platform compatibility)
    abs_path = skill_file.resolve().as_posix()

    code = f'''"""Tests for {metadata.name} skill."""

import pytest
from pathlib import Path
from em_cubed.skills.testing import SkillTestGenerator, SkillTestRunner
from em_cubed.indexer import get_skill_metadata
from em_cubed.plugin_manager import PluginManager

SKILL_FILE = Path("{abs_path}")
SKILL_ID = "{skill_id}"


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


class Test{safe_name}Skill:
    """Test suite for {metadata.name}."""

    def test_metadata_valid(self):
        """Test skill metadata is valid."""
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        assert metadata_dict is not None
        assert metadata_dict["name"] == "{metadata.name}"
        assert metadata_dict["domain"] == "{metadata.domain}"
        assert len(metadata_dict["surfaces"]) >= 1

    def test_surfaces_implemented(self, plugin_manager):
        """Test required surfaces are available."""
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        for surface in metadata_dict.get("surfaces", []):
            plugin = plugin_manager.get(surface)
            if plugin:
                assert plugin.available, f"Surface {{surface}} not available"

    @pytest.mark.asyncio
    async def test_skill_execution(self, test_runner, test_generator):
        """Test basic skill execution."""
        from em_cubed.skills.metadata import SkillMetadata
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        if not metadata_dict:
            pytest.skip("Skill metadata not available")
        
        metadata = SkillMetadata.from_frontmatter({{}}, "", SKILL_FILE)
        # Populate from dict
        for key, value in metadata_dict.items():
            if hasattr(metadata, key):
                setattr(metadata, key, value)

        tests = test_generator.generate_tests_for_skill(SKILL_FILE, metadata)
        if tests:
            results = await test_runner.run_test_suite(tests, SKILL_ID)
            # At least some tests should pass for a valid skill
            assert results["pass_rate"] > 0.3, f"Pass rate too low: {{results['pass_rate']}}"

'''
    return code
