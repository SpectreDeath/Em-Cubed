"""Tests for distributed execution framework."""

from em_cubed.workflow.distributed import DistributedExecutor, DistributedTask, TaskStatus


def test_distributed_executor_creation():
    """Test that distributed executor can be created."""
    executor = DistributedExecutor()
    assert executor is not None


def test_submit_workflow():
    """Test submitting a workflow for distributed execution."""
    executor = DistributedExecutor()
    
    # Create test tasks
    task1 = DistributedTask(
        workflow_id="test-workflow",
        skill_id="skill-1",
        input_data={"param": "value"}
    )
    
    task2 = DistributedTask(
        workflow_id="test-workflow",
        skill_id="skill-2",
        input_data={"param": "value2"},
        dependencies=[task1.task_id]
    )
    
    # Submit workflow
    result = executor.submit_workflow("test-workflow", [task1, task2])
    assert result is True
    
    # Check that tasks are stored
    assert len(executor._tasks) == 2
    assert task1.task_id in executor._tasks
    assert task2.task_id in executor._tasks
    
    # Check workflow tracking
    assert "test-workflow" in executor._workflows
    assert len(executor._workflows["test-workflow"]) == 2


def test_get_task_status():
    """Test getting task status."""
    executor = DistributedExecutor()
    
    task = DistributedTask(
        workflow_id="test-workflow",
        skill_id="test-skill",
        input_data={}
    )
    
    executor.submit_workflow("test-workflow", [task])
    
    # Check initial status
    status = executor.get_task_status(task.task_id)
    assert status == TaskStatus.PENDING


def test_get_workflow_status():
    """Test getting workflow status."""
    executor = DistributedExecutor()
    
    # Create tasks
    task1 = DistributedTask(
        workflow_id="test-workflow",
        skill_id="skill-1",
        input_data={}
    )
    
    task2 = DistributedTask(
        workflow_id="test-workflow",
        skill_id="skill-2",
        input_data={}
    )
    
    executor.submit_workflow("test-workflow", [task1, task2])
    
    # Check workflow status
    status = executor.get_workflow_status("test-workflow")
    assert status["status"] == "pending"
    assert status["total_tasks"] == 2
    assert status["pending"] == 2
    
    # Complete one task
    task1.status = TaskStatus.COMPLETED
    task1.result = "success"
    
    status = executor.get_workflow_status("test-workflow")
    assert status["status"] == "pending"  # Still pending because task2 is pending
    assert status["completed"] == 1
    assert status["pending"] == 1
    
    # Complete second task
    task2.status = TaskStatus.COMPLETED
    task2.result = "success"
    
    status = executor.get_workflow_status("test-workflow")
    assert status["status"] == "completed"
    assert status["completed"] == 2


def test_get_task_result():
    """Test getting task result."""
    executor = DistributedExecutor()
    
    task = DistributedTask(
        workflow_id="test-workflow",
        skill_id="test-skill",
        input_data={}
    )
    
    executor.submit_workflow("test-workflow", [task])
    
    # Initially no result
    result = executor.get_task_result(task.task_id)
    assert result is None
    
    # Complete task
    task.status = TaskStatus.COMPLETED
    task.result = {"output": "test"}
    
    # Now we should get the result
    result = executor.get_task_result(task.task_id)
    assert result == {"output": "test"}


def test_cancel_workflow():
    """Test cancelling a workflow."""
    executor = DistributedExecutor()
    
    task = DistributedTask(
        workflow_id="test-workflow",
        skill_id="test-skill",
        input_data={}
    )
    
    executor.submit_workflow("test-workflow", [task])
    
    # Cancel workflow
    result = executor.cancel_workflow("test-workflow")
    assert result is True
    
    # Check task status
    status = executor.get_task_status(task.task_id)
    assert status == TaskStatus.FAILED
    assert task.error == "Workflow cancelled"


def test_task_serialization():
    """Test task serialization and deserialization."""
    original_task = DistributedTask(
        workflow_id="test-workflow",
        skill_id="test-skill",
        input_data={"key": "value"},
        dependencies=["dep1", "dep2"]
    )
    original_task.status = TaskStatus.RUNNING
    original_task.result = "partial"
    
    # Convert to dict
    task_dict = original_task.to_dict()
    
    # Convert back
    restored_task = DistributedTask.from_dict(task_dict)
    
    # Check that properties match
    assert restored_task.task_id == original_task.task_id
    assert restored_task.workflow_id == original_task.workflow_id
    assert restored_task.skill_id == original_task.skill_id
    assert restored_task.input_data == original_task.input_data
    assert restored_task.dependencies == original_task.dependencies
    assert restored_task.status == original_task.status
    assert restored_task.result == original_task.result


if __name__ == "__main__":
    test_distributed_executor_creation()
    test_submit_workflow()
    test_get_task_status()
    test_get_workflow_status()
    test_get_task_result()
    test_cancel_workflow()
    test_task_serialization()
    print("All tests passed!")