"""DAG-based workflow execution for skills.

Provides the WorkflowExecutor which manages complex multi-skill dependencies
and handles parallel execution of independent steps.
"""

import asyncio
import structlog
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime

from .composer import ExecutionContext, CompositionStep, CompositionResult

logger = structlog.get_logger()

@dataclass
class WorkflowStep:
    """A single step in a DAG workflow."""
    id: str  # Unique ID for this step in the workflow
    skill_id: str  # The skill to execute
    input_mapping: Dict[str, str] = field(default_factory=dict)
    output_mapping: Dict[str, str] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # IDs of steps this depends on
    condition: Optional[str] = None  # Python expression evaluated against context
    timeout: Optional[float] = None

@dataclass
class WorkflowDefinition:
    """Definition of a DAG-based workflow."""
    name: str
    steps: List[WorkflowStep]
    description: Optional[str] = None
    timeout: Optional[float] = None

class WorkflowExecutor:
    """Executes a DAG of skills with dependency resolution."""

    def __init__(self, composer):
        self.composer = composer
        self.plugin_manager = composer.plugin_manager
        self.registry = composer.registry
        self.logger = logger.bind(component="workflow_executor")

    async def execute(self, workflow: WorkflowDefinition, initial_data: Dict[str, Any]) -> CompositionResult:
        """Execute a DAG workflow."""
        context = ExecutionContext(data=initial_data.copy())
        context.start_time = datetime.utcnow()
        
        self.logger.info("Starting workflow execution", workflow=workflow.name, steps=len(workflow.steps))
        
        # 1. Build dependency graph
        graph: Dict[str, Set[str]] = {step.id: set(step.dependencies) for step in workflow.steps}
        _steps_by_id: Dict[str, WorkflowStep] = {step.id: step for step in workflow.steps}
        
        # 2. Check for cycles
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        
        def has_cycle(step_id: str) -> bool:
            visited.add(step_id)
            rec_stack.add(step_id)
            
            for dependency in graph.get(step_id, set()):
                if dependency not in visited:
                    if has_cycle(dependency):
                        return True
                elif dependency in rec_stack:
                    return True
            
            rec_stack.remove(step_id)
            return False
        
        # Check for cycles in all nodes
        for step_id in graph:
            if step_id not in visited:
                if has_cycle(step_id):
                    return CompositionResult(
                        success=False,
                        context=context,
                        steps_executed=0,
                        error=f"circular dependency detected involving step {step_id}"
                    )
        
        # 3. Execute steps layer by layer or as tasks complete
        completed_steps: Set[str] = set()
        failed_steps: Set[str] = set()
        
        # Use a lock for context access during parallel execution
        context_lock = asyncio.Lock()

        async def run_step(step: WorkflowStep):
            # Wait for dependencies
            while not set(step.dependencies).issubset(completed_steps):
                if any(dep in failed_steps for dep in step.dependencies):
                    self.logger.warning("Skipping step due to dependency failure", step=step.id)
                    return False
                await asyncio.sleep(0.1)
            
            # Check condition if present
            if step.condition:
                try:
                    # Simple eval against context data (Caution: insecure, should be improved)
                    if not eval(step.condition, {"context": context.data}):
                        self.logger.info("Skipping step due to condition", step=step.id)
                        async with context_lock:
                            completed_steps.add(step.id)
                        return True
                except Exception as e:
                    self.logger.error("Error evaluating condition", step=step.id, error=str(e))
                    async with context_lock:
                        failed_steps.add(step.id)
                    return False

            # Convert WorkflowStep to CompositionStep for reuse
            comp_step = CompositionStep(
                skill_id=step.skill_id,
                input_mapping=step.input_mapping,
                output_mapping=step.output_mapping,
                timeout=step.timeout
            )
            
            self.logger.info("Executing step", step=step.id, skill=step.skill_id)
            try:
                success = await self.composer._execute_step(comp_step, context)
                async with context_lock:
                    if success:
                        completed_steps.add(step.id)
                    else:
                        failed_steps.add(step.id)
                return success
            except Exception as e:
                self.logger.exception("Step execution failed", step=step.id, error=str(e))
                async with context_lock:
                    failed_steps.add(step.id)
                return False

        # Create tasks for all steps
        tasks = [asyncio.create_task(run_step(step)) for step in workflow.steps]
        await asyncio.gather(*tasks)
        
        context.end_time = datetime.utcnow()
        success = len(failed_steps) == 0
        
        return CompositionResult(
            success=success,
            context=context,
            steps_executed=len(completed_steps),
            error="One or more steps failed" if not success else None
        )

    def _has_cycle(self, graph: Dict[str, Set[str]]) -> bool:
        """Simple DFS to detect cycles in the dependency graph."""
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def visit(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if visit(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for node in graph:
            if node not in visited:
                if visit(node):
                    return True
        return False
