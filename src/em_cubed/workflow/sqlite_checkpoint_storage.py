"""SQLiteCheckpointStorage: adapts the simple DurableExecutionManager SQLite schema
to the CheckpointStorage ABC defined in workflow/checkpoint.py.

This allows DurableExecutionManager to delegate to CheckpointManager rather than
maintaining its own raw SQLite connection logic.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import structlog

from em_cubed.workflow.checkpoint import Checkpoint, CheckpointStorage

logger = structlog.get_logger()


class SQLiteCheckpointStorage(CheckpointStorage):
    """CheckpointStorage backend backed by a SQLite database.

    Schema is intentionally minimal to remain compatible with the existing
    ``DurableExecutionManager`` table format while also supporting the richer
    ``Checkpoint`` dataclass fields via a ``state_json`` column.
    """

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or Path(".workflow_checkpoints.db")
        self._init_db()

    def _init_db(self) -> None:
        """Create checkpoint table if it does not already exist."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS em3_checkpoints (
                    checkpoint_id  TEXT PRIMARY KEY,
                    workflow_id    TEXT NOT NULL,
                    execution_id   TEXT NOT NULL DEFAULT '',
                    step_name      TEXT NOT NULL DEFAULT '',
                    status         TEXT NOT NULL DEFAULT 'pending',
                    state_json     TEXT NOT NULL DEFAULT '{}',
                    timestamp      REAL NOT NULL DEFAULT 0.0
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # CheckpointStorage ABC implementation
    # ------------------------------------------------------------------

    def save_checkpoint(self, checkpoint: Checkpoint) -> bool:
        """Persist a Checkpoint to SQLite."""
        try:
            conn = sqlite3.connect(self.db_path)
            try:
                state_json = json.dumps(
                    {
                        "state_data": checkpoint.state_data,
                        "variables": checkpoint.variables,
                        "context": checkpoint.context,
                        "substrate": checkpoint.substrate,
                    }
                )
                conn.execute(
                    """
                    INSERT OR REPLACE INTO em3_checkpoints
                        (checkpoint_id, workflow_id, execution_id, step_name, status, state_json, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        checkpoint.checkpoint_id,
                        checkpoint.workflow_id,
                        checkpoint.execution_id,
                        checkpoint.step_name,
                        checkpoint.state_data.get("status", "pending"),
                        state_json,
                        checkpoint.timestamp,
                    ),
                )
                conn.commit()
                logger.debug(
                    "SQLiteCheckpointStorage: saved checkpoint",
                    checkpoint_id=checkpoint.checkpoint_id,
                    workflow_id=checkpoint.workflow_id,
                )
                return True
            finally:
                conn.close()
        except Exception as exc:
            logger.error("SQLiteCheckpointStorage: save failed", error=str(exc))
            return False

    def load_checkpoint(self, checkpoint_id: str) -> Checkpoint | None:
        """Load a Checkpoint by its checkpoint_id."""
        try:
            conn = sqlite3.connect(self.db_path)
            try:
                row = conn.execute(
                    "SELECT checkpoint_id, workflow_id, execution_id, step_name, state_json, timestamp "
                    "FROM em3_checkpoints WHERE checkpoint_id = ?",
                    (checkpoint_id,),
                ).fetchone()
            finally:
                conn.close()

            if row is None:
                return None

            cp_id, wf_id, exec_id, step_name, state_json, ts = row
            extra = json.loads(state_json) if state_json else {}
            return Checkpoint(
                checkpoint_id=cp_id,
                workflow_id=wf_id,
                execution_id=exec_id,
                step_name=step_name,
                timestamp=ts,
                state_data=extra.get("state_data", {}),
                variables=extra.get("variables", {}),
                context=extra.get("context", {}),
                substrate=extra.get("substrate", {}),
            )
        except Exception as exc:
            logger.error("SQLiteCheckpointStorage: load failed", checkpoint_id=checkpoint_id, error=str(exc))
            return None

    def list_checkpoints(self, workflow_id: str | None = None) -> list[str]:
        """Return checkpoint IDs, optionally filtered by workflow_id."""
        try:
            conn = sqlite3.connect(self.db_path)
            try:
                if workflow_id is not None:
                    rows = conn.execute(
                        "SELECT checkpoint_id FROM em3_checkpoints WHERE workflow_id = ?",
                        (workflow_id,),
                    ).fetchall()
                else:
                    rows = conn.execute("SELECT checkpoint_id FROM em3_checkpoints").fetchall()
            finally:
                conn.close()
            return [r[0] for r in rows]
        except Exception as exc:
            logger.error("SQLiteCheckpointStorage: list failed", error=str(exc))
            return []

    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint by ID."""
        try:
            conn = sqlite3.connect(self.db_path)
            try:
                conn.execute(
                    "DELETE FROM em3_checkpoints WHERE checkpoint_id = ?", (checkpoint_id,)
                )
                conn.commit()
            finally:
                conn.close()
            return True
        except Exception as exc:
            logger.error("SQLiteCheckpointStorage: delete failed", checkpoint_id=checkpoint_id, error=str(exc))
            return False

    # ------------------------------------------------------------------
    # Convenience helpers used by DurableExecutionManager shim
    # ------------------------------------------------------------------

    def save_step(
        self,
        workflow_id: str,
        step_id: str,
        status: str,
        output: dict[str, Any] | None = None,
    ) -> bool:
        """Lightweight adapter matching the old DurableExecutionManager.save_step_checkpoint() API."""
        import time
        import uuid

        checkpoint = Checkpoint(
            checkpoint_id=str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{workflow_id}:{step_id}")),
            workflow_id=workflow_id,
            step_name=step_id,
            timestamp=time.time(),
            state_data={"status": status, "output": output or {}},
        )
        return self.save_checkpoint(checkpoint)

    def get_completed_steps(self, workflow_id: str) -> dict[str, dict[str, Any]]:
        """Return completed step data keyed by step_name (mirrors old DurableExecutionManager API)."""
        try:
            conn = sqlite3.connect(self.db_path)
            try:
                rows = conn.execute(
                    "SELECT step_name, state_json FROM em3_checkpoints WHERE workflow_id = ?",
                    (workflow_id,),
                ).fetchall()
            finally:
                conn.close()

            result: dict[str, dict[str, Any]] = {}
            for step_name, state_json in rows:
                extra = json.loads(state_json) if state_json else {}
                state_data = extra.get("state_data", {})
                if state_data.get("status") == "completed":
                    result[step_name] = {
                        "status": "completed",
                        "output": state_data.get("output", {}),
                    }
            return result
        except Exception as exc:
            logger.error("SQLiteCheckpointStorage: get_completed_steps failed", workflow_id=workflow_id, error=str(exc))
            return {}

    def clear_workflow(self, workflow_id: str) -> None:
        """Delete all checkpoints for a workflow."""
        try:
            conn = sqlite3.connect(self.db_path)
            try:
                conn.execute("DELETE FROM em3_checkpoints WHERE workflow_id = ?", (workflow_id,))
                conn.commit()
            finally:
                conn.close()
        except Exception as exc:
            logger.warning("SQLiteCheckpointStorage: clear_workflow failed", workflow_id=workflow_id, error=str(exc))
