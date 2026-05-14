"""Skill execution telemetry and usage tracking.

Instruments skill execution to collect metrics on usage, performance,
and quality. Integrates with the SkillRegistry for persistent storage.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, cast
from datetime import datetime, timezone
import time
import statistics
from pathlib import Path
import json

import structlog
import uuid

logger = structlog.get_logger()


@dataclass
class TraceSpan:
    """A single span within an execution trace."""
    span_id: str
    surface: str
    start_time: float
    end_time: Optional[float] = None
    input_data: Any = None
    output_data: Any = None
    success: bool = True
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "span_id": self.span_id,
            "surface": self.surface,
            "duration_ms": (self.end_time - self.start_time) * 1000 if self.end_time else 0,
            "success": self.success,
            "error": self.error,
            "input_size": len(str(self.input_data)) if self.input_data else 0,
            "output_size": len(str(self.output_data)) if self.output_data else 0,
        }


@dataclass
class ExecutionRecord:
    """Single skill execution record."""
    skill_id: str
    timestamp: datetime
    success: bool
    execution_time_ms: float
    token_usage: int = 0
    input_size: Optional[int] = None
    output_size: Optional[int] = None
    surface: str = "python"
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    spans: List[TraceSpan] = field(default_factory=list)

    def record_span(self, span: TraceSpan) -> None:
        self.spans.append(span)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "execution_time_ms": self.execution_time_ms,
            "token_usage": self.token_usage,
            "input_size": self.input_size,
            "output_size": self.output_size,
            "surface": self.surface,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "trace_id": self.trace_id,
            "spans": [s.to_dict() for s in self.spans],
        }


@dataclass
class TelemetryConfig:
    """Configuration for telemetry collection."""
    enabled: bool = True
    log_every_execution: bool = False  # Log to console on every execution
    persist_path: Optional[Path] = None  # Where to save telemetry data
    max_history_per_skill: int = 1000  # Max records to keep in memory
    aggregate_interval_seconds: float = 60.0  # How often to aggregate and persist
    send_to_endpoint: Optional[str] = None  # Remote telemetry endpoint

    def __post_init__(self):
        if self.persist_path is None:
            self.persist_path = Path("logs") / "skill_telemetry.jsonl"


class TelemetryCollector:
    """Collects and aggregates skill execution telemetry."""

    def __init__(self, config: Optional[TelemetryConfig] = None):
        self.config = config or TelemetryConfig()
        self.logger = logger.bind(component="telemetry")
        self._records: List[ExecutionRecord] = []
        self._aggregates: Dict[str, Dict[str, Any]] = {}
        self._last_aggregate = time.time()

    def record_execution(self, record: ExecutionRecord) -> None:
        """Record a skill execution."""
        if not self.config.enabled:
            return

        self._records.append(record)

        # Trim old records if needed
        if len(self._records) > self.config.max_history_per_skill * 10:  # Overall cap
            # Remove oldest records
            excess = len(self._records) - self.config.max_history_per_skill * 10
            self._records = self._records[excess:]

        # Log if configured
        if self.config.log_every_execution:
            self.logger.info("Execution recorded",
                           skill_id=record.skill_id,
                           success=record.success,
                           time_ms=record.execution_time_ms)

        # Periodically aggregate
        if time.time() - self._last_aggregate > self.config.aggregate_interval_seconds:
            self._aggregate_and_persist()

    def flush(self) -> None:
        """Force immediate aggregation and persistence."""
        self._aggregate_and_persist()

    def get_skill_metrics(self, skill_id: str, window_seconds: int = 3600) -> Dict[str, Any]:
        """Get metrics for a specific skill over a time window."""
        cutoff = datetime.now(timezone.utc).timestamp() - window_seconds

        relevant = [
            r for r in self._records
            if r.skill_id == skill_id and r.timestamp.timestamp() > cutoff
        ]

        if not relevant:
            return {"count": 0}

        times = [r.execution_time_ms for r in relevant if r.success]
        successes = sum(1 for r in relevant if r.success)
        failures = len(relevant) - successes
        token_usage = sum(r.token_usage for r in relevant)

        return {
            "count": len(relevant),
            "success_count": successes,
            "failure_count": failures,
            "success_rate": successes / len(relevant),
            "mean_execution_time_ms": statistics.mean(times) if times else 0,
            "p95_execution_time_ms": sorted(times)[int(0.95 * len(times))] if times else 0,
            "total_token_usage": token_usage,
            "avg_token_usage": token_usage / len(relevant) if relevant else 0,
        }

    def get_overall_stats(self) -> Dict[str, Any]:
        """Get overall telemetry statistics."""
        if not self._records:
            return {"total_executions": 0}

        total = len(self._records)
        successes = sum(1 for r in self._records if r.success)

        return {
            "total_executions": total,
            "overall_success_rate": successes / total,
            "unique_skills": len(set(r.skill_id for r in self._records)),
            "total_token_usage": sum(r.token_usage for r in self._records),
        }

    def _aggregate_and_persist(self) -> None:
        """Aggregate metrics and persist to disk."""
        self._last_aggregate = time.time()

        # Compute per-skill aggregates
        by_skill: Dict[str, List[ExecutionRecord]] = {}
        for record in self._records:
            by_skill.setdefault(record.skill_id, []).append(record)

        aggregates = {}
        for skill_id, records in by_skill.items():
            recent = [r for r in records if
                     (datetime.now(timezone.utc) - r.timestamp).total_seconds() < 3600]
            if recent:
                times = [r.execution_time_ms for r in recent if r.success]
                aggregates[skill_id] = {
                    "count_1h": len(recent),
                    "success_rate_1h": sum(1 for r in recent if r.success) / len(recent),
                    "mean_time_ms": statistics.mean(times) if times else 0,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }

        self._aggregates = aggregates

        # Persist to disk if configured
        if self.config.persist_path:
            self._persist()

    def _persist(self) -> None:
        """Write telemetry data to disk."""
        try:
            path = self.config.persist_path
            if path is None:
                return  # Telemetry persistence disabled
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "a") as f:
                for record in self._records[-100:]:  # Last 100 records
                    f.write(json.dumps(record.to_dict()) + "\n")
        except Exception as e:
            self.logger.warning("Failed to persist telemetry", error=str(e))

    def export_to_registry(self, registry) -> None:
        """Update SkillRegistry metrics based on collected telemetry."""
        by_skill: Dict[str, List[ExecutionRecord]] = {}
        for record in self._records:
            by_skill.setdefault(record.skill_id, []).append(record)

        for skill_id, records in by_skill.items():
            if skill_id in registry._skills:
                successes = sum(1 for r in records if r.success)
                times = [r.execution_time_ms for r in records if r.success]

                registry.update_metrics(
                    skill_id=skill_id,
                    success=successes > 0,  # Not exact but indicates success
                    execution_time=statistics.mean(times) / 1000 if times else 0.0,  # Convert to seconds
                    token_usage=sum(r.token_usage for r in records),
                )


class TraceContext:
    """Helper to manage hierarchical spans during execution."""
    def __init__(self, record: ExecutionRecord):
        self.record = record
    
    def start_span(self, surface: str, input_data: Any = None) -> TraceSpan:
        span = TraceSpan(
            span_id=str(uuid.uuid4()),
            surface=surface,
            start_time=time.perf_counter(),
            input_data=input_data
        )
        self.record.record_span(span)
        return span
    
    def end_span(self, span: TraceSpan, output_data: Any = None, success: bool = True, error: str = None):
        span.end_time = time.perf_counter()
        span.output_data = output_data
        span.success = success
        span.error = error


class SkillTelemetry:
    """Wrapper for skill execution that records telemetry."""

    def __init__(self, collector: TelemetryCollector):
        self.collector = collector
        self.logger = logger.bind(component="skill_telemetry")

    async def execute_with_telemetry(self, skill_executor, skill_id: str,
                                     input_data: Dict[str, Any],
                                     surface: str = "python",
                                     timeout: Optional[float] = None) -> Dict[str, Any]:
        """Execute a skill while recording telemetry."""
        start = time.perf_counter()
        token_usage = 0
        success = False
        error_type = None
        error_message = None
        
        record = ExecutionRecord(
            skill_id=skill_id,
            timestamp=datetime.now(timezone.utc),
            success=False,
            execution_time_ms=0,
            surface=surface,
        )
        trace_ctx = TraceContext(record)

        try:
            result = await skill_executor(input_data, trace_ctx)
            success = result.get("status") == "ok"
            if not success:
                error_type = "execution_error"
                error_message = result.get("message", "Unknown error")
            token_usage = self._estimate_tokens(input_data, result)
        except Exception as e:
            error_type = type(e).__name__
            error_message = str(e)
            result = {"status": "error", "message": error_message}

        record.execution_time_ms = (time.perf_counter() - start) * 1000
        record.success = success
        record.token_usage = token_usage
        record.error_type = error_type
        record.error_message = error_message
        record.context = {"input": str(input_data)[:200]}

        self.collector.record_execution(record)
        return cast(Dict[str, Any], result)

    def _estimate_tokens(self, input_data: Any, result: Dict[str, Any]) -> int:
        """Roughly estimate token usage from input/output size."""
        import json
        try:
            input_str = json.dumps(input_data)
            output_str = json.dumps(result)
            # Rough estimate: 1 token ~= 4 characters
            return (len(input_str) + len(output_str)) // 4
        except Exception:
            return 0


# Global telemetry collector (singleton)
_global_collector: Optional[TelemetryCollector] = None


def get_telemetry_collector() -> TelemetryCollector:
    """Get the global telemetry collector instance."""
    global _global_collector
    if _global_collector is None:
        _global_collector = TelemetryCollector()
    return _global_collector


def initialize_telemetry(config: Optional[TelemetryConfig] = None) -> TelemetryCollector:
    """Initialize global telemetry with optional config."""
    global _global_collector
    _global_collector = TelemetryCollector(config)
    logger.info("Telemetry initialized", config=config.__dict__ if config else "default")
    return _global_collector


def record_skill_execution(skill_id: str, success: bool, execution_time_ms: float,
                          token_usage: int = 0, surface: str = "python",
                          **kwargs) -> None:
    """Convenience function to record a skill execution."""
    collector = get_telemetry_collector()
    record = ExecutionRecord(
        skill_id=skill_id,
        timestamp=datetime.now(timezone.utc),
        success=success,
        execution_time_ms=execution_time_ms,
        token_usage=token_usage,
        surface=surface,
        **kwargs,
    )
    collector.record_execution(record)
