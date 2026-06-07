"""Distributed execution framework for Em-Cubed workflows."""

from __future__ import annotations

import asyncio
import threading
import time
import uuid
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
import structlog

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

    def shutdown(self) -> None:
        """Shutdown the executor."""
        pass


def _execute_distributed_task(task_dict: Dict[str, Any], skills_dir_str: str) -> Dict[str, Any]:
    """Independent worker process function that executes a skill task."""
    try:
        from pathlib import Path
        import asyncio
        from em_cubed.plugin_manager import PluginManager
        from em_cubed.skills.registry import SkillRegistry
        from em_cubed.skills.executor import SkillExecutor, SkillExecutionRequest
        
        # Initialize an isolated event loop for this worker process
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        skills_dir = Path(skills_dir_str)
        plugin_manager = PluginManager()
        
        # Load registry dynamically relative to skills_dir or current working dir
        registry = SkillRegistry(skills_dir, skills_dir / "registry.json")
        executor = SkillExecutor(plugin_manager, registry, skills_dir)
        
        # Construct and dispatch execution request
        request = SkillExecutionRequest(
            skill_id=task_dict["skill_id"],
            input_data=task_dict.get("input_data", {})
        )
        
        async def run():
            return await executor.execute(request)
            
        result = loop.run_until_complete(run())
        loop.close()
        
        return {
            "success": result.success,
            "output": result.output,
            "error": result.error,
            "execution_time_ms": result.execution_time_ms
        }
    except Exception as e:
        return {
            "success": False,
            "output": None,
            "error": str(e),
            "execution_time_ms": 0.0
        }


class ProcessDistributedExecutor(DistributedExecutor):
    """Actual distributed task executor that runs tasks in separate sandboxed OS processes."""
    
    def __init__(self, skills_dir: Path, max_workers: int = 4):
        super().__init__()
        self.skills_dir = skills_dir
        self._max_workers = max_workers
        self._process_executor = ProcessPoolExecutor(max_workers=max_workers)
        self._futures: Dict[str, Any] = {}
        self._scheduler_tasks: Dict[str, asyncio.Task] = {}
        self._callback_lock = threading.Lock()  # Guards _tasks mutations in done-callbacks
        
    def submit_workflow(self, workflow_id: str, tasks: List[DistributedTask]) -> bool:
        """Submit a workflow and start scheduling tasks across workers."""
        success = super().submit_workflow(workflow_id, tasks)
        if not success:
            return False

        # Spawn asynchronous scheduling pipeline.
        # Prefer an already-running loop (async call sites); fall back to
        # creating and setting a new loop (sync CLI call sites).
        try:
            loop = asyncio.get_running_loop()
            sched_task = loop.create_task(self._scheduler_loop(workflow_id))
            self._scheduler_tasks[workflow_id] = sched_task
        except RuntimeError:
            # No running event loop — caller is synchronous (e.g. CLI).
            # Schedule via a dedicated thread so the caller is not blocked.
            import threading as _threading

            def _run_loop():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    new_loop.run_until_complete(self._scheduler_loop(workflow_id))
                finally:
                    new_loop.close()

            t = _threading.Thread(target=_run_loop, daemon=True, name=f"dag-scheduler-{workflow_id[:8]}")
            t.start()
        return True
        
    async def _scheduler_loop(self, workflow_id: str):
        """Asynchronous scheduler that submits tasks when dependencies are completed."""
        task_ids = self._workflows.get(workflow_id, [])
        
        while True:
            # Check if all tasks in the workflow are done/failed
            all_done = True
            for tid in task_ids:
                task = self._tasks[tid]
                if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                    all_done = False
                    
            if all_done:
                break
                
            for tid in task_ids:
                task = self._tasks[tid]
                if task.status != TaskStatus.PENDING:
                    continue
                    
                # Verify that all parent task dependencies are fully completed
                deps_satisfied = True
                for dep_id in task.dependencies:
                    dep_task = self._tasks.get(dep_id)
                    if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                        deps_satisfied = False
                        break
                        
                if deps_satisfied:
                    # Promote task to RUNNING status
                    task.status = TaskStatus.RUNNING
                    task.started_at = time.time()
                    
                    # Offload compilation/execution to ProcessPoolExecutor
                    loop = asyncio.get_running_loop()
                    fut = loop.run_in_executor(
                        self._process_executor,
                        _execute_distributed_task,
                        task.to_dict(),
                        str(self.skills_dir)
                    )
                    
                    self._futures[task.task_id] = fut
                    fut.add_done_callback(
                        lambda f, t_id=task.task_id: self._task_completed_callback(t_id, f)  # type: ignore[misc]
                    )
                    
            await asyncio.sleep(0.05)
    
    def _task_completed_callback(self, task_id: str, future: Any):
        """Callback triggered when a worker process finishes task execution."""
        with self._callback_lock:
            try:
                res = future.result()
                task = self._tasks[task_id]
                task.completed_at = time.time()
                if res["success"]:
                    task.status = TaskStatus.COMPLETED
                    task.result = res["output"]
                    self.logger.info("Distributed task completed successfully", task_id=task_id)
                    
                    # Checkpoint progress durably using global manager (if initialised)
                    from em_cubed.workflow.checkpoint import get_checkpoint_manager
                    manager = get_checkpoint_manager()
                    if manager is not None:
                        manager.create_checkpoint(
                            workflow_id=task.workflow_id,
                            execution_id=task_id,
                            step_name=f"task_{task.skill_id}",
                            state_data={"result": task.result}
                        )
                    else:
                        self.logger.warning(
                            "CheckpointManager not initialised; task result not persisted",
                            task_id=task_id,
                        )
                else:
                    task.status = TaskStatus.FAILED
                    task.error = res["error"]
                    self.logger.error("Distributed task failed", task_id=task_id, error=res["error"])
            except Exception:
                task = self._tasks[task_id]
                task.status = TaskStatus.FAILED
                task.error = str(future.exception())
                self.logger.exception("Error retrieving distributed task result", task_id=task_id)
            
    def shutdown(self) -> None:
        """Clean up worker process execution pools."""
        self._process_executor.shutdown(wait=False)


# Global distributor instance
_distributed_executor: Optional[DistributedExecutor] = None


def get_distributed_executor() -> Optional[DistributedExecutor]:
    """Get the global distributed executor instance."""
    global _distributed_executor
    return _distributed_executor


def initialize_distributed_executor(skills_dir: Optional[Path] = None) -> DistributedExecutor:
    """Initialize the global distributed executor."""
    global _distributed_executor
    if skills_dir:
        _distributed_executor = ProcessDistributedExecutor(skills_dir)
        logger.info("Distributed Process executor initialized", skills_dir=str(skills_dir))
    else:
        _distributed_executor = DistributedExecutor()
        logger.info("In-memory Distributed executor initialized (portable mode)")
    return _distributed_executor