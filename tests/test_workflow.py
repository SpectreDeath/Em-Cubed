import pytest
import asyncio
from unittest.mock import MagicMock
from em_cubed.skills.workflow import WorkflowExecutor, WorkflowDefinition, WorkflowStep
from em_cubed.skills.composer import SkillComposer, ExecutionContext

@pytest.fixture
def mock_composer():
    composer = MagicMock(spec=SkillComposer)
    composer.plugin_manager = MagicMock()
    composer.registry = MagicMock()
    
    # Mock _execute_step to just mark step as used and return True
    async def mock_execute_step(step, context):
        context.skills_used.append(step.skill_id)
        # Simulate some work
        await asyncio.sleep(0.01)
        return True
        
    composer._execute_step.side_effect = mock_execute_step
    return composer

@pytest.mark.asyncio
async def test_workflow_sequential(mock_composer):
    executor = WorkflowExecutor(mock_composer)
    
    workflow = WorkflowDefinition(
        name="Sequential Workflow",
        steps=[
            WorkflowStep(id="step1", skill_id="skill1"),
            WorkflowStep(id="step2", skill_id="skill2", dependencies=["step1"]),
        ]
    )
    
    result = await executor.execute(workflow, {})
    
    assert result.success is True
    assert result.steps_executed == 2
    assert result.context.skills_used == ["skill1", "skill2"]

@pytest.mark.asyncio
async def test_workflow_parallel(mock_composer):
    executor = WorkflowExecutor(mock_composer)
    
    workflow = WorkflowDefinition(
        name="Parallel Workflow",
        steps=[
            WorkflowStep(id="step1", skill_id="skill1"),
            WorkflowStep(id="step2", skill_id="skill2"),
        ]
    )
    
    result = await executor.execute(workflow, {})
    
    assert result.success is True
    assert result.steps_executed == 2
    # Order might vary because they run in parallel, but here they are independent
    assert "skill1" in result.context.skills_used
    assert "skill2" in result.context.skills_used

@pytest.mark.asyncio
async def test_workflow_cycle_detection(mock_composer):
    executor = WorkflowExecutor(mock_composer)
    
    workflow = WorkflowDefinition(
        name="Cycle Workflow",
        steps=[
            WorkflowStep(id="step1", skill_id="skill1", dependencies=["step2"]),
            WorkflowStep(id="step2", skill_id="skill2", dependencies=["step1"]),
        ]
    )
    
    result = await executor.execute(workflow, {})
    
    assert result.success is False
    assert "circular dependency" in result.error

@pytest.mark.asyncio
async def test_workflow_condition(mock_composer):
    executor = WorkflowExecutor(mock_composer)
    
    workflow = WorkflowDefinition(
        name="Conditional Workflow",
        steps=[
            WorkflowStep(id="step1", skill_id="skill1", condition="context.get('run_me') == True"),
            WorkflowStep(id="step2", skill_id="skill2", condition="context.get('run_me') == False"),
        ]
    )
    
    result = await executor.execute(workflow, {"run_me": True})
    
    assert result.success is True
    assert result.steps_executed == 2 # step2 is "executed" but skipped
    assert "skill1" in result.context.skills_used
    assert "skill2" not in result.context.skills_used
