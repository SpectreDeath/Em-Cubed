"""Em-Cubed: Polyglot AI Skill Engine & Neuro-Symbolic Ontological Framework.

Unified execution engine supporting Python, Prolog, Z3, Datalog, Hy, SQLite, QuickJS, WASM, Clingo, Kanren.
"""

import warnings
from typing import Any

try:
    from .indexer import get_skill_metadata, reindex
    from .search import search_registry
    from .skills import SkillExecutor, SkillRegistry, SkillValidator
    from .surfaces import (
        ClingoSurface,
        DatalogSurface,
        HySurface,
        JanusSurface,
        KanrenSurface,
        PrologSurface,
        PythonSurface,
        QuickJSSurface,
        SQLiteSurface,
        WASMSurface,
        Z3Surface,
    )
except ImportError:
    pass

__version__ = "0.8.0"

# Tiered Public API: Core Skill Engine & Primary Surfaces
__all__ = [
    "ClingoSurface",
    "DatalogSurface",
    "HySurface",
    "JanusSurface",
    "KanrenSurface",
    "PrologSurface",
    "PythonSurface",
    "QuickJSSurface",
    "SQLiteSurface",
    "SkillExecutor",
    "SkillRegistry",
    "SkillValidator",
    "WASMSurface",
    "Z3Surface",
    "__version__",
    "get_skill_metadata",
    "reindex",
    "search_registry",
]

# Legacy sub-package mapping for backward-compatible attribute access with DeprecationWarning (PEP 562)
_DEPRECATED_LEGACY_EXPORTS = {
    # Skills / Quality framework
    "SkillMetadata": ("em_cubed.skills", "SkillMetadata"),
    "QualityMetrics": ("em_cubed.skills", "QualityMetrics"),
    "SkillComposer": ("em_cubed.skills", "SkillComposer"),
    "CompositionResult": ("em_cubed.skills", "CompositionResult"),
    "SkillBenchmark": ("em_cubed.skills", "SkillBenchmark"),
    "BenchmarkResult": ("em_cubed.skills", "BenchmarkResult"),
    "SkillRecommender": ("em_cubed.skills", "SkillRecommender"),
    "RecommendationResult": ("em_cubed.skills", "RecommendationResult"),
    "SkillQualityPipeline": ("em_cubed.skills", "SkillQualityPipeline"),
    "TelemetryCollector": ("em_cubed.skills", "TelemetryCollector"),
    "ExecutionRecord": ("em_cubed.skills", "ExecutionRecord"),
    "SkillTelemetry": ("em_cubed.skills", "SkillTelemetry"),
    "ValidationResult": ("em_cubed.skills", "ValidationResult"),
    "initialize_telemetry": ("em_cubed.skills", "initialize_telemetry"),
    "initialize_executor": ("em_cubed.skills", "initialize_executor"),
    # Gateway / MCP
    "EmCubedMCPServer": ("em_cubed.gateway", "EmCubedMCPServer"),
    "run_mcp_server": ("em_cubed.gateway", "run_mcp_server"),
    # Loopy
    "BaseLoopySkill": ("em_cubed.loopy", "BaseLoopySkill"),
    "LoopySkillRunner": ("em_cubed.loopy", "LoopySkillRunner"),
    "TextLoopMiner": ("em_cubed.loopy", "TextLoopMiner"),
    "TrajectoryAuditor": ("em_cubed.loopy", "TrajectoryAuditor"),
    "SkillEvolutionEngine": ("em_cubed.loopy", "SkillEvolutionEngine"),
    # Surfaces extra
    "SurfaceFunctor": ("em_cubed.surfaces", "SurfaceFunctor"),
    "OntologyMonad": ("em_cubed.surfaces", "OntologyMonad"),
    "SurfaceMorphism": ("em_cubed.surfaces", "SurfaceMorphism"),
    # CLI / TUI
    "OntologyTUIDashboard": ("em_cubed.cli_tui", "OntologyTUIDashboard"),
    "run_cli_tui_mode": ("em_cubed.cli_tui", "run_cli_tui_mode"),
    # Benchmarks
    "BenchmarkReport": ("em_cubed.benchmarks", "BenchmarkReport"),
    "DualEngineBenchmarkRunner": ("em_cubed.benchmarks", "DualEngineBenchmarkRunner"),
    # Swarm
    "DualEngineSwarmOrchestrator": ("em_cubed.orchestration.dual_engine_swarm", "DualEngineSwarmOrchestrator"),
    "SwarmExecutionReport": ("em_cubed.orchestration.dual_engine_swarm", "SwarmExecutionReport"),
    "SwarmRunConfig": ("em_cubed.orchestration.dual_engine_swarm", "SwarmRunConfig"),
}


def __getattr__(name: str) -> Any:
    if name in _DEPRECATED_LEGACY_EXPORTS:
        mod_path, attr_name = _DEPRECATED_LEGACY_EXPORTS[name]
        warnings.warn(
            f"Direct top-level import of '{name}' from 'em_cubed' is deprecated. "
            f"Please import from '{mod_path}' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        import importlib

        mod = importlib.import_module(mod_path)
        return getattr(mod, attr_name)

    # Check ontology module for any remaining ontology symbols
    try:
        import importlib

        mod = importlib.import_module("em_cubed.ontology")
        if hasattr(mod, name):
            warnings.warn(
                f"Direct top-level import of '{name}' from 'em_cubed' is deprecated. "
                f"Please import from 'em_cubed.ontology' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            return getattr(mod, name)
    except Exception:  # nosec B110 - intentional fallback for deprecated attribute resolution
        pass

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
