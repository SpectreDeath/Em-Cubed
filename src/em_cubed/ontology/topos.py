"""Topos Subobject Classifier and Truth Value Object (Omega).

Generalizes truth evaluation beyond classical binary Boolean {False, True} to include:
- Continuous Confidence: [0.0 ... 1.0]
- Modal Operators: Necessary (Box), Possible (Diamond)
- Temporal Validity: Valid within a specific step window [t_start, t_end]
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ModalType(Enum):
    """Modal logic operator classification."""

    ASSERTION = "Assertion"  # Standard factual assertion
    NECESSARY = "Necessary"  # Box (Must hold in all accessible worlds)
    POSSIBLE = "Possible"  # Diamond (Holds in at least one accessible world)


@dataclass
class TruthValue:
    """The Truth Value Object (Omega) in a Topos.

    Parameters
    ----------
    is_boolean : bool
        Classical boolean truth state.
    confidence : float
        Continuous truth degree [0.0, 1.0].
    modal_type : ModalType
        Modal logic classification (Necessary vs Possible).
    temporal_window : tuple[int, int] | None
        Optional (start_step, end_step) validity window.
    """

    is_boolean: bool
    confidence: float = 1.0
    modal_type: ModalType = ModalType.ASSERTION
    temporal_window: tuple[int, int] | None = None
    evidence: list[str] = field(default_factory=list)

    def is_satisfied(self, min_confidence: float = 0.8) -> bool:
        """Evaluate if truth value meets the satisfaction threshold in Omega."""
        if not self.is_boolean:
            return False
        return not self.confidence < min_confidence


class SubobjectClassifier:
    """Topos Subobject Classifier classifying candidate state subobjects (m : A -> X) against Omega."""

    @staticmethod
    def classify_boolean(is_true: bool, message: str = "") -> TruthValue:
        """Classify a standard boolean result into Omega."""
        return TruthValue(
            is_boolean=is_true,
            confidence=1.0 if is_true else 0.0,
            modal_type=ModalType.ASSERTION,
            evidence=[message] if message else [],
        )

    @staticmethod
    def classify_modal(
        is_true: bool,
        modal_type: ModalType,
        confidence: float = 1.0,
        message: str = "",
    ) -> TruthValue:
        """Classify a modal proposition (Necessary vs Possible) into Omega."""
        return TruthValue(
            is_boolean=is_true,
            confidence=confidence,
            modal_type=modal_type,
            evidence=[message] if message else [],
        )

    @staticmethod
    def evaluate_confidence(confidence: float) -> TruthValue:
        """Classify confidence rating into modal truth value in Omega."""
        is_true = confidence >= 0.50
        modal_type = (
            ModalType.NECESSARY
            if confidence >= 0.90
            else (ModalType.POSSIBLE if confidence >= 0.50 else ModalType.ASSERTION)
        )
        return TruthValue(
            is_boolean=is_true,
            confidence=confidence,
            modal_type=modal_type,
            evidence=[f"Confidence: {confidence:.2f}"],
        )

    @staticmethod
    def classify_temporal(
        is_true: bool,
        step: int,
        validity_window: tuple[int, int],
        message: str = "",
    ) -> TruthValue:
        """Classify a temporal proposition valid within a step window."""
        t_start, t_end = validity_window
        in_window = t_start <= step <= t_end
        return TruthValue(
            is_boolean=is_true and in_window,
            confidence=1.0 if (is_true and in_window) else 0.0,
            modal_type=ModalType.ASSERTION,
            temporal_window=validity_window,
            evidence=[message] if message else [],
        )
