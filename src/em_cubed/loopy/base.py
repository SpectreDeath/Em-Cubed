"""Base Loopy Skill Contract and Trajectory Data Structures.

Defines the universal loopy skill interface, trajectory logging, and execution result containers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from em_cubed.ontology.topos import SubobjectClassifier, TruthValue

logger = logging.getLogger(__name__)

T_State = TypeVar("T_State")
T_Result = TypeVar("T_Result")


@dataclass
class LoopTrajectory:
    """Represents a single step iteration within a loopy skill execution."""

    iteration: int
    action_taken: str
    observation: str
    passed_guard: bool
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class LoopySkillResult(Generic[T_Result]):
    """Outcome of a loopy skill execution containing output and full trajectory."""

    success: bool
    final_output: T_Result
    trajectory: list[LoopTrajectory] = field(default_factory=list)
    error_message: str | None = None


class BaseLoopySkill(Generic[T_State, T_Result]):
    """Abstract base class for iterative, self-correcting loopy skills.

    Parameters
    ----------
    max_iterations : int
        Maximum number of retry iterations allowed before hitting safety limit.
    """

    def __init__(self, max_iterations: int = 5) -> None:
        self.max_iterations = max_iterations

    def initialize_state(self, *args: Any, **kwargs: Any) -> T_State:
        """Set up initial skill state variables, code trees, or query environments."""
        raise NotImplementedError

    def mutate(self, state: T_State, iteration: int) -> tuple[T_State, str]:
        """Execute the action step (e.g., call micro-LLM, run code patch, query solver).

        Returns
        -------
        tuple[T_State, str]
            Updated state and description of action taken.
        """
        raise NotImplementedError

    def verify(self, state: T_State) -> tuple[bool, str]:
        """The Sensor: Deterministic check (e.g. pytest exit code, linter pass, regex match, ontology check).

        Returns
        -------
        tuple[bool, str]
            (passed_guard, observation_message)
        """
        raise NotImplementedError

    def verify_topos(self, state: T_State) -> TruthValue:
        """The Topos Subobject Classifier Sensor: Evaluates state against Omega truth object.

        Returns
        -------
        TruthValue
            Topos TruthValue object.
        """
        passed, obs = self.verify(state)
        return SubobjectClassifier.classify_boolean(passed, obs)

    def extract_result(self, state: T_State) -> T_Result:
        """Extract final output payload from completed state."""
        raise NotImplementedError

    def run(self, *args: Any, **kwargs: Any) -> LoopySkillResult[T_Result]:
        """Execute the core loop engine until guard passes or max_iterations is reached."""
        state = self.initialize_state(*args, **kwargs)
        trajectory: list[LoopTrajectory] = []

        logger.info("Starting Loopy Skill execution (max_iterations=%d)...", self.max_iterations)

        for i in range(1, self.max_iterations + 1):
            state, action_desc = self.mutate(state, i)

            # Evaluate against Topos Subobject Classifier
            truth_val = self.verify_topos(state)
            passed = truth_val.is_satisfied()
            observation = "; ".join(truth_val.evidence) if truth_val.evidence else f"Confidence: {truth_val.confidence:.2f}"

            trajectory.append(
                LoopTrajectory(
                    iteration=i,
                    action_taken=action_desc,
                    observation=observation,
                    passed_guard=passed,
                    metrics={"confidence": truth_val.confidence, "modal_type": truth_val.modal_type.value},
                )
            )

            if passed:
                logger.info("Loopy Skill passed verification guard on iteration %d.", i)
                return LoopySkillResult(
                    success=True,
                    final_output=self.extract_result(state),
                    trajectory=trajectory,
                )

        logger.warning("Loopy Skill reached max iterations (%d) without passing guard.", self.max_iterations)
        return LoopySkillResult(
            success=False,
            final_output=self.extract_result(state),
            trajectory=trajectory,
            error_message=f"Hit max iterations ({self.max_iterations}) without passing guard.",
        )
