"""Unit tests for Temporal-Spatial Dynamic Ontology Engine."""

from datetime import datetime, timezone
from em_cubed.ontology.temporal_spatial import (
    GeoLocation,
    SpatialProximityReasoner,
    TemporalSnapshotQueryEngine,
    TemporalSpatialTriple,
    TimeInterval,
    WorldStateTimeline,
)


def test_time_interval_validity():
    t_start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    t_end = datetime(2026, 6, 1, tzinfo=timezone.utc)
    interval = TimeInterval(start_time=t_start, end_time=t_end)

    t_mid = datetime(2026, 3, 15, tzinfo=timezone.utc)
    t_out = datetime(2026, 8, 1, tzinfo=timezone.utc)

    assert interval.is_valid_at(t_mid) is True
    assert interval.is_valid_at(t_out) is False


def test_haversine_distance_and_spatial_proximity():
    loc1 = GeoLocation(latitude=-34.9011, longitude=-56.1645)  # Montevideo Port
    loc2 = GeoLocation(latitude=-34.8000, longitude=-56.1000)  # ~12km away

    dist = loc1.distance_km(loc2)
    assert 10.0 < dist < 20.0

    timeline = WorldStateTimeline()
    t_triple = TemporalSpatialTriple(
        subject="Shipment_100",
        predicate="has_location",
        object="MontevideoBay",
        interval=TimeInterval(start_time=datetime(2026, 1, 1, tzinfo=timezone.utc)),
        location=loc2,
    )
    timeline.add_temporal_triple(t_triple)

    near = SpatialProximityReasoner.find_entities_within_radius(timeline, loc1, radius_km=50.0)
    assert len(near) == 1
    assert near[0][0] == "Shipment_100"


def test_temporal_snapshot_query():
    timeline = WorldStateTimeline()
    t1 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    t2 = datetime(2026, 4, 1, tzinfo=timezone.utc)
    t3 = datetime(2026, 7, 1, tzinfo=timezone.utc)

    triple_early = TemporalSpatialTriple(
        subject="Vessel_A",
        predicate="status",
        object="InTransit",
        interval=TimeInterval(start_time=t1, end_time=t2),
    )
    triple_late = TemporalSpatialTriple(
        subject="Vessel_A",
        predicate="status",
        object="Docked",
        interval=TimeInterval(start_time=t2, end_time=t3),
    )

    timeline.add_temporal_triple(triple_early)
    timeline.add_temporal_triple(triple_late)

    # Query snapshot at Feb 2026 (early)
    snapshot_feb = TemporalSnapshotQueryEngine.snapshot_at(timeline, datetime(2026, 2, 1, tzinfo=timezone.utc))
    assert len(snapshot_feb) == 1
    assert snapshot_feb[0].object == "InTransit"

    # Query snapshot at May 2026 (late)
    snapshot_may = TemporalSnapshotQueryEngine.snapshot_at(timeline, datetime(2026, 5, 1, tzinfo=timezone.utc))
    assert len(snapshot_may) == 1
    assert snapshot_may[0].object == "Docked"
