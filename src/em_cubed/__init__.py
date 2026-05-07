"""Em-Cubed: Multi-Surface Skill Framework.

Supports Python, Prolog, and Hy execution surfaces with unified indexing and search.
Enhanced with quality assurance, validation, and composition capabilities.
"""

from .indexer import reindex, get_skill_metadata  # noqa: E402
from .search import search_registry  # noqa: E402
from .surfaces import PrologSurface, HySurface, PythonSurface, Z3Surface, DatalogSurface, JanusSurface  # noqa: E402
from .skills import (
    SkillMetadata,
    SkillValidator,
    ValidationResult,
    SkillRegistry,
    QualityMetrics,
    SkillComposer,
    CompositionResult,
    SkillBenchmark,
    BenchmarkResult,
    SkillRecommender,
    RecommendationResult,
    SkillQualityPipeline,
    TelemetryCollector,
    ExecutionRecord,
    SkillTelemetry,
    SkillExecutor,
    initialize_telemetry,
    initialize_executor,
)

__version__ = "0.5.0"  # Bumped: Added skill quality framework, validation, composition, telemetry
__all__ = [
    "reindex",
    "get_skill_metadata",
    "search_registry",
    "PythonSurface",
    "PrologSurface",
    "HySurface",
    "Z3Surface",
    "DatalogSurface",
    "JanusSurface",
    # Skills quality framework
    "SkillMetadata",
    "SkillValidator",
    "ValidationResult",
    "SkillRegistry",
    "QualityMetrics",
    "SkillComposer",
    "CompositionResult",
    "SkillBenchmark",
    "BenchmarkResult",
    "SkillRecommender",
    "RecommendationResult",
    "SkillQualityPipeline",
    "TelemetryCollector",
    "ExecutionRecord",
    "SkillTelemetry",
    "SkillExecutor",
    "initialize_telemetry",
    "initialize_executor",
]
