"""Skill executor - loads and executes skills with telemetry and type conversion.

Provides runtime execution of skills by extracting code from SKILL.md files
and running it on appropriate surfaces with full telemetry and automatic
type conversion between surfaces.
"""

import time
from dataclasses import dataclass
from typing import Dict, Any, Optional, cast
from pathlib import Path
import structlog
import asyncio

from .telemetry import SkillTelemetry, get_telemetry_collector, TraceContext
from .registry import SkillRegistry

logger = structlog.get_logger()


@dataclass
class SkillExecutionRequest:
    """Request to execute a skill."""
    skill_id: str
    input_data: Dict[str, Any]
    surface: Optional[str] = None  # Override surface choice
    timeout: Optional[float] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class SkillExecutionResult:
    """Result of skill execution."""
    skill_id: str
    success: bool
    output: Any
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    surface_used: str = ""
    token_usage: int = 0


class TelemetryProxy:
    """Proxy for surface plugins that records trace spans."""
    def __init__(self, surface, trace_ctx):
        self._surface = surface
        self._trace_ctx = trace_ctx

    def __getattr__(self, name):
        attr = getattr(self._surface, name)
        if callable(attr) and name in ("execute", "execute_sync"):
            def wrapped(*args, **kwargs):
                code = args[0] if args else kwargs.get("code", "")
                span = self._trace_ctx.start_span(self._surface.name, code)
                try:
                    res = attr(*args, **kwargs)
                    return self._wrap_result(res, span)
                except Exception as e:
                    self._trace_ctx.end_span(span, success=False, error=str(e))
                    raise
            return wrapped
        elif name == "substrate":
            return attr
        return attr

    def _wrap_result(self, res, span):
        if asyncio.iscoroutine(res):
            async def wrapper():
                try:
                    r = await res
                    self._trace_ctx.end_span(
                        span, 
                        output_data=str(r)[:500], 
                        success=r.get("status") == "ok", 
                        error=r.get("message")
                    )
                    return r
                except Exception as e:
                    self._trace_ctx.end_span(span, success=False, error=str(e))
                    raise
            return wrapper()
        else:
            # Synchronous result
            self._trace_ctx.end_span(
                span, 
                output_data=str(res)[:500], 
                success=res.get("status") == "ok", 
                error=res.get("message")
            )
            return res


class SkillExecutor:
    """Loads and executes skills from SKILL.md files."""

    def __init__(self, plugin_manager, registry: 'SkillRegistry', skills_dir: Path):
        self.plugin_manager = plugin_manager
        self.registry = registry
        self.skills_dir = skills_dir
        self.telemetry = SkillTelemetry(get_telemetry_collector())
        self.logger = logger.bind(component="skill_executor")
        self._skill_cache: Dict[str, Dict[str, str]] = {}  # skill_id -> {"python": code, "prolog": code, ...}

    def _load_skill_code(self, skill_id: str) -> Dict[str, str]:
        """Load code blocks for a skill from its SKILL.md file."""
        if skill_id in self._skill_cache:
            return self._skill_cache[skill_id]

        skill = self.registry.get_skill(skill_id)
        if not skill or not skill.path:
            raise ValueError(f"Skill '{skill_id}' not found or has no path")

        skill_file = Path(skill.path)
        
        # Track if we've found the file
        found = False
        
        if skill_file.is_absolute():
            # Absolute path - use directly or fail
            if skill_file.exists():
                found = True
            # If not found, we'll fail below
        else:
            # Relative path - try multiple strategies
            # First try: relative to current cwd
            if skill_file.exists():
                found = True
            # Second try: relative to skills_dir
            elif self.skills_dir:
                candidate = self.skills_dir / skill.path
                if candidate.exists():
                    skill_file = candidate
                    found = True
                else:
                    # Third try: with leading "skills/" stripped (common double-dir issue)
                    stripped_parts = skill_file.parts
                    if stripped_parts and stripped_parts[0].lower() == "skills":
                        candidate = self.skills_dir.joinpath(*stripped_parts[1:])
                        if candidate.exists():
                            skill_file = candidate
                            found = True
        
        if not found:
            raise FileNotFoundError(f"Skill file not found: {skill.path}")

        content = skill_file.read_text(encoding="utf-8")

        # Extract code blocks
        code_blocks = {}
        import re
        # Match ```lang sections
        for match in re.finditer(r"```(\w+)\s*\r?\n(.*?)```", content, re.DOTALL):
            lang = match.group(1).lower()
            code = match.group(2).strip()
            code_blocks[lang] = code

        self._skill_cache[skill_id] = code_blocks
        return code_blocks

    async def execute(self, request: SkillExecutionRequest) -> SkillExecutionResult:
        """Execute a skill."""
        skill_id = request.skill_id
        skill = self.registry.get_skill(skill_id)
        if not skill:
            return SkillExecutionResult(
                skill_id=skill_id,
                success=False,
                output=None,
                error=f"Skill '{skill_id}' not found in registry",
            )

        # Determine which surface to use
        surface_name = request.surface or (skill.surfaces[0] if skill.surfaces else "python")
        plugin = self.plugin_manager.get(surface_name)
        if not plugin or not plugin.available:
            return SkillExecutionResult(
                skill_id=skill_id,
                success=False,
                output=None,
                error=f"Surface '{surface_name}' is not available",
                surface_used=surface_name,
            )

        # Load skill code
        try:
            code_blocks = self._load_skill_code(skill_id)
        except Exception as e:
            return SkillExecutionResult(
                skill_id=skill_id,
                success=False,
                output=None,
                error=f"Failed to load skill code: {str(e)}",
                surface_used=surface_name,
            )

        # Get code for this surface
        surface_code = code_blocks.get(surface_name)
        if not surface_code:
            return SkillExecutionResult(
                skill_id=skill_id,
                success=False,
                output=None,
                error=f"No {surface_name} implementation found in skill",
                surface_used=surface_name,
            )

        # Wrap execution with telemetry
        async def skill_runner(input_data: Dict[str, Any], trace_ctx: TraceContext) -> Dict[str, Any]:
            # Initialize shared substrate for this execution
            substrate = {}

            # Prepare execution context with input
            # Apply type conversion for cross-surface compatibility
            converted_input = {}
            for key, value in input_data.items():
                # Attempt to preserve type information through conversion
                # In a full implementation, we might have type hints from schemas
                converted_input[key] = value  # Keep as-is for now, conversion happens at surface boundary
            
            context = {
                "skill_input": converted_input,
                "skill_metadata": skill.to_registry_dict(),
                "trace_id": trace_ctx.record.trace_id,
                "substrate": substrate,
                **(request.context or {}),
            }

            # Inject surface plugins for cross-surface interaction (wrapped in proxy)
            context["surfaces"] = {}
            for s_name in ["python", "prolog", "hy", "z3", "datalog", "janus", "cangjie"]:
                surf_plugin = self.plugin_manager.get(s_name)
                if surf_plugin and surf_plugin.available:
                    # Inject shared substrate into the plugin
                    surf_plugin.substrate = substrate
                    context["surfaces"][s_name] = TelemetryProxy(surf_plugin, trace_ctx)

            # Also provide the trace context itself
            context["trace"] = trace_ctx

            # Execute on surface
            result = await plugin.execute(surface_code, context)
            # Apply type conversion for cross-surface compatibility if needed
            # In a full implementation, we would use type hints from skill schemas
            return cast(Dict[str, Any], result)

        # Execute with telemetry
        start = time.perf_counter()
        try:
            # Actually run the skill through telemetry wrapper
            result = await self.telemetry.execute_with_telemetry(
                skill_runner,
                skill_id=skill_id,
                input_data=request.input_data,
                surface=surface_name,
                timeout=request.timeout,
            )
            elapsed = (time.perf_counter() - start) * 1000
            success = result.get("status") == "ok"
            output = result.get("value")
            error_msg = result.get("message") if not success else None
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            success = False
            output = None
            error_msg = str(e)

        # Record telemetry
        from .telemetry import record_skill_execution, SkillTelemetry
        # Estimate token usage
        token_usage = SkillTelemetry(get_telemetry_collector())._estimate_tokens(request.input_data, {
            "status": "ok" if success else "error",
            "value": output,
            "message": error_msg
        })
        record_skill_execution(
            skill_id=skill_id,
            success=success,
            execution_time_ms=elapsed,
            surface=surface_name,
            error_message=error_msg,
            token_usage=token_usage,
        )

        # Update registry metrics
        self.registry.update_metrics(
            skill_id=skill_id,
            success=success,
            execution_time=elapsed / 1000.0,  # Convert to seconds
        )

        return SkillExecutionResult(
            skill_id=skill_id,
            success=success,
            output=output,
            error=error_msg,
            execution_time_ms=elapsed,
            surface_used=surface_name,
            token_usage=0,  # TODO: estimate tokens
        )


# Singleton executor
_global_executor: Optional[SkillExecutor] = None


def get_skill_executor() -> Optional[SkillExecutor]:
    """Get global skill executor instance."""
    return _global_executor


def initialize_executor(plugin_manager, registry, skills_dir: Path) -> SkillExecutor:
    """Initialize global skill executor."""
    global _global_executor
    _global_executor = SkillExecutor(plugin_manager, registry, skills_dir)
    logger.info("Skill executor initialized", skills_dir=str(skills_dir))
    return _global_executor
