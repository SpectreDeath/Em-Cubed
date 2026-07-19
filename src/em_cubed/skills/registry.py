"""Enhanced skill registry with quality metrics, telemetry, and remote federation.

This registry extends the basic skill index with quality tracking, performance
benchmarks, usage analytics, composition relationships, and remote skill discovery.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from pathlib import Path
import json
import structlog
from datetime import datetime
from collections import defaultdict
import os
import uuid
import sqlite3
from abc import ABC, abstractmethod

from .metadata import SkillMetadata, RuntimeMetrics

if TYPE_CHECKING:
    from .remote_registry import RemoteSkillRegistry

logger = structlog.get_logger()

# Current schema version for registry entries
CURRENT_SCHEMA_VERSION = 1


@dataclass
class QualityMetrics:
    """Aggregated quality metrics for a skill."""
    skill_id: str
    validation_score: float = 0.0  # From validator
    test_coverage: float = 0.0  # Percentage
    success_rate: float = 0.0  # Runtime success rate
    avg_execution_time: float = 0.0
    avg_token_savings: float = 0.0
    usage_count: int = 0
    last_validation: Optional[datetime] = None
    last_execution: Optional[datetime] = None
    issues: List[Dict[str, Any]] = field(default_factory=list)  # Validation issues
    benchmarks: Dict[str, float] = field(default_factory=dict)  # performance benchmarks

    def meets_thresholds(self, thresholds) -> bool:
        """Check if metrics meet quality thresholds."""
        if self.validation_score < 0.7:
            return False
        if self.test_coverage < thresholds.min_test_coverage:
            return False
        if self.success_rate < thresholds.min_success_rate:
            return False
        if self.avg_execution_time > thresholds.max_execution_time:
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "validation_score": self.validation_score,
            "test_coverage": self.test_coverage,
            "success_rate": self.success_rate,
            "avg_execution_time": self.avg_execution_time,
            "avg_token_savings": self.avg_token_savings,
            "usage_count": self.usage_count,
            "last_validation": self.last_validation.isoformat() if self.last_validation else None,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "issues": self.issues,
            "benchmarks": self.benchmarks,
        }


@dataclass
class CompositionEdge:
    """Represents a skill composition relationship."""
    source_skill_id: str
    target_skill_id: str
    compatibility_score: float  # 0-1 based on schema compatibility
    data_transformation: Optional[str] = None  # Transformation needed between skills
    common_patterns: List[str] = field(default_factory=list)  # Shared use cases

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source_skill_id,
            "target": self.target_skill_id,
            "compatibility_score": self.compatibility_score,
            "data_transformation": self.data_transformation,
            "common_patterns": self.common_patterns,
        }


class SkillRegistry:
    """Enhanced skill registry with quality tracking, telemetry, and remote federation."""

    def __init__(self, skills_dir: Path, registry_file: Path, storage: Optional[RegistryStorage] = None):
        self.skills_dir = skills_dir
        self.registry_file = registry_file
        self.logger = logger.bind(component="skill_registry")
        self.storage = storage or JSONFileRegistryStorage(registry_file)
        self._skills: Dict[str, SkillMetadata] = {}
        self._quality_metrics: Dict[str, QualityMetrics] = {}
        self._composition_graph: Dict[str, List[CompositionEdge]] = defaultdict(list)
        # Remote registry federation
        self._remote_registry_manager: Optional[RemoteSkillRegistry] = None
        self._remote_skill_cache: Dict[str, List[SkillMetadata]] = {}  # Cache for discovered skills
        
        self._load_registry()
        
        # Initialize remote registry if configured
        self._initialize_remote_registry()

    def _initialize_remote_registry(self):
        """Initialize remote registry federation from environment configuration."""
        # Check if remote registry is enabled via environment variable
        if os.getenv("EM_CUBED_REMOTE_REGISTRY_ENABLED", "false").lower() == "true":
            # The remote registry manager will be initialized externally and set via setter
            # For now, we'll just note that remote registry is expected to be configured
            self.logger.info("Remote registry federation enabled (will be configured externally)")
        else:
            self.logger.debug("Remote registry federation disabled")

    def set_remote_registry_manager(self, manager):
        """Set the remote registry manager for federation.
        
        Args:
            manager: The RemoteSkillRegistry instance to use for federation
        """
        self._remote_registry_manager = manager
        self.logger.info("Remote registry manager set for federation")

    def sync_with_remote_registries(self, force: bool = False) -> Dict[str, bool]:
        """Synchronize with all configured remote registries.
        
        Args:
            force: Whether to force sync even if not due
            
        Returns:
            Dictionary mapping registry names to sync success boolean
        """
        if self._remote_registry_manager is None:
            self.logger.warning("Remote registry manager not configured")
            return {}
        
        return self._remote_registry_manager.sync_all_registries(force=force)

    def discover_remote_skills(self, query: str, limit: int = 10) -> List[SkillMetadata]:
        """Discover skills from remote registries matching a query.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching SkillMetadata objects from remote registries
        """
        if self._remote_registry_manager is None:
            self.logger.warning("Remote registry manager not configured")
            return []
        
        # Check cache first
        cache_key = f"{query}:{limit}"
        if cache_key in self._remote_skill_cache:
            # Check if cache is fresh (5 minutes)
            # In a real implementation, we'd timestamp cache entries
            return self._remote_skill_cache[cache_key]
        
        # Discover from remote registries
        skills = self._remote_registry_manager.discover_skills(query, limit)
        
        # Cache results
        self._remote_skill_cache[cache_key] = skills
        
        return skills

    def get_remote_registry_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about configured remote registries.
        
        Returns:
            Dictionary with registry configuration and status
        """
        if self._remote_registry_manager is None:
            return {}
        
        return self._remote_registry_manager.get_registry_info()
        
        # Initialize remote registry if configured
        self._initialize_remote_registry()

    def _load_registry(self) -> None:
        """Load skills from registry storage."""
        try:
            registry_data = self.storage.load_skills()

            for skill_data in registry_data:
                # Migrate older schema versions to current
                skill_data = self._migrate_skill_entry(skill_data)
                # Reconstruct SkillMetadata
                metadata = self._deserialize_metadata(skill_data)
                assert metadata.skill_id is not None, "Skill ID must be set after deserialization"
                self._skills[metadata.skill_id] = metadata
                # Always initialize quality metrics; populate from data if available
                metrics_data = skill_data.get("metrics", {})
                qm = QualityMetrics(
                    skill_id=metadata.skill_id,
                    validation_score=skill_data.get("validation_score", 0.0),
                    test_coverage=skill_data.get("test_coverage", 0.0),
                    success_rate=metrics_data.get("completion_rate", 0.0),
                    avg_execution_time=metrics_data.get("avg_execution_time", 0.0),
                    avg_token_savings=metrics_data.get("avg_token_savings", 0.0),
                    usage_count=metrics_data.get("applied_count", 0),
                    last_execution=datetime.fromisoformat(metrics_data["last_executed"]) if metrics_data.get("last_executed") else None,
                )
                self._quality_metrics[metadata.skill_id] = qm

            self.logger.info("Loaded skills from registry", count=len(self._skills))
        except Exception as e:
            self.logger.error("Failed to load registry", error=str(e))

    def _migrate_skill_entry(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate a registry entry to the current schema version."""
        version = data.get("schema_version", 0)
        if version < CURRENT_SCHEMA_VERSION:
            # Ensure new fields required in current version have defaults
            data.setdefault("capabilities", {})
            data.setdefault("compatibility", {})
            data.setdefault("metrics", {})
            # Increment schema version
            data["schema_version"] = CURRENT_SCHEMA_VERSION
        return data

    def _deserialize_metadata(self, data: Dict[str, Any]) -> SkillMetadata:
        """Deserialize dictionary into SkillMetadata object."""
        from .metadata import (
            SkillDependency, InputOutputSchema, SkillCapability,
            CompatibilityRange, QualityThresholds
        )

        # Parse dependencies
        deps = [SkillDependency.from_dict(d) for d in data.get("dependencies", [])]

        # Parse schema objects
        input_schema = InputOutputSchema.from_dict(data.get("input_schema", {}))
        output_schema = InputOutputSchema.from_dict(data.get("output_schema", {}))

        # Parse capabilities
        capabilities = SkillCapability.from_dict(data.get("capabilities", {}))

        # Parse compatibility
        compatibility = CompatibilityRange.from_dict(data.get("compatibility", {}))

        # Parse quality thresholds
        qt_data = data.get("quality_thresholds", {})
        thresholds = QualityThresholds(
            min_test_coverage=qt_data.get("min_test_coverage", 0.8),
            min_success_rate=qt_data.get("min_success_rate", 0.7),
            max_execution_time=qt_data.get("max_execution_time", 30.0),
            max_memory_usage=qt_data.get("max_memory_usage", 512*1024*1024),
            required_surfaces=qt_data.get("required_surfaces", 1),
            min_documentation_ratio=qt_data.get("min_documentation_ratio", 0.3),
        )

        # Parse metrics
        metrics_data = data.get("metrics", {})
        metrics = RuntimeMetrics(
            applied_count=metrics_data.get("applied_count", 0),
            success_count=metrics_data.get("success_count", 0),
            total_execution_time=metrics_data.get("total_execution_time", 0.0),
            total_token_usage=metrics_data.get("total_token_usage", 0),
            last_executed=datetime.fromisoformat(metrics_data["last_executed"]) if metrics_data.get("last_executed") else None,
        )

        # Parse timestamps
        created_at = datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
        updated_at = datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None

        return SkillMetadata(
            name=data["name"],
            domain=data["domain"],
            version=data.get("version", "0.1.0"),
            surfaces=data.get("surfaces", []),
            purpose=data.get("purpose"),
            description=data.get("description"),
            dependencies=deps,
            input_schema=input_schema,
            output_schema=output_schema,
            capabilities=capabilities,
            compatibility=compatibility,
            quality_thresholds=thresholds,
            metrics=metrics,
            skill_id=data.get("skill_id"),
            path=data.get("path"),
            schema_version=data.get("schema_version", 1),
            tags=data.get("tags", []),
            created_at=created_at,
            updated_at=updated_at,
        )

    def get_skill(self, skill_id: str) -> Optional[SkillMetadata]:
        """Retrieve a skill by its ID, with fallback to fuzzy/slugified matching."""
        # 1. Exact match
        if skill_id in self._skills:
            return self._skills[skill_id]

        # 2. Case-insensitive match
        for sid, metadata in self._skills.items():
            if sid.lower() == skill_id.lower():
                return metadata

        # 3. Slugified match (robust for CLI usage)
        # Handle cases like "DOMAIN/Name" -> "domain/name"
        slug_id = SkillMetadata._slugify(skill_id)
        if "/" in skill_id:
            domain, name = skill_id.split("/", 1)
            slug_id = f"{SkillMetadata._slugify(domain)}/{SkillMetadata._slugify(name)}"

        for sid, metadata in self._skills.items():
            # Already slugified if newly indexed, but for backward compatibility:
            if sid == slug_id:
                return metadata
            
            # Check if stored ID slugifies to the target
            if "/" in sid:
                s_dom, s_nam = sid.split("/", 1)
                if f"{SkillMetadata._slugify(s_dom)}/{SkillMetadata._slugify(s_nam)}" == slug_id:
                    return metadata

        return None

    def list_skills(self, domain: Optional[str] = None,
                    surface: Optional[str] = None,
                    min_quality: Optional[float] = None) -> List[SkillMetadata]:
        """List skills with optional filtering."""
        skills = list(self._skills.values())

        if domain:
            skills = [s for s in skills if s.domain == domain]
        if surface:
            skills = [s for s in skills if surface in s.surfaces]
        if min_quality is not None:
            skills = [s for s in skills if s.skill_id is not None and (qm := self.get_quality(s.skill_id)) is not None and qm.validation_score >= min_quality]

        return skills

    def get_quality(self, skill_id: str) -> Optional[QualityMetrics]:
        """Get quality metrics for a skill."""
        return self._quality_metrics.get(skill_id)

    def update_metrics(self, skill_id: str, success: bool, execution_time: float,
                       token_usage: int = 0) -> None:
        """Update runtime metrics for a skill."""
        if skill_id in self._skills:
            self._skills[skill_id].metrics.record_execution(success, execution_time, token_usage)
            # Also update quality metrics
            if skill_id in self._quality_metrics:
                qm = self._quality_metrics[skill_id]
                qm.success_rate = self._skills[skill_id].metrics.completion_rate
                qm.avg_execution_time = self._skills[skill_id].metrics.avg_execution_time
                qm.avg_token_savings = self._skills[skill_id].metrics.avg_token_savings
                qm.usage_count = self._skills[skill_id].metrics.applied_count
                qm.last_execution = self._skills[skill_id].metrics.last_executed
            
            self.storage.update_skill_metrics(skill_id, success, execution_time, token_usage)
            if isinstance(self.storage, JSONFileRegistryStorage):
                self._save_registry()

    def add_composition_edge(self, edge: CompositionEdge) -> None:
        """Add a composition relationship between skills."""
        self._composition_graph[edge.source_skill_id].append(edge)

    def get_compositions(self, skill_id: str) -> List[CompositionEdge]:
        """Get all composition edges for a skill (both source and target)."""
        edges = []
        edges.extend(self._composition_graph.get(skill_id, []))
        # Also find edges where this skill is the target
        for src_id, edge_list in self._composition_graph.items():
            for edge in edge_list:
                if edge.target_skill_id == skill_id:
                    edges.append(edge)
        return edges

    def find_compatible_skills(self, skill_id: str, min_score: float = 0.5) -> List[str]:
        """Find skills that can be composed with the given skill."""
        compatible: List[str] = []
        target_skill = self.get_skill(skill_id)
        if not target_skill:
            return compatible

        for candidate in self._skills.values():
            if candidate.skill_id == skill_id:
                continue
            # Ensure skill_id is not None (should always be set)
            if candidate.skill_id is None:
                continue
            # Check input/output compatibility
            compatibility = self._check_compatibility(target_skill.output_schema, candidate.input_schema)
            if compatibility >= min_score:
                compatible.append(candidate.skill_id)
        return compatible

    def _check_compatibility(self, output_schema, input_schema) -> float:
        """Calculate compatibility score between output and input schemas."""
        score = 0.0
        if output_schema.type == input_schema.type or input_schema.type == "any":
            score += 0.3
        # Check property overlap
        common_props = set(output_schema.properties.keys()) & set(input_schema.properties.keys())
        required_props = set(input_schema.required)
        if required_props.issubset(common_props):
            score += 0.7
        elif common_props:
            score += 0.3 * (len(common_props) / len(required_props)) if required_props else 0.3
        return score

    def _save_registry(self) -> None:
        """Persist registry to storage."""
        try:
            registry_data = []
            for skill in self._skills.values():
                assert skill.skill_id is not None, "Skill ID must be set"
                data = skill.to_registry_dict()
                # Include quality metrics
                qm = self._quality_metrics.get(skill.skill_id)
                if qm:
                    data["validation_score"] = qm.validation_score
                    data["test_coverage"] = qm.test_coverage
                registry_data.append(data)

            self.storage.save_skills(registry_data)
            self.logger.debug("Saved registry", skills_count=len(registry_data))
        except Exception as e:
            self.logger.error("Failed to save registry", error=str(e))

    def add_skill(self, metadata: SkillMetadata) -> None:
        """Add a new skill to the registry."""
        assert metadata.skill_id is not None, "Skill ID must be set before adding to registry"
        self._skills[metadata.skill_id] = metadata
        self._quality_metrics[metadata.skill_id] = QualityMetrics(skill_id=metadata.skill_id)
        self._save_registry()

    def remove_skill(self, skill_id: str) -> bool:
        """Remove a skill from the registry."""
        if skill_id in self._skills:
            del self._skills[skill_id]
            if skill_id in self._quality_metrics:
                del self._quality_metrics[skill_id]
            self._save_registry()
            return True
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        total = len(self._skills)
        domains: Dict[str, int] = defaultdict(int)
        surfaces: Dict[str, int] = defaultdict(int)
        avg_quality = 0.0

        for skill in self._skills.values():
            assert skill.skill_id is not None, "Skill ID must be set"
            domains[skill.domain] += 1
            for surface in skill.surfaces:
                surfaces[surface] += 1
            qm = self._quality_metrics.get(skill.skill_id)
            if qm:
                avg_quality += qm.validation_score

        avg_quality = avg_quality / total if total > 0 else 0.0

        return {
            "total_skills": total,
            "domains": dict(domains),
            "surfaces": dict(surfaces),
            "average_quality_score": avg_quality,
            "composition_edges": sum(len(edges) for edges in self._composition_graph.values()),
        }


class RegistryStorage(ABC):
    """Abstract base class for registry storage backends."""
    
    @abstractmethod
    def load_skills(self) -> List[Dict[str, Any]]:
        """Load all skills from the storage backend."""
        pass
        
    @abstractmethod
    def save_skills(self, skills: List[Dict[str, Any]]) -> None:
        """Save all skills to the storage backend."""
        pass
        
    @abstractmethod
    def update_skill_metrics(self, skill_id: str, success: bool, execution_time: float, token_usage: int = 0) -> None:
        """Update runtime metrics for a specific skill atomically."""
        pass


class JSONFileRegistryStorage(RegistryStorage):
    """JSON file-based registry storage backend (default)."""
    
    def __init__(self, registry_file: Path):
        self.registry_file = registry_file
        
    def load_skills(self) -> List[Dict[str, Any]]:
        if not self.registry_file.exists():
            return []
        try:
            with open(self.registry_file, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
            
    def save_skills(self, skills: List[Dict[str, Any]]) -> None:
        try:
            tmp_file = self.registry_file.with_name(f".{self.registry_file.name}.{uuid.uuid4().hex}.tmp")
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(skills, f, indent=2)
            tmp_file.replace(self.registry_file)
        except Exception as e:
            logger.error("Failed to save registry to JSON file", error=str(e))
            
    def update_skill_metrics(self, skill_id: str, success: bool, execution_time: float, token_usage: int = 0) -> None:
        # Atomic update not natively supported for single JSON file, caller uses save_skills
        pass


class SQLiteRegistryStorage(RegistryStorage):
    """SQLite database-based registry storage backend for thread-safe concurrent access."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS skills (
                        skill_id TEXT PRIMARY KEY,
                        name TEXT,
                        domain TEXT,
                        version TEXT,
                        surfaces TEXT,
                        purpose TEXT,
                        description TEXT,
                        validation_score REAL DEFAULT 0.0,
                        test_coverage REAL DEFAULT 0.0,
                        applied_count INTEGER DEFAULT 0,
                        success_count INTEGER DEFAULT 0,
                        total_execution_time REAL DEFAULT 0.0,
                        total_token_usage INTEGER DEFAULT 0,
                        last_executed TEXT,
                        data TEXT
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.error("Failed to initialize SQLite registry database", error=str(e))
            
    def load_skills(self) -> List[Dict[str, Any]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT data, validation_score, test_coverage, applied_count, success_count, total_execution_time, total_token_usage, last_executed FROM skills")
                skills = []
                for row in cursor.fetchall():
                    try:
                        skill_data = json.loads(row["data"])
                        skill_data["validation_score"] = row["validation_score"]
                        skill_data["test_coverage"] = row["test_coverage"]
                        
                        metrics = skill_data.setdefault("metrics", {})
                        metrics["applied_count"] = row["applied_count"]
                        metrics["success_count"] = row["success_count"]
                        metrics["total_execution_time"] = row["total_execution_time"]
                        metrics["total_token_usage"] = row["total_token_usage"]
                        metrics["last_executed"] = row["last_executed"]
                        
                        metrics["completion_rate"] = row["success_count"] / row["applied_count"] if row["applied_count"] > 0 else 0.0
                        metrics["avg_execution_time"] = row["total_execution_time"] / row["success_count"] if row["success_count"] > 0 else 0.0
                        metrics["avg_token_savings"] = row["total_token_usage"] / row["applied_count"] if row["applied_count"] > 0 else 0.0
                        
                        skills.append(skill_data)
                    except Exception:
                        pass
                return skills
        except Exception as e:
            logger.error("Failed to load skills from SQLite registry", error=str(e))
            return []
            
    def save_skills(self, skills: List[Dict[str, Any]]) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM skills")
                for skill in skills:
                    skill_id = skill["skill_id"]
                    surfaces_str = ",".join(skill.get("surfaces", []))
                    metrics = skill.get("metrics", {})
                    conn.execute("""
                        INSERT OR REPLACE INTO skills (
                            skill_id, name, domain, version, surfaces, purpose, description,
                            validation_score, test_coverage, applied_count, success_count,
                            total_execution_time, total_token_usage, last_executed, data
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        skill_id,
                        skill["name"],
                        skill["domain"],
                        skill.get("version", "0.1.0"),
                        surfaces_str,
                        skill.get("purpose", ""),
                        skill.get("description", ""),
                        skill.get("validation_score", 0.0),
                        skill.get("test_coverage", 0.0),
                        metrics.get("applied_count", 0),
                        metrics.get("success_count", 0),
                        metrics.get("total_execution_time", 0.0),
                        metrics.get("total_token_usage", 0),
                        metrics.get("last_executed"),
                        json.dumps(skill)
                    ))
                conn.commit()
        except Exception as e:
            logger.error("Failed to save skills to SQLite registry", error=str(e))
            
    def update_skill_metrics(self, skill_id: str, success: bool, execution_time: float, token_usage: int = 0) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT data, applied_count, success_count, total_execution_time, total_token_usage FROM skills WHERE skill_id = ?", (skill_id,))
                row = cursor.fetchone()
                if row:
                    new_applied = row["applied_count"] + 1
                    new_success = row["success_count"] + (1 if success else 0)
                    new_time = row["total_execution_time"] + execution_time
                    new_token = row["total_token_usage"] + token_usage
                    last_exec = datetime.utcnow().isoformat()
                    
                    try:
                        skill_data = json.loads(row["data"])
                        metrics = skill_data.setdefault("metrics", {})
                        metrics["applied_count"] = new_applied
                        metrics["success_count"] = new_success
                        metrics["total_execution_time"] = new_time
                        metrics["total_token_usage"] = new_token
                        metrics["last_executed"] = last_exec
                        
                        hist = metrics.setdefault("execution_history", [])
                        hist.append({
                            "timestamp": last_exec,
                            "success": success,
                            "execution_time": execution_time,
                            "token_usage": token_usage
                        })
                        if len(hist) > 100:
                            hist = hist[-100:]
                        metrics["execution_history"] = hist
                        
                        updated_data = json.dumps(skill_data)
                    except Exception:
                        updated_data = row["data"]
                        
                    conn.execute("""
                        UPDATE skills SET
                            applied_count = ?,
                            success_count = ?,
                            total_execution_time = ?,
                            total_token_usage = ?,
                            last_executed = ?,
                            data = ?
                        WHERE skill_id = ?
                    """, (new_applied, new_success, new_time, new_token, last_exec, updated_data, skill_id))
                    conn.commit()
        except Exception as e:
            logger.error("Failed to update skill metrics in SQLite registry", skill_id=skill_id, error=str(e))
