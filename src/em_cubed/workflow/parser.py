"""
WorkflowDagParser - Declarative YAML/JSON DAG Parser for em-cubed Workflows
=============================================================================
Parses YAML and JSON declarative DAG specifications into DistributedTask pipelines
with dependency validation and cycle detection.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from em_cubed.workflow.distributed import DistributedTask, TaskStatus


class WorkflowDagParser:
    """
    Parser for declarative workflow DAG definitions in YAML or JSON format.
    """

    @classmethod
    def parse_file(cls, file_path: Path | str) -> tuple[str, list[DistributedTask]]:
        """
        Parse a DAG specification file (YAML or JSON).
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Workflow DAG file not found: {path}")

        content = path.read_text(encoding="utf-8")
        if path.suffix.lower() in (".yaml", ".yml"):
            spec = yaml.safe_load(content)
        else:
            spec = json.loads(content)

        return cls.parse_dict(spec)

    @classmethod
    def parse_dict(cls, spec: dict[str, Any]) -> tuple[str, list[DistributedTask]]:
        """
        Parse a DAG dictionary specification.
        """
        workflow_id = spec.get("workflow_id", "declarative_dag")
        raw_tasks = spec.get("tasks", [])

        if not raw_tasks:
            raise ValueError("DAG specification contains no tasks.")

        task_map: dict[str, DistributedTask] = {}
        task_list: list[DistributedTask] = []

        for item in raw_tasks:
            tid = item.get("task_id")
            if not tid:
                raise ValueError("Every DAG task must specify a 'task_id'.")
            if tid in task_map:
                raise ValueError(f"Duplicate task_id '{tid}' in DAG specification.")

            skill_id = item.get("skill_id", "")
            deps = item.get("dependencies", [])
            input_data = item.get("input_data", {})
            max_retries = item.get("max_retries", 3)

            task = DistributedTask(
                task_id=tid,
                workflow_id=workflow_id,
                skill_id=skill_id,
                input_data=input_data,
                dependencies=deps,
                status=TaskStatus.PENDING,
                max_retries=max_retries,
            )
            task_map[tid] = task
            task_list.append(task)

        # Validate dependencies exist and detect cycles
        cls._validate_dependencies(task_map)

        return workflow_id, task_list

    @classmethod
    def _validate_dependencies(cls, task_map: dict[str, DistributedTask]) -> None:
        """
        Validate dependency existence and ensure DAG contains no cycles.
        """
        for tid, task in task_map.items():
            for dep in task.dependencies:
                if dep not in task_map:
                    raise ValueError(f"Task '{tid}' references unknown dependency '{dep}'.")

        # Topological sort / Cycle check via DFS
        visited: dict[str, int] = {tid: 0 for tid in task_map}  # 0: unvisited, 1: visiting, 2: visited

        def dfs(node_id: str) -> None:
            visited[node_id] = 1
            task = task_map[node_id]
            for dep in task.dependencies:
                if visited[dep] == 1:
                    raise ValueError(f"Cyclic dependency detected involving task '{dep}'.")
                if visited[dep] == 0:
                    dfs(dep)
            visited[node_id] = 2

        for tid in task_map:
            if visited[tid] == 0:
                dfs(tid)
