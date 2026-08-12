"""Tests for dynamic skill auto-chaining engine."""

import pytest
from em_cubed.skills.auto_chain import AutoChainer


def test_auto_chainer_synthesizes_pipeline():
    chainer = AutoChainer()
    res = chainer.find_chain(
        input_schema={"dataset": "csv", "features": "list"},
        goal_description="optimization algorithm",
        max_depth=3,
    )

    assert res["status"] == "ok"
    assert "pipeline" in res
    assert res["pipeline_length"] > 0
    first_step = res["pipeline"][0]
    assert "surface" in first_step
    assert "compatibility_score" in first_step
