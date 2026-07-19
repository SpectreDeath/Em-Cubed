"""Extended skill metadata schema with validation.

This module provides the SkillMetadata class that extends the basic SKILL.md
frontmatter with comprehensive schema definitions for skill composition,
dependency management, and quality tracking.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path


@dataclass
class InputOutputSchema:
    """Schema definitions for skill inputs and outputs."""
    type: str = "object"  # object, array, string, number, boolean, null
    properties: Dict[str, Any] = field(default_factory=dict)
    required: List[str] = field(default_factory=list)
    additional_properties: bool = True
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        res = {
            "type": self.type,
            "properties": self.properties,
            "required": self.required,
            "additionalProperties": self.additional_properties,
        }
        if self.description is not None:
            res["description"] = self.description
        return res

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InputOutputSchema":
        """Construct from dictionary."""
        return cls(
            type=data.get("type", "object"),
            properties=data.get("properties", {}),
            required=data.get("required", []),
            additional_properties=data.get("additionalProperties", True),
            description=data.get("description"),
        )


@dataclass
class SkillCapability:
    """Required capabilities for skill execution."""
    surfaces: List[str] = field(default_factory=list)  # Required surface plugins
    permissions: List[str] = field(default_factory=list)  # Required permissions/privileges
    resources: Dict[str, Any] = field(default_factory=dict)  # Resource requirements (memory, cpu, etc.)
    external_services: List[str] = field(default_factory=list)  # External API/service dependencies

    def to_dict(self) -> Dict[str, Any]:
        return {
            "surfaces": self.surfaces,
            "permissions": self.permissions,
            "resources": self.resources,
            "external_services": self.external_services,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillCapability":
        return cls(
            surfaces=data.get("surfaces", []),
            permissions=data.get("permissions", []),
            resources=data.get("resources", {}),
            external_services=data.get("external_services", []),
        )


@dataclass
class CompatibilityRange:
    """Version compatibility constraints."""
    min_version: str = "0.1.0"
    max_version: Optional[str] = None  # Exclusive upper bound
    breaking_changes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "min_version": self.min_version,
            "max_version": self.max_version,
            "breaking_changes": self.breaking_changes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompatibilityRange":
        return cls(
            min_version=data.get("min_version", "0.1.0"),
            max_version=data.get("max_version"),
            breaking_changes=data.get("breaking_changes", []),
        )


@dataclass
class QualityThresholds:
    """Minimum quality thresholds for skill validation."""
    min_test_coverage: float = 0.8  # 80% code coverage
    min_success_rate: float = 0.7  # 70% execution success
    max_execution_time: float = 30.0  # seconds
    max_memory_usage: int = 512 * 1024 * 1024  # 512 MB
    required_surfaces: int = 1  # At least 1 surface implementation
    min_documentation_ratio: float = 0.3  # Documentation/comments vs code ratio

    def to_dict(self) -> Dict[str, Any]:
        return {
            "min_test_coverage": self.min_test_coverage,
            "min_success_rate": self.min_success_rate,
            "max_execution_time": self.max_execution_time,
            "max_memory_usage": self.max_memory_usage,
            "required_surfaces": self.required_surfaces,
            "min_documentation_ratio": self.min_documentation_ratio,
        }


@dataclass
class SkillDependency:
    """Dependency on another skill."""
    skill_id: str  # Unique skill identifier (domain/skill-name)
    version_range: str = ">=0.1.0"  # Semver range: defaults to any >=0.1.0
    optional: bool = False
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "version_range": self.version_range,
            "optional": self.optional,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillDependency":
        return cls(
            skill_id=data["skill_id"],
            version_range=data.get("version_range", ">=0.1.0"),
            optional=data.get("optional", False),
            description=data.get("description"),
        )


@dataclass
class RuntimeMetrics:
    """Runtime execution metrics for quality tracking."""
    applied_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_execution_time: float = 0.0  # seconds
    total_token_usage: int = 0
    last_executed: Optional[datetime] = None
    execution_history: List[Dict[str, Any]] = field(default_factory=list)
    performance_history: List[float] = field(default_factory=list)  # Success rates over time

    @property
    def completion_rate(self) -> float:
        """Calculate completion (success) rate."""
        if self.applied_count == 0:
            return 0.0
        return self.success_count / self.applied_count

    @property
    def avg_execution_time(self) -> float:
        """Calculate average execution time."""
        if self.success_count == 0:
            return 0.0
        return self.total_execution_time / self.success_count

    @property
    def avg_token_savings(self) -> float:
        """Calculate average token savings."""
        if self.applied_count == 0:
            return 0.0
        return self.total_token_usage / self.applied_count

    def record_execution(self, success: bool, execution_time: float, token_usage: int = 0) -> None:
        """Record a skill execution."""
        self.applied_count += 1
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        self.total_execution_time += execution_time
        self.total_token_usage += token_usage
        self.last_executed = datetime.utcnow()
        self.execution_history.append({
            "timestamp": self.last_executed.isoformat(),
            "success": success,
            "execution_time": execution_time,
            "token_usage": token_usage,
        })
        # Keep last 100 executions
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
        # Update performance history (rolling window of last 20)
        window = self.execution_history[-20:]
        if window:
            window_success = sum(1 for e in window if e["success"]) / len(window)
            self.performance_history.append(window_success)
            if len(self.performance_history) > 100:
                self.performance_history = self.performance_history[-100:]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "applied_count": self.applied_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "completion_rate": self.completion_rate,
            "total_execution_time": self.total_execution_time,
            "avg_execution_time": self.avg_execution_time,
            "total_token_usage": self.total_token_usage,
            "avg_token_savings": self.avg_token_savings,
            "last_executed": self.last_executed.isoformat() if self.last_executed else None,
            "recent_performance": self.performance_history[-10:] if self.performance_history else [],
        }


@dataclass
class SkillMetadata:
    """Extended skill metadata with full schema support."""
    # Core fields (from SKILL.md frontmatter)
    name: str
    domain: str
    version: str = "0.1.0"
    surfaces: List[str] = field(default_factory=list)
    purpose: Optional[str] = None
    description: Optional[str] = None

    # Extended fields
    dependencies: List[SkillDependency] = field(default_factory=list)
    input_schema: InputOutputSchema = field(default_factory=InputOutputSchema)
    output_schema: InputOutputSchema = field(default_factory=InputOutputSchema)
    capabilities: SkillCapability = field(default_factory=SkillCapability)
    compatibility: CompatibilityRange = field(default_factory=CompatibilityRange)
    quality_thresholds: QualityThresholds = field(default_factory=QualityThresholds)

    # Runtime metrics
    metrics: RuntimeMetrics = field(default_factory=RuntimeMetrics)

    # File/registry metadata
    skill_id: Optional[str] = None  # Computed: domain/name
    path: Optional[str] = None
    schema_version: int = 1
    tags: List[str] = field(default_factory=list)  # Derived from code analysis
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @staticmethod
    def _slugify(text: str) -> str:
        """Slugify text for consistent IDs."""
        import re
        # Lowercase
        text = text.lower()
        # Replace spaces, underscores and periods with hyphens
        text = re.sub(r'[\s_.]+', '-', text)
        # Remove non-alphanumeric (except hyphens)
        text = re.sub(r'[^a-z0-9\-]', '', text)
        # Remove leading/trailing hyphens
        text = text.strip('-')
        return text

    def __post_init__(self):
        """Compute derived fields after initialization."""
        if isinstance(self.input_schema, dict):
            self.input_schema = InputOutputSchema.from_dict(self.input_schema)
        if isinstance(self.output_schema, dict):
            self.output_schema = InputOutputSchema.from_dict(self.output_schema)
        if isinstance(self.capabilities, dict):
            self.capabilities = SkillCapability.from_dict(self.capabilities)
        if isinstance(self.compatibility, dict):
            self.compatibility = CompatibilityRange.from_dict(self.compatibility)
        if isinstance(self.quality_thresholds, dict):
            self.quality_thresholds = QualityThresholds(
                min_test_coverage=self.quality_thresholds.get("min_test_coverage", 0.8),
                min_success_rate=self.quality_thresholds.get("min_success_rate", 0.7),
                max_execution_time=self.quality_thresholds.get("max_execution_time", 30.0),
                max_memory_usage=self.quality_thresholds.get("max_memory_usage", 512*1024*1024),
                required_surfaces=self.quality_thresholds.get("required_surfaces", 1),
                min_documentation_ratio=self.quality_thresholds.get("min_documentation_ratio", 0.3),
            )
        if isinstance(self.metrics, dict):
            self.metrics = RuntimeMetrics()
            quality_data = self.metrics
            if isinstance(quality_data, dict):
                self.metrics.applied_count = quality_data.get("applied_count", 0)
                self.metrics.success_count = quality_data.get("success_count", 0)
                self.metrics.total_token_usage = quality_data.get("token_savings_avg", 0.0) * self.metrics.applied_count if self.metrics.applied_count > 0 else 0

        if self.skill_id is None:
            # Use slugified components for internal ID
            slug_domain = self._slugify(self.domain)
            slug_name = self._slugify(self.name)
            self.skill_id = f"{slug_domain}/{slug_name}"

    @staticmethod
    def _extract_surfaces_from_body(body: str) -> List[str]:
        """Detect which surfaces are implemented by scanning fenced code blocks."""
        import re
        surfaces = []
        # Pattern: ```lang or ````lang
        for match in re.finditer(r"`{3,}(\w+)\s*\r?\n", body):
            lang = match.group(1).lower()
            if lang in ("python", "py"):
                surfaces.append("python")
            elif lang == "prolog":
                surfaces.append("prolog")
            elif lang == "hy":
                surfaces.append("hy")
            elif lang in ("z3", "z3-smt2"):
                surfaces.append("z3")
            elif lang in ("datalog", "pyDatalog"):
                surfaces.append("datalog")
            elif lang in ("sql", "sqlite"):
                surfaces.append("sqlite")
            elif lang in ("js", "javascript", "quickjs"):
                surfaces.append("quickjs")
            elif lang in ("kanren", "kan"):
                surfaces.append("kanren")
            elif lang in ("clingo", "asp"):
                surfaces.append("clingo")
        # Deduplicate preserving order
        return list(dict.fromkeys(surfaces))

    @staticmethod
    def _extract_tags_from_body(body: str) -> List[str]:
        """Extract tags from code blocks."""
        import re
        tags = []
        # Python function names
        for match in re.finditer(r"^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", body, re.MULTILINE):
            tags.append(match.group(1))
        # Prolog predicates
        for match in re.finditer(r"^([a-z][a-zA-Z0-9_]*)\s*[.(]", body, re.MULTILINE):
            pred = match.group(1)
            if pred not in {"not", "is", "true", "fail"}:
                tags.append(pred)
        # Hy functions
        for match in re.finditer(r"\(defn\s+([a-zA-Z][a-zA-Z0-9_\-?!]*)", body):
            tags.append(match.group(1))
        # Kanren relations/goals
        for match in re.finditer(r"(?:def|relational_fact|relation)\s+([a-zA-Z][a-zA-Z0-9_]*)", body):
            tags.append(match.group(1))
        # Clingo atoms/predicates
        for match in re.finditer(r"\b([a-z][a-zA-Z0-9_]*)\s*\(", body):
            pred = match.group(1)
            if pred not in {"not", "is", "true", "fail", "show"}:
                tags.append(pred)
        return list(dict.fromkeys(tags))

    @property
    def unique_id(self) -> str:
        """Get unique identifier for this skill."""
        slug_domain = self._slugify(self.domain)
        slug_name = self._slugify(self.name)
        return f"{slug_domain}/{slug_name}@{self.version}"

    def check_compatibility(self, other_version: str) -> bool:
        """Check if another skill version is compatible with this one."""
        from packaging import version
        v_other = version.parse(other_version)
        min_v = version.parse(self.compatibility.min_version)
        max_v = version.parse(self.compatibility.max_version) if self.compatibility.max_version else None

        if v_other < min_v:
            return False
        if max_v and v_other >= max_v:
            return False
        return True

    def to_registry_dict(self) -> Dict[str, Any]:
        """Convert to registry JSON-compatible dict."""
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "domain": self.domain,
            "version": self.version,
            "surfaces": self.surfaces,
            "purpose": self.purpose,
            "description": self.description,
            "dependencies": [d.to_dict() for d in self.dependencies],
            "input_schema": self.input_schema.to_dict(),
            "output_schema": self.output_schema.to_dict(),
            "capabilities": self.capabilities.to_dict(),
            "compatibility": self.compatibility.to_dict(),
            "quality_thresholds": self.quality_thresholds.to_dict(),
            "tags": self.tags,
            "path": self.path,
            "schema_version": self.schema_version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metrics": self.metrics.to_dict(),
        }

    @classmethod
    def from_frontmatter(cls, frontmatter: Dict[str, Any], body: str = "", file_path: Optional[Path] = None) -> "SkillMetadata":
        """Construct SkillMetadata from SKILL.md frontmatter."""
        import re

        # Extract surfaces from code blocks in body, merged with explicit frontmatter
        # Frontmatter declarations take precedence; body detection supplements with
        # any additionally detected surfaces (e.g. sqlite from a sqlite fence).
        code_surfaces = cls._extract_surfaces_from_body(body)
        fm_surfaces = frontmatter.get("surfaces", [])
        # Merge with frontmatter-first ordering (deduplicates)
        surfaces = list(dict.fromkeys(fm_surfaces + code_surfaces))
        if not surfaces:
            surfaces = ["python"]  # sensible default

        # Extract tags from code blocks
        tags = cls._extract_tags_from_body(body)
        if not tags:
            tags = frontmatter.get("tags", [])

        # Extract purpose and description from body if not in frontmatter
        purpose = frontmatter.get("purpose", "")
        if not purpose:
            purpose_match = re.search(r"## Purpose\s*\n\s*(.+)", body)
            if purpose_match:
                purpose = purpose_match.group(1).strip()

        description = frontmatter.get("description", "")
        if not description:
            desc_match = re.search(r"## Description\s*\n\s*(.+)", body)
            if desc_match:
                description = desc_match.group(1).strip()
        # If description is still empty, fall back to purpose
        if not description and purpose:
            description = purpose

        # Parse extended fields...
        # [rest unchanged]
        deps = []
        for dep_data in frontmatter.get("dependencies", []):
            if isinstance(dep_data, str):
                deps.append(SkillDependency(skill_id=dep_data, version_range=">=0.1.0"))
            elif isinstance(dep_data, dict):
                deps.append(SkillDependency.from_dict(dep_data))

        # Parse input/output schemas
        input_schema = InputOutputSchema.from_dict(frontmatter.get("input_schema", {}))
        output_schema = InputOutputSchema.from_dict(frontmatter.get("output_schema", {}))

        # Parse capabilities
        capabilities = SkillCapability.from_dict(frontmatter.get("capabilities", {}))

        # Parse compatibility
        compatibility_raw = frontmatter.get("compatibility", {})
        if isinstance(compatibility_raw, str):
            compatibility_raw = {"description": compatibility_raw}
        compatibility = CompatibilityRange.from_dict(compatibility_raw)

        # Parse quality thresholds
        thresholds_data = frontmatter.get("quality_thresholds", {})
        quality_thresholds = QualityThresholds(
            min_test_coverage=thresholds_data.get("min_test_coverage", 0.8),
            min_success_rate=thresholds_data.get("min_success_rate", 0.7),
            max_execution_time=thresholds_data.get("max_execution_time", 30.0),
            max_memory_usage=thresholds_data.get("max_memory_usage", 512*1024*1024),
            required_surfaces=thresholds_data.get("required_surfaces", 1),
            min_documentation_ratio=thresholds_data.get("min_documentation_ratio", 0.3),
        )

        # Extract metrics from frontmatter quality fields (existing format)
        metrics = RuntimeMetrics()
        quality_data = frontmatter.get("quality", {})
        if quality_data:
            metrics.applied_count = quality_data.get("applied_count", 0)
            metrics.success_count = quality_data.get("success_count", 0)
            # completion_rate is computed property, not stored directly
            # Set token usage: token_savings_avg * applied_count
            metrics.total_token_usage = quality_data.get("token_savings_avg", 0.0) * metrics.applied_count if metrics.applied_count > 0 else 0

        # Build metadata
        # Store path relative to cwd for portability, fallback to absolute
        if file_path:
            try:
                file_path_str = str(file_path.relative_to(Path.cwd()))
            except ValueError:
                file_path_str = str(file_path.resolve())
        else:
            file_path_str = None

        return cls(
            name=frontmatter.get("name", frontmatter.get("Name", file_path.parent.name if file_path else "Unknown")),
            domain=frontmatter.get("domain", frontmatter.get("Domain", "General")),
            version=frontmatter.get("version", frontmatter.get("Version", "0.1.0")),
            surfaces=surfaces,
            purpose=purpose,
            description=description,
            dependencies=deps,
            input_schema=input_schema,
            output_schema=output_schema,
            capabilities=capabilities,
            compatibility=compatibility,
            quality_thresholds=quality_thresholds,
            metrics=metrics,
            skill_id=None,  # Computed in __post_init__
            path=file_path_str,
            schema_version=frontmatter.get("schema_version", frontmatter.get("Schema_Version", 1)),
            tags=tags,  # Use detected tags from code blocks
            created_at=datetime.fromisoformat(frontmatter["created_at"]) if frontmatter.get("created_at") else None,
            updated_at=datetime.fromisoformat(frontmatter["updated_at"]) if frontmatter.get("updated_at") else None,
        )
