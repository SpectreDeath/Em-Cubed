---
name: temporal-spatial-timeline-agent
domain: ONTOLOGY
version: 1.0.0
surfaces:
  - python
  - prolog
  - datalog
  - sqlite
description: 4D/5D temporal-spatial dynamic ontology engine. Executes point-in-time snapshot queries across historical world state timelines, computes Haversine spatial proximity filtering, and enforces 4D BFO continuant/occurrent temporal intervals. Use when querying historical ontology states at specific timestamps (as-of queries), executing spatial radius searches over semantic entities (e.g. maritime or logistics assets), or tracking entity trajectories over time.
purpose: Execute point-in-time historical snapshot queries and spatial proximity reasoning over dynamic 4D/5D knowledge graphs.
dependencies: []
tags:
  - temporal-spatial
  - point-in-time-query
  - haversine-proximity
  - 4d-ontology
  - timeline-engine
inputs:
  as_of_timestamp:
    type: string
    required: false
    description: ISO-8601 timestamp for historical snapshot query (e.g. '2026-03-15T12:00:00Z').
  spatial_center:
    type: object
    required: false
    description: 'Geographic coordinate center `{"lat": float, "lon": float}`.'
  radius_km:
    type: number
    required: false
    description: Proximity search radius in kilometers (default 50.0).
  temporal_triples:
    type: array
    required: true
    description: List of 4D temporal-spatial assertions with valid intervals and coordinates.
outputs:
  snapshot_state:
    type: array
    description: Active triples valid at requested point in time.
  entities_within_radius:
    type: array
    description: Filtered entities located within target radius with calculated distances.
  timeline_summary:
    type: object
    description: Temporal interval coverage and entity count summary.
---

# Temporal-Spatial Timeline Agent Engine

`temporal-spatial-timeline-agent` implements **Phase 13 Temporal-Spatial Dynamic Ontology & World State Timeline Engine** in `Em-Cubed`. Moving beyond static 3D ontologies, it models entities across **4D/5D spacetime**, allowing point-in-time historical reconstruction (as-of queries) and Haversine geodesic proximity reasoning over moving physical assets.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Temporal-Spatial Progression

```
[1. Temporal-Spatial Invariant Audit] → [2. As-Of Historical Slicing] → [3. Visual Brief] → [4. Checkpoint] → [5. Haversine Spatial Filtering]
```

### Stage 1: Temporal-Spatial Invariant Audit
1. Ingest `temporal_triples` and validate temporal interval bounds ($t_{\text{start}} \le t_{\text{end}}$).
2. Validate latitude/longitude coordinates ($-90 \le \text{lat} \le 90, -180 \le \text{lon} \le 180$).

> **Completion criterion**: Coordinate bounds and ISO-8601 temporal intervals validated.

---

### Stage 2: As-Of Point-in-Time Historical Slicing
1. Filter assertions to those strictly active at `as_of_timestamp`:
   $$T_{\text{valid}}(t) = \{ \text{Triple}_i \mid t_{\text{start}, i} \le t \le t_{\text{end}, i} \}$$
2. Reconstruct consistent snapshot state without temporal contradictions.

> **Completion criterion**: Discrete historical snapshot state extracted.

---

### Stage 3: The Visual Brief
For complex geospatial movements or historical timeline playback, generate an interactive brief:
- **Location**: Write to `%TEMP%\temporal-spatial-brief-<timestamp>.html` (Windows) or `/tmp/temporal-spatial-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render geographic proximity radar map and entity temporal interval Gantt timeline.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before executing computationally intensive spatial joins or timeline aggregations:
1. Verify timestamp format and coordinate projection.
2. If spatial radius covers $> 1000$ entities, verify spatial index bounding box optimization.

> **Completion criterion**: Spatial bounding box queries optimized and verified.

---

### Stage 5: Haversine Geodesic Spatial Filtering
1. Compute spherical distance between `spatial_center` and active entity coordinates:
   $$d = 2R \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos \phi_1 \cos \phi_2 \sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$
2. Filter entities where $d \le \text{radius\_km}$ and sort by proximity.
3. Emit snapshot state and sorted spatial entity records.

> **Completion criterion**: Filtered entity list emitted with calculated distances.

---

## Surface References

### Python Temporal-Spatial Surface

```python
import math
from typing import List, Dict, Any

def query_temporal_spatial(triples: List[Dict[str, Any]], as_of: str, center: Dict[str, float], radius_km: float = 50.0) -> Dict[str, Any]:
    # 1. Temporal filter
    active_triples = [t for t in triples if t.get("valid_from", "") <= as_of <= t.get("valid_to", "9999")]
    
    # 2. Haversine spatial filter
    R = 6371.0 # Earth radius in km
    lat1, lon1 = math.radians(center["lat"]), math.radians(center["lon"])
    
    nearby_entities = []
    for t in active_triples:
        if "lat" in t and "lon" in t:
            lat2, lon2 = math.radians(t["lat"]), math.radians(t["lon"])
            dlat, dlon = lat2 - lat1, lon2 - lon1
            a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            dist = R * c
            if dist <= radius_km:
                nearby_entities.append({"subject": t.get("subject"), "distance_km": round(dist, 1)})
                
    return {
        "query_timestamp": as_of,
        "active_triples_count": len(active_triples),
        "spatial_center": center,
        "entities_within_radius": nearby_entities
    }
```

---

## Anti-Patterns & Guardrails

- **Euclidean Distance on Geodetic Coordinates** — Calculating distance via naive $\sqrt{\Delta x^2 + \Delta y^2}$ instead of Great Circle / Haversine formula, causing massive spherical distortion.
- **Unbounded As-Of Queries** — Querying timelines without specifying temporal intervals, causing full table scans over millions of historical assertions.
- **Interval Inversion** — Allowing temporal records where $t_{\text{start}} > t_{\text{end}}$.
