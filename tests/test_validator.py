"""Tests for the skill validator module."""

import pytest
from unittest.mock import Mock

from src.em_cubed.skills.validator import (
    SkillValidator,
    ValidationSeverity,
    ValidationIssue,
    ValidationResult
)
from src.em_cubed.skills.metadata import SkillMetadata


class TestValidationSeverity:
    """Test cases for ValidationSeverity enum."""
    
    def test_severity_values(self):
        """Test that enum values are correct."""
        assert ValidationSeverity.ERROR.value == "error"
        assert ValidationSeverity.WARNING.value == "warning"
        assert ValidationSeverity.INFO.value == "info"
        assert ValidationSeverity.SUCCESS.value == "success"


class TestValidationIssue:
    """Test cases for ValidationIssue dataclass."""
    
    def test_issue_creation(self):
        """Test creating a validation issue."""
        issue = ValidationIssue(
            severity=ValidationSeverity.ERROR,
            code="TEST_ERROR",
            message="Test error message",
            component="test_component",
            suggestion="Fix this",
            line_number=42
        )
        
        assert issue.severity == ValidationSeverity.ERROR
        assert issue.code == "TEST_ERROR"
        assert issue.message == "Test error message"
        assert issue.component == "test_component"
        assert issue.suggestion == "Fix this"
        assert issue.line_number == 42
    
    def test_issue_to_dict(self):
        """Test converting issue to dictionary."""
        issue = ValidationIssue(
            severity=ValidationSeverity.WARNING,
            code="TEST_WARNING",
            message="Test warning",
            component="test",
            suggestion=None,
            line_number=None
        )
        
        result = issue.to_dict()
        
        assert result["severity"] == "warning"
        assert result["code"] == "TEST_WARNING"
        assert result["message"] == "Test warning"
        assert result["component"] == "test"
        assert result["suggestion"] is None
        assert result["line_number"] is None


class TestValidationResult:
    """Test cases for ValidationResult dataclass."""
    
    def test_result_creation(self):
        """Test creating a validation result."""
        result = ValidationResult(
            skill_id="test/skill",
            valid=True,
            issues=[],
            quality_score=0.95,
            validated_at="2023-01-01T00:00:00"
        )
        
        assert result.skill_id == "test/skill"
        assert result.valid is True
        assert result.issues == []
        assert result.quality_score == 0.95
        assert result.validated_at == "2023-01-01T00:00:00"
    
    def test_add_issue_no_error(self):
        """Test adding issues that don't affect validity."""
        result = ValidationResult(
            skill_id="test/skill",
            valid=True,
            issues=[],
            quality_score=0.0,
            validated_at=""
        )
        
        # Add a warning
        result.add_issue(
            severity=ValidationSeverity.WARNING,
            code="TEST_WARNING",
            message="Test warning",
            component="test"
        )
        
        assert result.valid is True  # Still valid because warning doesn't invalidate
        assert len(result.issues) == 1
        assert result.issues[0].code == "TEST_WARNING"
    
    def test_add_issue_with_error(self):
        """Test adding an error that affects validity."""
        result = ValidationResult(
            skill_id="test/skill",
            valid=True,
            issues=[],
            quality_score=0.0,
            validated_at=""
        )
        
        # Add an error
        result.add_issue(
            severity=ValidationSeverity.ERROR,
            code="TEST_ERROR",
            message="Test error",
            component="test"
        )
        
        assert result.valid is False  # Now invalid due to error
        assert len(result.issues) == 1
        assert result.issues[0].code == "TEST_ERROR"
    
    def test_get_issues_by_severity(self):
        """Test getting issues by severity."""
        result = ValidationResult(
            skill_id="test/skill",
            valid=True,
            issues=[],
            quality_score=0.0,
            validated_at=""
        )
        
        # Add various issues
        result.add_issue(ValidationSeverity.ERROR, "E1", "Error 1", "comp1")
        result.add_issue(ValidationSeverity.WARNING, "W1", "Warning 1", "comp1")
        result.add_issue(ValidationSeverity.INFO, "I1", "Info 1", "comp1")
        result.add_issue(ValidationSeverity.ERROR, "E2", "Error 2", "comp2")
        
        errors = result.get_issues_by_severity(ValidationSeverity.ERROR)
        warnings = result.get_issues_by_severity(ValidationSeverity.WARNING)
        info = result.get_issues_by_severity(ValidationSeverity.INFO)
        
        assert len(errors) == 2
        assert len(warnings) == 1
        assert len(info) == 1
        assert errors[0].code == "E1"
        assert errors[1].code == "E2"
        assert warnings[0].code == "W1"
        assert info[0].code == "I1"
    
    def test_to_dict(self):
        """Test converting result to dictionary."""
        result = ValidationResult(
            skill_id="test/skill",
            valid=False,
            issues=[],
            quality_score=0.6,
            validated_at="2023-01-01T00:00:00"
        )
        
        result.add_issue(ValidationSeverity.ERROR, "E1", "Error", "comp1")
        result.add_issue(ValidationSeverity.WARNING, "W1", "Warning", "comp1")
        
        data = result.to_dict()
        
        assert data["skill_id"] == "test/skill"
        assert data["valid"] is False
        assert data["quality_score"] == 0.6
        assert data["validated_at"] == "2023-01-01T00:00:00"
        assert len(data["issues"]) == 2
        assert data["error_count"] == 1
        assert data["warning_count"] == 1
        assert data["info_count"] == 0


class TestSkillValidator:
    """Test cases for SkillValidator class."""
    
    @pytest.fixture
    def validator(self):
        """Create a SkillValidator instance for testing."""
        return SkillValidator()
    
    @pytest.fixture
    def valid_skill_metadata(self):
        """Create a valid skill metadata for testing."""
        return SkillMetadata(
            name="Test Skill",
            domain="test",
            version="1.0.0",
            surfaces=["python", "prolog"],
            purpose="A test skill for validation",
            description="This is a test skill used in unit tests for the validator module.",
            dependencies=[],
            input_schema={},
            output_schema={},
            capabilities={},
            compatibility={},
            quality_thresholds={},
            metrics={},
            skill_id="test/test-skill",
            path="/fake/path/skill.md",
            schema_version=1,
            tags=["test", "skill"]
        )
    
    def test_initialization(self, validator):
        """Test SkillValidator initialization."""
        assert validator.logger is not None
        assert validator.min_purpose_length == 10
        assert validator.min_description_length == 20
        assert validator.min_code_lines == 5
        assert validator.ideal_surface_count == 3
        assert validator.min_surface_count == 1
        assert len(validator.valid_domains) > 0
    
    def test_validate_structure_missing_fields(self, validator):
        """Test structure validation with missing required fields."""
        # Create skill metadata with missing required fields
        skill_metadata = SkillMetadata(
            name="",  # Missing name (empty string)
            domain="",  # Missing domain (empty string)
            version="1.0.0",
            surfaces=["python"],
            purpose="Test",
            description="Test description",
            dependencies=[],
            input_schema={},
            output_schema={},
            capabilities={},
            compatibility={},
            quality_thresholds={},
            metrics={},
            skill_id="test/skill",
            path="/fake/path/skill.md",
            schema_version=1,
            tags=[]
        )
        
        # Mock file path
        file_path = Mock()
        file_path.read_text.return_value = ""
        
        result = validator.validate_skill_file(file_path, skill_metadata)
        
        # Should have errors for missing required fields
        assert not result.valid
        error_codes = [issue.code for issue in result.get_issues_by_severity(ValidationSeverity.ERROR)]
        assert "MISSING_REQUIRED_FIELD" in error_codes
        # Should have two errors (name and domain)
        assert len([c for c in error_codes if c == "MISSING_REQUIRED_FIELD"]) >= 2
    
    def test_validate_structure_short_purpose(self, validator, valid_skill_metadata):
        """Test structure validation with short purpose."""
        skill_metadata = valid_skill_metadata
        skill_metadata.purpose = "Short"  # Less than min_purpose_length (10)
        
        file_path = Mock()
        file_path.read_text.return_value = ""
        
        result = validator.validate_skill_file(file_path, skill_metadata)
        
        # Should have a warning for short purpose
        assert result.valid  # Warning doesn't invalidate
        warning_codes = [issue.code for issue in result.get_issues_by_severity(ValidationSeverity.WARNING)]
        assert "SHORT_PURPOSE" in warning_codes
    
    def test_validate_structure_short_description(self, validator, valid_skill_metadata):
        """Test structure validation with short description."""
        skill_metadata = valid_skill_metadata
        skill_metadata.description = "Too short"  # Less than min_description_length (20)
        
        file_path = Mock()
        file_path.read_text.return_value = ""
        
        result = validator.validate_skill_file(file_path, skill_metadata)
        
        # Should have a warning for short description
        assert result.valid  # Warning doesn't invalidate
        warning_codes = [issue.code for issue in result.get_issues_by_severity(ValidationSeverity.WARNING)]
        assert "SHORT_DESCRIPTION" in warning_codes
    
    def test_validate_metadata_invalid_version(self, validator, valid_skill_metadata):
        """Test metadata validation with invalid version."""
        skill_metadata = valid_skill_metadata
        skill_metadata.version = "invalid-version"
        
        file_path = Mock()
        file_path.read_text.return_value = ""
        
        result = validator.validate_skill_file(file_path, skill_metadata)
        
        # Should have a warning for invalid version
        assert result.valid  # Warning doesn't invalidate
        warning_codes = [issue.code for issue in result.get_issues_by_severity(ValidationSeverity.WARNING)]
        assert "INVALID_VERSION" in warning_codes
    
    def test_validate_metadata_unknown_domain(self, validator, valid_skill_metadata):
        """Test metadata validation with unknown domain."""
        skill_metadata = valid_skill_metadata
        skill_metadata.domain = "UnknownDomain"
        
        file_path = Mock()
        file_path.read_text.return_value = ""
        
        result = validator.validate_skill_file(file_path, skill_metadata)
        
        # Should have a warning for unknown domain
        assert result.valid  # Warning doesn't invalidate
        warning_codes = [issue.code for issue in result.get_issues_by_severity(ValidationSeverity.WARNING)]
        assert "UNKNOWN_DOMAIN" in warning_codes
    
    def test_validate_metadata_unknown_surface(self, validator, valid_skill_metadata):
        """Test metadata validation with unknown surface."""
        skill_metadata = valid_skill_metadata
        skill_metadata.surfaces = ["python", "unknown_surface"]
        
        file_path = Mock()
        file_path.read_text.return_value = ""
        
        result = validator.validate_skill_file(file_path, skill_metadata)
        
        # Should have an error for unknown surface
        assert not result.valid
        error_codes = [issue.code for issue in result.get_issues_by_severity(ValidationSeverity.ERROR)]
        assert "UNKNOWN_SURFACE" in error_codes
    
    def test_validate_metadata_insufficient_surfaces(self, validator, valid_skill_metadata):
        """Test metadata validation with insufficient surfaces."""
        skill_metadata = valid_skill_metadata
        skill_metadata.surfaces = []  # No surfaces
        
        file_path = Mock()
        file_path.read_text.return_value = ""
        
        result = validator.validate_skill_file(file_path, skill_metadata)
        
        # Should have an error for insufficient surfaces
        assert not result.valid
        error_codes = [issue.code for issue in result.get_issues_by_severity(ValidationSeverity.ERROR)]
        assert "INSUFFICIENT_SURFACES" in error_codes
    
    def test_validate_surfaces_invalid_surface(self, validator, valid_skill_metadata):
        """Test surface validation with invalid surface."""
        skill_metadata = valid_skill_metadata
        skill_metadata.surfaces = ["invalid_surface"]
        
        file_path = Mock()
        file_path.read_text.return_value = ""
        
        result = validator.validate_skill_file(file_path, skill_metadata)
        
        # Should have an error for invalid surface
        assert not result.valid
        error_codes = [issue.code for issue in result.get_issues_by_severity(ValidationSeverity.ERROR)]
        assert "INVALID_SURFACE" in error_codes
    
    def test_validate_dependencies_invalid_format(self, validator, valid_skill_metadata):
        """Test dependency validation with invalid format."""
        skill_metadata = valid_skill_metadata
        skill_metadata.dependencies = [
            # This dependency is missing a slash in skill_id
            # We'll create a mock dependency object
            Mock(skill_id="invalid_format", version_range=">=1.0.0", optional=False, description="Test")
        ]
        
        file_path = Mock()
        file_path.read_text.return_value = ""
        
        result = validator.validate_skill_file(file_path, skill_metadata)
        
        # Should have a warning for invalid dependency format
        assert result.valid  # Warning doesn't invalidate
        warning_codes = [issue.code for issue in result.get_issues_by_severity(ValidationSeverity.WARNING)]
        assert "INVALID_DEPENDENCY_FORMAT" in warning_codes
    
    def test_validate_dependencies_invalid_version_range(self, validator, valid_skill_metadata):
        """Test dependency validation with invalid version range."""
        skill_metadata = valid_skill_metadata
        skill_metadata.dependencies = [
            Mock(skill_id="valid/format", version_range="invalid-range", optional=False, description="Test")
        ]
        
        file_path = Mock()
        file_path.read_text.return_value = ""
        
        result = validator.validate_skill_file(file_path, skill_metadata)
        
        # Should have a warning for invalid version range
        assert result.valid  # Warning doesn't invalidate
        warning_codes = [issue.code for issue in result.get_issues_by_severity(ValidationSeverity.WARNING)]
        assert "INVALID_VERSION_RANGE" in warning_codes
    
    def test_validate_schemas_missing_required_property(self, validator, valid_skill_metadata):
        """Test schema validation with missing required property."""
        skill_metadata = valid_skill_metadata
        # Set up a schema with a required property that's not in properties
        skill_metadata.input_schema = Mock()
        skill_metadata.input_schema.properties = {"prop1": {"type": "string"}}
        skill_metadata.input_schema.required = ["prop1", "missing_prop"]  # missing_prop not in properties
        
        file_path = Mock()
        file_path.read_text.return_value = ""
        
        result = validator.validate_skill_file(file_path, skill_metadata)
        
        # Should have an error for missing required property
        assert not result.valid
        error_codes = [issue.code for issue in result.get_issues_by_severity(ValidationSeverity.ERROR)]
        assert "MISSING_REQUIRED_PROPERTY" in error_codes
    
    def test_calculate_quality_score(self, validator):
        """Test quality score calculation."""
        result = ValidationResult(
            skill_id="test/skill",
            valid=True,
            issues=[],
            quality_score=0.0,
            validated_at=""
        )
        
        # Start with perfect score
        # Deduct for errors (heavily)
        result.add_issue(ValidationSeverity.ERROR, "E1", "Error 1", "comp1")
        result.add_issue(ValidationSeverity.ERROR, "E2", "Error 2", "comp1")
        # Deduct for warnings
        result.add_issue(ValidationSeverity.WARNING, "W1", "Warning 1", "comp1")
        result.add_issue(ValidationSeverity.WARNING, "W2", "Warning 2", "comp1")
        result.add_issue(ValidationSeverity.WARNING, "W3", "Warning 3", "comp1")
        # Boost for good practices (none in this case)
        
        validator._calculate_quality_score(result)
        
        # Score should be: 1.0 - min(1.0, 2*0.5) - min(1.0, 3*0.1) = 1.0 - 1.0 - 0.3 = -0.3 -> clamped to 0.0
        assert result.quality_score == 0.0
        assert result.valid is False  # Because score < 0.3
    
    def test_calculate_quality_score_with_boosts(self, validator):
        """Test quality score calculation with boosts."""
        result = ValidationResult(
            skill_id="test/skill",
            valid=True,
            issues=[],
            quality_score=0.0,
            validated_at=""
        )
        
        # Add some issues
        result.add_issue(ValidationSeverity.ERROR, "E1", "Error 1", "comp1")
        result.add_issue(ValidationSeverity.WARNING, "W1", "Warning 1", "comp1")
        
        # Add boosts by adding issues with specific codes (the validator checks for these codes in _calculate_quality_score)
        # We'll simulate by adding issues with the boost codes
        result.add_issue(ValidationSeverity.INFO, "HAS_TESTS", "Has tests", "comp1")
        result.add_issue(ValidationSeverity.INFO, "HAS_EXAMPLES", "Has examples", "comp1")
        result.add_issue(ValidationSeverity.INFO, "HAS_DOCSTRINGS", "Has docstrings", "comp1")
        
        validator._calculate_quality_score(result)
        
        # Score: 1.0 - min(1.0, 1*0.5) - min(1.0, 1*0.1) + 0.1 + 0.1 + 0.1
        #       = 1.0 - 0.5 - 0.1 + 0.3 = 0.7
        assert result.quality_score == 0.7
        assert result.valid is False  # Still invalid due to the error issue
    
    def test_validate_composition_type_mismatch(self, validator):
        """Test composition validation with type mismatch."""
        source_skill = Mock()
        source_skill.skill_id = "source/skill"
        source_skill.output_schema = Mock()
        source_skill.output_schema.type = "string"
        
        target_skill = Mock()
        target_skill.skill_id = "target/skill"
        target_skill.input_schema = Mock()
        target_skill.input_schema.type = "object"
        target_skill.input_schema.properties = {}
        target_skill.input_schema.required = []
        
        result = validator.validate_composition(source_skill, target_skill)
        
        # Should have a warning for type mismatch
        assert result.valid  # Warning doesn't invalidate
        warning_codes = [issue.code for issue in result.get_issues_by_severity(ValidationSeverity.WARNING)]
        assert "TYPE_MISMATCH" in warning_codes
    
    def test_validate_composition_missing_required_field(self, validator):
        """Test composition validation with missing required field."""
        source_skill = Mock()
        source_skill.skill_id = "source/skill"
        source_skill.output_schema = Mock()
        source_skill.output_schema.type = "object"
        source_skill.output_schema.properties = {"existing_prop": {"type": "string"}}
        source_skill.output_schema.required = ["existing_prop"]
        
        target_skill = Mock()
        target_skill.skill_id = "target/skill"
        target_skill.input_schema = Mock()
        target_skill.input_schema.type = "object"
        target_skill.input_schema.properties = {}  # Empty properties
        target_skill.input_schema.required = ["missing_prop"]  # Required but not in source
        
        result = validator.validate_composition(source_skill, target_skill)
        
        # Should have an error for missing required field
        assert not result.valid
        error_codes = [issue.code for issue in result.get_issues_by_severity(ValidationSeverity.ERROR)]
        assert "MISSING_REQUIRED_FIELD" in error_codes


if __name__ == "__main__":
    pytest.main([__file__])