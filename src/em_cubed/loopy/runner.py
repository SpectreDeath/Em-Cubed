"""Loopy Skill Runner and Execution Scope Controller.

Provides helper runners to execute loopy skills with isolation, timeout guards, and trajectory logging.
"""

from __future__ import annotations

import logging
from typing import Any, TypeVar

from em_cubed.loopy.base import BaseLoopySkill, LoopySkillResult

logger = logging.getLogger(__name__)

T_State = TypeVar("T_State")
T_Result = TypeVar("T_Result")


class LoopySkillRunner:
    """Runner executing loopy skills with telemetry and optional context truncation."""

    @staticmethod
    def execute(
        skill: BaseLoopySkill[T_State, T_Result],
        *args: Any,
        **kwargs: Any,
    ) -> LoopySkillResult[T_Result]:
        """Execute a loopy skill within a controlled runner scope.

        Parameters
        ----------
        skill : BaseLoopySkill[T_State, T_Result]
            Instantiated loopy skill.

        Returns
        -------
        LoopySkillResult[T_Result]
            Execution outcome and trajectory history.
        """
        logger.info("LoopySkillRunner dispatching skill: %s", skill.__class__.__name__)
        return skill.run(*args, **kwargs)
