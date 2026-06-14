---
name: skill-telemetry
domain: META_ENGINEERING
version: "1.0.0"
surfaces: [python, sqlite]
description: Per-agent execution telemetry framework capturing input_state_complexity, execution_path_taken, outcome, and local_parsing_idiosyncrasies for localized skill honing without modifying the master registry.
compatibility: PYTHON, SQLITE
allowed-tools: |
  - read
  - write
  - edit
  - bash
  - glob
  - grep
  - codebase_search
  - task
  - sequentialthinking_sequentialthinking
  - webfetch
  - websearch
  - question
  - suggest
---

# Purpose

Provide a deterministic, per-agent execution logging framework so that individual agents can build up localised "experience" logs over time, enabling skill honing without modifying the central skill registry.

# Description

Every time an agent executes a skill, the telemetry framework captures:

- **`input_state_complexity`** — structural properties of the execution inputs (matrix dimensions, sparsity, vocabulary size, etc.)
- **`execution_path_taken`** — which surface path the agent used (python_vectorized_dense, prolog_datalog_asp, etc.)
- **`outcome`** — success / error / timeout
- **`local_parsing_idiosyncrasies`** — agent-private preferences (preferred tensor layout, retry behaviour, etc.)

These logs are stored per-agent in a local SQLite database and are **never** written back to the central `skills/` registry.

# Surfaces

- **Python (primary)**: `SkillTelemetry` class — append-only log helper with fluent API
- **SQLite (persistence)**: schema for local telemetry tables; per-agent sharding via `agent_id`

# Schema

```sql
-- Per-agent telemetry store
CREATE TABLE IF NOT EXISTS skill_telemetry (
    telemetry_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id            TEXT NOT NULL,
    skill_id            TEXT NOT NULL,
    experience_iteration INTEGER NOT NULL DEFAULT 0,
    input_state_complexity TEXT,       -- JSON blob
    execution_path_taken  TEXT,
    runtime_performance_ms REAL,
    outcome              TEXT CHECK(outcome IN ('success','error','timeout')),
    error_delta          TEXT,
    local_parsing_idiosyncrasies TEXT, -- JSON blob (agent-private)
    created_at           TEXT DEFAULT (datetime('now')),
    UNIQUE(agent_id, skill_id, experience_iteration)
);

CREATE INDEX IF NOT EXISTS idx_telemetry_agent
    ON skill_telemetry(agent_id, skill_id, created_at);
```

# WeightedParams helper

```python
"""
telemetry.py — Skill Telemetry Framework (META_ENGINEERING)

Provides:
  - WeightedParams: agent-private parameter bag that evolves with experience.
  - SkillTelemetryLogger: append-only telemetry logger backed by SQLite.
  - SkillHoningEngine: reads an agent's history to produce weight-bias
    wrappers that personalise how that agent initialises a skill.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ==========================================================================
#  Agent-private parameter bag
# ==========================================================================

@dataclass
class WeightedParams:
    """Mutable, agent-private parameters that influence how a skill is run.

    These are NOT written back to the registry.  They are loaded from the
    agent's local telemetry history each time the skill is invoked.
    """
    agent_id: str
    skill_id: str
    preferred_tensor_layout: str = "row_major"
    retry_on_marginal_convergence: bool = True
    max_retries: int = 3
    convergence_tolerance_override: Optional[float] = None
    surface_preference_order: List[str] = field(default_factory=lambda: ["python", "prolog"])
    custom_weights: Dict[str, float] = field(default_factory=dict)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WeightedParams":
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> "WeightedParams":
        return cls.from_dict(json.loads(json_str))


# ==========================================================================
#  SQLite-backed telemetry logger
# ==========================================================================

class SkillTelemetryLogger:
    """Append-only per-agent telemetry logger.

    Parameters
    ----------
    db_path:
        Path to the agent's local SQLite telemetry database.  Defaults
        to ``~/.em_cubed/telemetry/{agent_id}.db`` when omitted.
    agent_id:
        Unique agent identifier.  Required — the framework shards data
        by agent so histories never collide.
    """

    DEFAULT_DB_ROOT = str(Path.home() / ".em_cubed" / "telemetry")

    _DDL = """
        CREATE TABLE IF NOT EXISTS skill_telemetry (
            telemetry_id           INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id               TEXT    NOT NULL,
            skill_id               TEXT    NOT NULL,
            experience_iteration   INTEGER NOT NULL DEFAULT 0,
            input_state_complexity TEXT,
            execution_path_taken   TEXT,
            runtime_performance_ms REAL,
            outcome                TEXT    CHECK(outcome IN ('success','error','timeout')),
            error_delta            TEXT,
            local_parsing_idiosyncrasies TEXT,
            created_at             TEXT    DEFAULT (datetime('now')),
            UNIQUE(agent_id, skill_id, experience_iteration)
        );
        CREATE INDEX IF NOT EXISTS idx_telemetry_agent
            ON skill_telemetry(agent_id, skill_id, created_at);
    """

    def __init__(
        self,
        agent_id: str,
        db_path: Optional[str] = None,
    ) -> None:
        self.agent_id = agent_id
        self.db_path = db_path or str(
            Path(self.DEFAULT_DB_ROOT) / f"{agent_id}.db"
        )
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(self._DDL)
        self._conn.commit()
        logger.info("SkillTelemetryLogger initialised for %s at %s",
                     agent_id, self.db_path)

    # ------------------------------------------------------------------
    #  Logging
    # ------------------------------------------------------------------

    def log_execution(
        self,
        skill_id: str,
        experience_iteration: int,
        *,
        input_state_complexity: Optional[Dict[str, Any]] = None,
        execution_path_taken: Optional[str] = None,
        runtime_performance_ms: Optional[float] = None,
        outcome: str = "success",
        error_delta: Optional[str] = None,
        local_parsing_idiosyncrasies: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Append one execution record.  Returns the assigned telemetry_id."""
        complexity_json = json.dumps(input_state_complexity) if input_state_complexity else None
        idiosyncrasies_json = (
            json.dumps(local_parsing_idiosyncrasies)
            if local_parsing_idiosyncrasies
            else None
        )
        cursor = self._conn.execute(
            """
            INSERT OR REPLACE INTO skill_telemetry
                (agent_id, skill_id, experience_iteration,
                 input_state_complexity, execution_path_taken,
                 runtime_performance_ms, outcome, error_delta,
                 local_parsing_idiosyncrasies)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self.agent_id,
                skill_id,
                experience_iteration,
                complexity_json,
                execution_path_taken,
                runtime_performance_ms,
                outcome,
                error_delta,
                idiosyncrasies_json,
            ),
        )
        self._conn.commit()
        telemetry_id = cursor.lastrowid
        logger.debug("Logged telemetry id=%d skill=%s iter=%d outcome=%s",
                     telemetry_id, skill_id, experience_iteration, outcome)
        return telemetry_id

    def log_error(
        self,
        skill_id: str,
        experience_iteration: int,
        error: str,
        **kwargs: Any,
    ) -> int:
        return self.log_execution(
            skill_id,
            experience_iteration,
            outcome="error",
            error_delta=error[:2000],
            **kwargs,
        )

    def log_timeout(
        self,
        skill_id: str,
        experience_iteration: int,
        timeout_s: float,
        **kwargs: Any,
    ) -> int:
        return self.log_execution(
            skill_id,
            experience_iteration,
            outcome="timeout",
            error_delta=f"timed_out_after_{timeout_s}s",
            **kwargs,
        )

    # ------------------------------------------------------------------
    #  History queries
    # ------------------------------------------------------------------

    def get_history(
        self,
        skill_id: str,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        rows = self._conn.execute(
            """
            SELECT * FROM skill_telemetry
            WHERE agent_id = ? AND skill_id = ?
            ORDER BY experience_iteration DESC
            LIMIT ?
            """,
            (self.agent_id, skill_id, limit),
        ).fetchall()
        return [dict(row) for row in rows]

    def get_success_rate(self, skill_id: str) -> float:
        row = self._conn.execute(
            """
            SELECT
                SUM(CASE WHEN outcome = 'success' THEN 1 ELSE 0 END) AS successes,
                COUNT(*) AS total
            FROM skill_telemetry
            WHERE agent_id = ? AND skill_id = ?
            """,
            (self.agent_id, skill_id),
        ).fetchone()
        if not row or row["total"] == 0:
            return 0.0
        return row["successes"] / row["total"]

    def get_next_iteration(self, skill_id: str) -> int:
        row = self._conn.execute(
            """
            SELECT MAX(experience_iteration) AS max_iter
            FROM skill_telemetry
            WHERE agent_id = ? AND skill_id = ?
            """,
            (self.agent_id, skill_id),
        ).fetchone()
        return (row["max_iter"] or 0) + 1

    def close(self) -> None:
        self._conn.close()
        logger.debug("SkillTelemetryLogger closed for %s", self.agent_id)

    def __enter__(self) -> "SkillTelemetryLogger":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()


# ==========================================================================
#  Honing engine: derive WeightedParams from agent history
# ==========================================================================

class SkillHoningEngine:
    """Derives agent-private WeightedParams from execution history.

    This is the core of the 'experience honing' loop described in the
    skill_trees brainstorm.  Each agent's honing is completely isolated —
    the resulting WeightedParams are never serialised to the central
    skill registry.
    """

    def __init__(self, telemetry: SkillTelemetryLogger) -> None:
        self.telemetry = telemetry

    def derive_params(self, skill_id: str) -> WeightedParams:
        """Produce personalised WeightedParams for a skill from the agent's history."""
        history = self.telemetry.get_history(skill_id, limit=200)
        if not history:
            return WeightedParams(agent_id=self.telemetry.agent_id, skill_id=skill_id)

        # --- surface preference: majority vote across successes ---
        surface_votes: Dict[str, int] = {}
        retry_flags: List[bool] = []
        convergence_overrides: List[float] = []

        for record in history:
            path = record.get("execution_path_taken") or ""
            if path:
                surface = path.split("_")[0] if "_" in path else path
                surface_votes[surface] = surface_votes.get(surface, 0) + 1
            idiosyncrasies_raw = record.get("local_parsing_idiosyncrasies")
            if idiosyncrasies_raw:
                try:
                    idio = json.loads(idiosyncrasies_raw)
                    if "retry_on_marginal_convergence" in idio:
                        retry_flags.append(idio["retry_on_marginal_convergence"])
                except json.JSONDecodeError:
                    pass

        preferred_surface = (
            max(surface_votes, key=surface_votes.get) if surface_votes else "python"
        )

        params = WeightedParams(
            agent_id=self.telemetry.agent_id,
            skill_id=skill_id,
            preferred_tensor_layout="row_major",
            retry_on_marginal_convergence=(
                retry_flags[-1] if retry_flags else True
            ),
            surface_preference_order=[preferred_surface, "python"],
        )

        if convergence_overrides:
            median = sorted(convergence_overrides)[len(convergence_overrides) // 2]
            params.convergence_tolerance_override = median

        return params

    def load_or_default(self, skill_id: str) -> WeightedParams:
        """Load honed params if they exist, else return fresh defaults."""
        return self.derive_params(skill_id)


# ==========================================================================
#  Convenience factory
# ==========================================================================

def get_telemetry(agent_id: str, db_path: Optional[str] = None) -> SkillTelemetryLogger:
    return SkillTelemetryLogger(agent_id=agent_id, db_path=db_path)


def get_honing_engine(agent_id: str, db_path: Optional[str] = None) -> SkillHoningEngine:
    return SkillHoningEngine(telemetry=get_telemetry(agent_id, db_path))
