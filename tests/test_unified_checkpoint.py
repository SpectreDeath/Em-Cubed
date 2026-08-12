"""Tests for the unified checkpoint layer (Phase 3).

Covers SQLiteCheckpointStorage + the DurableExecutionManager delegation.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from em_cubed.workflow.checkpoint import Checkpoint
from em_cubed.workflow.sqlite_checkpoint_storage import SQLiteCheckpointStorage


# ---------------------------------------------------------------------------
# SQLiteCheckpointStorage
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_storage(tmp_path: Path) -> SQLiteCheckpointStorage:
    return SQLiteCheckpointStorage(db_path=tmp_path / "test_checkpoints.db")


def _make_checkpoint(workflow_id: str = "wf1", step: str = "step1") -> Checkpoint:
    return Checkpoint(
        checkpoint_id=f"{workflow_id}-{step}",
        workflow_id=workflow_id,
        execution_id="exec-001",
        step_name=step,
        timestamp=time.time(),
        state_data={"status": "completed", "output": {"value": 42}},
        variables={"x": 1},
        context={"env": "test"},
        substrate={},
    )


def test_save_and_load_checkpoint(tmp_storage: SQLiteCheckpointStorage):
    cp = _make_checkpoint()
    assert tmp_storage.save_checkpoint(cp) is True

    loaded = tmp_storage.load_checkpoint(cp.checkpoint_id)
    assert loaded is not None
    assert loaded.checkpoint_id == cp.checkpoint_id
    assert loaded.workflow_id == cp.workflow_id
    assert loaded.step_name == cp.step_name


def test_load_missing_checkpoint_returns_none(tmp_storage: SQLiteCheckpointStorage):
    result = tmp_storage.load_checkpoint("does-not-exist")
    assert result is None


def test_list_checkpoints_all(tmp_storage: SQLiteCheckpointStorage):
    tmp_storage.save_checkpoint(_make_checkpoint("wf1", "step1"))
    tmp_storage.save_checkpoint(_make_checkpoint("wf2", "step1"))
    ids = tmp_storage.list_checkpoints()
    assert len(ids) == 2


def test_list_checkpoints_filtered_by_workflow(tmp_storage: SQLiteCheckpointStorage):
    tmp_storage.save_checkpoint(_make_checkpoint("wf1", "step1"))
    tmp_storage.save_checkpoint(_make_checkpoint("wf1", "step2"))
    tmp_storage.save_checkpoint(_make_checkpoint("wf2", "step1"))
    ids = tmp_storage.list_checkpoints(workflow_id="wf1")
    assert len(ids) == 2
    assert all("wf1" in i for i in ids)


def test_delete_checkpoint(tmp_storage: SQLiteCheckpointStorage):
    cp = _make_checkpoint()
    tmp_storage.save_checkpoint(cp)
    assert tmp_storage.delete_checkpoint(cp.checkpoint_id) is True
    assert tmp_storage.load_checkpoint(cp.checkpoint_id) is None


def test_save_step_shim(tmp_storage: SQLiteCheckpointStorage):
    """save_step() must persist a completed step retrievable via get_completed_steps()."""
    tmp_storage.save_step("workflow-x", "run_python", "completed", {"result": 99})
    completed = tmp_storage.get_completed_steps("workflow-x")
    assert "run_python" in completed
    assert completed["run_python"]["status"] == "completed"


def test_get_completed_steps_excludes_pending(tmp_storage: SQLiteCheckpointStorage):
    tmp_storage.save_step("wfp", "s1", "completed", {})
    tmp_storage.save_step("wfp", "s2", "pending", {})
    completed = tmp_storage.get_completed_steps("wfp")
    assert "s1" in completed
    assert "s2" not in completed


def test_clear_workflow(tmp_storage: SQLiteCheckpointStorage):
    tmp_storage.save_step("wf_clear", "s1", "completed", {})
    tmp_storage.save_step("wf_clear", "s2", "completed", {})
    tmp_storage.clear_workflow("wf_clear")
    assert tmp_storage.list_checkpoints(workflow_id="wf_clear") == []


# ---------------------------------------------------------------------------
# DurableExecutionManager delegation
# ---------------------------------------------------------------------------


def test_durable_manager_delegates_to_storage(tmp_path: Path):
    from em_cubed.workflow.durable_execution import DurableExecutionManager

    storage = SQLiteCheckpointStorage(db_path=tmp_path / "mgr.db")
    manager = DurableExecutionManager(storage=storage)

    # Save via manager
    ok = manager.save_step_checkpoint("wf-mgr", "step-a", "completed", {"val": 1})
    assert ok is True

    # Retrieve via storage directly — confirms delegation not independent state
    completed = storage.get_completed_steps("wf-mgr")
    assert "step-a" in completed


def test_durable_manager_clear(tmp_path: Path):
    from em_cubed.workflow.durable_execution import DurableExecutionManager

    storage = SQLiteCheckpointStorage(db_path=tmp_path / "clear.db")
    manager = DurableExecutionManager(storage=storage)
    manager.save_step_checkpoint("wf-c", "step-1", "completed", {})
    manager.clear_workflow_checkpoints("wf-c")
    assert manager.get_completed_steps("wf-c") == {}


def test_durable_manager_default_db_path():
    """DurableExecutionManager should accept a custom db_path for test isolation."""
    import tempfile
    from em_cubed.workflow.durable_execution import DurableExecutionManager
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    manager = DurableExecutionManager(db_path=db_path)
    assert manager.db_path == db_path
