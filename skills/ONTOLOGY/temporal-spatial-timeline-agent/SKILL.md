---
name: temporal-spatial-timeline-agent
description: Demonstrates Phase 13 Temporal-Spatial Dynamic Ontology, querying point-in-time historical world state snapshots and spatial proximity filtering over maritime assets.
domain: ONTOLOGY
surfaces:
  - python
  - prolog
  - z3
  - datalog
version: 1.0.0
---

# Temporal-Spatial Timeline Agent Skill

## Overview

The `temporal-spatial-timeline-agent` skill demonstrates **Phase 13 Temporal-Spatial Dynamic Ontology & World State Timeline Engine** in `Em-Cubed`.

## Temporal-Spatial Workflow

```
[ TemporalSpatialTriples (ValidInterval, GeoLocation) ] ──► WorldStateTimeline
                                                                   │
                                                                   ├─► TemporalSnapshotQueryEngine (Snapshot at t)
                                                                   └─► SpatialProximityReasoner (Radius <= 50km)
```

## Point-in-Time & Spatial Query Example

```json
{
  "query_timestamp": "2026-03-15T12:00:00Z",
  "active_triples_count": 5,
  "spatial_center": {"lat": -34.9011, "lon": -56.1645},
  "entities_within_50km": [
    {"subject": "Vessel_Alpha", "distance_km": 12.4}
  ]
}
```
