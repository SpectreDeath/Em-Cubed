# Skill Summary Card: `temporal-spatial-timeline-agent`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        temporal-spatial-timeline-agent           │
│ Category:    ONTOLOGY / 4D/5D Spacetime Ontology       │
│ Invocation:  /temporal-spatial-timeline-agent          │
│ Trigger:     "temporal spatial query", "as-of query",  │
│              "haversine proximity", "timeline snapshot"│
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Point-in-time historical world state      │
│              snapshot reconstruction and Haversine     │
│              geodesic proximity spatial filtering.     │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Invariant Audit** | Validate interval bounds & geocoordinates | Validated Spacetime AST | Intervals $t_0 \le t_1$ & lat/lon in range |
| **2. As-Of Slicing** | Filter assertions valid at target timestamp | Historical Snapshot Graph | Active subset isolated without contradiction |
| **3. Visual Brief** | Render proximity radar and Gantt timeline | `%TEMP%\temporal-spatial-brief-*.html`| Dark theme HTML spacetime brief |
| **4. Checkpoint** | Validate bounding box & query complexity | Safety Gate Record | Query complexity within bounds |
| **5. Spatial Filter** | Compute Haversine distances & emit results | Filtered Spatial Payload | Entities within radius sorted by distance |

---

## Invariants & Guardrails

- [ ] **Haversine Geodesic**: All distance calculations must use spherical trigonometry ($R = 6371\text{ km}$).
- [ ] **Temporal Validity**: Valid intervals must satisfy $t_{\text{start}} \le t_{\text{end}}$.
- [ ] **ISO-8601 Formatting**: All timestamps must strictly follow ISO-8601 (`YYYY-MM-DDTHH:MM:SSZ`).
