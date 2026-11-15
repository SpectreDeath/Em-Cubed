"""Dynamic Multi-Surface Skill Auto-Chaining Engine.

Uses schema matching and semantic search over the SkillRegistry to discover
and synthesize multi-step workflow pipelines connecting input specs to target goals.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import structlog

from .composer import CompositionPattern, CompositionPlan, CompositionResult, CompositionStep, SkillComposer
from .registry import SkillRegistry

logger = structlog.get_logger()


class AutoChainer:
    """Discovers, constructs, and compiles multi-surface skill execution chains to achieve target goals."""

    def __init__(self, registry_path: str = "registry.json", registry: SkillRegistry | None = None):
        self.registry_path = registry_path
        self._registry = registry
        self.logger = logger.bind(component="auto_chainer")

    def _get_registry(self) -> SkillRegistry:
        if self._registry is None:
            registry_file = Path(self.registry_path)
            candidate_skills_dir = registry_file.parent / "skills"
            skills_dir = candidate_skills_dir if candidate_skills_dir.exists() else Path("skills")
            self._registry = SkillRegistry(skills_dir=skills_dir, registry_file=registry_file)
        return self._registry

    def _evaluate_step_compatibility(
        self,
        skill: dict[str, Any],
        available_inputs: set[str],
        step_idx: int,
    ) -> tuple[float, dict[str, str], set[str]]:
        """Evaluate input matching compatibility and build input/output mappings."""
        skill_id = skill.get("id", "")
        # Inspect metadata for required/optional inputs
        meta = skill.get("metadata") or {}
        inputs_meta = meta.get("inputs") or {}
        required_inputs = set(inputs_meta.get("required") or [])
        properties = set(inputs_meta.get("properties", {}).keys())

        expected_inputs = required_inputs or properties
        if not expected_inputs:
            # Fallback: skill accepts generic inputs or matches available context
            matched_inputs = available_inputs.copy()
            score = max(0.65, round(1.0 - (step_idx * 0.08), 2))
        else:
            overlap = expected_inputs.intersection(available_inputs)
            if expected_inputs:
                score = round(min(1.0, 0.5 + (len(overlap) / max(1, len(expected_inputs)) * 0.5) - (step_idx * 0.05)), 2)
            else:
                score = round(max(0.70, 0.95 - (step_idx * 0.05)), 2)
            matched_inputs = overlap if overlap else expected_inputs

        # Input mapping: map context data to skill inputs
        input_mapping = {inp: inp for inp in matched_inputs}

        # Projected outputs produced by this skill
        outputs_meta = meta.get("outputs") or {}
        produced_outputs = set(outputs_meta.get("properties", {}).keys()) or {f"output_{skill_id.split('/')[-1]}"}

        return score, input_mapping, produced_outputs

    def find_chain(self, input_schema: dict[str, Any], goal_description: str, max_depth: int = 3) -> dict[str, Any]:
        """Synthesize a pipeline DAG connecting input fields to the goal description.

        Args:
            input_schema: Dictionary specifying available input fields and types.
            goal_description: Natural language or domain goal for the pipeline.
            max_depth: Maximum number of skills allowed in the chain.

        Returns:
            Dict containing pipeline steps, execution sequence, surfaces, and estimated compatibility.
        """
        from ..search import search_registry

        self.logger.info("Synthesizing skill chain", goal=goal_description, inputs=list(input_schema.keys()))

        # Search registry for candidate skills matching the goal
        candidates = search_registry(goal_description, registry_path=Path(self.registry_path), max_results=10)

        if not candidates:
            return {
                "status": "error",
                "message": f"No matching skills found for goal: {goal_description}",
                "pipeline": [],
            }

        # Select top compatible skills to construct pipeline steps
        selected_steps: list[dict[str, Any]] = []
        current_inputs = set(input_schema.keys())
        scores: list[float] = []

        for idx, skill in enumerate(candidates[:max_depth]):
            skill_id = skill.get("id", f"skill_{idx}")
            surface = skill.get("surface", "python")
            title = skill.get("title", skill_id)

            comp_score, in_mapping, out_keys = self._evaluate_step_compatibility(
                skill=skill,
                available_inputs=current_inputs,
                step_idx=idx,
            )
            scores.append(comp_score)

            step = {
                "step_index": idx + 1,
                "skill_id": skill_id,
                "title": title,
                "surface": surface,
                "provided_inputs": list(current_inputs),
                "input_mapping": in_mapping,
                "produced_outputs": list(out_keys),
                "compatibility_score": comp_score,
            }
            selected_steps.append(step)
            current_inputs.update(out_keys)

        avg_compatibility = round(sum(scores) / len(scores), 2) if scores else 0.90

        return {
            "status": "ok",
            "goal": goal_description,
            "pipeline_length": len(selected_steps),
            "pipeline": selected_steps,
            "estimated_compatibility": avg_compatibility,
        }

    def build_composition_plan(
        self,
        input_schema: dict[str, Any],
        goal_description: str,
        max_depth: int = 3,
        plan_name: str | None = None,
    ) -> CompositionPlan:
        """Compile an auto-discovered skill chain into an executable CompositionPlan.

        Args:
            input_schema: Dictionary specifying initial available inputs.
            goal_description: Natural language goal.
            max_depth: Maximum number of skills in the chain.
            plan_name: Optional name for the synthesized composition plan.

        Returns:
            Executable CompositionPlan ready for SkillComposer.
        """
        chain_data = self.find_chain(input_schema, goal_description, max_depth=max_depth)
        name = plan_name or f"AutoChain: {goal_description[:40]}"

        if chain_data.get("status") != "ok" or not chain_data.get("pipeline"):
            return CompositionPlan(name=name, steps=[], pattern=CompositionPattern.SEQUENTIAL)

        steps: list[CompositionStep] = []
        for s in chain_data["pipeline"]:
            skill_id = s["skill_id"]
            in_map = s.get("input_mapping", {})
            out_map = {out: out for out in s.get("produced_outputs", [])}

            steps.append(
                CompositionStep(
                    skill_id=skill_id,
                    input_mapping=in_map,
                    output_mapping=out_map,
                )
            )

        return CompositionPlan(
            name=name,
            steps=steps,
            pattern=CompositionPattern.SEQUENTIAL,
        )

    async def execute_chain(
        self,
        input_data: dict[str, Any],
        goal_description: str,
        composer: SkillComposer | None = None,
        max_depth: int = 3,
    ) -> CompositionResult:
        """Discover, synthesize, and execute a multi-skill pipeline end-to-end.

        Args:
            input_data: Initial data payload for the workflow context.
            goal_description: Natural language or domain goal.
            composer: Optional pre-configured SkillComposer instance.
            max_depth: Maximum pipeline depth.

        Returns:
            CompositionResult of the completed execution.
        """
        from ..plugin_manager import PluginManager

        plan = self.build_composition_plan(
            input_schema=input_data,
            goal_description=goal_description,
            max_depth=max_depth,
        )

        if not plan.steps:
            from .composer import ExecutionContext

            ctx = ExecutionContext(data=input_data)
            return CompositionResult(
                success=False,
                context=ctx,
                error=f"No matching skills found for goal: {goal_description}",
                steps_executed=0,
            )

        if composer is None:
            plugin_manager = PluginManager()
            registry = self._get_registry()
            composer = SkillComposer(plugin_manager=plugin_manager, registry=registry)

        return await composer.compose(plan, input_data)

