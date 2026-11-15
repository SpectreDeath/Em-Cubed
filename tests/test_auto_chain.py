"""Tests for dynamic skill auto-chaining engine."""

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
    assert "input_mapping" in first_step
    assert "produced_outputs" in first_step


def test_auto_chainer_builds_composition_plan():
    chainer = AutoChainer()
    plan = chainer.build_composition_plan(
        input_schema={"data": "matrix"},
        goal_description="optimization algorithm",
        max_depth=2,
    )

    assert plan.name is not None
    assert len(plan.steps) > 0
    assert plan.steps[0].skill_id is not None


async def test_auto_chainer_execute_empty_goal():
    chainer = AutoChainer()
    res = await chainer.execute_chain(
        input_data={"data": "test"},
        goal_description="nonexistent_xyz_impossible_goal_12345",
        max_depth=2,
    )
    assert res.success is False
    assert res.error is not None

