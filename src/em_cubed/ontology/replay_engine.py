"""Tri-Engine Formal Epistemic Audit Log & Verifiable Replay Engine.

Records timestamped execution frames capturing SME epistemic trust, Em-Cubed Topos Ω
modal truth, and Strategify Mesa Geo ABM state actor moves into a cryptographic Merkle-hashed
audit log for deterministic replay and retrospective verification.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ReplayFrame:
    """Dataclass holding a single execution state frame."""

    step_index: int
    sme_trust_score: float
    topos_modal_truth: str
    strategify_actor_state: dict[str, Any]
    previous_hash: str = ""
    frame_hash: str = field(default_factory=str)

    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash for this replay frame."""
        payload = json.dumps(
            {
                "step_index": self.step_index,
                "sme_trust_score": self.sme_trust_score,
                "topos_modal_truth": self.topos_modal_truth,
                "strategify_actor_state": self.strategify_actor_state,
                "previous_hash": self.previous_hash,
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class EpistemicReplayEngine:
    """Engine recording and replaying deterministic execution state frames."""

    def __init__(self) -> None:
        self.frames: list[ReplayFrame] = []

    def record_frame(
        self,
        step_index: int,
        sme_trust_score: float,
        topos_modal_truth: str,
        strategify_actor_state: dict[str, Any],
    ) -> ReplayFrame:
        """Record a new state frame and append to hash chain.

        Parameters
        ----------
        step_index : int
            Execution step index.
        sme_trust_score : float
            Current SME epistemic trust metric.
        topos_modal_truth : str
            Em-Cubed Topos Ω modal status.
        strategify_actor_state : dict[str, Any]
            State dictionary of Strategify simulation actors.

        Returns
        -------
        ReplayFrame
            Recorded frame with computed hash.
        """
        prev_hash = self.frames[-1].frame_hash if self.frames else "GENESIS"
        frame = ReplayFrame(
            step_index=step_index,
            sme_trust_score=sme_trust_score,
            topos_modal_truth=topos_modal_truth,
            strategify_actor_state=strategify_actor_state,
            previous_hash=prev_hash,
        )
        frame.frame_hash = frame.calculate_hash()
        self.frames.append(frame)
        logger.info("Recorded Replay Frame #%d [Hash: %s]", step_index, frame.frame_hash[:10])
        return frame

    def verify_integrity(self) -> bool:
        """Verify the cryptographic hash chain integrity of all recorded frames."""
        for i, frame in enumerate(self.frames):
            expected_prev = self.frames[i - 1].frame_hash if i > 0 else "GENESIS"
            if frame.previous_hash != expected_prev:
                logger.error("Hash chain break at frame #%d: prev_hash mismatch", i)
                return False
            if frame.calculate_hash() != frame.frame_hash:
                logger.error("Tamper detected at frame #%d: computed hash mismatch", i)
                return False
        return True

    def replay_step(self, step_index: int) -> ReplayFrame | None:
        """Replay execution state for a specific step index.

        Parameters
        ----------
        step_index : int
            Target step index.

        Returns
        -------
        ReplayFrame | None
            Replayed frame if found, else None.
        """
        for frame in self.frames:
            if frame.step_index == step_index:
                logger.info("Replaying step #%d [Trust: %.2f, Modal: %s]", step_index, frame.sme_trust_score, frame.topos_modal_truth)
                return frame
        return None
