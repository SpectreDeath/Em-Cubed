"""
Unit Tests for Dynamic Context Pipelining in em-cubed Workflows
================================================================
Tests template resolution ({{ tasks.task_id.result.field }}) across task outputs.
"""

from __future__ import annotations

import pytest

from em_cubed.workflow.distributed import resolve_template_value


class TestTemplatePipelining:
    """Test template resolution for DAG task data pipelining."""

    def test_single_template_resolution(self):
        task_results = {
            "fetch_metadata": {"cid": 2244, "name": "Aspirin", "details": {"active": True}},
        }

        res_cid = resolve_template_value("{{ tasks.fetch_metadata.result.cid }}", task_results)
        assert res_cid == 2244

        res_name = resolve_template_value("{{ tasks.fetch_metadata.result.name }}", task_results)
        assert res_name == "Aspirin"

        res_active = resolve_template_value("{{ tasks.fetch_metadata.result.details.active }}", task_results)
        assert res_active is True

    def test_nested_dict_template_resolution(self):
        task_results = {
            "step1": {"compounds": ["C1", "C2"], "score": 98.5},
        }

        input_payload = {
            "target": "{{ tasks.step1.result.compounds.0 }}",
            "metadata": {
                "score_val": "{{ tasks.step1.result.score }}",
                "label": "Score is {{ tasks.step1.result.score }}",
            },
        }

        resolved = resolve_template_value(input_payload, task_results)
        assert resolved["target"] == "C1"
        assert resolved["metadata"]["score_val"] == 98.5
        assert resolved["metadata"]["label"] == "Score is 98.5"
