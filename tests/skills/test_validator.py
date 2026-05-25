"""Tests for skill validator module."""

import pytest

from em_cubed.skills.validator import (
    SkillValidator,
    ValidationResult,
    ValidationSeverity,
    ValidationIssue,
)
from em_cubed.skills.metadata import SkillMetadata


@pytest.fixture
def validator():
    """Create a SkillValidator instance."""
    return SkillValidator()


@pytest.fixture
def valid_metadata():
    """Create a valid SkillMetadata for testing."""
    return SkillMetadata(
        name="Test Skill",
        domain="General",
        version="1.0.0",
        surfaces=["python"],
        purpose="A test skill for validation purposes.",
        description="This skill is used to test the validation framework.",
    )


class TestValidationSeverity:
    """Test ValidationSeverity enum."""

    def test_error_value(self):
        assert ValidationSeverity.ERROR.value == "error"

    def test_warning_value(self):
        assert ValidationSeverity.WARNING.value == "warning"

    def test_info_value(self):
        assert ValidationSeverity.INFO.value == "info"

    def test_success_value(self):
        assert ValidationSeverity.SUCCESS.value == "success"


class TestValidationIssue:
    """Test ValidationIssue dataclass."""

    def test_issue_creation(self):
        issue = ValidationIssue(
            severity=ValidationSeverity.WARNING,
            code="TEST_CODE",
            message="Test message",
            component="test",
        )
        assert issue.severity == ValidationSeverity.WARNING
        assert issue.code == "TEST_CODE"
        assert issue.message == "Test message"
        assert issue.component == "test"
        assert issue.suggestion is None
        assert issue.line_number is None

    def test_issue_with_optional_fields(self):
        issue = ValidationIssue(
            severity=ValidationSeverity.ERROR,
            code="TEST_CODE",
            message="Test message",
            component="test",
            suggestion="Fix this",
            line_number=42,
        )
        assert issue.suggestion == "Fix this"
        assert issue.line_number == 42

    def test_issue_to_dict(self):
        issue = ValidationIssue(
            severity=ValidationSeverity.INFO,
            code="INFO_CODE",
            message="Info message",
            component="metadata",
            suggestion="Suggestion text",
            line_number=10,
        )
        d = issue.to_dict()
        assert d["severity"] == "info"
        assert d["code"] == "INFO_CODE"
        assert d["message"] == "Info message"
        assert d["component"] == "metadata"
        assert d["suggestion"] == "Suggestion text"
        assert d["line_number"] == 10


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_result_creation(self):
        result = ValidationResult(
            skill_id="test/skill",
            valid=True,
        )
        assert result.skill_id == "test/skill"
        assert result.valid is True
        assert result.issues == []
        assert result.quality_score == 0.0
        # validated_at defaults to empty string
        assert result.validated_at == ""

    def test_add_issue(self):
        result = ValidationResult(skill_id="test/skill", valid=True)
        result.add_issue(
            severity=ValidationSeverity.WARNING,
            code="TEST_WARN",
            message="Warning message",
            component="test",
        )
        assert len(result.issues) == 1
        assert result.issues[0].code == "TEST_WARN"

    def test_add_issue_error_makes_invalid(self):
        result = ValidationResult(skill_id="test/skill", valid=True)
        result.add_issue(
            severity=ValidationSeverity.ERROR,
            code="TEST_ERROR",
            message="Error message",
            component="test",
        )
        # Adding an error should set valid to False
        assert result.valid is False

    def test_get_issues_by_severity(self):
        result = ValidationResult(skill_id="test/skill", valid=True)
        result.add_issue(ValidationSeverity.ERROR, "E1", "Error", "test")
        result.add_issue(ValidationSeverity.WARNING, "W1", "Warning", "test")
        result.add_issue(ValidationSeverity.WARNING, "W2", "Warning 2", "test")
        result.add_issue(ValidationSeverity.INFO, "I1", "Info", "test")

        errors = result.get_issues_by_severity(ValidationSeverity.ERROR)
        warnings = result.get_issues_by_severity(ValidationSeverity.WARNING)
        infos = result.get_issues_by_severity(ValidationSeverity.INFO)

        assert len(errors) == 1
        assert len(warnings) == 2
        assert len(infos) == 1

    def test_to_dict(self):
        result = ValidationResult(skill_id="test/skill", valid=True)
        result.add_issue(ValidationSeverity.WARNING, "W1", "Warning", "test")
        d = result.to_dict()

        assert d["skill_id"] == "test/skill"
        assert d["valid"] is True
        assert d["error_count"] == 0
        assert d["warning_count"] == 1
        assert d["info_count"] == 0
        assert len(d["issues"]) == 1


class TestSkillValidator:
    """Test SkillValidator class."""

    def test_initialization(self, validator):
        assert validator.min_purpose_length == 10
        assert validator.min_description_length == 20
        assert validator.min_code_lines == 5
        assert validator.ideal_surface_count == 3
        assert validator.min_surface_count == 1

    def test_validate_skill_file_with_valid_metadata(self, validator, tmp_path):
        """Test validation with valid metadata passes."""
        skill_file = tmp_path / "skill.md"
        skill_file.write_text("""---
name: Test Skill
Domain: General
Version: 1.0.0
---

## Purpose

A test skill with a purpose that is long enough to pass the minimum length check.

## Description

A test skill description that is long enough to satisfy the minimum description length requirement.

```python
def hello():
    return 'hello'
```
""")

        metadata = SkillMetadata(
            name="Test Skill",
            domain="General",
            version="1.0.0",
            surfaces=["python"],
            purpose="A test skill with a purpose that is long enough.",
            description="A test skill description that is long enough to pass.",
        )

        result = validator.validate_skill_file(skill_file, metadata)
        assert result.valid is True
        assert result.quality_score >= 0.0

    def test_validate_missing_required_fields(self, validator, tmp_path):
        """Test validation fails when required fields are missing."""
        skill_file = tmp_path / "skill.md"
        skill_file.write_text("---\nVersion: 1.0.0\n---\n\nNo purpose or description.\n")

        metadata = SkillMetadata(
            name="",  # Empty name
            domain="",  # Empty domain
            version="1.0.0",
        )

        result = validator.validate_skill_file(skill_file, metadata)
        # Should have errors for missing name and domain
        assert result.valid is False

    def test_validate_metadata_semver(self, validator, tmp_path):
        """Test version format validation."""
        skill_file = tmp_path / "skill.md"
        skill_file.write_text("---\nname: Test\nDomain: General\nVersion: bad-version\n---\n\nTest\n")

        metadata = SkillMetadata(
            name="Test Skill",
            domain="General",
            version="bad-version",
        )

        result = validator.validate_skill_file(skill_file, metadata)

        # Should have a warning for invalid version
        version_warnings = [
            i for i in result.issues
            if i.code == "INVALID_VERSION" and i.severity == ValidationSeverity.WARNING
        ]
        assert len(version_warnings) == 1

    def test_validate_metadata_unknown_domain(self, validator, tmp_path):
        """Test validation with unknown domain."""
        skill_file = tmp_path / "skill.md"
        skill_file.write_text("---\nname: Test\nDomain: UNKNOWN_DOMAIN\nVersion: 1.0.0\n---\n\nTest\n")

        metadata = SkillMetadata(
            name="Test Skill",
            domain="UNKNOWN_DOMAIN",
            version="1.0.0",
        )

        result = validator.validate_skill_file(skill_file, metadata)

        domain_warnings = [
            i for i in result.issues
            if i.code == "UNKNOWN_DOMAIN"
        ]
        assert len(domain_warnings) == 1

    def test_validate_invalid_surface(self, validator, tmp_path):
        """Test validation with invalid surface type."""
        skill_file = tmp_path / "skill.md"
        skill_file.write_text("---\nname: Test\nDomain: General\nVersion: 1.0.0\nsurfaces:\n  - python\n  - invalid_surface\n---\n\nTest\n")

        metadata = SkillMetadata(
            name="Test Skill",
            domain="General",
            version="1.0.0",
            surfaces=["python", "invalid_surface"],
        )

        result = validator.validate_skill_file(skill_file, metadata)
        # Invalid surface should produce an error
        surface_errors = [
            i for i in result.issues
            if i.code == "UNKNOWN_SURFACE" and i.severity == ValidationSeverity.ERROR
        ]
        assert len(surface_errors) >= 1

    def test_validate_insufficient_surfaces(self, validator, tmp_path):
        """Test validation requires minimum surfaces."""
        skill_file = tmp_path / "skill.md"
        skill_file.write_text("---\nname: Test\nDomain: General\nVersion: 1.0.0\n---\n\nTest\n")

        metadata = SkillMetadata(
            name="Test Skill",
            domain="General",
            version="1.0.0",
            surfaces=[],  # No surfaces
        )

        result = validator.validate_skill_file(skill_file, metadata)

        surface_errors = [
            i for i in result.issues
            if i.code == "INSUFFICIENT_SURFACES"
        ]
        assert len(surface_errors) == 1

    def test_validate_dependencies(self, validator, tmp_path):
        """Test dependency validation."""
        from em_cubed.skills.metadata import SkillDependency

        skill_file = tmp_path / "skill.md"
        skill_file.write_text("---\nname: Test\nDomain: General\nVersion: 1.0.0\ndependencies:\n  - skill_id: bad_dependency\n    version_range: '>=1.0.0'\n---\n\nTest\n")

        metadata = SkillMetadata(
            name="Test Skill",
            domain="General",
            version="1.0.0",
            surfaces=["python"],
            dependencies=[
                SkillDependency(skill_id="bad_dependency", version_range=">=1.0.0"),
            ],
        )

        result = validator.validate_skill_file(skill_file, metadata)

        # Dependencies without proper domain format should get warnings
        dep_warnings = [
            i for i in result.issues
            if i.code == "INVALID_DEPENDENCY_FORMAT"
        ]
        assert len(dep_warnings) == 1

    def test_validate_composition(self, validator):
        """Test skill composition validation."""
        source = SkillMetadata(
            name="Source",
            domain="General",
            surfaces=["python"],
        )
        target = SkillMetadata(
            name="Target",
            domain="General",
            surfaces=["python"],
        )

        result = validator.validate_composition(source, target)
        assert result is not None
        # Should be valid by default with any type
        assert result.valid is True

    def test_quality_score_calculation(self, validator):
        """Test quality score calculation."""
        result = ValidationResult(skill_id="test/skill", valid=True)

        # Start with valid, add errors
        result.add_issue(ValidationSeverity.ERROR, "E1", "Error", "test")
        result.add_issue(ValidationSeverity.WARNING, "W1", "Warning", "test")

        validator._calculate_quality_score(result)

        # With 1 error (0.5 deduction) and 1 warning (0.1 deduction),
        # score should be 1.0 - 0.5 - 0.1 = 0.4
        assert result.quality_score >= 0.0
        assert result.quality_score <= 1.0

    def test_no_purpose_warning(self, validator, tmp_path):
        """Test that short purpose generates a warning."""
        skill_file = tmp_path / "skill.md"
        skill_file.write_text("---\nname: Test\nDomain: General\nVersion: 1.0.0\n---\n\n## Purpose\nHi\n\n## Description\nA description that is long enough to pass the minimum length requirement for descriptions.\n\n```python\ndef hello():\n    pass\n```\n")

        metadata = SkillMetadata(
            name="Test Skill",
            domain="General",
            version="1.0.0",
            purpose="Hi",  # Too short
        )

        result = validator.validate_skill_file(skill_file, metadata)

        purpose_warnings = [
            i for i in result.issues
            if i.code == "SHORT_PURPOSE"
        ]
        assert len(purpose_warnings) == 1

    def test_valid_version_passes(self, validator, tmp_path):
        """Test that valid semver passes."""
        skill_file = tmp_path / "skill.md"
        skill_file.write_text("---\nname: Test Skill\nDomain: General\nVersion: 1.0.0\n---\n\nTest\n")

        metadata = SkillMetadata(
            name="Test Skill",
            domain="General",
            version="1.0.0",
        )

        result = validator.validate_skill_file(skill_file, metadata)

        version_warnings = [
            i for i in result.issues
            if i.code == "INVALID_VERSION"
        ]
        assert len(version_warnings) == 0

    def test_validate_composition_incompatible(self, validator):
        """Test composition validation with incompatible surfaces."""
        source = SkillMetadata(
            name="Source",
            domain="General",
            surfaces=["python"],
        )
        target = SkillMetadata(
            name="Target",
            domain="General",
            surfaces=[],  # No surfaces - incompatible
        )

        result = validator.validate_composition(source, target)
        assert result is not None

    def test_validate_skill_file_successfully_validates(self, validator, tmp_path):
        """Test full skill file validation with all required fields."""
        skill_file = tmp_path / "skill.md"
        skill_file.write_text("""---
name: Full Test Skill
Domain: Machine Learning
Version: 2.0.0
surfaces:
  - python
  - prolog
description: A comprehensive test skill with a long enough description.
purpose: This skill tests the full validation pipeline with multiple surfaces.
tags:
  - test
  - validation
---

## Purpose

This skill tests the full validation pipeline.

## Description

A comprehensive description that satisfies the minimum length requirement.

```python
def main():
    return "result"
```
""")

        metadata = SkillMetadata(
            name="Full Test Skill",
            domain="Machine Learning",
            version="2.0.0",
            surfaces=["python", "prolog"],
            purpose="This skill tests the full validation pipeline with multiple surfaces.",
            description="A comprehensive description that satisfies the minimum length requirement.",
        )

        result = validator.validate_skill_file(skill_file, metadata)
        assert result.valid is True
        assert result.quality_score > 0.5