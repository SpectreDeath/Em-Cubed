"""Distributed execution framework for Em-Cubed workflows."""

from __future__ import annotations

import asyncio
import re
import threading
import time
import uuid
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import structlog

from em_cubed.workflow.worker_spec import SkillWorkerSpec

logger = structlog.get_logger()


_TMPL_PATTERN = re.compile(
    r"\{\{\s*tasks\.([a-zA-Z0-9_-]+)(?:\.(?:result|output|\$\.))?"
    r"\.?([a-zA-Z0-9_.-]+)?\s*\}\}"
)


def _resolve_path(root: Any, path_str: str | None) -> Any:
    """Walk a dot-separated path into a nested dict/list."""
    if not path_str or root is None:
        return root
    curr = root
    for part in path_str.split("."):
        if isinstance(curr, dict):
            if part not in curr:
                if "result" in curr and isinstance(curr["result"], dict) and part in curr["result"]:
                    curr = curr["result"].get(part)
                    continue
                elif "output" in curr and isinstance(curr["output"], dict) and part in curr["output"]:
                    curr = curr["output"].get(part)
                    continue
            curr = curr.get(part)
        elif isinstance(curr, list) and part.isdigit():
            idx = int(part)
            curr = curr[idx] if 0 <= idx < len(curr) else None
        else:
            return None
        if curr is None:
            return None
    return curr


def resolve_template_value(val: Any, task_results: dict[str, Any]) -> Any:
    """
    Resolve template placeholders like '{{ tasks.task_id.result.field }}' from completed parent task results.
    """
    if isinstance(val, str) and "{{" in val and "}}" in val:
        full_match = _TMPL_PATTERN.fullmatch(val.strip())
        if full_match:
            dep_id, path_str = full_match.groups()
            dep_res = task_results.get(dep_id)
            if dep_res is None:
                return val
            res = _resolve_path(dep_res, path_str)
            return res if res is not None else val

        def _replace_match(match: re.Match) -> str:
            dep_id, path_str = match.groups()
            dep_res = task_results.get(dep_id)
            if dep_res is None:
                return match.group(0)
            res = _resolve_path(dep_res, path_str)
            return str(res) if res is not None else match.group(0)

        return _TMPL_PATTERN.sub(_replace_match, val)

    elif isinstance(val, dict):
        return {k: resolve_template_value(v, task_results) for k, v in val.items()}
    elif isinstance(val, list):
        return [resolve_template_value(item, task_results) for item in val]
    return val


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
    input_data: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)  # Task IDs this depends on
    status: TaskStatus = TaskStatus.PENDING
    result: Any | None = None
    error: str | None = None
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    completed_at: float | None = None
    retry_count: int = 0
    max_retries: int = 3

    def to_dict(self) -> dict[str, Any]:
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
            "max_retries": self.max_retries,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DistributedTask:
        """Create from dictionary."""
        task = cls(
            task_id=data["task_id"],
            workflow_id=data["workflow_id"],
            skill_id=data["skill_id"],
            input_data=data.get("input_data", {}),
            dependencies=data.get("dependencies", []),
            max_retries=data.get("max_retries", 3),
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
        self._tasks: dict[str, DistributedTask] = {}
        self._workflows: dict[str, list[str]] = {}  # workflow_id -> task_ids

    def submit_workflow(self, workflow_id: str, tasks: list[DistributedTask]) -> bool:
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

    def get_task_status(self, task_id: str) -> TaskStatus | None:
        """Get the status of a task."""
        task = self._tasks.get(task_id)
        return task.status if task else None

    def get_workflow_status(self, workflow_id: str) -> dict[str, Any]:
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
            "pending": pending,
        }

    def get_task_result(self, task_id: str) -> Any | None:
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
        # nosec B110 - intentional fallback; caller handles None/False return


def _execute_distributed_task(
    task: "SkillWorkerSpec | dict[str, Any]",
    skills_dir_str: str = "skills",
) -> dict[str, Any]:
    """Independent worker-process function that executes a skill task.

    Accepts either a ``SkillWorkerSpec`` (preferred) or the legacy ``task_dict``
    format for backward compatibility during the transition period.

    When a ``SkillWorkerSpec`` is supplied the worker executes the pre-resolved
    code directly without touching ``PluginManager``, ``SkillRegistry``, or
    ``SkillExecutor``.  When a plain dict is supplied the legacy path is used.
    """
    # ------------------------------------------------------------------
    # Fast path: SkillWorkerSpec — no plugin stack required
    # ------------------------------------------------------------------
    if isinstance(task, SkillWorkerSpec):
        try:
            import asyncio

            code = task.get_code()
            if code is None:
                return {
                    "success": False,
                    "output": None,
                    "error": f"No code for surface '{task.surface_name}' in skill '{task.skill_id}'",
                    "execution_time_ms": 0.0,
                }

            # Lightweight surface instantiation — only the requested surface is imported.
            surface_instance = _get_surface_by_name(task.surface_name)
            if surface_instance is None:
                return {
                    "success": False,
                    "output": None,
                    "error": f"Surface '{task.surface_name}' not available in worker process",
                    "execution_time_ms": 0.0,
                }

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                import time
                t0 = time.perf_counter()
                result = loop.run_until_complete(
                    surface_instance.execute(code, task.input_data)
                )
                elapsed_ms = (time.perf_counter() - t0) * 1000
            finally:
                loop.close()

            success = result.get("status") == "ok"
            return {
                "success": success,
                "output": result.get("value") if success else None,
                "error": result.get("message") if not success else None,
                "execution_time_ms": elapsed_ms,
            }
        except Exception as exc:
            return {"success": False, "output": None, "error": str(exc), "execution_time_ms": 0.0}

    # ------------------------------------------------------------------
    # Legacy path: plain dict — re-uses the old plugin stack approach
    # ------------------------------------------------------------------
    task_dict: dict[str, Any] = task  # type: ignore[assignment]
    try:
        import asyncio
        from pathlib import Path

        from em_cubed.plugin_manager import PluginManager
        from em_cubed.skills.executor import SkillExecutionRequest, SkillExecutor
        from em_cubed.skills.registry import SkillRegistry

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        skills_dir = Path(skills_dir_str)
        plugin_manager = PluginManager()

        registry_candidates = [
            Path.cwd() / "registry.json",
            skills_dir / "registry.json",
            skills_dir.parent / "registry.json",
        ]
        registry_file = next((p for p in registry_candidates if p.exists()), skills_dir / "registry.json")
        registry = SkillRegistry(skills_dir, registry_file)
        executor = SkillExecutor(plugin_manager, registry, skills_dir)

        request = SkillExecutionRequest(skill_id=task_dict["skill_id"], input_data=task_dict.get("input_data", {}))

        async def run():
            return await executor.execute(request)

        result = loop.run_until_complete(run())
        loop.close()

        return {
            "success": result.success,
            "output": result.output,
            "error": result.error,
            "execution_time_ms": result.execution_time_ms,
        }
    except Exception as exc:
        return {"success": False, "output": None, "error": str(exc), "execution_time_ms": 0.0}


def _get_surface_by_name(name: str):
    """Lightweight surface factory for the isolated worker path.

    Imports only the requested surface class, not the full PluginManager stack.
    Returns ``None`` if the surface is unknown or unavailable.
    """
    _SURFACE_MAP = {
        "python": "em_cubed.surfaces.python_surface:PythonSurface",
        "prolog": "em_cubed.surfaces.prolog_surface:PrologSurface",
        "z3": "em_cubed.surfaces.z3_surface:Z3Surface",
        "datalog": "em_cubed.surfaces.datalog_surface:DatalogSurface",
        "sqlite": "em_cubed.surfaces.sqlite_surface:SQLiteSurface",
        "hy": "em_cubed.surfaces.hy_surface:HySurface",
        "kanren": "em_cubed.surfaces.kanren_surface:KanrenSurface",
        "clingo": "em_cubed.surfaces.clingo_surface:ClingoSurface",
        "quickjs": "em_cubed.surfaces.quickjs_surface:QuickJSSurface",
        "wasm": "em_cubed.surfaces.wasm_surface:WASMSurface",
        "janus": "em_cubed.surfaces.janus_surface:JanusSurface",
        "polars": "em_cubed.surfaces.polars_surface:PolarsSurface",
        "duckdb": "em_cubed.surfaces.duckdb_surface:DuckDBSurface",
    }
    spec = _SURFACE_MAP.get(name)
    if spec is None:
        return None
    try:
        module_path, class_name = spec.rsplit(":", 1)
        import importlib
        mod = importlib.import_module(module_path)
        cls = getattr(mod, class_name)
        instance = cls()
        return instance if getattr(instance, "available", True) else None
    except Exception:
        return None


class ProcessDistributedExecutor(DistributedExecutor):
    """Actual distributed task executor that runs tasks in separate sandboxed OS processes."""

    def __init__(self, skills_dir: Path, max_workers: int = 4):
        super().__init__()
        self.skills_dir = skills_dir
        self._max_workers = max_workers
        self._process_executor = ProcessPoolExecutor(max_workers=max_workers)
        self._futures: dict[str, Any] = {}
        self._scheduler_tasks: dict[str, asyncio.Task] = {}
        self._callback_lock = threading.Lock()  # Guards _tasks mutations in done-callbacks

    def submit_workflow(self, workflow_id: str, tasks: list[DistributedTask]) -> bool:
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
                    # Resolve dynamic template placeholders from parent task results
                    completed_results = {
                        dep_id: self._tasks[dep_id].result
                        for dep_id in task.dependencies
                        if dep_id in self._tasks and self._tasks[dep_id].result is not None
                    }
                    if completed_results and task.input_data:
                        task.input_data = resolve_template_value(task.input_data, completed_results)

                    # Promote task to RUNNING status
                    task.status = TaskStatus.RUNNING
                    task.started_at = time.time()

                    # Offload compilation/execution to ProcessPoolExecutor
                    loop = asyncio.get_running_loop()
                    fut = loop.run_in_executor(
                        self._process_executor, _execute_distributed_task, task.to_dict(), str(self.skills_dir)
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
                            state_data={"result": task.result},
                        )
                    else:
                        self.logger.warning(
                            "CheckpointManager not initialised; task result not persisted",
                            task_id=task_id,
                        )
                else:
                    if task.retry_count < task.max_retries:
                        task.retry_count += 1
                        task.status = TaskStatus.RETRYING
                        self.logger.warning(
                            f"Task failed, retrying (attempt {task.retry_count}/{task.max_retries})",
                            task_id=task_id,
                            error=res.get("error"),
                        )
                        backoff_sec = 0.1 * (2 ** (task.retry_count - 1))
                        timer = threading.Timer(backoff_sec, self._reset_task_to_pending, args=[task_id])
                        timer.daemon = True
                        timer.start()
                    else:
                        task.status = TaskStatus.FAILED
                        task.error = res["error"]
                        self.logger.error(
                            "Distributed task failed after max retries", task_id=task_id, error=res["error"]
                        )
            except Exception as e:
                task = self._tasks[task_id]
                if task.retry_count < task.max_retries:
                    task.retry_count += 1
                    task.status = TaskStatus.RETRYING
                    self.logger.warning(
                        f"Task exception, retrying (attempt {task.retry_count}/{task.max_retries})",
                        task_id=task_id,
                        error=str(e),
                    )
                    backoff_sec = 0.1 * (2 ** (task.retry_count - 1))
                    timer = threading.Timer(backoff_sec, self._reset_task_to_pending, args=[task_id])
                    timer.daemon = True
                    timer.start()
                else:
                    task.status = TaskStatus.FAILED
                    task.error = str(future.exception()) if hasattr(future, "exception") else str(e)
                    self.logger.exception("Error retrieving distributed task result", task_id=task_id)

    def _reset_task_to_pending(self, task_id: str) -> None:
        """Reset retrying task status back to PENDING for re-scheduling."""
        with self._callback_lock:
            if task_id in self._tasks:
                self._tasks[task_id].status = TaskStatus.PENDING

    def shutdown(self) -> None:
        """Clean up worker process execution pools."""
        try:
            processes = getattr(self._process_executor, "_processes", None)
            if processes:
                for p in list(processes):
                    try:
                        p.terminate()
                        p.kill()
                    except Exception:
                        pass  # nosec B110 - intentional fallback; caller handles None/False return
        except Exception:
            pass  # nosec B110 - intentional fallback; caller handles None/False return
        self._process_executor.shutdown(wait=False)


class AdaptiveWorkerPool:
    """
    Monitors system CPU and Memory telemetry to dynamically scale worker process pool limits.
    """

    def __init__(self, min_workers: int = 2, max_workers: int = 8) -> None:
        self.min_workers = min_workers
        self.max_workers = max_workers

    def calculate_optimal_workers(self) -> int:
        """Calculate optimal worker process count based on CPU and RAM utilization."""
        try:
            import psutil

            cpu_usage = psutil.cpu_percent(interval=None)
            mem_usage = psutil.virtual_memory().percent

            if cpu_usage > 85.0 or mem_usage > 90.0:
                return self.min_workers
            elif cpu_usage > 65.0 or mem_usage > 75.0:
                return max(self.min_workers, self.max_workers // 2)
            else:
                return self.max_workers
        except Exception:
            return self.max_workers


# Global distributor instance
_distributed_executor: DistributedExecutor | None = None


def get_distributed_executor() -> DistributedExecutor | None:
    """Get the global distributed executor instance."""
    global _distributed_executor
    return _distributed_executor


def initialize_distributed_executor(skills_dir: Path | None = None) -> DistributedExecutor:
    """Initialize the global distributed executor."""
    global _distributed_executor
    if skills_dir:
        _distributed_executor = ProcessDistributedExecutor(skills_dir)
        logger.info("Distributed Process executor initialized", skills_dir=str(skills_dir))
    else:
        _distributed_executor = DistributedExecutor()
        logger.info("In-memory Distributed executor initialized (portable mode)")
    return _distributed_executor
