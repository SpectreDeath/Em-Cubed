"""SkillWorkerSpec: serializable specification for a distributed skill execution task.

This dataclass is the only thing passed to ``_execute_distributed_task`` in
``distributed.py``, eliminating the need for worker subprocesses to re-import
``PluginManager``, ``SkillRegistry``, or ``SkillExecutor``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SkillWorkerSpec:
    """Self-contained, pickle-safe description of a skill execution task.

    All fields are JSON-serializable primitives so that ``ProcessPoolExecutor``
    can transmit the spec across process boundaries without importing heavy
    stack components.

    Parameters
    ----------
    skill_id:
        Registry identifier of the skill to execute.
    surface_name:
        The surface on which to execute (e.g. ``"python"``, ``"prolog"``).
    code_blocks:
        Mapping of surface name → source code.  The worker looks up
        ``code_blocks[surface_name]`` to get the code to run.
    input_data:
        Input payload forwarded to the surface's ``execute()`` context.
    timeout:
        Maximum execution time in seconds.
    """

    skill_id: str
    surface_name: str
    code_blocks: dict[str, str] = field(default_factory=dict)
    input_data: dict[str, Any] = field(default_factory=dict)
    timeout: float = 30.0

    def get_code(self) -> str | None:
        """Return the source code for the configured surface, or None if unavailable."""
        return self.code_blocks.get(self.surface_name)
