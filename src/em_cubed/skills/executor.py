"""Skill executor - loads and executes skills with telemetry.

Provides runtime execution of skills by extracting code from SKILL.md files
and running it on appropriate surfaces with full telemetry.
"""

import time
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from pathlib import Path
import asyncio
import structlog

from .telemetry import SkillTelemetry, get_telemetry_collector

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
        if not skill_file.exists():
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
        async def skill_runner(input_data: Dict[str, Any]) -> Dict[str, Any]:
            # Prepare execution context with input
            context = {
                "skill_input": input_data,
                "skill_metadata": skill.to_registry_dict(),
                **(request.context or {}),
            }

            # Execute on surface
            result = await plugin.execute(surface_code, context)
            return result

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
        from em_cubed.skills.telemetry import record_skill_execution
        record_skill_execution(
            skill_id=skill_id,
            success=success,
            execution_time_ms=elapsed,
            surface=surface_name,
            error_message=error_msg,
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
