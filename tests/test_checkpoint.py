"""Tests for durable execution and checkpointing system."""

import tempfile
from pathlib import Path

from em_cubed.workflow.checkpoint import (
    Checkpoint,
    CheckpointManager,
    FileCheckpointStorage,
)


def test_checkpoint_creation():
    """Test creating a checkpoint."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_dir = Path(temp_dir) / "checkpoints"
        storage = FileCheckpointStorage(storage_dir)
        manager = CheckpointManager(storage)

        checkpoint_id = manager.create_checkpoint(
            workflow_id="test-workflow",
            execution_id="exec-123",
            step_name="step-1",
            state_data={"key": "value"},
            variables={"x": 42},
            context={"user": "test"},
            substrate={"shared": "data"},
        )

        assert checkpoint_id != ""
        assert len(checkpoint_id) > 0


def test_checkpoint_load_save():
    """Test saving and loading a checkpoint."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_dir = Path(temp_dir) / "checkpoints"
        storage = FileCheckpointStorage(storage_dir)
        manager = CheckpointManager(storage)

        # Create a checkpoint
        checkpoint_id = manager.create_checkpoint(
            workflow_id="test-workflow",
            execution_id="exec-123",
            step_name="step-1",
            state_data={"key": "value"},
            variables={"x": 42},
            context={"user": "test"},
            substrate={"shared": "data"},
        )

        # Load the checkpoint
        checkpoint = manager.load_checkpoint(checkpoint_id)

        assert checkpoint is not None
        assert checkpoint.workflow_id == "test-workflow"
        assert checkpoint.execution_id == "exec-123"
        assert checkpoint.step_name == "step-1"
        assert checkpoint.state_data == {"key": "value"}
        assert checkpoint.variables == {"x": 42}
        assert checkpoint.context == {"user": "test"}
        assert checkpoint.substrate == {"shared": "data"}


def test_checkpoint_listing():
    """Test listing checkpoints."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_dir = Path(temp_dir) / "checkpoints"
        storage = FileCheckpointStorage(storage_dir)
        manager = CheckpointManager(storage)

        # Create multiple checkpoints
        cp1 = manager.create_checkpoint(workflow_id="workflow-1", execution_id="exec-1", step_name="step-1")

        cp2 = manager.create_checkpoint(workflow_id="workflow-1", execution_id="exec-2", step_name="step-2")

        cp3 = manager.create_checkpoint(workflow_id="workflow-2", execution_id="exec-3", step_name="step-1")

        # List all checkpoints
        all_checkpoints = manager.list_checkpoints()
        assert len(all_checkpoints) >= 3
        assert cp1 in all_checkpoints
        assert cp2 in all_checkpoints
        assert cp3 in all_checkpoints

        # List checkpoints for specific workflow
        workflow1_checkpoints = manager.list_checkpoints("workflow-1")
        assert len(workflow1_checkpoints) >= 2
        assert cp1 in workflow1_checkpoints
        assert cp2 in workflow1_checkpoints
        assert cp3 not in workflow1_checkpoints  # Different workflow

        workflow2_checkpoints = manager.list_checkpoints("workflow-2")
        assert len(workflow2_checkpoints) >= 1
        assert cp3 in workflow2_checkpoints


def test_checkpoint_deletion():
    """Test deleting a checkpoint."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_dir = Path(temp_dir) / "checkpoints"
        storage = FileCheckpointStorage(storage_dir)
        manager = CheckpointManager(storage)

        # Create a checkpoint
        checkpoint_id = manager.create_checkpoint(
            workflow_id="test-workflow", execution_id="exec-123", step_name="step-1"
        )

        # Verify it exists
        checkpoint = manager.load_checkpoint(checkpoint_id)
        assert checkpoint is not None

        # Delete it
        result = manager.delete_checkpoint(checkpoint_id)
        assert result is True

        # Verify it's gone
        checkpoint = manager.load_checkpoint(checkpoint_id)
        assert checkpoint is None


def test_get_latest_checkpoint():
    """Test getting the latest checkpoint for a workflow."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_dir = Path(temp_dir) / "checkpoints"
        storage = FileCheckpointStorage(storage_dir)
        manager = CheckpointManager(storage)

        # Create checkpoints with small time differences
        manager.create_checkpoint(workflow_id="test-workflow", execution_id="exec-1", step_name="step-1")

        # Small delay to ensure different timestamps
        import time

        time.sleep(0.01)

        manager.create_checkpoint(workflow_id="test-workflow", execution_id="exec-2", step_name="step-2")

        # Get latest checkpoint
        latest = manager.get_latest_checkpoint("test-workflow")

        assert latest is not None
        assert latest.execution_id == "exec-2"  # Should be the later one
        assert latest.step_name == "step-2"


def test_checkpoint_storage_directly():
    """Test the FileCheckpointStorage directly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_dir = Path(temp_dir) / "checkpoints"
        storage = FileCheckpointStorage(storage_dir)

        # Create a checkpoint
        checkpoint = Checkpoint(
            workflow_id="test-workflow",
            execution_id="exec-123",
            step_name="test-step",
            state_data={"test": "data"},
            variables={"count": 5},
            context={"user": "tester"},
            substrate={"shared": "info"},
        )

        # Save it
        result = storage.save_checkpoint(checkpoint)
        assert result is True

        # Load it
        loaded = storage.load_checkpoint(checkpoint.checkpoint_id)
        assert loaded is not None
        assert loaded.workflow_id == checkpoint.workflow_id
        assert loaded.execution_id == checkpoint.execution_id
        assert loaded.step_name == checkpoint.step_name
        assert loaded.state_data == checkpoint.state_data
        assert loaded.variables == checkpoint.variables
        assert loaded.context == checkpoint.context
        assert loaded.substrate == checkpoint.substrate

        # List checkpoints
        ids = storage.list_checkpoints()
        assert checkpoint.checkpoint_id in ids

        # Delete it
        result = storage.delete_checkpoint(checkpoint.checkpoint_id)
        assert result is True

        # Verify it's gone
        loaded = storage.load_checkpoint(checkpoint.checkpoint_id)
        assert loaded is None


def test_hypergraph_compaction_and_causal_dag_integration():
    """Verify state mutations generated during workflow checkpoints append to causal_dag and compact hyperedges."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage = FileCheckpointStorage(Path(temp_dir))
        manager = CheckpointManager(storage)

        # Create a sequence of 3 execution checkpoints
        cp1 = manager.create_checkpoint("wf_alpha", "exec_999", "step_init")
        cp2 = manager.create_checkpoint("wf_alpha", "exec_999", "step_process")
        cp3 = manager.create_checkpoint("wf_alpha", "exec_999", "step_finalize")

        # 1. Causal DAG verification
        assert manager.causal_dag.verify_integrity() is True
        nodes = manager.causal_dag.all_nodes()
        assert len(nodes) == 3

        # Provenance trace for final step
        latest_node_id = manager._last_checkpoint_node_id["exec_999"]
        provenance = manager.causal_dag.trace_provenance(latest_node_id)
        assert len(provenance) == 3
        assert provenance[-1].payload["step_name"] == "step_finalize"
        assert provenance[0].payload["step_name"] == "step_init"

        # 2. Hypergraph compaction verification
        edges = manager.hypergraph_store.all_edges()
        assert len(edges) >= 1
        # Consolidated edge should contain shared entities wf_alpha and exec_999
        consolidated = manager.hypergraph_store.get_edge("consolidated_exec_exec_999")
        assert consolidated is not None
        assert "wf_alpha" in consolidated.member_entities
        assert "exec_999" in consolidated.member_entities


if __name__ == "__main__":
    test_checkpoint_creation()
    test_checkpoint_load_save()
    test_checkpoint_listing()
    test_checkpoint_deletion()
    test_get_latest_checkpoint()
    test_checkpoint_storage_directly()
    test_hypergraph_compaction_and_causal_dag_integration()
    print("All tests passed!")
