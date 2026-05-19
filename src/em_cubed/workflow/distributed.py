"""Distributed execution framework for Em-Cubed workflows."""

from __future__ import annotations

import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import structlog
import time

logger = structlog.get_logger()


class TaskStatus(Enum):
    """Status of a distributed task."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class DistributedTask:
    """A task to be executed in a distributed system."""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str = ""
    skill_id: str = ""
    input_data: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # Task IDs this depends on
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "workflow_id": self.workflow_id,
            "skill_id": self.skill_id,
            "input_data": self.input_data,
            "dependencies": self.dependencies,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DistributedTask':
        """Create from dictionary."""
        task = cls(
            task_id=data["task_id"],
            workflow_id=data["workflow_id"],
            skill_id=data["skill_id"],
            input_data=data.get("input_data", {}),
            dependencies=data.get("dependencies", []),
            max_retries=data.get("max_retries", 3)
        )
        task.status = TaskStatus(data["status"])
        task.result = data.get("result")
        task.error = data.get("error")
        task.created_at = data.get("created_at", time.time())
        task.started_at = data.get("started_at")
        task.completed_at = data.get("completed_at")
        task.retry_count = data.get("retry_count", 0)
        return task


class DistributedExecutor:
    """Base class for distributed workflow executors."""
    
    def __init__(self):
        self.logger = logger.bind(component="distributed_executor")
        self._tasks: Dict[str, DistributedTask] = {}
        self._workflows: Dict[str, List[str]] = {}  # workflow_id -> task_ids
    
    def submit_workflow(self, workflow_id: str, tasks: List[DistributedTask]) -> bool:
        """Submit a workflow for distributed execution.
        
        Args:
            workflow_id: Unique identifier for the workflow
            tasks: List of tasks to execute
            
        Returns:
            True if submission successful
        """
        try:
            self._workflows[workflow_id] = [task.task_id for task in tasks]
            for task in tasks:
                self._tasks[task.task_id] = task
            self.logger.info("Workflow submitted", workflow_id=workflow_id, task_count=len(tasks))
            return True
        except Exception as e:
            self.logger.error("Failed to submit workflow", workflow_id=workflow_id, error=str(e))
            return False
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the status of a task."""
        task = self._tasks.get(task_id)
        return task.status if task else None
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get the status of a workflow."""
        task_ids = self._workflows.get(workflow_id, [])
        if not task_ids:
            return {"status": "not_found"}
        
        tasks = [self._tasks[tid] for tid in task_ids if tid in self._tasks]
        if not tasks:
            return {"status": "no_tasks"}
        
        completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in tasks if t.status == TaskStatus.FAILED)
        running = sum(1 for t in tasks if t.status == TaskStatus.RUNNING)
        pending = sum(1 for t in tasks if t.status == TaskStatus.PENDING)
        
        if failed > 0:
            status = "failed"
        elif completed == len(tasks):
            status = "completed"
        elif running > 0:
            status = "running"
        else:
            status = "pending"
            
        return {
            "status": status,
            "total_tasks": len(tasks),
            "completed": completed,
            "failed": failed,
            "running": running,
            "pending": pending
        }
    
    def get_task_result(self, task_id: str) -> Optional[Any]:
        """Get the result of a completed task."""
        task = self._tasks.get(task_id)
        return task.result if task and task.status == TaskStatus.COMPLETED else None
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a workflow and all its tasks."""
        task_ids = self._workflows.get(workflow_id, [])
        for task_id in task_ids:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                    task.status = TaskStatus.FAILED
                    task.error = "Workflow cancelled"
        self.logger.info("Workflow cancelled", workflow_id=workflow_id)
        return True


# Global distributor instance
_distributed_executor: Optional[DistributedExecutor] = None


def get_distributed_executor() -> Optional[DistributedExecutor]:
    """Get the global distributed executor instance."""
    global _distributed_executor
    return _distributed_executor


def initialize_distributed_executor() -> DistributedExecutor:
    """Initialize the global distributed executor."""
    global _distributed_executor
    _distributed_executor = DistributedExecutor()
    logger.info("Distributed executor initialized")
    return _distributed_executor