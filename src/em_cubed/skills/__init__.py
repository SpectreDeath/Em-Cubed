"""Skills quality framework for Em-Cubed.

This module provides comprehensive quality assurance, validation, and composition
capabilities for multi-surface skills following the Python/Prolog/Hy paradigm.
"""

from .benchmark import BenchmarkResult, SkillBenchmark
from .composer import CompositionResult, SkillComposer
from .executor import (
    SkillExecutionRequest,
    SkillExecutionResult,
    SkillExecutor,
    get_skill_executor,
    initialize_executor,
)
from .hub import SkillHub
from .metadata import SkillMetadata
from .quality_pipeline import SkillQualityPipeline
from .recommender import RecommendationResult, SkillRecommender
from .registry import QualityMetrics, SkillRegistry
from .skill_compiler import SkillCompiler
from .telemetry import (
    ExecutionRecord,
    SkillTelemetry,
    TelemetryCollector,
    TelemetryConfig,
    get_telemetry_collector,
    initialize_telemetry,
    record_skill_execution,
)
from .validator import SkillValidator, ValidationResult

__all__ = [
    "BenchmarkResult",
    "CompositionResult",
    "ExecutionRecord",
    "QualityMetrics",
    "RecommendationResult",
    "SkillBenchmark",
    "SkillCompiler",
    "SkillComposer",
    "SkillExecutionRequest",
    "SkillExecutionResult",
    "SkillExecutor",
    "SkillHub",
    "SkillMetadata",
    "SkillQualityPipeline",
    "SkillRecommender",
    "SkillRegistry",
    "SkillTelemetry",
    "SkillValidator",
    "TelemetryCollector",
    "TelemetryConfig",
    "ValidationResult",
    "get_skill_executor",
    "get_telemetry_collector",
    "initialize_executor",
    "initialize_telemetry",
    "record_skill_execution",
]

