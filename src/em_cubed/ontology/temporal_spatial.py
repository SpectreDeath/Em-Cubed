"""Temporal-Spatial Dynamic Ontology & World State Timeline Engine.

Implements 4D/5D temporal intervals, geospatial locations, point-in-time historical snapshot queries,
and spatial containment reasoning over dynamic entity triples.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from datetime import datetime

from em_cubed.ontology.schema import OntologyTriple

logger = logging.getLogger(__name__)


@dataclass
class TimeInterval:
    """Represents a valid temporal interval [start_time, end_time]."""

    start_time: datetime
    end_time: datetime | None = None

    def is_valid_at(self, timestamp: datetime) -> bool:
        """Check if timestamp falls within valid interval."""
        if timestamp < self.start_time:
            return False
        return not (self.end_time and timestamp > self.end_time)


@dataclass
class GeoLocation:
    """Represents geospatial coordinates (latitude, longitude, altitude)."""

    latitude: float
    longitude: float
    altitude: float = 0.0

    def distance_km(self, other: GeoLocation) -> float:
        """Calculate Haversine distance in kilometers to another location."""
        r = 6371.0  # Earth radius in km
        dlat = math.radians(other.latitude - self.latitude)
        dlon = math.radians(other.longitude - self.longitude)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(self.latitude)) * math.cos(math.radians(other.latitude)) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c


@dataclass
class TemporalSpatialTriple:
    """Semantic triple extended with TimeInterval and optional GeoLocation."""

    subject: str
    predicate: str
    object: str
    interval: TimeInterval
    location: GeoLocation | None = None
    confidence: float = 1.0

    def to_base_triple(self) -> OntologyTriple:
        """Convert to base OntologyTriple."""
        return OntologyTriple(
            subject=self.subject,
            predicate=self.predicate,
            object=self.object,
            confidence=self.confidence,
        )


class WorldStateTimeline:
    """Ledger tracking time-series evolution of temporal-spatial triples."""

    def __init__(self) -> None:
        self.temporal_triples: list[TemporalSpatialTriple] = []

    def add_temporal_triple(self, triple: TemporalSpatialTriple) -> None:
        """Record a new temporal-spatial triple into timeline."""
        self.temporal_triples.append(triple)
        logger.info(
            "Recorded Temporal Triple (%s, %s, %s) valid from %s",
            triple.subject,
            triple.predicate,
            triple.object,
            triple.interval.start_time.isoformat(),
        )


class TemporalSnapshotQueryEngine:
    """Filters state triples valid at a specific point-in-time timestamp t."""

    @staticmethod
    def snapshot_at(
        timeline: WorldStateTimeline,
        timestamp: datetime,
    ) -> list[OntologyTriple]:
        """Query state triples valid at timestamp t.

        Parameters
        ----------
        timeline : WorldStateTimeline
            World state timeline ledger.
        timestamp : datetime
            Point-in-time timestamp.

        Returns
        -------
        list[OntologyTriple]
            Active base triples valid at timestamp t.
        """
        valid_triples = [t.to_base_triple() for t in timeline.temporal_triples if t.interval.is_valid_at(timestamp)]
        logger.info("Snapshot query at %s returned %d valid triples.", timestamp.isoformat(), len(valid_triples))
        return valid_triples


class SpatialProximityReasoner:
    """Evaluates spatial containment and proximity constraints across dynamic entities."""

    @staticmethod
    def find_entities_within_radius(
        timeline: WorldStateTimeline,
        center: GeoLocation,
        radius_km: float,
    ) -> list[tuple[str, float]]:
        """Find all subjects with locations within radius_km of center location."""
        results: list[tuple[str, float]] = []
        for t in timeline.temporal_triples:
            if t.location:
                dist = center.distance_km(t.location)
                if dist <= radius_km:
                    results.append((t.subject, dist))

        logger.info("Found %d entities within %.1f km radius.", len(results), radius_km)
        return results
