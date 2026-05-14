"""Tests for skill testing framework module."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

from em_cubed.skills.testing import (
    SkillTestGenerator,
    SkillTestRunner,
    TestCase,
    TestResult,
)
from em_cubed.skills.metadata import SkillMetadata


class TestCaseCreation:
    """Test TestCase dataclass."""

    def test_test_case_creation(self):
        """Test basic TestCase creation."""
        tc = TestCase(
            name="test_example",
            surface="python",
            code="1 + 1",
            expected_output=2,
        )
        assert tc.name == "test_example"
        assert tc.surface == "python"
        assert tc.code == "1 + 1"
        assert tc.expected_output == 2
        assert tc.timeout == 10.0
        assert tc.setup_code == ""
        assert tc.teardown_code == ""

    def test_test_case_with_timeout(self):
        """Test TestCase with custom timeout."""
        tc = TestCase(
            name="test_custom",
            surface="prolog",
            code="fact(X).",
            timeout=30.0,
        )
        assert tc.timeout == 30.0

    def test_test_case_to_dict(self):
        """Test TestCase serialization to dict."""
        tc = TestCase(
            name="test_dict",
            surface="python",
            code="result = 42",
            expected_output=42,
            expected_error=None,
            timeout=5.0,
        )
        d = tc.to_dict()
        assert d["name"] == "test_dict"
        assert d["surface"] == "python"
        assert d["code"] == "result = 42"
        assert d["expected_output"] == 42
        assert d["expected_error"] is None
        assert d["timeout"] == 5.0


class TestResultCreation:
    """Test TestResult dataclass."""

    def test_test_result_creation(self):
        """Test basic TestResult creation."""
        tr = TestResult(
            test_name="test_1",
            skill_id="test_skill",
            surface="python",
            passed=True,
            output=42,
            duration_ms=100.0,
        )
        assert tr.test_name == "test_1"
        assert tr.skill_id == "test_skill"
        assert tr.surface == "python"
        assert tr.passed is True
        assert tr.output == 42
        assert tr.duration_ms == 100.0

    def test_test_result_with_error(self):
        """Test TestResult with error."""
        tr = TestResult(
            test_name="test_2",
            skill_id="test_skill",
            surface="prolog",
            passed=False,
            error="Something went wrong",
        )
        assert tr.passed is False
        assert tr.error == "Something went wrong"

    def test_test_result_to_dict(self):
        """Test TestResult serialization to dict."""
        tr = TestResult(
            test_name="test_dict",
            skill_id="test_skill",
            surface="python",
            passed=True,
            output="hello",
            duration_ms=50.0,
        )
        d = tr.to_dict()
        assert d["test_name"] == "test_dict"
        assert d["skill_id"] == "test_skill"
        assert d["surface"] == "python"
        assert d["passed"] is True
        assert d["output"] == "hello"
        assert d["duration_ms"] == 50.0
        # Output should be truncated to 200 chars in to_dict
        long_tr = TestResult(
            test_name="long",
            skill_id="s",
            surface="p",
            passed=True,
            output="x" * 300,
        )
        assert len(long_tr.to_dict()["output"]) == 200


class TestSkillTestGenerator:
    """Test SkillTestGenerator class."""

    @pytest.fixture
    def mock_plugin_manager(self):
        """Create a mock plugin manager."""
        return MagicMock()

    @pytest.fixture
    def generator(self, mock_plugin_manager):
        """Create a SkillTestGenerator instance."""
        return SkillTestGenerator(mock_plugin_manager)

    def test_initialization(self, generator, mock_plugin_manager):
        """Test generator initialization."""
        assert generator.plugin_manager is mock_plugin_manager

    def test_extract_test_blocks_empty(self, generator):
        """Test extracting test blocks from content with no tests."""
        content = """
# Just some code
def hello():
    return "world"
"""
        blocks = generator._extract_test_blocks(content)
        assert blocks == []

    def test_extract_test_blocks_with_assert(self, generator):
        """Test extracting test blocks with assert statements."""
        content = """
```python
assert 1 + 1 == 2
assert True
```
"""
        blocks = generator._extract_test_blocks(content)
        assert len(blocks) == 1
        assert blocks[0][0] == "python"
        assert "assert" in blocks[0][1]

    def test_extract_test_blocks_skips_imports(self, generator):
        """Test that test blocks with imports are skipped."""
        content = """
```python
import os
assert os.path.exists("/tmp")
```
"""
        blocks = generator._extract_test_blocks(content)
        assert blocks == []

    def test_extract_test_blocks_skips_non_test_code(self, generator):
        """Test that non-test code blocks are skipped."""
        content = """
```python
def hello():
    return "world"
```
"""
        blocks = generator._extract_test_blocks(content)
        assert blocks == []

    def test_extract_fenced_simple(self, generator):
        """Test extracting a simple fenced code block."""
        content = """
Some text before

```python
def hello():
    return "world"
```

Some text after
"""
        result = generator._extract_fenced(content, "python")
        assert result == "def hello():\n    return \"world\""

    def test_extract_fenced_not_found(self, generator):
        """Test extracting a fenced code block that doesn't exist."""
        content = "No python code here"
        result = generator._extract_fenced(content, "python")
        assert result is None

    def test_extract_fenced_prolog(self, generator):
        """Test extracting Prolog fenced code block."""
        content = """
Some text

```prolog
parent(john, mary).
parent(mary, ann).
```
"""
        result = generator._extract_fenced(content, "prolog")
        assert "parent(john, mary)" in result

    def test_generate_structure_test(self, generator):
        """Test structure test generation."""
        metadata = SkillMetadata(
            name="Test Skill",
            domain="General",
            surfaces=["python"],
            version="1.0.0",
        )
        test = generator._generate_structure_test(metadata)
        assert test is not None
        assert test.name == "test_test_skill_structure"
        assert test.surface == "python"
        assert "Test Skill" in test.code
        assert "General" in test.code

    def test_generate_schema_tests_with_input_schema(self, generator):
        """Test schema test generation with input schema."""
        metadata = MagicMock()
        metadata.input_schema.properties = {"x": {"type": "number"}, "y": {"type": "string"}}
        metadata.name = "Test Skill"

        tests = generator._generate_schema_tests(metadata)
        assert len(tests) == 1
        assert tests[0].name == "test_test_skill_input_schema"
        assert tests[0].surface == "python"

    def test_generate_schema_tests_empty_schema(self, generator):
        """Test schema test generation with empty input schema."""
        metadata = MagicMock()
        metadata.input_schema.properties = {}

        tests = generator._generate_schema_tests(metadata)
        assert tests == []

    def test_generate_from_implementation_no_imports(self, generator):
        """Test test generation from code without imports."""
        metadata = MagicMock()
        metadata.name = "Test Skill"

        content = """
## Implementation

```python
def add(a, b):
    return a + b

add(1, 2)
```
"""
        tests = generator._generate_from_implementation(metadata, content)
        assert len(tests) == 1
        assert tests[0].name == "test_test_skill_python_syntax"
        assert "SYNTAX_OK" in tests[0].expected_output

    def test_generate_from_implementation_with_imports(self, generator):
        """Test that code with imports is skipped for syntax tests."""
        metadata = MagicMock()
        metadata.name = "Test Skill"

        content = """
## Implementation

```python
import numpy as np
def compute():
    return np.array([1, 2, 3])
```
"""
        tests = generator._generate_from_implementation(metadata, content)
        assert tests == []

    def test_generate_tests_for_skill(self, generator, tmp_path):
        """Test full test generation from a skill file."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("""---
name: Test Skill
Domain: General
Version: 1.0.0
surfaces:
  - python
---

## Purpose

A test skill.

## Implementation

```python
def add(a, b):
    return a + b

add(1, 2)
```
""")

        from em_cubed.skills.metadata import SkillMetadata
        metadata = SkillMetadata.from_frontmatter(
            {"name": "Test Skill", "domain": "General", "version": "1.0.0", "surfaces": ["python"]},
            "",
            skill_file
        )

        tests = generator.generate_tests_for_skill(skill_file, metadata)
        assert len(tests) >= 1
        # Should have at least a structure test and a syntax test
        test_names = [t.name for t in tests]
        assert any("structure" in n for n in test_names)

    def test_generate_tests_with_explicit_test_block(self, generator, tmp_path):
        """Test that explicit test blocks are extracted."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("""---
name: Test Skill
Domain: General
Version: 1.0.0
---

## Testing

```python
assert 1 + 1 == 2
```
""")

        from em_cubed.skills.metadata import SkillMetadata
        metadata = SkillMetadata.from_frontmatter(
            {"name": "Test Skill", "domain": "General", "version": "1.0.0"},
            "",
            skill_file
        )

        tests = generator.generate_tests_for_skill(skill_file, metadata)
        test_names = [t.name for t in tests]
        assert any("explicit" in n for n in test_names)


class TestSkillTestRunner:
    """Test SkillTestRunner class."""

    @pytest.fixture
    def mock_plugin_manager(self):
        """Create a mock plugin manager with a mock surface."""
        mock_pm = MagicMock()
        mock_surface = MagicMock()
        mock_surface.available = True
        mock_pm.get.return_value = mock_surface
        mock_pm._plugins = {"python": mock_surface}
        return mock_pm

    @pytest.fixture
    def runner(self, mock_plugin_manager):
        """Create a SkillTestRunner instance."""
        registry = MagicMock()
        return SkillTestRunner(mock_plugin_manager, registry)

    @pytest.mark.asyncio
    async def test_run_test_success(self, runner, mock_plugin_manager):
        """Test running a single test successfully."""
        mock_surface = mock_plugin_manager.get("python")
        mock_surface.execute = AsyncMock(return_value={"status": "ok", "value": 42})

        test = TestCase(
            name="test_add",
            surface="python",
            code="1 + 1",
            expected_output=42,
        )

        result = await runner.run_test(test)
        assert result.test_name == "test_add"
        assert result.passed is True
        assert result.error is None
        assert result.surface == "python"

    @pytest.mark.asyncio
    async def test_run_test_wrong_output(self, runner, mock_plugin_manager):
        """Test running a test with wrong expected output."""
        mock_surface = mock_plugin_manager.get("python")
        mock_surface.execute = AsyncMock(return_value={"status": "ok", "value": 43})

        test = TestCase(
            name="test_add",
            surface="python",
            code="1 + 1",
            expected_output=42,
        )

        result = await runner.run_test(test)
        assert result.passed is False
        assert "Expected" in result.error
        assert "43" in result.error

    @pytest.mark.asyncio
    async def test_run_test_execution_error(self, runner, mock_plugin_manager):
        """Test running a test that produces an execution error."""
        mock_surface = mock_plugin_manager.get("python")
        mock_surface.execute = AsyncMock(return_value={"status": "error", "message": "Syntax error"})

        test = TestCase(
            name="test_broken",
            surface="python",
            code="invalid syntax !!",
        )

        result = await runner.run_test(test)
        assert result.passed is False
        assert result.error == "Syntax error"

    @pytest.mark.asyncio
    async def test_run_test_expected_error(self, runner, mock_plugin_manager):
        """Test running a test that expects an error but succeeds."""
        mock_surface = mock_plugin_manager.get("python")
        mock_surface.execute = AsyncMock(return_value={"status": "ok", "value": 42})

        test = TestCase(
            name="test_add",
            surface="python",
            code="1 + 1",
            expected_error="Should fail",
        )

        result = await runner.run_test(test)
        assert result.passed is False
        assert "Expected error" in result.error

    @pytest.mark.asyncio
    async def test_run_test_missing_surface(self, runner, mock_plugin_manager):
        """Test running a test with an unavailable surface."""
        mock_plugin_manager.get.return_value = None

        test = TestCase(
            name="test_add",
            surface="nonexistent",
            code="1 + 1",
        )

        result = await runner.run_test(test)
        assert result.passed is False
        assert "not available" in result.error

    @pytest.mark.asyncio
    async def test_run_test_exception(self, runner, mock_plugin_manager):
        """Test running a test that raises an exception."""
        mock_surface = mock_plugin_manager.get("python")
        mock_surface.execute = AsyncMock(side_effect=RuntimeError("Unexpected error"))

        test = TestCase(
            name="test_crash",
            surface="python",
            code="crash()",
        )

        result = await runner.run_test(test)
        assert result.passed is False
        assert "Unexpected error" in result.error

    @pytest.mark.asyncio
    async def test_run_test_suite(self, runner, mock_plugin_manager):
        """Test running a full test suite."""
        mock_surface = mock_plugin_manager.get("python")

        async def execute_side_effect(code, context=None):
            if "fail" in code:
                return {"status": "error", "message": "fail"}
            return {"status": "ok", "value": "ok"}

        mock_surface.execute = execute_side_effect

        tests = [
            TestCase(name="test_pass_1", surface="python", code="1 + 1", expected_output="ok"),
            TestCase(name="test_pass_2", surface="python", code="2 + 2", expected_output="ok"),
            TestCase(name="test_fail_1", surface="python", code="fail", expected_output="ok"),
        ]

        result = await runner.run_test_suite(tests, "test_skill")

        assert result["skill_id"] == "test_skill"
        assert result["total_tests"] == 3
        assert result["passed"] == 2
        assert result["failed"] == 1
        assert result["pass_rate"] == 2 / 3
        assert len(result["results"]) == 3

    @pytest.mark.asyncio
    async def test_run_test_suite_empty(self, runner, mock_plugin_manager):
        """Test running an empty test suite."""
        result = await runner.run_test_suite([], "empty_skill")
        assert result["skill_id"] == "empty_skill"
        assert result["total_tests"] == 0
        assert result["passed"] == 0
        assert result["failed"] == 0
        assert result["pass_rate"] == 0.0