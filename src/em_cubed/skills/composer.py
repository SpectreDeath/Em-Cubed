"""Skill composition and orchestration framework.

Enables chaining skills together, managing data flow between surfaces,
and coordinating multi-skill execution patterns.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import asyncio
import structlog
from pathlib import Path
import json
from datetime import datetime

from .metadata import SkillMetadata
from .registry import SkillRegistry

logger = structlog.get_logger()


class CompositionPattern(Enum):
    """Patterns for composing multiple skills."""
    SEQUENTIAL = "sequential"     # Execute skills in order, passing output to next
    PARALLEL = "parallel"         # Execute independent skills concurrently
    FANOUT = "fanout"            # One skill triggers multiple downstream
    FANIN = "fanin"              # Multiple skills converge to one
    CONDITIONAL = "conditional"  # Conditional branching based on output
    MAP_REDUCE = "map_reduce"    # Process collection then aggregate
    PIPELINE = "pipeline"        # Streaming data through stages


@dataclass
class ExecutionContext:
    """Runtime context for skill execution."""
    data: Dict[str, Any]  # Input data
    metadata: Dict[str, Any] = field(default_factory=dict)  # Execution metadata
    variables: Dict[str, Any] = field(default_factory=dict)  # Shared variables
    skills_used: List[str] = field(default_factory=list)  # Track skill invocations
    errors: List[Dict[str, Any]] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def add_result(self, skill_id: str, result: Dict[str, Any]) -> None:
        """Add a skill execution result to context."""
        self.skills_used.append(skill_id)
        if "output" not in self.data:
            self.data["output"] = {}
        self.data["output"][skill_id] = result

    def add_error(self, skill_id: str, error: str) -> None:
        """Record an error from skill execution."""
        self.errors.append({"skill": skill_id, "error": error})

    def get_final_output(self) -> Any:
        """Get the final output after composition."""
        if "final_output" in self.data:
            return self.data["final_output"]
        # Return last skill's output
        if self.skills_used:
            last_skill = self.skills_used[-1]
            return self.data.get("output", {}).get(last_skill, {}).get("value")
        return None


@dataclass
class CompositionStep:
    """A single step in a skill composition."""
    skill_id: str
    input_mapping: Dict[str, str] = field(default_factory=dict)  # Map context -> skill input
    output_mapping: Dict[str, str] = field(default_factory=dict)  # Map skill output -> context
    condition: Optional[Callable[[ExecutionContext], bool]] = None
    transform: Optional[Callable[[Any], Any]] = None
    retry_policy: Optional[Dict[str, Any]] = None
    timeout: Optional[float] = None

    def prepare_input(self, context: ExecutionContext) -> Dict[str, Any]:
        """Map context data to skill input according to input_mapping."""
        if not self.input_mapping:
            return context.data.copy()

        skill_input = {}
        for dest_key, src_path in self.input_mapping.items():
            # Navigate context data using dot notation
            value = self._get_nested(context.data, src_path)
            if value is not None:
                skill_input[dest_key] = value
        return skill_input

    def apply_output(self, context: ExecutionContext, skill_output: Dict[str, Any]) -> None:
        """Map skill output back to context according to output_mapping."""
        if self.transform:
            skill_output = self.transform(skill_output)

        for dest_path, src_key in self.output_mapping.items():
            value = skill_output.get(src_key) if isinstance(skill_output, dict) else skill_output
            self._set_nested(context.data, dest_path, value)

    def _get_nested(self, data: Dict, path: str) -> Any:
        """Get nested value using dot notation."""
        keys = path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value

    def _set_nested(self, data: Dict, path: str, value: Any) -> None:
        """Set nested value using dot notation."""
        keys = path.split(".")
        current = data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value


@dataclass
class CompositionPlan:
    """A complete composition plan with execution steps."""
    name: str
    steps: List[CompositionStep]
    pattern: CompositionPattern = CompositionPattern.SEQUENTIAL
    error_handler: Optional[Callable[[ExecutionContext], None]] = None
    timeout: Optional[float] = None
    max_retries: int = 0

    def add_step(self, step: CompositionStep) -> None:
        """Add a step to the composition."""
        self.steps.append(step)


class SkillComposer:
    """Compose and execute multi-skill workflows."""

    def __init__(self, plugin_manager, registry: SkillRegistry):
        self.plugin_manager = plugin_manager
        self.registry = registry
        self.logger = logger.bind(component="skill_composer")

    async def compose(self, plan: CompositionPlan, initial_data: Dict[str, Any]) -> CompositionResult:
        """Execute a skill composition plan."""
        import time
        from datetime import datetime

        context = ExecutionContext(data=initial_data.copy())
        context.start_time = datetime.utcnow()

        self.logger.info("Starting composition execution", plan=plan.name, steps=len(plan.steps))

        try:
            if plan.pattern == CompositionPattern.SEQUENTIAL:
                result = await self._execute_sequential(plan, context)
            elif plan.pattern == CompositionPattern.PARALLEL:
                result = await self._execute_parallel(plan, context)
            elif plan.pattern == CompositionPattern.CONDITIONAL:
                result = await self._execute_conditional(plan, context)
            elif plan.pattern == CompositionPattern.PIPELINE:
                result = await self._execute_pipeline(plan, context)
            else:
                self.logger.warning("Unknown composition pattern, using sequential", pattern=plan.pattern.value)
                result = await self._execute_sequential(plan, context)

            context.end_time = datetime.utcnow()
            return result

        except Exception as e:
            context.end_time = datetime.utcnow()
            self.logger.error("Composition execution failed", error=str(e))
            if plan.error_handler:
                try:
                    plan.error_handler(context)
                except Exception as eh:
                    self.logger.error("Error handler failed", error=str(eh))
            return CompositionResult(
                success=False,
                context=context,
                error=str(e),
                steps_executed=len(context.skills_used),
            )

    async def _execute_sequential(self, plan: CompositionPlan, context: ExecutionContext) -> CompositionResult:
        """Execute steps one after another."""
        for i, step in enumerate(plan.steps):
            try:
                success = await self._execute_step(step, context)
                if not success and plan.max_retries > 0:
                    # Retry logic
                    for attempt in range(plan.max_retries):
                        self.logger.info("Retrying step", step=i+1, attempt=attempt+1)
                        success = await self._execute_step(step, context)
                        if success:
                            break
                if not success:
                    self.logger.error("Step failed permanently", step=i+1)
                    return CompositionResult(
                        success=False,
                        context=context,
                        error=f"Step {i+1} ({step.skill_id}) failed",
                        steps_executed=len(context.skills_used),
                    )
            except Exception as e:
                return CompositionResult(
                    success=False,
                    context=context,
                    error=str(e),
                    steps_executed=len(context.skills_used),
                )

        return CompositionResult(
            success=True,
            context=context,
            steps_executed=len(context.skills_used),
        )

    async def _execute_parallel(self, plan: CompositionPlan, context: ExecutionContext) -> CompositionResult:
        """Execute independent steps concurrently."""
        tasks = []
        for step in plan.steps:
            task = asyncio.create_task(self._execute_step_with_result(step, context))
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check for failures
        failures = [(step, r) for step, r in zip(plan.steps, results) if isinstance(r, Exception) or not r]
        if failures:
            self.logger.warning("Parallel steps had failures", failures=len(failures))
            # Continue anyway - partial success is ok for parallel

        return CompositionResult(
            success=True,  # Partial success is ok for parallel
            context=context,
            steps_executed=len(context.skills_used),
            parallel_results=results,
        )

    async def _execute_conditional(self, plan: CompositionPlan, context: ExecutionContext) -> CompositionResult:
        """Execute steps based on conditions."""
        for step in plan.steps:
            if step.condition is None or step.condition(context):
                success = await self._execute_step(step, context)
                if not success:
                    return CompositionResult(
                        success=False,
                        context=context,
                        error=f"Conditional step {step.skill_id} failed",
                        steps_executed=len(context.skills_used),
                    )
            else:
                self.logger.info("Skipping step (condition false)", skill=step.skill_id)

        return CompositionResult(
            success=True,
            context=context,
            steps_executed=len(context.skills_used),
        )

    async def _execute_pipeline(self, plan: CompositionPlan, context: ExecutionContext) -> CompositionResult:
        """Execute as a streaming pipeline (if skills support it)."""
        # For now, pipeline is sequential with streaming data
        return await self._execute_sequential(plan, context)

    async def _execute_step(self, step: CompositionStep, context: ExecutionContext) -> bool:
        """Execute a single composition step."""
        skill_id = step.skill_id
        skill = self.registry.get_skill(skill_id)
        if not skill:
            self.logger.error("Skill not found", skill_id=skill_id)
            context.add_error(skill_id, f"Skill '{skill_id}' not found in registry")
            return False

        # Prepare input
        skill_input = step.prepare_input(context)

        # Get surface plugin
        surface_name = skill.surfaces[0] if skill.surfaces else "python"
        plugin = self.plugin_manager.get(surface_name)
        if not plugin or not plugin.available:
            self.logger.error("Surface not available", skill=skill_id, surface=surface_name)
            context.add_error(skill_id, f"Surface '{surface_name}' not available")
            return False

        try:
            # Execute skill (simplified - would need to extract and run actual skill code)
            result = await self._execute_skill_on_surface(skill, plugin, skill_input)
            if result.get("status") == "ok":
                context.add_result(skill_id, result)
                step.apply_output(context, result)
                return True
            else:
                context.add_error(skill_id, result.get("message", "Execution failed"))
                return False
        except Exception as e:
            context.add_error(skill_id, str(e))
            return False

    async def _execute_step_with_result(self, step: CompositionStep, context: ExecutionContext) -> bool:
        """Execute step and return boolean result."""
        return await self._execute_step(step, context)

    async def _execute_skill_on_surface(self, skill: SkillMetadata, plugin, input_data: Dict) -> Dict[str, Any]:
        """Execute a skill using the specified surface plugin."""
        # This is a simplified version - actual implementation would:
        # 1. Read skill's SKILL.md file
        # 2. Extract appropriate code block for the plugin's surface
        # 3. Execute code with input_data as context
        # 4. Return structured output

        # For now, mock execution
        self.logger.debug("Executing skill on surface", skill=skill.name, surface=plugin.name)
        return {
            "status": "ok",
            "value": f"Executed {skill.name}",
            "skill": skill.name,
        }

    def create_pipeline(self, steps: List[CompositionStep], name: str = "pipeline") -> CompositionPlan:
        """Create a sequential pipeline composition."""
        return CompositionPlan(
            name=name,
            steps=steps,
            pattern=CompositionPattern.PIPELINE,
        )

    def create_parallel(self, steps: List[CompositionStep], name: str = "parallel") -> CompositionPlan:
        """Create a parallel composition."""
        return CompositionPlan(
            name=name,
            steps=steps,
            pattern=CompositionPattern.PARALLEL,
        )

    def suggest_composition(self, source_skill_id: str, goal_description: str) -> List[CompositionPlan]:
        """Suggest composition plans based on goal."""
        # This would use the recommendation engine
        suggestions = []
        compatible_skills = self.registry.find_compatible_skills(source_skill_id)

        for target_id in compatible_skills[:3]:  # Top 3 suggestions
            target_skill = self.registry.get_skill(target_id)
            if target_skill:
                step = CompositionStep(
                    skill_id=target_id,
                    input_mapping={"input": "output"},  # Simple passthrough
                    output_mapping={"result": "final_output"},
                )
                plan = CompositionPlan(
                    name=f"{source_skill_id} → {target_id}",
                    steps=[step],
                    pattern=CompositionPattern.SEQUENTIAL,
                )
                suggestions.append(plan)

        return suggestions


@dataclass
class CompositionResult:
    """Result of a composition execution."""
    success: bool
    context: ExecutionContext
    error: Optional[str] = None
    steps_executed: int = 0
    parallel_results: Optional[List[Any]] = None
    duration_ms: Optional[float] = None

    def get_output(self) -> Any:
        """Get the final output value."""
        return self.context.get_final_output()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "error": self.error,
            "steps_executed": self.steps_executed,
            "duration_ms": self.duration_ms,
            "skills_used": self.context.skills_used,
            "output": self.get_output(),
        }
