"""Durable execution & checkpoint recovery engine for resilient workflow execution."""

import json
from pathlib import Path
import sqlite3
from typing import Any
import structlog

logger = structlog.get_logger()


class DurableExecutionManager:
    """Manages workflow execution checkpoints, state persistence, and resume recovery."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or Path(".workflow_checkpoints.db")
        self._init_db()

    def _init_db(self) -> None:
        """Initialize SQLite database for checkpoint persistence."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS workflow_checkpoints (
                workflow_id TEXT,
                step_id TEXT,
                status TEXT,
                output_json TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (workflow_id, step_id)
            )
            """
        )
        conn.commit()
        conn.close()

    def save_step_checkpoint(
        self, workflow_id: str, step_id: str, status: str, output: dict[str, Any] | None = None
    ) -> bool:
        """Save a step execution checkpoint."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            output_str = json.dumps(output or {})
            cursor.execute(
                """
                INSERT OR REPLACE INTO workflow_checkpoints (workflow_id, step_id, status, output_json)
                VALUES (?, ?, ?, ?)
                """,
                (workflow_id, step_id, status, output_str),
            )
            conn.commit()
            conn.close()
            logger.info("Saved step checkpoint", workflow_id=workflow_id, step_id=step_id, status=status)
            return True
        except Exception as e:
            logger.exception("Failed to save step checkpoint", workflow_id=workflow_id, step_id=step_id, error=str(e))
            return False

    def get_completed_steps(self, workflow_id: str) -> dict[str, dict[str, Any]]:
        """Retrieve completed step checkpoints for a workflow to allow resume recovery."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT step_id, status, output_json FROM workflow_checkpoints
                WHERE workflow_id = ? AND status = 'completed'
                """,
                (workflow_id,),
            )
            rows = cursor.fetchall()
            conn.close()

            completed: dict[str, dict[str, Any]] = {}
            for step_id, status, output_str in rows:
                completed[step_id] = {
                    "status": status,
                    "output": json.loads(output_str) if output_str else {},
                }
            return completed
        except Exception as e:
            logger.exception("Failed to get completed step checkpoints", workflow_id=workflow_id, error=str(e))
            return {}

    def clear_workflow_checkpoints(self, workflow_id: str) -> None:
        """Clear all stored checkpoints for a given workflow."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM workflow_checkpoints WHERE workflow_id = ?", (workflow_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning("Failed to clear checkpoints", workflow_id=workflow_id, error=str(e))
