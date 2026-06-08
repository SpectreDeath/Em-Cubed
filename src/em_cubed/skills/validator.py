"""Skill validation framework for enforcing quality standards.

Provides validation for skill structure, content quality, code correctness,
surface implementations, and composition readiness.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import structlog

logger = structlog.get_logger()


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    ERROR = "error"      # Skill fails validation entirely
    WARNING = "warning"  # Skill passes but has issues
    INFO = "info"        # Informational suggestions
    SUCCESS = "success"  # Validation passed


@dataclass
class ValidationIssue:
    """A single validation issue found."""
    severity: ValidationSeverity
    code: str  # Unique issue code (e.g., MISSING_PURPOSE, NO_TESTS)
    message: str
    component: str  # Which part failed (metadata, python, prolog, hy)
    suggestion: Optional[str] = None
    line_number: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity.value,
            "code": self.code,
            "message": self.message,
            "component": self.component,
            "suggestion": self.suggestion,
            "line_number": self.line_number,
        }


@dataclass
class ValidationResult:
    """Complete validation result for a skill."""
    skill_id: str
    valid: bool  # Overall pass/fail
    issues: List[ValidationIssue] = field(default_factory=list)
    quality_score: float = 0.0  # 0.0 to 1.0
    validated_at: str = ""  # ISO timestamp

    def add_issue(self, severity: ValidationSeverity, code: str, message: str,
                  component: str = "general", suggestion: Optional[str] = None,
                  line_number: Optional[int] = None) -> None:
        """Add a validation issue."""
        self.issues.append(ValidationIssue(
            severity=severity,
            code=code,
            message=message,
            component=component,
            suggestion=suggestion,
            line_number=line_number,
        ))
        if severity in (ValidationSeverity.ERROR,):
            self.valid = False

    def get_issues_by_severity(self, severity: ValidationSeverity) -> List[ValidationIssue]:
        """Get all issues of a given severity."""
        return [i for i in self.issues if i.severity == severity]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "valid": self.valid,
            "quality_score": self.quality_score,
            "validated_at": self.validated_at,
            "issues": [i.to_dict() for i in self.issues],
            "error_count": len(self.get_issues_by_severity(ValidationSeverity.ERROR)),
            "warning_count": len(self.get_issues_by_severity(ValidationSeverity.WARNING)),
            "info_count": len(self.get_issues_by_severity(ValidationSeverity.INFO)),
        }


class SkillValidator:
    """Validate skills across structure, content, and implementation dimensions."""

    # Required frontmatter fields for a minimal valid skill
    REQUIRED_FIELDS = {"name", "Domain"}

    # Default fallback values (will be overridden by manifest)
    DEFAULT_MIN_PURPOSE_LENGTH = 10
    DEFAULT_MIN_DESCRIPTION_LENGTH = 20
    DEFAULT_MIN_CODE_LINES = 5
    DEFAULT_IDEAL_SURFACE_COUNT = 3  # python, prolog, hy
    DEFAULT_MIN_SURFACE_COUNT = 1

    def __init__(self):
        self.logger = logger.bind(component="skill_validator")
        # Initialize with defaults
        self.min_purpose_length = self.DEFAULT_MIN_PURPOSE_LENGTH
        self.min_description_length = self.DEFAULT_MIN_DESCRIPTION_LENGTH
        self.min_code_lines = self.DEFAULT_MIN_CODE_LINES
        self.ideal_surface_count = self.DEFAULT_IDEAL_SURFACE_COUNT
        self.min_surface_count = self.DEFAULT_MIN_SURFACE_COUNT
        self._load_manifest()

    def _load_manifest(self):
        """Load manifest.yaml to get valid domains and quality thresholds."""
        from pathlib import Path
        try:
            import yaml
        except ImportError:
            yaml = None

        manifest_path = Path("skills") / "manifest.yaml"
        # Default fallback domains (hardcoded)
        self.valid_domains = {
            "AUTOMATION", "DATA_PROCESSING", "DECISION_MAKING", "DISTRIBUTED_SYSTEMS",
            "ENSEMBLE", "EPIDEMIOLOGY", "FEATURE_ENGINEERING", "General", "GRAPH_ML", "KNOWLEDGE_GRAPH",
            "MACHINE_LEARNING", "ML_OPERATIONS", "MODEL_VALIDATION", "NLP",
            "OPTIMIZATION", "RECOMMENDER_SYSTEMS", "RESOURCE_MANAGEMENT",
            "SIMULATION", "STATISTICS", "FORENSIC_ECONOMICS", "CLINICAL_TRIALS", "TIME_SERIES"
        }
        self.default_required_surfaces = 1

        if not manifest_path.exists():
            self.logger.debug("manifest.yaml not found, using defaults", path=str(manifest_path))
            return

        try:
            with open(manifest_path) as f:
                manifest = yaml.safe_load(f) if yaml else {}
            # skill_categories -> valid domains
            categories = manifest.get("skill_categories", [])
            if categories:
                self.valid_domains = set(categories)
            # quality_thresholds -> may override defaults
            qt = manifest.get("quality_thresholds", {})
            if "required_surfaces" in qt:
                self.default_required_surfaces = qt["required_surfaces"]
            if "min_purpose_length" in qt:
                self.min_purpose_length = qt["min_purpose_length"]
            if "min_description_length" in qt:
                self.min_description_length = qt["min_description_length"]
            if "min_code_lines" in qt:
                self.min_code_lines = qt["min_code_lines"]
            self.logger.info("Loaded manifest", domains_count=len(self.valid_domains), required_surfaces=self.default_required_surfaces)
        except Exception as e:
            self.logger.warning("Failed to parse manifest, using defaults", error=str(e))

    def validate_skill_file(self, file_path, skill_metadata) -> ValidationResult:
        """Perform comprehensive validation on a skill file."""
        from datetime import datetime

        result = ValidationResult(
            skill_id=skill_metadata.skill_id or skill_metadata.name,
            valid=True,
            issues=[],
            quality_score=0.0,
            validated_at=datetime.utcnow().isoformat(),
        )

        # Run all validation checks
        self._validate_structure(result, file_path, skill_metadata)
        self._validate_metadata(result, skill_metadata)
        self._validate_surfaces(result, skill_metadata)
        self._validate_dependencies(result, skill_metadata)
        self._validate_schemas(result, skill_metadata)
        self._calculate_quality_score(result)

        return result

    def _validate_structure(self, result: ValidationResult, file_path, skill_metadata) -> None:
        """Validate basic file structure and presence of required sections."""
        # Read content for any needed checks (currently just structure validation via metadata)
        _ = file_path.read_text(encoding="utf-8")

        # Check frontmatter completeness
        for required_field in self.REQUIRED_FIELDS:
            value = getattr(skill_metadata, required_field.lower(), None)
            if not value:
                result.add_issue(
                    severity=ValidationSeverity.ERROR,
                    code="MISSING_REQUIRED_FIELD",
                    message=f"Required field '{required_field}' is missing",
                    component="metadata",
                    suggestion=f"Add '{required_field}: value' to the YAML frontmatter"
                )

        # Check Purpose section
        if not skill_metadata.purpose or len(skill_metadata.purpose) < self.min_purpose_length:
            result.add_issue(
                severity=ValidationSeverity.WARNING,
                code="SHORT_PURPOSE",
                message=f"Purpose should be at least {self.min_purpose_length} characters",
                component="content",
                suggestion="Expand the skill's Purpose section with more detail"
            )

        # Check Description section
        if not skill_metadata.description or len(skill_metadata.description) < self.min_description_length:
            result.add_issue(
                severity=ValidationSeverity.WARNING,
                code="SHORT_DESCRIPTION",
                message=f"Description should be at least {self.min_description_length} characters",
                component="content",
                suggestion="Provide a more comprehensive description"
            )

    def _validate_metadata(self, result: ValidationResult, skill_metadata) -> None:
        """Validate metadata consistency and quality."""
        # Validate version format (semver)
        import re
        semver_pattern = r'^\d+\.\d+\.\d+$'
        if not re.match(semver_pattern, skill_metadata.version):
            result.add_issue(
                severity=ValidationSeverity.WARNING,
                code="INVALID_VERSION",
                message=f"Version should follow semantic versioning (X.Y.Z), got '{skill_metadata.version}'",
                component="metadata",
                suggestion="Update version to follow semver (e.g., 1.0.0)"
            )

        # Validate domain against manifest categories
        if skill_metadata.domain not in self.valid_domains:
            result.add_issue(
                severity=ValidationSeverity.WARNING,
                code="UNKNOWN_DOMAIN",
                message=f"Domain '{skill_metadata.domain}' is not in the recognized domains list",
                component="metadata",
                suggestion=f"Use one of: {', '.join(sorted(self.valid_domains))}"
            )

        # Validate surfaces
        valid_surfaces = {"python", "prolog", "hy", "z3", "datalog", "sqlite", "quickjs", "kanren", "clingo"}
        for surface in skill_metadata.surfaces:
            if surface not in valid_surfaces:
                result.add_issue(
                    severity=ValidationSeverity.ERROR,
                    code="UNKNOWN_SURFACE",
                    message=f"Surface '{surface}' is not supported",
                    component="metadata",
                    suggestion=f"Use one of: {', '.join(sorted(valid_surfaces))}"
                )

        # Check minimum surface count
        if len(skill_metadata.surfaces) < self.default_required_surfaces:
            result.add_issue(
                severity=ValidationSeverity.ERROR,
                code="INSUFFICIENT_SURFACES",
                message=f"Skill must implement at least {self.default_required_surfaces} surface(s), has {len(skill_metadata.surfaces)}",
                component="metadata",
                suggestion="Add implementations for missing surfaces (python, prolog, hy)"
            )

    def _validate_surfaces(self, result: ValidationResult, skill_metadata) -> None:
        """Validate each surface implementation for correctness."""
        # Read the skill file to extract code blocks
        # This is a simplified version - full validation would read and parse code
        for surface in skill_metadata.surfaces:
            # Check if surface is declared but likely not implemented (empty code block)
            self._validate_surface_implementation(result, skill_metadata, surface)

    def _validate_surface_implementation(self, result: ValidationResult, skill_metadata, surface: str) -> None:
        """Validate a specific surface implementation."""
        # Placeholder - actual implementation would read SKILL.md and verify code blocks
        # For now, we check basic naming conventions
        if surface not in ["python", "prolog", "hy", "z3", "datalog", "sqlite", "quickjs", "kanren", "clingo"]:
            result.add_issue(
                severity=ValidationSeverity.ERROR,
                code="INVALID_SURFACE",
                message=f"Surface '{surface}' is not a valid surface type",
                component="metadata",
                suggestion="Use python, prolog, hy, z3, datalog, sqlite, quickjs, kanren, or clingo"
            )

    def _validate_dependencies(self, result: ValidationResult, skill_metadata) -> None:
        """Validate skill dependencies."""

        for dep in skill_metadata.dependencies:
            # Check dependency skill_id format (domain/name)
            if "/" not in dep.skill_id:
                result.add_issue(
                    severity=ValidationSeverity.WARNING,
                    code="INVALID_DEPENDENCY_FORMAT",
                    message=f"Dependency '{dep.skill_id}' should be in format 'domain/skill-name'",
                    component="dependencies"
                )

            # Validate version range format
            if dep.version_range:
                import re
                # Simple semver range validation
                if not re.match(r'^[><=!]=?\d+\.\d+\.\d+(\s*,\s*[><=!]=?\d+\.\d+\.\d+)*$', dep.version_range):
                    result.add_issue(
                        severity=ValidationSeverity.WARNING,
                        code="INVALID_VERSION_RANGE",
                        message=f"Dependency version range '{dep.version_range}' is invalid",
                        component="dependencies",
                        suggestion="Use semver ranges like '>=1.0.0,<2.0.0'"
                    )

    def _validate_schemas(self, result: ValidationResult, skill_metadata) -> None:
        """Validate input/output JSON schemas."""
        # Validate input schema basics
        if skill_metadata.input_schema.properties:
            # Check property names are valid
            for prop_name in skill_metadata.input_schema.properties:
                if not prop_name.isidentifier():
                    result.add_issue(
                        severity=ValidationSeverity.WARNING,
                        code="INVALID_PROPERTY_NAME",
                        message=f"Property name '{prop_name}' is not a valid identifier",
                        component="schema"
                    )

        # Check required properties exist in properties
        for req in skill_metadata.input_schema.required:
            if req not in skill_metadata.input_schema.properties:
                result.add_issue(
                    severity=ValidationSeverity.ERROR,
                    code="MISSING_REQUIRED_PROPERTY",
                    message=f"Required property '{req}' not defined in schema properties",
                    component="schema"
                )

    def _calculate_quality_score(self, result: ValidationResult) -> None:
        """Calculate overall quality score 0-1 based on validation results."""
        # Start with perfect score
        score = 1.0

        # Deduct for errors (heavily)
        error_count = len(result.get_issues_by_severity(ValidationSeverity.ERROR))
        score -= min(1.0, error_count * 0.5)

        # Deduct for warnings
        warning_count = len(result.get_issues_by_severity(ValidationSeverity.WARNING))
        score -= min(1.0, warning_count * 0.1)

        # Boost for good practices
        if any(i.code == "HAS_TESTS" for i in result.issues):
            score += 0.1
        if any(i.code == "HAS_EXAMPLES" for i in result.issues):
            score += 0.1
        if any(i.code == "HAS_DOCSTRINGS" for i in result.issues):
            score += 0.1

        result.quality_score = max(0.0, min(1.0, score))
        result.valid = result.valid and score >= 0.3  # Minimum quality threshold

    def validate_composition(self, source_skill, target_skill) -> ValidationResult:
        """Validate that two skills can be composed (source output compatible with target input)."""
        result = ValidationResult(
            skill_id=f"{source_skill.skill_id}->{target_skill.skill_id}",
            valid=True,
            issues=[],
            quality_score=0.0,
            validated_at="",
        )

        # Check type compatibility
        src_out = source_skill.output_schema
        tgt_in = target_skill.input_schema

        if src_out.type != tgt_in.type and src_out.type != "any" and tgt_in.type != "any":
            result.add_issue(
                severity=ValidationSeverity.WARNING,
                code="TYPE_MISMATCH",
                message=f"Output type '{src_out.type}' may not match input type '{tgt_in.type}'",
                component="composition"
            )

        # Check required fields
        for req_field in tgt_in.required:
            if req_field not in src_out.properties:
                result.add_issue(
                    severity=ValidationSeverity.ERROR,
                    code="MISSING_REQUIRED_FIELD",
                    message=f"Target requires '{req_field}' but source doesn't provide it",
                    component="composition"
                )

        return result
