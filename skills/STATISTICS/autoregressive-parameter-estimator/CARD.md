# Skill Summary Card: `autoregressive-parameter-estimator`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        autoregressive-parameter-estimator        │
│ Category:    STATISTICS / Time-Series & ARIMA Models   │
│ Invocation:  /autoregressive-parameter-estimator       │
│ Trigger:     "autoregressive parameter estimator",     │
│              "acf pacf analysis", "arima order",       │
│              "stationarity testing", "adf test"        │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Time-series parameter estimation via ACF, │
│              PACF Yule-Walker, stationarity gating,    │
│              ARIMA (p,d,q) selection & SQLite storage. │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Filter NaN/Null & validate $N \ge 10$ points | Time-Series AST | Sequential order preserved |
| **2. ACF & PACF** | Evaluate sample autocorrelations & Yule-Walker | Autocorrelation Vector Array| ACF & PACF computed to lag $K$ |
| **3. Visual Brief** | Render correlogram & Bartlett confidence bands | `%TEMP%\autoregression-brief-*.html`| Dark theme HTML time-series brief|
| **4. Checkpoint** | Validate stationarity & differencing requirement| Stationarity Gate Record| $d \in \{0, 1, 2\}$ verified |
| **5. Model & Commit** | Select $(p,d,q)$ orders & commit SQLite caches | `AutoregressiveEstimateResult`| Full record emitted & SQLite updated|

---

## Invariants & Guardrails

- [ ] **Horizon Scale Gate**: Max lag $K < N / 2$.
- [ ] **Bartlett Band Control**: Confidence threshold set to $\pm 1.96/\sqrt{N}$.
- [ ] **Stationarity Precondition**: Non-stationary series must apply differencing ($d \ge 1$).
