"""
Unit Tests for WorkflowDagParser in em-cubed
=============================================
Tests YAML/JSON DAG parsing, dependency validation, and cycle detection.
"""

from __future__ import annotations

import pytest

from em_cubed.workflow.parser import WorkflowDagParser


class TestWorkflowDagParser:
    """Test Declarative Workflow DAG Parser."""

    def test_parse_valid_dict(self):
        spec = {
            "workflow_id": "test_pipeline",
            "tasks": [
                {
                    "task_id": "step1",
                    "skill_id": "skill_a",
                    "input_data": {"query": "hello"},
                },
                {
                    "task_id": "step2",
                    "skill_id": "skill_b",
                    "dependencies": ["step1"],
                    "input_data": {"data": "{{ tasks.step1.result.out }}"},
                },
            ],
        }

        workflow_id, tasks = WorkflowDagParser.parse_dict(spec)

        assert workflow_id == "test_pipeline"
        assert len(tasks) == 2
        assert tasks[0].task_id == "step1"
        assert tasks[1].dependencies == ["step1"]

    def test_unknown_dependency_raises_error(self):
        spec = {
            "workflow_id": "invalid_deps",
            "tasks": [
                {
                    "task_id": "step1",
                    "skill_id": "skill_a",
                    "dependencies": ["missing_step"],
                },
            ],
        }

        with pytest.raises(ValueError, match="unknown dependency 'missing_step'"):
            WorkflowDagParser.parse_dict(spec)

    def test_cyclic_dependency_raises_error(self):
        spec = {
            "workflow_id": "cyclic_deps",
            "tasks": [
                {"task_id": "step1", "dependencies": ["step2"]},
                {"task_id": "step2", "dependencies": ["step1"]},
            ],
        }

        with pytest.raises(ValueError, match="Cyclic dependency detected"):
            WorkflowDagParser.parse_dict(spec)
