"""Tests for the SkillWorkerSpec dataclass and the distributed worker isolation.

This file fills out the previously near-empty tests/test_worker.py.
"""

from __future__ import annotations

from typing import Any

import pytest

from em_cubed.workflow.worker_spec import SkillWorkerSpec


# ---------------------------------------------------------------------------
# SkillWorkerSpec construction and behaviour
# ---------------------------------------------------------------------------


def test_worker_spec_defaults():
    spec = SkillWorkerSpec(skill_id="my-skill", surface_name="python")
    assert spec.skill_id == "my-skill"
    assert spec.surface_name == "python"
    assert spec.code_blocks == {}
    assert spec.input_data == {}
    assert spec.timeout == 30.0


def test_worker_spec_get_code_present():
    spec = SkillWorkerSpec(
        skill_id="my-skill",
        surface_name="python",
        code_blocks={"python": "result = 42"},
    )
    assert spec.get_code() == "result = 42"


def test_worker_spec_get_code_missing():
    spec = SkillWorkerSpec(
        skill_id="my-skill",
        surface_name="prolog",
        code_blocks={"python": "result = 42"},  # no prolog code
    )
    assert spec.get_code() is None


def test_worker_spec_multi_surface():
    spec = SkillWorkerSpec(
        skill_id="poly-skill",
        surface_name="z3",
        code_blocks={"python": "x = 1", "z3": "(assert (= x 1))"},
        input_data={"x": 1},
        timeout=60.0,
    )
    assert spec.get_code() == "(assert (= x 1))"
    assert spec.timeout == 60.0


def test_worker_spec_is_picklable():
    """SkillWorkerSpec must be pickle-safe for ProcessPoolExecutor."""
    import pickle

    spec = SkillWorkerSpec(
        skill_id="pickle-test",
        surface_name="python",
        code_blocks={"python": "result = 'hello'"},
        input_data={"val": 42},
        timeout=5.0,
    )
    serialized = pickle.dumps(spec)
    restored = pickle.loads(serialized)

    assert restored.skill_id == spec.skill_id
    assert restored.surface_name == spec.surface_name
    assert restored.code_blocks == spec.code_blocks
    assert restored.input_data == spec.input_data
    assert restored.timeout == spec.timeout
    assert restored.get_code() == "result = 'hello'"


# ---------------------------------------------------------------------------
# _execute_distributed_task fast path (SkillWorkerSpec)
# ---------------------------------------------------------------------------


def test_execute_distributed_task_missing_code():
    """When spec has no code for the requested surface, return failure dict."""
    from em_cubed.workflow.distributed import _execute_distributed_task

    spec = SkillWorkerSpec(
        skill_id="no-code-skill",
        surface_name="prolog",
        code_blocks={"python": "x = 1"},  # no prolog code
    )
    result = _execute_distributed_task(spec)
    assert result["success"] is False
    assert "prolog" in result["error"]


def test_execute_distributed_task_unknown_surface():
    """When spec requests an unknown surface, return failure dict."""
    from em_cubed.workflow.distributed import _execute_distributed_task

    spec = SkillWorkerSpec(
        skill_id="bad-surface-skill",
        surface_name="nonexistent_surface",
        code_blocks={"nonexistent_surface": "x = 1"},
    )
    result = _execute_distributed_task(spec)
    assert result["success"] is False


def test_execute_distributed_task_legacy_dict_error():
    """Legacy dict path with a bad skill_id returns success=False without crashing."""
    from em_cubed.workflow.distributed import _execute_distributed_task

    legacy_dict = {"skill_id": "__nonexistent_skill__", "input_data": {}}
    result = _execute_distributed_task(legacy_dict, "skills")
    assert result["success"] is False
    assert result["output"] is None
    assert isinstance(result["error"], str)


# ---------------------------------------------------------------------------
# _get_surface_by_name
# ---------------------------------------------------------------------------


def test_get_surface_by_name_known_returns_instance_or_none():
    """Known surface names must not raise — they return an instance or None if unavailable."""
    from em_cubed.workflow.distributed import _get_surface_by_name

    # Python surface should always be available in the test environment
    python_surface = _get_surface_by_name("python")
    # Either a surface instance or None (if asteval not installed in this CI env)
    assert python_surface is None or hasattr(python_surface, "execute")


def test_get_surface_by_name_unknown_returns_none():
    from em_cubed.workflow.distributed import _get_surface_by_name

    result = _get_surface_by_name("totally_unknown_surface_xyz")
    assert result is None


# ---------------------------------------------------------------------------
# PolyglotWorker (existing class) still works after our changes
# ---------------------------------------------------------------------------


def test_polyglot_worker_construction():
    from em_cubed.workflow.worker import PolyglotWorker

    w = PolyglotWorker(surfaces=["python", "prolog"], skills_dir="skills", registry_file="registry.json")
    assert "python" in w.surfaces
    assert "prolog" in w.surfaces


def test_polyglot_worker_max_tasks_stop():
    """Worker should stop cleanly after max_tasks iterations."""
    from em_cubed.workflow.worker import PolyglotWorker

    w = PolyglotWorker()
    # Should exit after 1 poll without error
    w.run(poll_interval=0.001, max_tasks=1)
