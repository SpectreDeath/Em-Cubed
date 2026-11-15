# Skill Summary Card: `time-series-preprocessor`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        time-series-preprocessor                  │
│ Category:    DATA_PROCESSING / Time Series Preparation │
│ Invocation:  /time-series-preprocessor                 │
│ Trigger:     "time series preprocessor", "clean series │
│              "resample frequency", "detect outliers",  │
│              "interpolate missing", "rolling zscore"   │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Clean & align non-uniform time series with│
│              frequency resampling, outlier detection,  │
│              and interpolation in Python & SQLite.     │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest timestamps & values; parse chronology | Time Series AST | $|\text{TS}| = |\text{Val}| \ge 2$ |
| **2. Resampling** | Align observations to uniform frequency grid | Resampled Grid Record | Uniform grid established |
| **3. Visual Brief** | Render trajectory plot & outlier highlight markers | `%TEMP%\time-series-preprocessor-brief-*.html`| Dark theme HTML brief |
| **4. Checkpoint** | Detect statistical outliers via rolling Z-score/IQR| Anomaly Gate Record | Outlier indices flagged |
| **5. Model Emission**| Impute missing values, cache SQLite & emit payload| `TimeSeriesResult` Payload | Full cleaned payload emitted |

---

## Invariants & Guardrails

- [ ] **Chronological Ordering**: Timestamps strictly sorted prior to processing.
- [ ] **Dimension Invariant**: Output cleaned values length strictly matches grid.
- [ ] **Outlier Robustness**: Cleaned values eliminate severe anomalies without data loss.
