"""Skills quality framework for Em-Cubed.

This module provides comprehensive quality assurance, validation, and composition
capabilities for multi-surface skills following the Python/Prolog/Hy paradigm.
"""

from .metadata import SkillMetadata
from .validator import SkillValidator, ValidationResult
from .registry import SkillRegistry, QualityMetrics
from .composer import SkillComposer, CompositionResult
from .benchmark import SkillBenchmark, BenchmarkResult
from .recommender import SkillRecommender, RecommendationResult
from .quality_pipeline import SkillQualityPipeline
from .telemetry import (
    TelemetryCollector,
    TelemetryConfig,
    ExecutionRecord,
    SkillTelemetry,
    get_telemetry_collector,
    initialize_telemetry,
    record_skill_execution,
)
from .executor import SkillExecutor, SkillExecutionRequest, SkillExecutionResult, get_skill_executor, initialize_executor

__all__ = [
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
    "TelemetryConfig",
    "ExecutionRecord",
    "SkillTelemetry",
    "get_telemetry_collector",
    "initialize_telemetry",
    "record_skill_execution",
    "SkillExecutor",
    "SkillExecutionRequest",
    "SkillExecutionResult",
    "get_skill_executor",
    "initialize_executor",
]
