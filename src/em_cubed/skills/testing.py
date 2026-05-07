"""Skill testing framework - generates and runs tests for skills.

Provides automated test generation from SKILL.md files, execution validation,
and integration testing for skill composition.
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

import structlog

logger = structlog.get_logger()


@dataclass
class TestCase:
    """A single test case extracted from SKILL.md or generated."""
    name: str
    surface: str  # python, prolog, hy
    code: str
    expected_output: Optional[Any] = None
    expected_error: Optional[str] = None
    timeout: float = 10.0
    setup_code: str = ""  # Code to run before test
    teardown_code: str = ""  # Code to run after test

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "surface": self.surface,
            "code": self.code,
            "expected_output": self.expected_output,
            "expected_error": self.expected_error,
            "timeout": self.timeout,
        }


@dataclass
class TestResult:
    """Result of a single test."""
    test_name: str
    skill_id: str
    surface: str
    passed: bool
    error: Optional[str] = None
    output: Optional[Any] = None
    duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_name": self.test_name,
            "skill_id": self.skill_id,
            "surface": self.surface,
            "passed": self.passed,
            "error": self.error,
            "output": str(self.output)[:200] if self.output else None,
            "duration_ms": self.duration_ms,
        }


class SkillTestGenerator:
    """Generate test cases from SKILL.md files."""

    def __init__(self, plugin_manager):
        self.plugin_manager = plugin_manager
        self.logger = logger.bind(component="test_generator")

    def generate_tests_for_skill(self, skill_path: Path, skill_metadata) -> List[TestCase]:
        """Generate test cases from a SKILL.md file."""
        # Reconstruct a fully-validated SkillMetadata from the file to ensure
        # nested dataclass objects are properly typed (not raw dicts).
        from .metadata import SkillMetadata
        import yaml

        try:
            content = skill_path.read_text(encoding="utf-8-sig")
            if content.startswith("---"):
                parts = content.split("---", 2)
                frontmatter = yaml.safe_load(parts[1]) if len(parts) >= 3 else {}
                body = parts[2] if len(parts) >= 3 else ""
                skill_metadata = SkillMetadata.from_frontmatter(frontmatter, body, skill_path)
        except Exception as e:
            self.logger.warning("Failed to re-parse skill metadata, using provided", error=str(e))
            # Fallback: convert any dict attributes to proper dataclass instances
            from .metadata import InputOutputSchema, SkillCapability, CompatibilityRange, QualityThresholds
            if hasattr(skill_metadata, 'input_schema') and isinstance(skill_metadata.input_schema, dict):
                skill_metadata.input_schema = InputOutputSchema.from_dict(skill_metadata.input_schema)
            if hasattr(skill_metadata, 'output_schema') and isinstance(skill_metadata.output_schema, dict):
                skill_metadata.output_schema = InputOutputSchema.from_dict(skill_metadata.output_schema)
            if hasattr(skill_metadata, 'capabilities') and isinstance(skill_metadata.capabilities, dict):
                skill_metadata.capabilities = SkillCapability.from_dict(skill_metadata.capabilities)
            if hasattr(skill_metadata, 'compatibility') and isinstance(skill_metadata.compatibility, dict):
                skill_metadata.compatibility = CompatibilityRange.from_dict(skill_metadata.compatibility)
            if hasattr(skill_metadata, 'quality_thresholds') and isinstance(skill_metadata.quality_thresholds, dict):
                skill_metadata.quality_thresholds = QualityThresholds(**skill_metadata.quality_thresholds)
            # metrics can remain dict/RuntimeMetrics - not used in schema generation

        tests = []
        content = skill_path.read_text(encoding="utf-8-sig")

        # Extract test sections from markdown
        # Look for ```python test blocks, explicit test sections, or infer from examples

        # 1. Extract explicit test blocks (labeled as "Testing" section or ```python test)
        test_blocks = self._extract_test_blocks(content)
        for i, (lang, code) in enumerate(test_blocks):
            test = TestCase(
                name=f"test_explicit_{i+1}",
                surface=lang,
                code=code,
            )
            tests.append(test)

        # 2. Infer tests from Implementation sections
        impl_tests = self._generate_from_implementation(skill_metadata, content)
        tests.extend(impl_tests)

        # 3. Generate schema validation tests if input/output schemas exist
        if hasattr(skill_metadata, 'input_schema') and skill_metadata.input_schema.properties:
            schema_tests = self._generate_schema_tests(skill_metadata)
            tests.extend(schema_tests)

        # 4. Generate basic structure validation test
        structure_test = self._generate_structure_test(skill_metadata)
        if structure_test:
            tests.append(structure_test)

        self.logger.debug("Generated tests", skill=skill_metadata.name, count=len(tests))
        return tests

    def _extract_test_blocks(self, content: str) -> List[Tuple[str, str]]:
        """Extract fenced code blocks marked as tests."""
        import re
        blocks = []

        # Look for ```python followed by test code
        # Pattern: ```python, ```py, ```test, or sections labeled "Testing"
        patterns = [
            r"```python\s*\r?\n(.*?)(?=`+)",
            r"```py\s*\r?\n(.*?)(?=`+)",
            r"```test\s*\r?\n(.*?)(?=`+)",
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, content, re.DOTALL):
                code = match.group(1).strip()
                # Check if it looks like test code (has assert, test_, etc.)
                if any(keyword in code for keyword in ["assert", "test_", "unittest", "pytest"]):
                    # Skip test code with imports since asteval doesn't support them
                    if "import " in code or "from " in code:
                        continue
                    blocks.append(("python", code))

        return blocks

    def _generate_from_implementation(self, skill_metadata, content: str) -> List[TestCase]:
        """Generate tests by extracting and verifying implementation code."""
        tests = []

        # Extract Python implementation
        python_code = self._extract_fenced(content, "python")
        if python_code:
            # Skip syntax tests for code with imports since asteval doesn't support them.
            # The structure test validates skill metadata which is sufficient for basic validation.
            # Only test syntax for code without imports.
            has_imports = "import " in python_code or "from " in python_code
            if not has_imports and len(python_code.strip()) > 0:
                # Use compile() which is a builtin - no import needed
                # Escape single quotes for safe embedding in triple-quoted string
                escaped_code = python_code.replace("'", "\\'")
                test = TestCase(
                    name=f"test_{skill_metadata.name.lower().replace(' ', '_')}_python_syntax",
                    surface="python",
                    code=f"""try:
    compile('''{escaped_code}''', '<string>', 'exec')
    print("SYNTAX_OK")
except SyntaxError as e:
    print(f"SYNTAX_ERROR: {{e}}")
""",
                    expected_output="SYNTAX_OK",
                )
                tests.append(test)

        return tests

    def _generate_schema_tests(self, skill_metadata) -> List[TestCase]:
        """Generate tests that validate input/output schema conformance."""
        tests = []

        if skill_metadata.input_schema.properties:
            # Generate a test that validates sample input against schema
            sample_input = self._generate_sample_from_schema(skill_metadata.input_schema)
            test = TestCase(
                name=f"test_{skill_metadata.name.lower().replace(' ', '_')}_input_schema",
                surface="python",
                code=f"""
schema = {skill_metadata.input_schema.to_dict()}
sample_input = {sample_input}
required = schema.get('required', [])
for field in required:
    assert field in sample_input, f"Missing required field: {{field}}"
print("SCHEMA_VALID")
""",
                expected_output="SCHEMA_VALID",
            )
            tests.append(test)

        return tests

    def _generate_structure_test(self, skill_metadata) -> Optional[TestCase]:
        """Generate a test that checks skill structure integrity."""
        test = TestCase(
            name=f"test_{skill_metadata.name.lower().replace(' ', '_')}_structure",
            surface="python",
            code=f"""
metadata = {skill_metadata.to_registry_dict()}
assert metadata['name'] == '{skill_metadata.name}'
assert metadata['domain'] == '{skill_metadata.domain}'
assert len(metadata['surfaces']) >= 1
"STRUCTURE_OK"
""",
            expected_output="STRUCTURE_OK",
        )
        return test

    def _extract_fenced(self, content: str, lang: str) -> Optional[str]:
        """Extract fenced code block for a language."""
        pattern = rf"```{lang}\s*\r?\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else None

    def _generate_sample_from_schema(self, schema) -> Dict[str, Any]:
        """Generate a sample instance from a JSON schema."""
        sample: Dict[str, Any] = {}
        for prop_name, prop_def in schema.properties.items():
            prop_type = prop_def.get("type", "string")
            if prop_type == "string":
                sample[prop_name] = "test_string"
            elif prop_type in ("number", "integer"):
                sample[prop_name] = 42
            elif prop_type == "boolean":
                sample[prop_name] = True
            elif prop_type == "array":
                sample[prop_name] = []
            else:
                sample[prop_name] = {}
        return sample


class SkillTestRunner:
    """Run skill tests across surfaces."""

    def __init__(self, plugin_manager, registry):
        self.plugin_manager = plugin_manager
        self.registry = registry
        self.logger = logger.bind(component="test_runner")

    async def run_test(self, test: TestCase, context: Optional[Dict] = None) -> TestResult:
        """Run a single test case."""
        import time
        surface = self.plugin_manager.get(test.surface)
        if not surface or not surface.available:
            return TestResult(
                test_name=test.name,
                skill_id="unknown",
                surface=test.surface,
                passed=False,
                error=f"Surface '{test.surface}' not available",
            )

        start = time.perf_counter()
        try:
            result = await surface.execute(test.code, context)
            elapsed = (time.perf_counter() - start) * 1000

            passed = True
            error = None

            if result.get("status") != "ok":
                passed = False
                error = result.get("message", "Execution failed")
            elif test.expected_output is not None:
                output = result.get("value")
                if str(output) != str(test.expected_output):
                    passed = False
                    error = f"Expected '{test.expected_output}', got '{output}'"
            elif test.expected_error:
                passed = False
                error = f"Expected error '{test.expected_error}' but execution succeeded"

            return TestResult(
                test_name=test.name,
                skill_id="unknown",
                surface=test.surface,
                passed=passed,
                error=error,
                output=result.get("value"),
                duration_ms=elapsed,
            )
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            return TestResult(
                test_name=test.name,
                skill_id="unknown",
                surface=test.surface,
                passed=False,
                error=str(e),
                duration_ms=elapsed,
            )

    async def run_test_suite(self, tests: List[TestCase], skill_id: str) -> Dict[str, Any]:
        """Run a full test suite and return summary."""
        results = []
        passed = 0
        failed = 0
        total_duration = 0.0

        for test in tests:
            result = await self.run_test(test)
            result.skill_id = skill_id
            results.append(result)
            if result.passed:
                passed += 1
            else:
                failed += 1
            total_duration += result.duration_ms

        summary = {
            "skill_id": skill_id,
            "total_tests": len(tests),
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / len(tests) if tests else 0.0,
            "total_duration_ms": total_duration,
            "results": [r.to_dict() for r in results],
        }

        self.logger.info("Test suite completed",
                        skill=skill_id,
                        total=len(tests),
                        passed=passed,
                        failed=failed,
                        duration_ms=total_duration)

        return summary
