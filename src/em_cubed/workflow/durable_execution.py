"""Durable execution & checkpoint recovery engine for resilient workflow execution.

Delegates persistence to ``SQLiteCheckpointStorage`` (which implements the
``CheckpointStorage`` ABC) rather than maintaining its own raw SQLite schema.
The public API (``save_step_checkpoint``, ``get_completed_steps``,
``clear_workflow_checkpoints``) is unchanged so existing callers are unaffected.
"""

from pathlib import Path
from typing import Any

import structlog

from em_cubed.workflow.sqlite_checkpoint_storage import SQLiteCheckpointStorage

logger = structlog.get_logger()


class DurableExecutionManager:
    """Manages workflow execution checkpoints, state persistence, and resume recovery.

    Parameters
    ----------
    db_path:
        Path to the SQLite database.  Defaults to ``.workflow_checkpoints.db``
        in the current working directory.
    storage:
        Optional pre-constructed ``SQLiteCheckpointStorage`` instance.  When
        supplied *db_path* is ignored.  Useful for injecting a shared storage
        instance or for testing.
    """

    def __init__(
        self,
        db_path: Path | None = None,
        storage: SQLiteCheckpointStorage | None = None,
    ) -> None:
        if storage is not None:
            self._storage = storage
        else:
            self._storage = SQLiteCheckpointStorage(db_path)
        # Expose db_path for backward-compat with any callers that read it.
        self.db_path = self._storage.db_path

    def save_step_checkpoint(
        self,
        workflow_id: str,
        step_id: str,
        status: str,
        output: dict[str, Any] | None = None,
    ) -> bool:
        """Save a step execution checkpoint.

        Delegates to ``SQLiteCheckpointStorage.save_step()``.
        """
        result = self._storage.save_step(
            workflow_id=workflow_id, step_id=step_id, status=status, output=output
        )
        if result:
            logger.info("Saved step checkpoint", workflow_id=workflow_id, step_id=step_id, status=status)
        else:
            logger.error("Failed to save step checkpoint", workflow_id=workflow_id, step_id=step_id)
        return result

    def get_completed_steps(self, workflow_id: str) -> dict[str, dict[str, Any]]:
        """Retrieve completed step checkpoints for a workflow to allow resume recovery."""
        return self._storage.get_completed_steps(workflow_id)

    def clear_workflow_checkpoints(self, workflow_id: str) -> None:
        """Clear all stored checkpoints for a given workflow."""
        self._storage.clear_workflow(workflow_id)
