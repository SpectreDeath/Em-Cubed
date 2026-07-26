"""Tri-Engine Autonomous Swarm Load Balancing & Adaptive Capacity Scaler.

Dynamically balances agent worker allocations across SME perception ingestion,
Em-Cubed Topos Ω modal verification, and Strategify Mesa Geo ABM simulation based on
real-time Coherence Index (%) and SME Epistemic Trust score.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SwarmAllocationReport:
    """Dataclass holding swarm capacity allocation metrics."""

    total_workers: int
    sme_workers: int
    em_cubed_workers: int
    strategify_workers: int
    coherence_index: float
    epistemic_trust: float
    scaling_mode: str  # "BALANCED", "PERCEPTION_HEAVY", "REASONING_HEAVY", "SIMULATION_HEAVY"


class SwarmCapacityScaler:
    """Calculates dynamic worker node allocation ratios for tri-engine swarms."""

    @staticmethod
    def calculate_allocation(
        total_workers: int = 12,
        coherence_index: float = 0.95,
        epistemic_trust: float = 0.89,
    ) -> SwarmAllocationReport:
        """Calculate dynamic worker allocations across SME, Em-Cubed, and Strategify.

        Parameters
        ----------
        total_workers : int
            Total worker node pool size (default: 12).
        coherence_index : float
            Current Em-Cubed coherence index [0.0, 1.0].
        epistemic_trust : float
            Current SME epistemic trust score [0.0, 1.0].

        Returns
        -------
        SwarmAllocationReport
            Calculated allocation counts and scaling mode.
        """
        base_sme = max(1, int(total_workers * 0.25))
        base_em = max(1, int(total_workers * 0.35))
        base_strat = total_workers - base_sme - base_em

        if epistemic_trust < 0.70:
            scaling_mode = "PERCEPTION_HEAVY"
            sme_workers = max(1, base_sme + 2)
            em_cubed_workers = max(1, base_em - 1)
            strategify_workers = max(1, total_workers - sme_workers - em_cubed_workers)
        elif coherence_index < 0.80:
            scaling_mode = "REASONING_HEAVY"
            em_cubed_workers = max(1, base_em + 2)
            sme_workers = max(1, base_sme - 1)
            strategify_workers = max(1, total_workers - sme_workers - em_cubed_workers)
        elif epistemic_trust >= 0.85 and coherence_index >= 0.90:
            scaling_mode = "SIMULATION_HEAVY"
            strategify_workers = max(1, base_strat + 2)
            sme_workers = max(1, base_sme - 1)
            em_cubed_workers = max(1, total_workers - sme_workers - strategify_workers)
        else:
            scaling_mode = "BALANCED"
            sme_workers = base_sme
            em_cubed_workers = base_em
            strategify_workers = base_strat

        logger.info(
            "Swarm Scaler [%s]: Total=%d (SME=%d, Em-Cubed=%d, Strategify=%d)",
            scaling_mode,
            total_workers,
            sme_workers,
            em_cubed_workers,
            strategify_workers,
        )

        return SwarmAllocationReport(
            total_workers=total_workers,
            sme_workers=sme_workers,
            em_cubed_workers=em_cubed_workers,
            strategify_workers=strategify_workers,
            coherence_index=coherence_index,
            epistemic_trust=epistemic_trust,
            scaling_mode=scaling_mode,
        )
