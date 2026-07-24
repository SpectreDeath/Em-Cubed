"""Text-to-Loop Ontology Miner.

Parses unstructured text, standard operating procedures (SOPs), API documentation, or runbooks
into structured loop definitions (Trigger, State, Action, Exit Condition, Max Retries).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MinedLoopSchema:
    """Structured loop schema mined from unstructured text or documentation."""

    name: str
    trigger: str
    monitored_state: str
    action_sequence: list[str]
    exit_condition: str
    max_retries: int = 5
    fallback_action: str = "Escalate to human operator"


class TextLoopMiner:
    """Miner parsing procedural documentation into executable loop definitions."""

    def mine_loops_from_text(self, text: str, default_name: str = "ExtractedLoop") -> list[MinedLoopSchema]:
        """Parse raw text for implicit or explicit procedural loops.

        Parameters
        ----------
        text : str
            Raw SOP or documentation text.
        default_name : str
            Default loop name if none detected.

        Returns
        -------
        list[MinedLoopSchema]
            Extracted loop schemas.
        """
        logger.info("Mining procedural loops from text (%d chars)...", len(text))
        loops: list[MinedLoopSchema] = []

        lines = text.splitlines()
        trigger = "Manual Execution"
        state = "Unspecified State"
        actions: list[str] = []
        exit_cond = "Success Status"

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Detect triggers
            if re.search(r"\b(when|if|upon|whenever)\b", line_str, re.IGNORECASE):
                trigger = line_str
            # Detect actions
            elif re.search(r"\b(do|run|execute|check|update|apply)\b", line_str, re.IGNORECASE):
                actions.append(line_str)
            # Detect exit conditions
            elif re.search(r"\b(until|ensure|verify|confirm|exit code)\b", line_str, re.IGNORECASE):
                exit_cond = line_str

        if not actions:
            actions = ["Execute action step"]

        loops.append(
            MinedLoopSchema(
                name=default_name,
                trigger=trigger,
                monitored_state=state,
                action_sequence=actions,
                exit_condition=exit_cond,
                max_retries=5,
            )
        )

        return loops
