# Skill Summary Card: `skill-sensor-transducer`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        skill-sensor-transducer                   │
│ Category:    DATA_PROCESSING / Sensor Normalization    │
│ Invocation:  /skill-sensor-transducer                  │
│ Trigger:     "skill sensor transducer", "normalize raw │
│              "sensor transducer", "minmax scale",      │
│              "zscore scale", "schema hash sqlite"      │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Normalize unstructured sensor streams     │
│              into bounded typed tensors with SQLite    │
│              schema hashing & descriptive statistics.  │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest raw stream & compute SHA-256 schema hash | Stream & Schema AST | Valid schema hash generated |
| **2. Statistics** | Compute raw sample statistics (min, max, mean, std)| Raw Statistics Record | Stats computed |
| **3. Visual Brief** | Render before/after normalization histograms | `%TEMP%\sensor-transducer-brief-*.html`| Dark theme HTML brief |
| **4. Checkpoint** | Validate zero-variance guard & clamp bounds $[L, U]$| Clamping Gate Record | Bound bounds verified |
| **5. Model Emission**| Apply scaling, persist SQLite record & emit payload| `TransductionResult` Payload | Full transduced payload emitted |

---

## Invariants & Guardrails

- [ ] **Bounded Scaling Invariant**: MinMax scaling strictly clamped to $[0.0, 1.0]$.
- [ ] **Zero-Variance Safety**: Constant inputs map to $0.5$ without division errors.
- [ ] **Schema Hash Tracking**: All records indexed by SHA-256 schema hash.
